from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from api.routes import books, changes
from utils.config import settings

app = FastAPI(title="Book Crawler API")

@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url(settings.REDIS_URL)
    await FastAPILimiter.init(redis)

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(changes.router, prefix="/changes", tags=["Changes"])
