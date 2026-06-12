# Book Management System — Flask + React + SQL Server

A full-stack CRUD application for managing books, using Microsoft SQL Server as the database.

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Bootstrap, Axios |
| Backend | Flask 3, Flask-JWT-Extended, Flask-CORS, pyodbc |
| Database | Microsoft SQL Server 2019 |
| Backend tests | Pytest |
| Frontend tests | Playwright |
| API tests | Postman / Newman |
| CI/CD | GitHub Actions (real MSSQL container) |
| Containerisation | Docker, Docker Compose |

---

## Prerequisites

Install these before you begin:

| Tool | Minimum version | Purpose |
|---|---|---|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Docker | latest | Run SQL Server |
| Docker Compose | v2+ | Orchestrate all services |
| Microsoft ODBC Driver 17 | 17.x | Python ↔ SQL Server |

---

## Quick start (Docker Compose — recommended)

This is the simplest way to run the full stack including SQL Server.

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:5001 |
| SQL Server | localhost:1433 |

The backend calls `init_db()` on startup — tables are created automatically the first time.

Other useful commands:

```bash
docker compose up -d          # run in background
docker compose down           # stop everything
docker compose up --build     # rebuild after code changes
docker compose logs -f        # stream all logs
docker compose logs backend   # stream backend logs only
```

---

## Manual local setup (without Docker)

Use this if you want to run Flask and React directly on your machine (SQL Server still needs to run somewhere — see below).

### 1. Run SQL Server locally

The easiest way is Docker:

```bash
docker run -d \
  --name mssql-container \
  -e ACCEPT_EULA=Y \
  -e SA_PASSWORD=YourStrong@Passw0rd \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2019-latest
```

Wait ~15 seconds for SQL Server to be ready, then create the database:

```bash
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrong@Passw0rd' \
  -Q "CREATE DATABASE books_db"
```

Tables are created automatically when Flask starts for the first time.

### 2. Install the ODBC Driver 17

**Ubuntu / Debian:**

```bash
sudo bash Server/install_odbc.sh
```

Or manually:

```bash
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
  | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
  https://packages.microsoft.com/ubuntu/22.04/prod jammy main" \
  | sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev
```

**Windows:**

