import pytest
import uuid
import time
from fastapi.testclient import TestClient

from main import app, auth_rate_limiter
import auth
from database import get_db, format_timestamp_ist, utc_iso_now

client = TestClient(app)

def create_authenticated_user():
    auth_rate_limiter.reset()
    email = f"student_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/register", json={
        "full_name": "Test Student",
        "email": email,
        "password": "SecurePassword2026!"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["token"]
    user_id = data["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, headers, email

def test_1_paste_attempt_endpoint_requires_auth():
    """Verify unauthenticated requests cannot record paste attempts."""
    resp = client.post("/api/assessment/paste-attempt", json={
        "page_type": "coding",
        "question_id": "two-sum"
    })
    assert resp.status_code == 401

def test_2_record_coding_paste_attempt_and_verify_utc_and_ist():
    """Verify paste attempt records in UTC, displays in IST, and links to user."""
    user_id, headers, _ = create_authenticated_user()
    attempt_id = f"att_{uuid.uuid4().hex[:8]}"

    resp = client.post("/api/assessment/paste-attempt", headers=headers, json={
        "page_type": "coding",
        "question_id": "palindrome-number",
        "attempt_id": attempt_id
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert data["duplicate"] is False
    assert data["record"] is not None
    assert data["record"]["user_id"] == user_id
    assert data["record"]["page_type"] == "coding"
    assert data["record"]["question_id"] == "palindrome-number"
    assert data["record"]["attempt_id"] == attempt_id
    assert "IST" in data["record"]["event_timestamp_ist"]

    # Verify directly in SQLite that event_timestamp was stored in UTC
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM paste_events WHERE id = ?", (data["record"]["id"],))
        row = cursor.fetchone()
        assert row is not None
        assert row["user_id"] == user_id
        assert row["page_type"] == "coding"
        assert row["question_id"] == "palindrome-number"
        assert "Z" in row["event_timestamp"] or "+00:00" in row["event_timestamp"]

def test_3_record_viva_paste_attempt():
    """Verify paste attempt on AI Viva page is tracked with page_type viva."""
    user_id, headers, _ = create_authenticated_user()

    resp = client.post("/api/assessment/paste-attempt", headers=headers, json={
        "page_type": "viva",
        "question_id": "viva_two_sum_q1"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["record"]["page_type"] == "viva"
    assert data["record"]["question_id"] == "viva_two_sum_q1"

def test_4_deduplication_of_rapid_burst_paste_attempts():
    """Verify rapid consecutive paste attempts within 1.5s are deduplicated."""
    user_id, headers, _ = create_authenticated_user()
    attempt_id = f"att_burst_{uuid.uuid4().hex[:8]}"

    # First attempt
    r1 = client.post("/api/assessment/paste-attempt", headers=headers, json={
        "page_type": "coding",
        "question_id": "reverse-linked-list",
        "attempt_id": attempt_id
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["duplicate"] is False
    rec_id1 = d1["record"]["id"]

    # Second rapid attempt immediately (< 1.5 seconds)
    r2 = client.post("/api/assessment/paste-attempt", headers=headers, json={
        "page_type": "coding",
        "question_id": "reverse-linked-list",
        "attempt_id": attempt_id
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["duplicate"] is True
    assert d2["record"]["id"] == rec_id1

    # Verify in DB that only 1 record exists for this burst
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM paste_events WHERE attempt_id = ?", (attempt_id,))
        count = cursor.fetchone()["cnt"]
        assert count == 1

def test_5_retrieve_paste_attempts_with_user_isolation():
    """Verify users can only see their own paste attempt telemetry."""
    user1_id, headers1, _ = create_authenticated_user()
    user2_id, headers2, _ = create_authenticated_user()

    # User 1 has 2 events
    client.post("/api/assessment/paste-attempt", headers=headers1, json={
        "page_type": "coding",
        "question_id": "q1",
        "attempt_id": "u1_att1"
    })
    time.sleep(1.6) # Wait for deduplication window
    client.post("/api/assessment/paste-attempt", headers=headers1, json={
        "page_type": "viva",
        "question_id": "q1",
        "attempt_id": "u1_att2"
    })

    # User 2 has 1 event
    client.post("/api/assessment/paste-attempt", headers=headers2, json={
        "page_type": "coding",
        "question_id": "q2",
        "attempt_id": "u2_att1"
    })

    # Retrieve User 1 events
    resp1 = client.get("/api/assessment/paste-attempts", headers=headers1)
    assert resp1.status_code == 200
    events1 = resp1.json()["events"]
    assert len(events1) >= 2
    for ev in events1:
        assert ev["user_id"] == user1_id
        assert ev["user_id"] != user2_id

    # Retrieve User 2 events
    resp2 = client.get("/api/assessment/paste-attempts", headers=headers2)
    assert resp2.status_code == 200
    events2 = resp2.json()["events"]
    assert len(events2) >= 1
    for ev in events2:
        assert ev["user_id"] == user2_id
        assert ev["user_id"] != user1_id

def test_6_filter_by_attempt_id():
    """Verify filtering paste attempts by attempt_id works accurately."""
    user_id, headers, _ = create_authenticated_user()
    specific_attempt = f"att_filter_{uuid.uuid4().hex[:8]}"

    client.post("/api/assessment/paste-attempt", headers=headers, json={
        "page_type": "coding",
        "question_id": "q_filtered",
        "attempt_id": specific_attempt
    })

    resp = client.get(f"/api/assessment/paste-attempts?attempt_id={specific_attempt}", headers=headers)
    assert resp.status_code == 200
    events = resp.json()["events"]
    assert len(events) == 1
    assert events[0]["attempt_id"] == specific_attempt

def test_7_no_clipboard_content_collected_or_stored():
    """Verify that clipboard contents are never accepted, processed, or persisted."""
    user_id, headers, _ = create_authenticated_user()
    secret_clipboard_payload = "def stolen_solution(): return True"

    # Even if malicious or buggy client passes clipboard fields, verify server schema ignores/drops them
    resp = client.post("/api/assessment/paste-attempt", headers=headers, json={
        "page_type": "coding",
        "question_id": "q_privacy",
        "clipboard_content": secret_clipboard_payload,
        "text": secret_clipboard_payload,
        "content": secret_clipboard_payload
    })
    assert resp.status_code == 200
    data = resp.json()
    record_id = data["record"]["id"]

    # Verify database table schema has NO clipboard column
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(paste_events)")
        columns = [col["name"] for col in cursor.fetchall()]
        assert "clipboard" not in columns
        assert "content" not in columns
        assert "text" not in columns
        assert "payload" not in columns

        cursor.execute("SELECT * FROM paste_events WHERE id = ?", (record_id,))
        row = dict(cursor.fetchone())
        # None of the values should contain the secret clipboard payload
        for k, v in row.items():
            assert secret_clipboard_payload not in str(v)

def test_8_paste_attempt_does_not_affect_scoring():
    """Verify that blocked paste attempts do not reduce scores or label students as cheating."""
    user_id, headers, _ = create_authenticated_user()
    attempt_id = f"score_test_{uuid.uuid4().hex[:8]}"

    # Record 5 blocked paste attempts
    for i in range(5):
        client.post("/api/assessment/paste-attempt", headers=headers, json={
            "page_type": "coding",
            "question_id": "two-sum",
            "attempt_id": attempt_id
        })
        time.sleep(0.1)

    # Now run evaluation on standard two sum code
    code = """def two_sum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        comp = target - num
        if comp in lookup:
            return [lookup[comp], i]
        lookup[num] = i
    return []
"""
    eval_resp = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 0
    })
    assert eval_resp.status_code == 200
    res_data = eval_resp.json()
    assert "score_data" in res_data
    assert res_data["overall_score"] == 100.0
    breakdown = res_data["score_data"]["breakdown"]
    # Perfect solution with 0 hints receives full score (100) regardless of paste attempts
    assert breakdown["correctness"]["points_earned"] == 40.0
    assert breakdown["independent"]["points_earned"] == 10.0
