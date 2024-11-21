import re
from pathlib import PurePosixPath
from typing import Optional
from urllib.parse import urlparse


class ShikiUrlParser:
    """Parse URL as Shikimori URL and validate it"""

    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.path_parts = PurePosixPath(self.parsed_url.path).parts

    def is_shiki_url(self) -> bool:
        return self.parsed_url.netloc in [
            "shikimori.one",
            "shikimori.org",
            "shikimori.net",
        ]

    def is_shiki_anime_url(self) -> bool:
        return (
            self.is_shiki_url()
            and len(self.path_parts) >= 2
            and self.path_parts[1] == "animes"
            and self.mal_id
        )

    def is_valid(self) -> bool:
        return self.is_shiki_url() and self.is_shiki_anime_url()

    @property
    def mal_id(self) -> Optional[int]:
        try:
            return int(re.sub("\\D", "", self.path_parts[2].split("-")[0]))
        except:
            return None

    @property
    def shiki_url(self) -> str:
        return f"https://shikimori.one/animes/{self.path_parts[2]}"

    @property
    def mal_url(self) -> str:
        return f"https://myanimelist.net/anime/{self.mal_id}"
