# Flask CRUD App with SQLite and React

## Description

This is a simple full-stack **Book Management CRUD application**.

It has:

- A **React frontend** for the browser UI
- A **Flask backend** for REST API endpoints
- A **SQLite database** for storing book records

The app allows users to:

- View all books
- Add a new book
- Update an existing book
- Delete a book

CRUD means:

| Operation | Meaning |
|---|---|
| Create | Add a new record |
| Read | View records |
| Update | Edit an existing record |
| Delete | Remove a record |

## Project Structure

```text
simple_book_management_may_2026/
|-- Client/                         # React frontend
|   |-- public/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- Books.jsx
|   |   |-- CreateBook.jsx
|   |   |-- UpdateBook.jsx
|   |   |-- Nav.jsx
|   |   |-- main.jsx
|   |-- package.json
|   |-- vite.config.js
|   |-- playwright.config.js
|
|-- Server/                         # Flask + SQLite backend
|   |-- app.py
|   |-- books.db                    # SQLite database file, created after running app
|   |-- requirements.txt
|   |-- setup_database.sql
|   |-- run-pytest.sh
|   |-- tests/
|
|-- README.md
```

## How The App Works

```text
Browser user
    |
    v
React frontend on http://localhost:5173
    |
    v
Axios sends HTTP requests
    |
    v
Flask backend on http://localhost:5001
    |
    v
SQLite database file: Server/books.db
```

Example:

1. User clicks **Create** in the React app.
2. React sends a `POST /create` request to Flask.
3. Flask inserts the book into SQLite.
4. Flask returns JSON.
5. React navigates back to the book list.

## Prerequisites

Install these first:

- Python 3.8 or newer
- Node.js 16 or newer
- pip
- npm
- Git Bash or WSL on Windows if you want to run `.sh` scripts

SQLite does not need a separate server installation because Python includes SQLite support.

Optional monitoring tools:

- **Wireshark** for watching HTTP traffic on Windows
- **tcpdump** for watching HTTP traffic on Linux
- **DB Browser for SQLite** for opening and checking `books.db`

## Backend Setup On Windows

Open PowerShell from the project root.

```powershell
cd Server
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

The backend starts at:

```text
http://localhost:5001
```

Health check:

```powershell
curl http://localhost:5001/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

If PowerShell blocks virtual environment activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

## Backend Setup On Linux

Open a terminal from the project root.

```bash
cd Server
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

The backend starts at:

```text
http://localhost:5001
```

Health check:

```bash
curl http://localhost:5001/health
```

## Frontend Setup On Windows

Open another PowerShell terminal from the project root.

```powershell
cd Client
npm install
npm run dev
```

The frontend starts at:

```text
http://localhost:5173
```

Open this URL in the browser:

```text
http://localhost:5173
```

## Frontend Setup On Linux

Open another terminal from the project root.

```bash
cd Client
npm install
npm run dev
```

The frontend starts at:

```text
http://localhost:5173
```

Open this URL in the browser:

```text
http://localhost:5173
```

## Running The Full App

You need two terminals.

Terminal 1:

```bash
cd Server
python app.py
```

Terminal 2:

```bash
cd Client
npm run dev
```

Then open:

```text
http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Retrieve all books |
| `POST` | `/create` | Create a new book |
| `PUT` | `/update/<id>` | Update a book by ID |
| `DELETE` | `/delete/<id>` | Delete a book by ID |
| `GET` | `/health` | Check backend health |

## Example API Requests

### Get All Books

```http
GET http://localhost:5001/
```

### Create A Book

```http
POST http://localhost:5001/create
Content-Type: application/json

{
  "publisher": "O'Reilly",
  "name": "Learning Flask",
  "date": "2024-10-11",
  "cost": 399.99
}
```

### Update A Book

```http
PUT http://localhost:5001/update/1
Content-Type: application/json

{
  "publisher": "Updated Publisher",
  "name": "Updated Book Name",
  "date": "2024-12-01",
  "cost": 499.99
}
```

### Delete A Book

```http
DELETE http://localhost:5001/delete/1
```

