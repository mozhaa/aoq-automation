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

    @property
    def url(self) -> str:
        return f"https://anidb.net/anime/{self.anidb_id}"

    @property
    def anidb_id(self) -> int:
        if self._path_parts[1] == "anime":
            return int(self._path_parts[2])
        else:
            print(self._parsed_url.query)
            print(parse_qs(self._parsed_url.query)["aid"])
            print(parse_qs(self._parsed_url.query)["aid"][0])
            return int(parse_qs(self._parsed_url.query)["aid"][0])
