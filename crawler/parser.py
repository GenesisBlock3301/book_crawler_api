from bs4 import BeautifulSoup
from crawler.schemas import Book
from datetime import datetime
from urllib.parse import urljoin
import re

def parse_book_page(html: str, url: str, category: str) -> Book:
    soup = BeautifulSoup(html, "html.parser")
    name = soup.find("h1").text.strip()
    price_incl = float(soup.select_one("th:contains('price (incl. tax)') + td").text.strip('£'))
    price_excl = float(soup.select_one("th:contains('price (excl. tax)') + td").text.strip('£'))
    availability = soup.select_one(".availability").text.strip()
    rating = soup.select_one(".star-rating")["class"][1]
    num_reviews = int(soup.select_one("th:contains('Number of reviews') + td").text)
    img_url = urljoin(url, soup.find("img")["src"])
    desc = soup.select_one("#product_description + p")
    desc_text = desc.text if desc else None

    return Book(
        name=name,
        description=desc_text,
        category=category,
        price_excl_tax=price_excl,
        price_incl_tax=price_incl,
        availability=availability,
        num_reviews=num_reviews,
        image_url=img_url,
        rating=rating,
        source_url=url,
        crawl_timestamp=datetime.utcnow()
    )