Note: The app uses lowercase `cost` in the React frontend, Flask API JSON, and SQLite schema.

## Inspecting The SQLite Database With DB Browser

Use **DB Browser for SQLite** when you want to see the database records directly.

### Install DB Browser

Windows:

1. Download DB Browser for SQLite from `https://sqlitebrowser.org/`.
2. Install and open it.

Linux:

```bash
sudo apt update
sudo apt install sqlitebrowser
```

### Open The App Database

1. Run the Flask backend once so `books.db` is created.
2. Open DB Browser for SQLite.
3. Click **Open Database**.
4. Select:

```text
Server/books.db
```

5. Go to the **Browse Data** tab.
6. Select the `book` table.

You can now monitor records while using the React app.

### What To Check

After creating a book in the UI, check that a new row appears in the `book` table.

After updating a book, check that the row values changed.

After deleting a book, check that the row is removed.

Important: If the Flask server is running and DB Browser also has the database open, avoid manually editing rows at the same time unless you understand SQLite locking.

## Monitoring App Traffic

Use **Wireshark on Windows** or **tcpdump on Linux** to see traffic between React and Flask.

The important backend port is:

```text
5001
```

The frontend port is:

```text
5173
```

Most API traffic to inspect is on port `5001`.

### Install Wireshark On Windows

1. Download Wireshark from `https://www.wireshark.org/`.
2. Install it.
3. During installation, install **Npcap**.
4. Enable loopback capture support if the installer asks.

### Capture Traffic On Windows

1. Start Flask backend on port `5001`.
2. Start React frontend on port `5173`.
3. Open Wireshark.
4. Select the loopback adapter. It may be named:

```text
Adapter for loopback traffic capture
```

or something similar from Npcap.

5. Start capture.
6. Use this display filter:

```text
http and tcp.port == 5001 and (http.request.method or http.response.code or json)
```

7. In the React app, create, update, delete, or refresh books.
8. Watch requests going to the Flask API.

Useful filters:

```text
tcp.port == 5001
http
http.request
http.response
```

### Install tcpdump On Linux

```bash
sudo apt update
sudo apt install tcpdump
```

### Capture Traffic On Linux With tcpdump

1. Start Flask backend on port `5001`.
2. Start React frontend on port `5173`.
3. In another terminal, capture loopback traffic on port `5001`:

```bash
sudo tcpdump -i lo port 5001
```

4. Use the React app in the browser: view, create, update, or delete books.
5. Watch the terminal output for traffic between the frontend and backend.

For more readable output with packet contents, use:

```bash
sudo tcpdump -i lo -A port 5001
```

To capture both frontend and backend development ports:

```bash
sudo tcpdump -i lo 'port 5001 or port 5173'
```

To save traffic to a file for later analysis:

```bash
sudo tcpdump -i lo port 5001 -w flask-traffic.pcap
```

Then you can open `flask-traffic.pcap` later in Wireshark if needed.

Useful tcpdump options:

```text
-i lo       Capture on Linux loopback interface
port 5001   Capture Flask backend traffic
-A          Print packet contents as ASCII
-w file     Save capture to a file
```

### What You Should See

When viewing books:

```text
GET /
```

When creating a book:

```text
POST /create
```

When updating a book:

```text
PUT /update/<id>
```

When deleting a book:

```text
DELETE /delete/<id>
```

If the traffic tool does not show clear HTTP details, it may still show TCP packets. Localhost traffic can behave differently depending on OS, browser, and adapter selection.

## Running Pytest Backend Tests

Pytest tests are in:

```text
Server/tests/pytest/
```

### Windows PowerShell

From the project root:

```powershell
cd Server
.\venv\Scripts\Activate.ps1
python -m pytest tests/pytest/ -v
```

To generate the JSON report:

```powershell
python -m pytest tests/pytest/ -v --json-report --json-report-file=tests/pytest/pytest-report.json
```

### Linux

From the project root:

```bash
cd Server
source venv/bin/activate
python -m pytest tests/pytest/ -v
```

Or use the helper script:

```bash
cd Server
bash run-pytest.sh
```

Pytest report output:

```text
Server/tests/pytest/pytest-report.json
```

