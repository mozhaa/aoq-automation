from abc import abstractmethod
from typing import Type

from aoq_automation.database.models import Base


class PageParser:
    def __init__(self, url: str) -> None:
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    @abstractmethod
    async def load_pages(self) -> None: ...

    @abstractmethod
    def as_parsed(self) -> Type[Base]: ...

    @property
    @abstractmethod
    def valid(self) -> bool: ...
