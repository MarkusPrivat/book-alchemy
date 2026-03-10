from pathlib import Path
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from data.data_models import db, Author, Book
from data.data_validation import add_book_validate_form_input


PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / "data/library.sqlite"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH.as_posix()}"
db.init_app(app)


@app.route('/', methods=['GET'])
def home():
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
    if request.method == 'GET':
        return render_template('add_author.html')
    if request.method == 'POST':
        name_form = request.form.get('name', '').strip()
        birthdate_form = request.form.get('birthdate', '')
        date_of_death_form = request.form.get('date_of_death', '')

        if not name_form:
            return "Name cannot be empty!", 400
        if not birthdate_form:
            return "Author must have a birthdate!", 400

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

            return f"Author {name_form} successfully added!", 200

        except ValueError:
            return "Invalid date format received. Please use YYYY-MM-DD.", 400


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        authors = db.session.execute(select(Author).order_by(Author.name)).scalars().all()
        return render_template('add_book.html', authors=authors)

    if request.method == 'POST':
        author_id_form = request.form.get('author_id', '')
        title_form = request.form.get('title').strip()
        isbn_form = request.form.get('isbn', '').strip()
        publication_year_form =  request.form.get('publication_year', '')

        errors = add_book_validate_form_input(
            author_id_form,
            title_form,
            isbn_form,
            publication_year_form)

        if errors:
            return "<br>".join(errors), 400
        if not db.session.get(Author, int(author_id_form)):
            return "Selected author does not exist!", 404

        book = Book(
            isbn=isbn_form,
            title=title_form,
            publication_year=int(publication_year_form),
            author_id=int(author_id_form)
        )
        db.session.add(book)
        db.session.commit()
        return f"Book '{title_form}' successfully added!", 200






def init_db():
    """
    Checks if the required tables exist.
    If not, it creates all defined models.
    """
    with app.app_context():
        inspector = inspect(db.engine)

        if not inspector.has_table("authors"):
            print("Database tables not found. Creating tables...")
            db.create_all()
            print("Tables created successfully.")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
