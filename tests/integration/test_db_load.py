import json
import random

from pathlib import Path

import pytest

from zensearch.store.file import FileStore
from zensearch.db.user_ticket_db import UserTicketDatabase


@pytest.fixture(scope="session")
def base_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("records")


@pytest.fixture
def incomplete_ticket_records(base_dir):
    fields_to_remove = ["_id", "created_at", "type", "subject", "assignee_id", "tags"]

    with open("tests/resources/tickets.json") as fh:
        tickets = json.load(fh)

    for ticket in tickets:
        index = random.randint(0, 5)
        if fields_to_remove[index] in ticket:
            ticket = ticket.pop(fields_to_remove[index])

    filename = base_dir / "incomplete_tickets.json"

    with open(filename, "w") as fh:
        fh.write(json.dumps(tickets))

    return base_dir


@pytest.fixture
def incomplete_user_records(base_dir):
    fields_to_remove = ["_id", "created_at", "name", "verified"]

    with open("tests/resources/users.json") as fh:
        users = json.load(fh)

    for user in users:
        index = random.randint(0, 3)
        if fields_to_remove[index] in user:
            user = user.pop(fields_to_remove[index])

    filename = base_dir / "incomplete_users.json"

    with open(filename, "w") as fh:
        fh.write(json.dumps(users))

    return base_dir


def test_db_should_relax_model_records_to_schema(
    incomplete_ticket_records, incomplete_user_records
):
    store = FileStore(incomplete_ticket_records)
    db = UserTicketDatabase(store)
    db.load_data("incomplete_users.json", "incomplete_tickets.json")

    for ticket in db.tickets:
        assert ticket.record.keys() == db.ticket_schema.keys()

    for user in db.users:
        assert user.record.keys() == db.user_schema.keys()
