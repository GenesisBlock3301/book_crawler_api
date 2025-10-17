from fastapi import Depends
from app.db import BookRepository, ChangeBookRepository, UserRepository
from app.services import BookService, ChangeBookService, UserService


def get_book_repository() -> BookRepository:
    return BookRepository()

def get_book_service(repo: BookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(repo)

def get_change_book_repository() -> ChangeBookRepository:
    return ChangeBookRepository()

def get_change_book_service(repo: ChangeBookRepository = Depends(get_change_book_repository)) -> ChangeBookService:
    return ChangeBookService(repo)


def get_user_repository() -> UserRepository:
    return UserRepository()

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)
