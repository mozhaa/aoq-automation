import httpx
from pyquery import PyQuery
from async_lru import alru_cache
import logging

logger = logging.getLogger(__name__)

_headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}

@alru_cache(maxsize=32)
async def pget(url: str) -> PyQuery | None:
    logger.debug('requesting "%s"', url)
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=_headers)
    if r.is_success:
        return PyQuery(r.text)
    return None