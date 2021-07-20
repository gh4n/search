import json
import random

from pathlib import Path

import pytest

from zensearch.store.file import FileStore
from zensearch.model.user import User
from zensearch.model.ticket import Ticket
from zensearch.db.user_ticket_db import UserTicketDatabase
from zensearch.index.inverted import InvertedIndex

@pytest.fixture()
def user_documents():
    store = FileStore(Path("tests/resources"))
    raw_data = store.load("users.json")
    users = []

    for user in raw_data:
        user_model = User(user)
        users.append(user_model)
    return users

@pytest.fixture()
def ticket_documents():
    store = FileStore(Path("tests/resources"))
    raw_data = store.load("tickets.json")
    tickets = []

    for ticket in raw_data:
        ticket_model = Ticket(ticket)
        tickets.append(ticket_model)
    return tickets

def test_inverted_index_should_contain_all_user_fields(user_documents):
    index = InvertedIndex().build(user_documents)

    for user_id, document in enumerate(user_documents):
        for key, value in document.record.items():
            key , value = str(key), str(value)
            assert user_id in index[key][value]

def test_inverted_index_should_contain_all_ticket_fields(ticket_documents):
    index = InvertedIndex().build(ticket_documents)

    for ticket_id, document in enumerate(ticket_documents):
        for key, value in document.record.items():
            key = str(key)

            if isinstance(value, list):
                for item in value:
                    item = str(item)
                    assert ticket_id in index[key][item]
            else:
                value = str(value)
                assert ticket_id in index[key][value]

