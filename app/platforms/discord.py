import httpx

from app.config import get_env

from .base import Platform


class DiscordPlatform(Platform):
    name = "Discord"
    check_public = False  # a private server: honestly NOT public

    async def publish(self, message: str) -> str:
        webhook = get_env("DISCORD_WEBHOOK_URL")
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                webhook, params={"wait": "true"}, json={"content": message}
            )
            if r.status_code != 200:
                raise RuntimeError(f"Discord error {r.status_code}: {r.text[:150]}")
            data = r.json()
            guild = data.get("guild_id")
            if not guild:  # ask the webhook which server it belongs to
                guild = (await client.get(webhook)).json().get("guild_id")
        return f"https://discord.com/channels/{guild}/{data['channel_id']}/{data['id']}"