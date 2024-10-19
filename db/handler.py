from db.objects import *
from db.db import SmartCursor
from parser.parse import *
import asyncio
import re

class Handler:
    def __init__(self, cur: SmartCursor):
        self.cur = cur

    async def add_anime(self, query: str) -> Anime:
        anime = await parse_anime_by_url(url=query)
        if self.cur.exists(Anime, ['title_ru = ?'], [anime.title_ru]):
            return anime, False
        self.cur.insert(anime)
        return anime, True
        
            