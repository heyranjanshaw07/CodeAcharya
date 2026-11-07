import pytest
import uuid
import json
import sqlite3
from fastapi.testclient import TestClient

from main import app
import auth
from database import get_db, format_timestamp_ist, utc_iso_now, init_database
from seed_data import seed_questions

client = TestClient(app)

def test_1_user_registration_and_argon2_hashing():
    """Verify registration creates user with Argon2id hash in database."""
    unique_email = f"learner_{uuid.uuid4().hex[:8]}@example.com"
    full_name = "Alan Turing"
    password = "EnigmaSecurePassword2026!"

    resp = client.post("/api/auth/register", json={
        "full_name": full_name,
        "email": unique_email,
        "password": password
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == unique_email
    assert data["user"]["full_name"] == full_name
    assert "token" in data
    assert "codeacharya_session" in resp.cookies

    # Verify directly in SQLite database that password was hashed with Argon2id
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, auth_provider FROM users WHERE email = ?", (unique_email,))
        row = cursor.fetchone()
        assert row is not None
        assert row["auth_provider"] == "local"
        assert row["password_hash"].startswith("$argon2id$")
        # Verify plaintext password is NEVER stored
        assert password not in row["password_hash"]

def test_2_duplicate_email_registration_rejected():
    """Verify duplicate email registration is rejected cleanly with 400."""
    email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "ValidPassword123!"

    # First registration
    r1 = client.post("/api/auth/register", json={
        "full_name": "First User",
        "email": email,
        "password": pwd
    })
    assert r1.status_code == 200

    # Second registration with same email
    r2 = client.post("/api/auth/register", json={
        "full_name": "Second User",
        "email": email,
        "password": pwd
    })
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"].lower()

def test_3_signin_credential_validation():
    """Verify sign in works with valid credentials and rejects bad credentials."""
    email = f"signin_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "CorrectPassword123!"

    client.post("/api/auth/register", json={
        "full_name": "Sign In Test User",
        "email": email,
        "password": pwd
    })

    # 1. Correct credentials
    r_success = client.post("/api/auth/login", json={
        "email": email,
        "password": pwd,
        "remember_me": True
    })
    assert r_success.status_code == 200
    data = r_success.json()
    assert data["user"]["email"] == email
    assert "token" in data
    assert "codeacharya_session" in r_success.cookies

    # 2. Incorrect password
    r_bad_pwd = client.post("/api/auth/login", json={
        "email": email,
        "password": "WrongPassword999!"
    })
    assert r_bad_pwd.status_code == 401
    assert "Invalid email or password" in r_bad_pwd.json()["detail"]

    # 3. Unknown email
    r_unknown = client.post("/api/auth/login", json={
        "email": "nonexistent_account_99999@nowhere.ai",
        "password": pwd
    })
    assert r_unknown.status_code == 401
    assert "Invalid email or password" in r_unknown.json()["detail"]

def test_4_google_auth_flow_and_idempotent_account_retrieval():
    """Verify Google token verification, user creation, and idempotent login."""
    unique_sub = f"g_sub_{uuid.uuid4().hex[:12]}"
    mock_token = f"mock_google_token_{unique_sub}"

    # 1. First Google login -> creates user
    r1 = client.post("/api/auth/google", json={
        "id_token": mock_token,
        "remember_me": True
    })
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["user"]["auth_provider"] == "google"
    user_id = d1["user"]["id"]
    token1 = d1["token"]

    # 2. Second Google login with same token/sub -> retrieves same user without duplicate
    r2 = client.post("/api/auth/google", json={
        "id_token": mock_token,
        "remember_me": False
    })
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["user"]["id"] == user_id
    assert d2["user"]["email"] == d1["user"]["email"]

    # Verify only ONE user record was created in SQLite database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE provider_subject_id = ?", (unique_sub,))
        assert cursor.fetchone()[0] == 1

def test_5_logout_invalidates_session():
    """Verify logout invalidates session token in DB and clears session cookie."""
    # Register and login
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "ValidPassword123!"
    reg_res = client.post("/api/auth/register", json={
        "full_name": "Logout Tester",
        "email": email,
        "password": pwd
    })
    token = reg_res.json()["token"]

    # Verify session is valid
    me_before = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_before.status_code == 200

    # Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

    # Verify session is now rejected
    me_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_after.status_code == 401

def test_6_protected_routes_reject_unauthenticated():
    """Verify all protected API endpoints return 401 Unauthorized for unauthenticated requests."""
    anon = TestClient(app)

    routes = [
        "/api/auth/me",
        "/api/profile",
        "/api/recommendations",
        "/api/attempts",
        "/api/tab-switches",
        "/api/viva/history"
    ]
    for r in routes:
        resp = anon.get(r)
        assert resp.status_code == 401, f"Route {r} did not return 401"
        assert "Authentication required" in resp.json()["detail"] or "invalid" in resp.json()["detail"]

def test_7_user_data_isolation_and_ownership():
    """Verify User B cannot access User A's coding attempts or tab switch records."""
    # User A
    user_a_email = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    r_a = client.post("/api/auth/register", json={
        "full_name": "User Alpha",
        "email": user_a_email,
        "password": "PasswordAlpha123!"
    })
    token_a = r_a.json()["token"]
    user_a_id = r_a.json()["user"]["id"]

    # User B
    user_b_email = f"user_b_{uuid.uuid4().hex[:8]}@example.com"
    r_b = client.post("/api/auth/register", json={
        "full_name": "User Beta",
        "email": user_b_email,
        "password": "PasswordBeta123!"
    })
    token_b = r_b.json()["token"]
    user_b_id = r_b.json()["user"]["id"]

    # User A records a coding attempt with tab switches
    exec_res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target):\n    lookup = {}\n    for i, n in enumerate(nums):\n        if target - n in lookup:\n            return [lookup[target - n], i]\n        lookup[n] = i\n    return []",
        "language": "python",
        "time_spent_seconds": 120,
        "tab_switch_count": 2,
        "total_time_away_seconds": 15,
        "tab_switch_history": [
            {"id": f"ts_{uuid.uuid4().hex[:8]}", "switch_time": "2026-10-22T14:00:00Z", "return_time": "2026-10-22T14:00:15Z", "time_away_seconds": 15, "status": "returned"}
        ]
    }, headers={"Authorization": f"Bearer {token_a}"})
    assert exec_res.status_code == 200

    # User A views attempts and tab switches
    a_attempts = client.get("/api/attempts", headers={"Authorization": f"Bearer {token_a}"}).json()
    assert len(a_attempts) >= 1
    assert a_attempts[0]["user_id"] == user_a_id

    a_switches = client.get("/api/tab-switches", headers={"Authorization": f"Bearer {token_a}"}).json()
    assert len(a_switches) >= 1
    assert a_switches[0]["user_id"] == user_a_id
    assert "IST" in a_switches[0]["event_timestamp_ist"]

    # User B queries their own attempts and tab switches -> must be empty, isolated from User A
    b_attempts = client.get("/api/attempts", headers={"Authorization": f"Bearer {token_b}"}).json()
    assert len(b_attempts) == 0

    b_switches = client.get("/api/tab-switches", headers={"Authorization": f"Bearer {token_b}"}).json()
    assert len(b_switches) == 0

