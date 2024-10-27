from typing import *
import asyncio

from aoq.database import *
from .mal import MALAnimeParser
from .shiki import ShikiAnimeParser
from .url import parse_url

async def parse_anime_by_url(url: str) -> Anime:
    anime = Anime()
        
    urls = parse_url(url)
    if urls is None:
        raise RuntimeError(f'{url} is not a valid url')
    
    shiki_page, mal_page = ShikiAnimeParser(urls['shiki']), MALAnimeParser(urls['mal'])
    await asyncio.gather(shiki_page.load_pages(), mal_page.load_pages())
            
    anime.mal_url = mal_page.url
    anime.shiki_url = shiki_page.url
    anime.mal_id = mal_page.mal_id
    anime.title_en = mal_page.title_en
    anime.title_ro = mal_page.title_ro or shiki_page.title_ro
    anime.title_ru = shiki_page.title_ru
    
    anime.shiki_poster_thumbnail_url = shiki_page.poster_thumbnail_url
    anime.shiki_poster_url = shiki_page.poster_url
    anime.shiki_rating = shiki_page.rating
    anime.shiki_rating_count = shiki_page.rating_count
    anime.shiki_completed = shiki_page.completed
    anime.shiki_watching = shiki_page.watching
    anime.shiki_plan_to_watch = shiki_page.plan_to_watch
    anime.shiki_dropped = shiki_page.dropped
    anime.shiki_on_hold = shiki_page.on_hold
    anime.shiki_favorites = shiki_page.favorites
    anime.shiki_comments = shiki_page.comments
    
    anime.mal_poster_url = mal_page.poster_url
    anime.mal_favorites = mal_page.favorites
    anime.mal_rating = mal_page.rating
    anime.mal_popularity = mal_page.popularity
    anime.mal_ranked = mal_page.ranked
    anime.mal_plan_to_watch = mal_page.plan_to_watch
    anime.mal_completed = mal_page.completed
    anime.mal_watching = mal_page.watching
    anime.mal_dropped = mal_page.dropped
    anime.mal_on_hold = mal_page.on_hold
    
    return anime

async def parse_qitems_by_url(url: str) -> List[QItem]:
    mal_page = await MALAnimeParser(url)
    return mal_page.qitems