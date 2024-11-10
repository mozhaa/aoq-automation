from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, Filter
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from typing import Dict, Any, Optional
from aoq_automation.config import Settings
from aoq_automation.parser.url import MALUrlParser


bot = Bot(token=Settings().token)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

default_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]])
menu_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Find anime")]])
anime_page_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Find another anime")],
        [KeyboardButton(text="Back to menu")],
    ]
)


class Form(StatesGroup):
    menu = State()
    searching_anime = State()
    anime_page = State()


@router.message(Command("start"))
@router.message(Form.anime_page, F.text == "Back to menu")
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.menu)
    await message.reply(text="What do you want to do?", reply_markup=menu_markup)


@router.message(Form.menu, F.text == "Find anime")
@router.message(Form.anime_page, F.text == "Find another anime")
async def find_anime(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.searching_anime)
    await message.reply(
        text="Please enter anime URL on MyAnimeList (myanimelist.net)",
        reply_markup=default_markup,
    )


def MALUrl(message: Message) -> bool | Dict[str, Any]:
    url = message.text
    url_parser = MALUrlParser(url)
    if url_parser.is_valid():
        return {"mal_url": url_parser.mal_url}
    return False


@router.message(Form.searching_anime, MALUrl)
async def anime_page(
    message: Message, state: FSMContext, mal_url: Optional[str] = None
) -> None:
    await state.set_state(Form.anime_page)
    await message.reply(
        text="You're on anime page!",
        reply_markup=anime_page_markup,
    )


@router.message(Form.menu)
@router.message(Form.anime_page)
async def invalid_menu_option(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"No such option: {message.text}")


@router.message(Form.searching_anime)
async def invalid_anime_query(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"Invalid MAL URL, try again")
