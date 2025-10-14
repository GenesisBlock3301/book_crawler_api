from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from app.utils.config import settings
from app.api.routes import books_router, changes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await aioredis.from_url(settings.REDIS_URL)
    await FastAPILimiter.init(redis)
    print("Redis limiter initialized...")

    # Yield control back to FastAPI
    yield

    # Connection cleanup
    await redis.close()
    print("Redis connection closed...")


app = FastAPI(title="Book Crawler API", lifespan=lifespan)

app.include_router(books_router, prefix="/books", tags=["Books"])
app.include_router(changes_router, prefix="/changes", tags=["Changes"])
