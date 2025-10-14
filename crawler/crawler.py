import aiohttp
import asyncio
from crawler.parser import parse_book_page
from crawler.storage import books_col
from utils.config import settings
from utils.logger import logger
from datetime import datetime
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def fetch(session: ClientSession, url: str):
    for _ in range(3):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text()
        except Exception as e:
            logger.warning(f"Retry due to: {e}")
        await asyncio.sleep(2)
    logger.error(f"Failed to fetch {url}")
    return None

async def crawl_books():
    async with aiohttp.ClientSession() as session:
        next_page = settings.BASE_URL
        while next_page:
            html = await fetch(session, next_page)
            if not html:
                break
            soup = BeautifulSoup(html, "html.parser")
            books = soup.select(".product_pod h3 a")
            for book in books:
                book_url = urljoin(settings.BASE_URL, book["href"])
                book_html = await fetch(session, book_url)
                if not book_html:
                    continue
                book_data = parse_book_page(book_html, book_url, "Unknown")
                await books_col.update_one(
                    {"name": book_data.name},
                    {"$set": book_data.dict()},
                    upsert=True
                )
                logger.info(f"Saved {book_data.name}")
            next_btn = soup.select_one(".next a")
            next_page = urljoin(next_page, next_btn["href"]) if next_btn else None

if __name__ == "__main__":
    asyncio.run(crawl_books())
