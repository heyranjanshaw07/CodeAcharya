import pytest
import uuid
import json
from typing import Tuple
from fastapi.testclient import TestClient

from main import app
from problems import PROBLEMS
from scoring_engine import (
    CodingScoringEngine, 
    DEFAULT_SCORING_WEIGHTS, 
    calculate_independent_score
)
from database import get_db

client = TestClient(app)

def create_authenticated_user(name: str = "Test Student") -> Tuple[str, str]:
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword2026!"
    resp = client.post("/api/auth/register", json={
        "full_name": name,
        "email": email,
        "password": pwd
    })
    assert resp.status_code == 200
    token = resp.json()["token"]
    user_id = resp.json()["user"]["id"]
    return user_id, token

# ===========================================================================
# 1. Hint Score Function & Curve Tests (Section 6 & 13)
# ===========================================================================

def test_hint_score_exact_curve():
    """Verify exact independent problem-solving score per hint usage table:
       0 hints -> 10/10
       1 hint  -> 9/10
       2 hints -> 7/10
       3 hints -> 4/10
       4 hints -> 1/10
       5 hints -> 1/10
       6 hints -> 1/10
    """
    assert calculate_independent_score(0) == 10
    assert calculate_independent_score(-1) == 10
    assert calculate_independent_score(1) == 9
    assert calculate_independent_score(2) == 7
    assert calculate_independent_score(3) == 4
    assert calculate_independent_score(4) == 1
    assert calculate_independent_score(5) == 1
    assert calculate_independent_score(10) == 1

def test_hint_score_api_endpoint():
    """Verify /api/hints/independent-score endpoint returns correct points and deduction."""
    r0 = client.post("/api/hints/independent-score", json={"unique_hints_used": 0})
    assert r0.status_code == 200
    assert r0.json()["score"] == 10
    assert r0.json()["points_deducted"] == 0

    r1 = client.post("/api/hints/independent-score", json={"unique_hints_used": 1})
    assert r1.status_code == 200
    assert r1.json()["score"] == 9
    assert r1.json()["points_deducted"] == 1

    r2 = client.post("/api/hints/independent-score", json={"unique_hints_used": 2})
    assert r2.status_code == 200
    assert r2.json()["score"] == 7
    assert r2.json()["points_deducted"] == 3

    r3 = client.post("/api/hints/independent-score", json={"unique_hints_used": 3})
    assert r3.status_code == 200
    assert r3.json()["score"] == 4
    assert r3.json()["points_deducted"] == 6

    r4 = client.post("/api/hints/independent-score", json={"unique_hints_used": 4})
    assert r4.status_code == 200
    assert r4.json()["score"] == 1
    assert r4.json()["points_deducted"] == 9

    r5 = client.post("/api/hints/independent-score", json={"unique_hints_used": 7})
    assert r5.status_code == 200
    assert r5.json()["score"] == 1
    assert r5.json()["points_deducted"] == 9

def test_hint_independence_from_other_dimensions():
    """Important requirement: Hint usage must not cause additional deductions from 
       correctness, complexity, code quality, or problem-solving approach.
       Its effect is limited to the 10-point independent problem-solving component.
    """
    code = """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    # Submission A: 0 hints
    rA = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 0
    })
    assert rA.status_code == 200
    dA = rA.json()
    bA = dA["score_data"]["breakdown"]

    # Submission B: 3 hints used
    rB = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 3
    })
    assert rB.status_code == 200
    dB = rB.json()
    bB = dB["score_data"]["breakdown"]

    # Correctness, complexity, quality, approach MUST be identical
    assert bA["correctness"]["points_earned"] == bB["correctness"]["points_earned"]
    assert bA["complexity"]["points_earned"] == bB["complexity"]["points_earned"]
    assert bA["quality"]["points_earned"] == bB["quality"]["points_earned"]
    assert bA["approach"]["points_earned"] == bB["approach"]["points_earned"]

    # Only independent score differs: 10 vs 4
    assert bA["independent"]["points_earned"] == 10.0
    assert bB["independent"]["points_earned"] == 4.0
    # Overall score diff is exactly 10 - 4 = 6 points
    assert round(dA["overall_score"] - dB["overall_score"], 1) == 6.0

# ===========================================================================
# 2. Correctness & Test Execution Tests (Section 2 & 13)
# ===========================================================================

def test_correctness_full_pass():
    """Verify optimal solution achieving 100% test pass receives 40/40 correctness points."""
    code = """def two_sum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in lookup:
            return [lookup[diff], i]
        lookup[num] = i
    return []