Download and install from [Microsoft's ODBC Driver page](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server).

**macOS:**

```bash
brew tap microsoft/mssql-release https://github.com/microsoft/homebrew-mssql-release
brew install msodbcsql17 mssql-tools
```

### 3. Configure the backend

Create `Server/.env` (never commit this file):

```env
MSSQL_SERVER=localhost
MSSQL_DATABASE=books_db
MSSQL_USERNAME=sa
MSSQL_PASSWORD=YourStrong@Passw0rd
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
MSSQL_TRUST_CERT=yes
JWT_SECRET_KEY=change-me-to-something-random
```

### 4. Start the backend

```bash
cd Server

python -m venv venv
source venv/bin/activate        # Linux / macOS
# OR
.\venv\Scripts\Activate.ps1     # Windows PowerShell

pip install -r requirements.txt
python app.py
```

Backend starts at `http://localhost:5001`.

Health check:

```bash
curl http://localhost:5001/health
# → {"status":"healthy"}
```

### 5. Start the frontend (new terminal)

```bash
cd Client
npm install
npm run dev
```

Frontend starts at `http://localhost:5173`.

---

## Project structure

```
.
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # GitHub Actions — uses real MSSQL container
├── Client/                        # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── Books.jsx
│   │   ├── CreateBook.jsx
│   │   ├── UpdateBook.jsx
│   │   ├── Login.jsx
│   │   ├── Signup.jsx
│   │   └── Nav.jsx
│   ├── tests/                     # Playwright E2E tests
│   ├── global-setup.js            # Playwright global setup (login + token)
│   ├── playwright.config.js
│   ├── Dockerfile
│   └── package.json
├── Server/                        # Flask backend
│   ├── app.py                     # Main application (MSSQL via pyodbc)
│   ├── requirements.txt
│   ├── .env                       # Local secrets — do NOT commit
│   ├── setup_database.sql         # Run manually inside SQL Server container
│   ├── install_odbc.sh            # ODBC driver installer for Ubuntu
│   ├── Dockerfile
│   └── tests/
│       ├── pytest/                # Pytest suite
│       │   ├── conftest.py
│       │   └── test_books_api.py
│       └── postman_newman/        # Newman / Postman tests
├── docker-compose.yml             # Runs MSSQL + backend + frontend
└── README.md
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `MSSQL_SERVER` | `localhost` | SQL Server host (use `mssql-container,1433` in Docker) |
| `MSSQL_DATABASE` | `books_db` | Database name |
| `MSSQL_USERNAME` | `sa` | SQL Server login |
| `MSSQL_PASSWORD` | `YourStrong@Passw0rd` | SQL Server password |
| `MSSQL_DRIVER` | `ODBC Driver 17 for SQL Server` | ODBC driver name |
| `MSSQL_TRUST_CERT` | `yes` | Trust self-signed cert (dev only) |
| `JWT_SECRET_KEY` | `dev-secret-key-change-me` | JWT signing key — **change in production** |

---

## API reference

All endpoints on `http://localhost:5001`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | No | Health check |
| `POST` | `/signup` | No | Register a new user |
| `POST` | `/login` | No | Login — returns JWT |
| `GET` | `/` | No | List all books |
| `POST` | `/create` | JWT | Add a book |
| `PUT` | `/update/<id>` | JWT | Update a book |
| `DELETE` | `/delete/<id>` | JWT | Delete a book |

### Signup

```http
POST /signup
Content-Type: application/json

{"username": "alice", "password": "Secret@1"}
```

### Login

```http
POST /login
Content-Type: application/json

{"username": "alice", "password": "Secret@1"}
```

Returns:

```json
{"access_token": "<jwt>"}
```

### Create a book

```http
POST /create
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "publisher": "O'Reilly",
  "name": "Learning Flask",
  "date": "2024-10-11",
  "cost": 49.99
}
```

### Update a book

```http
PUT /update/1
Authorization: Bearer <jwt>
Content-Type: application/json

{"publisher": "Packt", "name": "Updated", "date": "2025-01-01", "cost": 39.99}
```

### Delete a book

```http
DELETE /delete/1
Authorization: Bearer <jwt>
```

---

## Database schema

The app creates tables automatically on startup via `init_db()`.
To set up manually (or add sample data) run:

```bash
docker exec -it mssql-container \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrong@Passw0rd' \
  -i /path/to/Server/setup_database.sql
```

Tables:

```sql
-- books
CREATE TABLE book (
    id        INT IDENTITY(1,1) PRIMARY KEY,
    publisher NVARCHAR(255) NOT NULL,
    name      NVARCHAR(255) NOT NULL,
    date      NVARCHAR(20)  NOT NULL,
    cost      FLOAT         NOT NULL
);

-- users
CREATE TABLE users (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    username      NVARCHAR(150) NOT NULL UNIQUE,
    password_hash NVARCHAR(256) NOT NULL
);
```

---

## Running Pytest (backend tests)

Tests run against a real MSSQL instance. Make sure SQL Server is running and the `.env` file is configured.

```bash
cd Server
source venv/bin/activate        # or .\venv\Scripts\Activate.ps1 on Windows

python -m pytest tests/pytest -v

# With JSON report
python -m pytest tests/pytest -v \
  --json-report --json-report-file=tests/pytest/pytest-report.json
```

---

## Running Playwright (frontend E2E tests)

The Flask backend must be running first.

**Terminal 1 — start backend:**

```bash
cd Server
source venv/bin/activate
python app.py
```

**Terminal 2 — run tests:**

```bash
cd Client
npm install
npx playwright install          # first time only
npx playwright test
```

Useful commands:

```bash
npx playwright test --headed    # show browser
npx playwright test --debug     # step-by-step
npx playwright show-report      # open HTML report
```

---

## Running Newman (API tests)

```bash
cd Server/tests/postman_newman
npm install
npm test
```

Flask must be running on port `5001`.

---

## GitHub Actions CI/CD

The pipeline at `.github/workflows/ci-cd.yml` runs on every push/PR to `main`.

| Job | What it does |
|---|---|
| `backend-tests` | Spins up MSSQL container, installs ODBC 17, creates DB + tables, seeds test user, runs Pytest |
| `frontend-build` | Runs `npm ci` + `npm run build`, uploads dist artifact |
| `playwright-tests` | Spins up MSSQL container, starts Flask, serves built frontend, runs Playwright |
| `package-artifacts` | Bundles release artifacts (main branch pushes only) |

**No GitHub secrets required** for CI — MSSQL credentials are baked into the workflow with the standard developer password. For production deployments, add secrets via **Settings → Secrets and variables → Actions**.

| Secret name | Used for |
|---|---|
| `JWT_SECRET_KEY` | Override the default JWT key in production |
| `MSSQL_PASSWORD` | Override the SA password if you change it |

---

## Troubleshooting

### `Can't open lib 'ODBC Driver 17 for SQL Server': file not found`

The ODBC driver is not installed on this machine.

Ubuntu:

```bash
sudo bash Server/install_odbc.sh
```

Verify:

```bash
odbcinst -q -d
# should list: [ODBC Driver 17 for SQL Server]
```

### `Login timeout expired` / `TCP Provider: Error code 0x2746`

SQL Server is not running or not reachable on port 1433. Start it with Docker:

```bash
docker start mssql-container
# or
docker compose up mssql
```

### `Login failed for user 'sa'`

Either the password is wrong or the SA account is disabled. Check your `.env` file. If using Docker, make sure `SA_PASSWORD` matches.

### `Login returns 401 with correct credentials`

The user doesn't exist. Register first:

```bash
curl -X POST http://localhost:5001/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@1234"}'
```

### `Address already in use` on port 5001 or 5173

```bash
# Linux / macOS
lsof -ti :5001 | xargs kill -9
lsof -ti :5173 | xargs kill -9

# Windows PowerShell
netstat -ano | findstr :5001
Stop-Process -Id <PID> -Force
```

### Port 1433 already in use

Another SQL Server instance is running. Stop it or change the host port mapping in `docker-compose.yml` to e.g. `"1434:1433"` and update `MSSQL_SERVER` accordingly.

---

## Technologies

- [Flask](https://flask.palletsprojects.com/)
- [pyodbc](https://github.com/mkleehammer/pyodbc)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- [Playwright](https://playwright.dev/)
- [Pytest](https://pytest.org/)
- [Newman](https://learning.postman.com/docs/collections/using-newman-cli/)
- [SQL Server 2019](https://www.microsoft.com/en-us/sql-server/)
- [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/)

---

## License

Educational use only.
