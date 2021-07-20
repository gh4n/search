from pathlib import Path
from typing import Dict, List, Any, Iterable, Tuple, Union

from zensearch.db.database import Database
from zensearch.store.store import Store
from zensearch.model.model import Model

from zensearch.model.user import User
from zensearch.model.ticket import Ticket
from zensearch.index.inverted import InvertedIndex
from zensearch.model.consts import USER_SCHEMA, TICKET_SCHEMA


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

        # For production I would validate that the document matches the schema here
        # otherwise raise an error/decide what behvaiour I want to occur
        for user in users:
            user_model = User(user)
            self.users.append(user_model)

            # Merge schema and record so that all columns are present
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
            user.tickets = self.tickets_index.query("assignee_id", str(user.id))

    def link_ticket_assignees(self) -> None:
        for ticket in self.tickets:
            assignee = self.users_index.query("_id", str(ticket.assignee_id))
            if assignee:
                ticket.assignee_name = self.users[assignee[0]].record["name"]

    def get_user_tickets(self, user: User) -> List[Ticket]:
        return [self.tickets[ticket_id] for ticket_id in user.tickets]

    def query(
        self, entity: str, key: str, value: str, related=False
    ) -> Iterable[Dict[Any, Any]]:

        results = []
        if entity == "users":
            user_ids = self.users_index.query(key, value)
            for user_id in user_ids:
                user = self.users[user_id]
                if related:
                    tickets = [
                        ticket.record["subject"]
                        for ticket in self.get_user_tickets(user)
                    ]
                    user.record["tickets"] = tickets
                results.append(user.record)
        elif entity == "tickets":
            ticket_ids = self.tickets_index.query(key, value)
            for ticket_id in ticket_ids:
                ticket = self.tickets[ticket_id]
                if related:
                    ticket.record["assignee_name"] = ticket.assignee_name
                results.append(ticket.record)
        else:
            raise LookupError(f"{entity} not found! Please search on users or tickets")

        return results
