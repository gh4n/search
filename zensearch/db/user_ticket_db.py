from pathlib import Path
from typing import Dict, List, Any

from zensearch.db.database import Database
from zensearch.store.store import Store
from zensearch.index.index import Index
from zensearch.model.model import Model
from zensearch.model.user import User
from zensearch.model.ticket import Ticket

from zensearch.store.file import FileStore
from zensearch.index.inverted import InvertedIndex


class UserTicketDatabase(Database):
    def __init__(self, store: Store) -> None:
        self.store = store
        self.users = []
        self.tickets = []
        self.users_index = InvertedIndex()
        self.tickets_index = InvertedIndex()
        self.user_fields = None
        self.ticket_fields = None

    def load_data(self) -> None:
        users = store.load("users.json")
        tickets = store.load("tickets.json")

        for user in users:
            user_model = User(user)
            self.users.append(User(user))

        for ticket in tickets:
            self.tickets.append(Ticket(ticket))

    @staticmethod
    def get_unique_fields(models: List[Model]) -> Dict[Any, Any]:
        unique_fields = {}

        for model in models:
            for field in model.record.keys():
                unique_fields[field] = ""
        return unique_fields

    def set_unique_fields(self) -> None:
        self.user_fields = self.get_unique_fields(self.users)
        self.ticket_fields = self.get_unique_fields(self.tickets)

    def add_missing_props(self) -> None:
        for user in self.users:
            user.record = self.user_fields | user.record

        for ticket in self.tickets:
            ticket.record = self.ticket_fields | ticket.record

    def build_index(self):
        self.users_index.build(self.users)
        self.tickets_index.build(self.tickets)

    def link_users_tickets(self):
        for user in self.users:
            user_id = user.record["_id"]
            if user_id in self.tickets_index.index["assignee_id"]:
                user.record["tickets"] = self.tickets_index.index["assignee_id"][user_id]
            else:
                user.record["tickets"] = []

    def link_ticket_assignees(self):
        for ticket in self.tickets:
            assignee_id = ticket.record["assignee_id"]
            if assignee_id in self.users_index.index["_id"]:
                ticket.record["assignee_name"] = self.users[self.users_index.index["_id"][assignee_id][0]].record["name"]
            else:
                ticket.record["assignee_name"] = ""

    def query(self, entity: str, key: str, value: str):
        if entity == "user":
            user_ids = self.users_index.query(key, value)
            for user_id in user_ids:
                print(self.users[user_id].record)
                for ticket_id in self.users[user_id].record["tickets"]:
                    print(self.tickets[ticket_id].record)
        if entity == "ticket":
            ticket_ids = self.tickets_index.query(key, value)
            for ticket_id in ticket_ids:
                print(self.tickets[ticket_id].record)


if __name__ == "__main__":
    store = FileStore(Path("/home/han/Projects/usa/interviews/coding-challenge-2021"))
    db = UserTicketDatabase(store)
    db.load_data()
    db.set_unique_fields()
    db.add_missing_props()
    db.build_index()
    db.link_users_tickets()
    db.link_ticket_assignees()
    db.query("ticket", "tags", "Georgia")
