from app.db.database import users_collection
from typing import TYPE_CHECKING
from .cache import cache

if TYPE_CHECKING:
    from app.schemas import User

class UserRepository:
    def __init__(self, collection=users_collection):
        self.collection = collection

    async def get(self, username: str):
        return await self.collection.find_one({"username": username})

    async def create(self, user: "User"):
        await self.collection.insert_one(user.model_dump(mode="json"))
        return user

    async def update(self, username: str, update_data: dict):
        await self.collection.update_one({"username": username}, {"$set": update_data})
        return await self.get(username)

    async def delete(self, username: str):
        result = await self.collection.delete_one({"username": username})
        return result.deleted_count

    @staticmethod
    async def list(
            query: dict,
            skip: int = 0,
            limit: int = 10,
            sort_field: str | None = None,
    ):
        key = cache.generate_cache_key(
            "user_list",
            query=query,
            skip=skip,
            limit=limit,
            sort_field=sort_field
        )
        cached = await cache.get(key)
        if cached: return cached
        users = await users_collection.find(query).skip(skip).limit(limit).sort(sort_field)
        if users: await cache.set(key, users)
        return users