def test_8_dashboard_genuine_empty_state():
    """Verify new user profile has 0 total_solved and 0% mastery without arbitrary mock numbers."""
    email = f"fresh_learner_{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/api/auth/register", json={
        "full_name": "Fresh Student",
        "email": email,
        "password": "Password123!"
    })
    token = r.json()["token"]

    prof_res = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert prof_res.status_code == 200
    prof = prof_res.json()

    # Must be real 0s, not fake numbers
    assert prof["total_solved"] == 0
    assert prof["total_attempts"] == 0
    assert prof["total_debug_time_mins"] == 0
    assert prof["total_coding_time_seconds"] == 0
    for topic, mastery in prof["topic_mastery"].items():
        assert mastery == 0, f"Topic {topic} had non-zero initial mastery: {mastery}"

def test_9_relational_database_questions_seeded_and_idempotent():
    """Verify curated coding questions exist in coding_questions relational table."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM coding_questions WHERE is_active = 1")
        count = cursor.fetchone()[0]
        assert count > 50, f"Expected >50 questions in database, found {count}"

    # Re-running seed_questions must be idempotent
    seed_questions()
    new_seeded = seed_questions()
    assert new_seeded == 0


def test_10_tab_switch_ist_timezone_conversion():
    """Verify UTC ISO timestamps are correctly formatted in Asia/Kolkata (IST = UTC+05:30)."""
    utc_str = "2026-10-22T10:00:00Z"
    ist_str = format_timestamp_ist(utc_str)
    # UTC 10:00:00 + 05:30 = 15:30:00 IST
    assert "15:30:00 IST" in ist_str
    assert "2026-10-22" in ist_str
