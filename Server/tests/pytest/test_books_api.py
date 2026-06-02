import pytest
import json

# ----------------------------
# SECTION 1: Basic Functional
# ----------------------------

@pytest.mark.functional
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code in [200, 503]
    assert "status" in response.get_json()

@pytest.mark.functional
def test_get_books_empty(client, db_connection):
    conn, cursor = db_connection
    cursor.execute("DELETE FROM book")
    conn.commit()
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json() == []

# ----------------------------
# SECTION 2: Create Book API
# ----------------------------

@pytest.mark.create_api
def test_create_valid_book(client):
    payload = {
        "publisher": "O'Reilly",
        "name": "Flask101",
        "date": "2025-01-01",
        "cost": 49.99
    }
    response = client.post("/create", json=payload)
    data = response.get_json()
    assert response.status_code == 201
    assert data["name"] == "Flask101"

@pytest.mark.create_api
def test_create_missing_field(client):
    payload = {
        "name": "Flask101",
        "date": "2025-01-01",
        "cost": 49.99
    }
    response = client.post("/create", json=payload)
    assert response.status_code == 400
    assert "Missing field" in response.get_json()["error"]

@pytest.mark.create_api
def test_create_invalid_cost(client):
    payload = {
        "publisher": "Packt",
        "name": "Flask",
        "date": "2025-01-01",
        "cost": "abc"
    }
    response = client.post("/create", json=payload)
    assert response.status_code == 400
    assert "Invalid cost" in response.get_json()["error"]

@pytest.mark.create_api
def test_create_invalid_date(client):
    payload = {
        "publisher": "Packt",
        "name": "Flask",
        "date": "32-13-2025",
        "cost": 39.99
    }
    response = client.post("/create", json=payload)
    assert response.status_code == 400
    assert "Invalid date format" in response.get_json()["error"]

@pytest.mark.create_api
def test_create_empty_body(client):
    response = client.post("/create", data="")
    assert response.status_code == 400
    assert "Request must be JSON" in response.get_json()["error"]

# ----------------------------
# SECTION 3: Update Book API
# ----------------------------

@pytest.mark.update_api
def test_update_valid_book(client, create_sample_book):
    book_id = create_sample_book
    payload = {
        "publisher": "UpdatePub",
        "name": "UpdatedBook",
        "date": "2025-12-12",
        "cost": 60.0
    }
    response = client.put(f"/update/{book_id}", json=payload)
    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "UpdatedBook"

@pytest.mark.update_api
def test_update_nonexistent_book(client):
    payload = {
        "publisher": "X",
        "name": "Y",
        "date": "2025-01-01",
        "cost": 10
    }
    response = client.put("/update/99999", json=payload)
    assert response.status_code == 404
    assert "Book not found" in response.get_json()["error"]

# ----------------------------
# SECTION 4: Delete Book API
# ----------------------------

@pytest.mark.delete_api
def test_delete_existing_book(client, create_sample_book):
    book_id = create_sample_book
    response = client.delete(f"/delete/{book_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"]

@pytest.mark.delete_api
def test_delete_nonexistent_book(client):
    response = client.delete("/delete/99999")
    assert response.status_code == 404
    assert "Book not found" in response.get_json()["error"]

# ----------------------------
# SECTION 5: DB Failure (Simulated)
# ----------------------------

# These would require DB mock or stop DB service manually
@pytest.mark.db_failure
def test_db_connection_failure(client, monkeypatch):
    from app import get_db_connection
    def fake_conn():
        raise Exception("DB not reachable")
    monkeypatch.setattr("app.get_db_connection", fake_conn)
    response = client.get("/")
    assert response.status_code == 500 or response.status_code == 503

# ----------------------------
# SECTION 6: Global Error Handling
# ----------------------------

@pytest.mark.global_error
def test_404_not_found(client):
    response = client.get("/unknown")
    assert response.status_code == 404
    assert "Resource not found" in response.get_json()["error"]

@pytest.mark.global_error
def test_method_not_allowed(client):
    response = client.patch("/create")
    assert response.status_code == 405
