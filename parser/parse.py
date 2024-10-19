from db.objects import *
from parser import mal, shiki
import asyncio

async def parse_anime_by_url(url: str) -> Anime | None:
    anime = Anime()
        
    # get pages on mal and shiki
    shiki_page, mal_page = await asyncio.gather(shiki.Page.from_url(url), mal.Page.from_url(url))
    
    if shiki_page is None or mal_page is None:
        raise ValueError(f'{url} is not a valid url')
            
    # get poster
    anime.poster_url = mal_page.poster or shiki_page.poster
    
    # get titles
    anime.title_en = mal_page.title_en
    anime.title_ro = mal_page.title_ro or shiki_page.title_ro
    anime.title_ru = shiki_page.title_ru
    
    # # get release year
    # anime.airing_start, anime.airing_end = shiki_page.get_airings()
    
    return anime