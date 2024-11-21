from pathlib import Path

import pytest
from pyquery import PyQuery

from aoq_automation.webparse.mal import MALPageParser


@pytest.mark.asyncio
async def test_page_1():
    url = "https://myanimelist.net/anime/56964"
    page = MALPageParser(url)
    await page.load_pages()
    assert (
        page.stats_url
        == "https://myanimelist.net/anime/56964/Raise_wa_Tanin_ga_Ii/stats"
    )
    assert page.title_ro == "Raise wa Tanin ga Ii"

    
@pytest.mark.asyncio
async def test_page_2():
    url = "https://myanimelist.net/anime/457"
    page = MALPageParser(url)
    await page.load_pages()
    assert page.stats_url == "https://myanimelist.net/anime/457/Mushishi/stats"
    assert page.title_ro == "Mushishi"


@pytest.mark.asyncio
async def test_page_3():
    url = "https://myanimelist.net/anime/52991"
    page = MALPageParser(url)
    await page.load_pages()
    assert (
        page.stats_url == "https://myanimelist.net/anime/52991/Sousou_no_Frieren/stats"
    )
    assert page.title_ro == "Sousou no Frieren"


@pytest.fixture
def page_1():
    page = MALPageParser("https://myanimelist.net/anime/57181")
    with open(Path(".") / "tests" / "files" / "mal-ao-no-hako.html", "r") as f:
        page._main_page = PyQuery(f.read())
    with open(Path(".") / "tests" / "files" / "mal-stats-ao-no-hako.html", "r") as f:
        page._stats_page = PyQuery(f.read())
    return page


def test_url(page_1):
    assert page_1.url == "https://myanimelist.net/anime/57181"


def test_stats_url(page_1):
    assert page_1.stats_url == "https://myanimelist.net/anime/57181/Ao_no_Hako/stats"


def test_poster_url(page_1):
    assert (
        page_1.poster_url == "https://cdn.myanimelist.net/images/anime/1341/145349.jpg"
    )


def test_rating(page_1):
    assert page_1.rating == 8.4


def test_ratings_count(page_1):
    assert page_1.ratings_count == 16830


def test_ranked(page_1):
    assert page_1.ranked == 193


def test_popularity(page_1):
    assert page_1.popularity == 1807


def test_favorites(page_1):
    assert page_1.favorites == 918


def test_title_en(page_1):
    assert page_1.title_en == "Blue Box"


def test_title_ro(page_1):
    assert page_1.title_ro == "Ao no Hako"


def test_watching(page_1):
    assert page_1.watching == 71897


def test_completed(page_1):
    assert page_1.completed == 11


def test_on_hold(page_1):
    assert page_1.on_hold == 1061


def test_dropped(page_1):
    assert page_1.dropped == 835


def test_plan_to_watch(page_1):
    assert page_1.plan_to_watch == 54638
