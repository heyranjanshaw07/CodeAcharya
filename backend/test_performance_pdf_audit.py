import pytest
import uuid
import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from main import app
from database import get_db, format_timestamp_ist, parse_utc_timestamp, IST_TZ
import performance_service
import pdf_generator

def create_user(name: str = "Audit Student") -> tuple[str, str, dict]:
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
# 1. ACCURATE ATTEMPT TIMESTAMPS & DURATION MATH
# =============================================================================

def test_accurate_attempt_timestamps_and_in_progress():
    """Requirement 1: Record actual start and end timestamps; do not fabricate end time for in-progress."""
    client = TestClient(app)
    uid, token, headers = create_user("Timestamp Audit Student")

    now = datetime.now(timezone.utc)
    start_iso = (now - timedelta(minutes=15)).isoformat()
    end_iso = (now - timedelta(minutes=5)).isoformat() # 10 mins elapsed (600s)

    # Completed attempt with distinct start & end
    attempt_id_1 = str(uuid.uuid4())
    resp1 = client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id_1,
        "problem_id": "two-sum",
        "question_title": "Two Sum",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "language": "python",
        "code": "def twoSum(): pass",
        "time_spent_seconds": 450,       # 7.5 min active coding
        "paused_seconds": 150,           # 2.5 min paused
        "start_time": start_iso,
        "end_time": end_iso,
        "session_status": "completed",
        "passed_test_cases": 2,
        "total_test_cases": 2,
        "overall_score": 95.0
    })
    assert resp1.status_code == 200

    # Running / in-progress attempt (no end_time)
    attempt_id_2 = str(uuid.uuid4())
    resp2 = client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id_2,
        "problem_id": "reverse-linked-list",
        "question_title": "Reverse Linked List",
        "topic": "Linked List",
        "difficulty": "Easy",
        "language": "python",
        "code": "def reverseList(): pass",
        "time_spent_seconds": 180,
        "paused_seconds": 0,
        "start_time": (now - timedelta(minutes=3)).isoformat(),
        "end_time": None,
        "session_status": "running",
        "passed_test_cases": 0,
        "total_test_cases": 0,
        "overall_score": 0.0
    })
    assert resp2.status_code == 200

    # Query dashboard
    dash = client.get("/api/performance/dashboard?date_filter=all", headers=headers).json()
    attempts = {a["attempt_id"]: a for a in dash["questions_performance"]}

    att1 = attempts[attempt_id_1]
    att2 = attempts[attempt_id_2]

    # Verify attempt 1 has distinct timestamps and not "In progress"
    assert att1["start_time_ist"] != att1["end_time_ist"]
    assert att1["end_time_ist"] != "In progress"
    assert "IST" in att1["start_time_ist"]
    assert "IST" in att1["end_time_ist"]
    assert att1["coding_duration_seconds"] == 450

    # Verify attempt 2 is "In progress" and has None as raw end_time
    assert att2["end_time"] is None
    assert att2["end_time_ist"] == "In progress"
    assert att2["attempt_status"] == "running"
    assert att2["is_completed"] is False


# =============================================================================
# 2. TAB-SWITCH DURATION CONSISTENCY & DEDUPLICATION
# =============================================================================

def test_tab_switch_duration_consistency_and_no_zero_discrepancy():
    """Requirement 2: Fix 0s vs 97s summary discrepancy; handle incomplete tab events."""
    client = TestClient(app)
    uid, token, headers = create_user("Tab Switch Audit Student")

    attempt_id = str(uuid.uuid4())
    t0 = datetime(2026, 10, 24, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=97) # 1m 37s away

    # Event 1: 97s away (persisted duration_away_seconds = 97)
    ev1_res = client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t0.isoformat(),
        "return_timestamp": t1.isoformat(),
        "time_away_seconds": 97,
        "event_status": "returned"
    })
    assert ev1_res.status_code == 200

    # Event 2: Incomplete event (user switched tab and hasn't returned yet)
    t2 = t1 + timedelta(minutes=5)
    ev2_res = client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": t2.isoformat(),
        "return_timestamp": None,
        "time_away_seconds": 0,
        "event_status": "away"
    })
    assert ev2_res.status_code == 200

    dash = client.get("/api/performance/dashboard?date_filter=all", headers=headers).json()
    tab_events = dash["tab_switch_events"]
    summary = dash["summary"]

    # Verify 2 events recorded
    assert len(tab_events) == 2

    # Find the completed event
    ret_ev = next(e for e in tab_events if e["status"] == "returned")
    assert ret_ev["duration_away_seconds"] == 97
    assert ret_ev["duration_away_formatted"] == "1m 37s"
    assert "IST" in ret_ev["hidden_time_ist"]
    assert "IST" in ret_ev["return_time_ist"]

    # Find the incomplete event
    inc_ev = next(e for e in tab_events if e["status"] == "away")
    assert inc_ev["duration_away_seconds"] == 0
    assert inc_ev["duration_away_formatted"] in ("Incomplete", "Pending")
    assert inc_ev["return_time_ist"] in ("Awaiting return", "Active / Pending Return")

    # Verify summary total away is exactly 97s (1m 37s) matching the returned events
    assert summary["total_tab_switches"] == 2
    assert summary["total_time_away_seconds"] == 97
    assert summary["total_time_away_formatted"] == "1m 37s"


