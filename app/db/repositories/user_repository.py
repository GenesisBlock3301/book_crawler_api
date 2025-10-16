from app.db.database import users_collection
from typing import TYPE_CHECKING

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
