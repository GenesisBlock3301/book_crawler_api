from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import settings


client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]
book_sol = db.books
changes_col = db.changes