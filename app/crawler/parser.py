from selectolax.parser import HTMLParser
from datetime import datetime
from urllib.parse import urljoin
from app.crawler.schemas import Book


class BookParser:
    def __init__(self, html: str, url: str, category: str):
        self.tree = HTMLParser(html)
        self.url = url
        self.category = category
    @staticmethod
    def parse_price(value: str) -> float | None:
        try:
            return float(value.replace("£", ""))
        except (ValueError, AttributeError):
            return None

    def parse_metadata(self) -> tuple[float | None, float | None, int]:
        price_incl = price_excl = None
        num_reviews = 0

        for row in self.tree.css("table.table tr"):
            th = row.css_first("th")
            td = row.css_first("td")
            if not (th and td):
                continue

            label = th.text(strip=True).lower()
            value = td.text(strip=True)

            if "price (incl. tax)" in label:
                price_incl = self.parse_price(value)
            elif "price (excl. tax)" in label:
                price_excl = self.parse_price(value)
            elif "number of reviews" in label:
                try:
                    num_reviews = int(value)
                except ValueError:
                    num_reviews = 0

        return price_incl, price_excl, num_reviews

    def parse_availability(self) -> str:
        node = self.tree.css_first(".availability")
        return node.text(strip=True) if node else "Unknown"

    def parse_rating(self) -> str | None:
        node = self.tree.css_first(".star-rating")
        if not node:
            return None
        classes = node.attributes.get("class", "").split()
        return classes[1] if len(classes) > 1 else None

    def parse_image(self) -> str | None:
        node = self.tree.css_first("#product_gallery img")
        return urljoin(self.url, node.attributes.get("src")) if node else None

    def parse_description(self) -> str | None:
        desc_header = self.tree.css_first("#product_description")
        if not desc_header:
            return None

        node = desc_header.next
        while node and node.tag != "p":
            node = node.next
        return node.text(strip=True) if node else None

    def parse_name(self) -> str | None:
        name_node = self.tree.css_first("h1")
        return name_node.text(strip=True) if name_node else None

    def parse_book(self) -> Book:
        name = self.parse_name()
        price_incl, price_excl, num_reviews = self.parse_metadata()
        availability = self.parse_availability()
        rating = self.parse_rating()
        image_url = self.parse_image()
        description = self.parse_description()

        return Book(
            name=name,
            description=description,
            category=self.category,
            price_excl_tax=price_excl,
            price_incl_tax=price_incl,
            availability=availability,
            num_reviews=num_reviews,
            image_url=image_url,
            rating=rating,
            source_url=self.url,
            crawl_timestamp=datetime.now(),
        )
