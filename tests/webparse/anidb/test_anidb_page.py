from datetime import datetime
from pathlib import Path

import pytest
from pyquery import PyQuery

from aoq_automation.webparse.anidb import AniDBPageParser


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_page_1():
    url = "https://anidb.net/anime/13734"
    page = AniDBPageParser(url)
    await page.load_pages()
    assert page.is_valid()


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_page_2():
    url = "https://anidb.net/anime/222"
    page = AniDBPageParser(url)
    await page.load_pages()
    assert page.is_valid()


@pytest.mark.asyncio
@pytest.mark.webtest
async def test_page_3():
    url = "https://anidb.net/anime/4112"
    page = AniDBPageParser(url)
    await page.load_pages()
    assert page.is_valid()


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


@pytest.fixture
def page_2():
    page = AniDBPageParser("https://anidb.net/anime/14603")
    with open(
        Path(".") / "tests" / "files" / "anidb-dumbbell.html",
        "r",
        encoding="utf-8",
    ) as f:
        page._main_page = PyQuery(f.read())
    return page


def test_airing_start(page_1, page_2):
    assert page_1.airing_start == datetime(2018, 7, 14)
    assert page_2.airing_start == datetime(2019, 7, 3)


def test_airing_end(page_1, page_2):
    assert page_1.airing_end == datetime(2018, 9, 29)
    assert page_2.airing_end == datetime(2019, 9, 18)


def test_anidb_id(page_1, page_2):
    assert page_1.anidb_id == 13734
    assert page_2.anidb_id == 14603


def test_mal_url(page_1, page_2):
    assert page_1.mal_url == "https://myanimelist.net/anime/37105"
    assert page_2.mal_url == "https://myanimelist.net/anime/39026"
