# JWT Login Integration Guide

This guide shows how to add JWT-based login to this project (Flask backend + React frontend). It includes step-by-step instructions and exact code to replace or add in the project files.

Overview
- Server: add `flask-jwt-extended` configuration, a `/login` POST route that returns a JWT, and protect create/update/delete endpoints with `@jwt_required()`.
- Client: add a `Login` page (route `/login`), store the token in `localStorage`, set Axios Authorization header, and show a logout button in `Nav`.

Prerequisites
- Python packages: install server requirements

```bash
pip install -r Server/requirements.txt
```

- Node packages (Client folder):

```bash
cd Client
npm install
npm run dev    # or npm start depending on your setup
```

Security note
- This guide uses a simple in-memory user store for demo. Replace with a secure user table (database) and proper password hashing in production.
- Keep `JWT_SECRET_KEY` secret; set it via environment variables in production.

---

**Server changes**

1) Install dependency: `flask-jwt-extended` is already included in `Server/requirements.txt`. If not, add it.

2) Replace `Server/app.py` with the following content (this preserves existing book CRUD behavior and adds JWT auth):

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
import tempfile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

app = Flask(__name__)
CORS(app)

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key-change-me')
jwt = JWTManager(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')

# Simple demo users (replace with DB-backed users in production)
# Passwords are hashed for demo purposes; to add a user use generate_password_hash('password')
users = {
    'Mayank': generate_password_hash('mayankpass'),
    'Yash': generate_password_hash('yashpass')
}


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


# Public route to fetch books (keeps current behavior)
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


# Protected endpoints: require valid JWT access token
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
        (new_book['publisher'], new_book['name'], new_book['date'], new_book['cost'])
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
@jwt_required()
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


@app.route('/health')
def health():
    return {"status": "healthy"}, 200


# Authentication route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    hashed = users.get(username)
    if not hashed or not check_password_hash(hashed, password):
        return jsonify({"error": "Bad credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
```

Notes about the server changes
- The `users` dict is just for demo; remove or replace with proper DB-backed users.
- Protected endpoints now require the header `Authorization: Bearer <access_token>`.

---

**Client changes**

Goal: when a user hits `/login` or `/` (we'll use `/login` page and redirect `/` to `/login` if not authenticated), show a login form. After successful login, the token is stored in `localStorage` and used for subsequent API calls.

1) Add a new file `Client/src/Login.jsx` with this content:

```jsx
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    axios.post('http://localhost:5001/login', { username, password })
      .then(res => {
        const token = res.data.access_token;
        localStorage.setItem('access_token', token);
        // set default axios header for subsequent requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        navigate('/');
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Login failed');
      });
  };

  return (
    <div className='d-flex align-items-center flex-column mt-3'>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className='w-25'>
        {error && <div className='alert alert-danger'>{error}</div>}
        <div className='mb-3'>
          <label className='form-label'>Username</label>
          <input className='form-control' value={username} onChange={e => setUsername(e.target.value)} />
        </div>
        <div className='mb-3'>
          <label className='form-label'>Password</label>
          <input type='password' className='form-control' value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button className='btn btn-primary' type='submit'>Login</button>
      </form>
    </div>
  );
};

export default Login;
```

2) Update `Client/src/App.jsx` to include the login route and apply token on load. Replace with the following content:

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Books from './Books';
import CreateBook from './CreateBook';
import UpdateBook from './UpdateBook';
import Nav from './Nav';
import Login from './Login';
import axios from 'axios';

function App() {
  // If there is a token stored, set the axios default header.
  const token = localStorage.getItem('access_token');
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  const isAuthenticated = !!token;

  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path='/login' element={<Login />} />
        <Route path='/' element={isAuthenticated ? <Books /> : <Navigate to='/login' />} />
        <Route path='/create' element={isAuthenticated ? <CreateBook /> : <Navigate to='/login' />} />
        <Route path='/update' element={isAuthenticated ? <UpdateBook /> : <Navigate to='/login' />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

3) Update `Client/src/Nav.jsx` to show a logout button when authenticated. Replace with:

```jsx
import React from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
import { useNavigate } from 'react-router-dom'

const Nav = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    delete window.axios?.defaults?.headers?.common?.Authorization; // optional
    navigate('/login');
    window.location.reload();
  }

  return (
    <div className='d-flex justify-content-between align-items-center px-3 py-2 shadow-sm'>
      <div className='fs-4 fw-bold'>Book Management System</div>
      <div>
        {token ? (
          <button className='btn btn-outline-secondary' onClick={handleLogout}>Logout</button>
        ) : (
          <button className='btn btn-primary' onClick={() => navigate('/login')}>Login</button>
        )}
      </div>
    </div>
  )
}

