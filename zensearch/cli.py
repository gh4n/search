from pathlib import Path
from typing import Dict, List, Any, Iterable, Tuple, Union
import sys

from zensearch.model.model import Model
from zensearch.store.file import FileStore
from zensearch.db.user_ticket_db import UserTicketDatabase

import inquirer
import yaml


class Prompt:
    def __init__(
        self, base_dir: Path, users_filename: str, tickets_filename: str
    ) -> None:
        self.base_dir = base_dir
        self.user_filename = users_filename
        self.tickets_filename = tickets_filename
        self.store = FileStore(base_dir)
        self.db = UserTicketDatabase(self.store)

    def setup(self) -> None:
        self.db.load_data(self.user_filename, self.tickets_filename)
        self.db.build_index()
        self.db.link_users_tickets()
        self.db.link_ticket_assignees()

    def prompt(self):
        ask_action = [
            inquirer.List(
                "action",
                message="What would you do?",
                choices=["search", "quit"],
            )
        ]

        action = inquirer.prompt(ask_action)["action"]
        if action == "quit":
            print("Until next time...")
            sys.exit()

        ask_entity = [
            inquirer.List(
                "entity",
                message="What would you like to search for?",
                choices=["users", "tickets"],
            )
        ]

        entity = inquirer.prompt(ask_entity)["entity"]

        if entity == "QUIT":
            sys.exit()

        ask_search_term = [
            inquirer.List(
                "key",
                message="What field would you like to search on?",
                choices=self.db.user_schema
                if entity == "users"
                else self.db.ticket_schema,
            ),
            inquirer.Text("value", message="Enter a search term", default=""),
        ]

        answers = inquirer.prompt(ask_search_term)

        results = self.db.query(entity, answers["key"], answers["value"], related=True)

        if results:
            self.display(results)
        else:
            print("Nothing found")

    def display(self, results: Iterable[Dict[Any, Any]]) -> None:
        print("\n-----results------\n")
        for result in results:
            print(yaml.dump(result))
