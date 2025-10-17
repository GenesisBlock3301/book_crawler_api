import secrets, asyncio
from datetime import datetime

from fastapi import Header, HTTPException, status, Request
from app.utils.config import settings
from app.db import users_collection


def verify_admin_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")


def generate_api_key():
    return secrets.token_hex(16)


async def verify_user_api_key(x_api_key: str = Header(...)):
    user = await users_collection.find_one({"api_key": x_api_key})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")

    await users_collection.update_one(
        {"api_key": x_api_key},
        {"$set": {"last_used": datetime.now()}},
        upsert=True,
    )
    return user


async def user_rate_limit_identifier(request: Request):
    await asyncio.sleep(0)
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key missing")
    return f"user:{api_key}"