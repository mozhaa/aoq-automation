from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from typing import Dict, Any, Tuple
from aoq_automation.config import Settings
from aoq_automation.parser import MALPageParser, MALUrlParser
from .utils import Chain
import math


bot = Bot(token=Settings().token)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

default_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]])
menu_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Find anime")]])
anime_page_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Manage OP & ED")],
        [KeyboardButton(text="Find another anime")],
        [KeyboardButton(text="Back to menu")],
    ]
)


def build_qitems_page_markup(page: int = 0) -> Tuple[ReplyKeyboardMarkup, int]:
    qitems_page_markup = ReplyKeyboardBuilder()
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

    rows, cols = 2, 5
    page_size = rows * cols
    n_pages = math.ceil(len(qitems) / page_size)
    current_qitems = qitems[page_size * page : page_size * (page + 1)]

    keyboard = [[KeyboardButton(text="-") for _ in range(cols)] for _ in range(rows)]
    row, col = 0, 0
    for qitem in current_qitems:
        keyboard[row][col] = KeyboardButton(text=qitem)
        col += 1
        if col >= cols:
            col = 0
            row += 1

    qitems_page_markup.attach(
        ReplyKeyboardBuilder.from_markup(ReplyKeyboardMarkup(keyboard=keyboard))
    )
    qitems_page_markup.adjust(*([cols] * rows))

    qitems_page_markup.attach(
        ReplyKeyboardBuilder.from_markup(
            markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Previous page"),
                        KeyboardButton(text="Next page"),
                    ],
                    [KeyboardButton(text="Add new")],
                    [KeyboardButton(text="Back to Anime page")],
                    [KeyboardButton(text="Back to menu")],
                ]
            )
        )
    )
    return qitems_page_markup.as_markup(), n_pages


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
    url = message.text
    url_parser = MALUrlParser(url)
    if url_parser.is_valid():
        return {"mal_url": url_parser.mal_url}
    return False


async def MALPage(message: Message, mal_url: str, **kwargs) -> bool | Dict[str, Any]:
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


@router.message(Form.anime_page, F.text == "Manage OP & ED")
async def qitems_page(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.qitems_page)
    state_data = await state.get_data()
    mal_url = state_data["mal_url"]
    page = state_data.get("page", 0)
    markup, n_pages = build_qitems_page_markup(page)
    await state.update_data(n_pages=n_pages)
    await message.answer(
        text=f"You're on QItems page! Anime URL: {mal_url}",
        reply_markup=markup,
    )


@router.message(Form.qitems_page, F.text == "Next page")
async def qitems_page_next_page(message: Message, state: FSMContext) -> None:
    page_num = max(
        0,
        min(
            await state.get_value("n_pages", 0) - 1,
            await state.get_value("page", 0) + 1,
        ),
    )
    await state.update_data(page=page_num)
    return await qitems_page(message, state)


@router.message(Form.qitems_page, F.text == "Previous page")
async def qitems_page_previous_page(message: Message, state: FSMContext) -> None:
    page_num = max(
        0,
        min(
            await state.get_value("n_pages", 0) - 1,
            await state.get_value("page", 0) - 1,
        ),
    )
    await state.update_data(page=page_num)
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
