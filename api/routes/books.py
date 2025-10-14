from fastapi import APIRouter, Depends, Query
from crawler.storage import books_col
from api.deps import verify_api_key
from fastapi_limiter.depends import RateLimiter

router = APIRouter(dependencies=[Depends(verify_api_key),
                                 Depends(RateLimiter(times=100, seconds=3600))])

@router.get("/")
async def get_books(category: str = None, min_price: float = 0, max_price: float = 9999, skip: int = 0, limit: int = 10):
    query = {"price_incl_tax": {"$gte": min_price, "$lte": max_price}}
    if category:
        query["category"] = category
    books = await books_col.find(query).skip(skip).limit(limit).to_list(length=limit)
    return books

@router.get("/{book_id}")
async def get_book(book_id: str):
    book = await books_col.find_one({"_id": book_id})
    return book
