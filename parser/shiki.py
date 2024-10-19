import re
from urllib.parse import urlparse
from utils import pget
from typing import *

class Page:
    @classmethod
    async def from_url(cls, url: str):
        result = cls()
        result.url = url
        parsed = urlparse(url)
        if parsed.netloc not in ['shikimori.one', 'shikimori.org', 'shikimori.net']:
            return None
        if re.match(r'^/animes/(\d*)(-.*)?$', parsed.path) is None:
            return None
        result.page = await pget(url=url)
        if result.page is None:
            return None
        if result.page.find('.error-404').eq(0) != []:
            return None
        return result


    @classmethod
    async def from_mal_url(cls, mal_url: str):
        anime_id = re.match('^/anime/([0-9]*)$', urlparse(mal_url).path).group(1)
        return await cls.from_url(f'https://shikimori.one/animes/{anime_id}')


    def get_poster(self) -> str:
        if not hasattr(self, 'poster'):
            self.poster = self.page.find('.c-poster .b-image img').eq(0).attr.src
        return self.poster


    def get_titles(self) -> Dict[str, str]:
        if not hasattr(self, 'titles'):
            ru, ro = map(lambda s: s.strip(), self.page.find('header.head > h1').eq(0).text().split('/'))
            self.titles = {
                'ro': ro,
                'ru': ru,
            }
        return self.titles


    # def get_airings(self)