def test_tab_switch_deduplication():
    """Requirement 2: Avoid double-counting and duplicate events for same attempt and timestamp."""
    client = TestClient(app)
    uid, token, headers = create_user("Deduplication Student")

    attempt_id = str(uuid.uuid4())
    ts_iso = "2026-10-24T12:00:00Z"

    # Post initial away event
    r1 = client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": ts_iso,
        "return_timestamp": None,
        "time_away_seconds": 0,
        "event_status": "away"
    })
    assert r1.status_code == 200

    # Post return update for the SAME event
    r2 = client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": ts_iso,
        "return_timestamp": "2026-10-24T12:00:30Z",
        "time_away_seconds": 30,
        "event_status": "returned"
    })
    assert r2.status_code == 200

    dash = client.get("/api/performance/dashboard?date_filter=all", headers=headers).json()
    assert len(dash["tab_switch_events"]) == 1
    assert dash["tab_switch_events"][0]["duration_away_seconds"] == 30
    assert dash["summary"]["total_tab_switches"] == 1
    assert dash["summary"]["total_time_away_seconds"] == 30


# =============================================================================
# 3. CORRECT ATTEMPT STATUSES & SUMMARY COUNT AGREEMENT
# =============================================================================

def test_attempt_status_distinction_and_summary_counts():
    """Requirement 3: Distinguish completed, failed, running, paused, abandoned without false completions."""
    client = TestClient(app)
    uid, token, headers = create_user("Status Audit Student")

    now = datetime.now(timezone.utc)

    # 1. Completed: passed all test cases
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": str(uuid.uuid4()),
        "problem_id": "two-sum",
        "question_title": "Two Sum",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "language": "python",
        "time_spent_seconds": 120,
        "start_time": (now - timedelta(minutes=20)).isoformat(),
        "end_time": (now - timedelta(minutes=18)).isoformat(),
        "session_status": "completed",
        "passed_test_cases": 2,
        "total_test_cases": 2,
        "overall_score": 100.0
    })

    # 2. Failed: executed tests, but did not pass all
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": str(uuid.uuid4()),
        "problem_id": "two-sum",
        "question_title": "Two Sum",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "language": "python",
        "time_spent_seconds": 90,
        "start_time": (now - timedelta(minutes=16)).isoformat(),
        "end_time": (now - timedelta(minutes=14)).isoformat(),
        "session_status": "failed",
        "passed_test_cases": 0,
        "total_test_cases": 2,
        "overall_score": 25.0
    })

    # 3. Running: currently in progress
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": str(uuid.uuid4()),
        "problem_id": "valid-anagram",
        "question_title": "Valid Anagram",
        "topic": "Strings",
        "difficulty": "Easy",
        "language": "python",
        "time_spent_seconds": 60,
        "start_time": (now - timedelta(minutes=10)).isoformat(),
        "end_time": None,
        "session_status": "running",
        "passed_test_cases": 0,
        "total_test_cases": 0,
        "overall_score": 0.0
    })

    # 4. Paused: timer paused
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": str(uuid.uuid4()),
        "problem_id": "group-anagrams",
        "question_title": "Group Anagrams",
        "topic": "Strings",
        "difficulty": "Medium",
        "language": "python",
        "time_spent_seconds": 150,
        "paused_seconds": 60,
        "start_time": (now - timedelta(minutes=8)).isoformat(),
        "end_time": None,
        "session_status": "paused",
        "passed_test_cases": 0,
        "total_test_cases": 0,
        "overall_score": 0.0
    })

    # 5. Abandoned
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": str(uuid.uuid4()),
        "problem_id": "longest-consecutive-sequence",
        "question_title": "Longest Consecutive Sequence",
        "topic": "Arrays",
        "difficulty": "Medium",
        "language": "python",
        "time_spent_seconds": 40,
        "start_time": (now - timedelta(minutes=5)).isoformat(),
        "end_time": (now - timedelta(minutes=4)).isoformat(),
        "session_status": "abandoned",
        "passed_test_cases": 0,
        "total_test_cases": 2,
        "overall_score": 10.0
    })

    dash = client.get("/api/performance/dashboard?date_filter=all", headers=headers).json()
    s = dash["summary"]
    q_table = dash["questions_performance"]

    assert s["total_attempts"] == 5
    assert len(q_table) == 5

    assert s["completed_attempts"] == 1
    assert s["failed_attempts"] == 1
    assert s["running_attempts"] == 1
    assert s["paused_attempts"] == 1
    assert s["abandoned_attempts"] == 1

    # Incomplete attempts must NOT be counted as completed
    assert s["completed_attempts"] != s["total_attempts"]

    statuses_in_table = [q["attempt_status"] for q in q_table]
    assert "completed" in statuses_in_table
    assert "failed" in statuses_in_table
    assert "running" in statuses_in_table
    assert "paused" in statuses_in_table
    assert "abandoned" in statuses_in_table


