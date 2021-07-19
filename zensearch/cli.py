from pathlib import Path

from zensearch.store.file import FileStore
from zensearch.db.user_ticket_db import UserTicketDatabase

import inquirer
import pprint

store = FileStore(Path("data"))
db = UserTicketDatabase(store)
db.setup()


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
        choices=db.user_fields if entity == "users" else db.ticket_fields,
    ),
    inquirer.Text("value", message="Enter a search term", default=""),
]

print(db.tickets_index)

answers = inquirer.prompt(questions)
# print(answers)
results = db.query(entity[:len(entity) - 1], answers["key"], answers["value"])
# results = db.query("user", "verified", "")
# print(db.users_index.query("verified", "True"))

# print(list(results))
# print(db.users_index.index["verified"]["False"])
# print(list(results))
for result in results:
    print(result)

# print(db.users_index.index)
