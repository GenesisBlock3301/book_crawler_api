import asyncio
from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from fastapi_limiter.depends import RateLimiter
from app.utils import verify_user_api_key, BookSortEnum
from app.services import BookService
from app.api.deps import get_book_service


async def user_rate_limit_identifier(request: Request):
    await asyncio.sleep(0)
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key missing")
    return f"user:{api_key}"


books_router = APIRouter(dependencies=[Depends(verify_user_api_key),
                                       Depends(RateLimiter(times=100, seconds=3600,
                                                           identifier=user_rate_limit_identifier))])


@books_router.get("/")
async def get_books(
        service: BookService = Depends(get_book_service),
        category: str = None,
        min_price: float = 0,
        max_price: float = 9999,
        skip: int = 0,
        limit: int = 10,
        sort_by: BookSortEnum | None = Query(None, description="Sort by: rating, price, reviews")
):
    sort_field = sort_by.value if sort_by else None
    return await service.get_books(category, min_price, max_price, skip, limit, sort_field)


@books_router.get("/{book_id}")
async def get_book(book_id: str, service: BookService = Depends(get_book_service)):
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book
