from functools import cached_property

from aiohttp import ClientSession

from aoq_automation.database.models import PAnimeMAL

from ..utils import InvalidURLError, default, pget, text_without_span
from ..pageparser import PageParser


class MALPageParser(PageParser):
    async def load_pages(self) -> None:
        async with ClientSession() as session:
            try:
                self._main_page = await pget(session=session, url=self._url)
                self._stats_page = await pget(session=session, url=self.stats_url)
                self._valid = True
            except InvalidURLError:
                pass

    def as_parsed(self) -> PAnimeMAL:
        return PAnimeMAL(
            url=self.url,
            title_en=self.title_en,
            poster_url=self.poster_url,
            rating=self.rating,
            ratings_count=self.ratings_count,
            favorites=self.favorites,
            popularity=self.popularity,
            ranked=self.ranked,
            plan_to_watch=self.plan_to_watch,
            completed=self.completed,
            watching=self.watching,
            dropped=self.dropped,
            on_hold=self.on_hold,
        )

    @cached_property
    def stats_url(self) -> str:
        return self._main_page.find('a:contains("Stats")').attr.href

    @cached_property
    def title_ro(self) -> str:
        return self._main_page.find("div.h1-title h1.title-name > strong").eq(0).text()

    @cached_property
    @default(
        "https://moe.shikimori.one/uploads/poster/animes/49603"
        "/main-60ad2591305ea0490f90fd90f48c63d2.webp"
    )
    def poster_url(self) -> str:
        return (
            self._main_page.find('.leftside a img[itemprop="image"]')
            .eq(0)
            .attr["data-src"]
        )

    @cached_property
    def title_en(self) -> str:
        return text_without_span(
            self._main_page.find('.js-alternative-titles span:contains("English:")').eq(
                0
            )
        )

    @cached_property
    @default(5)
    def rating(self) -> float:
        return float(self._main_page.find('span[itemprop="ratingValue"]').text())

    @cached_property
    @default(0)
    def ratings_count(self) -> int:
        return int(
            self._main_page.find('span[itemprop="ratingCount"]').text().replace(",", "")
        )

    def _get_int_from_spaceit_pad(
        self, span_content: str, stats_page: bool = False
    ) -> int:
        return int(
            text_without_span(
                (self._stats_page if stats_page else self._main_page).find(
                    f'.spaceit_pad span:contains("{span_content}")'
                )
            )
        )

    @cached_property
    @default(0)
    def favorites(self) -> int:
        return self._get_int_from_spaceit_pad("Favorites:")

    @cached_property
    @default(0)
    def popularity(self) -> int:
        return self._get_int_from_spaceit_pad("Popularity:")

    @cached_property
    @default(100000)
    def ranked(self) -> int:
        return self._get_int_from_spaceit_pad("Ranked:")

    @cached_property
    @default(0)
    def watching(self) -> int:
        return self._get_int_from_spaceit_pad("Watching:", stats_page=True)

    @cached_property
    @default(0)
    def completed(self) -> int:
        return self._get_int_from_spaceit_pad("Completed:", stats_page=True)

    @cached_property
    @default(0)
    def plan_to_watch(self) -> int:
        return self._get_int_from_spaceit_pad("Plan to Watch:", stats_page=True)

    @cached_property
    @default(0)
    def dropped(self) -> int:
        return self._get_int_from_spaceit_pad("Dropped:", stats_page=True)

    @cached_property
    @default(0)
    def on_hold(self) -> int:
        return self._get_int_from_spaceit_pad("On-Hold:", stats_page=True)
