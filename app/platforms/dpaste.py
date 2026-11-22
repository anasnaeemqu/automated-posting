import ssl

import httpx
import truststore

from .base import Platform


class DpastePlatform(Platform):
    name = "dpaste"

    async def publish(self, message: str) -> str:
        # use the operating system's trusted certificate store
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        async with httpx.AsyncClient(timeout=20, verify=ctx) as client:
            r = await client.post(
                "https://dpaste.com/api/v2/",
                data={"content": message, "syntax": "text", "expiry_days": 7},
            )
        if r.status_code != 201:
            raise RuntimeError(f"dpaste error {r.status_code}: {r.text[:150]}")
        url = r.text.strip()
        if not url.startswith("https://dpaste.com/"):  # don't trust a fake "success"
            raise RuntimeError(f"dpaste returned an unexpected answer: {url[:100]}")
        return url