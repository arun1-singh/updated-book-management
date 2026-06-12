import pytest
import sys
import os
from flask_jwt_extended import create_access_token

# Make sure 'app' is importable from Server/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import app as flask_app, get_db_connection


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    yield flask_app


@pytest.fixture(scope="session")
def client(app):
    """
    Flask test client pre-loaded with a valid JWT so every request is
    authenticated without going through the /login route.
    """
    test_client = app.test_client()
    with flask_app.app_context():
        token = create_access_token(identity="test-user")
    test_client.environ_base['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    return test_client


@pytest.fixture(scope="session")
def auth_token(client):
    """
    Registers pytest_user (ignores 409 if already exists) and returns a
    fresh JWT for use in tests that need a real DB-backed identity.
    """
    client.post("/signup", json={"username": "pytest_user", "password": "pytest_pass"})
    resp = client.post("/login", json={"username": "pytest_user", "password": "pytest_pass"})
    return resp.get_json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# ---------------------------------------------------------------------------
# Function-scoped DB fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_connection():
    """
    Yields (conn, cursor) against the real MSSQL database.
    Rolls back any changes after each test to keep the DB clean.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    yield conn, cursor
    conn.rollback()
    cursor.close()
    conn.close()


@pytest.fixture(scope="function")
def create_sample_book(db_connection):
    """
    Inserts a sample book before the test, yields its id, then deletes it
    regardless of test outcome.
    """
    conn, cursor = db_connection
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?)",
        ("TestPub", "TestBook", "2025-01-01", 50.0)
    )
    conn.commit()

    cursor.execute("SELECT @@IDENTITY AS id")
    book_id = int(cursor.fetchone()[0])

    yield book_id

    cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
    conn.commit()
