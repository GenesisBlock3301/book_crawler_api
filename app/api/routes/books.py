from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter
from bson import ObjectId

from app.db import books_collection
from app.api.deps import verify_api_key
from app.serializers import serialize_book
from app.utils import paginate

books_router = APIRouter(dependencies=[Depends(verify_api_key),
                                 Depends(RateLimiter(times=100, seconds=3600))])


@books_router.get("/")
async def get_books(
        category: str = None,
        min_price: float = 0,
        max_price: float = 9999,
        skip: int = 0,
        limit: int = 10):
    query = {"price_incl_tax": {"$gte": min_price, "$lte": max_price}}
    if category:
        query["category"] = category
    return await paginate(books_collection, query, skip, limit)


@books_router.get("/{book_id}")
async def get_book(book_id: str):
    book = await books_collection.find_one({"_id": ObjectId(book_id)})
    return serialize_book(book) if book else (
        {"error": "Book not found"}, status.HTTP_404_NOT_FOUND
    )
