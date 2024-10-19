from dataclasses import dataclass
from typing import Optional, Dict

class DBObject:
    def __init__(self):
        pass

    def as_sql_values(self) -> Dict:
        '''Example output: {"title_en": "aa", "title_ru": "sdf", ...}'''
        return {key: value for key, value in self.__dict__.items() if value is not None}
    
    def as_sql_placeholders(self) -> str:
        '''Example output: "(:title_en, :title_ru, :title_ro, :year)"'''
        return '(' + ', '.join([f':{key}' for key, value in self.__dict__.items() if value is not None]) + ')'
    
    def as_sql_keys(self) -> str:
        '''Example output: "(title_en, title_ru, title_ro, year)"'''
        return '(' + ', '.join([key for key, value in self.__dict__.items() if value is not None]) + ')'
    
    def from_sql(cls, sql):
        return cls(*sql)


@dataclass
class Anime(DBObject):
    id: Optional[int] = None
    title_en: Optional[str] = None
    title_ro: Optional[str] = None
    title_ru: Optional[str] = None
    mal_url: Optional[str] = None
    shiki_url: Optional[str] = None
    poster_url: Optional[str] = None

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
    print(a.as_sql_keys())
    print(a.as_sql_values())