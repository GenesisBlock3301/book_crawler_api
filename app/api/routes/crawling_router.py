from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_limiter.depends import RateLimiter
from app.crawler import main

from app.utils import user_rate_limit_identifier, logger, verify_admin_api_key

crawler_router = APIRouter(dependencies=[Depends(verify_admin_api_key),
                                       Depends(RateLimiter(times=100, seconds=3600,
                                                           identifier=user_rate_limit_identifier))])

@crawler_router.post("/")
async def get_crawling_status(background_tasks: BackgroundTasks):
    logger.info("Crawling status requested")
    background_tasks.add_task(main)
    return {"message": "Crawling started in background"}
