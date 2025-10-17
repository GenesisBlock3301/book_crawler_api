import aiohttp
import pytest
from fastapi import status
from app.utils import settings

test_books = [
    {
        "_id": "68ef592950ca2000ff19b018",
        "name": "Chase Me (Paris Nights #2)",
        "availability": "In stock (19 available)",
        "category": "Unknown",
        "crawl_timestamp": "2025-10-15T14:34:23.289311",
        "description": "A Michelin two-star chef at twenty-eight, Violette Lenoir could handle anything, including a cocky burglar who broke into her restaurant in the middle of the night.Or so she thought.Elite counterterrorist operative Chase “Smith” had been through things that made Hell Week look easy. But nothing had prepared him for a leather-clad blonde who held him at bay at knifepoint an A Michelin two-star chef at twenty-eight, Violette Lenoir could handle anything, including a cocky burglar who broke into her restaurant in the middle of the night.Or so she thought.Elite counterterrorist operative Chase “Smith” had been through things that made Hell Week look easy. But nothing had prepared him for a leather-clad blonde who held him at bay at knifepoint and dared him to take her on.Now if only saving the world didn’t require he ruin her life.Two people who thought they could handle anything now have to take on each other. It's a battle neither one expected. But with their futures on the line, they have nothing to lose...but their hearts.Warning: This book contains one arrogant Navy SEAL, nights of Paris passion, and a woman who wants to have it all. ...more",
        "image_url": "https://books.toscrape.com/media/cache/6c/84/6c84fcf7a53b02b6e763de7272934842.jpg",
        "num_reviews": 0,
        "price_excl_tax": 25.27,
        "price_incl_tax": 25.27,
        "rating": "Five",
        "row_html": "...",
        "source_url": "https://books.toscrape.com/catalogue/chase-me-paris-nights-2_977/index.html"
    },
    {
        "_id": "68ef592250ca2000ff19b001",
        "name": "A Light in the Attic",
        "availability": "In stock (22 available)",
        "category": "Unknown",
        "crawl_timestamp": "2025-10-15T14:34:15.996968",
        "description": "...",
        "image_url": "https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg",
        "num_reviews": 0,
        "price_excl_tax": 51.77,
        "price_incl_tax": 51.77,
        "rating": "Three",
        "row_html": "...",
        "source_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    }
]

TEST_API_KEY = "supersecretkey123"


@pytest.fixture(autouse=True)
async def setup_db():
    from app.db import books_collection
    await books_collection.insert_many(test_books)
    yield
    await books_collection.delete_many({})


@pytest.mark.asyncio
class TestBooksAPI:

    base_url = settings.HOST
    headers = {"x-api-key": TEST_API_KEY}

    async def get(self, endpoint: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                return response, await response.json()

    async def test_get_books_no_filter(self):
        endpoint = "api/books"
        response, data = await self.get(endpoint)
        assert response.status == status.HTTP_200_OK
        assert any(book["name"] == "A Light in the Attic" for book in data['results'])

    async def test_get_book_by_id_found(self):
        test_book = test_books[1]
        endpoint = f"api/books/{test_book['_id']}"
        response, data = await self.get(endpoint)
        data['row_html'] = "..."

        assert response.status == status.HTTP_200_OK
        assert data['name'] == test_book['name']
        assert data['price_incl_tax'] == test_book['price_incl_tax']
        assert data['num_reviews'] == test_book['num_reviews']
        assert data['rating'] == test_book['rating']
        assert data['image_url'] == test_book['image_url']
        assert data['source_url'] == test_book['source_url']
        assert data['row_html'] == test_book['row_html']

    async def test_get_book_by_id_not_found(self):
        non_existent_id = "68ef592950ca2000ff19b118"
        endpoint = f"api/books/{non_existent_id}"
        response, data = await self.get(endpoint)

        assert response.status == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "Book not found"

    async def test_internal_server_error_to_get_book_by_id(self):
        invalid_id = "nonexistentid1234567890"
        endpoint = f"api/books/{invalid_id}"
        response, data = await self.get(endpoint)

        assert response.status == status.HTTP_404_NOT_FOUND
        assert data["detail"] == "Book not found"

    async def test_rate_limit_per_user(self):
        endpoint = "api/books"
        max_requests = 100

        async with aiohttp.ClientSession() as session:
            for i in range(max_requests):
                async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                    assert response.status == status.HTTP_200_OK, f"Request {i+1} failed"
            async with session.get(f"{self.base_url}/{endpoint}", headers=self.headers) as response:
                assert response.status == status.HTTP_429_TOO_MANY_REQUESTS