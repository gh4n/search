from abc import ABC, abstractmethod
from typing import Iterable, Any, Optional, Dict
from pathlib import Path

from zensearch.store.store import Store
from zensearch.index.index import Index

class Database(ABC):
    @abstractmethod
    def __init__(self, store: Store) -> None:
        self.store = store

    @abstractmethod
    def query() -> Iterable[Dict[Any, Any]]:
        pass
