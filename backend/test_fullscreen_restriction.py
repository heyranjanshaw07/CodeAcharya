import pytest
import uuid
import json
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from main import app, auth_rate_limiter
from database import get_db, format_timestamp_ist, parse_utc_timestamp
import performance_service
import auth

def create_test_user(name: str = "Fullscreen Student") -> tuple[str, str, dict]:
    auth_rate_limiter.reset()
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


# 1. Test locking session transitions attempt to locked state
def test_session_lock_endpoint():
    client = TestClient(app)
    uid, token, headers = create_test_user("Lock Test User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    # Start a running session
    start_resp = client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "time_spent_seconds": 15,
        "session_status": "running",
        "start_time": now,
        "code": "def two_sum(): pass"
    })
    assert start_resp.status_code == 200

    # Call lock endpoint (simulating full-screen exit)
    lock_resp = client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit",
        "event_timestamp": now,
        "metadata": {"mode": "assessment"}
    })
    assert lock_resp.status_code == 200
    lock_data = lock_resp.json()
    assert lock_data["status"] == "locked"
    assert lock_data["is_locked"] is True
    assert lock_data["reason"] == "fullscreen_exit"

    # Verify database state
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_locked, lock_reason FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["is_locked"] == 1
        assert row["lock_reason"] == "fullscreen_exit"


# 2. Test resume rejected when fullscreen is NOT verified
def test_resume_rejected_without_fullscreen_verification():
    client = TestClient(app)
    uid, token, headers = create_test_user("Resume Fail User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    # Lock session
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit",
        "event_timestamp": now
    })

    # Attempt resume with fullscreen_verified = False (e.g. browser rejected or user clicked without full-screen)
    resume_resp = client.post("/api/session/resume", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": False,
        "event_timestamp": now
    })
    assert resume_resp.status_code == 400
    assert "Verification failed" in resume_resp.json()["detail"]

    # Verify attempt remains locked in database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_locked FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        if row:
            assert row["is_locked"] == 1


# 3. Test resume succeeds when fullscreen is verified
def test_resume_success_with_fullscreen_verification():
    client = TestClient(app)
    uid, token, headers = create_test_user("Resume Success User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    # Start and lock session
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": "def two_sum(nums, target): return [0, 1]"
    })
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit"
    })

    # Resume with fullscreen_verified = True
    resume_resp = client.post("/api/session/resume", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": True
    })
    assert resume_resp.status_code == 200
    res_data = resume_resp.json()
    assert res_data["status"] == "unlocked"
    assert res_data["is_locked"] is False

    # Verify attempt is unlocked in database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_locked, lock_reason FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        assert row["is_locked"] == 0
        assert row["lock_reason"] == ""


# 4. Backend rejects execution while session is locked
def test_execution_rejected_while_locked():
    client = TestClient(app)
    uid, token, headers = create_test_user("Exec Rejection User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    code_content = "def two_sum(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        comp = target - n\n        if comp in lookup: return [lookup[comp], i]\n        lookup[n] = i\n    return []"

    # Start session and lock it
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": code_content
    })
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit"
    })

    # Attempt to execute code with the locked attempt_id
    exec_resp = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code_content,
        "language": "python",
        "attempt_id": attempt_id
    })
    assert exec_resp.status_code == 403
    assert "locked" in exec_resp.json()["detail"].lower()

    # Attempt to execute code with is_locked=True flag
    exec_resp_flag = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code_content,
        "language": "python",
        "is_locked": True
    })
    assert exec_resp_flag.status_code == 403
    assert "locked" in exec_resp_flag.json()["detail"].lower()


# 5. Backend allows execution after session is resumed
def test_execution_allowed_after_resume():
    client = TestClient(app)
    uid, token, headers = create_test_user("Exec Allowed User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    code_content = "def two_sum(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        comp = target - n\n        if comp in lookup: return [lookup[comp], i]\n        lookup[n] = i\n    return []"

    # Start session, lock, then verify resume
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": code_content
    })
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit"
    })
    client.post("/api/session/resume", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": True
    })

    # Execute code after resume
    exec_resp = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code_content,
        "language": "python",
        "attempt_id": attempt_id
    })
    assert exec_resp.status_code == 200
    res = exec_resp.json()
    assert res["status"] == "success"
    assert res["is_completed"] is True


