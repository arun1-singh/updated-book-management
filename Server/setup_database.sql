-- ============================================================
-- MSSQL Database Setup for Book Management Flask App
-- Run this manually inside the SQL Server container:
--
--   docker exec -it mssql-container \
--     /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrong@Passw0rd' \
--     -i /setup_database.sql
-- ============================================================

-- Step 1: Create the database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'books_db')
BEGIN
    CREATE DATABASE books_db;
END
GO

-- Step 2: Use the database
USE books_db;
GO

-- Step 3: Create the book table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'book' AND xtype = 'U')
BEGIN
    CREATE TABLE book (
        id        INT IDENTITY(1,1) PRIMARY KEY,
        publisher NVARCHAR(255) NOT NULL,
        name      NVARCHAR(255) NOT NULL,
        date      NVARCHAR(20)  NOT NULL,
        cost      FLOAT         NOT NULL
    );
END
GO

-- Step 4: Create the users table
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name = 'users' AND xtype = 'U')
BEGIN
    CREATE TABLE users (
        id            INT IDENTITY(1,1) PRIMARY KEY,
        username      NVARCHAR(150) NOT NULL UNIQUE,
        password_hash NVARCHAR(256) NOT NULL
    );
END
GO

-- Step 5: Insert sample books for testing
INSERT INTO book (publisher, name, date, cost) VALUES
('Penguin Random House', 'Python Crash Course',    '2023-01-15', 299.99),
('O''Reilly Media',      'Learning Flask',         '2023-06-20', 399.50),
('Manning Publications', 'Flask Web Development',  '2024-03-10', 449.00);
GO

-- Step 6: Verify
SELECT * FROM book;
GO
SELECT * FROM users;
GO
