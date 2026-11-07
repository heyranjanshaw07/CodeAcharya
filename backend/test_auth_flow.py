import pytest
from fastapi.testclient import TestClient
import uuid

from main import app
import auth

client = TestClient(app)

def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "online"

def test_unauthenticated_protected_routes():
    # Protected routes must return 401 Unauthorized without auth
    resp_me = client.get("/api/auth/me")
    assert resp_me.status_code == 401
    assert "Authentication required" in resp_me.json()["detail"] or "invalid" in resp_me.json()["detail"]

    resp_profile = client.get("/api/profile")
    assert resp_profile.status_code == 401
    assert "Authentication required" in resp_profile.json()["detail"]

    resp_recs = client.get("/api/recommendations")
    assert resp_recs.status_code == 401
    assert "Authentication required" in resp_recs.json()["detail"]

def test_login_unknown_account():
    resp = client.post("/api/auth/login", json={
        "email": "nonexistent_user_9999@example.com",
        "password": "Password123!"
    })
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]

def test_login_incorrect_password():
    resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "WrongPassword999!"
    })
    assert resp.status_code == 401
    assert "Invalid email or password" in resp.json()["detail"]

def test_successful_login_and_auth_persistence():
    resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["email"] == "student@codeacharya.ai"
    token = data["token"]

    # Test /api/auth/me with Bearer token
    resp_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_me.status_code == 200
    assert resp_me.json()["user"]["email"] == "student@codeacharya.ai"

    # Test protected /api/profile with Bearer token
    resp_profile = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp_profile.status_code == 200
    profile_data = resp_profile.json()
    assert "student_name" in profile_data
    assert "topic_mastery" in profile_data

    # Test protected /api/recommendations with Bearer token
    resp_recs = client.get("/api/recommendations", headers={"Authorization": f"Bearer {token}"})
    assert resp_recs.status_code == 200
    assert isinstance(resp_recs.json(), list)

def test_registration_flow_and_duplicate_prevention():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    full_name = "Dev Learner"
    password = "SecurePassword123!"

    # 1. Validation error: password too short
    resp_short = client.post("/api/auth/register", json={
        "full_name": full_name,
        "email": unique_email,
        "password": "short"
    })
    assert resp_short.status_code == 400
    assert "at least 8 characters" in resp_short.json()["detail"]

    # 2. Validation error: invalid email format
    resp_bad_email = client.post("/api/auth/register", json={
        "full_name": full_name,
        "email": "not-an-email",
        "password": password
    })
    assert resp_bad_email.status_code == 400
    assert "Invalid email" in resp_bad_email.json()["detail"]

    # 3. Validation error: empty or short name
    resp_bad_name = client.post("/api/auth/register", json={
        "full_name": "A",
        "email": unique_email,
        "password": password
    })
    assert resp_bad_name.status_code == 400
    assert "at least 2 characters" in resp_bad_name.json()["detail"]

    # 4. Successful registration
    resp_reg = client.post("/api/auth/register", json={
        "full_name": full_name,
        "email": unique_email,
        "password": password
    })
    assert resp_reg.status_code == 200
    reg_data = resp_reg.json()
    assert reg_data["user"]["email"] == unique_email
    assert reg_data["user"]["full_name"] == full_name
    token = reg_data["token"]

    # 5. Duplicate registration must fail gracefully
    resp_dup = client.post("/api/auth/register", json={
        "full_name": "Another Name",
        "email": unique_email,
        "password": password
    })
    assert resp_dup.status_code == 400
    assert "already exists" in resp_dup.json()["detail"]

    # 6. Verify new user profile is isolated and starts clean
    resp_prof = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp_prof.status_code == 200
    prof = resp_prof.json()
    assert prof["student_name"] == full_name
    assert prof["total_solved"] == 0

def test_logout_invalidates_session():
    # Login to acquire a session
    resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    assert resp.status_code == 200
    token = resp.json()["token"]

    # Verify session works
    resp_before = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_before.status_code == 200

    # Perform logout
    resp_logout = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp_logout.status_code == 200
    assert resp_logout.json()["status"] == "success"

    # Verify session is now invalidated in DB and returns 401
    resp_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_after.status_code == 401

    # Verify protected profile returns 401 with invalidated token
    resp_profile = client.get("/api/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp_profile.status_code == 401
