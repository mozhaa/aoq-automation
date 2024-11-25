from typing import Self

from ..urlparser import *
from ..utils import default


class MALUrlParser(UrlParser):
    @validator
    def _netloc(self) -> bool:
        return self._parsed_url.netloc == "myanimelist.net"

    @validator
    @default(False)
    def _anime(self) -> bool:
        return self._path_parts[1] == "anime" and self.mal_id is not None

    @classmethod
    def _url_from_mal_id(cls, mal_id: int) -> str:
        return f"https://myanimelist.net/anime/{mal_id}"

    @property
    def url(self) -> str:
        return MALUrlParser._url_from_mal_id(self.mal_id)

    @property
    def mal_id(self) -> int:
        return int(self._path_parts[2])

    @classmethod
    def from_mal_id(cls, mal_id: int) -> Self:
        return cls(cls._url_from_mal_id(mal_id))
