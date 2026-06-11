# Feature Implementation Guide: Adding 3 New Fields to Book Management System

**Date:** June 3, 2026  
**Objective:** Add Stock/Quantity, Category/Genre, and ISBN fields to the existing 4-field book management system  
**Current Fields:** Publisher, Name (Title), Date, Cost  
**New Fields:** ISBN, Category, Stock  

---

## Table of Contents

1. [High-Level Architecture Overview](#high-level-architecture-overview)
2. [Feature Scope & Requirements](#feature-scope--requirements)
3. [Database Layer Implementation](#database-layer-implementation)
4. [Backend API Implementation](#backend-api-implementation)
5. [Frontend UI Implementation](#frontend-ui-implementation)
6. [Testing Strategy](#testing-strategy)
7. [Migration & Deployment](#migration--deployment)
8. [Implementation Checklist](#implementation-checklist)

---

## High-Level Architecture Overview

### Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 5173)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Books.jsx  │  │ CreateBook   │  │  UpdateBook.jsx  │  │
│  │  (View List) │  │   .jsx       │  │  (Edit Form)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└────────────┬─────────────────────────────────────────────────┘
             │ HTTP Requests (Axios)
             │
┌────────────▼──────────────────────────────────────────────────┐
│              Flask Backend API (Port 5001)                    │
│  GET /              (Read all books)                          │
│  POST /create       (Create new book)                         │
│  PUT /update/<id>   (Update book)                             │
│  DELETE /delete/<id> (Delete book)                            │
└────────────┬──────────────────────────────────────────────────┘
             │ SQL Queries
             │
┌────────────▼──────────────────────────────────────────────────┐
│          SQLite Database (books.db)                           │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ TABLE: book                                          │    │
│  │ ├─ id (PK)                                          │    │
│  │ ├─ publisher, name, date, cost (Current)            │    │
│  │ ├─ isbn, category, stock (NEW)                      │    │
│  └──────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow with New Fields

**Creating a Book:**
```
User fills form → React validates → POST /create → Flask validates 
→ INSERT all 7 fields → SQLite returns → Response to frontend
```

**Fetching Books:**
```
User navigates to Books list → GET / → Flask queries all columns 
→ Returns JSON with 7 fields → React renders table with all fields
```

**Updating a Book:**
```
User clicks Update → Form pre-fills 7 fields → User edits → 
PUT /update/<id> → Flask validates & updates all fields → SQLite updates → Response
```

---

## Feature Scope & Requirements

### 1. ISBN Field

| Attribute | Details |
|-----------|---------|
| **Type** | TEXT (STRING) |
| **Constraints** | NOT NULL, UNIQUE |
| **Format** | ISBN-10 or ISBN-13 (13 digits with optional hyphens) |
| **Example** | `978-0-13-468599-1` or `9780134685991` |
| **Validation** | Must be numeric (after removing hyphens), length 10 or 13 |
| **UI Component** | Text input field |
| **Display** | Table column, form field |

**Why Important:**
- ISBN is a unique international identifier for books
- Prevents duplicate book entries
- Enables integration with book databases
- Essential for inventory management

---

### 2. Category Field

| Attribute | Details |
|-----------|---------|
| **Type** | TEXT (STRING) |
| **Constraints** | NOT NULL |
| **Format** | Pre-defined categories (dropdown) |
| **Options** | Fiction, Non-Fiction, Science, History, Technology, Biography, Mystery, Self-Help, Others |
| **Validation** | Must be from predefined list |
| **UI Component** | Dropdown select |
| **Display** | Table column, form field |

**Why Important:**
- Organizes books by genre/category
- Enables filtering and search capabilities
- Improves user experience
- Supports future reporting features

---

### 3. Stock Field

| Attribute | Details |
|-----------|---------|
| **Type** | INTEGER |
| **Constraints** | NOT NULL, DEFAULT 0, MIN 0 |
| **Format** | Whole numbers (0, 1, 2, ...) |
| **Example** | `5`, `10`, `0` |
| **Validation** | Non-negative integer |
| **UI Component** | Number input field |
| **Display** | Table column, form field |

**Why Important:**
- Tracks inventory levels
- Prevents overselling
- Enables stock alerts
- Supports future ordering workflows

---

## Database Layer Implementation

### Current Schema

```sql
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    cost REAL NOT NULL
);
```

### Updated Schema (With New Fields)

```sql
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    cost REAL NOT NULL,
    isbn TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);
```

### Migration Strategy

Since SQLite doesn't have built-in ALTER TABLE ADD COLUMN with UNIQUE constraint for new columns, we need a migration approach:

#### Option 1: Create New Table & Copy Data (RECOMMENDED)

```sql
-- Step 1: Create new table with updated schema
CREATE TABLE book_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    cost REAL NOT NULL,
    isbn TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0
);

-- Step 2: Copy existing data (with default values for new fields)
INSERT INTO book_new (id, publisher, name, date, cost, isbn, category, stock)
SELECT id, publisher, name, date, cost, 
       'UNKNOWN-' || id,  -- Placeholder ISBN
       'Others',           -- Default category
       0                   -- Default stock
FROM book;

-- Step 3: Drop old table
DROP TABLE book;

-- Step 4: Rename new table
ALTER TABLE book_new RENAME TO book;
```

#### Option 2: Add Columns Incrementally

```sql
-- This is a fallback if Option 1 isn't preferred
ALTER TABLE book ADD COLUMN isbn TEXT DEFAULT 'UNKNOWN';
ALTER TABLE book ADD COLUMN category TEXT DEFAULT 'Others';
ALTER TABLE book ADD COLUMN stock INTEGER DEFAULT 0;

-- Then update to add UNIQUE constraint on isbn requires recreation anyway
```

### Implementation Approach

**In `app.py` `ensure_schema()` function:**

```python
def ensure_schema(connection):
    cursor = connection.cursor()
    
    # Check if new columns exist
    cursor.execute("PRAGMA table_info(book)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Create table if it doesn't exist
    if not columns:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publisher TEXT NOT NULL,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                cost REAL NOT NULL,
                isbn TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        ''')
    
    # If old table exists without new columns, run migration
    elif 'isbn' not in columns:
        # Run migration logic here
        # This handles existing databases
        pass
    
    connection.commit()
    cursor.close()
```

---

## Backend API Implementation

### 1. Update Validation Function

**Current validation:**
```python
def validate_book_payload(payload):
    required_fields = ("publisher", "name", "date", "cost")
    for field in required_fields:
        if field not in payload or payload[field] in (None, ""):
            return f"Missing field: {field}"
    # ... more validation
```

**Updated validation (add this logic):**

```python
def validate_isbn(isbn_str):
    """Validate ISBN format (10 or 13 digits)"""
    # Remove hyphens
    clean_isbn = isbn_str.replace("-", "").replace(" ", "")
    
    # Must be all digits
    if not clean_isbn.isdigit():
        return "ISBN must contain only digits and hyphens"
    
    # Must be 10 or 13 characters
    if len(clean_isbn) not in (10, 13):
        return "ISBN must be 10 or 13 digits"
    
    return None

def validate_category(category):
    """Validate category is from allowed list"""
    valid_categories = [
        "Fiction", "Non-Fiction", "Science", "History", 
        "Technology", "Biography", "Mystery", "Self-Help", "Others"
    ]
    
    if category not in valid_categories:
        return f"Category must be one of: {', '.join(valid_categories)}"
    
    return None

def validate_stock(stock):
    """Validate stock is non-negative integer"""
    try:
        stock_int = int(stock)
        if stock_int < 0:
            return "Stock cannot be negative"
        return None
    except (TypeError, ValueError):
        return "Stock must be a valid integer"

def validate_book_payload(payload):
    if not request.is_json or payload is None:
        return "Request must be JSON"

    # Handle Cost/cost field mapping
    if "cost" not in payload and "Cost" in payload:
        payload["cost"] = payload["Cost"]

    # Updated required fields
    required_fields = ("publisher", "name", "date", "cost", "isbn", "category", "stock")
    for field in required_fields:
        if field not in payload:
            return f"Missing field: {field}"
        if payload[field] in (None, ""):
            return f"Missing field: {field}"

    # Existing validations
    try:
        float(payload["cost"])
    except (TypeError, ValueError):
        return "Invalid cost"

    try:
        datetime.strptime(payload["date"], "%Y-%m-%d")
    except (TypeError, ValueError):
        return "Invalid date format"

    # New field validations
    isbn_error = validate_isbn(payload["isbn"])
    if isbn_error:
        return isbn_error

    category_error = validate_category(payload["category"])
    if category_error:
        return category_error

    stock_error = validate_stock(payload["stock"])
    if stock_error:
        return stock_error

    return None
```

### 2. Update GET Endpoint

**Current:**
```python
@app.route('/', methods=['GET'])
def get_books():
    # ... database connection
    cursor.execute("SELECT id, publisher, name, date, cost FROM book")
    rows = cursor.fetchall()
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
```

**Updated:**
```python
@app.route('/', methods=['GET'])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, publisher, name, date, cost, isbn, category, stock FROM book")
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
            "isbn": row[5],
            "category": row[6],
            "stock": row[7],
        }
        for row in rows
    ])
```

### 3. Update POST Endpoint (/create)

**Current:**
```python
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
```

**Updated:**
```python
@app.route('/create', methods=['POST'])
def create_books():
    new_book = request.get_json(silent=True)
    validation_error = validate_book_payload(new_book)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO book (publisher, name, date, cost, isbn, category, stock) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                new_book['publisher'], 
                new_book['name'], 
                new_book['date'], 
                new_book['cost'],
                new_book['isbn'],
                new_book['category'],
                new_book['stock']
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(new_book), 201
    except sqlite3.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({"error": f"ISBN must be unique. {str(e)}"}), 400
```

### 4. Update PUT Endpoint (/update/<id>)

**Current:**
```python
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
    # ... rest of update logic
```

**Updated:**
```python
@app.route('/update/<int:id>', methods=['PUT'])
def update_book(id):
    updated_book = request.get_json(silent=True)
    validation_error = validate_book_payload(updated_book)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "UPDATE book SET publisher=?, name=?, date=?, cost=?, isbn=?, category=?, stock=? WHERE id=?",
            (
                updated_book['publisher'], 
                updated_book['name'], 
                updated_book['date'], 
                updated_book['cost'],
                updated_book['isbn'],
                updated_book['category'],
                updated_book['stock'],
                id
            )
        )
        if cursor.rowcount == 0:
            cursor.close()
            connection.close()
            return jsonify({"error": "Book not found"}), 404

        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"data": updated_book})
    except sqlite3.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({"error": f"ISBN must be unique. {str(e)}"}), 400
```

### 5. API Response Format Example

**GET / Response (multiple books):**
```json
[
    {
        "id": 1,
        "publisher": "Penguin",
        "name": "Python Mastery",
        "date": "2023-01-15",
        "cost": 45.99,
        "isbn": "978-0-13-468599-1",
        "category": "Technology",
        "stock": 5
    },
    {
        "id": 2,
        "publisher": "HarperCollins",
        "name": "The Great Gatsby",
        "date": "1925-04-10",
        "cost": 12.50,
        "isbn": "978-0-7432-7356-5",
        "category": "Fiction",
        "stock": 12
    }
]
```

---

## Frontend UI Implementation

### 1. Update Books.jsx (List View)

**Current Table Header:**
```jsx
<thead>
    <tr>
        <th scope='col'>Publisher</th>
        <th scope='col'>Book</th>
        <th scope='col'>Date</th>
        <th scope='col'>Cost</th>
        <th scope='col'>Actions</th>
    </tr>
</thead>
```

**Updated Table Header (Add 3 columns):**
```jsx
<thead>
    <tr>
        <th scope='col'>Publisher</th>
        <th scope='col'>Book</th>
        <th scope='col'>ISBN</th>
        <th scope='col'>Category</th>
        <th scope='col'>Date</th>
        <th scope='col'>Cost</th>
        <th scope='col'>Stock</th>
        <th scope='col'>Actions</th>
    </tr>
</thead>
```

**Updated Table Body:**
```jsx
<tbody>
    {books.map(book =>
        <tr key={book.id}>
            <td>{book.publisher}</td>
            <td>{book.name}</td>
            <td>{book.isbn}</td>
            <td>{book.category}</td>
            <td>{book.date}</td>
            <td>${book.cost.toFixed(2)}</td>
            <td>
                <span className={book.stock > 0 ? "text-success" : "text-danger"}>
                    {book.stock}
                </span>
            </td>
            <td>
                <button className="btn btn-primary btn-sm" onClick={() => handleUpdate(book)}>
                    Update
                </button>
                <button className="btn btn-danger btn-sm ms-2" onClick={() => handleDelete(book.id)}>
                    Delete
                </button>
            </td>
        </tr>
    )}
</tbody>
```

**CSS Enhancement (for stock visual indicator):**
```jsx
// Add this style for better UX
const getStockBadgeClass = (stock) => {
    if (stock > 10) return "badge bg-success";
    if (stock > 0) return "badge bg-warning";
    return "badge bg-danger";
};

// Then use in render:
<td>
    <span className={getStockBadgeClass(book.stock)}>
        Stock: {book.stock}
    </span>
</td>
```

---

### 2. Update CreateBook.jsx (Creation Form)

**Current Form Structure:**
```jsx
// Form fields for: publisher, name, date, cost

const handleSubmit = (e) => {
    e.preventDefault();
    const bookData = {
        publisher: publisherRef.current.value,
        name: nameRef.current.value,
        date: dateRef.current.value,
        cost: costRef.current.value
    };
    // axios POST...
}
```

**Updated Form Structure (Add 3 fields):**

```jsx
import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CreateBook = () => {
    const publisherRef = useRef();
    const nameRef = useRef();
    const dateRef = useRef();
    const costRef = useRef();
    const isbnRef = useRef();              // NEW
    const categoryRef = useRef();           // NEW
    const stockRef = useRef();              // NEW
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        
        // Validate ISBN format
        const isbn = isbnRef.current.value.replace(/[-\s]/g, '');
        if (!/^\d{10}$|^\d{13}$/.test(isbn)) {
            alert('ISBN must be 10 or 13 digits');
            return;
        }

        // Validate stock is non-negative
        if (parseInt(stockRef.current.value) < 0) {
            alert('Stock cannot be negative');
            return;
        }

        const bookData = {
            publisher: publisherRef.current.value,
            name: nameRef.current.value,
            date: dateRef.current.value,
            cost: parseFloat(costRef.current.value),
            isbn: isbnRef.current.value,
            category: categoryRef.current.value,
            stock: parseInt(stockRef.current.value)
        };

        axios.post('http://localhost:5001/create', bookData)
            .then(() => {
                alert('Book created successfully');
                navigate('/books');
            })
            .catch(err => {
                console.error(err);
                alert(err.response?.data?.error || 'Error creating book');
            });
    };

    return (
        <div className='container mt-5'>
            <h2>Create Book</h2>
            <form onSubmit={handleSubmit}>
                
                {/* Publisher Field */}
                <div className="mb-3">
                    <label htmlFor="publisher" className="form-label">Publisher</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="publisher"
                        ref={publisherRef} 
                        required 
                    />
                </div>

                {/* Name/Title Field */}
                <div className="mb-3">
                    <label htmlFor="name" className="form-label">Book Title</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="name"
                        ref={nameRef} 
                        required 
                    />
                </div>

                {/* ISBN Field (NEW) */}
                <div className="mb-3">
                    <label htmlFor="isbn" className="form-label">ISBN (10 or 13 digits)</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="isbn"
                        ref={isbnRef} 
                        placeholder="e.g., 978-0-13-468599-1"
                        pattern="[\d\-\s]{10,17}"
                        required 
                    />
                    <small className="form-text text-muted">Format: 10 or 13 digits with optional hyphens</small>
                </div>

                {/* Category Field (NEW) */}
                <div className="mb-3">
                    <label htmlFor="category" className="form-label">Category</label>
                    <select 
                        className="form-control" 
                        id="category"
                        ref={categoryRef} 
                        required
                    >
                        <option value="">Select a category</option>
                        <option value="Fiction">Fiction</option>
                        <option value="Non-Fiction">Non-Fiction</option>
                        <option value="Science">Science</option>
                        <option value="History">History</option>
                        <option value="Technology">Technology</option>
                        <option value="Biography">Biography</option>
                        <option value="Mystery">Mystery</option>
                        <option value="Self-Help">Self-Help</option>
                        <option value="Others">Others</option>
                    </select>
                </div>

                {/* Date Field */}
                <div className="mb-3">
                    <label htmlFor="date" className="form-label">Publication Date</label>
                    <input 
                        type="date" 
                        className="form-control" 
                        id="date"
                        ref={dateRef} 
                        required 
                    />
                </div>

                {/* Cost Field */}
                <div className="mb-3">
                    <label htmlFor="cost" className="form-label">Cost ($)</label>
                    <input 
                        type="number" 
                        className="form-control" 
                        id="cost"
                        ref={costRef} 
                        step="0.01"
                        required 
                    />
                </div>

                {/* Stock Field (NEW) */}
                <div className="mb-3">
                    <label htmlFor="stock" className="form-label">Stock Quantity</label>
                    <input 
                        type="number" 
                        className="form-control" 
                        id="stock"
                        ref={stockRef} 
                        min="0"
                        defaultValue="0"
                        required 
                    />
                    <small className="form-text text-muted">Number of copies in inventory</small>
                </div>

                {/* Submit Button */}
                <button type="submit" className="btn btn-success">
                    Create Book
                </button>
                <button 
                    type="button" 
                    className="btn btn-secondary ms-2"
                    onClick={() => navigate('/books')}
                >
                    Cancel
                </button>
            </form>
        </div>
    );
};

export default CreateBook;
```

---

### 3. Update UpdateBook.jsx (Edit Form)

**Pattern similar to CreateBook but with pre-filled values:**

```jsx
import React, { useRef, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const UpdateBook = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    
    const publisherRef = useRef();
    const nameRef = useRef();
    const dateRef = useRef();
    const costRef = useRef();
    const isbnRef = useRef();          // NEW
    const categoryRef = useRef();       // NEW
    const stockRef = useRef();          // NEW

    const { book } = location.state;

    useEffect(() => {
        if (book) {
            publisherRef.current.value = book.publisher;
            nameRef.current.value = book.name;
            dateRef.current.value = book.date;
            costRef.current.value = book.cost;
            isbnRef.current.value = book.isbn;          // NEW
            categoryRef.current.value = book.category;   // NEW
            stockRef.current.value = book.stock;        // NEW
        }
    }, [book]);

    const handleUpdate = (e) => {
        e.preventDefault();
        setLoading(true);

        // Validate ISBN format
        const isbn = isbnRef.current.value.replace(/[-\s]/g, '');
        if (!/^\d{10}$|^\d{13}$/.test(isbn)) {
            alert('ISBN must be 10 or 13 digits');
            setLoading(false);
            return;
        }

        // Validate stock is non-negative
        if (parseInt(stockRef.current.value) < 0) {
            alert('Stock cannot be negative');
            setLoading(false);
            return;
        }

        const updatedBook = {
            publisher: publisherRef.current.value,
            name: nameRef.current.value,
            date: dateRef.current.value,
            cost: parseFloat(costRef.current.value),
            isbn: isbnRef.current.value,
            category: categoryRef.current.value,
            stock: parseInt(stockRef.current.value)
        };

        axios.put(`http://localhost:5001/update/${book.id}`, updatedBook)
            .then(() => {
                alert('Book updated successfully');
                navigate('/books');
            })
            .catch(err => {
                console.error(err);
                alert(err.response?.data?.error || 'Error updating book');
            })
            .finally(() => setLoading(false));
    };

    return (
        <div className='container mt-5'>
            <h2>Update Book</h2>
            <form onSubmit={handleUpdate}>
                
                {/* Publisher Field */}
                <div className="mb-3">
                    <label htmlFor="publisher" className="form-label">Publisher</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="publisher"
                        ref={publisherRef} 
                        required 
                    />
                </div>

                {/* Name/Title Field */}
                <div className="mb-3">
                    <label htmlFor="name" className="form-label">Book Title</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="name"
                        ref={nameRef} 
                        required 
                    />
                </div>

                {/* ISBN Field (NEW) */}
                <div className="mb-3">
                    <label htmlFor="isbn" className="form-label">ISBN (10 or 13 digits)</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="isbn"
                        ref={isbnRef} 
                        placeholder="e.g., 978-0-13-468599-1"
                        pattern="[\d\-\s]{10,17}"
                        required 
                    />
                    <small className="form-text text-muted">Format: 10 or 13 digits with optional hyphens</small>
                </div>

                {/* Category Field (NEW) */}
                <div className="mb-3">
                    <label htmlFor="category" className="form-label">Category</label>
                    <select 
                        className="form-control" 
                        id="category"
                        ref={categoryRef} 
                        required
                    >
                        <option value="Fiction">Fiction</option>
                        <option value="Non-Fiction">Non-Fiction</option>
                        <option value="Science">Science</option>
                        <option value="History">History</option>
                        <option value="Technology">Technology</option>
                        <option value="Biography">Biography</option>
                        <option value="Mystery">Mystery</option>
                        <option value="Self-Help">Self-Help</option>
                        <option value="Others">Others</option>
                    </select>
                </div>

                {/* Date Field */}
                <div className="mb-3">
                    <label htmlFor="date" className="form-label">Publication Date</label>
                    <input 
                        type="date" 
                        className="form-control" 
                        id="date"
                        ref={dateRef} 
                        required 
                    />
                </div>

                {/* Cost Field */}
                <div className="mb-3">
                    <label htmlFor="cost" className="form-label">Cost ($)</label>
                    <input 
                        type="number" 
                        className="form-control" 
                        id="cost"
                        ref={costRef} 
                        step="0.01"
                        required 
                    />
                </div>

                {/* Stock Field (NEW) */}
                <div className="mb-3">
                    <label htmlFor="stock" className="form-label">Stock Quantity</label>
                    <input 
                        type="number" 
                        className="form-control" 
                        id="stock"
                        ref={stockRef} 
                        min="0"
                        required 
                    />
                    <small className="form-text text-muted">Number of copies in inventory</small>
                </div>

                {/* Submit Button */}
                <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={loading}
                >
                    {loading ? 'Updating...' : 'Update Book'}
                </button>
                <button 
                    type="button" 
                    className="btn btn-secondary ms-2"
                    onClick={() => navigate('/books')}
                    disabled={loading}
                >
                    Cancel
                </button>
            </form>
        </div>
    );
};

export default UpdateBook;
```

---

## Testing Strategy

### Unit Tests Updates (Jest/Vitest for React)

**Books.jsx Tests:**
```javascript
describe('Books Component - New Fields', () => {
    test('displays ISBN column in table', () => {
        // Mock data with new fields
        const mockBooks = [
            {
                id: 1,
                publisher: "Penguin",
                name: "Python Mastery",
                date: "2023-01-15",
                cost: 45.99,
                isbn: "978-0-13-468599-1",
                category: "Technology",
                stock: 5
            }
        ];
        // Assert ISBN column exists
    });

    test('displays category column in table', () => {
        // Assert category column exists and shows correct value
    });

    test('displays stock with color indicator (green for > 0, red for 0)', () => {
        // Assert stock value displays with correct badge color
    });

    test('renders table with all 8 columns: Publisher, Book, ISBN, Category, Date, Cost, Stock, Actions', () => {
        // Count headers and verify all are present
    });
});
```

### API Tests Updates (Pytest for Flask)

**test_books_api.py additions:**

```python
import pytest
import json

class TestBooksAPI:
    
    # Test POST /create with all 7 fields
    def test_create_book_with_all_fields(self, client):
        """Test creating a book with all 7 fields including new ones"""
        new_book = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "978-0-13-468599-1",
            "category": "Technology",
            "stock": 5
        }
        
        response = client.post(
            '/create',
            data=json.dumps(new_book),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        assert response.json["isbn"] == "978-0-13-468599-1"
        assert response.json["category"] == "Technology"
        assert response.json["stock"] == 5

    # Test ISBN validation
    def test_create_book_invalid_isbn_format(self, client):
        """Test that invalid ISBN is rejected"""
        book_invalid_isbn = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "INVALID-ISBN",  # Invalid
            "category": "Technology",
            "stock": 5
        }
        
        response = client.post(
            '/create',
            data=json.dumps(book_invalid_isbn),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert "ISBN" in response.json["error"]

    # Test ISBN uniqueness
    def test_isbn_uniqueness_constraint(self, client):
        """Test that duplicate ISBNs are rejected"""
        book1 = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "978-0-13-468599-1",
            "category": "Technology",
            "stock": 5
        }
        
        # Create first book
        response1 = client.post(
            '/create',
            data=json.dumps(book1),
            content_type='application/json'
        )
        assert response1.status_code == 201
        
        # Try to create second book with same ISBN
        response2 = client.post(
            '/create',
            data=json.dumps(book1),
            content_type='application/json'
        )
        
        assert response2.status_code == 400
        assert "unique" in response2.json["error"].lower()

    # Test category validation
    def test_create_book_invalid_category(self, client):
        """Test that invalid category is rejected"""
        book_invalid_category = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "978-0-13-468599-1",
            "category": "InvalidCategory",  # Invalid
            "stock": 5
        }
        
        response = client.post(
            '/create',
            data=json.dumps(book_invalid_category),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert "Category" in response.json["error"]

    # Test stock validation
    def test_create_book_negative_stock(self, client):
        """Test that negative stock is rejected"""
        book_negative_stock = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "978-0-13-468599-1",
            "category": "Technology",
            "stock": -5  # Invalid
        }
        
        response = client.post(
            '/create',
            data=json.dumps(book_negative_stock),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert "negative" in response.json["error"].lower()

    # Test GET returns all fields
    def test_get_books_returns_all_fields(self, client):
        """Test that GET / returns all 7 fields"""
        # First create a book
        book = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "978-0-13-468599-1",
            "category": "Technology",
            "stock": 5
        }
        client.post(
            '/create',
            data=json.dumps(book),
            content_type='application/json'
        )
        
        # Now fetch
        response = client.get('/')
        
        assert response.status_code == 200
        books = response.json
        assert len(books) > 0
        
        returned_book = books[0]
        assert "isbn" in returned_book
        assert "category" in returned_book
        assert "stock" in returned_book

    # Test PUT update all fields
    def test_update_book_with_new_fields(self, client):
        """Test updating all 7 fields of a book"""
        # Create initial book
        book = {
            "publisher": "Penguin",
            "name": "Python Mastery",
            "date": "2023-01-15",
            "cost": 45.99,
            "isbn": "978-0-13-468599-1",
            "category": "Technology",
            "stock": 5
        }
        create_response = client.post(
            '/create',
            data=json.dumps(book),
            content_type='application/json'
        )
        book_id = create_response.json["id"]
        
        # Update book
        updated_book = {
            "publisher": "O'Reilly",
            "name": "Advanced Python",
            "date": "2024-06-15",
            "cost": 59.99,
            "isbn": "978-0-13-468599-2",  # Different ISBN
            "category": "Science",         # Different category
            "stock": 10                    # Different stock
        }
        
        response = client.put(
            f'/update/{book_id}',
            data=json.dumps(updated_book),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        assert response.json["data"]["isbn"] == "978-0-13-468599-2"
        assert response.json["data"]["category"] == "Science"
        assert response.json["data"]["stock"] == 10
```

### Integration Tests (Playwright for E2E)

**create-book.spec.js updates:**

```javascript
test('Create book with all 7 fields including new ISBN, Category, Stock', async ({ page }) => {
    await page.goto('http://localhost:5173/create');
    
    // Fill form with all fields
    await page.fill('input[id="publisher"]', 'Penguin');
    await page.fill('input[id="name"]', 'Python Mastery');
    await page.fill('input[id="isbn"]', '978-0-13-468599-1');
    await page.selectOption('select[id="category"]', 'Technology');
    await page.fill('input[id="date"]', '2023-01-15');
    await page.fill('input[id="cost"]', '45.99');
    await page.fill('input[id="stock"]', '5');
    
    await page.click('button[type="submit"]');
    
    // Verify success message or redirect to books list
    await page.waitForURL('http://localhost:5173/books');
    
    // Verify book appears in list with all fields
    const table = await page.$eval('table', el => el.textContent);
    expect(table).toContain('978-0-13-468599-1');
    expect(table).toContain('Technology');
    expect(table).toContain('5');
});

test('Update book and modify ISBN and stock', async ({ page }) => {
    await page.goto('http://localhost:5173/books');
    
    // Click update button
    await page.click('button:has-text("Update")');
    
    // Change ISBN
    await page.fill('input[id="isbn"]', '978-0-13-468599-2');
    
    // Change stock
    await page.fill('input[id="stock"]', '10');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Verify update
    await page.waitForURL('http://localhost:5173/books');
    const updatedContent = await page.textContent('body');
    expect(updatedContent).toContain('978-0-13-468599-2');
    expect(updatedContent).toContain('10');
});

test('Reject invalid ISBN format', async ({ page }) => {
    await page.goto('http://localhost:5173/create');
    
    await page.fill('input[id="isbn"]', 'INVALID-ISBN');
    await page.click('button[type="submit"]');
    
    // Expect alert or error message
    const alert = page.once('dialog', dialog => dialog.accept());
    await alert;
});
```

---

## Migration & Deployment

### Step-by-Step Migration Process

#### Phase 1: Pre-Migration (Backup)
1. **Backup existing database:**
   ```bash
   cp Server/books.db Server/books.db.backup
   ```

2. **Create migration script:** `Server/migrate_v2.py`
   ```python
   import sqlite3
   import os
   
   def migrate_database():
       db_path = 'books.db'
       connection = sqlite3.connect(db_path)
       cursor = connection.cursor()
       
       try:
           # Create new table with updated schema
           cursor.execute('''
               CREATE TABLE book_new (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   publisher TEXT NOT NULL,
                   name TEXT NOT NULL,
                   date TEXT NOT NULL,
                   cost REAL NOT NULL,
                   isbn TEXT NOT NULL UNIQUE,
                   category TEXT NOT NULL,
                   stock INTEGER NOT NULL DEFAULT 0
               )
           ''')
           
           # Copy existing data
           cursor.execute('''
               INSERT INTO book_new (id, publisher, name, date, cost, isbn, category, stock)
               SELECT id, publisher, name, date, cost, 
                      'UNKNOWN-' || id, 'Others', 0
               FROM book
           ''')
           
           # Drop old table and rename new one
           cursor.execute('DROP TABLE book')
           cursor.execute('ALTER TABLE book_new RENAME TO book')
           
           connection.commit()
           print("✓ Migration successful!")
           
       except Exception as e:
           connection.rollback()
           print(f"✗ Migration failed: {e}")
       finally:
           cursor.close()
           connection.close()
   
   if __name__ == '__main__':
       migrate_database()
   ```

3. **Test migration on backup:**
   ```bash
   cp Server/books.db.backup Server/books.db.test
   python migrate_v2.py  # Run on test copy
   ```

#### Phase 2: Code Updates
1. Update `app.py` with new validation and database changes
2. Update React components (Books.jsx, CreateBook.jsx, UpdateBook.jsx)
3. Run linting and type checks

#### Phase 3: Testing
1. Run unit tests (Jest for React, Pytest for Flask)
2. Run integration tests (Playwright E2E)
3. Manual smoke testing

#### Phase 4: Deployment
1. Stop current application
2. Run migration script on production database
3. Deploy updated code
4. Run smoke tests
5. Monitor for errors

### Deployment Checklist

```bash
# Stop Flask backend
# Stop React frontend
# Backup production database
cp Server/books.db Server/books.db.backup_$(date +%Y%m%d_%H%M%S)

# Run migration
python Server/migrate_v2.py

# Verify migration
# (Check data integrity manually)

# Update backend code (app.py)
# Update frontend code (React components)

# Restart Flask backend
cd Server && python app.py

# Restart React frontend (if needed)
cd Client && npm run dev

# Run tests
cd Server && bash run-pytest.sh
cd Client && npm run test

# Monitor logs
tail -f Server/app.log
```

---

## Implementation Checklist

### Backend Changes
- [ ] Update `ensure_schema()` in `app.py` with migration logic
- [ ] Add validation functions: `validate_isbn()`, `validate_category()`, `validate_stock()`
- [ ] Update `validate_book_payload()` to validate all 7 fields
- [ ] Update `/` (GET) endpoint to SELECT all 7 columns
- [ ] Update `/create` (POST) endpoint with new fields
- [ ] Update `/update/<id>` (PUT) endpoint with new fields
- [ ] Add try-catch for ISBN UNIQUE constraint in POST and PUT
- [ ] Update requirements.txt if any new dependencies needed
- [ ] Test all endpoints with Postman/cURL

### Frontend Changes
- [ ] Update `Books.jsx` table headers (add ISBN, Category, Stock columns)
- [ ] Update `Books.jsx` table rows to display new fields
- [ ] Add stock badge styling based on quantity
- [ ] Update `CreateBook.jsx` form with 3 new input fields
- [ ] Add client-side validation for ISBN, category, stock
- [ ] Update `UpdateBook.jsx` form with 3 new input fields
- [ ] Test form submissions and validations
- [ ] Test form pre-filling on update

### Database Changes
- [ ] Create migration script `migrate_v2.py`
- [ ] Test migration on backup database
- [ ] Document migration steps
- [ ] Add schema documentation

### Testing Changes
- [ ] Add Pytest test cases for ISBN, category, stock validation
- [ ] Add Pytest test cases for UNIQUE ISBN constraint
- [ ] Add Playwright E2E tests for new fields
- [ ] Update existing tests to include new fields
- [ ] Run full test suite

### Documentation Changes
- [ ] Update README.md with new fields
- [ ] Update API documentation with new request/response formats
- [ ] Document field validation rules
- [ ] Document migration steps for existing databases

### Deployment
- [ ] Backup production database
- [ ] Run migration on production
- [ ] Deploy updated backend code
- [ ] Deploy updated frontend code
- [ ] Verify new functionality in production
- [ ] Monitor for issues

---

## Summary

### What's Being Added

| Aspect | Details |
|--------|---------|
| **New Fields** | ISBN (TEXT, UNIQUE), Category (TEXT, dropdown), Stock (INTEGER, non-negative) |
| **Database Tables** | 1 table (book) with 7 total columns |
| **API Endpoints** | 4 endpoints updated (GET, POST, PUT, DELETE) |
| **React Components** | 3 components updated (Books, CreateBook, UpdateBook) |
| **Validation Rules** | ISBN: 10 or 13 digits; Category: predefined list; Stock: non-negative integer |
| **Database Changes** | Schema migration with data preservation |
| **Test Coverage** | Unit, integration, and E2E tests added |

### Implementation Timeline

- **Day 1:** Backend changes + database migration
- **Day 2:** Frontend changes + component testing
- **Day 3:** Full testing suite (unit + integration + E2E)
- **Day 4:** Bug fixes + final deployment

### Key Considerations

1. **ISBN Uniqueness:** UNIQUE constraint prevents duplicate ISBNs
2. **Backward Compatibility:** Migration preserves existing book data
3. **Validation:** Multi-layer validation (client + server)
4. **User Experience:** Dropdown for categories, number inputs for stock
5. **Error Handling:** Clear error messages for validation failures

---

**End of Implementation Guide**
