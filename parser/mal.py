import re
import urllib
from urllib.parse import urlparse
from utils import pget
from typing import *

class Page:
    @classmethod
    async def from_url(cls, url: str):
        result = cls()
        result.url = url
        parsed = urlparse(url)
        if parsed.netloc != 'myanimelist.net':
            return None
        if re.match(r'^/anime/(\d*)$', parsed.path) is None:
            return None
        result.page = await pget(url=url)
        if result.page is None:
            return None
        if result.page.find('.error404').eq(0) != []:
            return None
        return result


    @classmethod
    async def from_shiki_url(cls, shiki_url: str):
        anime_id = re.match('^\\/animes\\/([0-9]*)-.*$', urlparse(shiki_url).path).group(1)
        return await cls.from_url(f'https://myanimelist.net/anime/{anime_id}')


    def get_poster(self) -> str:
        if not hasattr(self, 'poster'):
            self.poster = self.page.find('.leftside a img.lazyloaded').eq(0).attr.src
        return self.poster


    def get_titles(self) -> str:
        if not hasattr(self, 'titles'):
            ro = self.page.find('div.h1-title h1.title-name > strong').eq(0).text()
            en = self.page.find('.js-alternative-titles span:contains("English:")').eq(0).parent().remove('span').text()
            self.titles = {
                'ro': ro,
                'en': en,
            }
        return self.titles


def search(query: str) -> List[str]:
    url = f'https://myanimelist.net/search/all?q={urllib.quote_plus(query)}&cat=all'
    page = pget(url)
    if page is None:
        return []
    return [a.attr.href for a in page.find('h2#anime ~ article a.hoverinfo_trigger').items()]
