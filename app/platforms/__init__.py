from .bluesky import BlueskyPlatform
from .devto import DevToPlatform
from .discord import DiscordPlatform
from .dpaste import DpastePlatform
from .gist import GistPlatform

PLATFORMS = [
    DevToPlatform(),
    GistPlatform(),
    BlueskyPlatform(),
    DpastePlatform(),
    DiscordPlatform(),
]