from abc import ABC, abstractmethod
from typing import Dict, Any

class Model(ABC):
    @abstractmethod
    def __init__(self, record: Dict[Any, Any]) -> None:
        self.record = record