# =============================================================================
# 4. TRANSPARENT SCORE CALCULATIONS & METRICS
# =============================================================================

def test_transparent_score_calculations_and_na_handling():
    """Requirement 4: Document calculation method; base pass rates on actual test executions."""
    client = TestClient(app)
    uid, token, headers = create_user("Scoring Transparency Student")

    # Record 1 attempt: scored 80/100, 2/2 tests passed
    client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        c = target - n\n        if c in seen:\n            return [seen[c], i]\n        seen[n] = i\n    return []\n",
        "language": "python",
        "time_spent_seconds": 60,
        "session_status": "completed"
    })

    dash = client.get("/api/performance/dashboard?date_filter=all", headers=headers).json()
    summary = dash["summary"]

    assert "score_calculation_method" in summary
    assert "All Evaluated Attempts" in summary["score_calculation_method"]
    assert summary["average_coding_score"] is not None
    assert summary["best_coding_score"] is not None
    assert summary["overall_pass_rate_percentage"] == 100.0


# =============================================================================
# 5. RELEVANT LEARNING INSIGHTS & NEUTRAL FOCUS TELEMETRY
# =============================================================================

def test_pedagogical_insights_topic_grounding_and_neutrality():
    """Requirement 5: Topic-grounded recommendations without loop-bound bias on recursion; neutral tab telemetry."""
    # Build test report data structure with a failed recursion question
    report_data = {
        "user_info": {"full_name": "Recursion Learner", "email": "rec@example.com"},
        "summary": {
            "total_unique_solved": 1,
            "total_attempts": 3,
            "completed_attempts": 1,
            "failed_attempts": 2,
            "abandoned_attempts": 0,
            "running_attempts": 0,
            "paused_attempts": 0,
            "other_attempts": 0,
            "average_coding_score": 55.0,
            "average_completed_coding_score": 90.0,
            "score_calculation_method": "All Evaluated Attempts (mean of all evaluated attempts in period)",
            "best_coding_score": 90.0,
            "total_active_coding_time_seconds": 600,
            "total_active_coding_time_formatted": "10m",
            "total_unique_hints_used": 1,
            "total_tab_switches": 4,
            "total_time_away_seconds": 180,
            "total_time_away_formatted": "3m 0s",
            "overall_pass_rate_percentage": 40.0,
            "total_test_cases_passed": 2,
            "total_test_cases_evaluated": 5,
            "viva": {"sessions_count": 0, "average_score": None, "best_score": None}
        },
        "questions_performance": [
            {
                "attempt_id": "att-1",
                "question_id": "fibonacci-recursion",
                "question_title": "Fibonacci Number",
                "topic": "Recursion",
                "difficulty": "Easy",
                "language": "python",
                "attempt_number": 1,
                "attempt_status": "failed",
                "start_time_ist": "2026-10-24 14:00:00 IST",
                "end_time_ist": "2026-10-24 14:05:00 IST",
                "coding_duration_formatted": "5m",
                "execution_time_ms": 12.5,
                "overall_score": 30.0,
                "passed_count": 1,
                "total_count": 3,
                "unique_hints_used": 1,
                "independent_score": 9.0,
                "tab_switch_count": 2,
                "time_away_formatted": "1m"
            },
            {
                "attempt_id": "att-2",
                "question_id": "two-sum",
                "question_title": "Two Sum",
                "topic": "Arrays",
                "difficulty": "Easy",
                "language": "python",
                "attempt_number": 1,
                "attempt_status": "completed",
                "start_time_ist": "2026-10-24 14:10:00 IST",
                "end_time_ist": "2026-10-24 14:15:00 IST",
                "coding_duration_formatted": "5m",
                "execution_time_ms": 8.0,
                "overall_score": 90.0,
                "passed_count": 2,
                "total_count": 2,
                "unique_hints_used": 0,
                "independent_score": 10.0,
                "tab_switch_count": 2,
                "time_away_formatted": "2m"
            }
        ],
        "tab_switch_events": [
            {
                "switch_number": 1,
                "attempt_id": "att-1",
                "question_title": "Fibonacci Number",
                "date_ist": "2026-10-24",
                "hidden_time_ist": "2026-10-24 14:01:00 IST",
                "return_time_ist": "2026-10-24 14:02:00 IST",
                "duration_away_formatted": "1m 0s",
                "status": "returned"
            },
            {
                "switch_number": 2,
                "attempt_id": "att-2",
                "question_title": "Two Sum",
                "date_ist": "2026-10-24",
                "hidden_time_ist": "2026-10-24 14:11:00 IST",
                "return_time_ist": "Active / Pending Return",
                "duration_away_formatted": "Pending",
                "status": "incomplete"
            }
        ],
        "viva_sessions": [],
        "charts": {
            "topic_accuracy": [
                {"topic": "Arrays", "attempts_count": 1, "unique_solved": 1, "pass_rate_percentage": 100.0, "average_score": 90.0},
                {"topic": "Recursion", "attempts_count": 1, "unique_solved": 0, "pass_rate_percentage": 33.3, "average_score": 30.0}
            ]
        }
    }

    # Generate PDF
    pdf_bytes = pdf_generator.generate_student_performance_pdf(
        data=report_data,
        include_tab_switches=True,
        include_viva=False
    )

    # Extract and decompress stream text from the generated PDF
    import re, zlib, base64
    all_chunks = []
    for match in re.finditer(rb"stream\r?\n(.*?~>)endstream", pdf_bytes, re.DOTALL):
        try:
            raw = base64.a85decode(match.group(1), adobe=True)
            dec = zlib.decompress(raw)
            all_chunks.append(dec.decode("latin1", "ignore"))
        except Exception:
            all_chunks.append(match.group(1).decode("latin1", "ignore"))
    pdf_text = " ".join(all_chunks).lower()

    # Verify no loop-bound advice is given for recursion topic
    assert "loop bounds" not in pdf_text
    # Verify recursion advice recommends base cases / call stack
    assert "base case" in pdf_text or "call stack" in pdf_text
    # Verify focus telemetry is neutral without accusatory "Frequent Context Switching" / "external reference lookups"
    assert "frequent context switching" not in pdf_text
    assert "limiting external reference" not in pdf_text
    assert "browser focus" in pdf_text


