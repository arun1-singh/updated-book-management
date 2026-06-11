import json
import pandas as pd
from jinja2 import Template
from datetime import datetime
import os
import re

# ---------- ENHANCED CONFIGURATION (paths resolved relative to this script) ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.dirname(SCRIPT_DIR)  # .../Server/tests
POSTMAN_DIR = os.path.join(TESTS_DIR, "postman_newman")

# Inputs
newman_json = os.path.join(POSTMAN_DIR, "newman-result.json")
pytest_json = os.path.join(TESTS_DIR, "pytest", "pytest-report.json")
csv_file = os.path.join(TESTS_DIR, "Flask_CRUD_TestPlan_44TCs.csv")

# Output (always generate into unified_report)
OUTPUT_DIR = os.path.join(TESTS_DIR, "unified_report")
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_html = os.path.join(OUTPUT_DIR, "comprehensive-test-report.html")

# ---------- LOAD NEWMAN DATA ----------
print("🔍 Loading Newman results...")
try:
    with open(newman_json, "r", encoding="utf-8") as f:
        newman_data = json.load(f)
    print(f"✅ Newman results loaded")
except FileNotFoundError:
    print(f"❌ Error: {newman_json} not found!")
    print("💡 Run: cd Server/tests/postman_newman && ./run-newman-tests.sh")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON: {e}")
    exit(1)

# ---------- LOAD PYTEST DATA ----------
pytest_data = {"summary": {"passed": 0, "failed": 0, "total": 0}, "tests": []}
print("🔍 Loading Pytest results...")
try:
    with open(pytest_json, "r", encoding="utf-8") as f:
        pytest_raw = json.load(f)
    pytest_data = {
        "summary": pytest_raw.get("summary", {"passed": 0, "failed": 0, "total": 0}),
        "tests": pytest_raw.get("tests", []),
        "duration": pytest_raw.get("duration", 0),
        "exitcode": pytest_raw.get("exitcode", 0)
    }
    print(f"✅ Pytest results loaded: {pytest_data['summary']['total']} tests")
except FileNotFoundError:
    print(f"⚠️ Warning: {pytest_json} not found - pytest data will be empty")
    print("💡 Run: pytest tests/ -v --json-report --json-report-file=tests/pytest/pytest-report.json")
except json.JSONDecodeError as e:
    print(f"⚠️ Warning: Invalid pytest JSON: {e}")

# ---------- EXTRACT ESSENTIAL STATS ----------
stats = newman_data["run"]["stats"]
executions = newman_data["run"]["executions"]
failures = newman_data["run"]["failures"]

# Simple counters
total_requests = len(executions)
total_assertions = stats["assertions"]["total"]
failed_assertions = stats["assertions"]["failed"]
passed_assertions = total_assertions - failed_assertions

# Success rate
success_rate = (passed_assertions / total_assertions * 100) if total_assertions > 0 else 0

# Failed test details with TC mapping
failed_tests = []
for failure in failures:
    source = failure.get("source")
    if isinstance(source, dict):
        test_name = source.get("name", "Unknown Test")
    else:
        test_name = source or "Unknown Test"
    # Try to extract TC number from test name (e.g., "TC01 - Server Start Check")
    tc_match = re.search(r'TC(\d+)', test_name)
    tc_number = tc_match.group(0) if tc_match else "N/A"

    err = failure.get("error", {}) or {}
    assertion = err.get("test") or err.get("name") or "N/A"
    message = err.get("message", "")

    failed_tests.append({
        "tc_number": tc_number,
        "test": test_name,
        "assertion": assertion,
        "message": message
    })

