from .book_router import books_router
from .change_book_router import changes_router
from .user_router import users_router
from .crawling_router import crawler_router
from .report_generate_router import report_router

__all__ = (
    'books_router',
    'changes_router',
    'users_router',
    'crawler_router',
    'report_router'
)
