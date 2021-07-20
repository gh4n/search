from abc import ABC, abstractmethod
from typing import Any, Dict


class Index(ABC):
    @abstractmethod
    def build(records: Dict[str, Any]) -> None:
        pass
