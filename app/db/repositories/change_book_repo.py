from typing import List, Optional
from bson import ObjectId, errors as bson_errors
from app.db import changes_collection
from app.utils import paginate


class ChangeBookRepository:

    @staticmethod
    async def get_by_id(book_id: str) -> Optional[dict]:
        try:
            obj_id = ObjectId(book_id)
        except bson_errors.InvalidId:
            return None
        return await changes_collection.find_one({"_id": obj_id})

    @staticmethod
    async def find(
            query: dict,
            skip: int = 0,
            limit: int = 10,
            sort_field: str | None = None,
    ) -> List[dict]:
        return await paginate(changes_collection, query, skip, limit, sort_field)
