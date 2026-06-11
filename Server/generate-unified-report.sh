#!/usr/bin/env bash
set -euo pipefail

# Resolve to repo root regardless of where script is invoked
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR"
TESTS_DIR="$SERVER_DIR/tests"
UNIFIED_SCRIPT="$TESTS_DIR/unified_report/test-report-generator.py"

if [[ ! -f "$UNIFIED_SCRIPT" ]]; then
	echo "Error: Unified report generator not found at $UNIFIED_SCRIPT" >&2
	exit 1
fi

# Prefer using the workspace Python if available; fallback to python
if [[ -x "$SERVER_DIR/venv/bin/python" ]]; then
	PYTHON_BIN="$SERVER_DIR/venv/bin/python"
else
	PYTHON_BIN=${PYTHON_BIN:-python3}
fi

echo "Generating unified test report..."
"$PYTHON_BIN" "$UNIFIED_SCRIPT"

echo "Done. See output under: $TESTS_DIR/unified_report"
