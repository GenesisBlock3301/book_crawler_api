from fastapi import APIRouter, Query, Depends
from app.services import generate_report_service
from app.utils import verify_admin_api_key

report_router = APIRouter(dependencies=[Depends(verify_admin_api_key)])


@report_router.get("/", summary="Generate daily change report (JSON or CSV)")
async def generate_change_report(
    format: str = Query("json", description="Output format: json or csv"),
    date: str = Query(None, description="Date (YYYY-MM-DD). Defaults to today (UTC).")
):
    return await generate_report_service(format, date)