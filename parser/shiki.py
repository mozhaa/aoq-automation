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
    def poster_thumbnail_url(self):
        if not hasattr(self, '_poster_thumbnail_url'):
            self._poster_thumbnail_url = self.page.find('.c-poster .b-image img').eq(0).attr.src
        return self._poster_thumbnail_url
        
    @property
    def poster_url(self):
        if not hasattr(self, '_poster_url'):
            self._poster_url = self.page.find('.c-poster .b-image').eq(0).attr['data-href']
        return self._poster_url
        
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
            stats = eval(self.page.find('#rates_scores_stats').eq(0).attr['data-stats'])
            self._rating = sum([int(stat[0]) * stat[1] for stat in stats]) / sum([stat[1] for stat in stats])
        return self._rating
    
    @property
    def lists(self):
        if not hasattr(self, '_lists'):
            stats = eval(self.page.find('#rates_statuses_stats').eq(0).attr['data-stats'])
            self._lists = dict(stats)
        return self._lists
        
    @property
    def watching(self):
        return self.lists.get('watching')
    
    @property
    def completed(self):
        return self.lists.get('completed')
    
    @property
    def plan_to_watch(self):
        return self.lists.get('planned')
    
    @property
    def dropped(self):
        return self.lists.get('dropped')
    
    @property
    def on_hold(self):
        return self.lists.get('on_hold')
    
    # @property
    # def (self):
    # def get_airings(self)