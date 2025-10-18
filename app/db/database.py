import secrets
from datetime import datetime, date, timezone

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.utils import logger
from app.utils import UserRoleEnum


client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]
books_collection = db.books
changes_collection = db.change
users_collection = db.users


async def init_db():
    await users_collection.create_index("api_key", unique=True)
    await users_collection.create_index("username", unique=True)

    admin = await users_collection.find_one({"username": "admin"})

    if not admin:
        admin_api_key = settings.ADMIN_API_KEY or secrets.token_hex(16)
        user = {
            "username": "admin",
            "api_key": admin_api_key,
            "role": UserRoleEnum.admin.value,
            "rate_limit": 100,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": None,
            "last_used": None
        }
        await users_collection.insert_one(user)
        logger.info("[DB INIT] Created admin user.")
    else:
        logger.info("[DB INIT] Admin user already exists.")

    demo_change = await changes_collection.find_one({})
    if not demo_change:
        book = await books_collection.find_one({})
        if not book:
            book = {
                "name": "Demo Book",
                "availability": "In stock",
                "crawl_timestamp": datetime.now(),
                "hash": "demo_hash"
            }
            result = await books_collection.insert_one(book)
            book["_id"] = result.inserted_id

        await changes_collection.insert_one({
            "book_id": book["_id"],
            "timestamp": datetime.now(),
            "changes": "Demo modification detected"
        })
        logger.info("[DB INIT] Added demo change record to changes_collection.")
    else:
        logger.info("[DB INIT] changes_collection already has data.")