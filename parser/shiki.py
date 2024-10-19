import re
import logging
from urllib.parse import urlparse
from utils import pget
from typing import *

logger = logging.getLogger(__name__)

class Page:
    @classmethod
    async def from_url(cls, url: str):
        logger.debug('from_url("%s")', url)
        return (await cls.from_shiki_url(url)) or (await cls.from_mal_url(url))
    
    @classmethod
    async def from_shiki_url(cls, shiki_url: str):
        logger.debug('  trying from_shiki_url("%s")', shiki_url)
        result = cls()
        result.url = shiki_url
        parsed = urlparse(shiki_url)
        if parsed.netloc not in ['shikimori.one', 'shikimori.org', 'shikimori.net']:
            logger.debug('      is not shiki url')
            return None
        shiki_match = re.match('^/animes/(\d*)(-.*)?$', parsed.path)
        if shiki_match is None:
            logger.debug('      is not anime url')
            return None
        result._anime_id = int(shiki_match.group(1))
        result.page = await pget(url=shiki_url)
        if result.page is None:
            logger.debug('      is unreachable page')
            return None
        if result.page.find('.error-404').eq(0) != []:
            logger.debug('      is invalid anime page')
            return None
        logger.debug('      success')
        return result


    @classmethod
    async def from_mal_url(cls, mal_url: str):
        logger.debug('  trying from_mal_url("%s")', mal_url)
        mal_match = re.match('^/anime/([0-9]*)$', urlparse(mal_url).path)
        if mal_match is None:
            logger.debug('      is not mal anime url')
            return None
        anime_id = mal_match.group(1)
        return await cls.from_shiki_url(f'https://shikimori.one/animes/{anime_id}')


    @property
    def poster(self):
        if not hasattr(self, '_poster'):
            self._poster = self.page.find('.c-poster .b-image img').eq(0).attr.src
        return self._poster
        
    @property
    def titles(self):
        if not hasattr(self, '_titles'):
            ru, ro = map(lambda s: s.strip(), self.page.find('header.head > h1').eq(0).text().split('/'))
            self._titles = {
                'ro': ro,
                'ru': ru,
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
    
    @property
    def anime_id(self):
        return self._anime_id
    
    @property
    def rating(self):
        if not hasattr(self, '_rating'):
            scores_container = self.page.find('#rates_scores_stats').eq(0)
            total_people = 0
            total_rating = 0
            for line in scores_container.find('.line').items():
                score = int(line.find('.x_label').eq(0).text())
                bar_count = int(line.find('.bar-container > .bar').attr.title)
                total_people += bar_count
                total_rating += bar_count * score
            self._rating = total_rating / total_people if total_people > 0 else 0
        return self._rating
    
    # def get_airings(self)