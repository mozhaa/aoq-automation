from aiohttp import ClientSession
from asyncache import cached
from cachetools import LRUCache
from cachetools.keys import hashkey
from pyquery import PyQuery

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


class InvalidURLError(BaseException): ...


@cached(LRUCache(maxsize=32), key=lambda session, url: hashkey(url))
async def pget(session: ClientSession, url: str) -> PyQuery:
    """Cached GET request for web-page"""
    async with session.get(url, headers=default_headers) as response:
        if response.ok:
            return PyQuery(await response.text())
        raise InvalidURLError()


def text_without_span(el) -> str:
    return (
        el.parent()
        .clone()
        .remove("span")
        .remove("sup")
        .text()
        .strip()
        .replace(",", "")
        .replace("#", "")
        .replace(":", "")
        .split("\n")[0]
    )
