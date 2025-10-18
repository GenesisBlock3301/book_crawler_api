from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from app.api.routes import books_router, changes_router, users_router, crawler_router
from app.db import init_db
from app.utils import logger
from app.config import RedisCache


REDIS_INIT_MESSAGE = "Redis limiter initialized..."
REDIS_CLOSE_MESSAGE = "Redis connection closed..."

async def initialize_redis():
    """Initialize Redis connection and rate limiter."""
    redis = await RedisCache().get_client()
    await FastAPILimiter.init(redis)
    logger.info(REDIS_INIT_MESSAGE)
    return redis


async def cleanup_redis(redis_client: aioredis.Redis):
    """Close Redis connection and cleanup resources."""
    if redis_client:
        await redis_client.close()
        logger.info(REDIS_CLOSE_MESSAGE)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    redis = await RedisCache().get_client()
    yield
    await cleanup_redis(redis)


app = FastAPI(title="Book Crawler API", lifespan=lifespan)

app.include_router(books_router, prefix="/api/books", tags=["Books"])
app.include_router(changes_router, prefix="/api/changes", tags=["Changes"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(crawler_router, prefix="/api/crawler", tags=["Crawler"])
