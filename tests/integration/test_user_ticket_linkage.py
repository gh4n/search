import json
import random
from pathlib import Path
from typing import List, Dict, Any
from copy import deepcopy

import pytest
from faker import Faker

from zensearch.store.file import FileStore
from zensearch.model.user import User
from zensearch.model.ticket import Ticket
from zensearch.db.user_ticket_db import UserTicketDatabase
from zensearch.index.inverted import InvertedIndex
from zensearch.model.consts import USER_SCHEMA, TICKET_SCHEMA

N_USERS = 100
N_TICKETS = 1000


@pytest.fixture()
def generate_linked_users_tickets():
    faker = Faker()
    users = []

    for id in range(N_USERS):
        user_record = USER_SCHEMA.copy()
        user_record["_id"] = id
        user_record["name"] = faker.name()
        user_record["_tickets"] = []
        users.append(User(user_record))

    tickets = []

    for id in range(N_TICKETS):
        ticket_record = TICKET_SCHEMA.copy()

        # assign a random user to the ticket
        user_id = random.randint(0, N_USERS - 1)
        subject = " ".join(faker.words(3))

        ticket_record["_id"] = id
        ticket_record["assignee_id"] = user_id
        ticket_record["subject"] = subject
        tickets.append(Ticket(ticket_record))

        # append the ticket subject to its assignee
        users[user_id].record["_tickets"].append(subject)
    return (users, tickets)


@pytest.fixture()
def db(generate_linked_users_tickets):
    store = FileStore(Path("tests/resources"))
    db = UserTicketDatabase(store)
    db.users = generate_linked_users_tickets[0]
    db.tickets = generate_linked_users_tickets[1]
    db.build_index()
    return db


def test_ticket_queries_return_linked_assignee(db):
    db.link_ticket_assignees()

    for ticket in db.tickets:
        document = db.query("tickets", "_id", str(ticket.record["_id"]), related=True)[
            0
        ]
        assert (
            document["assignee_name"]
            == db.users[ticket.record["assignee_id"]].record["name"]
        )


def test_user_queries_return_linked_tickets(db):
    db.link_users_tickets()

    for user in db.users:
        document = db.query("users", "_id", str(user.id), related=True)[0]
        assert sorted(document["tickets"]) == sorted(user.record["_tickets"])
