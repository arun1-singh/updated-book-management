from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
import tempfile

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')

def get_db_path():
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return os.path.join(tempfile.gettempdir(), "simple_book_management_test_books.db")
    return os.environ.get("BOOKS_DB_PATH", DB_PATH)

def ensure_schema(connection):
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publisher TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            cost REAL NOT NULL
        )
    ''')
    connection.commit()
    cursor.close()

def get_db_connection():
    connection = sqlite3.connect(get_db_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    ensure_schema(connection)
    return connection

def init_db():
    connection = get_db_connection()
    connection.close()

def validate_book_payload(payload):
    if not request.is_json or payload is None:
        return "Request must be JSON"

    if "cost" not in payload and "Cost" in payload:
        payload["cost"] = payload["Cost"]

    required_fields = ("publisher", "name", "date", "cost")
    for field in required_fields:
        if field not in payload:
            return f"Missing field: {field}"
        if payload[field] in (None, ""):
            return f"Missing field: {field}"

    try:
        float(payload["cost"])
    except (TypeError, ValueError):
        return "Invalid cost"

    try:
        datetime.strptime(payload["date"], "%Y-%m-%d")
    except (TypeError, ValueError):
        return "Invalid date format"

    return None

@app.route('/', methods=['GET'])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, publisher, name, date, cost FROM book")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([
        {
            "id": row[0],
            "publisher": row[1],
            "name": row[2],
            "date": row[3],
            "cost": row[4],
        }
        for row in rows
    ])

@app.route('/create', methods=['POST'])
def create_books():
    new_book = request.get_json(silent=True)
    validation_error = validate_book_payload(new_book)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?)",
        (new_book['publisher'], new_book['name'], new_book['date'], new_book['cost'])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(new_book), 201

@app.route('/update/<int:id>', methods=['PUT'])
def update_book(id):
    updated_book = request.get_json(silent=True)
    validation_error = validate_book_payload(updated_book)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE book SET publisher=?, name=?, date=?, cost=? WHERE id=?",
        (updated_book['publisher'], updated_book['name'], updated_book['date'], updated_book['cost'], id)
    )
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({"error": "Book not found"}), 404

    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"data": updated_book})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_book(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book WHERE id=?", (id,))
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({"error": "Book not found"}), 404

    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'message': 'Book deleted successfully'})

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
