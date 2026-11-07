import pytest
from fastapi.testclient import TestClient
import uuid

from main import app
import auth

client = TestClient(app)

def test_req_1_successful_login():
    """Requirement 9.1: Test successful login returns token, user info and sets session cookie."""
    resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Login successful"
    assert data["user"]["email"] == "student@codeacharya.ai"
    assert data["user"]["full_name"] == "Student Learner"
    assert "token" in data
    assert "codeacharya_session" in resp.cookies

def test_req_2_incorrect_password_and_unknown_account():
    """Requirement 9.2: Test incorrect password and unknown account both fail with 401."""
    # Unknown account
    resp_unknown = client.post("/api/auth/login", json={
        "email": "ghost_unknown_user@codeacharya.ai",
        "password": "Password123!"
    })
    assert resp_unknown.status_code == 401
    assert "Invalid email or password" in resp_unknown.json()["detail"]

    # Incorrect password
    resp_bad_pwd = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "WrongPassword2026!"
    })
    assert resp_bad_pwd.status_code == 401
    assert "Invalid email or password" in resp_bad_pwd.json()["detail"]

def test_req_3_successful_registration():
    """Requirement 9.3: Test successful registration creates user in DB and default isolated profile."""
    unique_email = f"learner_{uuid.uuid4().hex[:8]}@example.com"
    full_name = "Marie Curie"
    password = "SciencePassword2026!"

    resp = client.post("/api/auth/register", json={
        "full_name": full_name,
        "email": unique_email,
        "password": password
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == unique_email
    assert data["user"]["full_name"] == full_name
    token = data["token"]
    assert "codeacharya_session" in resp.cookies

    # Verify user profile was initialized for this specific user
    resp_profile = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp_profile.status_code == 200
    prof = resp_profile.json()
    assert prof["student_name"] == full_name
    assert prof["total_solved"] == 0

def test_req_4_duplicate_email_registration():
    """Requirement 9.4: Test duplicate email registration fails gracefully with 400."""
    resp = client.post("/api/auth/register", json={
        "full_name": "Duplicate Student",
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]

def test_req_5_form_validation():
    """Requirement 9.5: Test server-side validation for required fields, email format, password policy."""
    # Short password (< 8 chars)
    r1 = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "valid@example.com",
        "password": "123"
    })
    assert r1.status_code == 400
    assert "at least 8 characters" in r1.json()["detail"]

    # Invalid email format
    r2 = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "invalid-email-string",
        "password": "Password123!"
    })
    assert r2.status_code == 400
    assert "Invalid email" in r2.json()["detail"]

    # Short name (< 2 chars)
    r3 = client.post("/api/auth/register", json={
        "full_name": " ",
        "email": "valid@example.com",
        "password": "Password123!"
    })
    assert r3.status_code == 400
    assert "at least 2 characters" in r3.json()["detail"]

def test_req_6_authentication_persistence():
    """Requirement 9.6: Test authentication state restoration after page refresh via /api/auth/me."""
    login_resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    token = login_resp.json()["token"]

    # Simulate page refresh by querying /api/auth/me with Bearer token
    resp_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_me.status_code == 200
    assert resp_me.json()["user"]["email"] == "student@codeacharya.ai"

    # Query with session cookie
    resp_cookie = client.get("/api/auth/me", cookies={"codeacharya_session": token})
    assert resp_cookie.status_code == 200
    assert resp_cookie.json()["user"]["email"] == "student@codeacharya.ai"

def test_req_7_accessing_protected_routes_without_auth():
    """Requirement 9.7: Test accessing protected routes without authentication returns 401."""
    anon_client = TestClient(app)
    # /api/auth/me without token
    r1 = anon_client.get("/api/auth/me")
    assert r1.status_code == 401
    assert "Authentication required" in r1.json()["detail"]

    # /api/profile without token
    r2 = anon_client.get("/api/profile")
    assert r2.status_code == 401
    assert "Authentication required" in r2.json()["detail"]

    # /api/recommendations without token
    r3 = anon_client.get("/api/recommendations")
    assert r3.status_code == 401
    assert "Authentication required" in r3.json()["detail"]

def test_req_10_confirming_logout_invalidates_session():
    """Requirement 9.10: Test logout deletes session token from DB and revokes credentials."""
    login_resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    token = login_resp.json()["token"]

    # Verify session is initially valid
    r_valid = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_valid.status_code == 200

    # Call logout
    logout_resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"

    # Subsequent /api/auth/me must return 401
    r_invalid = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_invalid.status_code == 401

    # Protected /api/profile must return 401
    r_prof = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert r_prof.status_code == 401

def test_req_13_existing_codeacharya_features_operational():
    """Requirement 9.13: Verify coding executor, mentor hints, viva, and analytics work."""
    login_resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Code execution
    exec_resp = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "language": "python"
    }, headers=headers)
    assert exec_resp.status_code == 200
    assert exec_resp.json()["passed_count"] == 5

    # 2. Hints
    hint_resp = client.post("/api/hints", json={
        "problem_id": "factorial-recursion",
        "code": "def factorial(n):\n    return 0",
        "language": "python",
        "hint_level": 1
    }, headers=headers)
    assert hint_resp.status_code == 200
    assert "hint_content" in hint_resp.json()

    # 3. Viva questions start
    viva_start = client.post("/api/viva/start", json={
        "problem_id": "factorial-recursion",
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "language": "python"
    }, headers=headers)
    assert viva_start.status_code == 200
    assert len(viva_start.json()) > 0

    # 4. Viva evaluation
    viva_eval = client.post("/api/viva/evaluate", json={
        "problem_id": "factorial-recursion",
        "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "question_id": 1,
        "question": "What is the base case in factorial?",
        "category": "conceptual",
        "student_answer": "The base case is when n is 0 or 1, which returns 1 to prevent infinite recursion."
    }, headers=headers)
    assert viva_eval.status_code == 200
    assert viva_eval.json()["overall_score"] > 0
