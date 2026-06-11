#!/bin/bash
# Dependency checker for Newman API testing setup
# Run this script to verify all dependencies are properly installed

echo "🔍 Newman API Testing - Dependency Checker"
echo "=============================================="
echo ""

# Initialize status tracking
ALL_GOOD=true

# Check Node.js
echo "📋 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
    
    # Check if version is 14+
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$MAJOR_VERSION" -ge 14 ]; then
        echo "✅ Node.js version is compatible (14.0+)"
    else
        echo "⚠️  Node.js version should be 14.0+ (current: $NODE_VERSION)"
        ALL_GOOD=false
    fi
else
    echo "❌ Node.js not found"
    echo "   Install from: https://nodejs.org/"
    ALL_GOOD=false
fi

echo ""

# Check NPM
echo "📋 Checking NPM..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ NPM installed: $NPM_VERSION"
else
    echo "❌ NPM not found (usually comes with Node.js)"
    ALL_GOOD=false
fi

echo ""

# Check Newman
echo "📋 Checking Newman..."
if command -v newman &> /dev/null; then
    NEWMAN_VERSION=$(newman --version)
    echo "✅ Newman installed: $NEWMAN_VERSION"
else
    echo "❌ Newman not found"
    echo "   Run: npm install (local) or npm install -g newman (global)"
    ALL_GOOD=false
fi

echo ""

# Check HTMLExtra Reporter
echo "📋 Checking HTMLExtra Reporter..."
if [ -d "node_modules/newman-reporter-htmlextra" ]; then
    echo "✅ HTMLExtra reporter available (local installation)"
elif command -v newman-reporter-htmlextra &> /dev/null; then
    echo "✅ HTMLExtra reporter available (global installation)"
elif npm list newman-reporter-htmlextra &> /dev/null; then
    echo "✅ HTMLExtra reporter available (npm package)"
else
    echo "❌ HTMLExtra reporter not found"
    echo "   Run: npm install (local) or npm install -g newman-reporter-htmlextra (global)"
    ALL_GOOD=false
fi

echo ""

# Check Python
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python installed: $PYTHON_VERSION"
else
    echo "❌ Python3 not found"
    ALL_GOOD=false
fi

echo ""

# Check Python Dependencies
echo "📋 Checking Python Dependencies..."
if python3 -c "import pandas" 2>/dev/null; then
    PANDAS_VERSION=$(python3 -c "import pandas; print(pandas.__version__)" 2>/dev/null)
    echo "✅ Pandas installed: $PANDAS_VERSION"
else
    echo "❌ Pandas not found"
    echo "   Run: pip install pandas"
    ALL_GOOD=false
fi

if python3 -c "import jinja2" 2>/dev/null; then
    JINJA2_VERSION=$(python3 -c "import jinja2; print(jinja2.__version__)" 2>/dev/null)
    echo "✅ Jinja2 installed: $JINJA2_VERSION"
else
    echo "❌ Jinja2 not found"
    echo "   Run: pip install jinja2"
    ALL_GOOD=false
fi

echo ""

# Check if package.json exists
echo "📋 Checking Project Setup..."
if [ -f "package.json" ]; then
    echo "✅ package.json found"
else
    echo "❌ package.json not found"
    echo "   Make sure you're in the postman_tests directory"
    ALL_GOOD=false
fi

if [ -f "book_api_postman_collection.json" ]; then
    echo "✅ Postman collection found"
else
    echo "❌ Postman collection not found"
    echo "   Make sure book_api_postman_collection.json exists"
    ALL_GOOD=false
fi

if [ -f "postman_environment.json" ]; then
    echo "✅ Postman environment found"
else
    echo "❌ Postman environment not found"
    echo "   Make sure postman_environment.json exists"
    ALL_GOOD=false
fi

echo ""
echo "=============================================="

# Final status
if [ "$ALL_GOOD" = true ]; then
    echo "🎉 All dependencies are properly installed!"
    echo "✅ You're ready to run Newman API tests"
    echo ""
    echo "Next steps:"
    echo "1. Start Flask API: cd .. && source venv/bin/activate && python3 app.py"
    echo "2. Run tests: ./run-newman-tests.sh --enhanced"
    echo "3. Generate report: cd ../.. && bash generate-unified-report.sh"
else
    echo "❌ Some dependencies are missing"
    echo "🔧 Please install the missing components listed above"
    echo ""
    echo "Quick fix commands:"
    echo "npm install                    # Install Newman dependencies"
    echo "pip install pandas jinja2      # Install Python dependencies"
fi

echo ""