from datetime import date
from typing import Optional, List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Integer, ForeignKey, CheckConstraint

db = SQLAlchemy()


class Author(db.Model):
    """
    Represents an author in the database.
    """
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_death: Mapped[Optional[date]] = mapped_column(Date)

    # relationship to the books table
    books: Mapped[List["Book"]] = relationship(
        "Book",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        Technical string representation for developers.
        Useful for debugging in the Python shell or logs.
        """
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:
        """
        User-friendly string representation.
        Used when printing the object or displaying it in a UI/Template.
        """
        return f"Author: '{self.name}' (born '{self.birth_date}')"


class Book(db.Model):
    """
    Represents a book in the database
    """
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    publication_year: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint('publication_year >= 0 AND publication_year <= 2100'),
        nullable=False
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)

    # relationship to the authors table
    author: Mapped["Author"] = relationship(
        "Author",
        back_populates="books"
    )

    def __repr__(self) -> str:
        """
        Technical string representation for developers.
        Useful for debugging in the Python shell or logs.
        """
        return f"<Book(id={self.id}, title='{self.title}', author_id={self.author_id})>"

    def __str__(self) -> str:
        """
        User-friendly string representation.
        Used when printing the object or displaying it in a UI/Template.
        """
        return f"Book: '{self.title}' (Publication Year: {self.publication_year})"
