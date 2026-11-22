import httpx

from app.config import get_env

from .base import Platform


class GistPlatform(Platform):
    name = "GitHub Gist"

    async def publish(self, message: str) -> str:
        token = get_env("GITHUB_TOKEN")
        payload = {
            "description": message[:80],
            "public": True,
            "files": {"post.md": {"content": message}},
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://api.github.com/gists", json=payload, headers=headers
            )
        if r.status_code != 201:
            raise RuntimeError(f"GitHub error {r.status_code}: {r.text[:150]}")
        return r.json()["html_url"]