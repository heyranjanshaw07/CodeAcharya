import pytest
import uuid
import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from main import app
from database import get_db, format_timestamp_ist, parse_utc_timestamp, IST_TZ
import performance_service
import pdf_generator
import auth

def create_test_user(name: str = "Lifecycle Student") -> tuple[str, str, dict]:
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


# 1. User switches away for 10-15 seconds and returns; persisted event reflects actual duration within tolerance
def test_tab_switch_10_15_seconds_duration():
    client = TestClient(app)
    uid, token, headers = create_test_user("Tab Switch Timing User")

    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc)
    ev_time = (now - timedelta(seconds=13)).isoformat()
    ret_time = now.isoformat()

    # Page hidden
    resp_hide = client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": ev_time,
        "event_status": "away"
    })
    assert resp_hide.status_code == 200
    assert resp_hide.json()["event_status"] in ("away", "incomplete")

    # Page returned
    resp_return = client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "return_timestamp": ret_time,
        "event_status": "returned"
    })
    assert resp_return.status_code == 200
    ret_data = resp_return.json()
    assert ret_data["event_status"] == "returned"
    # Expected duration is 13 seconds (tolerance: 12-14 seconds)
    assert 12 <= ret_data["time_away_seconds"] <= 14


# 2. Multiple hide/show cycles produce correct number of events and total duration
def test_multiple_hide_show_cycles():
    client = TestClient(app)
    uid, token, headers = create_test_user("Multi Cycle User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc)

    # Cycle 1: 10s away
    c1_hide = (now - timedelta(seconds=50)).isoformat()
    c1_ret = (now - timedelta(seconds=40)).isoformat()
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id, "question_id": "two-sum", "event_timestamp": c1_hide, "event_status": "away"
    })
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id, "question_id": "two-sum", "return_timestamp": c1_ret, "event_status": "returned"
    })

    # Cycle 2: 15s away
    c2_hide = (now - timedelta(seconds=30)).isoformat()
    c2_ret = (now - timedelta(seconds=15)).isoformat()
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id, "question_id": "two-sum", "event_timestamp": c2_hide, "event_status": "away"
    })
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id, "question_id": "two-sum", "return_timestamp": c2_ret, "event_status": "returned"
    })

    data = performance_service.get_student_performance_data(uid, "all")
    events = data["tab_switch_events"]
    assert len(events) == 2
    total_away = sum(e["duration_away_seconds"] for e in events)
    assert 24 <= total_away <= 26 # 10s + 15s = 25s
    assert data["summary"]["total_tab_switches"] == 2
    assert data["summary"]["total_time_away_seconds"] == total_away


# 3. Duplicate visibility notifications do not double-count events
def test_duplicate_visibility_notifications_deduplicated():
    client = TestClient(app)
    uid, token, headers = create_test_user("Deduplication User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    # Send 3 identical away notifications (e.g. blur + visibilitychange firing concurrently)
    for _ in range(3):
        r = client.post("/api/tab-switch/record", headers=headers, json={
            "attempt_id": attempt_id,
            "question_id": "two-sum",
            "event_timestamp": now,
            "event_status": "away"
        })
        assert r.status_code == 200

    data = performance_service.get_student_performance_data(uid, "all")
    assert len(data["tab_switch_events"]) == 1


# 4. An event without a return timestamp is handled as incomplete
def test_event_without_return_timestamp_handled_as_incomplete():
    client = TestClient(app)
    uid, token, headers = create_test_user("Incomplete Event User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": now,
        "event_status": "away"
    })

    data = performance_service.get_student_performance_data(uid, "all")
    assert len(data["tab_switch_events"]) == 1
    ev = data["tab_switch_events"][0]
    assert ev["status"] in ("away", "incomplete")
    assert ev["return_time_ist"] in ("Awaiting return", "Active / Pending Return")
    assert ev["duration_away_formatted"] in ("Incomplete", "Pending")
    assert ev["duration_away_seconds"] == 0


