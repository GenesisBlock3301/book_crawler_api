from math import ceil
from app.serializers import serialize_book


async def paginate(collection, query: dict, skip: int = 0, limit: int = 10):
    total = await collection.count_documents(query)
    items = await collection.find(query).skip(skip).limit(limit).to_list(length=limit)
    items = [serialize_book(book) for book in items]

    total_pages = ceil(total / limit) if total else 0
    page = (skip // limit) + 1 if total else 1

    # Ensure skip/page do not exceed total items
    if skip >= total:
        items = []
        page = total_pages if total_pages > 0 else 1
        skip = min(skip, max(total - 1, 0))

    next_skip = skip + limit if skip + limit < total else None
    prev_skip = skip - limit if skip - limit >= 0 else None

    return {
        "total": total,
        "limit": limit,
        "skip": skip,
        "page": page,
        "total_pages": total_pages,
        "results": items,
        "next": next_skip,
        "previous": prev_skip
    }
