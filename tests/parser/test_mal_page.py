from aoq_automation.parser import MALPageParser
import pytest


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
