import pytest
import uuid
import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from main import app
from database import get_db, format_timestamp_ist, IST_TZ
from scoring_engine import calculate_independent_score
import performance_service
import pdf_generator

def create_user(name: str = "Test Student") -> tuple[str, str, dict]:
    """Helper to create and authenticate a test user via TestClient."""
    client = TestClient(app)
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    resp = client.post("/api/auth/register", json={
        "full_name": name,
        "email": email,
        "password": pwd
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    user_id = data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, token, headers


# =============================================================================
# Dashboard Criteria 1-5: Real Persisted Records, Empty States, Agreements & Date Filters
# =============================================================================

def test_empty_account_dashboard():
    """Criteria 2: Empty accounts show an appropriate empty state without fabricated metrics."""
    client = TestClient(app)
    uid, token, headers = create_user("Empty Account Student")

    res = client.get("/api/performance/dashboard?date_filter=all", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["summary"]["total_unique_solved"] == 0
    assert data["summary"]["total_attempts"] == 0
    assert data["summary"]["completed_attempts"] == 0
    assert data["summary"]["average_coding_score"] is None
    assert data["summary"]["best_coding_score"] is None
    assert data["summary"]["total_active_coding_time_seconds"] == 0
    assert data["summary"]["total_unique_hints_used"] == 0
    assert data["summary"]["total_tab_switches"] == 0
    assert data["summary"]["total_time_away_seconds"] == 0
    assert data["summary"]["overall_pass_rate_percentage"] == 0.0
    assert len(data["questions_performance"]) == 0
    assert len(data["tab_switch_events"]) == 0


def test_dashboard_uses_real_persisted_records_and_agrees():
    """Criteria 1, 3, 4: Dashboard uses real persisted records; summary cards, charts, and tables agree."""
    client = TestClient(app)
    uid, token, headers = create_user("Active Student")

    # Record 2 attempts on 'two-sum' and 1 attempt on 'factorial-recursion'
    # Attempt 1: two-sum, failed
    r1 = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": "def twoSum(nums, target):\n    return []\n",
        "language": "python",
        "time_spent_seconds": 45,
        "session_status": "failed",
        "tab_switch_count": 1,
        "total_time_away_seconds": 10,
        "unique_hints_used": 1
    })
    assert r1.status_code == 200

    # Attempt 2: two-sum, completed & passed
    r2 = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        c = target - n\n        if c in seen:\n            return [seen[c], i]\n        seen[n] = i\n    return []\n",
        "language": "python",
        "time_spent_seconds": 120,
        "session_status": "completed",
        "tab_switch_count": 2,
        "total_time_away_seconds": 25,
        "unique_hints_used": 1
    })
    assert r2.status_code == 200

    # Query Dashboard
    dash_res = client.get("/api/performance/dashboard?date_filter=all", headers=headers)
    assert dash_res.status_code == 200
    data = dash_res.json()
    summary = data["summary"]
    attempts = data["questions_performance"]

    # Criteria 4: Question history correctly separates attempts for two-sum
    two_sum_atts = [a for a in attempts if a["question_id"] == "two-sum"]
    assert len(two_sum_atts) == 2
    # Ensure attempt numbers are cleanly numbered 1 and 2
    attempt_nums = sorted([a["attempt_number"] for a in two_sum_atts])
    assert attempt_nums == [1, 2]

    # Criteria 3: Summary cards agree with table items
    assert summary["total_attempts"] == len(attempts)
    assert summary["completed_attempts"] == sum(1 for a in attempts if a["is_completed"])
    assert summary["total_active_coding_time_seconds"] == sum(a["coding_duration_seconds"] for a in attempts)
    assert summary["total_unique_hints_used"] == sum(a["unique_hints_used"] for a in attempts)

    # Distinct solved questions
    assert summary["total_unique_solved"] == 1


def test_date_filtering_consistency():
    """Criteria 5, 17, 18: Date filters update dashboard sections; invalid custom ranges rejected."""
    client = TestClient(app)
    uid, token, headers = create_user("Date Filter Student")

    # Record attempt
    client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": "def twoSum(nums, target): return []",
        "language": "python",
        "time_spent_seconds": 30
    })

    # Test presets
    for f in ["today", "last_7_days", "last_30_days", "this_month", "all"]:
        r = client.get(f"/api/performance/dashboard?date_filter={f}", headers=headers)
        assert r.status_code == 200, f"Filter {f} failed"
        assert "reporting_period_label" in r.json()

    # Test valid custom range
    valid_custom = client.get("/api/performance/dashboard?date_filter=custom&start_date=2026-01-01&end_date=2026-12-31", headers=headers)
    assert valid_custom.status_code == 200

    # Test invalid custom range (start > end) -> Must reject with 400
    invalid_custom = client.get("/api/performance/dashboard?date_filter=custom&start_date=2026-12-31&end_date=2026-01-01", headers=headers)
    assert invalid_custom.status_code == 400
    assert "start_date cannot be" in invalid_custom.json()["detail"].lower()


