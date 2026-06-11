import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')

sample_books = [
    ("Scribner", "The Great Gatsby", "1925-04-10", 10.99),
    ("Secker & Warburg", "1984", "1949-06-08", 8.99),
    ("J.B. Lippincott & Co.", "To Kill a Mockingbird", "1960-07-11", 12.50)
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS book (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        publisher TEXT NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        cost REAL NOT NULL
    )
""")

# Insert sample books if they don't already exist
for book in sample_books:
    cur.execute("""
        INSERT INTO book (publisher, name, date, cost)
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM book WHERE name=? AND publisher=?
        )
    """, (book[0], book[1], book[2], book[3], book[1], book[0]))

conn.commit()
cur.close()
conn.close()
print("Sample books added to database successfully!")
