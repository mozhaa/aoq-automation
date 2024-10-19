import httpx
import asyncio
from pyquery import PyQuery
from functools import lru_cache, partial

_headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

@lru_cache(maxsize=32)
async def pget(url: str) -> PyQuery | None:
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.is_success:
            return PyQuery(r.text)
        return None
    # response = grequests.get(url, headers=_headers)
    # # response = await asyncio.get_event_loop().run_in_executor(None, partial(grequests.get, headers=_headers), url)
    # if response.ok:
    #     return PyQuery(response.text)
    # return None