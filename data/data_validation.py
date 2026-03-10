from sqlalchemy import select

from data.data_models import db, Author, Book


def add_book_validate_form_input(
        author_id: str,
        title: str,
        isbn: str,
        publication_year: str) -> list:
    """
    Validates form data for adding a new book to the library.

    Performs several checks: ensures required fields are present, verifies
    that numeric fields contain valid digits, and checks for potential
    duplicates (e.g., existing ISBN) within the database.

    Args:
        author_id (str): The ID of the selected author.
        title (str): The title of the book.
        isbn (str): The ISBN of the book.
        publication_year (str): The year of publication.

    Returns:
        list: A list of error messages (strings). If the list is empty,
              the input data is considered valid.
    """
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