# =============================================================================
# 6. IST HANDLING & NO DOUBLE OFFSETTING
# =============================================================================

def test_ist_conversion_no_double_offset():
    """Requirement 6: Format in IST without applying UTC+05:30 offset twice."""
    # Stored ISO UTC string
    utc_str = "2026-10-24T10:00:00Z"
    ist_str = format_timestamp_ist(utc_str)
    # 10:00:00 UTC + 5h30m = 15:30:00 IST
    assert ist_str == "2026-10-24 15:30:00 IST"

    # Re-passing the IST string should not add another 5h30m!
    ist_str_2 = format_timestamp_ist(ist_str)
    assert ist_str_2 == "2026-10-24 15:30:00 IST"


# =============================================================================
# 7. END-TO-END PDF GENERATION VIA API FROM REAL DB RECORDS
# =============================================================================

def test_full_pdf_generation_endpoint_with_real_db_data():
    """Requirement 7: Generate a fresh PDF using actual database records; verify validity and headers."""
    client = TestClient(app)
    uid, token, headers = create_user("Full PDF Student")

    # Create attempts and tab switch in real DB
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": str(uuid.uuid4()),
        "problem_id": "two-sum",
        "question_title": "Two Sum",
        "topic": "Arrays",
        "difficulty": "Easy",
        "language": "python",
        "time_spent_seconds": 150,
        "paused_seconds": 30,
        "start_time": "2026-10-24T08:00:00Z",
        "end_time": "2026-10-24T08:03:00Z",
        "session_status": "completed",
        "passed_test_cases": 2,
        "total_test_cases": 2,
        "overall_score": 100.0
    })

    client.post("/api/tab-switch/record", headers=headers, json={
        "question_id": "two-sum",
        "event_timestamp": "2026-10-24T08:01:00Z",
        "return_timestamp": "2026-10-24T08:01:45Z",
        "time_away_seconds": 45,
        "event_status": "returned"
    })

    # Call PDF download API
    pdf_resp = client.post("/api/reports/pdf", headers=headers, json={
        "date_filter": "all",
        "include_tab_switches": True,
        "include_viva": True
    })

    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    content = pdf_resp.content
    assert content.startswith(b"%PDF-")
    assert len(content) > 5000  # Non-empty, structurally complete PDF
