from aiohttp import ClientSession
from .utils import pget
from functools import cached_property


class MALPageParser:
    def __init__(self, mal_url: str) -> None:
        self.mal_url = mal_url

    async def load_pages(self) -> None:
        async with ClientSession() as session:
            try:
                self.main_page = await pget(session=session, url=self.mal_url)
                self.stats_page = await pget(session=session, url=self.stats_url)
                self._valid = True
            except:
                self._valid = False

    @property
    def valid(self) -> bool:
        return self._valid

    @cached_property
    def stats_url(self) -> str:
        return self.main_page.find('a:contains("Stats")').attr.href

    @cached_property
    def title_ro(self) -> str:
        return self.main_page.find('div.h1-title h1.title-name > strong').eq(0).text()