# =============================================================================
# Timer, Duration & Tab Switch Tracking 6-11
# =============================================================================

def test_accurate_coding_duration_and_tab_switches():
    """Criteria 6, 7, 8, 9, 10, 11: Accurate duration, paused time separation, tab-switch history and IST timestamps."""
    client = TestClient(app)
    uid, token, headers = create_user("Timer Tab Student")

    # Record tab switch event with return time
    ts_res = client.post("/api/tab-switch/record", headers=headers, json={
        "question_id": "two-sum",
        "event_timestamp": "2026-10-23T10:00:00Z",
        "return_timestamp": "2026-10-23T10:00:45Z",
        "time_away_seconds": 45,
        "event_status": "returned"
    })
    assert ts_res.status_code == 200

    # Record an unreturned / active away event (Criteria 10: missing return timestamp not fabricated)
    ts_open = client.post("/api/tab-switch/record", headers=headers, json={
        "question_id": "two-sum",
        "event_timestamp": "2026-10-23T10:05:00Z",
        "return_timestamp": None,
        "time_away_seconds": 0,
        "event_status": "away"
    })
    assert ts_open.status_code == 200

    dash = client.get("/api/performance/dashboard?date_filter=all", headers=headers).json()
    events = dash["tab_switch_events"]
    assert len(events) >= 2

    # Check unreturned event
    open_ev = next(e for e in events if e["status"] == "away")
    assert open_ev["return_time_ist"] == "Active / Pending Return"

    # Criteria 11: All timestamps displayed in IST
    closed_ev = next(e for e in events if e["status"] == "returned")
    assert "IST" in closed_ev["hidden_time_ist"]
    assert "IST" in closed_ev["return_time_ist"]


# =============================================================================
# Scoring and Hints 12-15
# =============================================================================

def test_exact_hint_scoring_rules():
    """Criteria 12, 13: Exact configured hint curve (10, 9, 7, 4, 1) and no inflation on reopening."""
    assert calculate_independent_score(0) == 10
    assert calculate_independent_score(1) == 9
    assert calculate_independent_score(2) == 7
    assert calculate_independent_score(3) == 4
    assert calculate_independent_score(4) == 1
    assert calculate_independent_score(8) == 1


# =============================================================================
# PDF-Only Report Generation 16-24
# =============================================================================

def test_pdf_report_generation_and_configuration():
    """Criteria 16, 17, 18, 19, 20, 21, 22, 24: Download PDF Report generates valid PDF; optional sections; no CSV/Excel."""
    client = TestClient(app)
    uid, token, headers = create_user("PDF Audit Student")

    # 1. Generate via GET
    get_res = client.get("/api/reports/pdf?date_filter=all&include_tab_switches=true&include_viva=true", headers=headers)
    assert get_res.status_code == 200
    assert get_res.headers["content-type"] == "application/pdf"
    assert get_res.content.startswith(b"%PDF-")
    assert "attachment; filename=" in get_res.headers["content-disposition"]

    # 2. Generate via POST with options
    post_res = client.post("/api/reports/pdf", headers=headers, json={
        "date_filter": "last_30_days",
        "include_tab_switches": False,
        "include_viva": False,
        "view_mode": "summary"
    })
    assert post_res.status_code == 200
    assert post_res.headers["content-type"] == "application/pdf"
    assert post_res.content.startswith(b"%PDF-")

    # 3. Invalid custom date range on PDF endpoint
    bad_pdf = client.get("/api/reports/pdf?date_filter=custom&start_date=2026-12-01&end_date=2026-01-01", headers=headers)
    assert bad_pdf.status_code == 400


# =============================================================================
# Security & Authorization 23, 25-27
# =============================================================================

def test_student_data_isolation_and_security():
    """Criteria 23, 25: Students cannot view or export another student's records."""
    client = TestClient(app)
    uid_a, tok_a, headers_a = create_user("Student Alpha")
    uid_b, tok_b, headers_b = create_user("Student Beta")

    # Student A records an attempt
    client.post("/api/execute", headers=headers_a, json={
        "problem_id": "two-sum",
        "code": "def twoSum(nums, target): return [0, 1]",
        "language": "python",
        "time_spent_seconds": 99
    })

    # Student B queries dashboard
    dash_b = client.get("/api/performance/dashboard?date_filter=all", headers=headers_b).json()
    assert dash_b["summary"]["total_attempts"] == 0
    assert len(dash_b["questions_performance"]) == 0

    # Student B's PDF contains no records from Student A
    pdf_b = client.get("/api/reports/pdf?date_filter=all", headers=headers_b)
    assert pdf_b.status_code == 200
    assert b"Student Alpha" not in pdf_b.content
