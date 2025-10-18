from typing import List, Optional
from bson import ObjectId, errors as bson_errors
from app.db import changes_collection
from app.utils import paginate, logger
from .cache import cache

class ChangeBookRepository:

    @staticmethod
    async def get_by_id(book_id: str) -> Optional[dict]:
        generate_cache_key = cache.generate_cache_key("change_book", book_id=book_id)
        cached_book = await cache.get(generate_cache_key)
        if cached_book:
            logger.info(f"Change book {book_id} found in cache")
            return cached_book
        try:
            obj_id = ObjectId(book_id)
        except bson_errors.InvalidId:
            return None
        change_book = await changes_collection.find_one({"_id": obj_id})
        if change_book:
            logger.info(f"generate cache key and store book id: {book_id}")
            await cache.set(generate_cache_key, change_book)
        return change_book

    @staticmethod
    async def find(
            query: dict,
            skip: int = 0,
            limit: int = 10,
            sort_field: str | None = None,
    ) -> List[dict]:
        key = cache.generate_cache_key(
            "change_books_list",
            query=query,
            skip=skip,
            limit=limit,
            sort_field=sort_field
        )
        cached = await cache.get(key)
        if cached:
            logger.info("Change book list found in cache")
            return cached

        books = await paginate(changes_collection, query, skip, limit, sort_field)
        if books:
            logger.info("generate cache key and store change book list")
            await cache.set(key, books)
        return books
