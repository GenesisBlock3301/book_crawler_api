from fastapi import APIRouter, Depends
from app.db import changes_collection
from app.api.deps import verify_api_key
from app.utils import paginate

changes_router = APIRouter(dependencies=[Depends(verify_api_key)])

@changes_router.get("/")
async def get_changes(page: int = 50, page_size: int = 50):
    skip = (page - 1) * page_size
    query = {}
    return await paginate(changes_collection, query, skip, limit=page_size)
