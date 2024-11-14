from sqlalchemy import select
from typing import *
from .models import Base
from .database import db


async def get_or_create(obj: Base, key_columns: List[str]) -> int:
    async with db.async_session() as session:
        stmt = select(type(obj)).filter_by(**{k: v for k, v in obj.__dict__.items() if k in key_columns})
        result = await session.execute(stmt)
        try:
            obj = result.scalar_one()
            return obj.id
        except:
            session.add(obj)
            await session.commit()
            return await obj.awaitable_attrs.id
