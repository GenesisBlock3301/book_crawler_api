from fastapi import Depends
from app.db.repositories.book_repository import BookRepository
from app.services import BookService

def get_book_repository() -> BookRepository:
    return BookRepository()

def get_book_service(repo: BookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(repo)
