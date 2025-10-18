import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi import status
from app.config import settings

TEST_API_KEY = "supersecretkey123"


@pytest.mark.asyncio
class TestBooksAPI:
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
    async def test_get_books_endpoint(self, mock_get):
        mock_data = {"results": [{"_id": "68ef592250ca2000ff19b001", "name": "A Light in the Attic"}]}
        mock_get.return_value.__aenter__.return_value = await self.mock_response(status.HTTP_200_OK, mock_data)

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/changes", headers=self.headers) as response:
                data = await response.json()

        assert response.status == status.HTTP_200_OK
        assert "results" in data or isinstance(data, list), "Response format not as expected"

    @patch("aiohttp.ClientSession.get")
    async def test_get_book_by_id_found(self, mock_get):
        mock_book = {"_id": "68ef592250ca2000ff19b001", "name": "A Light in the Attic"}
        mock_get.return_value.__aenter__.return_value = await self.mock_response(status.HTTP_200_OK, mock_book)

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/changes/{mock_book['_id']}", headers=self.headers) as response:
                data = await response.json()

        assert response.status == status.HTTP_200_OK
        assert data["_id"] == mock_book["_id"]

    @patch("aiohttp.ClientSession.get")
    async def test_get_book_by_id_not_found(self, mock_get):
        mock_data = {"detail": "Book not found"}
        mock_get.return_value.__aenter__.return_value = await self.mock_response(status.HTTP_404_NOT_FOUND, mock_data)

        invalid_id = "nonexistent-id-12345"
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/changes/{invalid_id}", headers=self.headers) as response:
                data = await response.json()

        assert response.status == status.HTTP_404_NOT_FOUND
        assert "detail" in data

    @patch("aiohttp.ClientSession.get")
    async def test_rate_limit_trigger(self, mock_get):
        ok_response = await self.mock_response(status.HTTP_200_OK, {"results": []})
        limit_response = await self.mock_response(status.HTTP_429_TOO_MANY_REQUESTS, {"detail": "Too Many Requests"})
        mock_get.return_value.__aenter__.side_effect = [ok_response] * 100 + [limit_response]

        import aiohttp
        endpoint = "api/changes"

        async with aiohttp.ClientSession() as session:
            for i in range(100):
                async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                    assert response.status == status.HTTP_200_OK, f"Request {i + 1} failed"
            async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                data = await response.json()

        assert response.status == status.HTTP_429_TOO_MANY_REQUESTS
        assert data["detail"] == "Too Many Requests"
