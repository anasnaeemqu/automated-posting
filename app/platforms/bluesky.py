import re
from datetime import datetime, timezone

import httpx

from app.config import get_env

from .base import Platform

API = "https://bsky.social/xrpc"
URL = re.compile(r"https?://\S+")


def _link_facets(message: str) -> list[dict]:
    """Make links clickable (Bluesky counts positions in bytes)."""
    facets = []
    for m in URL.finditer(message):
        url = m.group().rstrip(".,!?;:)")
        start = len(message[: m.start()].encode("utf-8"))
        end = start + len(url.encode("utf-8"))
        facets.append(
            {
                "index": {"byteStart": start, "byteEnd": end},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
            }
        )
    return facets


class BlueskyPlatform(Platform):
    name = "Bluesky"

    async def publish(self, message: str) -> str:
        handle = get_env("BLUESKY_HANDLE")
        password = get_env("BLUESKY_APP_PASSWORD")
        async with httpx.AsyncClient(timeout=20) as client:
            s = await client.post(
                f"{API}/com.atproto.server.createSession",
                json={"identifier": handle, "password": password},
            )
            if s.status_code != 200:
                raise RuntimeError(f"Bluesky login failed {s.status_code}: {s.text[:100]}")
            session = s.json()
            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "facets": _link_facets(message),
            }
            r = await client.post(
                f"{API}/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {session['accessJwt']}"},
                json={
                    "repo": session["did"],
                    "collection": "app.bsky.feed.post",
                    "record": record,
                },
            )
        if r.status_code != 200:
            raise RuntimeError(f"Bluesky post failed {r.status_code}: {r.text[:100]}")
        rkey = r.json()["uri"].split("/")[-1]
        return f"https://bsky.app/profile/{session['handle']}/post/{rkey}"