from pathlib import PurePosixPath
from typing import Optional
from urllib.parse import urlparse


class MALUrlParser:
    """Parse URL as MyAnimeList URL and validate it"""

    def __init__(self, url: str) -> None:
        self.url = url
        self.parsed_url = urlparse(url)
        self.path_parts = PurePosixPath(self.parsed_url.path).parts

    def is_mal_url(self) -> bool:
        return self.parsed_url.netloc == "myanimelist.net"

    def is_mal_anime_url(self) -> bool:
        return (
            len(self.path_parts) >= 2 and self.path_parts[1] == "anime" and self.mal_id
        )

    def is_valid(self) -> bool:
        return self.is_mal_url() and self.is_mal_anime_url()

    @property
    def mal_id(self) -> Optional[int]:
        try:
            return int(self.path_parts[2])
        except:
            return None

    @property
    def mal_url(self) -> Optional[str]:
        if self.mal_id is not None:
            return f"https://myanimelist.net/anime/{self.mal_id}"
