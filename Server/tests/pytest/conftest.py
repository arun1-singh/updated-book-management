import pytest
import psycopg2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app, get_db_connection

@pytest.fixture(scope="session")
def app():
    # Provide the Flask app for testing
    yield flask_app

@pytest.fixture(scope="session")
def client(app):
    # Flask test client
    return app.test_client()

@pytest.fixture(scope="function")
def db_connection():
    """
    Provides a DB connection for tests. Rollback any changes after each test.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    yield conn, cursor
    conn.rollback()
    cursor.close()
    conn.close()

# @pytest.fixture(scope="function")
# def create_sample_book(db_connection):
#     """
#     Fixture to create a sample book for testing update/delete/fetch.
#     Returns the inserted book id.
#     """
#     conn, cursor = db_connection
#     cursor.execute(
#         "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?) RETURNING id",
#         ("TestPub", "TestBook", "2025-01-01", 50.0)
#     )
#     book_id = cursor.fetchone()[0]
#     conn.commit()
#     yield book_id
#     cursor.execute("DELETE FROM book WHERE id=%s", (book_id,))
#     conn.commit()

@pytest.fixture(scope="function")
def create_sample_book(db_connection):
    """
    Fixture to create a sample book for testing update/delete/fetch.
    Returns the inserted book id.
    """
    conn, cursor = db_connection

    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?) RETURNING id",
        ("TestPub", "TestBook", "2025-01-01", 50.0)
    )

    book_id = cursor.fetchone()[0]
    conn.commit()

    yield book_id

    cursor.execute(
        "DELETE FROM book WHERE id = ?",
        (book_id,)
    )
    conn.commit()
