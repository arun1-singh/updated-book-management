from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pyodbc
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

app = Flask(__name__)
CORS(app)

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-me')
jwt = JWTManager(app)

# MSSQL connection configuration — set these via environment variables
MSSQL_SERVER   = os.environ.get('MSSQL_SERVER', 'localhost')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'books_db')
MSSQL_USERNAME = os.environ.get('MSSQL_USERNAME', 'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', 'YourStrong@Pass123')
MSSQL_DRIVER   = os.environ.get('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')

# For test environments, allow overriding the database name
def get_db_name():
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return os.environ.get("MSSQL_TEST_DATABASE", "books_db_test")
    return MSSQL_DATABASE

def get_connection_string():
    return (
        f"DRIVER={{{MSSQL_DRIVER}}};"
        f"SERVER={MSSQL_SERVER};"
        f"DATABASE={get_db_name()};"
        f"UID={MSSQL_USERNAME};"
        f"PWD={MSSQL_PASSWORD};"
        "TrustServerCertificate=yes;"
    )

def get_db_connection():
    connection = pyodbc.connect(get_connection_string())
    return connection

def ensure_schema(connection):
    cursor = connection.cursor()
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects WHERE name='book' AND xtype='U'
        )
        CREATE TABLE book (
            id        INT IDENTITY(1,1) PRIMARY KEY,
            publisher NVARCHAR(255) NOT NULL,
            name      NVARCHAR(255) NOT NULL,
            date      NVARCHAR(20)  NOT NULL,
            cost      FLOAT         NOT NULL
        )
    """)
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects WHERE name='users' AND xtype='U'
        )
        CREATE TABLE users (
            id            INT IDENTITY(1,1) PRIMARY KEY,
            username      NVARCHAR(150) UNIQUE NOT NULL,
            password_hash NVARCHAR(256) NOT NULL
        )
    """)
    connection.commit()
    cursor.close()

def init_db():
    connection = get_db_connection()
    ensure_schema(connection)
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


# ──────────────────────────────────────────────
# Auth endpoints
# ──────────────────────────────────────────────

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        return jsonify({"error": "Username already exists"}), 409

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    connection.commit()

    # Retrieve the new user's ID
    cursor.execute("SELECT @@IDENTITY AS id")
    user_id = int(cursor.fetchone()[0])

    cursor.close()
    connection.close()

    return jsonify({"message": "User created successfully", "user_id": user_id}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return jsonify({"error": "Bad credentials"}), 401

    if not check_password_hash(user[1], password):
        return jsonify({"error": "Bad credentials"}), 401

    access_token = create_access_token(identity=str(user[0]))
    return jsonify({"access_token": access_token}), 200


# ──────────────────────────────────────────────
# Book endpoints
# ──────────────────────────────────────────────

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
            "id":        row[0],
            "publisher": row[1],
            "name":      row[2],
            "date":      row[3],
            "cost":      row[4],
        }
        for row in rows
    ])


@app.route('/create', methods=['POST'])
@jwt_required()
def create_books():
    new_book = request.get_json(silent=True)
    validation_error = validate_book_payload(new_book)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?)",
        (new_book['publisher'], new_book['name'], new_book['date'], float(new_book['cost']))
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(new_book), 201


@app.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    updated_book = request.get_json(silent=True)
    validation_error = validate_book_payload(updated_book)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE book SET publisher=?, name=?, date=?, cost=? WHERE id=?",
        (updated_book['publisher'], updated_book['name'], updated_book['date'],
         float(updated_book['cost']), id)
    )
    rows_affected = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({"data": updated_book})


@app.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book WHERE id=?", (id,))
    rows_affected = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    if rows_affected == 0:
        return jsonify({"error": "Book not found"}), 404

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