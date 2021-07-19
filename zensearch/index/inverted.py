from typing import Iterable, Any, Dict, List
from pathlib import Path
from collections import defaultdict

from zensearch.model.model import Model
from zensearch.index.index import Index


class InvertedIndex(Index):
    def __init__(self) -> None:
        self.documents = None
        self.index = {}
    
    def build(self, documents: List[Model]) -> Dict[str, List[int]]:
        self.index = defaultdict(list)
        for doc_id, document in enumerate(documents):
            for key, value in document.record.items():

                key = str(key)
                if key not in self.index:
                    self.index[key] = defaultdict(list)

                if isinstance(value, list):
                    for item in value:
                        item = str(item)
                        self.index[key][item].append(doc_id)
                    continue

                value = str(value)

                self.index[key][value].append(doc_id)
        return self.index

    def query(self, key: str, value: str) -> List[int]:
        return self.index[key][value]
