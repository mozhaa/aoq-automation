from db.objects import *
from parser import mal, shiki
import asyncio

async def parse_anime_by_url(url: str) -> Anime | None:
    anime = Anime()
        
    # get pages on mal and shiki
    shiki_page, mal_page = await asyncio.gather(shiki.Page.from_url(url), mal.Page.from_url(url))
    
    if shiki_page is None or mal_page is None:
        raise ValueError(f'{url} is not a valid url')
            
    anime.anime_id = mal_page.anime_id
    anime.shiki_poster_thumbnail_url = shiki_page.poster_thumbnail_url
    anime.shiki_poster_url = shiki_page.poster_url
    anime.mal_poster_url = mal_page.poster_url
    anime.title_en = mal_page.title_en
    anime.title_ro = mal_page.title_ro or shiki_page.title_ro
    anime.title_ru = shiki_page.title_ru
    anime.shiki_rating = shiki_page.rating
    anime.shiki_completed = shiki_page.completed
    anime.shiki_watching = shiki_page.watching
    anime.shiki_plan_to_watch = shiki_page.plan_to_watch
    anime.shiki_dropped = shiki_page.dropped
    anime.shiki_on_hold = shiki_page.on_hold
    
    return anime