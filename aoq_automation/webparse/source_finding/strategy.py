from abc import ABC, abstractmethod
from typing import *

from aoq_automation.database.models import *


class SourceFindingStrategy(ABC):
    @abstractmethod
    async def find_source(self, qitem_id: int) -> Optional[QItemSource]: ...
