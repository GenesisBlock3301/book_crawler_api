from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class Book(BaseModel):
    name: str
    description: Optional[str]
    category: str
    price_excl_tax: float
    price_incl_tax: float
    availability: str
    num_reviews: int
    image_url: HttpUrl
    rating: str
    source_url: HttpUrl
    crawl_timestamp: datetime