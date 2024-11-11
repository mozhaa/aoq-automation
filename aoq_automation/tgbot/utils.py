from aiogram.filters import Filter
from aiogram.types import Message
from typing import Protocol, Dict, Any, List
from inspect import iscoroutine


class FunctionalFilter(Protocol):
    def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]: ...


class AsyncFunctionalFilter(Protocol):
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]: ...


class Chain(Filter):
    """Chain filters into one.

    Returned kwargs from filter will be passed into arguments of next one
    (eventually, all kwargs will be accumulated into returning value)."""

    def __init__(
        self, filters: List[Filter | FunctionalFilter | AsyncFunctionalFilter]
    ) -> None:
        self.filters = filters

    async def __call__(self, message: Message) -> bool | Dict[str, Any]:
        kwargs = {}
        for filter in self.filters:
            new_kwargs = filter(message, **kwargs)
            if iscoroutine(new_kwargs):
                new_kwargs = await new_kwargs
            if new_kwargs is False:
                return False
            kwargs.update(new_kwargs)
        return kwargs
