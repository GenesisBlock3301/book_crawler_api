from fastapi import APIRouter, Query, Depends
from fastapi_limiter.depends import RateLimiter

from app.services import generate_report_service
from app.utils import user_rate_limit_identifier, verify_user_api_key

report_router = APIRouter(dependencies=[Depends(verify_user_api_key),
                                       Depends(RateLimiter(times=100, seconds=3600,
                                                           identifier=user_rate_limit_identifier))])


@report_router.get("/", summary="Generate daily change report (JSON or CSV)")
async def generate_change_report(
    format: str = Query("json", description="Output format: json or csv"),
    date: str = Query(None, description="Date (YYYY-MM-DD). Defaults to today (UTC).")
):
    return await generate_report_service(format, date)