# ---------- ENHANCED TEST PLAN MAPPING ----------
test_plan_data = {"df": None, "coverage_stats": {}}
try:
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        test_plan_data["df"] = df
        
        # Enhanced TC mapping logic
        newman_test_names = [exec["item"]["name"] for exec in executions]
        
        # Add automation status columns
        df["Automation_Status"] = "Not Automated"
        df["Newman_Test_Name"] = ""
        df["Automation_Result"] = ""
        
        automated_count = 0
        manual_required_count = 0
        
        for idx, row in df.iterrows():
            tc_id = str(row["TC No"]).strip().upper()
            
            # Check if marked as manual in CSV
            if str(row.get("Pass/Fail", "")).strip().lower() == "manual":
                df.at[idx, "Automation_Status"] = "Manual Required"
                manual_required_count += 1
                continue
                
            # Try to find matching Newman test
            matched_test = None
            for test_name in newman_test_names:
                if tc_id.lower() in test_name.lower():
                    matched_test = test_name
                    break
            
            if matched_test:
                df.at[idx, "Automation_Status"] = "Automated"
                df.at[idx, "Newman_Test_Name"] = matched_test
                automated_count += 1
                
                # Determine pass/fail status from Newman results
                test_failed = any(
                    failure["source"]["name"] == matched_test 
                    for failure in failures
                )
                df.at[idx, "Automation_Result"] = "❌ Failed" if test_failed else "✅ Passed"
        
        # Calculate coverage statistics
        total_tcs = len(df)
        not_automated = total_tcs - automated_count - manual_required_count
        
        test_plan_data["coverage_stats"] = {
            "total": total_tcs,
            "automated": automated_count,
            "manual_required": manual_required_count,
            "not_automated": not_automated,
            "automation_coverage": (automated_count / total_tcs * 100) if total_tcs > 0 else 0
        }
        
        print(f"📋 Test plan analysis:")
        print(f"   Total test cases: {total_tcs}")
        print(f"   Automated: {automated_count}")
        print(f"   Manual required: {manual_required_count}")
        print(f"   Not automated: {not_automated}")
        print(f"   Coverage: {test_plan_data['coverage_stats']['automation_coverage']:.1f}%")
        
except Exception as e:
    print(f"⚠️  Test plan analysis failed: {e}")
    test_plan_data["coverage_stats"] = {"total": 0, "automated": 0, "manual_required": 0, "not_automated": 0, "automation_coverage": 0}

