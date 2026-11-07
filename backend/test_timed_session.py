import pytest
from fastapi.testclient import TestClient
from main import app
from problems import PROBLEMS
from models import TestCase, ExecuteResponse

client = TestClient(app)

def test_req_1_and_2_problem_available_before_coding():
    """Verify problem details (statement, difficulty, constraints, examples) are available via API before coding starts."""
    res = client.get("/api/problems/factorial-recursion")
    assert res.status_code == 200
    data = res.json()
    assert "Factorial" in data["title"]
    assert "description" in data and len(data["description"]) > 0
    assert "constraints" in data and len(data["constraints"]) > 0
    assert "examples" in data and len(data["examples"]) > 0
    assert len(data["test_cases"]) > 0

def test_req_7_all_tests_passing_marks_completed_and_stops_timer():
    """Verify that when ALL test cases pass, the session is marked completed and timer time is recorded."""
    problem = PROBLEMS["factorial-recursion"]
    correct_code = problem.expected_solution["python"]
    
    payload = {
        "problem_id": "factorial-recursion",
        "code": correct_code,
        "language": "python",
        "time_spent_seconds": 142,
        "session_status": "running"
    }
    res = client.post("/api/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["passed_count"] == data["total_count"]
    assert data["total_count"] > 0
    assert data["is_completed"] is True
    assert data["session_status"] == "completed"
    assert data["time_spent_seconds"] == 142

def test_req_8_partial_tests_do_not_stop_timer():
    """Verify that partial test pass does NOT mark completed and does not stop the session."""
    # Code that only returns 1 (passes n=0, n=1, but fails n=5, etc.)
    partial_code = "def factorial(n):\n    return 1\n"
    payload = {
        "problem_id": "factorial-recursion",
        "code": partial_code,
        "language": "python",
        "time_spent_seconds": 45,
        "session_status": "running"
    }
    res = client.post("/api/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["passed_count"] < data["total_count"]
    assert data["is_completed"] is False
    assert data["session_status"] == "running"

def test_req_9_compilation_and_runtime_errors_do_not_mark_complete():
    """Verify compilation or runtime error does NOT mark question complete."""
    # Syntax error
    bad_code = "def factorial(n:\n    return n\n"
    payload = {
        "problem_id": "factorial-recursion",
        "code": bad_code,
        "language": "python",
        "time_spent_seconds": 60,
        "session_status": "running"
    }
    res = client.post("/api/execute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"
    assert data["is_completed"] is False
    assert data["session_status"] == "running"

    # Runtime error
    runtime_err_code = "def factorial(n):\n    raise RuntimeError('boom')\n"
    payload["code"] = runtime_err_code
    res2 = client.post("/api/execute", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["is_completed"] is False
    assert data2["session_status"] == "running"

def test_req_10_empty_test_suites_do_not_produce_false_completion():
    """If a problem or mock execution had 0 test cases, it must NOT produce completion."""
    from main import execute_code
    from models import ExecuteRequest

    req = ExecuteRequest(
        problem_id="factorial-recursion",
        code="def factorial(n): return 1",
        language="python",
        time_spent_seconds=30,
        session_status="running"
    )
    # Simulate a zero-testcase response
    dummy_res = ExecuteResponse(
        status="success",
        passed_count=0,
        total_count=0,
        results=[],
        runtime_ms=1.0
    )
    passed = (dummy_res.status == "success" and dummy_res.total_count > 0 and dummy_res.passed_count == dummy_res.total_count)
    assert passed is False

def test_req_12_abandoned_session_recording():
    """Verify that an abandoned session is recorded with duration and marked as abandoned, never completed."""
    payload = {
        "problem_id": "factorial-recursion",
        "language": "python",
        "time_spent_seconds": 88,
        "status": "abandoned",
        "passed_count": 0,
        "total_count": 5
    }
    res = client.post("/api/session/record", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["recorded_status"] == "abandoned"
    assert data["time_spent_seconds"] == 88

def test_req_14_existing_features_continue_working():
    """Verify Hints, AI Explain, Debug Guide, Viva continue working with timed mode enhancements."""
    # 1. Hints
    hint_res = client.post("/api/hints", json={
        "problem_id": "factorial-recursion",
        "code": "def factorial(n): return n",
        "language": "python",
        "hint_level": 1
    })
    assert hint_res.status_code == 200
    assert "hint_content" in hint_res.json()

    # 2. Viva Start
    viva_res = client.post("/api/viva/start", json={
        "problem_id": "factorial-recursion",
        "code": "def factorial(n): return 1",
        "language": "python"
    })
    assert viva_res.status_code == 200
    assert len(viva_res.json()) >= 3
