from pathlib import Path

from zensearch.store.file import FileStore
from zensearch.db.user_ticket_db import UserTicketDatabase

import inquirer
import pprint

store = FileStore(Path("data"))
db = UserTicketDatabase(store)
db.setup("users.json", "tickets.json")

questions = [
    inquirer.List(
        "entity",
        message="What would you like to search for?",
        choices=["users", "tickets"],
    )
]

entity = inquirer.prompt(questions)["entity"]

questions = [
    inquirer.List(
        "key",
        message="What field would you like to search on?",
        choices=db.user_schema if entity == "users" else db.ticket_schema,
    ),
    inquirer.Text("value", message="Enter a search term", default=""),
]

# print(db.users_index.index)


answers = inquirer.prompt(questions)
results = db.query(entity[:len(entity) - 1], answers["key"], answers["value"])
for result in results:
    print(result)

