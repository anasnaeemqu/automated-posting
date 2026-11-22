import asyncio
import ssl
from datetime import datetime, timezone

import httpx
import truststore

from app.platforms import PLATFORMS
from app.schemas import PlatformResult, PostingResponse


async def _is_public(url: str) -> bool:
    try:
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        async with httpx.AsyncClient(
            timeout=10, follow_redirects=True, verify=ctx
        ) as client:
            r = await client.get(url)
        return r.status_code == 200
    except Exception:
        return False


async def _post_one(platform, message: str) -> PlatformResult:
    try:
        url = await platform.publish(message)
    except Exception as e:  # one platform failing must not stop the others
        return PlatformResult(
            platform=platform.name,
            status="failed",
            error=str(e) or type(e).__name__,
        )
    now = datetime.now(timezone.utc)
    return PlatformResult(
        platform=platform.name,
        status="success",
        posted_url=url,
        public_access=platform.check_public and await _is_public(url),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
    )


async def post_everywhere(message: str) -> PostingResponse:
    results = await asyncio.gather(*[_post_one(p, message) for p in PLATFORMS])
    return PostingResponse(
        success=any(r.status == "success" for r in results),
        results=list(results),
    )