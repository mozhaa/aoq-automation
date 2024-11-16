from aiohttp import ClientSession
from ..utils import pget, text_without_span
from aoq_automation.database.models import PAnimeMAL
from functools import cached_property


class MALPageParser:
    def __init__(self, url: str) -> None:
        self._url = url

    async def load_pages(self) -> None:
        async with ClientSession() as session:
            try:
                self._main_page = await pget(session=session, url=self._url)
                self._stats_page = await pget(session=session, url=self.stats_url)
                self._valid = True
            except:
                self._valid = False

    @property
    def valid(self) -> bool:
        return self._valid

    @property
    def url(self) -> str:
        return self._url

    @cached_property
    def stats_url(self) -> str:
        return self._main_page.find('a:contains("Stats")').attr.href

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
    def title_ro(self) -> str:
        return self._main_page.find("div.h1-title h1.title-name > strong").eq(0).text()

    @cached_property
    def poster_url(self) -> str:
        return (
            self._main_page.find('.leftside a img[itemprop="image"]')
            .eq(0)
            .attr["data-src"]
        )

    @cached_property
    def title_en(self):
        return text_without_span(
            self._main_page.find('.js-alternative-titles span:contains("English:")').eq(
                0
            )
        )

    @cached_property
    def rating(self):
        return float(self._main_page.find('span[itemprop="ratingValue"]').text())

    @cached_property
    def ratings_count(self):
        return int(
            self._main_page.find('span[itemprop="ratingCount"]').text().replace(",", "")
        )

    def _get_int_from_spaceit_pad(self, span_content: str, stats_page: bool = False):
        return int(
            text_without_span(
                (self._stats_page if stats_page else self._main_page).find(
                    f'.spaceit_pad span:contains("{span_content}")'
                )
            )
        )

    @cached_property
    def favorites(self):
        return self._get_int_from_spaceit_pad("Favorites:")

    @cached_property
    def popularity(self):
        return self._get_int_from_spaceit_pad("Popularity:")

    @cached_property
    def ranked(self):
        return self._get_int_from_spaceit_pad("Ranked:")

    @cached_property
    def watching(self):
        return self._get_int_from_spaceit_pad("Watching:", stats_page=True)

    @cached_property
    def completed(self):
        return self._get_int_from_spaceit_pad("Completed:", stats_page=True)

    @cached_property
    def plan_to_watch(self):
        return self._get_int_from_spaceit_pad("Plan to Watch:", stats_page=True)

    @cached_property
    def dropped(self):
        return self._get_int_from_spaceit_pad("Dropped:", stats_page=True)

    @cached_property
    def on_hold(self):
        return self._get_int_from_spaceit_pad("On-Hold:", stats_page=True)
