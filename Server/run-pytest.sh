#!/usr/bin/env bash
set -euo pipefail

# Run pytest and generate JSON report in the correct location
echo "🧪 Running Pytest unit tests..."

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest not found"
    echo "💡 Install with: pip install pytest pytest-json-report"
    exit 1
fi

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$SCRIPT_DIR/tests"
PYTEST_OUTPUT="$TESTS_DIR/pytest/pytest-report.json"

# Ensure output directory exists
mkdir -p "$(dirname "$PYTEST_OUTPUT")"

# Run pytest with JSON report
echo "📝 Generating pytest report to: $PYTEST_OUTPUT"
cd "$SCRIPT_DIR"

pytest tests/pytest/ -v \
    --json-report \
    --json-report-file="$PYTEST_OUTPUT" \
    --tb=short

echo "✅ Pytest execution completed"
echo "📊 Report saved to: $PYTEST_OUTPUT"
echo ""
echo "💡 Next steps:"
echo "   Generate unified report: bash generate-unified-report.sh"