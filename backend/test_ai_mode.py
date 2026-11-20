import os
import json
import pytest
from fastapi.testclient import TestClient

from main import app
from database import get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_token():
    # Login as default student
    resp = client.post("/api/auth/login", json={
        "email": "student@codeacharya.ai",
        "password": "Password123!"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["token"]


def test_ai_mode_lifecycle(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Start AI Mode Assessment
    start_resp = client.post("/api/ai-mode/start", json={
        "language": "python",
        "difficulty": "Easy",
        "topic": "Arrays",
        "num_questions": 3
    }, headers=headers)
    assert start_resp.status_code == 200, f"Start failed: {start_resp.text}"
    start_data = start_resp.json()

    assessment_id = start_data["assessment_id"]
    assert assessment_id.startswith("ai_asmt_")
    assert start_data["language"] == "python"
    assert start_data["difficulty"] == "Easy"
    assert start_data["topic"] == "Arrays"
    assert len(start_data["questions"]) == 3

    # Security check: verify no hidden test cases or expected solutions exposed to frontend
    for q in start_data["questions"]:
        assert "expected_solution" not in q
        for tc in q.get("sample_test_cases", []):
            assert not tc.get("is_hidden", False)

    first_q = start_data["questions"][0]
    first_qid = first_q["id"]

    # 2. Test Execution against Public Test Cases (Run Code)
    exec_resp = client.post("/api/ai-mode/execute", json={
        "assessment_id": assessment_id,
        "question_id": first_qid,
        "code": first_q["starter_code"],
        "language": "python"
    }, headers=headers)
    assert exec_resp.status_code == 200, f"Execute failed: {exec_resp.text}"
    exec_data = exec_resp.json()
    assert "status" in exec_data
    assert "passed_count" in exec_data
    assert "total_count" in exec_data

    # 3. Test Submission against Hidden Test Cases (Submit Solution)
    sub_resp = client.post("/api/ai-mode/submit-question", json={
        "assessment_id": assessment_id,
        "question_id": first_qid,
        "code": first_q["starter_code"],
        "language": "python",
        "time_spent_seconds": 45,
        "tab_switch_count": 1
    }, headers=headers)
    assert sub_resp.status_code == 200, f"Submit failed: {sub_resp.text}"
    sub_data = sub_resp.json()
    assert "status" in sub_data
    assert "score" in sub_data
    assert "passed_count" in sub_data
    assert "total_count" in sub_data
    # Hidden test inputs must be masked
    for r in sub_data.get("results", []):
        if r.get("is_hidden"):
            assert "input" not in r
            assert "expected_output" not in r

    # 4. Finish Assessment
    finish_resp = client.post("/api/ai-mode/finish", json={
        "assessment_id": assessment_id,
        "total_time_seconds": 120,
        "tab_switch_count": 1
    }, headers=headers)
    assert finish_resp.status_code == 200, f"Finish failed: {finish_resp.text}"
    finish_data = finish_resp.json()
    assert finish_data["status"] == "completed"
    assert "overall_score" in finish_data
    assert finish_data["total_time_seconds"] == 120

    # 5. Fetch Session Data
    session_resp = client.get(f"/api/ai-mode/session/{assessment_id}", headers=headers)
    assert session_resp.status_code == 200
    sess_data = session_resp.json()
    assert sess_data["status"] == "completed"
    assert sess_data["total_count"] == 3

    # 6. Download Official PDF Report
    pdf_resp = client.get(f"/api/ai-mode/report/pdf/{assessment_id}", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content.startswith(b"%PDF-")
    assert len(pdf_resp.content) > 1000
    print(f"Generated PDF Size: {len(pdf_resp.content)} bytes")


def test_ai_mode_topics_and_languages(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test C++ language with searching & sorting topic
    resp = client.post("/api/ai-mode/start", json={
        "language": "cpp",
        "difficulty": "Medium",
        "topic": "Searching and Sorting",
        "num_questions": 3
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["language"] == "cpp"
    assert len(data["questions"]) == 3
    for q in data["questions"]:
        assert "#include" in q["starter_code"] or "int" in q["starter_code"]
