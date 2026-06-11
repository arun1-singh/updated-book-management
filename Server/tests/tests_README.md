## Structure of tests

```
CRUD_app_Flask/
├── Client/                         # Frontend React application
└── Server/
    ├── app.py                      # 🚀 Main Flask CRUD API application
    ├── requirements.txt            # 📦 Python dependencies
    ├── pytest.ini                 # ⚙️  Pytest configuration
    ├── generate-unified-report.sh  # 🎯 Main test report generator (entry point)
    ├── run-pytest.sh              # 🧪 Pytest runner helper script
    ├── setup_database.sql          # 🗄️  Database schema setup
    ├── venv/                       # 🐍 Python virtual environment
    └── tests/
        ├── Flask_CRUD_TestPlan_44TCs.csv    # 📋 Formal test plan (44 test cases)
        ├── pytest/                          # 🧪 Unit & Integration Tests
        │   ├── conftest.py                  #     Pytest fixtures & configuration
        │   ├── test_books_api.py           #     Main API test suite (14 tests)
        │   └── pytest-report.json          #     Generated pytest results
        ├── postman_newman/                  # 📡 API Testing with Newman
        │   ├── book_api_postman_collection.json  # Postman collection (58 tests)
        │   ├── postman_environment.json          # Environment variables
        │   ├── package.json                      # NPM dependencies
        │   ├── run-newman-tests.sh               # Newman test runner
        │   ├── check-dependencies.sh             # Dependency validator
        │   ├── newman-result.json                # Generated Newman results
        │   ├── newman-enhanced-report.html       # Visual test report
        │   └── README.md                         # Newman testing guide
        └── unified_report/                  # 📊 Comprehensive Reporting
            ├── test-report-generator.py          # Enhanced report generator
            └── comprehensive-test-report.html    # Final unified report
```

## Server Folder Files Brief

### Core Application
- **`app.py`** - Main Flask CRUD API with Book management endpoints
- **`requirements.txt`** - Python dependencies (Flask, PostgreSQL, etc.)
- **`setup_database.sql`** - Database schema and table creation scripts

### Testing Infrastructure  
- **`pytest.ini`** - Pytest configuration with test markers
- **`run-pytest.sh`** - Helper script to run pytest with JSON reporting
- **`generate-unified-report.sh`** - Main entry point for comprehensive test reports

### Virtual Environment
- **`venv/`** - Python virtual environment with all dependencies installed

## Quick Test Commands

### 🧪 Run Pytest Unit Tests
```bash
# Method 1: Using helper script (recommended)
bash run-pytest.sh

# Method 2: Direct pytest command  
pytest tests/pytest/ -v --json-report --json-report-file=tests/pytest/pytest-report.json

# Results: tests/pytest/pytest-report.json (14 unit tests)
```

### 📡 Run Newman API Tests  
```bash
# Navigate to postman_newman directory
cd tests/postman_newman

# Method 1: Standard HTML report
npm test
# or: ./run-newman-tests.sh

# Method 2: Enhanced visual report (recommended)
npm run test:enhanced  
# or: ./run-newman-tests.sh --enhanced

# Results: newman-result.json + newman-enhanced-report.html (58 API tests)
```

### 📊 Generate Unified Report (Both Tests Combined)
```bash
# From Server directory - combines pytest + newman results
bash generate-unified-report.sh

# Output: tests/unified_report/comprehensive-test-report.html
# Features: TC mapping, coverage analysis, visual metrics
```

### ⚡ Complete Test Workflow
```bash
# 1. Run all tests and generate comprehensive report
bash run-pytest.sh                              # Unit tests
cd tests/postman_newman && npm run test:enhanced # API tests  
cd ../.. && bash generate-unified-report.sh     # Unified report

# 2. View results
# - Pytest: tests/pytest/pytest-report.json
# - Newman: tests/postman_newman/newman-enhanced-report.html  
# - Unified: tests/unified_report/comprehensive-test-report.html
```

## Test Coverage Summary
- **📊 Newman API Tests**: 58 assertions across 33 endpoints
- **🧪 Pytest Unit Tests**: 14 tests covering CRUD operations  
- **📋 Test Plan**: 44 formal test cases with automation mapping
- **📈 Reports**: Individual + unified reporting with TC coverage analysis