"""
    resp = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed_count"] == data["total_count"]
    corr = data["score_data"]["breakdown"]["correctness"]
    assert corr["points_earned"] == 40.0
    assert corr["max_points"] == 40.0
    assert corr["ratio"] == 1.0

def test_correctness_proportional_formula():
    """Verify (passed / total) * 40 formula for partial passes."""
    partial_code = """def two_sum(nums, target):
    if len(nums) >= 2 and nums[0] + nums[1] == target:
        return [0, 1]
    return []
"""
    resp = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": partial_code,
        "language": "python",
        "unique_hints_used": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed_count"] < data["total_count"]
    corr = data["score_data"]["breakdown"]["correctness"]
    expected_pts = round((data["passed_count"] / float(data["total_count"])) * 40.0, 1)
    assert abs(corr["points_earned"] - expected_pts) < 0.2

def test_zero_pass_and_compilation_error_points():
    """Verify 0 passed tests, compilation errors, and syntax errors get 0 correctness points."""
    # Zero tests passed
    r_zero = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target): return [999, 999]",
        "language": "python"
    })
    assert r_zero.status_code == 200
    assert r_zero.json()["score_data"]["breakdown"]["correctness"]["points_earned"] == 0.0

    # Syntax error
    r_syntax = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target): def broken :",
        "language": "python"
    })
    assert r_syntax.status_code == 200
    assert r_syntax.json()["score_data"]["breakdown"]["correctness"]["points_earned"] == 0.0

    # Infinite loop / timeout
    r_timeout = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target): \n    while True: pass",
        "language": "python"
    })
    assert r_timeout.status_code == 200
    assert r_timeout.json()["score_data"]["breakdown"]["correctness"]["points_earned"] == 0.0

# ===========================================================================
# 3. Problem-Solving Approach & Backtracking Requirement (Section 5 & 13)
# ===========================================================================

def test_backtracking_requirement_enforcement():
    """Section 5: If a question explicitly requires backtracking, a solution that violates 
       this requirement must not receive full approach points merely because its output is correct.
    """
    engine = CodingScoringEngine()
    backtracking_problem = {
        "id": "subsets",
        "title": "Subsets Generator",
        "category": "Recursion & Backtracking",
        "description": "Given an integer array nums of unique elements, return all possible subsets using backtracking.",
        "input_constraints": "1 <= nums.length <= 10"
    }

    # Approach 1: Non-backtracking (iterative power set or library call)
    non_backtrack_code = """def subsets(nums):
    result = [[]]
    for n in nums:
        result += [curr + [n] for curr in result]
    return result
"""
    eval_non = engine._evaluate_approach(non_backtrack_code, "python", backtracking_problem, True)
    assert eval_non["ratio"] < 0.8
    assert "backtracking" in eval_non["notes"].lower()

    # Approach 2: Proper backtracking with recursive choose/unchoose or backtrack helper
    backtrack_code = """def subsets(nums):
    res = []
    def backtrack(start, path):
        res.append(list(path))
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return res
"""
    eval_bt = engine._evaluate_approach(backtrack_code, "python", backtracking_problem, True)
    assert eval_bt["ratio"] >= 0.9
    assert eval_bt["ratio"] > eval_non["ratio"]

# ===========================================================================
# 4. Proportional Renormalization (Section 3, 7, 13)
# ===========================================================================

def test_renormalization_of_unavailable_dimensions():
    """Verify proportional weight renormalization when dimensions are N/A so sum of max points is 100."""
    engine = CodingScoringEngine()
    
    dimensions = {
        "correctness": {"ratio": 1.0, "is_available": True, "status": "evaluated"},
        "complexity": {"ratio": 0.0, "is_available": False, "status": "N/A", "notes": "Static parser unavailable"},
        "quality": {"ratio": 1.0, "is_available": True, "status": "evaluated"},
        "approach": {"ratio": 1.0, "is_available": True, "status": "evaluated"},
        "independent": {"ratio": 1.0, "is_available": True, "status": "evaluated"}
    }
    base_weights = {
        "correctness": 40.0,
        "complexity": 20.0,
        "quality": 15.0,
        "approach": 15.0,
        "independent": 10.0
    }
    
    breakdown, overall, is_renorm = engine._renormalize_and_score(dimensions, base_weights)
    assert is_renorm is True
    assert breakdown["complexity"]["is_available"] is False
    assert breakdown["complexity"]["points_earned"] == 0.0
    
    # Available weights sum = 40 + 15 + 15 + 10 = 80.
    # Total effective max should be 100.
    total_max = sum(b["max_points"] for b in breakdown.values())
    assert abs(total_max - 100.0) < 0.5
    assert overall == 100.0

def test_score_boundaries_0_to_100():
    """Verify score stays within [0, 100] even with extreme values."""
    engine = CodingScoringEngine()
    # 0 passed, 0 hints, broken code
    eval_zero = engine.evaluate(
        code="broken",
        language="python",
        problem=PROBLEMS["two-sum"],
        test_results=[{"passed": False}],
        passed_count=0,
        total_count=1,
        execution_status="error",
        runtime_ms=100.0,
        coding_time_seconds=10,
        unique_hints_used=5
    )
    assert 0.0 <= eval_zero["overall_score"] <= 100.0
    assert eval_zero["breakdown"]["independent"]["points_earned"] in (1.0, 1.2)

# ===========================================================================
# 5. Database Persistence & User Isolation (Section 10 & 13)
# ===========================================================================

def test_persistence_of_independent_score_and_hints():
    """Verify coding_scores and coding_attempts persist independent_score, unique_hints_used, and snapshot."""
    user_id, token = create_authenticated_user("Hint Student")
    headers = {"Authorization": f"Bearer {token}"}

    code = """def two_sum(nums, target):
    s = {}
    for i, x in enumerate(nums):
        if target - x in s:
            return [s[target - x], i]
        s[x] = i
    return []
