import aiohttp
import asyncio
from app.crawler.parser import parse_book_page
from app.db import books_collection
from app.utils.config import settings
from app.utils.logger import logger
from aiohttp import ClientSession
from selectolax.parser import HTMLParser
from urllib.parse import urljoin


async def fetch(session: ClientSession, url: str):
    """Fetch page with retry logic."""
    for _ in range(3):
        try:
            async with session.get(url, timeout=10) as resp:
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
            tree = HTMLParser(html)
            book_links = []
            for node in tree.css("article.product_pod h3 a"):
                href = node.attributes.get("href", "")
                if "catalogue/" not in href:
                    href = f"catalogue/{href.lstrip('./')}"
                book_links.append(urljoin(settings.BASE_URL, href))

            for book_url in book_links:
                book_html = await fetch(session, book_url)
                if not book_html:
                    continue

                book_data = parse_book_page(book_html, book_url, "Unknown")

                # create or update a book in db
                await books_collection.update_one(
                    {"name": book_data.name},
                    {"$set": book_data.model_dump(mode="json")},
                    upsert=True,
                )
                logger.info(f"Saved {book_data.name}")

            # select the next page
            next_btn = tree.css_first(".next a")
            next_page = (
                urljoin(next_page, next_btn.attributes.get("href"))
                if next_btn
                else None
            )


if __name__ == "__main__":
    asyncio.run(crawl_books())
