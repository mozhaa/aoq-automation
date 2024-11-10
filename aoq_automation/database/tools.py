from .models import *
from .database import connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select


@connection
async def set_anime(session: AsyncSession, mal_url: str) -> Anime:
    try:
        anime = await session.scalar(select(Anime).filter_by(mal_url=mal_url))
        if anime:
            # Anime already in database
            return anime
        else:
            # Add anime into database
            anime = Anime(title_ro="TODO WTF", mal_url=mal_url)
            session.add(anime)
            await session.commit()
            return anime
    except SQLAlchemyError:
        await session.rollback()
