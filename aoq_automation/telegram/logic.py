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
from aoq_automation.database.tools import get_or_create

from .markups import *
from .preactions import *
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
            text=f"You're on anime page! URL: {anime.mal_url}, ID: {anime_id}, rating: {p_anime_mal.rating}",
            reply_markup=anime_page_markup,
        )


@redirect_to(anime_page)
async def to_anime_page(message: Message, state: FSMContext) -> None:
    mal_page = await state.get_value("mal_page")
    anime = Anime(mal_url=mal_page.url, title_ro=mal_page.title_ro)
    anime_id, is_new = await get_or_create(anime, ["mal_url"])
    if is_new:
        async with db.async_session() as session:
            p_anime_mal = mal_page.as_parsed()
            p_anime_mal.anime_id = anime_id
            session.add(p_anime_mal)
            await session.commit()
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
        SurveyQuestion(
            key="mal_url",
            filterset=AsMALUrl(),
        ),
    ],
    state=Form.searching_anime,
    on_exit=to_anime_page,
    on_cancel=menu,
    enter_filterset=[
        [Form.menu, F.text == "Find anime"],
        [Form.anime_page, F.text == "Find another anime"],
    ],
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
            text=f"You're on QItems page!",
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
        filterset=as_model_parameter(QItem, "category"),
        keyboard_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Opening"), KeyboardButton(text="Ending")]]
        ),
        save=False,
    ),
    "number": SurveyQuestion(
        key="number",
        filterset=as_model_parameter(QItem, "number"),
        save=False,
    ),
    "difficulty": SurveyQuestion(
        key="value",
        filterset=as_model_parameter(QItemDifficulty, "value"),
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
        filterset=as_model_parameter(QItemSource, "path"),
        save=False,
    ),
    "guess_start": SurveyQuestion(
        key="guess_start",
        filterset=as_model_parameter(QItemSourceTiming, "guess_start"),
        save=False,
    ),
    "reveal_start": SurveyQuestion(
        key="reveal_start",
        filterset=as_model_parameter(QItemSourceTiming, "reveal_start"),
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
            text=f"Quiz Item {values["category"]} {values["number"]} already exists. Delete or edit it, and try again."
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
    enter_filterset=(F.text == "Add new"),
).include_into(router, fallback_router)


# for key, question_suite in editing_question_suites.items():
#     Survey(
#         questions=question_suite,
#         on_exit=edit_parameter(key=key),
#         on_cancel=qitem_page,
#         state=Form.editing_parameter,
#         enter_filterset=[[Form.qitem_page, F.text == f"Edit {key}"]],
#     ).include_into(router, fallback_router)

# def edit_parameter(key: str) -> Callable:
#     @redirect_to(qitem_page)
#     async def wrapped(message: Message, state: FSMContext) -> None:
#         values = await state.get_data()
#         added_by = get_user_mark(message)
#         parameter = values[key]
#         qitem_id = values["qitem_id"]
#         async with db.async_session() as session:
#             qitem = await session.get(QItem, qitem_id)
#             if key in ["category", "number"]:
#                 qitem.__setattr__(key, parameter)
#             elif key == "value":
#                 qitem_difficulties = await qitem.awaitable_attrs.difficulties
#                 found = False
#                 for diff in qitem_difficulties:
#                     if diff.added_by == added_by:
#                         diff.__setattr__(key, parameter)
#                         found = True
#                         break
#                 if not found:
#                     diff = QItemDifficulty(
#                         qitem=qitem,
#                         value=parameter
#                     )
#                     session.add(diff)
#             elif key == "source":
#                 qitem_sources = await qitem.awaitable_attrs.sources
#                 found = False
#                 for src in qitem_sources:
#                     if src.added_by == added_by:
#                         src.__setattr__(key, parameter)
#                         found = True
#                         break
#                 qitem.__setattr__(key, parameter)
#             elif key in ["guess_start", "reveal_start"]:

#             category, number = qitem.category, qitem.number
#             try:
#                 await session.commit()
#                 await state.update_data(category=category, number=number)
#             except:
#                 await message.answer(
#                     text=f"Quiz Item {category} {number} already exists. Delete or edit it, and try again."
#                 )

#     return wrapped


@fallback_router.message(Form.menu)
@fallback_router.message(Form.anime_page)
@fallback_router.message(Form.qitems_page)
@fallback_router.message(Form.qitem_page)
async def invalid_menu_option(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"No such option: {message.text}")


@fallback_router.message(default_state)
async def no_state(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"Click /start to enter menu", reply_markup=default_markup)


dp.include_router(fallback_router)
