from typing import *

from sqlalchemy import select

from .database import db
from .models import Base


def retrieve_key_columns(obj: Base, key_columns: List[str]) -> Dict[str, Any]:
    return {k: v for k, v in obj.__dict__.items() if k in key_columns}


async def get_or_create(obj: Base, key_columns: List[str]) -> Tuple[int, bool]:
    """
    If object with `key_columns` same as `obj` exists in database, retrieve it and return its id and False
    Else, insert `obj` into database and return its id and True
    """
    async with db.async_session() as session:
        stmt = select(type(obj)).filter_by(**retrieve_key_columns(obj, key_columns))
        result = await session.execute(stmt)
        try:
            obj = result.scalar_one()
            return obj.id, False
        except:
            session.add(obj)
            await session.commit()
            return await obj.awaitable_attrs.id, True
