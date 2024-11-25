from typing import List

from aiogram.dispatcher.event.handler import FilterObject
from aiogram.filters import Filter


class Filterset(Filter):
    """
    Set of filters in disjunctive normal form
    """

    def __init__(self, filters: List[List[Filter]] | List[Filter] | Filter) -> None:
        if not isinstance(filters, list):
            self._table = [[filters]]
        elif isinstance(filters, list) and all(
            [not isinstance(el, list) for el in filters]
        ):
            self._table = [filters]
        else:
            self._table = filters

    async def __call__(self, *args, **kwargs) -> bool:
        for row in self._table:
            row_failed = False
            for filter in row:
                result = await FilterObject(filter).call(*args, **kwargs)
                if result is False:
                    row_failed = True
                    break
            if not row_failed:
                return True
        return False
