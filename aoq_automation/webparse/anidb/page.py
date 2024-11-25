from datetime import datetime
from functools import cached_property

from aiohttp import ClientSession

from aoq_automation.database.models import PAnimeAniDB

from ..pageparser import PageParser
from ..utils import InvalidURLError, default, pget
from .url import AniDBUrlParser


class AniDBPageParser(PageParser):
    async def load_pages(self) -> None:
        async with ClientSession() as session:
            try:
                self._main_page = await pget(session=session, url=self.url)
                if len(self._main_page.find(".error").eq(0)) == 0:
                    self._valid = True
                    return
            except InvalidURLError:
                pass

    def as_parsed(self) -> PAnimeAniDB:
        return PAnimeAniDB(
            url=self.url,
            anidb_id=self.anidb_id,
            airing_start=self.airing_start,
            airing_end=self.airing_end,
        )

    @property
    def anidb_id(self) -> int:
        return AniDBUrlParser(self.url).anidb_id

    def _parse_datetime(self, s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%d")

    @cached_property
    @default(datetime(1970, 1, 1))
    def airing_start(self) -> datetime:
        return self._parse_datetime(
            self._main_page.find('span[itemprop="startDate"]').attr["content"]
        )

    @cached_property
    @default(None)
    def airing_end(self) -> datetime:
        return self._parse_datetime(
            self._main_page.find('span[itemprop="endDate"]').attr["content"]
        )

    @cached_property
    def mal_url(self) -> str:
        mal_buttons = self._main_page.find(".i_resource_mal")
        href = mal_buttons.attr["href"]
        if href is not None:
            return href
        else:
            return mal_buttons.siblings("a").eq(0).attr["href"]
