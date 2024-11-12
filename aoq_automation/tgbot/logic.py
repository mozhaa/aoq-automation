from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import Command
from aiogram.types import Message
from aoq_automation.config import Settings
from typing import *
from .markups import *
from .preactions import *
from .utils import Survey, SurveyQuestion


bot = Bot(token=Settings().token)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


# Router for handling updates, that didn't pass any filters
# It must be last router to be chained to dispatcher
fallback_router = Router()


class Form(StatesGroup):
    menu = State()
    searching_anime = State()
    anime_page = State()
    qitems_page = State()
    qitem_page = State()


@router.message(Command("start"))
@router.message(Form.anime_page, F.text == "Back to menu")
@router.message(Form.qitems_page, F.text == "Back to menu")
@router.message(Form.qitem_page, F.text == "Back to menu")
async def menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Form.menu)
    await message.answer(text="What do you want to do?", reply_markup=menu_markup)


@router.message(Form.qitems_page, F.text == "Back to Anime page")
@router.message(Form.qitem_page, F.text == "Back to Anime page")
async def anime_page(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.anime_page)
    mal_url = (await state.get_data())["mal_url"]
    await message.answer(
        text=f"You're on anime page! URL: {mal_url}",
        reply_markup=anime_page_markup,
    )


r, fr = Survey(
    questions=[
        SurveyQuestion(
            key="mal_url",
            filterset=[
                [AsMALUrl(), AsMALPage()],
            ],
        ),
    ],
    state=Form.searching_anime,
    on_exit=anime_page,
    on_cancel=menu,
    enter_filters=[
        [Form.menu, F.text == "Find anime"],
        [Form.anime_page, F.text == "Find another anime"],
    ],
).as_routers()

router.include_router(r)
fallback_router.include_router(fr)


@router.message(Form.anime_page, F.text == "Manage OP & ED", GetQItems())
@router.message(Form.qitem_page, F.text == "Back to OP & ED page")
async def qitems_page(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.qitems_page)
    state_data = await state.get_data()
    mal_url = state_data["mal_url"]
    qitems = await state.get_value("qitems")
    qitems_keyboard = state_data.get("qitems_keyboard", QItemsKeyboardMarkup(qitems))
    await state.update_data(qitems_keyboard=qitems_keyboard)
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


@router.message(Form.qitems_page, AsQItem())
async def qitem_page(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.qitem_page)
    qitem = await state.get_value("qitem")
    await message.answer(
        text=f"You're on QItem page: {qitem}",
        reply_markup=qitem_markup,
    )


@fallback_router.message(Form.menu)
@fallback_router.message(Form.anime_page)
@fallback_router.message(Form.qitems_page)
async def invalid_menu_option(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"No such option: {message.text}")


@fallback_router.message(default_state)
async def no_state(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"Click /start to enter menu", reply_markup=default_markup)


dp.include_router(fallback_router)
