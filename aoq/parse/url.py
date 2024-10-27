from pathlib import PurePosixPath
from typing import *
from urllib.parse import urlparse
import re


class MALUrlParser:
    def __init__(self, url: str):
        self.url = url
        self.parsed_url = urlparse(url)
        self.path_parts = PurePosixPath(self.parsed_url.path).parts

    def is_mal_url(self) -> bool:
        return self.parsed_url.netloc == 'myanimelist.net'

    def is_mal_anime_url(self) -> bool:
        return (
            len(self.path_parts) >= 2
            and self.path_parts[1] == 'anime'
        )

    def is_valid(self) -> bool:
        return self.is_mal_url() and self.is_mal_anime_url()

    @property
    def mal_id(self) -> int:
        return int(self.path_parts[2])

    @property
    def shiki_url(self) -> str:
        return f'https://shikimori.one/animes/{self.mal_id}'

    @property
    def mal_url(self) -> str:
        return self.url


class ShikiUrlParser:
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
        )

    def is_valid(self) -> bool:
        return self.is_shiki_url() and self.is_shiki_anime_url()

    @property
    def mal_id(self) -> int:
        return int(re.sub('\D', '', self.path_parts[2].split("-")[0]))

    @property
    def shiki_url(self) -> str:
        return f"https://shikimori.one/animes/{self.path_parts[2]}"

    @property
    def mal_url(self) -> str:
        return f"https://myanimelist.net/anime/{self.mal_id}"


def parse_url(url: str) -> Dict[str, str]:
    url_parser = MALUrlParser(url)
    if url_parser.is_valid():
        return {
            'mal': url_parser.mal_url,
            'shiki': url_parser.shiki_url,
        }

    url_parser = ShikiUrlParser(url)
    if url_parser.is_valid():
        return {
            'mal': url_parser.mal_url,
            'shiki': url_parser.shiki_url,
        }

    return None
