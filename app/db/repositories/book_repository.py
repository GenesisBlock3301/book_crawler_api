from typing import List, Optional
from bson import ObjectId, errors as bson_errors
from app.db import books_collection
from app.utils import paginate
from .cache import cache

class BookRepository:

    @staticmethod
    async def get_by_id(book_id: str) -> Optional[dict]:
        generate_cache_key = cache.generate_cache_key("book", book_id=book_id)
        cached_book = await cache.get(generate_cache_key)
        if cached_book: return cached_book
        try:
            obj_id = ObjectId(book_id)
        except bson_errors.InvalidId:
            return None
        book = await books_collection.find_one({"_id": obj_id})
        if book: await cache.set(generate_cache_key, book)
        return book

    @staticmethod
    async def find(
            query: dict,
            skip: int = 0,
            limit: int = 10,
            sort_field: str | None = None,
    ) -> List[dict]:
        key = cache.generate_cache_key(
            "books_list",
            query=query,
            skip=skip,
            limit=limit,
            sort_field=sort_field
        )
        cached = await cache.get(key)
        if cached: return cached
        books = await paginate(books_collection, query, skip, limit, sort_field)
        if books: await cache.set(key, books)
        return books
