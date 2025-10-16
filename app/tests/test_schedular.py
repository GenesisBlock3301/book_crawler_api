import pytest
from unittest.mock import patch
from datetime import datetime
from bson import ObjectId
import hashlib

from app.scheduler.detector import detect_changes


@pytest.fixture
def mock_collections():
    with patch('app.scheduler.detector.books_collection') as books_mock, \
            patch('app.scheduler.detector.changes_collection') as changes_mock:
        yield books_mock, changes_mock


@pytest.mark.asyncio
async def test_detect_changes_no_changes(mock_collections):
    books_mock, changes_mock = mock_collections
    book = {
        "_id": ObjectId(),
        "title": "Test Book",
        "author": "Test Author"
    }

    book["hash"] = hashlib.md5(str(book).encode()).hexdigest()

    books_mock.find.return_value.__aiter__.return_value = [book]

    await detect_changes()

    changes_mock.insert_one.assert_not_called()
    books_mock.update_one.assert_not_called()


@pytest.mark.asyncio
async def test_detect_changes_with_modification(mock_collections):
    books_mock, changes_mock = mock_collections

    book = {
        "_id": ObjectId(),
        "title": "Modified Book",
        "author": "Test Author",
        "hash": "old_hash_value"
    }

    books_mock.find.return_value.__aiter__.return_value = [book]

    await detect_changes()

    changes_mock.insert_one.assert_called_once()
    inserted_doc = changes_mock.insert_one.call_args[0][0]

    assert inserted_doc["book_id"] == book["_id"]
    assert inserted_doc["changes"] == "Detected modification"
    assert isinstance(inserted_doc["timestamp"], datetime)

    books_mock.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_detect_changes_multiple_books(mock_collections):
    books_mock, changes_mock = mock_collections

    book1 = {"_id": ObjectId(), "title": "Book 1", "hash": "old_hash"}
    book2 = {"_id": ObjectId(), "title": "Book 2"}
    book2["hash"] = hashlib.md5(str(book2).encode()).hexdigest()
    book3 = {"_id": ObjectId(), "title": "Book 3", "hash": "another_old_hash"}

    books_mock.find.return_value.__aiter__.return_value = [book1, book2, book3]

    await detect_changes()

    assert changes_mock.insert_one.call_count == 2
    assert books_mock.update_one.call_count == 2


@pytest.mark.asyncio
async def test_detect_changes_empty_collection(mock_collections):
    books_mock, changes_mock = mock_collections
    books_mock.find.return_value.__aiter__.return_value = []

    await detect_changes()

    changes_mock.insert_one.assert_not_called()
    books_mock.update_one.assert_not_called()
