from typing import Dict, Any

from zensearch.model.model import Model


class User(Model):
    def __init__(self, record: Dict[Any, Any]) -> None:
        self.record = record
        self._id = None
        self.tickets = []

    @property
    def id(self) -> str:
        return self.record["_id"] if "_id" in self.record else ""
