import json
import random

from pathlib import Path
from typing import List, Dict, Any
from copy import deepcopy

import pytest

from zensearch.store.file import FileStore
from zensearch.model.user import User
from zensearch.model.ticket import Ticket
from zensearch.db.user_ticket_db import UserTicketDatabase
from zensearch.index.inverted import InvertedIndex

@pytest.fixture()
def db():
    store = FileStore(Path("tests/resources"))
    db = UserTicketDatabase(store)
    db.load_data("users.json", "tickets.json")
    db.build_index()
    return db

def test_db_shoud_query_all_user_fields_correctly(db):
    users = deepcopy(db.users)

    for user_id, doc in enumerate(db.users):
        for key, value in doc.record.items():
            key , value = str(key), str(value)
            assert doc.record in db.query("users", key, value)

def test_db_shoud_query_all_ticket_fields_correctly(db):
    tickets = deepcopy(db.tickets)

    for ticket_id, doc in enumerate(tickets):
        for key, value in doc.record.items():

            key = str(key)

            if isinstance(value, list):
                print(value)
                for item in value:
                    item = str(item)
                    assert doc.record in db.query("tickets", key, item)
            else:
                value = str(value)
                results = db.query("tickets", key, value)  
                assert doc.record in results

# def test_db_should_not_find_unindexed_tickets(db)