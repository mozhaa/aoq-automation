from typing import *

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select

from aoq_automation.database.database import db
from aoq_automation.database.models import *
from aoq_automation.webparse.anidb import *
from aoq_automation.webparse.mal import *
from aoq_automation.webparse.shiki import *


async def anime_id_by_mal_url(mal_url: str) -> Optional[int]:
    async with db.async_session() as sess:
        anime = await sess.scalar(select(Anime).where(Anime.mal_url == mal_url))
        if anime is not None:
            return anime.id


async def parse_anime_page(
    up: UrlParser, pp_type: Type[PageParser], state: FSMContext, key: str
) -> bool:
    if not up.is_valid():
        return False
    pp = pp_type(up.url)
    await pp.load_pages()
    if not pp.is_valid():
        return False
    await state.update_data({key: pp.as_parsed()})
    await state.update_data({key + "_up": up})
    await state.update_data({key + "_pp": pp})
    return True


async def as_mal_url(mal_up: MALUrlParser, state: FSMContext) -> bool:
    anime_id = await anime_id_by_mal_url(mal_up.url)
    if anime_id is not None:
        # if anime already in database, presume that all parsed info is also in DB
        await state.update_data(anime_id=anime_id)
        return True

    # otherwise, parse all pages
    mal_res = await parse_anime_page(mal_up, MALPageParser, state, "mal")
    if not mal_res:
        return False

    shiki_res = await parse_anime_page(
        ShikiUrlParser.from_mal_id(mal_up.mal_id), ShikiPageParser, state, "shiki"
    )
    if not shiki_res:
        return False

    shiki_pp = await state.get_value("shiki_pp")
    anidb_res = await parse_anime_page(
        AniDBUrlParser(shiki_pp.anidb_url), AniDBPageParser, state, "anidb"
    )
    if not anidb_res:
        return False

    return True


async def as_shiki_url(shiki_up: ShikiUrlParser, state: FSMContext) -> bool:
    anime_id = await anime_id_by_mal_url(shiki_up.mal_url)
    if anime_id is not None:
        await state.update_data(anime_id=anime_id)
        return True

    shiki_res = await parse_anime_page(shiki_up, ShikiPageParser, state, "shiki")
    if not shiki_res:
        return False

    shiki_pp = await state.get_value("shiki_pp")
    anidb_res = await parse_anime_page(
        AniDBUrlParser(shiki_pp.anidb_url), AniDBPageParser, state, "anidb"
    )
    if not anidb_res:
        return False

    mal_res = await parse_anime_page(
        MALUrlParser(shiki_up.mal_url), MALPageParser, state, "mal"
    )
    if not mal_res:
        return False

    return True


async def as_anidb_url(anidb_up: AniDBUrlParser, state: FSMContext) -> bool:
    async with db.async_session() as sess:
        p_anime_anidb = await sess.scalar(
            select(PAnimeAniDB).where(PAnimeAniDB.url == anidb_up.url)
        )
        if p_anime_anidb is not None:
            anime_id = p_anime_anidb.anime_id
            await state.update_data(anime_id=anime_id)
            return True

    anidb_res = await parse_anime_page(anidb_up, AniDBPageParser, state, "anidb")
    if not anidb_res:
        return False

    anidb_pp = await state.get_value("anidb_pp")
    mal_res = await parse_anime_page(
        MALUrlParser(anidb_pp.mal_url), MALPageParser, state, "mal"
    )
    if not mal_res:
        return False

    mal_up = await state.get_value("mal_up")
    shiki_res = await parse_anime_page(
        ShikiUrlParser.from_mal_id(mal_up.mal_id), ShikiPageParser, state, "shiki"
    )
    if not shiki_res:
        return False

    return True


async def as_anime_query(message: Message, state: FSMContext) -> bool:
    mal_up = MALUrlParser(message.text)
    if mal_up.is_valid():
        return await as_mal_url(mal_up, state)
    shiki_up = ShikiUrlParser(message.text)
    if shiki_up.is_valid():
        return await as_shiki_url(shiki_up, state)
    anidb_up = AniDBUrlParser(message.text)
    if anidb_up.is_valid():
        return await as_anidb_url(anidb_up, state)
    # TODO: as search query
    return False


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
