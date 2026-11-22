from abc import ABC, abstractmethod


class Platform(ABC):
    name: str
    check_public: bool = True

    @abstractmethod
    async def publish(self, message: str) -> str:
        """Post the message. Return the URL of the new post."""