from functools import wraps
from typing import *

from aiogram.dispatcher.event.handler import CallableObject, CallbackType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aoq_automation.database.database import db
from aoq_automation.database.models import *


def redirect_to(callback: CallbackType):
    def decorator(action: CallbackType):
        @wraps(action)
        async def wrapper(*args, **kwargs):
            await CallableObject(action).call(*args, **kwargs)
            await CallableObject(callback).call(*args, **kwargs)

        return wrapper

    return decorator


def as_model_parameter(model: Type[Base], parameter: str) -> bool:
    """
    Creates filter, that interprets message text as model parameter,
    and if it's valid, saves parameter, processed by model, into state[parameter].
    """

    async def filter(message: Message, state: FSMContext) -> bool:
        try:
            value = model(**{parameter: message.text}).__getattribute__(parameter)
            await state.update_data({parameter: value})
            return True
        except ValueError:
            return False

    return filter


def get_user_mark(message: Message) -> str:
    return f"manual_{message.from_user.id}"


async def save_qitem_from_dict(values: Dict[str, Any], added_by: str) -> bool:
    """
    Takes all required parameters from values, and saves
    qitem(+source, difficulty, timing) into db
    """

    async with db.async_session() as session:
        qitem = QItem(
            anime_id=values["anime_id"],
            category=values["category"],
            number=values["number"],
        )
        session.add(qitem)

        qitem_source = QItemSource(
            qitem=qitem,
            platform="youtube",
            path=values["path"],
            added_by=added_by,
        )
        session.add(qitem_source)

        qitem_difficulty = QItemDifficulty(
            qitem=qitem,
            value=values["value"],
            added_by=added_by,
        )
        session.add(qitem_difficulty)

        qitem_timing = QItemSourceTiming(
            qitem_source=qitem_source,
            guess_start=values["guess_start"],
            reveal_start=values["reveal_start"],
            added_by=added_by,
        )
        session.add(qitem_timing)

        try:
            await session.commit()
            return True
        except:
            return False
