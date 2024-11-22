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
                if (
                    self._main_page is None
                    or len(self._main_page.find(".error").eq(0)) > 0
                ):
                    self._valid = False
                else:
                    self._valid = True
            except InvalidURLError:
                self._valid = False

    def as_parsed(self) -> PAnimeAniDB:
        return PAnimeAniDB(
            url=self.url,
            anidb_id=self.anidb_id,
            airing_start=self.airing_start,
            airing_end=self.airing_end,
        )

    @property
    def valid(self) -> bool:
        return self._valid

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
        return self._main_page.find(".i_resource_mal").attr["href"]
