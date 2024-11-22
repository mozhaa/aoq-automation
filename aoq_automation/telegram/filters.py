from abc import abstractmethod
from functools import partialmethod
from typing import *

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aoq_automation.webparse.anidb import *
from aoq_automation.webparse.mal import *
from aoq_automation.webparse.shiki import *

from .filterset import Filterset


class TraceFilter(Filter):
    """
    Filter, that takes input either from message.text (if key is None) or state[key].
    You can chain them, so that first will take message.text as input,
    and next ones will take inputs from state.
    """

    def __init__(
        self, key: str = None, key_preprocess: Callable[[str], str] = None
    ) -> None:
        self.key = key
        self.key_preprocess = key_preprocess

    async def __call__(self, message: Message, state: FSMContext, **kwargs) -> bool:
        value = message.text if self.key is None else await state.get_value(self.key)
        if self.key_preprocess is not None:
            value = self.key_preprocess(value)
        return await self.call(value, message, state, **kwargs)

    @abstractmethod
    async def call(
        self, value: str, message: Message, state: FSMContext, **kwargs
    ) -> bool: ...


class AsAnimeUrl(TraceFilter):
    def __init__(
        self,
        url_parser: Type[UrlParser],
        page_parser: Type[PageParser],
        output_key: str,
        input_key: str = None,
        input_key_preprocess: Callable[[Any], str] = None,
    ) -> None:
        self.url_parser = url_parser
        self.page_parser = page_parser
        self.output_key = output_key
        super().__init__(key=input_key, key_preprocess=input_key_preprocess)

    async def call(
        self, value: str, message: Message, state: FSMContext, **kwargs
    ) -> bool:
        url_parser = self.url_parser(value)
        if not url_parser.is_valid():
            return False
        page_parser = self.page_parser(url_parser.url)
        await page_parser.load_pages()
        if not page_parser.valid:
            return False
        await state.update_data({self.output_key: page_parser.as_parsed()})
        await state.update_data({self.output_key + "_url": url_parser})
        await state.update_data({self.output_key + "_page": page_parser})
        return True


def mal_to_shiki_url(url_parser: MALUrlParser) -> str:
    return ShikiUrlParser.from_mal_id(url_parser.mal_id).url


def shiki_to_anidb_url(page_parser: ShikiPageParser) -> str:
    return page_parser.anidb_url


def anidb_to_mal_url(page_parser: AniDBPageParser) -> str:
    return page_parser.mal_url


class AsShikiUrl(AsAnimeUrl):
    __init__ = partialmethod(
        AsAnimeUrl.__init__, ShikiUrlParser, ShikiPageParser, "shiki"
    )


class AsAniDBUrl(AsAnimeUrl):
    __init__ = partialmethod(
        AsAnimeUrl.__init__, AniDBUrlParser, AniDBPageParser, "anidb"
    )


class AsMALUrl(AsAnimeUrl):
    __init__ = partialmethod(AsAnimeUrl.__init__, MALUrlParser, MALPageParser, "mal")


# NOTE: MAL -(id from url)-> Shiki -(link on page)-> AniDB -(link on page)-> MAL
AsUnknownUrl = Filterset(
    [
        [
            AsMALUrl(),
            AsShikiUrl("mal_url", mal_to_shiki_url),
            AsAniDBUrl("shiki_page", shiki_to_anidb_url),
        ],
        [
            AsShikiUrl(),
            AsAniDBUrl("shiki_page", shiki_to_anidb_url),
            AsMALUrl("anidb_page", anidb_to_mal_url),
        ],
        [
            AsAniDBUrl(),
            AsMALUrl("anidb_page", anidb_to_mal_url),
            AsShikiUrl("mal_url", mal_to_shiki_url),
        ],
    ]
)


class AsQItem(Filter):
    """
    Interpret message as QItem representation (category + number, f.e. "OP 3"),
    and save category and number into FSMContext
    """

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        qitems = await state.get_value("qitems")
        qitem = message.text
        if qitem not in qitems:
            return False
        category, number = qitem.split(" ")
        await state.update_data(category=category, number=int(number))
        return True
