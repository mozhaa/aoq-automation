from dataclasses import dataclass

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey

from aoq_automation.telegram.filters import AsUnknownUrl


@dataclass
class MockMessage:
    text: str


@pytest.mark.asyncio
async def test_unknown_url():
    urls = [
        "https://anidb.net/anime/14603",
        "https://myanimelist.net/anime/24415/Kuroko_no_Basket_3rd_Season",
        "https://shikimori.one/animes/52991-sousou-no-frieren",
        "https://shikimori.one/animes/y590-kage-kara-mamoru",
        "https://anidb.net/perl-bin/animedb.pl?show=anime&aid=4112",
        "https://anidb.net/anime/10320",
        "https://myanimelist.net/anime/9047",
    ]

    for url in urls:
        print(f"Testing {url}...")
        state = FSMContext(storage=MemoryStorage(), key=StorageKey(0, 0, 0))
        message = MockMessage(text=url)
        result = await AsUnknownUrl(message, state)
        assert result
