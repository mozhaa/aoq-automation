import re
import urllib
import logging
from urllib.parse import urlparse
from utils import pget
from typing import *
from db.types import *

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
        mal_match = re.match('^/anime/(\d*)$', parsed.path)
        if mal_match is None:
            logger.debug('      is not anime')
            return None
        result._anime_id = int(mal_match.group(1))
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

    async def load_stats_page(self):
        self.stats_page = await pget(self.page.find('a:contains("Stats")').attr.href)

    @property
    def poster_url(self) -> str:
        if not hasattr(self, '_poster_url'):
            self._poster_url = self.page.find('.leftside a img.lazyloaded').eq(0).attr.src
        return self._poster_url

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
    
    @property
    def anime_id(self):
        return self._anime_id
    
    @property
    def poster_url(self) -> str:
        if not hasattr(self, '_poster_url'):
            self._poster_url = None
        return self._poster_url
    
    @property
    def rating(self):
        if not hasattr(self, '_rating'):
            self._rating = float(self.page.find('[itemprop="ratingValue"]').text())
        return self._rating
    
    @property
    def favorites(self):
        if not hasattr(self, '_favorites'):
            self._favorites = int(self.page.find('.spaceit_pad span:contains("Favorites:")').parent().clone().remove('span').text().strip().replace(',', '').split('\n')[0])
        return self._favorites
    
    @property
    def popularity(self):
        if not hasattr(self, '_popularity'):
            self._popularity = int(self.page.find('.spaceit_pad span:contains("Popularity:")').parent().clone().remove('span').text().strip().replace(',', '').replace('#', '').split('\n')[0])
        return self._popularity
    
    @property
    def ranked(self):
        if not hasattr(self, '_ranked'):
            self._ranked = int(self.page.find('.spaceit_pad span:contains("Ranked:")').parent().clone().remove('span').text().strip().replace('#', '').replace(',', '').split('\n')[0])
        return self._ranked
        
    @property
    def watching(self):
        if not hasattr(self, '_watching'):
            self._watching = int(self.stats_page.find('.spaceit_pad span:contains("Watching:")').parent().clone().remove('span').text().strip().replace(',', '').replace('#', '').split('\n')[0])
        return self._watching
    
    @property
    def completed(self):
        if not hasattr(self, '_completed'):
            self._completed = int(self.stats_page.find('.spaceit_pad span:contains("Completed:")').parent().clone().remove('span').text().strip().replace(',', '').replace('#', '').split('\n')[0])
        return self._completed
    
    @property
    def plan_to_watch(self):
        if not hasattr(self, '_plan_to_watch'):
            self._plan_to_watch = int(self.stats_page.find('.spaceit_pad span:contains("Plan to Watch:")').parent().clone().remove('span').text().strip().replace(',', '').replace('#', '').split('\n')[0])
        return self._plan_to_watch
    
    @property
    def dropped(self):
        if not hasattr(self, '_dropped'):
            self._dropped = int(self.stats_page.find('.spaceit_pad span:contains("Dropped:")').parent().clone().remove('span').text().strip().replace(',', '').replace('#', '').split('\n')[0])
        return self._dropped
    
    @property
    def on_hold(self):
        if not hasattr(self, '_on_hold'):
            self._on_hold = int(self.stats_page.find('.spaceit_pad span:contains("On-Hold:")').parent().clone().remove('span').text().strip().replace(',', '').replace('#', '').split('\n')[0])
        return self._on_hold
    
    @property
    def qitems(self):
        if not hasattr(self, '_qitems'):
            self._qitems = []
            # opnening not a typo (not mine)
            ops = self.page.find('.theme-songs.opnening .theme-song-artist').parent().items()
            eds = self.page.find('.theme-songs.ending .theme-song-artist').parent().items()
            counters = {}
            for items, item_type_idx in zip([ops, eds], [0, 1]):
                for item in items:
                    qitem = QItem()
                    
                    qitem.item_type = item_type_idx
                    
                    if item_type_idx not in counters.keys():
                        counters[item_type_idx] = 1
                    else:
                        counters[item_type_idx] += 1
                    
                    theme_song_index = item.find('.theme-song-index')
                    if theme_song_index.text() is not None:
                        theme_song_index = theme_song_index.text().replace(':', '')
                        qitem.num = int(theme_song_index) if theme_song_index != '' else counters[item_type_idx]
                    else:
                        qitem.num = counters[item_type_idx]
                    
                    theme_song_artist = item.find('.theme-song-artist')
                    if theme_song_artist is not None:
                        qitem.song_artist = theme_song_artist.text()[3:]
                    
                    theme_song_episode = item.find('.theme-song-episode')
                    if theme_song_episode is not None:
                        qitem.episodes = theme_song_episode.text()[1:-1]
                    
                    qitem.song_name = item.clone().remove('span').text()[1:-1]
                    
                    self._qitems.append(qitem)
        return self._qitems


def search(query: str) -> List[str]:
    url = f'https://myanimelist.net/search/all?q={urllib.quote_plus(query)}&cat=all'
    page = pget(url)
    if page is None:
        return []
    return [a.attr.href for a in page.find('h2#anime ~ article a.hoverinfo_trigger').items()]
