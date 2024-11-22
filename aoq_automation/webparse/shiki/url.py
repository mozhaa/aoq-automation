import re

from ..urlparser import *
from ..utils import default
from typing import Self


class ShikiUrlParser(UrlParser):
    @validator
    def _netloc(self) -> bool:
        return self._parsed_url.netloc in [
            "shikimori.one",
            "shikimori.org",
            "shikimori.net",
        ]

    @validator
    @default(False)
    def _path_parts(self) -> bool:
        return self._path_parts[1] == "animes" and self.mal_id is not None

    @classmethod
    def _url_from_mal_id(cls, mal_id: int) -> str:
        return f"https://shikimori.one/animes/{mal_id}"
        
    @property
    def url(self) -> str:
        return ShikiUrlParser._url_from_mal_id(self.mal_id)
    
    @property
    def mal_id(self) -> int:
        return int(re.sub("\\D", "", self._path_parts[2].split("-")[0]))

    @property
    def mal_url(self) -> str:
        return f"https://myanimelist.net/anime/{self.mal_id}"
    
    @classmethod
    def from_mal_id(cls, mal_id: int) -> Self:
        return cls(cls._url_from_mal_id(mal_id))
