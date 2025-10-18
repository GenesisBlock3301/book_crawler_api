from app.db.database import users_collection
from typing import TYPE_CHECKING
from .cache import cache
from app.utils import logger, paginate

if TYPE_CHECKING:
    from app.schemas import User

class UserRepository:
    def __init__(self, collection=users_collection):
        self.collection = collection

    async def get(self, username: str):
        key = cache.generate_cache_key("user", username=username)
        cached = await cache.get(key)
        if cached:
            logger.info("User found in cache")
            return cached
        user = await self.collection.find_one({"username": username})
        if user:
            logger.info(f"generate cache key and store user id: {user['_id']}")
            await cache.set(key, user)
        return user

    async def create(self, user: "User"):
        await self.collection.insert_one(user.model_dump(mode="json"))
        return user

    async def update(self, username: str, update_data: dict):
        await self.collection.update_one({"username": username}, {"$set": update_data})
        return await self.get(username)

    async def delete(self, username: str):
        result = await self.collection.delete_one({"username": username})
        logger.info(f"Deleted user: {username}")
        return result.deleted_count

    @staticmethod
    async def list(
            query=None,
            skip: int = 0,
            limit: int = 10,
            sort_field: str | None = None,
    ):
        if query is None:
            query = {}
        key = cache.generate_cache_key(
            "user_list",
            query=query | {'query': 'query'},
            skip=skip,
            limit=limit,
            sort_field=sort_field
        )
        cached = await cache.get(key)
        if cached:
            logger.info("User list found in cache")
            return cached
        users = await paginate(users_collection, query, skip, limit, sort_field)
        if users: await cache.set(key, users)
        return users