# 6. Attempt ownership check: User cannot lock or resume another user's session
def test_cross_user_attempt_tampering_prevented():
    client = TestClient(app)
    uid1, token1, headers1 = create_test_user("Victim User")
    uid2, token2, headers2 = create_test_user("Attacker User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"

    # User 1 starts session
    client.post("/api/session/record", headers=headers1, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running"
    })

    # User 2 tries to lock or resume User 1's attempt
    lock_resp = client.post("/api/session/lock", headers=headers2, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum"
    })
    assert lock_resp.status_code == 403

    resume_resp = client.post("/api/session/resume", headers=headers2, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": True
    })
    assert resume_resp.status_code == 403


# 7. Resuming completed or abandoned attempts is rejected
def test_cannot_resume_completed_attempt():
    client = TestClient(app)
    uid, token, headers = create_test_user("Completed Resume User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"

    # Record completed session
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "completed",
        "passed_count": 2,
        "total_count": 2
    })

    # Attempt to resume
    resume_resp = client.post("/api/session/resume", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": True
    })
    assert resume_resp.status_code == 400
    assert "completed" in resume_resp.json()["detail"].lower()


# 8. Cannot mark session completed while locked
def test_cannot_complete_session_while_locked():
    client = TestClient(app)
    uid, token, headers = create_test_user("Lock Complete User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"

    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running"
    })
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit"
    })

    # Attempt to mark completed directly via session/record while locked
    complete_resp = client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "completed",
        "passed_count": 2,
        "total_count": 2
    })
    assert complete_resp.status_code == 403
    assert "locked" in complete_resp.json()["detail"].lower()


# 9. Telemetry: session lock events recording & deduplication
def test_lock_telemetry_recording_and_deduplication():
    client = TestClient(app)
    uid, token, headers = create_test_user("Telemetry User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    # Record fullscreen entered
    resp1 = client.post("/api/session/lock-event", headers=headers, json={
        "event_type": "fullscreen_entered",
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": now
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "success"
    assert data1["duplicate"] is False

    # Rapid identical event within 1s should be deduplicated
    resp2 = client.post("/api/session/lock-event", headers=headers, json={
        "event_type": "fullscreen_entered",
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "event_timestamp": now
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["duplicate"] is True

    # Fetch events via GET endpoint
    get_resp = client.get("/api/session/lock-events", headers=headers)
    assert get_resp.status_code == 200
    events = get_resp.json()["events"]
    assert len(events) >= 1
    assert any(e["event_type"] == "fullscreen_entered" for e in events)


# 10. Distinction between tab switch events and fullscreen events
def test_distinction_between_tab_switches_and_fullscreen_events():
    client = TestClient(app)
    uid, token, headers = create_test_user("Distinction User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc)

    # 1 genuine tab switch (away and returned)
    c_hide = (now - timedelta(seconds=20)).isoformat()
    c_ret = now.isoformat()
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id, "question_id": "two-sum", "event_timestamp": c_hide, "event_status": "away"
    })
    client.post("/api/tab-switch/record", headers=headers, json={
        "attempt_id": attempt_id, "question_id": "two-sum", "return_timestamp": c_ret, "event_status": "returned"
    })

    # Fullscreen exit without leaving tab (e.g. Esc key pressed)
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit",
        "event_timestamp": c_ret
    })

    # Verify performance data: tab switches count is strictly 1 (NOT 2!)
    data = performance_service.get_student_performance_data(uid, "all")
    assert len(data["tab_switch_events"]) == 1
    assert data["summary"]["total_tab_switches"] == 1

    # Session lock events are separate
    assert len(data["session_lock_events"]) >= 1
    lock_types = [e["event_type"] for e in data["session_lock_events"]]
    assert "fullscreen_exited" in lock_types or "editor_locked" in lock_types


# 11. Code preservation: Code is never wiped or lost during lock/resume
def test_code_preservation_during_lock_lifecycle():
    client = TestClient(app)
    uid, token, headers = create_test_user("Code Preservation User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    student_code = "def custom_algorithm():\n    return 'preserved_code_content'"

    # Start session with code
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": student_code
    })

    # Lock session
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit"
    })

    # Verify code in database is intact
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        assert row["code"] == student_code

    # Resume session
    client.post("/api/session/resume", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": True
    })

    # Verify code in database is still intact
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        assert row["code"] == student_code


