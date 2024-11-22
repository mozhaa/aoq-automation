from datetime import datetime
from pathlib import Path

import pytest
from pyquery import PyQuery

from aoq_automation.webparse.anidb import AniDBPageParser


@pytest.mark.asyncio
async def test_page_1():
    url = "https://anidb.net/anime/13734"
    page = AniDBPageParser(url)
    await page.load_pages()
    assert page.valid


@pytest.mark.asyncio
async def test_page_2():
    url = "https://anidb.net/anime/222"
    page = AniDBPageParser(url)
    await page.load_pages()
    assert page.valid


@pytest.mark.asyncio
async def test_page_3():
    url = "https://anidb.net/anime/4112"
    page = AniDBPageParser(url)
    await page.load_pages()
    assert page.valid


@pytest.fixture
def page_1():
    page = AniDBPageParser("https://anidb.net/anime/13734")
    with open(
        Path(".") / "tests" / "files" / "anidb-grand-blue.html",
        "r",
        encoding="utf-8",
    ) as f:
        page._main_page = PyQuery(f.read())
    return page


def test_airing_start(page_1):
    assert page_1.airing_start == datetime(2018, 7, 14)


def test_airing_end(page_1):
    assert page_1.airing_end == datetime(2018, 9, 29)


def test_anidb_id(page_1):
    assert page_1.anidb_id == 13734


def test_mal_url(page_1):
    assert page_1.mal_url == "https://myanimelist.net/anime/37105"
