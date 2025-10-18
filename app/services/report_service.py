from datetime import datetime, timezone
from io import StringIO
import csv
from bson import ObjectId
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import HTTPException
from app.db import get_books_by_date


def serialize_doc(doc: dict) -> dict:
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, dict):
            doc[key] = serialize_doc(value)
        elif isinstance(value, list):
            doc[key] = [serialize_doc(i) if isinstance(i, dict) else i for i in value]
    return doc

async def generate_report_service(format: str, date_str: str = None):
    try:
        if date_str:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            now = datetime.now(timezone.utc)
            target_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    changes = await get_books_by_date(target_date)

    changes = [serialize_doc(c) for c in changes]

    if not changes:
        raise HTTPException(status_code=404, detail="No changes found for this date.")
    if format.lower() == "json":
        return JSONResponse(content={
            "date": target_date.strftime("%Y-%m-%d"),
            "total": len(changes),
            "results": changes
        })

    # Return CSV response
    elif format.lower() == "csv":
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=list(changes[0].keys()))
        writer.writeheader()
        writer.writerows(changes)
        output.seek(0)
        filename = f"book_changes_{target_date.strftime('%Y_%m_%d')}.csv"

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid format. Choose 'json' or 'csv'.")
