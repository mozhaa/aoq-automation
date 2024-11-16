from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import Command
from aiogram.types import Message
from aoq_automation.config import config
from typing import *
from .markups import *
from .preactions import *
from aoq_automation.database.models import *
from .utils import Survey, SurveyQuestion, Filterset, redirect_to
from sqlalchemy import select
from aoq_automation.database.tools import get_or_create
from aoq_automation.database.database import db


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
        await state.update_data(qitems=qitems_repr)
        qitems_keyboard = await state.get_value(
            "qitems_keyboard", QItemsKeyboardMarkup(qitems_repr)
        )
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
    category = await state.get_value("category")
    number = await state.get_value("number")
    async with db.async_session() as session:
        qitem = await session.execute(
            select(QItem).filter_by(category=category, number=number)
        )
        qitem = qitem.scalar_one()
        if qitem is None:
            return await qitems_page(message, state)
        await message.answer(
            text=f"You're on QItem page: {qitem.category} {qitem.number}",
            reply_markup=qitem_markup,
        )


keys = ["category", "number", "difficulty", "source", "guess time", "reveal time"]
filtersets = [
    Filterset(F.text.in_(["OP", "ED"])),
    Filterset(F.text.regexp("^[0-9]*$")),
    Filterset(
        [
            [F.text.regexp("^[0-9]*$"), F.func(lambda s: int(s) > 0 and int(s) <= 100)],
            [F.text.in_(["Very easy", "Easy", "Medium", "Hard", "Very hard"])],
        ]
    ),
    Filterset(F.text),
    Filterset(F.text),
    Filterset([F.text, F.func(lambda x: False)]),
]

for key, filterset in zip(keys, filtersets):
    Survey(
        questions=[
            SurveyQuestion(
                key=key,
                filterset=filterset,
            )
        ],
        on_exit=qitem_page,
        on_cancel=qitem_page,
        state=Form.editing_parameter,
        enter_filterset=[[Form.qitem_page, F.text == f"Edit {key}"]],
    ).include_into(router, fallback_router)


@fallback_router.message(Form.menu)
@fallback_router.message(Form.anime_page)
@fallback_router.message(Form.qitems_page)
async def invalid_menu_option(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"No such option: {message.text}")


@fallback_router.message(default_state)
async def no_state(message: Message, state: FSMContext) -> None:
    await message.reply(text=f"Click /start to enter menu", reply_markup=default_markup)


dp.include_router(fallback_router)
