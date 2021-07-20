from typing import Dict, Any

from zensearch.model.model import Model


class Ticket(Model):
    def __init__(self, record: Dict[Any, Any]) -> None:
        self.record = record
        self.assignee_name = ""
        self._assignee_id = None

    @property
    def assignee_id(self) -> str:
        return self.record["assignee_id"] if "assignee_id" in self.record else ""
