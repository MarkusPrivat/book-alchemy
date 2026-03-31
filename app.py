from pathlib import Path
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from data.data_models import db, Author, Book
from data.data_validation import add_book_validate_form_input


PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / "data/library.sqlite"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH.as_posix()}"
app.secret_key = "Loremipsum-Secret!"
db.init_app(app)


@app.route('/', methods=['GET'])
def home():
    """
    Renders the library home page with support for searching and sorting.

    Retrieves query parameters from the request URL to filter and sort the
    collection of books stored in the database.

    Args:
        q (str, optional): The search string to filter books by title (case-insensitive).
            Defaults to an empty string.
        sort (str, optional): The criteria to sort the books by ('title' or 'author').
            Defaults to 'title'.

    Returns:
        str: The rendered 'home.html' template containing the processed book list
             and the current sorting state.
    """
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')

    query = select(Book)

    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))
    if sort_by == 'author':
        query = query.join(Author).order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    books = db.session.execute(query).scalars().all()

    return render_template('home.html', books=books, sort_by=sort_by)



@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Handles the creation of a new author entry in the library database.

    Supports both GET to display the creation form and POST to process
    the submitted author data. Validates that the name and birthdate
    fields are provided and that dates are in the correct ISO format.

    Returns:
        str: The rendered 'add_author.html' template for GET requests.
        str, int: A success message and 200 status code for successful POSTs,
                  or an error message and 400 status code if validation fails.
    """
    if request.method == 'GET':
        return render_template('add_author.html')

    if request.method == 'POST':
        name_form = request.form.get('name', '').strip()
        birthdate_form = request.form.get('birthdate', '')
        date_of_death_form = request.form.get('date_of_death', '')

        if not name_form or not birthdate_form:
            flash("Name and birthdate are required!", "error")
            return redirect(url_for('add_author'))

        try:
            birth_date_obj = date.fromisoformat(birthdate_form)
            death_date_obj = None
            if date_of_death_form:
                death_date_obj = date.fromisoformat(date_of_death_form)

            author = Author(
                name=name_form,
                birth_date=birth_date_obj,
                date_of_death=death_date_obj
            )

            db.session.add(author)
            db.session.commit()

            flash(f"Author '{name_form}' successfully added!", "success")
            return redirect(url_for('home'))

        except IntegrityError:
            db.session.rollback()
            flash(f"Error: An author with the name '{name_form}' already exists.", "error")
            return redirect(url_for('add_author'))
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for('add_author'))


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Handles the creation of a new book record and its association with an author.

    On GET requests, it retrieves all authors from the database to populate
    the selection menu in the form. On POST requests, it processes form data,
    validates inputs using a helper function, ensures the referenced author
    exists, and saves the new book to the database.

    Returns:
        str: The rendered 'add_book.html' template with an author list for GET.
        str, int: A success message and 200 status code upon successful
                  creation, or error messages and 400/404 status codes
                  for validation or database failures.
    """
    if request.method == 'GET':
        authors = db.session.execute(select(Author).order_by(Author.name)).scalars().all()
        return render_template('add_book.html', authors=authors)

    if request.method == 'POST':
        author_id_form = request.form.get('author_id', '')
        title_form = request.form.get('title', '').strip()
        isbn_form = request.form.get('isbn', '').strip()
        publication_year_form = request.form.get('publication_year', '')

        errors = add_book_validate_form_input(
            author_id_form, title_form, isbn_form, publication_year_form)

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for('add_book'))

        if not db.session.get(Author, int(author_id_form)):
            flash("Selected author does not exist!", "error")
            return redirect(url_for('add_book'))

        book = Book(
            isbn=isbn_form,
            title=title_form,
            publication_year=int(publication_year_form),
            author_id=int(author_id_form)
        )
        db.session.add(book)
        db.session.commit()

        flash(f"Book '{title_form}' successfully added!", "success")
        return redirect(url_for('home'))


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Deletes a specific book from the database and performs cleanup of orphaned authors.

    Retrieves a book by its unique ID and deletes it. If the associated author
    has no remaining books in the library after this deletion, the author record
    is also removed from the database to maintain data integrity.

    Args:
        book_id (int): The unique identifier of the book to be deleted.

    Returns:
        Response: A redirect to the home page with a flash message indicating
                  the success of the operation.
    """
    book = db.session.get(Book, book_id)
    if book:
        author = book.author
        db.session.delete(book)
        db.session.commit()

        if len(author.books) == 0:
            db.session.delete(author)
            db.session.commit()

        flash(f'Das Buch "{book.title}" wurde gelöscht.', 'success')

    return redirect(url_for('home'))




def init_db():
    """
    Initializes the database by creating tables if they do not exist.

    Uses an SQLAlchemy inspector to verify the existence of the 'authors' table.
    If the table is missing, it triggers the creation of all defined
    database models via SQLAlchemy's create_all() method.

    Returns:
        None
    """
    with app.app_context():
        inspector = inspect(db.engine)

        if not inspector.has_table("authors"):
            print("Database tables not found. Creating tables...")
            db.create_all()
            print("Tables created successfully.")


if __name__ == "__main__":
    """
    Entry point of the application.

    Triggers the database initialization process to ensure all required 
    tables exist and then starts the Flask development server in debug mode.
    """
    init_db()
    app.run(host="0.0.0.0", port=5002, debug=True)
