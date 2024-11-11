from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from typing import *
from aoq_automation.parser import MALPageParser, MALUrlParser


class Preaction(Filter):
    """Type of aiogram filter, that does some action and saves result into FSMContext."""

    async def __call__(self, message: Message, state: FSMContext, **kwargs) -> bool: ...


class MALUrl(Preaction):
    """
    Interpret message as MAL URL, validate it and save MAL URL in consistent format into state["mal_url"].
    If it is not valid MAL URL, fail filtering (return False).
    """

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        url = message.text
        url_parser = MALUrlParser(url)
        if not url_parser.is_valid():
            return False
        await state.update_data(mal_url=url_parser.mal_url)
        return True


class MALPage(Preaction):
    """
    Take mal_url from FSMContext, and create MALPageParser object from this URL (validate it as URL to anime page).
    Pass if it's valid, otherwise fail filtering (return False).
    """

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        mal_url = await state.get_value("mal_url")
        page = MALPageParser(mal_url)
        await page.load_pages()
        if not page.valid:
            return False
        await state.update_data(mal_page=page)
        return True


class GetQItems(Preaction):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        # TODO: database query
        qitems = [
            "OP 1",
            "OP 2",
            "OP 3",
            "ED 1",
            "ED 2",
            "ED 3",
            "OP 1",
            "OP 2",
            "OP 3",
            "ED 1",
            "ED 2",
            "ED 3",
        ]
        
        await state.update_data(qitems=qitems)
        return True