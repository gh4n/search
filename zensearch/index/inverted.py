from typing import Iterable, Any, Dict, List
from pathlib import Path

from zensearch.model.model import Model
from zensearch.index.index import Index


class InvertedIndex(Index):

    def __init__(self) -> None:
        self.documents = None
        self.index = {}

    def build(self, documents: List[Model]) -> None:
        for doc_id, document in enumerate(documents):
            for key, value in document.record.items():
            
                # handle arrays, insert each item of the array a key associate them with a document
                # document ABC: {tags: [meow, purr]}
                #   => [index][tags][meow] = [ABC], [index][tags][purr] = [ABC]
                if isinstance(value, list):
                    for item in value:
                        if key not in self.index:
                            self.index[key] = {}
                        elif item not in self.index[key]:
                            self.index[key][item] = [doc_id]
                        else:
                            self.index[key][item].append(doc_id)
                    continue

                # handle non-array case
                # document ABC: {_id: 123} 
                #   => index[id][123] = [ABC]
                if key not in self.index:
                    self.index[key] = {value: [doc_id]}
                elif value not in self.index[key]:
                    self.index[key][value] = [doc_id]
                else:
                    self.index[key][value].append(doc_id)

    def query(self, key: str, value: str) -> List[int]:
        try:
            return self.index[key][value]
        except KeyError:
            return False
