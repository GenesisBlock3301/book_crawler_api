import pytest
import aiohttp
from unittest.mock import patch, AsyncMock
from fastapi import status
from app.config import settings

TEST_API_KEY = "supersecretkey123"
mock_changes = [
    {
        "_id": "68ef592250ca2000ff19b001",
        "book_id": "68ef592250ca2000ff19b001",
        "timestamp": "2025-10-15T00:00:00+00:00",
        "changes": "Demo modification detected"
    }
]

@pytest.mark.asyncio
class TestGenerateChangeReport:
    base_url = settings.HOST
    headers = {"x-api-key": TEST_API_KEY}

    @patch("app.services.generate_report_service", new_callable=AsyncMock)
    async def test_generate_report_json(self, mock_service):
        mock_service.return_value = {"date": "2025-10-18", "total": 1, "results": mock_changes}

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/report/?format=json", headers=self.headers) as response:
                data = await response.json()
        if data['detail'] == "No changes found for this date.":
            assert response.status == status.HTTP_404_NOT_FOUND
        else:
            assert response.status == status.HTTP_200_OK
            assert data["total"] >= 1