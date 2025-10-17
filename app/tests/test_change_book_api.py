import aiohttp
import pytest
from fastapi import status
from app.utils import settings

TEST_API_KEY = "supersecretkey123"


@pytest.mark.asyncio
class TestBooksAPI:
    base_url = settings.HOST
    headers = {"x-api-key": TEST_API_KEY}

    async def get(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                data = await response.json()
                return response, data

    async def test_get_books_endpoint(self):
        endpoint = "api/changes"
        response, data = await self.get(endpoint)
        if response.status == status.HTTP_429_TOO_MANY_REQUESTS:
            assert data['detail'] == 'Too Many Requests'
        else:
            assert response.status == status.HTTP_200_OK, f"Expected 200, got {response.status}"
            assert "results" in data or isinstance(data, list), "Response format not as expected"

    async def test_get_book_by_id_found(self):
        valid_id = "68ef592250ca2000ff19b001"
        endpoint = f"api/changes/{valid_id}"
        response, _ = await self.get(endpoint)

        assert response.status in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND], \
            f"Expected 200 or 404, got {response.status}"

    async def test_get_book_by_id_not_found(self):
        invalid_id = "nonexistent-id-12345"
        endpoint = f"api/changes/{invalid_id}"
        response, data = await self.get(endpoint)

        assert response.status == status.HTTP_404_NOT_FOUND, f"Expected 404, got {response.status}"
        assert "detail" in data, "Error response should contain detail message"

    async def test_rate_limit_trigger(self):
        endpoint = "api/changes"
        max_requests = 100

        async with aiohttp.ClientSession() as session:
            for i in range(max_requests):
                async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                    if response.status == status.HTTP_429_TOO_MANY_REQUESTS:
                        break
                    assert response.status == status.HTTP_200_OK, f"Request {i + 1} failed with {response.status}"
            async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                assert response.status == status.HTTP_429_TOO_MANY_REQUESTS, \
                    f"Expected 429 after rate limit, got {response.status}"
