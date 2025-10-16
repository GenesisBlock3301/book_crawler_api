from app.db import UserRepository
from app.schemas import User, UserUpdate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_by_username(self, username: str) -> User:
        return await self.repo.get(username)

    async def create_user(self, user: User) -> UserUpdate:
        return await self.repo.create(user)

    async def update_user(self, username: str, update_data: dict) -> UserUpdate:
        return await self.repo.update(username, update_data)

    async def delete_user(self, username: str) -> int:
        return await self.repo.delete(username)

