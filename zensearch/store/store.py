from abc import ABC, abstractmethod
from typing import Iterable, Optional, Dict, Any


class Store(ABC):
    @abstractmethod
    def save(self, records: Iterable[Dict[str, Any]], name: str) -> None:
        pass

    @abstractmethod
    def load(self, name: str) -> Iterable[Dict[str, Any]]:
        pass
