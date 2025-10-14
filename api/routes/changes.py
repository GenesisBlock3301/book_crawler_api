from fastapi import APIRouter, Depends
from crawler.storage import changes_col
from api.deps import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("/")
async def get_changes(limit: int = 50):
    return await changes_col.find().sort("timestamp", -1).limit(limit).to_list(length=limit)
