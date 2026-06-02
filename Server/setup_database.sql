-- SQLite Database Setup for Flask CRUD App
-- SQLite database (books.db) is auto-created by Flask on first run.
-- This script is provided for reference only.

-- Create the book table
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher TEXT NOT NULL,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    cost REAL NOT NULL
);

-- Insert sample data for testing
INSERT INTO book (publisher, name, date, cost) VALUES
('Penguin Random House', 'Python Crash Course', '2023-01-15', 299.99),
('O''Reilly Media', 'Learning Flask', '2023-06-20', 399.50),
('Manning Publications', 'Flask Web Development', '2024-03-10', 449.00);
