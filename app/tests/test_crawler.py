import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.crawler.crawler import BookCrawler
from app.crawler.parser import BookParser


@pytest.fixture
def mock_session():
    """Mock aiohttp ClientSession"""
    session = MagicMock()
    return session


@pytest.fixture
def book_crawler(mock_session):
    """Create BookCrawler instance with mocked session"""
    return BookCrawler(
        base_url="http://books.toscrape.com",
        session=mock_session,
        book_parser=BookParser
    )


class TestBookCrawler:
    @pytest.mark.asyncio
    async def test_fetch_success(self, book_crawler, mock_session):
        """Test successful page fetch"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>Test HTML</html>")

        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await book_crawler.fetch("http://test.com")
        assert result == "<html>Test HTML</html>"

    @pytest.mark.asyncio
    async def test_fetch_failure(self, book_crawler, mock_session):
        """Test failed page fetch with retries"""
        mock_response = AsyncMock()
        mock_response.status = 500

        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        result = await book_crawler.fetch("http://test.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_page_exists(self, book_crawler):
        """Test getting the last crawled page when it exists"""
        with patch('app.crawler.crawler.books_collection') as mock_collection:
            mock_collection.find_one = AsyncMock(return_value={
                "_id": "book_crawler",
                "last_page": "http://test.com/page2"
            })

            result = await book_crawler.get_last_page()
            assert result == "http://test.com/page2"

    @pytest.mark.asyncio
    async def test_get_last_page_not_exists(self, book_crawler):
        with patch('app.crawler.crawler.books_collection') as mock_collection:
            mock_collection.find_one = AsyncMock(return_value=None)

            result = await book_crawler.get_last_page()
            assert result is None

    @pytest.mark.asyncio
    async def test_save_last_page(self, book_crawler):
        with patch('app.crawler.crawler.books_collection') as mock_collection:
            mock_collection.update_one = AsyncMock()

            await book_crawler.save_last_page("http://test.com/page3")
            mock_collection.update_one.assert_called_once()

    def test_extract_book_links(self, book_crawler):
        """Test extracting book links from HTML"""
        html = """
        <html>
            <article class="product_pod">
                <h3><a href="catalogue/book1.html">Book 1</a></h3>
            </article>
            <article class="product_pod">
                <h3><a href="catalogue/book2.html">Book 2</a></h3>
            </article>
        </html>
        """
        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)

        links = book_crawler._extract_book_links(tree)
        assert len(links) == 2
        assert "book1.html" in links[0]
        assert "book2.html" in links[1]

    @pytest.mark.asyncio
    async def test_process_book_already_exists(self, book_crawler):
        with patch('app.crawler.crawler.books_collection') as mock_collection:
            mock_collection.find_one = AsyncMock(return_value={"name": "Existing Book"})

            await book_crawler._process_book("http://test.com/book1")
            # Should not insert if already exists
            mock_collection.update_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_book_new(self, book_crawler, mock_session):
        book_html = "<html><h1>New Book</h1><p class='price_color'>£19.99</p></html>"

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=book_html)

        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch('app.crawler.crawler.books_collection') as mock_collection:
            mock_collection.find_one = AsyncMock(return_value=None)
            mock_collection.update_one = AsyncMock()

            with patch.object(book_crawler.parser, 'parse_book') as mock_parse:
                mock_parse.return_value = MagicMock(
                    name="New Book",
                    model_dump=MagicMock(return_value={"name": "New Book"})
                )

                await book_crawler._process_book("http://test.com/book1")
                mock_collection.update_one.assert_called_once()

    def test_next_page_exists(self, book_crawler):
        html = """
        <html>
            <li class="next"><a href="catalogue/page-2.html">next</a></li>
        </html>
        """
        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)

        next_page = book_crawler._next_page(tree)
        assert next_page is not None
        assert "page-2.html" in next_page

    def test_next_page_not_exists(self, book_crawler):
        html = "<html></html>"
        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)

        next_page = book_crawler._next_page(tree)
        assert next_page is None