export default Nav
```

4) Minor updates to API calls (optional)
- The `axios.defaults.headers.common['Authorization']` is set after login and on page load in `App.jsx`, so `Books.jsx`, `CreateBook.jsx`, `UpdateBook.jsx` don't need header changes. If you prefer explicit headers, call:

```js
axios.get('http://localhost:5001', { headers: { Authorization: `Bearer ${token}` } })
```

---

**How it works (brief)**
- Client requests `POST /login` with `{username, password}`.
- Server validates credentials and returns `{ access_token }`.
- Client stores token in `localStorage` and sets Axios default Authorization header.
- Subsequent requests to protected endpoints include the header `Authorization: Bearer <token>` and the server validates the JWT.

**Testing**
1. Start the server

```bash
cd Server
python app.py
```

2. Start the client

```bash
cd Client
npm run dev
```

3. In the browser go to `http://localhost:5173/login` (or where Vite serves) and login with a demo user (alice/alicepass or bob/bobpass).
4. After login, you should be redirected to `/` and be able to create/update/delete books. If you attempt operations without a token you will get 401.

**Next steps / Production hardening**
- Replace the in-memory `users` dict with a user table in your database.
- Use HTTPS and a strong `JWT_SECRET_KEY` via environment variables.
- Add refresh tokens if you want long-lived sessions.
- Implement role-based access control if necessary.

---

## What should happen after successful login

Once the user logs in successfully:

- the app should redirect to the book list page.
- the page should display the list of books from the backend.
- the user should be able to perform create, read, update, and delete operations on books.

In this project, that means:

1. You log in at `/login`.
2. The client stores the JWT in `localStorage`.
3. Axios sends the JWT with protected requests.
4. The books listing page should render the books table.
5. The `CreateBook`, `UpdateBook`, and delete buttons should work without requiring a second login.

If the token is missing or invalid, the app should redirect back to `/login` and prevent the CRUD actions until authentication succeeds.

---

## Example code for successful login flow

The following code shows the exact client-side flow that ensures a successful login redirects the user to the book list page and keeps the JWT available for CRUD operations.

### Login handler (client-side)

```jsx
const handleSubmit = (e) => {
  e.preventDefault();
  setError('');

  axios.post('http://localhost:5001/login', { username, password })
    .then(res => {
      const token = res.data.access_token;
      localStorage.setItem('access_token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      navigate('/');
    })
    .catch(err => {
      setError(err.response?.data?.error || 'Login failed');
    });
};
```

### Redirect to book list after login

This route configuration sends authenticated users to the book list page and redirects unauthenticated visitors to `/login`.

```jsx
<BrowserRouter>
  <Nav />
  <Routes>
    <Route path='/login' element={<Login />} />
    <Route path='/' element={isAuthenticated ? <Books /> : <Navigate to='/login' />} />
    <Route path='/create' element={isAuthenticated ? <CreateBook /> : <Navigate to='/login' />} />
    <Route path='/update' element={isAuthenticated ? <UpdateBook /> : <Navigate to='/login' />} />
  </Routes>
</BrowserRouter>
```

### Book list page access after login

Once the token is stored and the app navigates to `/`, the `Books` component should load book data from the backend and show the list:

```jsx
useEffect(() => {
  axios.get('http://localhost:5001')
    .then(res => {
      setBooks(res.data);
    })
    .catch(err => console.log(err));
}, []);
```

### Protected create/update/delete

Because the token is stored in `axios.defaults.headers.common['Authorization']`, the following endpoints work after login:

- `POST http://localhost:5001/create`
- `PUT http://localhost:5001/update/:id`
- `DELETE http://localhost:5001/delete/:id`

These operations will succeed as long as the JWT is valid and present in the request headers.

---

If you want, I can apply these code changes directly to the repository (edit `Server/app.py`, add `Client/src/Login.jsx`, and replace `Client/src/App.jsx` and `Client/src/Nav.jsx`). Tell me to proceed and I will apply the patches and run quick checks.
