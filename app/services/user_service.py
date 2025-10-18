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

    async def get_all_user(
            self,
            skip: int = 0,
            limit: int = 100,
            sort_by: str | None = None
    ) -> User:
        return await self.repo.list(skip=skip, limit=limit, sort_field=sort_by)

