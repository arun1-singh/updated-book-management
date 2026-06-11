# 🗄️ Flask + MSSQL Migration Session Notes

> **Date:** June 11, 2026  
> **Topic:** Migrating a Flask Book Management API from SQLite → MSSQL, with SQLAlchemy ORM insights

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [SQLite → MSSQL Migration](#2-sqlite--mssql-migration)
3. [Environment Setup (.env)](#3-environment-setup-env)
4. [TrustServerCertificate Explained](#4-trustservercertificate-explained)
5. [SQLAlchemy ORM vs Raw pyodbc](#5-sqlalchemy-orm-vs-raw-pyodbc)
6. [Key Takeaways](#6-key-takeaways)

---

## 1. Project Overview

A Flask REST API for managing books, with JWT authentication and a React/Vite frontend.

### Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python · Flask · Flask-JWT-Extended |
| Database | SQLite → **MSSQL** (migrated this session) |
| DB Driver | `pyodbc` |
| Frontend | React · Vite |
| Auth | JWT (JSON Web Tokens) |
| Containerization | Docker / Docker Compose |

### API Endpoints

| Method | Route | Auth Required | Description |
|---|---|---|---|
| `POST` | `/signup` | ❌ | Register a new user |
| `POST` | `/login` | ❌ | Login, returns JWT token |
| `GET` | `/` | ❌ | Fetch all books |
| `POST` | `/create` | ✅ | Create a new book |
| `PUT` | `/update/<id>` | ✅ | Update a book |
| `DELETE` | `/delete/<id>` | ✅ | Delete a book |
| `GET` | `/health` | ❌ | Health check |

---

## 2. SQLite → MSSQL Migration

### What Changed

#### Dependency Swap
```diff
- import sqlite3          # stdlib, no install needed
+ import pyodbc           # pip install pyodbc
```

#### Connection Setup
```python
# Before — SQLite (file-based)
DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')
connection = sqlite3.connect(DB_PATH, timeout=10)
connection.row_factory = sqlite3.Row  # enables dict-style access

# After — MSSQL (server-based)
def get_connection_string():
    return (
        f"DRIVER={{{MSSQL_DRIVER}}};"
        f"SERVER={MSSQL_SERVER};"
        f"DATABASE={MSSQL_DATABASE};"
        f"UID={MSSQL_USERNAME};"
        f"PWD={MSSQL_PASSWORD};"
        "TrustServerCertificate=yes;"
    )
connection = pyodbc.connect(get_connection_string())
```

#### Schema — Column Type Mapping

| SQLite Type | MSSQL Type | Notes |
|---|---|---|
| `TEXT` | `NVARCHAR(255)` | Unicode support |
| `REAL` | `FLOAT` | Decimal numbers |
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `INT IDENTITY(1,1) PRIMARY KEY` | Auto-increment |

#### Schema — Conditional Table Creation
```sql
-- SQLite
CREATE TABLE IF NOT EXISTS book ( ... );

-- MSSQL equivalent
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='book' AND xtype='U')
CREATE TABLE book ( ... )
```

#### Getting Last Inserted ID
```python
# SQLite
user_id = cursor.lastrowid

# MSSQL
cursor.execute("SELECT @@IDENTITY AS id")
user_id = int(cursor.fetchone()[0])
```

#### Row Access
```python
# SQLite — dict-style (via row_factory)
row["publisher"]

# MSSQL pyodbc — positional index
row[1]   # publisher is the 2nd column
```

---

## 3. Environment Setup (.env)

### Folder Structure
```
Project/
├── Client/
│   ├── .env           ← Frontend config
│   └── src/
└── Server/
    ├── .env           ← Backend config  ← CREATE THIS
    └── app.py
```

### Server/.env
```env
# MSSQL Connection
MSSQL_SERVER=localhost
MSSQL_DATABASE=books_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_DRIVER=ODBC Driver 17 for SQL Server

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this

# SSL (dev vs prod)
MSSQL_TRUST_CERT=yes
```

### Client/.env
```env
VITE_API_BASE_URL=http://localhost:5001
```

### Loading .env in app.py
```python
# Add these TWO lines at the very top of app.py
from dotenv import load_dotenv
load_dotenv()
```

```bash
pip install python-dotenv
```

### .gitignore (both folders)
```gitignore
.env
.env.local
__pycache__/
*.db
```

### Setup Checklist

- [ ] ODBC Driver 17 installed on the machine
- [ ] MSSQL server running and accessible
- [ ] `Server/.env` file created with correct credentials
- [ ] `Client/.env` file created with API base URL
- [ ] Both `.env` files added to `.gitignore`
- [ ] `python-dotenv` installed: `pip install python-dotenv`
- [ ] `load_dotenv()` added at top of `app.py`

---

## 4. TrustServerCertificate Explained

### What It Does

When connecting to MSSQL, the server presents an **SSL/TLS certificate**. This setting controls whether your app verifies it.

```
TrustServerCertificate=yes  →  Skip verification — trust blindly
TrustServerCertificate=no   →  Verify the certificate (secure default)
```

### The Analogy
> Like an ID check at a door:
> - `yes` = Bouncer lets everyone in without checking ID
> - `no` = Bouncer carefully verifies the ID is genuine

### When to Use Each

| Environment | Setting | Reason |
|---|---|---|
| `localhost` dev | `yes` ✅ | No real cert needed |
| Internal server, self-signed cert | `yes` ⚠️ | Acceptable but know the risk |
| Production with real SSL cert | `no` ❌ | Always verify |
| Cloud DB (Azure SQL, AWS RDS) | `no` ❌ | They have valid certs |

### Security Risk of `yes`

With `yes`, you're vulnerable to a **Man-in-the-Middle (MITM) attack** — someone could intercept your DB connection and impersonate the MSSQL server, stealing credentials or data.

### Best Practice — Drive from .env

```python
# app.py
trust_cert = os.environ.get("MSSQL_TRUST_CERT", "no")
f"TrustServerCertificate={trust_cert};"
```

```env
# .env (dev)
MSSQL_TRUST_CERT=yes

# .env (production)
MSSQL_TRUST_CERT=no
```

---

## 5. SQLAlchemy ORM vs Raw pyodbc

### The Core Difference

#### Raw pyodbc — Manual everything, every route
```python
# You repeat this pattern in EVERY route
connection = get_db_connection()      # open
cursor = connection.cursor()          # create cursor
cursor.execute("SELECT * FROM book")  # raw SQL string
rows = cursor.fetchall()              # fetch manually
cursor.close()                        # close cursor
connection.close()                    # close connection
```

#### SQLAlchemy ORM — Abstracted, automated
```python
# Set up ONCE when app starts
engine = create_engine(connection_string)
SessionLocal = sessionmaker(bind=engine)

# In each route — just use a session
with SessionLocal() as session:       # auto open + auto close
    books = session.query(Book).all() # Python, not SQL
```

---

### Two Key Concepts SQLAlchemy Introduces

#### 1. Connection Pool (replaces manual `get_db_connection()`)

SQLAlchemy maintains a **pool of reusable connections** internally.

```
Without Pool (pyodbc):
  Request 1 → open connection → query → close connection
  Request 2 → open connection → query → close connection  ← wasteful

With Pool (SQLAlchemy):
  Request 1 → borrow from pool → query → return to pool
  Request 2 → borrow from pool → query → return to pool  ← efficient
```

#### 2. Session (replaces cursor)

A **Session** is your unit of work — it tracks all DB operations and commits them together.

```python
Session = sessionmaker(bind=engine)

with SessionLocal() as session:
    session.add(some_object)   # stage changes
    session.commit()           # apply all at once
    # session auto-closes here
```

---

### Side-by-Side Route Comparison

#### Create Book

```python
# ── Raw pyodbc ──────────────────────────────────────────
@app.route('/create', methods=['POST'])
@jwt_required()
def create_books():
    connection = get_db_connection()       # manual open
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO book (publisher, name, date, cost) VALUES (?, ?, ?, ?)",
        (new_book['publisher'], new_book['name'], new_book['date'], new_book['cost'])
    )
    connection.commit()
    cursor.close()                         # manual close
    connection.close()                     # manual close
    return jsonify(new_book), 201


# ── SQLAlchemy ORM ───────────────────────────────────────
@app.route('/create', methods=['POST'])
@jwt_required()
def create_books():
    with SessionLocal() as session:        # auto open + close
        book = Book(                       # no SQL — just Python object
            publisher=new_book['publisher'],
            name=new_book['name'],
            date=new_book['date'],
            cost=new_book['cost']
        )
        session.add(book)
        session.commit()
    return jsonify(new_book), 201
```

---

### Full Comparison Table

| Aspect | Raw pyodbc | SQLAlchemy ORM |
|---|---|---|
| Connection handling | Manual open/close every route | Pool managed automatically |
| Queries | Raw SQL strings | Python objects & methods |
| Cursor | You create and close it | Doesn't exist — session handles it |
| Tables | SQL `CREATE TABLE` | Python classes (Models) |
| Commit | Manual `connection.commit()` | `session.commit()` |
| Error/Rollback | You handle manually | Session auto-rolls back on error |
| Code per route | ~6 boilerplate lines | ~2 lines |
| Learning curve | Low | Moderate |
| Flexibility | Full SQL control | ORM abstraction (raw SQL still possible) |

### Mental Model

```
pyodbc:
  Route → open connection → write SQL → close connection
               ↑
      you manage everything

SQLAlchemy:
  Route → borrow session from pool → work with Python objects → return session
               ↑
      SQLAlchemy manages everything
```

---

## 6. Key Takeaways

### Migration Summary
- Replaced `sqlite3` with `pyodbc` for MSSQL connectivity
- Updated SQL syntax for MSSQL (IDENTITY, sysobjects, @@IDENTITY)
- All credentials moved to `.env` file loaded via `python-dotenv`

### Security Reminders
- `TrustServerCertificate=yes` is only safe for local development
- Always use `no` in production with a valid SSL certificate
- Never commit `.env` files to version control

### Next Steps (Optional Upgrade)
- [ ] Migrate from raw `pyodbc` to **SQLAlchemy ORM**
- [ ] Add `alembic` for database migrations
- [ ] Add request logging middleware
- [ ] Add rate limiting to auth endpoints

---

*Session conducted on June 11, 2026*
