from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from app.utils.config import settings
from app.api.routes import books_router, changes_router


REDIS_INIT_MESSAGE = "Redis limiter initialized..."
REDIS_CLOSE_MESSAGE = "Redis connection closed..."

async def initialize_redis():
    """Initialize Redis connection and rate limiter."""
    redis = aioredis.from_url(settings.REDIS_URL)
    await FastAPILimiter.init(redis)
    print(REDIS_INIT_MESSAGE)
    return redis


async def cleanup_redis(redis):
    """Close Redis connection and cleanup resources."""
    await redis.close()
    print(REDIS_CLOSE_MESSAGE)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await initialize_redis()
    yield
    await cleanup_redis(redis)


app = FastAPI(title="Book Crawler API", lifespan=lifespan)

app.include_router(books_router, prefix="/books", tags=["Books"])
app.include_router(changes_router, prefix="/changes", tags=["Changes"])
