import httpx

from app.config import get_env

from .base import Platform


class DevToPlatform(Platform):
    name = "Dev.to"

    async def publish(self, message: str) -> str:
        key = get_env("DEVTO_API_KEY")
        payload = {
            "article": {
                "title": message[:60],
                "body_markdown": message,
                "published": True,
            }
        }
        headers = {"api-key": key, "Accept": "application/vnd.forem.api-v1+json"}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://dev.to/api/articles", json=payload, headers=headers
            )
        if r.status_code not in (200, 201):
            raise RuntimeError(f"Dev.to error {r.status_code}: {r.text[:150]}")
        return r.json()["url"]