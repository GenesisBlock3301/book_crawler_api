from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter
from app.utils.config import settings
from app.api.routes import changes, books


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await aioredis.from_url(settings.REDIS_URL)
    await FastAPILimiter.init(redis)
    print("✅ Redis limiter initialized")

    # Yield control back to FastAPI
    yield

    # --- Shutdown section ---
    await redis.close()
    print("🛑 Redis connection closed")


app = FastAPI(title="Book Crawler API", lifespan=lifespan)

app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(changes.router, prefix="/changes", tags=["Changes"])
