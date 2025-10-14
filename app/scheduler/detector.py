from app.db import books_collection, changes_collection
from datetime import datetime
import hashlib

async def detect_changes():
    async for book in books_collection.find({}):
        new_hash = hashlib.md5(str(book).encode()).hexdigest()
        if book.get("hash") != new_hash:
            await changes_collection.insert_one({
                "book_id": book["_id"],
                "timestamp": datetime.now(),
                "changes": "Detected modification",
            })
            await books_collection.update_one(
                {"_id": book["_id"]},
                {"$set": {"hash": new_hash}}
            )
