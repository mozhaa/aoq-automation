from pathlib import Path

import pytest
from pyquery import PyQuery

from aoq_automation.webparse.shiki import ShikiPageParser


@pytest.mark.asyncio
async def test_page_1():
    url = "https://shikimori.one/animes/y28851-koe-no-katachi"
    page = ShikiPageParser(url)
    await page.load_pages()
    assert page.title_ro == "Koe no Katachi"
    assert page.title_ru == "Форма голоса"


@pytest.mark.asyncio
async def test_page_2():
    url = "https://shikimori.one/animes/49603-trip-trap"
    page = ShikiPageParser(url)
    await page.load_pages()
    assert page.title_ro == "Trip!-Trap!"
    assert page.title_ru


@pytest.mark.asyncio
async def test_page_3():
    url = "https://shikimori.one/animes/151231231"
    page = ShikiPageParser(url)
    await page.load_pages()
    assert not page.valid


@pytest.fixture
def page_1():
    page = ShikiPageParser("https://shikimori.one/animes/y590-kage-kara-mamoru")
    with open(
        Path(".") / "tests" / "files" / "shiki-kage-kara-mamoru.html",
        "r",
        encoding="utf-8",
    ) as f:
        page._main_page = PyQuery(f.read())
    return page


def test_rating(page_1):
    assert f"{page_1.rating:.2f}" == "6.53"


def test_rating_count(page_1):
    assert page_1.rating_count == 354


def test_watching(page_1):
    assert page_1.watching == 77


def test_completed(page_1):
    assert page_1.completed == 728


def test_plan_to_watch(page_1):
    assert page_1.plan_to_watch == 722


def test_dropped(page_1):
    assert page_1.dropped == 80


def test_on_hold(page_1):
    assert page_1.on_hold == 41


def test_title_ro(page_1):
    assert page_1.title_ro == "Kage kara Mamoru!"


def test_title_ru(page_1):
    assert page_1.title_ru == "Мамору выходит из тени!"


def test_favorites(page_1):
    assert page_1.favorites == 0


def test_comments(page_1):
    assert page_1.comments == 6


def test_poster_url(page_1):
    assert (
        page_1.poster_url
        == "https://moe.shikimori.one/uploads/poster/animes/590/a062e49ec7e8dc7cd207a85dc9b3a991.jpeg"
    )


def test_poster_thumbnail_url(page_1):
    assert (
        page_1.poster_thumbnail_url
        == "https://moe.shikimori.one/uploads/poster/animes/590/main_alt-5605f29ae19a25d17ea5d456a29ff57d.jpeg"
    )
