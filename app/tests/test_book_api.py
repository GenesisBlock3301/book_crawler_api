import aiohttp
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi import status
from app.config import settings

test_books = [
    {
        "_id": "68ef592250ca2000ff19b001",
        "name": "A Light in the Attic",
        "availability": "In stock (22 available)",
        "category": "Unknown",
        "crawl_timestamp": "2025-10-15T14:34:15.996968",
        "description": "...",
        "image_url": "https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg",
        "num_reviews": 0,
        "price_excl_tax": 51.77,
        "price_incl_tax": 51.77,
        "rating": "Three",
        "row_html": "...",
        "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    }
]

TEST_API_KEY = "supersecretkey123"


@pytest.mark.asyncio
class TestChangeBooksAPI:
    base_url = settings.HOST
    headers = {"x-api-key": TEST_API_KEY}

    @staticmethod
    async def mock_response(status_code, json_data):
        await asyncio.sleep(0)
        mock_resp = AsyncMock()
        mock_resp.status = status_code
        mock_resp.json = AsyncMock(return_value=json_data)
        return mock_resp

    @patch("aiohttp.ClientSession.get")
    async def test_get_books_no_filter(self, mock_get):
        mock_data = {"results": test_books}
        mock_get.return_value.__aenter__.return_value = await self.mock_response(status.HTTP_200_OK, mock_data)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/books", headers=self.headers) as response:
                data = await response.json()

        assert response.status == status.HTTP_200_OK
        assert any(book["name"] == "A Light in the Attic" for book in data["results"])

    @patch("aiohttp.ClientSession.get")
    async def test_get_book_by_id_not_found(self, mock_get):
        mock_data = {"detail": "Book not found"}
        mock_get.return_value.__aenter__.return_value = await self.mock_response(status.HTTP_404_NOT_FOUND, mock_data)

        book_id = "68ef592950ca2000ff19b118"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/books/{book_id}", headers=self.headers) as response:
                data = await response.json()

        assert response.status == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "Book not found"
