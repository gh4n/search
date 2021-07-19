from pathlib import Path
from typing import Dict, List, Any, Iterable, Tuple, Union

from zensearch.db.database import Database
from zensearch.store.store import Store
from zensearch.index.index import Index
from zensearch.model.model import Model
from zensearch.model.user import User
from zensearch.model.ticket import Ticket

from zensearch.store.file import FileStore
from zensearch.index.inverted import InvertedIndex
from zensearch.consts import USER_SCHEMA, TICKET_SCHEMA


class UserTicketDatabase(Database):
    def __init__(self, store: Store) -> None:
        self.store = store
        self.users = []
        self.tickets = []
        self.users_index = InvertedIndex()
        self.tickets_index = InvertedIndex()
        self.user_schema = USER_SCHEMA
        self.ticket_schema = TICKET_SCHEMA

    def load_data(self, user_filename, tickets_filename) -> None:
        users = self.store.load(user_filename)
        tickets = self.store.load(tickets_filename)

        # Ideally I should validate that the document matches the schema
        for user in users:
            user_model = User(user)
            self.users.append(user_model)
            user_model.record = self.user_schema | user_model.record

        for ticket in tickets:
            ticket_model = Ticket(ticket)
            self.tickets.append(ticket_model)
            ticket_model.record = self.ticket_schema | ticket_model.record

    def build_index(self) -> None:
        self.users_index.build(self.users)
        self.tickets_index.build(self.tickets)

    def link_users_tickets(self) -> None:
        for user in self.users:
            user.tickets = self.tickets_index.index["assignee_id"][user.id]

    def link_ticket_assignees(self) -> None:
        for ticket in self.tickets:

            assignee_id = str(ticket.assignee_id)
            if assignee_id in self.users_index.index["_id"]:
                linked_user = self.users_index.index["_id"][assignee_id]

            if linked_user:
                ticket.assignee_name = self.users[linked_user[0]].record["name"]

    def link_related(self) -> None:
        self.link_users_tickets()
        self.link_ticket_assignees()

    def get_user_tickets(self, user: User) -> List[Ticket]:
        tickets = []
        for ticket_id in user.tickets:
            tickets.append(self.tickets[ticket_id])
        return tickets

    def setup(self, user_filename, tickets_filename) -> None:
        self.load_data(user_filename, tickets_filename)
        self.build_index()
        self.link_related()

    def query(
        self, entity: str, key: str, value: str
    ) -> Iterable[Tuple[Model, Union[str, List[str]]]]:

        if entity == "user":
            user_ids = self.users_index.query(key, value)
            for user_id in user_ids:
                user = self.users[user_id]
                tickets = [
                    ticket.record["subject"] for ticket in self.get_user_tickets(user)
                ]
                yield (user, tickets)

        elif entity == "ticket":
            ticket_ids = self.tickets_index.query(key, value)
            for ticket_id in ticket_ids:
                ticket = self.tickets[ticket_id]
                yield (ticket.record, ticket.assignee_name)

        else:
            raise LookupError(f"{entity} not found! Please search on users or tickets")

    def export(self, filename: str) -> None:
        self.store.save([self.users_index, self.ticket_index], filename)
