import math
import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch, MagicMock
from app.crawler.parser import BookParser
from app.crawler.crawler import BookCrawler
from app.db import books_collection


BOOK_HTML = """
<html>
  <h1>Test Book</h1>
  <table class="table">
    <tr><th>Price (incl. tax)</th><td>£20.0</td></tr>
    <tr><th>Price (excl. tax)</th><td>£18.0</td></tr>
    <tr><th>Number of reviews</th><td>5</td></tr>
  </table>
  <p class="availability">In stock</p>
  <div id="product_description" class="sub-header">
    <h2>Product Description</h2>
  </div>
  <p>Test description</p>
  <div id="product_gallery"><img src="image.jpg"></div>
  <p class="star-rating Three"></p>
</html>
"""

PAGE_HTML = """
<html>
  <article class="product_pod">
    <h3><a href="book_1.html">Book 1</a></h3>
  </article>
  <li class="next"><a href="page2.html">next</a></li>
</html>
"""


@pytest.mark.asyncio
async def test_book_parser():
    parser = BookParser(BOOK_HTML, url="http://test.com",)
    book = parser.parse_book()

    assert book.name == "Test Book"
    assert math.isclose(book.price_incl_tax, 20.0, rel_tol=1e-9)
    assert math.isclose(book.price_excl_tax, 18.0, rel_tol=1e-9)
    assert book.num_reviews == 5
    assert book.availability == "In stock"
    assert book.rating == "Three"
    assert book.description == "Test description"
    assert book.image_url == "http://test.com/image.jpg"


@pytest.mark.asyncio
async def test_crawler_fetch_and_process():
    mock_resp = AsyncMock()
    mock_resp.status = status.HTTP_200_OK
    mock_resp.text = AsyncMock(return_value=BOOK_HTML)

    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_resp))):
        with patch.object(books_collection, "find_one", AsyncMock(return_value=None)):
            with patch.object(books_collection, "update_one", AsyncMock()) as mock_update:
                crawler = BookCrawler(session=MagicMock(), book_parser=BookParser)
                html = await crawler.fetch("https://books.toscrape.com/catalogue/page-1.html")
                assert html is not None
                assert "Tipping the Velvet" in html

                await crawler._process_book("https://books.toscrape.com/catalogue/page-1.html")

                assert mock_update.called



@pytest.mark.asyncio
async def test_crawl_flow():
    def fake_fetch(url):
        if "book" in url:
            return BOOK_HTML
        return PAGE_HTML

    with patch.object(BookCrawler, "fetch", side_effect=fake_fetch):
        with patch.object(books_collection, "find_one", AsyncMock(return_value=None)):
            with patch.object(books_collection, "update_one", AsyncMock()):
                crawler = BookCrawler(session=MagicMock(), book_parser=BookParser)
                await crawler.crawl()
                assert books_collection.update_one.called
