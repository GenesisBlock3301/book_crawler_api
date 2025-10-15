from math import ceil
from app.serializers import serialize_book


async def paginate(collection, query: dict, skip: int = 0, limit: int = 10, sort_field: str = None):
    total = await collection.count_documents(query)
    cursor = collection.find(query)
    if sort_field:
        # membership check with runtime O(1)
        sort_order = -1 if sort_field in {"rating", "num_reviews", "price_incl_tax"} else 1
        cursor = cursor.sort(sort_field, sort_order)

    items = await cursor.skip(skip).limit(limit).to_list(length=limit)
    items = [serialize_book(book) for book in items]

    total_pages = ceil(total / limit) if total else 0
    page = (skip // limit) + 1 if total else 1

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