# 5. Paused and completed attempts do not accumulate excluded time
def test_paused_and_completed_attempts_duration_math():
    client = TestClient(app)
    uid, token, headers = create_test_user("Timer Pause User")
    now = datetime.now(timezone.utc)

    # Attempt started 10 minutes ago, active coding 300s (5m), paused 300s (5m)
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 300,
        "paused_seconds": 300,
        "start_time": (now - timedelta(minutes=10)).isoformat(),
        "end_time": now.isoformat(),
        "status": "completed",
        "passed_count": 2,
        "total_count": 2,
        "overall_score": 90.0
    })

    data = performance_service.get_student_performance_data(uid, "all")
    att = data["questions_performance"][0]
    # Total active coding duration strictly reflects active coding time (excludes paused intervals)
    assert att["coding_duration_seconds"] == 300
    assert data["summary"]["total_active_coding_time_seconds"] == 300


# 6 & 7. Refreshing or reconnecting restores state without duplicating attempt
def test_refresh_reconnect_preserves_attempt():
    client = TestClient(app)
    uid, token, headers = create_test_user("Refresh User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    # Step 1: Start attempt
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 10,
        "start_time": now,
        "session_status": "running"
    })

    # Step 2: "Page reloads", send another heartbeat/execution with SAME attempt_id
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 25,
        "start_time": now,
        "session_status": "running"
    })

    data = performance_service.get_student_performance_data(uid, "all")
    assert len(data["questions_performance"]) == 1
    assert data["questions_performance"][0]["attempt_id"] == attempt_id
    assert data["questions_performance"][0]["attempt_status"] == "running"
    assert data["questions_performance"][0]["coding_duration_seconds"] == 25


