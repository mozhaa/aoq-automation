from aoq.database import *
from typing import *
from aoq.parse import *

class Handler:
    def __init__(self, cur: DatabaseCursor):
        self.cur = cur

    def close(self):
        self.cur.close()

    async def add_anime_by_url(self, url: str) -> Anime:
        self.anime = await parse_anime_by_url(url=url)
        
        already_in_database = self.cur.exists(self.anime, key_columns=['mal_id'])
        if already_in_database:
            self.cur.update(self.anime, key_columns=['mal_id'])
        else:
            self.cur.insert(self.anime)
            
        return self.anime, already_in_database

    async def parse_and_add_qitems(self) -> List[QItem]:
        qitems = await parse_qitems_by_url(self.anime.mal_url)
        for qitem in qitems:
            qitem.anime_id = self.anime.anime_id
            if self.cur.exists(qitem, key_columns=['anime_id', 'num']):
                self.cur.update(qitem, key_columns=['anime_id', 'num'])
            else:
                self.cur.insert(qitem)
        
        return self.list_qitems()
    
    def list_qitems(self) -> List[QItem]:
        return self.cur.select_all(QItem)
        