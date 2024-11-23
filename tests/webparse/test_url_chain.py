from dataclasses import dataclass

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey

from aoq_automation.telegram.filters import AsUnknownUrl


@dataclass
class MockMessage:
    text: str


async def process_url(url: str) -> bool:
    state = FSMContext(storage=MemoryStorage(), key=StorageKey(0, 0, 0))
    message = MockMessage(text=url)
    return await AsUnknownUrl(message, state)


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_redirect_shiki_1():
    urls = [
        "https://shikimori.one/animes/y590-kage-kara-mamoru",
        "https://anidb.net/perl-bin/animedb.pl?show=anime&aid=4112",
        "https://myanimelist.net/anime/590",
    ]

    for url in urls:
        print(f"Testing {url}...")
        assert await process_url(url)


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_redirect_shiki_2():
    urls = [
        "https://shikimori.one/animes/9969",
        "https://myanimelist.net/anime/9969",
        "https://anidb.net/anime/8126",
    ]

    for url in urls:
        print(f"Testing {url}...")
        assert await process_url(url)


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_random_1():
    urls = [
        "https://anidb.net/anime/12337",
        "https://myanimelist.net/anime/33889",
        "https://shikimori.one/animes/33889",
    ]

    for url in urls:
        print(f"Testing {url}...")
        assert await process_url(url)


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_random_2():
    urls = [
        "https://anidb.net/anime/17156",
        "https://myanimelist.net/anime/50917",
        "https://shikimori.one/animes/50917",
    ]

    for url in urls:
        print(f"Testing {url}...")
        assert await process_url(url)
