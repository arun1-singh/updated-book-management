# Complete Setup Guide — Book Management System

Every command you need, in order, to get this project running on a fresh machine.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone the Repository](#2-clone-the-repository)
3. [Option A — Docker Compose (recommended, one command)](#3-option-a--docker-compose-recommended)
4. [Option B — Manual Setup (no Docker)](#4-option-b--manual-setup-no-docker)
   - [4.1 Install ODBC Driver 17](#41-install-microsoft-odbc-driver-17-for-sql-server)
   - [4.2 Run SQL Server in Docker](#42-run-sql-server-in-docker)
   - [4.3 Set up the Backend](#43-set-up-the-flask-backend)
   - [4.4 Set up the Frontend](#44-set-up-the-react-frontend)
5. [Docker — Individual Container Commands](#5-docker--individual-container-commands)
6. [Docker Compose Commands](#6-docker-compose-commands)
7. [Docker Networking](#7-docker-networking)
8. [SQL Server — Database Commands](#8-sql-server--database-commands)
9. [Running Tests](#9-running-tests)
   - [9.1 Pytest (backend)](#91-pytest-backend-tests)
   - [9.2 Playwright (frontend E2E)](#92-playwright-frontend-e2e-tests)
   - [9.3 Newman (API tests)](#93-newman-api-tests)
10. [Environment Variables Reference](#10-environment-variables-reference)
11. [Port Reference](#11-port-reference)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

Install these tools before you start.

### Git
```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y git

# macOS
brew install git

# Windows — download from https://git-scm.com
```

### Python 3.10+
```bash
# Ubuntu / Debian
sudo apt-get install -y python3 python3-pip python3-venv

# macOS
brew install python

# Verify
python3 --version
```

### Node.js 18+
```bash
# Ubuntu / Debian (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node

# Windows — download from https://nodejs.org

# Verify
node --version
npm --version
```

### Docker and Docker Compose
```bash
# Ubuntu / Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# Add your user to the docker group (log out and back in after)
sudo usermod -aG docker $USER

# macOS / Windows — install Docker Desktop from https://www.docker.com/products/docker-desktop

# Verify
docker --version
docker compose version
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/arun1-singh/updated-book-management.git
cd updated-book-management
```

---

## 3. Option A — Docker Compose (recommended)

This single command starts SQL Server, the Flask backend, and the React frontend together.

```bash
# From the project root
docker compose up --build
```

Wait for all three services to become healthy (about 60–90 seconds on first run).

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:5173  |
| Backend  | http://localhost:5001  |
| MSSQL    | localhost:1433         |

```bash
# Run in background
docker compose up --build -d

# View live logs
docker compose logs -f

# View logs for one service only
docker compose logs -f backend
docker compose logs -f mssql
docker compose logs -f frontend

# Stop everything (keeps volumes)
docker compose down

# Stop and delete all volumes (wipes the database)
docker compose down -v

# Rebuild after code changes
docker compose up --build
```

---

## 4. Option B — Manual Setup (no Docker for app, Docker for SQL Server)

### 4.1 Install Microsoft ODBC Driver 17 for SQL Server

#### Ubuntu 22.04 (jammy)
```bash
# Download the Microsoft GPG key
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.asc
sudo gpg --batch --yes --dearmor \
  -o /usr/share/keyrings/microsoft-prod.gpg /tmp/microsoft.asc

# Add the Microsoft apt repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
  https://packages.microsoft.com/ubuntu/22.04/prod jammy main" \
  | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Install ODBC Driver 17
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Verify
odbcinst -q -d
# Expected output: [ODBC Driver 17 for SQL Server]
```

#### Ubuntu 20.04 (focal)
```bash
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc -o /tmp/microsoft.asc
sudo gpg --batch --yes --dearmor \
  -o /usr/share/keyrings/microsoft-prod.gpg /tmp/microsoft.asc

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
  https://packages.microsoft.com/ubuntu/20.04/prod focal main" \
  | sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
```

#### macOS
```bash
brew tap microsoft/mssql-release https://github.com/microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools
```

#### Windows
Download and install from:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

Or use the helper script included in the repo (Ubuntu only):
```bash
sudo bash Server/install_odbc.sh
```

---

### 4.2 Run SQL Server in Docker

```bash
# Pull the image
docker pull mcr.microsoft.com/mssql/server:2019-latest

# Run SQL Server container
docker run -d \
  --name mssql-container \
  -e ACCEPT_EULA=Y \
  -e SA_PASSWORD=YourStrong@Passw0rd \
  -e MSSQL_PID=Developer \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2019-latest

# Wait ~15 seconds for SQL Server to start, then check it's running
docker ps | grep mssql-container

# View SQL Server logs
docker logs mssql-container

# Create the database
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong@Passw0rd' \
  -Q "CREATE DATABASE books_db"

# Verify the database exists
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong@Passw0rd' \
  -Q "SELECT name FROM sys.databases"
```

Tables are created automatically when Flask starts for the first time via `init_db()`.

To run the full SQL setup script manually (creates tables + sample data):
```bash
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong@Passw0rd' \
  -i /path/to/Server/setup_database.sql
```

---

### 4.3 Set up the Flask Backend

```bash
# Navigate to the Server directory
cd Server

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
# Linux / macOS:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Create the .env file (edit values to match your setup)
cat > .env << 'EOF'
MSSQL_SERVER=localhost
MSSQL_DATABASE=books_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
MSSQL_TRUST_CERT=yes
JWT_SECRET_KEY=change-me-to-something-random-and-long
EOF

# Start the Flask backend
python app.py
```

The backend starts at **http://localhost:5001**

Verify it is running:
```bash
curl http://localhost:5001/health
# Expected: {"status":"healthy"}
```

To run with Flask CLI instead:
```bash
export FLASK_APP=app.py
flask run --host 0.0.0.0 --port 5001
```

---

### 4.4 Set up the React Frontend

Open a **new terminal** (keep the backend running).

```bash
# Navigate to the Client directory
cd Client

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

The frontend starts at **http://localhost:5173**

Open http://localhost:5173 in your browser.

---

## 5. Docker — Individual Container Commands

### SQL Server container
```bash
# Start (if already created)
docker start mssql-container

# Stop
docker stop mssql-container

# Restart
docker restart mssql-container

# Remove container
docker rm -f mssql-container

# View logs
docker logs mssql-container
docker logs -f mssql-container          # follow / live

# Open interactive sqlcmd shell inside the container
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong@Passw0rd'

# Run a one-off SQL query
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong@Passw0rd' \
  -Q "USE books_db; SELECT * FROM book"
```

### Backend container (when built manually)
```bash
# Build the image
docker build -t book-management-backend ./Server

# Run the container
docker run -d \
  --name book-management-backend \
  -p 5001:5001 \
  -e MSSQL_SERVER=host.docker.internal \
  -e MSSQL_DATABASE=books_db \
  -e MSSQL_USERNAME=sa \
  -e MSSQL_PASSWORD=YourStrong@Passw0rd \
  -e MSSQL_DRIVER="ODBC Driver 17 for SQL Server" \
  -e MSSQL_TRUST_CERT=yes \
  -e JWT_SECRET_KEY=my-secret-key \
  book-management-backend

# View logs
docker logs book-management-backend
docker logs -f book-management-backend

# Stop and remove
docker stop book-management-backend
docker rm book-management-backend
```

### Frontend container (when built manually)
```bash
# Build the image
docker build -t book-management-frontend ./Client

# Run the container
docker run -d \
  --name book-management-frontend \
  -p 5173:5173 \
  book-management-frontend

# View logs
docker logs book-management-frontend

# Stop and remove
docker stop book-management-frontend
docker rm book-management-frontend
```

### General Docker commands
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List all images
docker images

# Remove an image
docker rmi book-management-backend

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# Remove all unused volumes
docker volume prune

# Full system cleanup (containers, images, volumes, networks)
docker system prune -a --volumes
```

---

## 6. Docker Compose Commands

Run all commands from the project root (where `docker-compose.yml` lives).

```bash
# Build and start all services
docker compose up --build

# Start in detached / background mode
docker compose up --build -d

# Start without rebuilding (use cached images)
docker compose up -d

# Stop all services (keep containers and volumes)
docker compose stop

# Stop and remove containers (keep volumes)
docker compose down

# Stop, remove containers AND volumes (deletes database data)
docker compose down -v

# Rebuild a single service
docker compose build backend
docker compose build frontend

# Start a single service
docker compose up -d mssql
docker compose up -d backend

# Restart a single service
docker compose restart backend

# View logs for all services
docker compose logs

# Follow logs live
docker compose logs -f

# Follow logs for one service
docker compose logs -f backend

# View running service status
docker compose ps

# Open a shell in a running container
docker compose exec backend bash
docker compose exec mssql bash

# Run a one-off command in a service container
docker compose exec backend python -c "from app import init_db; init_db()"

# Scale a service (run multiple replicas)
docker compose up -d --scale backend=2

# Pull latest images
docker compose pull
```

---

## 7. Docker Networking

The project uses a custom bridge network called `book-management-network`.

```bash
# List all Docker networks
docker network ls

# Inspect the project network (shows connected containers and IPs)
docker network inspect book-management-network

# Create the network manually (Docker Compose does this automatically)
docker network create \
  --driver bridge \
  book-management-network

# Connect an existing container to the network
docker network connect book-management-network mssql-container

# Disconnect a container from the network
docker network disconnect book-management-network mssql-container

# Remove the network (all containers must be disconnected first)
docker network rm book-management-network

# Ping between containers (test connectivity)
docker exec book-management-backend ping mssql-container

# Check which containers are on a network
docker network inspect book-management-network \
  --format '{{range .Containers}}{{.Name}} {{end}}'
```

**Container hostnames within `book-management-network`:**

| Container | Hostname | Port |
|---|---|---|
| SQL Server | `mssql-container` | 1433 |
| Flask backend | `book-management-backend` | 5001 |
| React frontend | `book-management-frontend` | 5173 |

Containers talk to each other by hostname. The backend connects to SQL Server using `MSSQL_SERVER=mssql-container,1433`.

---

## 8. SQL Server — Database Commands

### Connect to SQL Server

From inside the container:
```bash
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong@Passw0rd'
```

From the host machine (requires sqlcmd installed locally):
```bash
sqlcmd -S localhost,1433 -U sa -P 'YourStrong@Passw0rd'
```

From Python (test connection):
```bash
python3 -c "
import pyodbc
conn = pyodbc.connect(
  'DRIVER={ODBC Driver 17 for SQL Server};'
  'SERVER=localhost,1433;DATABASE=master;'
  'UID=sa;PWD=YourStrong@Passw0rd;TrustServerCertificate=yes;'
)
print('Connected OK')
conn.close()
"
```

### Common SQL operations

```sql
-- List all databases
SELECT name FROM sys.databases;
GO

-- Switch to books_db
USE books_db;
GO

-- List all tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;
GO

-- View all books
SELECT * FROM book;
GO

-- View all users
SELECT id, username FROM users;
GO

-- Count books
SELECT COUNT(*) AS total_books FROM book;
GO

-- Insert a test book manually
INSERT INTO book (publisher, name, date, cost)
VALUES ('Test Publisher', 'Test Book', '2024-01-01', 29.99);
GO

-- Delete all books (reset table)
DELETE FROM book;
GO

-- Drop and recreate the books table
DROP TABLE IF EXISTS book;
CREATE TABLE book (
    id        INT IDENTITY(1,1) PRIMARY KEY,
    publisher NVARCHAR(255) NOT NULL,
    name      NVARCHAR(255) NOT NULL,
    date      NVARCHAR(20)  NOT NULL,
    cost      FLOAT         NOT NULL
);
GO
```

### Create a test user for login

```bash
# Run this Python script to create testuser (password: Test@1234)
cd Server
source venv/bin/activate
python3 - << 'EOF'
import pyodbc
from werkzeug.security import generate_password_hash

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost,1433;DATABASE=books_db;'
    'UID=sa;PWD=YourStrong@Passw0rd;TrustServerCertificate=yes;'
)
cursor = conn.cursor()
cursor.execute("SELECT id FROM users WHERE username = 'testuser'")
if not cursor.fetchone():
    hashed = generate_password_hash('Test@1234')
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ('testuser', hashed)
    )
    conn.commit()
    print("testuser created OK")
else:
    print("testuser already exists")
cursor.close()
conn.close()
EOF
```

---

## 9. Running Tests

### 9.1 Pytest (backend tests)

Tests run against a real SQL Server instance.

```bash
cd Server

# Activate virtual environment
source venv/bin/activate         # Linux / macOS
.\venv\Scripts\Activate.ps1      # Windows

# Run all tests with verbose output
python -m pytest tests/pytest -v

# Run a specific test file
python -m pytest tests/pytest/test_books_api.py -v

# Run tests matching a keyword
python -m pytest tests/pytest -v -k "delete"

# Run tests by marker
python -m pytest tests/pytest -v -m create_api
python -m pytest tests/pytest -v -m delete_api

# Run with JSON report
python -m pytest tests/pytest -v \
  --json-report \
  --json-report-file=tests/pytest/pytest-report.json

# Show test output even for passing tests
python -m pytest tests/pytest -v -s

# Stop on first failure
python -m pytest tests/pytest -v -x
```

### 9.2 Playwright (frontend E2E tests)

The Flask backend must be running before Playwright tests start.

**Terminal 1 — start backend:**
```bash
cd Server
source venv/bin/activate
python app.py
```

**Terminal 2 — run Playwright:**
```bash
cd Client

# Install dependencies (first time only)
npm install

# Install Playwright browsers (first time only)
npx playwright install
npx playwright install --with-deps chromium     # install system dependencies too

# Run all tests (headless)
npx playwright test

# Run tests with 1 worker (sequential, good for debugging)
npx playwright test --workers=1

# Run a specific test file
npx playwright test tests/books.spec.js

# Run in headed mode (shows browser window)
npx playwright test --headed

# Run in debug mode (step through tests)
npx playwright test --debug

# Run with Playwright UI (interactive test runner)
npx playwright test --ui

# Open the HTML report after a run
npx playwright show-report

# Run only tests matching a pattern
npx playwright test --grep "delete"
```

### 9.3 Newman (API tests)

```bash
cd Server/tests/postman_newman

# Install dependencies
npm install

# Run Newman tests
npm test

# Run with enhanced HTML report
npm run test:enhanced

# Check dependencies
bash check-dependencies.sh
```

---

## 10. Environment Variables Reference

Create `Server/.env` (never commit this file):

```env
# SQL Server connection
MSSQL_SERVER=localhost
MSSQL_DATABASE=books_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
MSSQL_TRUST_CERT=yes

# JWT
JWT_SECRET_KEY=replace-this-with-a-long-random-string
```

| Variable | Default | Description |
|---|---|---|
| `MSSQL_SERVER` | `localhost` | SQL Server host. Use `mssql-container,1433` when running in Docker Compose |
| `MSSQL_DATABASE` | `books_db` | Database name |
| `MSSQL_USERNAME` | `sa` | SQL Server login |
| `MSSQL_PASSWORD` | `YourStrong@Passw0rd` | SA password |
| `MSSQL_DRIVER` | `ODBC Driver 17 for SQL Server` | ODBC driver string — must match what `odbcinst -q -d` shows |
| `MSSQL_TRUST_CERT` | `yes` | Trust self-signed cert (fine for dev) |
| `JWT_SECRET_KEY` | `dev-secret-key-change-me` | Change this in production |

---

## 11. Port Reference

| Service | Port | URL |
|---|---|---|
| React frontend (dev) | 5173 | http://localhost:5173 |
| Flask backend | 5001 | http://localhost:5001 |
| SQL Server | 1433 | localhost,1433 |

API health check:
```bash
curl http://localhost:5001/health
# {"status":"healthy"}
```

---

## 12. Troubleshooting

### `Can't open lib 'ODBC Driver 17 for SQL Server': file not found`
The ODBC driver is not installed.
```bash
# Install it
sudo bash Server/install_odbc.sh

# Verify
odbcinst -q -d
```

### `Login timeout expired` / `TCP Provider: Error code 0x2746`
SQL Server is not running or not reachable on port 1433.
```bash
# Check if container is running
docker ps | grep mssql

# Start it
docker start mssql-container

# Check logs
docker logs mssql-container
```

### `Login failed for user 'sa'`
Wrong password or SA login is disabled.
```bash
# Check your .env file password matches what you used when starting the container
# If using Docker Compose, both must match SA_PASSWORD in docker-compose.yml
```

### `Address already in use` — port 5001 or 5173
```bash
# Linux / macOS
lsof -ti :5001 | xargs kill -9
lsof -ti :5173 | xargs kill -9

# Windows PowerShell
netstat -ano | findstr :5001
Stop-Process -Id <PID> -Force
```

### `Address already in use` — port 1433
Another SQL Server instance is running.
```bash
# Find what is using 1433
lsof -ti :1433

# Or change the host port in docker-compose.yml / docker run command
# e.g. -p 1434:1433 and set MSSQL_SERVER=localhost,1434
```

### Virtual environment not activating on Windows
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\venv\Scripts\Activate.ps1
```

### `ModuleNotFoundError` after activating venv
```bash
pip install -r requirements.txt
```

### Docker permission denied
```bash
# Add user to docker group then log out and back in
sudo usermod -aG docker $USER
newgrp docker
```

### Playwright tests fail with `ERR_CONNECTION_REFUSED`
The Flask backend or frontend server is not running.
```bash
# Check Flask is running
curl http://localhost:5001/health

# Check frontend is running
curl http://localhost:5173
```

### Reset everything (fresh start)
```bash
# Stop and remove all containers + volumes
docker compose down -v

# Remove built images
docker rmi book-management-backend book-management-frontend

# Delete Python venv
rm -rf Server/venv

# Delete Node modules
rm -rf Client/node_modules

# Start fresh
docker compose up --build
```
