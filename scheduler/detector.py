from crawler.storage import books_col, changes_col
from datetime import datetime
import hashlib

async def detect_changes():
    async for book in books_col.find({}):
        new_hash = hashlib.md5(str(book).encode()).hexdigest()
        if book.get("hash") != new_hash:
            await changes_col.insert_one({
                "book_id": book["_id"],
                "timestamp": datetime.utcnow(),
                "changes": "Detected modification",
            })
            await books_col.update_one(
                {"_id": book["_id"]},
                {"$set": {"hash": new_hash}}
            )
