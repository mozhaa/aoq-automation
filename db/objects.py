from dataclasses import dataclass
from typing import Optional, Dict, List

class DBObject:
    def __init__(self):
        pass

    def select_parameters(self) -> Dict:
        '''Example output: {"title_en": "aa", "title_ru": "sdf", ...}'''
        return {key: value for key, value in self.__dict__.items() if value is not None}
    
    def select_placeholders(self) -> str:
        '''Example output: "(:title_en, :title_ru, :title_ro, :year)"'''
        return '(' + ', '.join([f':{key}' for key, value in self.__dict__.items() if value is not None]) + ')'
    
    def select_columns(self) -> str:
        '''Example output: "(title_en, title_ru, title_ro, year)"'''
        return '(' + ', '.join([key for key, value in self.__dict__.items() if value is not None]) + ')'
    
    def where_parameters(self, key_columns: List[str]) -> Dict:
        return {f'{col}': getattr(self, col) for col in key_columns}
    
    def where_placeholders(self, key_columns: List[str]):
        return ' AND '.join(["{col} = :{col}".format(col=col) for col in key_columns])
    
    def set_placeholders(self):
        return self.where_placeholders(self.__dict__.keys())
    
    def set_parameters(self):
        return self.where_parameters(self.__dict__.keys())
    
    def from_sql(cls, sql):
        return cls(*sql)


@dataclass
class Anime(DBObject):
    id = None,
    anime_id = None,
    title_en = None,
    title_ro = None,
    title_ru = None,
    mal_url = None,
    shiki_url = None,
    mal_poster_url = None,
    shiki_poster_url = None,
    shiki_poster_thumbnail_url = None,
    aired_start = None,
    aired_end = None,
    shiki_rating = None,
    shiki_rating_count = None,
    shiki_plan_to_watch = None,
    shiki_completed = None,
    shiki_watching = None,
    shiki_dropped = None,
    shiki_on_hold = None,
    shiki_favorites = None,
    shiki_comments = None,
    mal_rating = None,
    mal_favorites = None,
    mal_popularity = None,
    mal_ranked = None,
    mal_plan_to_watch = None,
    mal_completed = None,
    mal_watching = None,
    mal_dropped = None,
    mal_on_hold = None,

@dataclass
class QItem(DBObject):
    id: Optional[int] = None
    anime_id: Optional[int] = None
    type: Optional[int] = None
    num: Optional[int] = None

@dataclass
class QItemSource(DBObject):
    id: Optional[int] = None
    qitem_id: Optional[int] = None
    type: Optional[int] = None
    path: Optional[str] = None
    guess_time: Optional[float] = None
    reveal_time: Optional[float] = None

if __name__ == '__main__':
    a = Anime()
    print(a.select_columns())
    print(a.select_parameters())