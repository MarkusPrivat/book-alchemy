from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

from data.data_models import db, Author, Book


PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / "data/library.sqlite"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_PATH.as_posix()}"
db.init_app(app)


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
