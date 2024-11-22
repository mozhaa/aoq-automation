from functools import cached_property
from typing import *

from aiohttp import ClientSession

from aoq_automation.database.models import PAnimeShiki

from ...webparse.utils import InvalidURLError, default, pget


class ShikiPageParser:
    def __init__(self, url: str) -> None:
        self._url = url

    async def load_pages(self) -> None:
        async with ClientSession() as session:
            try:
                self._main_page = await pget(session=session, url=self.url)
                if (
                    self._main_page is None
                    or len(self._main_page.find(".error-404").eq(0)) > 0
                ):
                    self._valid = False
                else:
                    self._valid = True
            except InvalidURLError:
                self._valid = False

    def as_parsed(self) -> PAnimeShiki:
        return PAnimeShiki(
            url=self.url,
            title_ru=self.title_ru,
            poster_url=self.poster_url,
            poster_thumb_url=self.poster_thumb_url,
            rating=self.rating,
            ratings_count=self.ratings_count,
            favorites=self.favorites,
            comments=self.comments,
            plan_to_watch=self.plan_to_watch,
            completed=self.completed,
            watching=self.watching,
            dropped=self.dropped,
            on_hold=self.on_hold,
        )

    @property
    def valid(self) -> bool:
        return self._valid

    @cached_property
    def url(self) -> str:
        return self._url

    @cached_property
    @default("https://shikimori.one/assets/globals/missing/main.png")
    def poster_thumbnail_url(self) -> str:
        return self._main_page.find(".c-poster .b-image img").eq(0).attr.src

    @cached_property
    @default("https://shikimori.one/assets/globals/missing/main.png")
    def poster_url(self) -> str:
        return self._main_page.find(".c-poster .b-image").eq(0).attr["data-href"]

    @cached_property
    def titles(self) -> List[str]:
        return list(map(lambda s: s.strip(), self._main_page.find("header.head > h1").eq(0).text().split("/")))

    @cached_property
    def title_ru(self) -> str:
        return self.titles[0]

    @cached_property
    def title_ro(self) -> str:
        return self.titles[-1]

    @cached_property
    def scores_stats(self) -> List[Tuple[str, int]]:
        return eval(
            self._main_page.find("#rates_scores_stats").eq(0).attr["data-stats"]
        )

    @cached_property
    @default(5)
    def rating(self) -> float:
        return (
            sum([int(stat[0]) * stat[1] for stat in self.scores_stats])
            / self.rating_count
        )

    @cached_property
    @default(0)
    def rating_count(self) -> int:
        return sum([stat[1] for stat in self.scores_stats])

    @cached_property
    def statuses_stats(self) -> Dict[str, int]:
        return {
            k: v
            for k, v in eval(
                self._main_page.find("#rates_statuses_stats").eq(0).attr["data-stats"]
            )
        }

    @cached_property
    @default(0)
    def watching(self) -> int:
        return self.statuses_stats.get("watching")

    @cached_property
    @default(0)
    def completed(self) -> int:
        return self.statuses_stats.get("completed")

    @cached_property
    @default(0)
    def plan_to_watch(self) -> int:
        return self.statuses_stats.get("planned")

    @cached_property
    @default(0)
    def dropped(self) -> int:
        return self.statuses_stats.get("dropped")

    @cached_property
    @default(0)
    def on_hold(self) -> int:
        return self.statuses_stats.get("on_hold")

    @cached_property
    @default(0)
    def favorites(self) -> int:
        el = self._main_page.find(".b-favoured .subheadline .count").eq(0)
        return int(el.text()) if len(el) > 0 else 0

    @cached_property
    @default(0)
    def comments(self) -> int:
        return int(self._main_page.find('[title="Все комментарии"] > .count').eq(0).text())
    
    @cached_property
    def anidb_url(self) -> str:
        return self._main_page.find(".b-external_link.anime_db .b-link").eq(0).attr["data-href"]