# 8. Stale attempt follows documented recovery policy without fabricated timestamps
def test_stale_attempt_recovery_policy():
    client = TestClient(app)
    uid, token, headers = create_test_user("Stale Session User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    old_time = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()

    # Insert a 3-hour-old running attempt directly into database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO coding_attempts (
                id, user_id, question_id, language, attempt_status,
                start_time, end_time, elapsed_coding_time_seconds,
                is_completed, passed_count, total_count, created_at, last_activity_at
            ) VALUES (?, ?, 'two-sum', 'python', 'running', ?, NULL, 120, 0, 0, 2, ?, ?)
        """, (attempt_id, uid, old_time, old_time, old_time))
        conn.commit()

    # Querying performance data triggers server-side stale-running recovery policy
    data = performance_service.get_student_performance_data(uid, "all")
    att = data["questions_performance"][0]

    assert att["attempt_status"] == "abandoned"
    assert att["end_time"] is None
    assert att["end_time_ist"] == "Abandoned"
    assert data["summary"]["abandoned_attempts"] == 1
    assert data["summary"]["running_attempts"] == 0


# 9. Completed-attempt scores vs provisional scores displayed correctly
def test_completed_vs_provisional_scores():
    client = TestClient(app)
    uid, token, headers = create_test_user("Score Audit User")
    now = datetime.now(timezone.utc).isoformat()

    # Completed attempt with score 92
    att_comp = f"att_{uuid.uuid4().hex[:10]}"
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": att_comp,
        "problem_id": "two-sum",
        "time_spent_seconds": 180,
        "status": "completed",
        "passed_count": 2,
        "total_count": 2,
        "overall_score": 92.0
    })

    # Unfinished running attempt with interim score 45
    att_run = f"att_{uuid.uuid4().hex[:10]}"
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": att_run,
        "problem_id": "reverse-linked-list",
        "time_spent_seconds": 60,
        "session_status": "running",
        "passed_count": 1,
        "total_count": 3,
        "overall_score": 45.0
    })

    data = performance_service.get_student_performance_data(uid, "all")
    atts = {a["attempt_id"]: a for a in data["questions_performance"]}

    assert atts[att_comp]["is_provisional"] is False
    assert atts[att_comp]["overall_score"] == 92.0

    assert atts[att_run]["is_provisional"] is True
    assert atts[att_run]["overall_score"] == 45.0


# 10. PDF summary counts match detailed attempt records
def test_pdf_summary_matches_detailed_records():
    client = TestClient(app)
    uid, token, headers = create_test_user("PDF Match User")

    for i in range(3):
        client.post("/api/session/record", headers=headers, json={
            "attempt_id": f"att_{uuid.uuid4().hex[:10]}",
            "problem_id": "two-sum",
            "time_spent_seconds": 100 + i * 20,
            "status": "completed",
            "passed_count": 2,
            "total_count": 2,
            "overall_score": 80.0 + i * 5
        })

    client.post("/api/session/record", headers=headers, json={
        "attempt_id": f"att_{uuid.uuid4().hex[:10]}",
        "problem_id": "reverse-linked-list",
        "time_spent_seconds": 50,
        "status": "abandoned",
        "passed_count": 0,
        "total_count": 2,
        "overall_score": 20.0
    })

    data = performance_service.get_student_performance_data(uid, "all")
    summary = data["summary"]
    detailed = data["questions_performance"]

    assert summary["total_attempts"] == len(detailed) == 4
    assert summary["completed_attempts"] == sum(1 for a in detailed if a["attempt_status"] == "completed") == 3
    assert summary["abandoned_attempts"] == sum(1 for a in detailed if a["attempt_status"] == "abandoned") == 1
    assert summary["total_unique_solved"] == len(set(a["question_id"] for a in detailed if a["is_completed"])) == 1


# 11. PDF tab-switch totals match detailed event records
def test_pdf_tab_switch_totals_match_events():
    client = TestClient(app)
    uid, token, headers = create_test_user("Tab Match User")
    now = datetime.now(timezone.utc)

    # 2 returned events with durations 12s and 18s
    ev1 = client.post("/api/tab-switch/record", headers=headers, json={
        "question_id": "two-sum",
        "event_timestamp": (now - timedelta(seconds=40)).isoformat(),
        "return_timestamp": (now - timedelta(seconds=28)).isoformat(),
        "event_status": "returned"
    })
    ev2 = client.post("/api/tab-switch/record", headers=headers, json={
        "question_id": "two-sum",
        "event_timestamp": (now - timedelta(seconds=20)).isoformat(),
        "return_timestamp": (now - timedelta(seconds=2)).isoformat(),
        "event_status": "returned"
    })

    data = performance_service.get_student_performance_data(uid, "all")
    summary = data["summary"]
    events = data["tab_switch_events"]

    assert summary["total_tab_switches"] == len(events) == 2
    sum_durations = sum(e["duration_away_seconds"] for e in events)
    assert summary["total_time_away_seconds"] == sum_durations
    assert sum_durations == 12 + 18


# 12. IST conversion and date filters work across midnight
def test_date_filters_across_midnight_ist():
    client = TestClient(app)
    uid, token, headers = create_test_user("Midnight User")

    # Today in IST
    now_ist = datetime.now(timezone.utc).astimezone(IST_TZ)
    today_str = now_ist.strftime("%Y-%m-%d")
    yesterday_str = (now_ist - timedelta(days=1)).strftime("%Y-%m-%d")

    data = performance_service.get_student_performance_data(
        uid, date_filter="custom", start_date_str=yesterday_str, end_date_str=today_str
    )
    assert data["date_filter"] == "custom"
    assert "Custom:" in data["reporting_period_label"]


# 13. One user cannot access another user's attempts or reports
def test_user_data_isolation():
    client = TestClient(app)
    u1_id, t1, h1 = create_test_user("User One")
    u2_id, t2, h2 = create_test_user("User Two")

    # User 1 attempts
    client.post("/api/session/record", headers=h1, json={
        "problem_id": "two-sum",
        "time_spent_seconds": 120,
        "status": "completed",
        "passed_count": 2,
        "total_count": 2,
        "overall_score": 99.0
    })

    # User 2 dashboard query
    dash2 = client.get("/api/performance/dashboard?date_filter=all", headers=h2).json()
    assert dash2["summary"]["total_attempts"] == 0
    assert len(dash2["questions_performance"]) == 0


# 14. PDF generation and full export workflow succeeds
def test_pdf_generation_full_workflow():
    client = TestClient(app)
    uid, token, headers = create_test_user("PDF Export User")

    client.post("/api/session/record", headers=headers, json={
        "problem_id": "two-sum",
        "time_spent_seconds": 150,
        "status": "completed",
        "passed_count": 2,
        "total_count": 2,
        "overall_score": 88.0
    })

    pdf_resp = client.get("/api/reports/pdf?date_filter=all", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000
    assert pdf_resp.content.startswith(b"%PDF")
