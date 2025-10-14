import pytest
import aiohttp
from aioresponses import aioresponses
from unittest.mock import patch, AsyncMock
from urllib.parse import urljoin
from app.crawler.crawler import BookCrawler
from app.utils.config import settings

LIST_PAGE_HTML = """
<html>
    <body>
        <article class="product_pod">
            <h3><a href="catalogue/book_1.html">Book 1</a></h3>
        </article>
        <ul class="pager">
            <li class="next"><a href="page-2.html">next</a></li>
        </ul>
    </body>
</html>
"""

# Sample HTML for the book detail page
BOOK_PAGE_HTML = """
<html>
    <body>
        <h1>Book 1</h1>
        <table class="table">
            <tr><th>Price (excl. tax)</th><td>£10.00</td></tr>
            <tr><th>Price (incl. tax)</th><td>£12.00</td></tr>
            <tr><th>Number of reviews</th><td>5</td></tr>
        </table>
        <p class="instock availability">In stock</p>
        <p class="star-rating Three"></p>
        <div id="product_gallery">
            <img src="cover.jpg"/>
        </div>
        <div id="product_description">
            <h2>Product Description</h2>
        </div>
        <p>This is a test description</p>
    </body>
</html>
"""


@pytest.mark.asyncio
async def test_crawl_books_class_based():
    with aioresponses() as m:
        m.get(settings.BASE_URL, status=200, body=LIST_PAGE_HTML)
        m.get(urljoin(settings.BASE_URL, "catalogue/book_1.html"), status=200, body=BOOK_PAGE_HTML)
        m.get(urljoin(settings.BASE_URL, "page-2.html"), status=404)

        # mocking update_one method
        with patch("app.crawler.crawler.books_collection.update_one", new_callable=AsyncMock) as mock_update:
            async with aiohttp.ClientSession() as session:
                crawler = BookCrawler(session=session)
                await crawler.crawl()

            # DB should be called once
            assert mock_update.call_count == 1
            args, _ = mock_update.call_args
            filter_arg = args[0]
            assert filter_arg["name"] == "Book 1"
