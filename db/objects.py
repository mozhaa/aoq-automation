from dataclasses import dataclass
from typing import Optional

class DBObject:
    def __init__(self):
        pass

    def as_sql(self) -> str:
        return (
            '(' + 
            ', '.join(
                [
                    '\'' + str(value) + '\'' 
                    if isinstance(value, str) 
                    else str(value) 
                    for key, value in self.__dict__.items()
                    if key != 'id'
                ]
            ) + 
            ')'
        )
    
    def as_sql_header(self) -> str:
        return (
            '(' + 
            ', '.join(
                [
                    f'\'{a}\'' 
                    for a in dir(self) 
                    if not a.startswith('__') and 
                       not callable(getattr(self, a)) and 
                       a != 'id'
                ]
            ) + 
            ')'
        )
    
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
    print(a.as_sql_header())
    print(a.as_sql())