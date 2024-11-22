import re

from ..urlparser import *
from ..utils import default


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

    @property
    def url(self) -> str:
        return f"https://shikimori.one/animes/{self.path_parts[2]}"
    
    @property
    def mal_id(self) -> int:
        return int(re.sub("\\D", "", self._path_parts[2].split("-")[0]))

    @property
    def mal_url(self) -> str:
        return f"https://myanimelist.net/anime/{self.mal_id}"
