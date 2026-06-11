# Newman API Testing

Automated API testing for Flask Book CRUD application using Newman (Postman CLI).

## Quick Start

```bash
# 1. Check dependencies
./check-dependencies.sh

# 2. Install if needed
npm install

# 3. Run tests (ensure Flask API is running on :5000)
npm test
```

## Prerequisites

- **Node.js** 14.0+ and **NPM** 6.0+
- **Python** 3.8+ (for test report generator)
- **Flask API** running on http://127.0.0.1:5000

### Python Dependencies (for comprehensive reporting)
```bash
# Required for test-report-generator.py
pip install pandas jinja2

# Or in virtual environment
source venv/bin/activate
pip install pandas jinja2
```

## Installation

### Automatic Setup
```bash
npm install
./check-dependencies.sh  # Verify installation
```

### Manual Setup
```bash
# Node.js dependencies
npm install newman newman-reporter-htmlextra


## Usage

### Basic Testing
```bash
npm test                    # Runs Newman with standard HTML report
npm run test:enhanced      # Runs Newman with enhanced visual charts & analytics
```

**What these commands actually do:**

- **`npm test`**: Executes `./run-newman-tests.sh` which:
  - Runs all 58 Newman tests from the Postman collection
  - Generates `newman-standard-report.html` (basic HTML report)
  - Creates `newman-result.json` (for automation/CI)
  - Uses 100ms delay between requests and 5s timeout

- **`npm run test:enhanced`**: Executes `./run-newman-tests.sh --enhanced` which:
  - Runs all 58 Newman tests with enhanced reporting
  - Generates `newman-enhanced-report.html` with visual charts and analytics
  - Includes dark theme, test paging, and comprehensive dashboards
  - Creates `newman-result.json` (for automation/CI)
  - Uses 100ms delay between requests and 5s timeout

### Advanced Commands
```bash
# Validate collection syntax
newman run book_api_postman_collection.json --dry-run

# Test specific section
newman run book_api_postman_collection.json \
  --folder "SECTION 1 - Basic Functional Tests"

# Verbose debugging
newman run book_api_postman_collection.json \
  -e postman_environment.json --verbose
```

## Files Structure

```
postman_tests/
├── book_api_postman_collection.json  # Test collection (58 tests)
├── postman_environment.json          # Environment variables
├── package.json                      # NPM dependencies
├── check-dependencies.sh             # Dependency validator
├── newman-report.html               # Generated test report
├── newman-enhanced-report.html      # Enhanced visual report (charts)
├── newman-result.json               # JSON results for automation
└── newman-enhanced-report.html      # Enhanced Newman report (when using --enhanced)

../Flask_CRUD_TestPlan_44TCs.csv      # Formal test plan (44 test cases)
../test-report-generator.py           # TC mapping & coverage analysis tool
```

## Test Coverage

- **Total Tests**: 58 assertions across 33 API requests
- **Endpoints**: GET, POST, PUT, DELETE operations
- **Database**: PostgreSQL on port 5433
- **Report Format**: Enhanced HTML with charts and analytics

### Test Plan Integration

The project includes `test-report-generator.py` which provides **comprehensive test analysis**:

- **Maps Newman tests** to formal test cases from `Flask_CRUD_TestPlan_44TCs.csv`
- **Tracks automation coverage** (which TCs are automated vs manual)
- **Generates comprehensive HTML report** with TC mapping and pass/fail status
- **Analyzes test plan** to identify gaps in automation coverage

**Usage:**
```bash
# Prerequisites: pandas and jinja2 must be installed
# If using virtual environment:
source venv/bin/activate
pip install pandas jinja2  # (if not already installed)

# After running Newman tests, generate comprehensive analysis
python3 test-report-generator.py

# Output: tests/unified_report/comprehensive-test-report.html
```

**Generated Report Features:**
- **TC Mapping**: Links Newman tests to formal test cases (CSV)
- **Coverage Analysis**: Shows automation vs manual test ratio
- **Pass/Fail Status**: Visual dashboard with progress bars  
- **Failed Test Analysis**: Detailed breakdown with TC numbers
- **Professional HTML**: Comprehensive report for stakeholders

**This tool is valuable for:**
- **QA teams** tracking formal test case execution
- **Project managers** monitoring automation coverage  
- **Developers** understanding which TCs need manual testing
- **Compliance** showing test traceability and coverage

**Note**: Requires `Flask_CRUD_TestPlan_44TCs.csv` and Newman JSON results. Works best when test names include TC numbers (e.g., "TC01 - Server Check").

## Troubleshooting

### Common Issues

**Newman not found**
```bash
npm install -g newman  # Global install
# OR
npx newman --version   # Use via NPX
```

**API connection failed**
```bash
curl http://127.0.0.1:5000/health  # Check API status
```

**Permission denied on scripts**
```bash
chmod +x check-dependencies.sh
```

**test-report-generator.py fails**
```bash
# Ensure Python dependencies are installed
source venv/bin/activate  # If using virtual env
pip install pandas jinja2

# Ensure Newman tests have been run first
npm test  # This creates newman-result.json
```

### Support Commands
```bash
./check-dependencies.sh    # System status check
npm run check-deps        # NPM script version
newman --version          # Verify Newman
node --version           # Check Node.js
```

## NPM Scripts

| Command | Description | Output Files |
|---------|-------------|--------------|
| `npm test` | Run 58 Newman tests with standard HTML report | `newman-standard-report.html`, `newman-result.json` |
| `npm run test:enhanced` | Run tests with enhanced charts & analytics | `newman-enhanced-report.html`, `newman-result.json` |
| `npm run check-deps` | Validate all Newman & Python dependencies | Console output with ✅/❌ status |
| `npm run report` | Generate comprehensive TC mapping & coverage analysis | `../unified_report/comprehensive-test-report.html` |

### Complete Testing Workflow

```bash
# 1. Run Newman tests (choose one)
npm test                    # OR npm run test:enhanced

# 2. Generate comprehensive analysis (recommended)
cd .. && python3 test-report-generator.py

# Output reports:
# - newman-standard-report.html (basic Newman results)  
# - newman-enhanced-report.html (visual charts & analytics)
# - ../unified_report/comprehensive-test-report.html (TC mapping & coverage analysis)
```

---

**Note**: Ensure Flask API is running before executing tests. Check API health at http://127.0.0.1:5000/health
