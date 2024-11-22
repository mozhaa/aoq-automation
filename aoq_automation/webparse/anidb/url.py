from urllib.parse import parse_qs

from ..urlparser import *
from ..utils import default


class AniDBUrlParser(UrlParser):
    @validator
    def _netloc(self) -> bool:
        return self._parsed_url.netloc == "anidb.net"

    @validator
    @default(False)
    def _anime(self) -> bool:
        return self.anidb_id is not None
    
    @classmethod
    def _url_from_anidb_id(cls, anidb_id: int) -> str:
        return f"https://anidb.net/anime/{anidb_id}"

    @property
    def url(self) -> str:
        return AniDBUrlParser._url_from_anidb_id(self.anidb_id)

    @property
    def anidb_id(self) -> int:
        if self._path_parts[1] == "anime":
            return int(self._path_parts[2])
        else:
            return int(parse_qs(self._parsed_url.query)["aid"][0])
