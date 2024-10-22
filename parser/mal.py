from urllib import quote_plus
from urllib.parse import urlparse
from pathlib import PurePosixPath
from functools import cached_property
from pyquery import PyQuery

from utils import pget
from typing import *
from db.types import *
from parser.shiki import ShikiUrlParser


class MALUrlParser:
    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.path_parts = PurePosixPath(self.parsed_url.path).parts

    def is_mal_url(self) -> bool:
        return self.parsed_url.netloc == 'myanimelist.net'

    def is_mal_anime_url(self) -> bool:
        return (
            len(self.path_parts) >= 2
            and self.path_parts[0] == 'anime'
            and self.path_parts[1].isdigit()
        )

    def is_valid(self) -> bool:
        return self.is_mal_url() and self.is_mal_anime_url()

    def get_mal_id(self) -> int:
        return int(self.path_parts[1])

    def to_shiki_url(self) -> str:
        return f'https://shikimori.one/animes/{self.get_mal_id()}'


class MALAnimeParser:
    async def __init__(self, url: str):
        self.url_parser = MALUrlParser(url)
        if not self.url_parser.is_valid():
            raise ValueError(f'"{url}" is not valid MAL url')
        self.page = await self.load_page(url)
        self.stats_page = await self.load_page(self.stats_url)

    async def load_page(self, url: str):
        page = await pget(url)
        if page is None or len(page.find('.error404').eq(0)) > 0:
            raise ValueError(f'"{url}" is not valid MAL url')
        return page

    @cached_property
    def url(self) -> str:
        return self.page.find('a:contains("Details")').attr.href

    @cached_property
    def stats_url(self) -> str:
        return self.page.find('a:contains("Stats")').attr.href

    @classmethod
    async def from_shiki_url(cls, url: str):
        url_parser = ShikiUrlParser(url)
        if not url_parser.is_valid():
            raise ValueError(f'"{url}" is not valid Shiki url')
        return cls(url_parser.to_mal_url())

    @cached_property
    def poster_url(self) -> str:
        # TODO: fix (returning None currently)
        return self.page.find('.leftside a img.lazyloaded').eq(0).attr.src

    @cached_property
    def titles(self) -> str:
        return {
            'ro': self.page.find('div.h1-title h1.title-name > strong').eq(0).text(),
            'en': get_text(
                self.page.find('.js-alternative-titles span:contains("English:")').eq(0)
            ),
        }

    @cached_property
    def title_en(self):
        return self.titles.get('en')

    @cached_property
    def title_ro(self):
        return self.titles.get('ro')

    @cached_property
    def title_ru(self):
        return self.titles.get('ru')

    @cached_property
    def mal_id(self):
        return self.url_parser.get_mal_id()

    @cached_property
    def rating(self):
        return float(self.page.find('[itemprop="ratingValue"]').text())

    def get_int_from_spaceit_pad(self, span_content: str):
        return int(get_text(self.page.find(f'.spaceit_pad span:contains("{span_content}")')))

    @cached_property
    def favorites(self):
        return self.get_int_from_spaceit_pad('Favorites:')

    @cached_property
    def popularity(self):
        return self.get_int_from_spaceit_pad('Popularity:')

    @cached_property
    def ranked(self):
        return self.get_int_from_spaceit_pad('Ranked:')

    @cached_property
    def watching(self):
        return self.get_int_from_spaceit_pad('Watching:')

    @cached_property
    def completed(self):
        return self.get_int_from_spaceit_pad('Completed:')

    @cached_property
    def plan_to_watch(self):
        return self.get_int_from_spaceit_pad('Plan to Watch:')

    @cached_property
    def dropped(self):
        return self.get_int_from_spaceit_pad('Dropped:')

    @cached_property
    def on_hold(self):
        return self.get_int_from_spaceit_pad('On-Hold:')

    @cached_property
    def qitems(self):
        qitems = []
        # .opnening - copied from mal page (not mistake)
        ops = self.page.find('.theme-songs.opnening .theme-song-artist').parent().items()
        eds = self.page.find('.theme-songs.ending .theme-song-artist').parent().items()
        qitem_amounts_by_type = {}
        for item, item_type in zip(ops, [0] * len(ops)) + zip(eds, [1] * len(eds)):
            qitem = QItem()
            qitem_amounts_by_type[item_type] = 1 + qitem_amounts_by_type.get(item_type, 0)
            qitem.num = qitem_amounts_by_type[item_type]
            qitem.item_type = item_type
            qitem.song_artist = item.find('.theme-song-artist').text()[3:]
            qitem.episodes = item.find('.theme-song-episode').text()[1:-1]
            qitem.song_name = item.clone().remove('span').text()[1:-1]
            qitems.append(qitem)
        return qitems


def search(query: str) -> List[str]:
    url = f'https://myanimelist.net/search/all?q={quote_plus(query)}&cat=all'
    page = pget(url)
    if page is None:
        return []
    return [
        a.attr.href for a in page.find('h2#anime ~ article a.hoverinfo_trigger').items()
    ]


def get_text(element) -> str:
    return (
        element.parent()
        .clone()
        .remove('span')
        .text()
        .strip()
        .replace(',', '')
        .replace('#', '')
        .replace(':', '')
        .split('\n')[0]
    )
