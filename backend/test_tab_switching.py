import pytest
from fastapi.testclient import TestClient
from main import app
from models import ExecuteRequest, SessionRecordRequest
from analytics import AnalyticsManager
from auth import create_user, record_user_session, get_user_profile
import tempfile
import json
import os
import uuid

client = TestClient(app)

def test_api_execute_accepts_tab_switching_stats():
    """Verify /api/execute accepts tab_switch_count, total_time_away_seconds, and last_switch_timestamp."""
    payload = {
        "problem_id": "factorial-recursion",
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "language": "python",
        "time_spent_seconds": 45,
        "session_status": "running",
        "tab_switch_count": 3,
        "total_time_away_seconds": 12,
        "last_switch_timestamp": "12:45:00 PM"
    }
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"

def test_api_session_record_accepts_tab_switching_stats():
    """Verify /api/session/record captures tab switching metrics for completed and abandoned attempts."""
    # Test abandoned attempt
    abandon_payload = {
        "problem_id": "factorial-recursion",
        "language": "python",
        "time_spent_seconds": 120,
        "status": "abandoned",
        "passed_count": 0,
        "total_count": 3,
        "tab_switch_count": 4,
        "total_time_away_seconds": 35,
        "last_switch_timestamp": "12:42:18 PM"
    }
    res_abandon = client.post("/api/session/record", json=abandon_payload)
    assert res_abandon.status_code == 200
    data_abandon = res_abandon.json()
    assert data_abandon.get("status") == "success"
    assert data_abandon.get("tab_switch_count") == 4
    assert data_abandon.get("total_time_away_seconds") == 35
    assert data_abandon.get("last_switch_timestamp") == "12:42:18 PM"

    # Test completed attempt
    complete_payload = {
        "problem_id": "factorial-recursion",
        "language": "python",
        "time_spent_seconds": 150,
        "status": "completed",
        "passed_count": 3,
        "total_count": 3,
        "tab_switch_count": 2,
        "total_time_away_seconds": 15,
        "last_switch_timestamp": "12:50:00 PM"
    }
    res_complete = client.post("/api/session/record", json=complete_payload)
    assert res_complete.status_code == 200
    data_complete = res_complete.json()
    assert data_complete.get("status") == "success"
    assert data_complete.get("tab_switch_count") == 2

def test_analytics_manager_persists_tab_switch_stats():
    """Verify AnalyticsManager records tab switches in problem_solving_times and activity_log."""
    with tempfile.TemporaryDirectory() as tmpdir:
        profile_path = os.path.join(tmpdir, "test_student_profile.json")
        from analytics import DEFAULT_PROFILE
        initial_data = DEFAULT_PROFILE.copy()
        initial_data["problem_solving_times"] = {}
        initial_data["activity_log"] = []
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(initial_data, f)

        analytics = AnalyticsManager(filepath=profile_path)
        
        # Record session with tab switches
        analytics.record_session(
            problem_id="factorial-recursion",
            topic="Recursion & Backtracking",
            status="completed",
            time_spent_seconds=75,
            passed_count=3,
            total_count=3,
            tab_switch_count=3,
            total_time_away_seconds=22,
            last_switch_timestamp="01:15:30 PM"
        )

        with open(profile_path, "r", encoding="utf-8") as f:
            saved = json.load(f)

        assert "factorial-recursion" in saved["problem_solving_times"]
        record = saved["problem_solving_times"]["factorial-recursion"]
        assert record["tab_switch_count"] == 3
        assert record["total_time_away_seconds"] == 22
        assert record["last_switch_timestamp"] == "01:15:30 PM"

        # Check activity log
        assert len(saved["activity_log"]) > 0
        latest_act = saved["activity_log"][0]
        assert latest_act["tab_switch_count"] == 3

def test_auth_manager_persists_user_tab_switch_stats():
    """Verify record_user_session records tab switches in user's individual profile."""
    unique_email = f"student_{uuid.uuid4().hex[:8]}@codeacharya.ai"
    user, err = create_user("Test Student", unique_email, "SecurePassword123!")
    assert user is not None, f"Registration failed: {err}"

    record_user_session(
        user_id=user["id"],
        problem_id="factorial",
        topic="Recursion",
        status="completed",
        time_spent_seconds=90,
        passed_count=2,
        total_count=2,
        tab_switch_count=5,
        total_time_away_seconds=40,
        last_switch_timestamp="02:30:10 PM"
    )

    profile = get_user_profile(user["id"])
    solving_times = profile.get("problem_solving_times", {})
    assert "factorial" in solving_times
    rec = solving_times["factorial"]
    assert rec["tab_switch_count"] == 5
    assert rec["total_time_away_seconds"] == 40
    assert rec["last_switch_timestamp"] == "02:30:10 PM"

def test_api_execute_accepts_and_returns_tab_switch_history():
    """Verify /api/execute accepts tab_switch_history and preserves the event records."""
    history = [
        {
            "switch_number": 1,
            "date": "22 Oct 2026",
            "switch_timestamp_ist": "11:03:20 AM IST",
            "return_timestamp_ist": "11:03:25 AM IST",
            "duration_away_seconds": 5,
            "duration_away_formatted": "00:00:05"
        },
        {
            "switch_number": 2,
            "date": "22 Oct 2026",
            "switch_timestamp_ist": "11:04:10 AM IST",
            "return_timestamp_ist": "11:04:18 AM IST",
            "duration_away_seconds": 8,
            "duration_away_formatted": "00:00:08"
        },
        {
            "switch_number": 3,
            "date": "22 Oct 2026",
            "switch_timestamp_ist": "11:05:00 AM IST",
            "return_timestamp_ist": "11:05:09 AM IST",
            "duration_away_seconds": 9,
            "duration_away_formatted": "00:00:09"
        }
    ]
    payload = {
        "problem_id": "factorial-recursion",
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "language": "python",
        "time_spent_seconds": 60,
        "session_status": "running",
        "tab_switch_count": 3,
        "total_time_away_seconds": 22,
        "last_switch_timestamp": "11:05:00 AM IST",
        "tab_switch_history": history
    }
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tab_switch_count"] == 3
    assert len(data.get("tab_switch_history", [])) == 3
    assert data["tab_switch_history"][0]["switch_number"] == 1
    assert data["tab_switch_history"][2]["switch_number"] == 3

def test_api_session_record_persists_tab_switch_history():
    """Verify /api/session/record preserves tab_switch_history on attempt recording."""
    history = [
        {
            "switch_number": 1,
            "date": "22 Oct 2026",
            "switch_timestamp_ist": "10:15:00 AM IST",
            "return_timestamp_ist": "10:15:10 AM IST",
            "duration_away_seconds": 10,
            "duration_away_formatted": "00:00:10"
        }
    ]
    payload = {
        "problem_id": "factorial-recursion",
        "language": "python",
        "time_spent_seconds": 45,
        "status": "completed",
        "passed_count": 3,
        "total_count": 3,
        "tab_switch_count": 1,
        "total_time_away_seconds": 10,
        "last_switch_timestamp": "10:15:00 AM IST",
        "tab_switch_history": history
    }
    res = client.post("/api/session/record", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "success"
    assert data.get("tab_switch_count") == 1
    assert len(data.get("tab_switch_history", [])) == 1
    assert data["tab_switch_history"][0]["switch_timestamp_ist"] == "10:15:00 AM IST"
