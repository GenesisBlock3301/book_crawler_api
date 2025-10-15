from datetime import datetime

import aiohttp
import asyncio
from app.crawler.parser import BookParser
from app.db import books_collection
from app.utils.config import settings
from app.utils.logger import logger
from selectolax.parser import HTMLParser
from urllib.parse import urljoin


class BookCrawler:
    def __init__(self, base_url=settings.BASE_URL, session=None, book_parser=None):
        self.base_url = base_url
        self.session = session
        self.logger = logger
        self.parser = book_parser

    async def fetch(self, url: str):
        for _ in range(3):
            try:
                async with self.session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.text()
            except Exception as e:
                self.logger.warning(f"Retry due to: {e}")
            await asyncio.sleep(2)
        self.logger.error(f"Failed to fetch {url}")
        return None

    @staticmethod
    async def get_last_page():
        state = await books_collection.find_one({"_id": "book_crawler"})
        return state.get("last_page") if state else None

    @staticmethod
    async def save_last_page(next_page):
        await books_collection.update_one(
            {"_id": "book_crawler"},
            {"$set": {"last_page": next_page, "last_updated": datetime.now()}},
            upsert=True,
        )

    async def crawl(self):
        next_page = self.get_last_page() or self.base_url
        while next_page:
            html = await self.fetch(next_page)
            if not html:
                break
            tree = HTMLParser(html)
            book_links = self._extract_book_links(tree)
            for url in book_links:
                await self._process_book(url)
            next_page = self._next_page(tree)

    def _extract_book_links(self, tree):
        links = []
        for node in tree.css("article.product_pod h3 a"):
            href = node.attributes.get("href", "")
            if "catalogue/" not in href:
                href = f"catalogue/{href.lstrip('./')}"
            links.append(urljoin(self.base_url, href))
        return links

    async def _process_book(self, url):
        exists = await books_collection.find_one({"url": url})
        if exists:
            self.logger.info(f"Skipping {url} as it already exists")
            return
        book_html = await self.fetch(url)
        if not book_html:
            self.logger.error(f"Failed to fetch {url}")
            return
        book_data = self.parser(book_html, url, "Unknown").parse_book()
        await books_collection.update_one(
            {"name": book_data.name},
            {"$set": book_data.model_dump(mode="json")},
            upsert=True,
        )
        self.logger.info(f"Saved {book_data.name}")

    def _next_page(self, tree):
        next_btn = tree.css_first(".next a")
        if not next_btn:
            return None
        href = next_btn.attributes.get("href", "")
        if 'catalogue/' not in href:
            href = f"catalogue/{next_btn.attributes.get('href').lstrip('./')}"
        return urljoin(self.base_url, href) if next_btn else None


async def main():
    async with aiohttp.ClientSession() as session:
        crawler = BookCrawler(session=session, book_parser=BookParser)
        await crawler.crawl()


if __name__ == "__main__":
    asyncio.run(main())
