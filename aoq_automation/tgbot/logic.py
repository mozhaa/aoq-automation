from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import Command
from aiogram.types import Message
from aoq_automation.config import Settings
from aoq_automation.parser import MALPageParser, MALUrlParser
from typing import *
from .markups import *
from .utils import Chain


bot = Bot(token=Settings().token)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


class Form(StatesGroup):
    menu = State()
    searching_anime = State()
    anime_page = State()
    qitems_page = State()


@router.message(Command("start"))
@router.message(Form.anime_page, F.text == "Back to menu")
@router.message(Form.qitems_page, F.text == "Back to menu")
async def command_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Form.menu)
    await message.answer(text="What do you want to do?", reply_markup=menu_markup)


@router.message(Form.menu, F.text == "Find anime")
@router.message(Form.anime_page, F.text == "Find another anime")
async def find_anime(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.searching_anime)
    await message.answer(
        text="Please enter anime URL on MyAnimeList (myanimelist.net)",
        reply_markup=default_markup,
    )


def MALUrl(message: Message, **kwargs) -> bool | Dict[str, Any]:
    """
    Interpret message as MAL URL, validate it and return MAL URL in consistent format.
    If it is not valid MAL URL, fail filtering (return False).
    """
    url = message.text
    url_parser = MALUrlParser(url)
    if url_parser.is_valid():
        return {"mal_url": url_parser.mal_url}
    return False


async def MALPage(message: Message, mal_url: str, **kwargs) -> bool | Dict[str, Any]:
    """
    Take mal_url from arguments, and create MALPageParser object from this URL (validate it as URL to anime page).
    Return MALPageParser object if it's valid, otherwise fail filtering (return False).
    """
    page = MALPageParser(mal_url)
    await page.load_pages()
    if not page.valid:
        return False
    return {"mal_page": page}


@router.message(Form.qitems_page, F.text == "Back to Anime page")
@router.message(Form.searching_anime, Chain([MALUrl, MALPage]))
async def anime_page(message: Message, state: FSMContext, **kwargs) -> None:
    await state.update_data(kwargs)
    await state.set_state(Form.anime_page)
    mal_url = (await state.get_data())["mal_url"]
    await message.answer(
        text=f"You're on anime page! URL: {mal_url}",
        reply_markup=anime_page_markup,
    )


async def get_qitems() -> List[str]:
    # TODO: database query
    return [
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


@router.message(Form.anime_page, F.text == "Manage OP & ED")
async def qitems_page(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.qitems_page)
    state_data = await state.get_data()
    mal_url = state_data["mal_url"]
    qitems = await get_qitems()
    qitems_keyboard = state_data.get("qitems_keyboard", QItemsKeyboardMarkup(qitems))
    await state.update_data(qitems=qitems, qitems_keyboard=qitems_keyboard)
    await message.answer(
        text=f"You're on QItems page! Anime URL: {mal_url}",
        reply_markup=qitems_keyboard.as_markup(),
    )


@router.message(Form.qitems_page, F.text == "Next page")
async def qitems_page_next_page(message: Message, state: FSMContext) -> None:
    qitems_keyboard = await state.get_value("qitems_keyboard")
    qitems_keyboard.next_page()
    await state.update_data(qitems_keyboard=qitems_keyboard)
    return await qitems_page(message, state)


@router.message(Form.qitems_page, F.text == "Previous page")
async def qitems_page_previous_page(message: Message, state: FSMContext) -> None:
    qitems_keyboard = await state.get_value("qitems_keyboard")
    qitems_keyboard.previous_page()
    await state.update_data(qitems_keyboard=qitems_keyboard)
    return await qitems_page(message, state)


@router.message(Form.menu)
@router.message(Form.anime_page)
@router.message(Form.qitems_page)
async def invalid_menu_option(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"No such option: {message.text}")


@router.message(Form.searching_anime)
async def invalid_anime_query(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"Invalid MAL URL, try again")


@router.message(default_state)
async def no_state(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"Click /start to enter menu", reply_markup=default_markup)
