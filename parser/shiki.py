import re
from pathlib import PurePosixPath
from urllib.parse import urlparse
from functools import cached_property

from utils import pget
from typing import *
from parser.mal import MALUrlParser


class ShikiUrlParser:
    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.path_parts = PurePosixPath(self.parsed_url.path).parts

    def is_shiki_url(self) -> bool:
        return self.parsed_url.netloc in [
            "shikimori.one",
            "shikimori.org",
            "shikimori.net",
        ]

    def is_shiki_anime_url(self) -> bool:
        return (
            len(self.path_parts) >= 2
            and self.path_parts[0] == "animes"
            and self.path_parts[1].split("-")[0].isdigit()
        )

    def is_valid(self) -> bool:
        return self.is_shiki_url() and self.is_shiki_anime_url()

    def get_mal_id(self) -> int:
        return int(self.path_parts[1].split("-")[0])

    def to_mal_url(self) -> str:
        return f"https://myanimelist.net/anime/{self.get_mal_id()}"

    def get_clean_url(self) -> str:
        return f"https://shikimori.one/animes/{self.path_parts[1]}"


class MALAnimeParser:
    async def __init__(self, url: str):
        self.url_parser = ShikiUrlParser(url)
        if not self.url_parser.is_valid():
            raise ValueError(f'"{url}" is not valid Shiki url')
        self.page = await self.load_page(url)
        self.stats_page = await self.load_page(self.stats_url)

    async def load_page(self, url: str):
        page = await pget(url)
        if page is None or len(page.find(".error-404").eq(0)) > 0:
            raise ValueError(f'"{url}" is not valid Shiki url')
        return page

    @cached_property
    def url(self) -> str:
        return self.url_parser.get_clean_url()

    @classmethod
    async def from_mal_url(cls, url: str):
        url_parser = MALUrlParser(url)
        if not url_parser.is_valid():
            raise ValueError(f'"{url}" is not valid MAL url')
        return cls(url_parser.to_shiki_url())

    @cached_property
    def poster_thumbnail_url(self):
        return self.page.find(".c-poster .b-image img").eq(0).attr.src

    @cached_property
    def poster_url(self):
        return self.page.find(".c-poster .b-image").eq(0).attr["data-href"]

    @cached_property
    def titles(self):
        return dict(zip(['ru', 'ro'], self.page.find("header.head > h1").eq(0).text().split("/")))

    @cached_property
    def title_ru(self):
        return self.titles['ru']

    @cached_property
    def title_ro(self):
        return self.titles['ro']

    @cached_property
    def mal_id(self):
        return self.url_parser.get_mal_id()

    @cached_property
    def scores_stats(self):
        return eval(self.page.find("#rates_scores_stats").eq(0).attr["data-stats"])

    @cached_property
    def rating(self):
        return sum([int(stat[0]) * stat[1] for stat in self.scores_stats]) / self.rating_count

    @cached_property
    def rating_count(self):
        return sum([stat[1] for stat in self.scores_stats])

    @cached_property
    def statuses_stats(self):
        return eval(self.page.find("#rates_statuses_stats").eq(0).attr["data-stats"])

    @cached_property
    def watching(self):
        return self.statuses_stats.get("watching")

    @cached_property
    def completed(self):
        return self.statuses_stats.get("completed")

    @cached_property
    def plan_to_watch(self):
        return self.statuses_stats.get("planned")

    @cached_property
    def dropped(self):
        return self.statuses_stats.get("dropped")

    @cached_property
    def on_hold(self):
        return self.statuses_stats.get("on_hold")

    @cached_property
    def favorites(self):
        return int(self.page.find(".b-favoured .subheadline .count").eq(0).text())

    @cached_property
    def comments(self):
        return int(self.page.find('[title="Все комментарии"] > .count').eq(0).text())