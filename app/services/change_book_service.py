from app.db import ChangeBookRepository
from app.serializers import serialize_book


class ChangeBookService:

    def __init__(self, repo: ChangeBookRepository):
        self.repo = repo

    async def get_book_by_id(self, book_id: str) -> dict|None:
        book = await self.repo.get_by_id(book_id)
        if not book:
            return None
        return serialize_book(book)

    async def get_changes(
            self,
            category: str | None = None,
            min_price: float = 0,
            max_price: float = 9999,
            skip: int = 0,
            limit: int = 10,
            sort_field: str | None = None,
    ) -> list[dict]:
        query: dict = {"price_incl_tax": {"$gte": min_price, "$lte": max_price}}
        if category:
            query["category"] = category

        return await self.repo.find(query, skip, limit, sort_field)

