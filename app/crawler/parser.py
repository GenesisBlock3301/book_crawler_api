from selectolax.parser import HTMLParser
from datetime import datetime
from urllib.parse import urljoin
from app.crawler.schemas import Book


def parse_book_page(html: str, url: str, category: str) -> Book:
    tree = HTMLParser(html)

    # Find Title
    name_node = tree.css_first("h1")
    name = name_node.text(strip=True) if name_node else None

    # Find Price
    price_incl = price_excl = None
    num_reviews = 0

    for row in tree.css("table.table tr"):
        th = row.css_first("th")
        td = row.css_first("td")
        if not (th and td):
            continue
        label = th.text(strip=True).lower()
        value = td.text(strip=True)
        if "price (incl. tax)" in label:
            price_incl = float(value.replace("£", ""))
        elif "price (excl. tax)" in label:
            price_excl = float(value.replace("£", ""))
        elif "number of reviews" in label:
            try:
                num_reviews = int(value)
            except ValueError:
                num_reviews = 0

    # ---- Availability ----
    avail_node = tree.css_first(".availability")
    availability = avail_node.text(strip=True) if avail_node else "Unknown"

    # ---- Rating ----
    rating_node = tree.css_first(".star-rating")
    rating = None
    if rating_node:
        classes = rating_node.attributes.get("class", "").split()
        if len(classes) > 1:
            rating = classes[1]  # e.g., "Three"

    # ---- Image ----
    img_node = tree.css_first("#product_gallery img")
    img_url = urljoin(url, img_node.attributes.get("src")) if img_node else None

    # ---- Description ----
    desc = None
    desc_header = tree.css_first("#product_description")
    if desc_header:
        # In this page, description <p> follows #product_description
        desc_p = desc_header.next
        while desc_p and desc_p.tag != "p":
            desc_p = desc_p.next
        if desc_p:
            desc = desc_p.text(strip=True)

    # ---- Construct Book ----
    return Book(
        name=name,
        description=desc,
        category=category,
        price_excl_tax=price_excl,
        price_incl_tax=price_incl,
        availability=availability,
        num_reviews=num_reviews,
        image_url=img_url,
        rating=rating,
        source_url=url,
        crawl_timestamp=datetime.now(),
    )
