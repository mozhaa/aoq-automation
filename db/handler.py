from db.objects import *
from db.db import Cursor
from parser import mal, shiki
import asyncio
import re

class Handler:
    def __init__(self, cur: Cursor):
        self.cur = cur

    def add_anime(self, url: str) -> Anime:
        anime = Anime()
        
        shiki_, mal_ = asyncio.run(asyncio.gather(shiki.Page.from_url(url), mal.Page.from_url(url)))
        shiki_page = shiki_.result()
        mal_page = mal_.result()
        print(shiki_page)
        print(mal_page)
        # shiki_page = await shiki.Page.from_url(url)
        # mal_page = await shiki.Page.from_url(url)
        
        
        if shiki_page is None and mal_page is None:
            raise ValueError(f'{url} is not a valid url')
        if shiki_page is None:
            shiki_page = asyncio.run(shiki.page.from_mal_url(mal_page.url)).result()
            if shiki_page is None:
                raise ValueError(f'can\'t parse shiki {url}')
        if mal_page is None:
            mal_page = asyncio.run(mal.page.from_shiki_url(shiki_page.url)).result()
            if mal_page is None:
                raise ValueError(f'can\'t parse mal {url}')
                
        # get poster
        anime.poster_url = mal_page.get_poster() or shiki_page.get_poster()
        
        # get titles
        titles = mal_page.get_titles()
        titles.update(shiki_page.get_titles())
        anime.title_en = titles['en']
        anime.title_ro = titles['ro']
        anime.title_ru = titles['ru']
        
        # # get release year
        # anime.airing_start, anime.airing_end = shiki_page.get_airings()
        
        return anime
        
            