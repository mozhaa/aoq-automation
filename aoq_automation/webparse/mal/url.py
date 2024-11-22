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

    @property
    def url(self) -> str:
        return f"https://myanimelist.net/anime/{self.mal_id}"

    @property
    def mal_id(self) -> int:
        return int(self._path_parts[2])
