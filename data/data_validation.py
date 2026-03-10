from sqlalchemy import select

from data.data_models import db, Author, Book


def add_book_validate_form_input(
        author_id: str,
        title: str,
        isbn: str,
        publication_year: str) -> list:
    errors = []
    if not author_id:
        errors.append("Author must be selected!")
    if not title:
        errors.append("Title cannot be empty!")
    if not isbn:
        errors.append("ISBN cannot be empty!")
    if not publication_year:
        errors.append("Publication Year cannot be empty!")
    if author_id and not author_id.isdigit():
        errors.append("Invalid format for author ID")
    if publication_year and not publication_year.isdigit():
        errors.append("Invalid format for publication year.")
    if isbn:
        existing_book = db.session.execute(select(Book).filter_by(isbn=isbn)).scalar_one_or_none()
        if existing_book:
            errors.append("This ISBN already exists in the database!")
    return errors