# ---------- ENHANCED HTML TEMPLATE WITH TC MAPPING ----------
template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Book CRUD API - Comprehensive Test Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
               margin: 40px auto; max-width: 1200px; line-height: 1.6; color: #333; background: #f8f9fa; }
        .container { background: #fff; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px; text-align: center; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: #fff; border: 1px solid #e1e5e9; border-radius: 8px; 
                     padding: 20px; text-align: center; transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .success { border-left: 5px solid #28a745; }
        .error { border-left: 5px solid #dc3545; }
        .warning { border-left: 5px solid #ffc107; }
        .info { border-left: 5px solid #17a2b8; }
        .metric { font-size: 28px; font-weight: 700; margin: 10px 0; }
        .metric.success { color: #28a745; }
        .metric.error { color: #dc3545; }
        .metric.warning { color: #ffc107; }
        .metric.info { color: #17a2b8; }
        .section { margin: 40px 0; }
        .section-title { font-size: 24px; font-weight: 600; margin-bottom: 20px; color: #495057; 
                        border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        .test-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .test-table th, .test-table td { padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        .test-table th { background: #f8f9fa; font-weight: 600; color: #495057; }
        .test-table tbody tr:hover { background: #f8f9fa; }
        .status-automated { background: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .status-manual { background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .status-not-automated { background: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .failure-item { background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px; 
                       padding: 20px; margin: 15px 0; border-left: 5px solid #dc3545; }
        .failure-tc { font-weight: 600; color: #721c24; margin-bottom: 8px; }
        .failure-test { font-weight: 500; margin-bottom: 5px; }
        .failure-assertion { font-style: italic; color: #856404; margin-bottom: 5px; }
        .failure-message { font-size: 14px; color: #6c757d; }
        .timestamp { color: #6c757d; font-size: 14px; }
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #28a745, #20c997); transition: width 0.3s ease; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Book CRUD API - Comprehensive Test Report</h1>
            <p class="timestamp">Generated: {{ timestamp }}</p>
            <p>Complete test analysis with TC mapping and manual test tracking</p>
        </div>

        <div class="section">
            <h2 class="section-title">🎯 Newman Test Execution Summary</h2>
            <div class="stats">
                <div class="stat-card success">
                    <div class="metric success">{{ passed_assertions }}</div>
                    <div><strong>Passed Assertions</strong></div>
                </div>
                <div class="stat-card {{ 'error' if failed_assertions > 0 else 'success' }}">
                    <div class="metric {{ 'error' if failed_assertions > 0 else 'success' }}">{{ failed_assertions }}</div>
                    <div><strong>Failed Assertions</strong></div>
                </div>
                <div class="stat-card info">
                    <div class="metric info">{{ "%.1f"|format(success_rate) }}%</div>
                    <div><strong>Success Rate</strong></div>
                </div>
                <div class="stat-card warning">
                    <div class="metric warning">{{ total_requests }}</div>
                    <div><strong>API Endpoints Tested</strong></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div><strong>Test Execution Progress:</strong></div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ "%.1f"|format(success_rate) }}%;"></div>
                </div>
                <small style="color: #6c757d;">{{ passed_assertions }}/{{ total_assertions }} assertions passed</small>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🧪 Pytest Unit Test Summary</h2>
            <div class="stats">
                <div class="stat-card success">
                    <div class="metric success">{{ pytest_summary.passed }}</div>
                    <div><strong>Passed Tests</strong></div>
                </div>
                <div class="stat-card {{ 'error' if pytest_summary.failed > 0 else 'success' }}">
                    <div class="metric {{ 'error' if pytest_summary.failed > 0 else 'success' }}">{{ pytest_summary.failed }}</div>
                    <div><strong>Failed Tests</strong></div>
                </div>
                <div class="stat-card info">
                    <div class="metric info">{{ "%.1f"|format(pytest_success_rate) }}%</div>
                    <div><strong>Unit Test Success Rate</strong></div>
                </div>
                <div class="stat-card warning">
                    <div class="metric warning">{{ pytest_summary.total }}</div>
                    <div><strong>Total Unit Tests</strong></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div><strong>Unit Test Execution Progress:</strong></div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ "%.1f"|format(pytest_success_rate) }}%;"></div>
                </div>
                <small style="color: #6c757d;">{{ pytest_summary.passed }}/{{ pytest_summary.total }} unit tests passed</small>
            </div>
        </div>

        {% if coverage_stats.total > 0 %}
        <div class="section">
            <h2 class="section-title">📋 Test Plan Coverage Analysis</h2>
            <div class="stats">
                <div class="stat-card success">
                    <div class="metric success">{{ coverage_stats.automated }}</div>
                    <div><strong>Automated TCs</strong></div>
                </div>
                <div class="stat-card warning">
                    <div class="metric warning">{{ coverage_stats.manual_required }}</div>
                    <div><strong>Manual Required</strong></div>
                </div>
                <div class="stat-card error">
                    <div class="metric error">{{ coverage_stats.not_automated }}</div>
                    <div><strong>Not Automated</strong></div>
                </div>
                <div class="stat-card info">
                    <div class="metric info">{{ "%.1f"|format(coverage_stats.automation_coverage) }}%</div>
                    <div><strong>Automation Coverage</strong></div>
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <div><strong>Automation Coverage Progress:</strong></div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ "%.1f"|format(coverage_stats.automation_coverage) }}%;"></div>
                </div>
                <small style="color: #6c757d;">{{ coverage_stats.automated }}/{{ coverage_stats.total }} test cases automated</small>
            </div>
        </div>

        {% if test_plan_df is not none %}
        <div class="section">
            <h2 class="section-title">📝 Detailed Test Case Status</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>TC No</th>
                        <th>Category</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Automation Result</th>
                        <th>Newman Test</th>
                    </tr>
                </thead>
                <tbody>
                    {% for _, row in test_plan_df.iterrows() %}
                    <tr>
                        <td><strong>{{ row["TC No"] }}</strong></td>
                        <td>{{ row["Category"] }}</td>
                        <td>{{ row["Description"] }}</td>
                        <td>
                            {% if row["Automation_Status"] == "Automated" %}
                                <span class="status-automated">✅ Automated</span>
                            {% elif row["Automation_Status"] == "Manual Required" %}
                                <span class="status-manual">⚠️ Manual Required</span>
                            {% else %}
                                <span class="status-not-automated">❌ Not Automated</span>
                            {% endif %}
                        </td>
                        <td>{{ row["Automation_Result"] }}</td>
                        <td><small>{{ row["Newman_Test_Name"] }}</small></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        {% endif %}

        {% if failed_tests %}
        <div class="section">
            <h2 class="section-title">❌ Failed Test Details</h2>
            {% for failure in failed_tests %}
            <div class="failure-item">
                <div class="failure-tc"><strong>{{ failure.tc_number }}</strong> - Test Case</div>
                <div class="failure-test">{{ failure.test }}</div>
                <div class="failure-assertion"><em>Assertion:</em> {{ failure.assertion }}</div>
                <div class="failure-message"><em>Error:</em> {{ failure.message }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if failed_assertions == 0 %}
        <div class="section">
            <div class="stat-card success" style="text-align: center; padding: 30px;">
                <h2 style="color: #28a745; margin-bottom: 15px;">🎉 All Automated Tests Passed!</h2>
                <p>Your Book CRUD API automated tests are working correctly.</p>
                {% if coverage_stats.manual_required > 0 %}
                <p><small><strong>Note:</strong> {{ coverage_stats.manual_required }} test cases require manual execution.</small></p>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <div class="section" style="text-align: center; margin-top: 50px; padding-top: 30px; border-top: 1px solid #dee2e6;">
            <p style="color: #6c757d; font-size: 14px; margin: 0;">
                <em>Comprehensive report generated by test-report-generator.py</em><br>
                <small>Newman {{ total_assertions }} assertions | {{ coverage_stats.total }} total test cases | Generated {{ timestamp }}</small>
            </p>
        </div>
    </div>
</body>
</html>
""")

# ---------- CALCULATE PYTEST METRICS ----------
pytest_success_rate = (pytest_data["summary"]["passed"] / pytest_data["summary"]["total"] * 100) if pytest_data["summary"]["total"] > 0 else 0

# ---------- GENERATE ENHANCED REPORT ----------
html = template.render(
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    total_requests=total_requests,
    total_assertions=total_assertions,
    passed_assertions=passed_assertions,
    failed_assertions=failed_assertions,
    success_rate=success_rate,
    failed_tests=failed_tests,
    coverage_stats=test_plan_data["coverage_stats"],
    test_plan_df=test_plan_data["df"],
    newman_data=newman_data,
    pytest_summary=pytest_data["summary"],
    pytest_success_rate=pytest_success_rate,
    pytest_tests=pytest_data["tests"]
)

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html)

# ---------- SUMMARY ----------
print(f"\n✅ COMPREHENSIVE TEST REPORT GENERATED!")
print(f"📊 Main Report: {output_html}")
print(f"📈 Enhanced Report: {os.path.join(POSTMAN_DIR, 'newman-enhanced-report.html')} (if generated)")
print(f"🔗 Open: file://{os.path.abspath(output_html)}")
print(f"\n📈 RESULTS:")
print(f"   Newman API Tests: {passed_assertions}/{total_assertions} passed ({success_rate:.1f}%)")
print(f"   API Endpoints Tested: {total_requests}")
if pytest_data["summary"]["total"] > 0:
    print(f"   Pytest Unit Tests: {pytest_data['summary']['passed']}/{pytest_data['summary']['total']} passed ({pytest_success_rate:.1f}%)")
if test_plan_data["coverage_stats"]["total"] > 0:
    stats = test_plan_data["coverage_stats"]
    print(f"   Test Plan Coverage: {stats['automated']}/{stats['total']} automated ({stats['automation_coverage']:.1f}%)")
    print(f"   Manual Tests Required: {stats['manual_required']}")

if failed_assertions > 0:
    print(f"\n⚠️  {failed_assertions} Newman assertions failed - check the comprehensive report!")
    print(f"📊 Enhanced htmlextra report available: newman-enhanced-report.html")
else:
    print(f"\n🎉 All automated tests passed! Your CRUD API is working correctly.")
    if test_plan_data["coverage_stats"]["manual_required"] > 0:
        print(f"💡 Note: {test_plan_data['coverage_stats']['manual_required']} test cases still require manual execution.")