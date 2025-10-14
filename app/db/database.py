from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import settings


client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]
books_collection = db.books
changes_collection = db.changes