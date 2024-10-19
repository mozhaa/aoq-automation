import re
import urllib
import logging
from urllib.parse import urlparse
from utils import pget
from typing import *

logger = logging.getLogger(__name__)

class Page:
    @classmethod
    async def from_url(cls, url: str):
        logger.debug('from_url("%s")', url)
        return (await cls.from_mal_url(url)) or (await cls.from_shiki_url(url))
    
    @classmethod
    async def from_mal_url(cls, mal_url: str):
        logger.debug('  trying from_mal_url("%s")', mal_url)
        result = cls()
        result.url = mal_url
        parsed = urlparse(mal_url)
        if parsed.netloc != 'myanimelist.net':
            logger.debug('      is not mal url')
            return None
        if re.match(r'^/anime/(\d*)$', parsed.path) is None:
            logger.debug('      is not anime')
            return None
        result.page = await pget(url=mal_url)
        if result.page is None:
            logger.debug('      is unreachable page')
            return None
        if result.page.find('.error404').eq(0) != []:
            logger.debug('      is invalid anime page')
            return None
        logger.debug('      success')
        return result


    @classmethod
    async def from_shiki_url(cls, shiki_url: str):
        logger.debug('  trying from_shiki_url("%s")', shiki_url)
        shiki_match = re.match('^\\/animes\\/([0-9]*)-.*$', urlparse(shiki_url).path)
        if shiki_match is None:
            logger.debug('      is not shiki anime url')
            return None
        anime_id = shiki_match.group(1)
        return await cls.from_mal_url(f'https://myanimelist.net/anime/{anime_id}')

    @property
    def poster(self) -> str:
        if not hasattr(self, '_poster'):
            self._poster = self.page.find('.leftside a img.lazyloaded').eq(0).attr.src
        return self._poster

    @property
    def titles(self) -> str:
        if not hasattr(self, '_titles'):
            ro = self.page.find('div.h1-title h1.title-name > strong').eq(0).text()
            en = self.page.find('.js-alternative-titles span:contains("English:")').eq(0).parent().clone().remove('span').text()
            self._titles = {
                'ro': ro,
                'en': en,
            }
        return self._titles

    @property
    def title_en(self):
        return self.titles.get('en')
    
    @property
    def title_ro(self):
        return self.titles.get('ro')
    
    @property
    def title_ru(self):
        return self.titles.get('ru')


def search(query: str) -> List[str]:
    url = f'https://myanimelist.net/search/all?q={urllib.quote_plus(query)}&cat=all'
    page = pget(url)
    if page is None:
        return []
    return [a.attr.href for a in page.find('h2#anime ~ article a.hoverinfo_trigger').items()]
