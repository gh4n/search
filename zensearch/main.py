from pathlib import Path

from zensearch.cli import Prompt


cli = Prompt(Path("data"), "users.json", "tickets.json")
cli.setup()
cli.prompt()
