from abc import ABC, abstractmethod
from typing import Iterable, Any, Optional, Dict
from pathlib import Path

class Index(ABC):
    @abstractmethod
    def build(records: Dict[str, Any]) -> None:
        pass