"""
    idem_key = f"hint_test_idem_{uuid.uuid4().hex}"

    resp = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 2,
        "idempotency_key": idem_key
    })
    assert resp.status_code == 200
    data = resp.json()
    attempt_id = data["attempt_id"]
    assert data["unique_hints_used"] == 2
    assert data["independent_score"] == 7.0

    # Query DB directly to verify columns in coding_scores
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT independent_score, independent_max, unique_hints_used, code_snapshot
            FROM coding_scores WHERE attempt_id = ?
        """, (attempt_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 7.0  # independent_score
        assert row[1] == 10.0 # independent_max
        assert row[2] == 2    # unique_hints_used
        assert "def two_sum" in row[3] # code_snapshot

        # Verify coding_attempts table
        cursor.execute("""
            SELECT unique_hints_used, independent_score
            FROM coding_attempts WHERE id = ?
        """, (attempt_id,))
        att_row = cursor.fetchone()
        assert att_row is not None
        assert att_row[0] == 2
        assert att_row[1] == 7.0

    # Fetch history via API
    h_resp = client.get("/api/scores/history", headers=headers)
    assert h_resp.status_code == 200
    h_scores = h_resp.json()
    assert len(h_scores) >= 1
    assert h_scores[0]["unique_hints_used"] == 2
    assert h_scores[0]["independent_score"] == 7.0

    # Fetch analytics via API
    a_resp = client.get("/api/scores/analytics", headers=headers)
    assert a_resp.status_code == 200
    an_data = a_resp.json()
    assert an_data["average_hints_per_problem"] == 2.0
    assert an_data["hint_usage_trend"]["2_hints"] >= 1
    assert "independent" in an_data["dimension_averages"]
    assert an_data["dimension_averages"]["independent"] == 7.0

def test_idempotency_prevents_duplicate_records():
    """Verify repeated requests with identical idempotency key return cached result without duplicate records."""
    user_id, token = create_authenticated_user("Repeat Student")
    headers = {"Authorization": f"Bearer {token}"}
    idem_key = f"repeat_key_{uuid.uuid4().hex}"
    code = "def two_sum(nums, target): return []"

    r1 = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "idempotency_key": idem_key,
        "unique_hints_used": 1
    })
    assert r1.status_code == 200

    r2 = client.post("/api/execute", headers=headers, json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "idempotency_key": idem_key,
        "unique_hints_used": 1
    })
    assert r2.status_code == 200

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM coding_scores WHERE idempotency_key = ?", (idem_key,))
        assert cursor.fetchone()[0] == 1

def test_hidden_test_cases_protected():
    """Verify hidden test cases never expose raw inputs or expected outputs in execution response."""
    resp = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target): return []",
        "language": "python"
    })
    assert resp.status_code == 200
    data = resp.json()
    for res in data["results"]:
        if "[Hidden" in str(res.get("input")) or "[Hidden" in str(res.get("expected")):
            assert "[Hidden" in res["input"]
            assert "[Hidden" in res["expected"]