Note: Some tests may fail if the current Flask implementation does not match the stronger validation behavior expected by the tests.

## Running Playwright Frontend Tests

Playwright tests are in:

```text
Client/tests/
```

The Playwright config starts the React dev server automatically, but the Flask backend should be running separately because the UI calls the backend API.

### First-Time Playwright Setup

Windows or Linux:

```bash
cd Client
npm install
npx playwright install
```

### Run Playwright Tests On Windows

Terminal 1:

```powershell
cd Server
.\venv\Scripts\Activate.ps1
python app.py
```

Terminal 2:

```powershell
cd Client
npm test
```

Alternative:

```powershell
npx playwright test
```

### Run Playwright Tests On Linux

Terminal 1:

```bash
cd Server
source venv/bin/activate
python app.py
```

Terminal 2:

```bash
cd Client
npm test
```

Alternative:

```bash
npx playwright test
```

### Useful Playwright Commands

```bash
npm run test
npm run test:headed
npm run test:debug
npm run test:ui
npm run test:report
```

Playwright HTML report:

```text
Client/playwright-report/index.html
```

## Running Newman API Tests

Newman tests are in:

```text
Server/tests/postman_newman/
```

Install dependencies:

```bash
cd Server/tests/postman_newman
npm install
```

Run tests:

```bash
npm test
```

Run enhanced report:

```bash
npm run test:enhanced
```

Important: Check `postman_environment.json` before running Newman. If it points to `http://127.0.0.1:5000`, update or override it to match the current Flask backend port:

```text
http://127.0.0.1:5001
```

## Test Reports

| Tool | Report Location |
|---|---|
| Pytest | `Server/tests/pytest/pytest-report.json` |
| Newman | `Server/tests/postman_newman/newman-result.json` |
| Newman HTML | `Server/tests/postman_newman/newman-standard-report.html` or `newman-enhanced-report.html` |
| Playwright | `Client/playwright-report/index.html` |
| Unified Report | `Server/tests/unified_report/comprehensive-test-report.html` |

Generate unified report after Pytest and Newman have run:

```bash
cd Server
bash generate-unified-report.sh
```

## Technologies Used

### Backend

- **Flask**: Python web framework
- **Flask-CORS**: Allows frontend and backend to communicate across ports
- **SQLite**: File-based database
- **Pytest**: Backend test framework

### Frontend

- **React**: UI library
- **Vite**: React development/build tool
- **Axios**: HTTP client for API calls
- **Bootstrap**: Styling framework
- **Playwright**: Browser automation testing

### API Testing And Monitoring

- **Postman/Newman**: API test automation
- **Wireshark**: Network traffic inspection on Windows
- **tcpdump**: Network traffic inspection on Linux
- **DB Browser for SQLite**: Database inspection

## Troubleshooting

### Backend Will Not Start

Make sure the virtual environment is activated and dependencies are installed.

Windows:

```powershell
cd Server
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Linux:

```bash
cd Server
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend Cannot Connect To Backend

Check:

- Flask is running on `http://localhost:5001`
- React is running on `http://localhost:5173`
- CORS is enabled in Flask
- Browser console does not show network errors

### Port Already In Use

Windows:

```powershell
netstat -ano | findstr :5001
netstat -ano | findstr :5173
```

Linux:

```bash
lsof -i :5001
lsof -i :5173
```

### Recreate Python Virtual Environment

Windows PowerShell:

```powershell
cd Server
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux:

```bash
cd Server
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Reinstall Frontend Dependencies

```bash
cd Client
npm install
```

## Quick Explanation For Presentation

This project is a full-stack CRUD Book Management System. The React frontend runs on port `5173` and provides the user interface. It uses Axios to send HTTP requests to the Flask backend on port `5001`. Flask performs create, read, update, and delete operations on a SQLite database file called `books.db`. The project also includes Pytest tests for backend APIs, Playwright tests for frontend flows, Newman tests for API scenarios, Wireshark steps for Windows traffic monitoring, tcpdump steps for Linux traffic monitoring, and DB Browser steps for inspecting database records.

## License

This project is for educational purposes.