# 12. Normal practice mode requires full-screen
def test_normal_practice_mode_requires_fullscreen():
    client = TestClient(app)
    uid, token, headers = create_test_user("Practice Mode User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    student_code = "def two_sum(nums, target): return [0, 1]"

    # Practice mode (isAssessmentMode=False) session
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": student_code
    })

    # When student exits fullscreen, practice session locks
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit",
        "metadata": {"mode": "practice"}
    })

    # Execution must be rejected while locked in practice mode
    exec_resp = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": student_code,
        "language": "python",
        "attempt_id": attempt_id
    })
    assert exec_resp.status_code == 403
    assert "locked" in exec_resp.json()["detail"].lower()


# 13. Timed coding mode requires full-screen and tracks pause
def test_timed_coding_mode_requires_fullscreen_and_tracks_pause():
    client = TestClient(app)
    uid, token, headers = create_test_user("Timed Coding User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc)

    # Start timed coding session
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "start_time": (now - timedelta(seconds=60)).isoformat(),
        "time_spent_seconds": 60,
        "paused_seconds": 0
    })

    # Lock session on fullscreen exit (timer paused)
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit",
        "metadata": {"mode": "timed", "elapsed_seconds": 60}
    })

    # Cannot execute while locked
    res = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target): return [0, 1]",
        "attempt_id": attempt_id
    })
    assert res.status_code == 403


# 14. Assessment mode requires full-screen
def test_assessment_mode_requires_fullscreen():
    client = TestClient(app)
    uid, token, headers = create_test_user("Assessment Mode User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"

    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": "def two_sum(): pass"
    })
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit",
        "metadata": {"mode": "assessment"}
    })

    res = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": "def two_sum(): pass",
        "attempt_id": attempt_id
    })
    assert res.status_code == 403


# 15. Refresh & reconnection restores locked state and preserves code
def test_refresh_and_reconnection_restores_state():
    client = TestClient(app)
    uid, token, headers = create_test_user("Refresh User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    saved_code = "def two_sum(nums, target):\n    # in progress code\n    return [0, 1]"

    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": saved_code
    })
    # Browser reloads, triggering fullscreen exit and lock
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "reason": "fullscreen_exit"
    })

    # On reconnection / refresh, retrieve user's attempts
    attempts_resp = client.get("/api/scores/history", headers=headers)
    assert attempts_resp.status_code == 200

    # Ensure code is preserved and session remains locked
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code, is_locked FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        assert row["code"] == saved_code
        assert row["is_locked"] == 1


# 16. Existing hints and scoring rubric continue working regression-free
def test_hints_and_scoring_rubric_unaffected():
    client = TestClient(app)
    uid, token, headers = create_test_user("Scoring Hints User")
    attempt_id = f"att_{uuid.uuid4().hex[:10]}"
    sol_code = "def two_sum(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        comp = target - n\n        if comp in lookup: return [lookup[comp], i]\n        lookup[n] = i\n    return []"

    # Start session, lock, verify resume
    client.post("/api/session/record", headers=headers, json={
        "attempt_id": attempt_id,
        "problem_id": "two-sum",
        "session_status": "running",
        "code": sol_code
    })
    client.post("/api/session/lock", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum"
    })
    client.post("/api/session/resume", headers=headers, json={
        "attempt_id": attempt_id,
        "question_id": "two-sum",
        "fullscreen_verified": True
    })

    # Fetch hint
    hint_resp = client.post("/api/hints", headers=headers, json={
        "problem_id": "two-sum",
        "code": sol_code,
        "language": "python",
        "hint_level": 1
    })
    assert hint_resp.status_code == 200
    assert "hint_content" in hint_resp.json()

    # Execute and evaluate score
    exec_resp = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": sol_code,
        "language": "python",
        "attempt_id": attempt_id,
        "unique_hints_used": 1
    })
    assert exec_resp.status_code == 200
    data = exec_resp.json()
    assert data["is_completed"] is True
    assert data["overall_score"] is not None
    assert data["overall_score"] > 0

