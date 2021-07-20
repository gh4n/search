import json
from pathlib import Path
from json import JSONDecodeError
import pytest

from zensearch.store.file import FileStore


@pytest.fixture
def expected_user_data():
    with open("tests/resources/users.json") as fh:
        return json.load(fh)


def test_file_store_should_load_dict(expected_user_data):
    filestore = FileStore(Path("tests/resources"))
    loaded_file = filestore.load("users.json")

    assert loaded_file == expected_user_data


def test_file_store_load_malformed_json_should_raise_error():
    filestore = FileStore(Path("tests/resources"))
    with pytest.raises(JSONDecodeError) as exception:
        filestore.load("malformed.json")
