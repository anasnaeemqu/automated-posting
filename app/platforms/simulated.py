import asyncio
import uuid

from .base import Platform


class FakeOne(Platform):
    name = "Fake One"

    async def publish(self, message: str) -> str:
        await asyncio.sleep(0.2)
        return f"https://example.com/one/{uuid.uuid4().hex[:8]}"


class FakeTwo(Platform):
    name = "Fake Two"

    async def publish(self, message: str) -> str:
        await asyncio.sleep(0.2)
        return f"https://example.com/two/{uuid.uuid4().hex[:8]}"


class FakeThree(Platform):
    name = "Fake Three"

    async def publish(self, message: str) -> str:
        raise RuntimeError("Authentication failed")  # on purpose, to test failures