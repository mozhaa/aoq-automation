from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import *
from aoq_automation.parser import MALPageParser, MALUrlParser


class Preaction(Filter):
    """Type of aiogram filter, that does some action and saves result into FSMContext."""

    async def __call__(self, message: Message, state: FSMContext, **kwargs) -> bool: ...


class AsMALUrl(Preaction):
    """
    Interpret message as MAL URL, validate it (both URL and accessed page) and save MALPageParser
    into state["mal_page"]. If it is not valid MAL URL, fail filtering (return False).
    """

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        url = message.text
        url_parser = MALUrlParser(url)
        if not url_parser.is_valid():
            return False
        page = MALPageParser(url_parser.mal_url)
        await page.load_pages()
        if not page.valid:
            return False
        await state.update_data(mal_page=page)
        return True


class AsQItem(Preaction):
    """
    Interpret message as QItem representation (category + number, f.e. "OP 3") and save it into state["qitem"]
    """

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        qitems = await state.get_value("qitems")
        qitem = message.text
        if qitem not in qitems:
            return False
        await state.update_data(qitem=qitem)
        return True
