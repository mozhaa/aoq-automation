from typing import *

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from sqlalchemy import select

from aoq_automation.config import config
from aoq_automation.database.database import db
from aoq_automation.database.models import *

from .markups import *
from .filters import *
from .survey import *
from .utils import *

bot = Bot(token=config["telegram"]["token"])
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
    editing_parameter = State()
    adding_qitem = State()


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
    anime_id = await state.get_value("anime_id")
    async with db.async_session() as session:
        anime = await session.get(Anime, anime_id)
        p_anime_mal = await anime.awaitable_attrs.p_mal
        await message.answer(
            text=f"You're on anime page! URL: {anime.mal_url}, "
            f"ID: {anime_id}, rating: {p_anime_mal.rating}",
            reply_markup=anime_page_markup,
        )


@redirect_to(anime_page)
async def to_anime_page(message: Message, state: FSMContext) -> None:
    anime_id = await state.get_value("anime_id")
    if anime_id is not None:
        # anime already in database
        return
    mal_pp = await state.get_value("mal_pp")
    async with db.async_session() as sess:
        anime = Anime(mal_url=mal_pp.url, title_ro=mal_pp.title_ro)
        sess.add(anime)
        for key in ["mal", "shiki", "anidb"]:
            p_anime = await state.get_value(key)
            p_anime.anime = anime
            sess.add(p_anime)
        await sess.commit()
        anime_id = await anime.awaitable_attrs.id
    await state.update_data(anime_id=anime_id)


@router.message(Form.anime_page, F.text == "Delete this anime")
@redirect_to(menu)
async def delete_anime(message: Message, state: FSMContext) -> None:
    anime_id = await state.get_value("anime_id")
    async with db.async_session() as session:
        anime = await session.get(Anime, anime_id)
        await session.delete(anime)
        await session.commit()


Survey(
    questions=[
        SurveyQuestion(key="URL", filter=as_anime_query, save=False),
    ],
    state=Form.searching_anime,
    on_exit=to_anime_page,
    on_cancel=menu,
    enter_filter=Filterset(
        [
            [Form.menu, F.text == "Find anime"],
            [Form.anime_page, F.text == "Find another anime"],
        ]
    ),
).include_into(router, fallback_router)


@router.message(Form.anime_page, F.text == "Manage OP & ED")
@router.message(Form.qitem_page, F.text == "Back to OP & ED page")
async def qitems_page(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.qitems_page)
    anime_id = await state.get_value("anime_id")
    async with db.async_session() as session:
        anime = await session.get(Anime, anime_id)
        qitems = await anime.awaitable_attrs.qitems
        qitems_repr = [f"{qitem.category} {qitem.number}" for qitem in qitems]
        qitems_keyboard = await state.get_value(
            "qitems_keyboard", QItemsKeyboardMarkup(qitems_repr)
        )
        if qitems_repr != qitems_keyboard.qitems:
            qitems_keyboard = QItemsKeyboardMarkup(qitems_repr)
        await state.update_data(qitems=qitems_repr)
        await state.update_data(qitems_keyboard=qitems_keyboard)
        await message.answer(
            text="You're on QItems page!",
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
    values = await state.get_data()
    category = values["category"]
    number = values["number"]
    anime_id = values["anime_id"]
    async with db.async_session() as session:
        qitem = await session.execute(
            select(QItem).filter_by(anime_id=anime_id, category=category, number=number)
        )
        qitem = qitem.scalar_one()
        if qitem is None:
            return await qitems_page(message, state)
        await state.update_data(qitem_id=qitem.id)
        await message.answer(
            text=f"You're on QItem page: {qitem.category} {qitem.number}",
            reply_markup=qitem_markup,
        )


parameter_questions = {
    "category": SurveyQuestion(
        key="category",
        filter=as_model_parameter(QItem, "category"),
        keyboard_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Opening"), KeyboardButton(text="Ending")]]
        ),
        save=False,
    ),
    "number": SurveyQuestion(
        key="number",
        filter=as_model_parameter(QItem, "number"),
        save=False,
    ),
    "difficulty": SurveyQuestion(
        key="value",
        filter=as_model_parameter(QItemDifficulty, "value"),
        keyboard_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Very Easy"), KeyboardButton(text="Easy")],
                [KeyboardButton(text="Medium")],
                [KeyboardButton(text="Hard"), KeyboardButton(text="Very Hard")],
            ]
        ),
        save=False,
    ),
    "source": SurveyQuestion(
        key="path",
        filter=as_model_parameter(QItemSource, "path"),
        save=False,
    ),
    "guess_start": SurveyQuestion(
        key="guess_start",
        filter=as_model_parameter(QItemSourceTiming, "guess_start"),
        save=False,
    ),
    "reveal_start": SurveyQuestion(
        key="reveal_start",
        filter=as_model_parameter(QItemSourceTiming, "reveal_start"),
        save=False,
    ),
}


editing_question_suites = {
    "label": [
        parameter_questions["category"],
        parameter_questions["number"],
    ],
    "difficulty": [
        parameter_questions["difficulty"],
    ],
    "source": [
        parameter_questions["source"],
        parameter_questions["guess_start"],
        parameter_questions["reveal_start"],
    ],
}


@redirect_to(qitem_page)
async def add_qitem(message: Message, state: FSMContext) -> None:
    values = await state.get_data()
    added_by = get_user_mark(message)
    success = await save_qitem_from_dict(values, added_by)
    if not success:
        await message.answer(
            text=f"Quiz Item {values["category"]} {values["number"]} already "
            "exists. Delete or edit it, and try again."
        )
    await state.update_data(
        category=values["category"],
        number=values["number"],
    )


Survey(
    questions=[q for q in parameter_questions.values()],
    on_exit=add_qitem,
    on_cancel=qitems_page,
    state=Form.adding_qitem,
    enter_filter=(F.text == "Add new"),
).include_into(router, fallback_router)


@fallback_router.message(Form.menu)
@fallback_router.message(Form.anime_page)
@fallback_router.message(Form.qitems_page)
@fallback_router.message(Form.qitem_page)
async def invalid_menu_option(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"No such option: {message.text}")


@fallback_router.message(default_state)
async def no_state(message: Message, state: FSMContext) -> None:
    await message.reply(text="Click /start to enter menu", reply_markup=default_markup)


dp.include_router(fallback_router)
