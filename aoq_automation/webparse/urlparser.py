from abc import abstractmethod
from functools import wraps
from pathlib import PurePosixPath
from typing import Callable
from urllib.parse import urlparse, urlunparse
import re


def validator(wrapped: Callable):
    wrapped._is_validator = True
    return wrapped


def normalize_url(url: str) -> str:
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    parsed_url = urlparse(url)
    netloc = re.sub("^www\.", "", parsed_url.netloc)
    url = urlunparse(parsed_url._replace(netloc=netloc))
    return url


class UrlParser:
    def __init__(self, url: str) -> None:
        self._url = normalize_url(url)
        self._parsed_url = urlparse(self._url)
        self._path_parts = PurePosixPath(self._parsed_url.path).parts

    def is_valid(self) -> bool:
        for name, method in self.__class__.__dict__.items():
            if hasattr(method, "_is_validator") and not method(self):
                return False
        return True

    @property
    @abstractmethod
    def url(self) -> str: ...
