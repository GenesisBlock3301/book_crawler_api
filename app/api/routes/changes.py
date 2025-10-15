from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.db import changes_collection
from app.api.deps import verify_api_key
from app.utils import paginate, BookSortEnum

changes_router = APIRouter(dependencies=[Depends(verify_api_key), Depends(RateLimiter(times=100, seconds=3600))])

@changes_router.get("/")
async def get_changes(
        category: str = "",
        min_price: float = 0,
        max_price: float = 9999,
        skip: int = 0,
        limit: int = 10,
        sort_by: BookSortEnum | None = Query(None, description="Sort by: rating, price, reviews")
):
    query: dict = {"price_incl_tax": {"$gte": min_price, "$lte": max_price}}
    if category:
        query["category"] = category
    sort_field = sort_by.value if sort_by else None
    return await paginate(changes_collection, query, skip, limit, sort_field)
