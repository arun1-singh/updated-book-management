#!/bin/bash
# Enhanced Newman test runner with comprehensive reporting
# Supports both standard and enhanced (htmlextra) reporting modes

echo "🚀 Running Newman API Tests for Book CRUD..."

# Check if collection exists
if [ ! -f "./book_api_postman_collection.json" ]; then
    echo "❌ Error: book_api_postman_collection.json not found"
    exit 1
fi

# Check if environment exists
if [ ! -f "./postman_environment.json" ]; then
    echo "❌ Error: postman_environment.json not found"
    exit 1
fi

# Determine reporting mode
ENHANCED_MODE=false
if [[ "$1" == "--enhanced" ]]; then
    ENHANCED_MODE=true
    echo "📊 Enhanced reporting mode enabled (with charts and detailed analytics)"
else
    echo "📋 Standard reporting mode"
fi

# Always generate JSON for programmatic access
echo "📝 Generating JSON results..."
newman run ./book_api_postman_collection.json \
    -e ./postman_environment.json \
    -r json \
    --reporter-json-export ./newman-result.json \
    --color on \
    --delay-request 100 \
    --timeout-request 5000

# Generate appropriate HTML report based on mode
if [ "$ENHANCED_MODE" = true ]; then
    echo "📊 Generating enhanced HTML report with charts..."
    newman run ./book_api_postman_collection.json \
        -e ./postman_environment.json \
        -r htmlextra \
        --reporter-htmlextra-export ./newman-enhanced-report.html \
        --reporter-htmlextra-darkTheme \
        --reporter-htmlextra-showOnlyFails false \
        --reporter-htmlextra-testPaging true \
        --reporter-htmlextra-browserTitle "📊 Book CRUD API - Test Dashboard" \
        --reporter-htmlextra-title "Book CRUD API - Enhanced Test Results with TC Mapping" \
        --reporter-htmlextra-titleSize 2 \
        --reporter-htmlextra-logs true \
        --reporter-htmlextra-showEnvironmentData true \
        --reporter-htmlextra-skipHeaders "User-Agent,Accept" \
        --reporter-htmlextra-hideRequestBody "false" \
        --reporter-htmlextra-hideResponseBody "false" \
        --reporter-htmlextra-showMarkdownLinks true \
        --delay-request 100 \
        --timeout-request 5000
else
    echo "📄 Generating standard HTML report..."
    newman run ./book_api_postman_collection.json \
        -e ./postman_environment.json \
        -r html \
        --reporter-html-export ./newman-standard-report.html \
        --delay-request 100 \
        --timeout-request 5000
fi

# Check exit code and provide appropriate feedback
echo ""
echo "📋 Test Execution Summary:"
if [ "$ENHANCED_MODE" = true ]; then
    echo "📊 Enhanced report with charts: newman-enhanced-report.html"
    echo "📈 Includes comprehensive analytics and visual summaries"
else
    echo "� Standard report: newman-standard-report.html"
fi
echo "📁 JSON data for automation: newman-result.json"
echo ""
echo "💡 Next steps:"
echo "   1. Run unified report: cd ../.. && ./generate-unified-report.sh"
echo "   2. View comprehensive TC mapping in: tests/unified_report/comprehensive-test-report.html"
echo ""

if [ $? -eq 0 ]; then
    echo "✅ Newman test execution completed"
else
    echo "⚠️  Some tests had failures - check detailed reports for TC-specific issues"
fi