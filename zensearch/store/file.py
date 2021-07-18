import json

from pathlib import Path
from typing import Iterable, Any, Dict, Optional

from zensearch.store.store import Store


class FileStore(Store):
    def __init__(self, basedir: Path) -> None:
        self.basedir = basedir

    def save(self, records: Iterable[Optional[Dict[str, Any]]], name: str) -> None:
        output_path = self.basedir / name

        with open(output_path, "w") as file_handle:
            for record in records:
                file_handle.write(json.dumps(record))

    def load(self, name: str) -> Dict[str, Any]:
        load_path = self.basedir / name

        with open(load_path, "r") as file_handle:
            records = json.load(file_handle)
        return records
