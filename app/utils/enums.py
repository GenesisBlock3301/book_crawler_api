from enum import Enum


class BookSortEnum(str, Enum):
    rating = "rating"
    price = "price_incl_tax"
    reviews = "num_reviews"

class UserRoleEnum(str, Enum):
    admin = "admin"
    user = "user"