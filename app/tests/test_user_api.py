import aiohttp
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from app.utils import settings

TEST_API_KEY = "supersecretkey123"


@pytest.mark.asyncio
class TestUsersAPI:
    """Test suite for User API endpoints"""

    @pytest.fixture
    def mock_user_service(self):
        """Mock UserService for testing"""
        return AsyncMock()

    @pytest.fixture
    def sample_user(self):
        """Sample user data for testing"""
        return {
            "username": "testuser",
            "api_key": "test_api_key_123456",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00",
            "last_used": "2024-01-01T00:00:00"
        }

    @pytest.fixture
    def admin_headers(self):
        """Admin API key headers"""
        return {"x-api-key": "supersecretkey123"}

    # ------------------ Helper methods using aiohttp ------------------ #
    async def _get(self, endpoint: str, headers=None):
        headers = headers or {"x-api-key": TEST_API_KEY}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.HOST}/{endpoint}", headers=headers) as resp:
                return resp, await resp.json()

    async def _post(self, endpoint: str, payload: dict, headers=None):
        headers = headers or {"x-api-key": TEST_API_KEY}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{settings.HOST}/{endpoint}", json=payload, headers=headers) as resp:
                return resp, await resp.json()

    async def _put(self, endpoint: str, payload: dict, headers=None):
        headers = headers or {"x-api-key": TEST_API_KEY}
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{settings.HOST}/{endpoint}", json=payload, headers=headers) as resp:
                return resp, await resp.json()

    async def _delete(self, endpoint: str, headers=None):
        headers = headers or {"x-api-key": TEST_API_KEY}
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{settings.HOST}/{endpoint}", headers=headers) as resp:
                return resp, await resp.json()

    async def test_create_user_success(self, mock_user_service, admin_headers):
        response, data = await self._post("api/users/", {"username": "newuser"}, admin_headers)
        if response.status == status.HTTP_200_OK:
            assert data["message"] == "User & API key created successfully"
            assert data["user"]["username"] == "newuser"
            assert "api_key" in data["user"]
        elif response.status == status.HTTP_400_BAD_REQUEST:
            assert data["detail"] == "User already exists"
        else:
            pytest.fail(f"Unexpected response status: {response.status}")

    async def test_create_user_already_exists(self, mock_user_service, sample_user, admin_headers):
        response, data = await self._post("api/users/", {"username": "testuser"}, admin_headers)
        assert response.status == status.HTTP_400_BAD_REQUEST
        assert data["detail"] == "User already exists"

    async def test_create_user_without_admin_key(self):
        response, data = await self._post("api/users/", {"username": "newuser"},
                                              headers={"x-api-key": "invalid_key"})

        assert response.status == status.HTTP_401_UNAUTHORIZED
        assert data["detail"] == "Invalid API Key"

    async def test_get_user_by_username_success(self, mock_user_service, sample_user, admin_headers):

        response, data = await self._get("api/users/testuser", admin_headers)

        assert response.status == status.HTTP_200_OK
        assert data["username"] == "testuser"
        assert data["api_key"] == '399ec205bd781247d35c66cc6bc9357b'

    async def test_get_user_not_found(self, mock_user_service, admin_headers):
        response, data = await self._get("api/users/nonexistent", admin_headers)

        assert response.status == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "User not found"

    async def test_update_user_success(self, mock_user_service, sample_user, admin_headers):
        updated_user = sample_user.copy()
        updated_user["is_active"] = False
        response, data = await self._put("api/users/testuser", {"is_active": False}, admin_headers)

        assert response.status == status.HTTP_200_OK
        assert data["message"] == "User updated successfully"
        assert data["user"]["is_active"] is False

    async def test_delete_user_success(self, mock_user_service, admin_headers):
        mock_user_service.delete_user.return_value = 1

        with patch("app.api.deps.get_user_service", return_value=mock_user_service), \
                patch("app.utils.security.settings.ADMIN_API_KEY", "admin_test_key"):
            response, data = await self._delete("/api/v1/users/testuser", admin_headers)

        assert response.status == status.HTTP_200_OK
        assert data["message"] == "User 'testuser' deleted successfully"
        mock_user_service.delete_user.assert_called_once_with("testuser")
