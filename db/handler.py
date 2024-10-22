from db.objects import *
from db.db import SmartCursor
from parser.parse import *

class Handler:
    def __init__(self, cur: SmartCursor):
        self.cur = cur

    async def add_anime(self, query: str) -> Anime:
        anime, qitems = await parse_anime_by_url(url=query)
        exists = False
        if self.cur.exists(anime, key_columns=['mal_id']):
            anime_id = self.cur.update(anime, key_columns=['mal_id'])
            exists = True
        else:
            anime_id = self.cur.insert(anime)
        for qitem in qitems:
            qitem.anime_id = anime_id
            if self.cur.exists(qitem, key_columns=['anime_id', 'num']):
                self.cur.update(qitem, key_columns=['anime_id', 'num'])
            else:
                self.cur.insert(qitem)
        return anime, exists
        
            