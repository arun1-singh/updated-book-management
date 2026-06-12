from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-me')
jwt = JWTManager(app)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_connection_string():
    return (
        f"DRIVER={{{os.environ.get('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
        f"SERVER={os.environ.get('MSSQL_SERVER', 'localhost')};"
        f"DATABASE={os.environ.get('MSSQL_DATABASE', 'books_db')};"
        f"UID={os.environ.get('MSSQL_USERNAME', 'sa')};"
        f"PWD={os.environ.get('MSSQL_PASSWORD', 'YourStrong@Passw0rd')};"
        "TrustServerCertificate=yes;"
    )


def get_db_connection():
    return pyodbc.connect(get_connection_string())


def init_db():
    """Create tables if they don't exist. Called once at startup."""
    conn = get_db_connection()
    cursor = conn.cursor()
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
            username      NVARCHAR(150) NOT NULL UNIQUE,
            password_hash NVARCHAR(256) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_book_payload(payload):
    if not request.is_json or payload is None:
        return "Request must be JSON"
    # Accept both 'cost' and 'Cost'
    if "cost" not in payload and "Cost" in payload:
        payload["cost"] = payload["Cost"]
    for field in ("publisher", "name", "date", "cost"):
        if field not in payload or payload[field] in (None, ""):
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


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Username already exists"}), 409

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    conn.commit()
    cursor.execute("SELECT @@IDENTITY AS id")
    user_id = int(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return jsonify({"message": "User created successfully", "user_id": user_id}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not check_password_hash(user[1], password):
        return jsonify({"error": "Bad credentials"}), 401

    access_token = create_access_token(identity=str(user[0]))
    return jsonify({"access_token": access_token}), 200


# ---------------------------------------------------------------------------
# Book routes
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, publisher, name, date, cost FROM book")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([
        {"id": r[0], "publisher": r[1], "name": r[2], "date": str(r[3]), "cost": r[4]}
        for r in rows
    ])


@app.route('/create', methods=['POST'])
@jwt_required()
def create_books():
    new_book = request.get_json(silent=True)
    err = validate_book_payload(new_book)
    if err:
        return jsonify({"error": err}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?)",
        (new_book['publisher'], new_book['name'], new_book['date'], float(new_book['cost']))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(new_book), 201


@app.route('/update/<int:id>', methods=['PUT'])
@jwt_required()
def update_book(id):
    updated_book = request.get_json(silent=True)
    err = validate_book_payload(updated_book)
    if err:
        return jsonify({"error": err}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE book SET publisher=?, name=?, date=?, cost=? WHERE id=?",
        (updated_book['publisher'], updated_book['name'],
         updated_book['date'], float(updated_book['cost']), id)
    )
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "Book not found"}), 404
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"data": updated_book})


@app.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_book(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM book WHERE id=?", (id,))
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        return jsonify({"error": "Book not found"}), 404
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book deleted successfully'})


# ---------------------------------------------------------------------------
# Health & error handlers
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True, port=5001)
