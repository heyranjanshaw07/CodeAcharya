import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.problems import PROBLEMS
from backend.question_store import get_question_store
from backend.deduplication import is_duplicate_problem, compute_token_jaccard, compute_string_similarity
from backend.question_validator import validate_problem_schema, ensure_progressive_hints, ensure_multi_language_starter_code
from backend.question_generator import generate_blueprint_fallback, generate_coding_problems_batch, TOPIC_SUBTOPICS

client = TestClient(app)

def test_health_check():
    """Verify backend health and problem metrics."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "total_problems" in data
    assert "curated_problems_count" in data
    assert "generated_problems_count" in data
    assert "has_gemini_key" in data


def test_topics_endpoint_with_subtopics_and_counts():
    """Verify /api/topics returns all topics, subtopic lists, and curated/generated breakdown."""
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics_list = response.json()
    assert isinstance(topics_list, list)
    assert len(topics_list) >= 8
    
    recursion_topic = next((t for t in topics_list if t["name"] == "Recursion & Backtracking"), None)
    assert recursion_topic is not None
    assert "subtopics" in recursion_topic
    assert len(recursion_topic["subtopics"]) > 1
    assert "curated_count" in recursion_topic
    assert recursion_topic["curated_count"] >= 1
    assert "counts" in recursion_topic


def test_problems_endpoint_filtering():
    """Verify /api/problems supports filtering by topic, difficulty, subtopic, and source."""
    # 1. Base list
    resp = client.get("/api/problems")
    assert resp.status_code == 200
    all_problems = resp.json()
    assert len(all_problems) >= 30

    # 2. Filter by topic
    resp_topic = client.get("/api/problems?topic=Recursion & Backtracking")
    assert resp_topic.status_code == 200
    rec_probs = resp_topic.json()
    assert all(p["topic"] == "Recursion & Backtracking" for p in rec_probs)

    # 3. Filter by source=curated
    resp_curated = client.get("/api/problems?source=curated")
    assert resp_curated.status_code == 200
    curated_probs = resp_curated.json()
    assert all(not p.get("is_generated", False) for p in curated_probs)


def test_single_question_generation_endpoint():
    """Test POST /api/generate-question schema and persistence."""
    payload = {
        "topic": "Dynamic Programming",
        "difficulty": "Easy",
        "language": "python",
        "subtopic": "Memoization",
        "count": 1
    }
    response = client.post("/api/generate-question", json=payload)
    assert response.status_code == 200
    problem = response.json()

    # Schema integrity checks
    assert "id" in problem and problem["id"]
    assert "title" in problem and problem["title"]
    assert problem["topic"] == "Dynamic Programming"
    assert problem["difficulty"] == "Easy"
    assert "description" in problem and len(problem["description"]) > 10
    assert "constraints" in problem and isinstance(problem["constraints"], list)
    assert "examples" in problem and len(problem["examples"]) >= 1
    assert "starter_code" in problem
    assert "python" in problem["starter_code"]
    assert "c" in problem["starter_code"]
    assert "cpp" in problem["starter_code"]
    assert "java" in problem["starter_code"]
    assert "test_cases" in problem and len(problem["test_cases"]) >= 2
    assert "progressive_hints" in problem
    assert len(problem["progressive_hints"]) >= 2
    assert "expected_solution" in problem
    assert problem.get("is_generated") is True
    assert "badge" in problem

    # Persistence verification: must be retrievable from /api/problems/{id}
    detail_resp = client.get(f"/api/problems/{problem['id']}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == problem["id"]
    assert detail_data["title"] == problem["title"]


def test_batch_question_generation_endpoint():
    """Test POST /api/problems/generate-batch with within-batch deduplication."""
    payload = {
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "language": "python",
        "subtopic": "Hash Maps & Sets",
        "count": 3
    }
    response = client.post("/api/problems/generate-batch", json=payload)
    assert response.status_code == 200
    batch_data = response.json()

    assert "questions" in batch_data
    assert batch_data["count"] == 3
    assert len(batch_data["questions"]) == 3

    # Check that all questions in batch have unique IDs and distinct titles
    ids = [q["id"] for q in batch_data["questions"]]
    titles = [q["title"].lower().strip() for q in batch_data["questions"]]
    assert len(set(ids)) == 3
    assert len(set(titles)) == 3

    for q in batch_data["questions"]:
        assert q["topic"] == "Arrays & Hashing"
        assert q["difficulty"] == "Easy"
        assert len(q["test_cases"]) >= 2


def test_deduplication_engine():
    """Verify deduplication detects identical or highly similar problem titles/descriptions."""
    # Exact title
    is_dup, reason = is_duplicate_problem({"title": "Fibonacci Sequence", "id": "fib-1"}, ["Fibonacci Sequence"])
    assert is_dup is True
    assert "title" in reason.lower()

    # High token Jaccard similarity
    sim = compute_token_jaccard("Find Maximum Subarray Sum in Array", "Maximum Subarray Sum in Array")
    assert sim > 0.65

    # Low similarity
    is_dup_diff, _ = is_duplicate_problem({"title": "Two Sum Problem", "id": "two-sum-prob"}, ["Reverse Linked List", "Valid Palindrome"])
    assert is_dup_diff is False


def test_validation_and_sanitization():
    """Test problem schema validator and progressive hint normalizers."""
    raw_problem = {
        "id": "test-sample-problem",
        "title": "Sample Problem",
        "topic": "Trees & Binary Search Trees",
        "difficulty": "Medium",
        "description": "Calculate tree depth",
        "constraints": ["1 <= N <= 1000"],
        "examples": [{"input": "root = [3,9,20]", "output": "3", "explanation": "Depth is 3"}],
        "starter_code": {"python": "def maxDepth(root):\n    pass\n"},
        "test_cases": [{"input": "[3,9,20]", "expected_output": "3", "is_hidden": False}, {"input": "[]", "expected_output": "0", "is_hidden": True}],
        "hints": ["Check child heights"],
        "expected_solution": "def maxDepth(root):\n    return 3\n"
    }

    # Ensure schema validation passes
    is_valid, errors = validate_problem_schema(raw_problem)
    assert is_valid is True, f"Validation errors: {errors}"
    
    # Ensure helper augmenters work
    ensure_multi_language_starter_code(raw_problem)
    ensure_progressive_hints(raw_problem)
    assert "c" in raw_problem["starter_code"]
    assert "cpp" in raw_problem["starter_code"]
    assert "java" in raw_problem["starter_code"]
    assert "progressive_hints" in raw_problem
    assert len(raw_problem["progressive_hints"]) == 4


def test_execution_on_generated_problem_solution():
    """Verify that expected solution on a generated problem passes test execution."""
    payload = {
        "topic": "Recursion & Backtracking",
        "difficulty": "Easy",
        "language": "python",
        "count": 1
    }
    gen_res = client.post("/api/generate-question", json=payload)
    assert gen_res.status_code == 200
    problem = gen_res.json()

    exp_sol = problem.get("expected_solution")
    code_to_run = exp_sol.get("python") if isinstance(exp_sol, dict) else exp_sol
    assert code_to_run and len(code_to_run) > 0

    # Execute the expected_solution against the generated problem's test cases
    exec_res = client.post("/api/execute", json={
        "problem_id": problem["id"],
        "code": code_to_run,
        "language": "python"
    })
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["passed_count"] == exec_data["total_count"]
    assert exec_data["passed_count"] > 0


def test_rate_limiter_protection():
    """Verify rate limiter blocks excessive requests beyond limit."""
    from backend.rate_limiter import RateLimiter
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    assert limiter.is_allowed("client-test-1")[0] is True
    assert limiter.is_allowed("client-test-1")[0] is True
    assert limiter.is_allowed("client-test-1")[0] is True
    allowed, retry_after = limiter.is_allowed("client-test-1")
    assert allowed is False
    assert retry_after > 0


def test_static_regression_curated_problems():
    """Ensure all original curated static problems remain intact and executable."""
    original_ids = ["factorial-recursion", "two-sum", "valid-palindrome"]
    for pid in original_ids:
        assert pid in PROBLEMS
        p = PROBLEMS[pid]
        assert not getattr(p, "is_generated", False)
        
        # Test endpoint
        resp = client.get(f"/api/problems/{pid}")
        assert resp.status_code == 200
        pdata = resp.json()
        assert pdata["id"] == pid
        assert "starter_code" in pdata
