from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi_limiter.depends import RateLimiter

from app.services import ChangeBookService
from app.utils import BookSortEnum, user_rate_limit_identifier, verify_user_api_key
from app.api.deps import get_change_book_service
from app.serializers import serialize_book

changes_router = APIRouter(
    dependencies=[Depends(verify_user_api_key),
                  Depends(RateLimiter(times=100, seconds=3600, identifier=user_rate_limit_identifier))])


@changes_router.get("/")
async def get_changes(
        service: ChangeBookService = Depends(get_change_book_service),
        category: str = "",
        min_price: float = 0,
        max_price: float = 9999,
        skip: int = 0,
        limit: int = 10,
        sort_by: BookSortEnum | None = Query(None, description="Sort by: rating, price, reviews")
):
    sort_field = sort_by.value if sort_by else None
    return await service.get_changes(category, min_price, max_price, skip, limit, sort_field)


@changes_router.get("/{book_id}")
async def get_change(book_id: str, service: ChangeBookService = Depends(get_change_book_service)):
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return serialize_book(book)
