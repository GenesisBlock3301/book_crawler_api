from datetime import datetime, timedelta, timezone
from typing import List
from app.db import changes_collection


async def get_books_by_date(target_date: datetime) -> List[dict]:
    start_time = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
    end_time = start_time + timedelta(days=1)

    cursor = changes_collection.find(
        {"timestamp": {"$gte": start_time, "$lt": end_time}},
        {"_id": 0}
    )
    return await cursor.to_list(length=None)
