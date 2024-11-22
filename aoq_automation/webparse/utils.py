from functools import wraps
from typing import Any

from aiogram.dispatcher.event.handler import CallableObject
from aiohttp import ClientSession
from pyquery import PyQuery

default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


class InvalidURLError(BaseException): ...


async def pget(
    session: ClientSession, url: str, ignore_status_code: bool = False
) -> PyQuery:
    """GET request for PyQuery'd web-page"""
    async with session.get(
        url, headers=default_headers, allow_redirects=True
    ) as response:
        if ignore_status_code or response.ok:
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


def default(value: Any):
    def decorator(wrapped: CallableObject):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            try:
                return wrapped(*args, **kwargs)
            except:
                return value

        return wrapper

    return decorator
