from abc import abstractmethod
from typing import Type

from aoq_automation.database.models import Base


class PageParser:
    def __init__(self, url: str) -> None:
        self._url = url
        self._valid = False

    @property
    def url(self) -> str:
        return self._url

    def is_valid(self) -> bool:
        return self._valid

    @abstractmethod
    async def load_pages(self) -> None: ...

    @abstractmethod
    def as_parsed(self) -> Type[Base]: ...
