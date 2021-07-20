import json

from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict

from zensearch.store.store import Store


class FileStore(Store):
    def __init__(self, basedir: Path) -> None:
        self.basedir = basedir

    def load(self, name: str) -> Dict[str, Any]:
        load_path = self.basedir / name

        with open(load_path, "r") as file_handle:
            try:
                records = json.load(file_handle)
            except JSONDecodeError as err:
                print(f"Bad format {load_path}, please provide a valid JSON file")
                raise err
        return records
