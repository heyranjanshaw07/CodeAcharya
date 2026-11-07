import pytest
from fastapi.testclient import TestClient
from main import app
from problems import PROBLEMS
from models import Problem

client = TestClient(app)

def test_debug_guide_syntax_error():
    """Test Debug Guide with code containing a syntax error."""
    broken_code = "def factorial(n)\n    return n * factorial(n-1)"
    res = client.post("/api/debug", json={
        "problem_id": "factorial-recursion",
        "code": broken_code,
        "language": "python",
        "error_message": None,
        "has_run": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "suspected_static_issue"
    assert "Syntax Error" in data["primary_symptom"] or "syntax" in data["bug_summary"].lower()
    assert len(data["investigation_steps"]) > 0

def test_debug_guide_logical_bug_factorial_zero():
    """Test Debug Guide with logically incorrect code (returning 0 in factorial base case)."""
    buggy_code = """def factorial(n):
    if n <= 1:
        return 0
    return n * factorial(n - 1)
"""
    res = client.post("/api/debug", json={
        "problem_id": "factorial-recursion",
        "code": buggy_code,
        "language": "python",
        "has_run": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "suspected_static_issue"
    assert "0" in data["primary_symptom"]
    assert "return 0" in data["relevant_section"] or "0" in data["bug_summary"]
    assert "why_it_occurs" in data
    assert len(data["edge_cases_to_check"]) > 0

def test_debug_guide_with_test_failure():
    """Test Debug Guide with verified test case failure context."""
    code = """def factorial(n):
    return n * (n - 1)
"""
    res = client.post("/api/debug", json={
        "problem_id": "factorial-recursion",
        "code": code,
        "language": "python",
        "failing_input": "5",
        "expected_output": "120",
        "actual_output": "20",
        "has_run": True
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "verified_runtime_error"
    assert "5" in data["primary_symptom"] or "120" in data["bug_summary"]
    assert "why_it_occurs" in data
    assert len(data["investigation_steps"]) >= 3

def test_debug_guide_clean_code_before_run():
    """Test Debug Guide before running code on clean code: must say no clear issue identified, not invent bugs."""
    clean_code = """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    res = client.post("/api/debug", json={
        "problem_id": "factorial-recursion",
        "code": clean_code,
        "language": "python",
        "has_run": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "clean"
    assert data["primary_symptom"] == "No clear issue identified"
    assert "clean" in data["bug_summary"].lower() or "sound" in data["why_it_occurs"].lower()

def test_debug_guide_empty_code():
    """Test Debug Guide with empty code string."""
    res = client.post("/api/debug", json={
        "problem_id": "factorial-recursion",
        "code": "   ",
        "language": "python"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "empty_code"
    assert "empty" in data["primary_symptom"].lower()
    assert len(data["investigation_steps"]) > 0

def test_explain_code_valid_python():
    """Test Explain Code with valid Python code."""
    valid_code = """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    res = client.post("/api/explain", json={
        "problem_id": "factorial-recursion",
        "code": valid_code,
        "language": "python"
    })
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "algorithmic_approach" in data
    assert "time_complexity" in data
    assert "space_complexity" in data
    assert "execution_flow" in data
    assert len(data["execution_flow"]) >= 3
    assert "key_components" in data
    assert "edge_cases_and_limitations" in data

def test_explain_code_supported_language_c():
    """Test Explain Code with C solution."""
    c_code = """#include <stdio.h>

long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}"""
    res = client.post("/api/explain", json={
        "problem_id": "factorial-recursion",
        "code": c_code,
        "language": "c"
    })
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "time_complexity" in data
    assert "space_complexity" in data
    assert "key_components" in data
    assert "execution_flow" in data

def test_explain_code_empty_code():
    """Test Explain Code with empty code."""
    res = client.post("/api/explain", json={
        "problem_id": "factorial-recursion",
        "code": "",
        "language": "python"
    })
    assert res.status_code == 200
    data = res.json()
    assert "empty" in data["summary"].lower()
    assert data["time_complexity"] == "N/A"
    assert data["space_complexity"] == "N/A"

def test_debug_and_explain_dynamic_problem():
    """Test Debug Guide and Explain Code with dynamically provided problem title and statement."""
    res_debug = client.post("/api/debug", json={
        "problem_id": "dynamic-custom-problem-99",
        "code": "def solve(x):\n    return x * 2",
        "language": "python",
        "problem_title": "Double the Number",
        "problem_statement": "Given an integer x, return x multiplied by 2."
    })
    assert res_debug.status_code == 200
    assert res_debug.json()["status"] == "clean"

    res_explain = client.post("/api/explain", json={
        "problem_id": "dynamic-custom-problem-99",
        "code": "def solve(x):\n    return x * 2",
        "language": "python",
        "problem_title": "Double the Number",
        "problem_statement": "Given an integer x, return x multiplied by 2."
    })
    assert res_explain.status_code == 200
    assert "Double the Number" in res_explain.json()["summary"] or "solve" in res_explain.json()["purpose"]
