import pytest
from fastapi.testclient import TestClient
from main import app
from scoring_engine import CodingScoringEngine, calculate_independent_score
from main import PROBLEMS

client = TestClient(app)

def test_empty_code_submission():
    """Requirement 1 & 2: Empty code must receive 0 overall score, 0 correctness, and not_evaluated status."""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "",
        "language": "python",
        "unique_hints_used": 0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "error"
    assert data["passed_count"] == 0
    assert data["overall_score"] == 0.0

    score_data = data["score_data"]
    assert score_data["is_empty_submission"] is True
    assert score_data["scoring_status"] == "not_evaluated"

    bd = score_data["breakdown"]
    assert bd["correctness"]["points_earned"] == 0.0
    assert bd["complexity"]["points_earned"] == 0.0
    assert bd["complexity"]["is_available"] is False
    assert bd["complexity"]["status"] == "N/A"
    assert bd["quality"]["points_earned"] == 0.0
    assert bd["quality"]["status"] == "not_evaluated"
    assert bd["approach"]["points_earned"] == 0.0
    assert bd["approach"]["status"] == "not_evaluated"
    assert bd["independent"]["points_earned"] == 0.0

    total_breakdown = sum(dim["points_earned"] for dim in bd.values())
    assert total_breakdown == 0.0
    assert total_breakdown == data["overall_score"]

def test_whitespace_only_submission():
    """Requirement 1: Whitespace-only code must be detected as empty and receive 0 score."""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "   \n\t  \n  ",
        "language": "python",
        "unique_hints_used": 0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["overall_score"] == 0.0
    assert data["score_data"]["is_empty_submission"] is True
    assert data["score_data"]["scoring_status"] == "not_evaluated"
    assert data["score_data"]["breakdown"]["quality"]["points_earned"] == 0.0
    assert data["score_data"]["breakdown"]["complexity"]["points_earned"] == 0.0

def test_comments_only_submission():
    """Requirement 1: Code containing only comments without executable statements receives 0 score."""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "# Just a comment\n# Another comment\n",
        "language": "python",
        "unique_hints_used": 0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["overall_score"] == 0.0
    assert data["score_data"]["is_empty_submission"] is True
    assert data["score_data"]["scoring_status"] == "not_evaluated"

def test_empty_code_with_hints_does_not_award_points():
    """Requirement 6: Hint points alone must not produce a misleading final score when code is empty."""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "",
        "language": "python",
        "unique_hints_used": 2  # 2 hints would normally yield 7 points
    })
    assert res.status_code == 200
    data = res.json()
    assert data["overall_score"] == 0.0

    bd = data["score_data"]["breakdown"]
    # Hint tracking is preserved in raw_score, but points_earned towards coding score is strictly 0.0
    assert bd["independent"]["raw_score"] == 7
    assert bd["independent"]["points_earned"] == 0.0
    assert bd["independent"]["status"] == "pending"

    # Total must be 0.0
    assert sum(dim["points_earned"] for dim in bd.values()) == 0.0

def test_syntax_error_code():
    """Requirement 1, 3, 4: Syntax error code receives 0 correctness, N/A complexity, 0 quality, 0 approach."""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target): if broken :",
        "language": "python",
        "unique_hints_used": 1
    })
    assert res.status_code == 200
    data = res.json()
    bd = data["score_data"]["breakdown"]
    assert bd["correctness"]["points_earned"] == 0.0
    assert bd["complexity"]["is_available"] is False
    assert bd["complexity"]["status"] == "N/A"
    assert bd["quality"]["points_earned"] == 0.0
    assert bd["approach"]["points_earned"] == 0.0

    # Total score equals sum of breakdown
    total_breakdown = round(sum(dim["points_earned"] for dim in bd.values()), 1)
    assert total_breakdown == data["overall_score"]

def test_valid_code_with_failed_tests():
    """Requirement 2, 3: Valid code that fails all test cases receives 0 correctness and N/A complexity."""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "def two_sum(nums, target):\n    return [-1, -1]\n",
        "language": "python",
        "unique_hints_used": 0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["passed_count"] == 0
    bd = data["score_data"]["breakdown"]
    assert bd["correctness"]["points_earned"] == 0.0
    assert bd["complexity"]["is_available"] is False
    assert bd["complexity"]["status"] == "N/A"
    assert bd["approach"]["points_earned"] == 0.0

    # Quality evaluates submitted code structure
    assert bd["quality"]["points_earned"] > 0.0

    # Total score equals sum of breakdown
    total_breakdown = round(sum(dim["points_earned"] for dim in bd.values()), 1)
    assert total_breakdown == data["overall_score"]

def test_valid_code_with_passed_tests():
    """Requirement 2, 3, 4, 5, 6: Working code passing all tests receives verified score."""
    code = """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    res = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 0
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["passed_count"] == data["total_count"]
    assert data["overall_score"] >= 95.0

    score_data = data["score_data"]
    assert score_data["scoring_status"] == "evaluated"
    assert score_data["is_provisional"] is False

    bd = score_data["breakdown"]
    assert bd["correctness"]["points_earned"] == 40.0
    assert bd["complexity"]["points_earned"] == 20.0
    assert bd["quality"]["points_earned"] >= 12.0
    assert bd["approach"]["points_earned"] >= 12.0
    assert bd["independent"]["points_earned"] == 10.0

    total_breakdown = round(sum(dim["points_earned"] for dim in bd.values()), 1)
    assert total_breakdown == data["overall_score"]

def test_score_breakdown_sum_invariant_across_varied_hints():
    """Requirement 9: Score breakdown always strictly adds up to overall_score."""
    code = """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    for hints in [0, 1, 2, 3, 4]:
        res = client.post("/api/execute", json={
            "problem_id": "two-sum",
            "code": code,
            "language": "python",
            "unique_hints_used": hints
        })
        assert res.status_code == 200
        data = res.json()
        bd = data["score_data"]["breakdown"]
        expected_indep = float(calculate_independent_score(hints))
        assert bd["independent"]["points_earned"] == expected_indep

        total_pts = round(sum(dim["points_earned"] for dim in bd.values()), 1)
        assert total_pts == data["overall_score"], f"Sum {total_pts} != overall {data['overall_score']} for hints={hints}"

def test_renormalization_of_unavailable_dimensions():
    """Requirement 3 & 9: Test that when complexity is N/A, weights renormalize proportionally to 100."""
    engine = CodingScoringEngine()
    # Dimension setup where complexity is marked unavailable
    dims = {
        "correctness": {"ratio": 1.0, "is_available": True, "status": "evaluated"},
        "complexity": {"ratio": 0.0, "is_available": False, "status": "N/A"},
        "quality": {"ratio": 1.0, "is_available": True, "status": "evaluated"},
        "approach": {"ratio": 1.0, "is_available": True, "status": "evaluated"},
        "independent": {"ratio": 1.0, "is_available": True, "status": "evaluated"}
    }
    breakdown, final_score, is_renorm = engine._renormalize_and_score(
        dimensions=dims,
        base_weights={"correctness": 40.0, "complexity": 20.0, "quality": 15.0, "approach": 15.0, "independent": 10.0}
    )
    assert is_renorm is True
    assert breakdown["complexity"]["is_available"] is False
    assert breakdown["complexity"]["points_earned"] == 0.0

    # Total available weight was 80. Correctness: (40/80)*100 = 50. Quality: (15/80)*100 = 18.75. Approach: 18.75. Indep: 12.5.
    total_points = round(sum(d["points_earned"] for d in breakdown.values()), 1)
    assert total_points == 100.0
    assert final_score == 100.0

def test_fresh_attempt_after_previously_scored_attempt():
    """Requirement 8: Ensure a subsequent empty attempt does not reuse or inherit previous attempt scores."""
    # Step 1: Successful attempt with code
    code = "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen: return [seen[target-n], i]\n        seen[n] = i\n    return []"
    res1 = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": code,
        "language": "python",
        "unique_hints_used": 0
    })
    assert res1.status_code == 200
    assert res1.json()["overall_score"] >= 90.0

    # Step 2: Fresh attempt with completely empty code
    res2 = client.post("/api/execute", json={
        "problem_id": "two-sum",
        "code": "",
        "language": "python",
        "unique_hints_used": 0
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["overall_score"] == 0.0
    assert data2["score_data"]["is_empty_submission"] is True
    assert data2["score_data"]["scoring_status"] == "not_evaluated"
    assert data2["score_data"]["breakdown"]["correctness"]["points_earned"] == 0.0
    assert data2["score_data"]["breakdown"]["complexity"]["points_earned"] == 0.0
    assert data2["score_data"]["breakdown"]["quality"]["points_earned"] == 0.0

def test_all_languages_empty_code_rejection():
    """Requirement 1: Verify empty submissions across Python, C, C++, and Java all receive 0 score."""
    for lang in ["python", "c", "cpp", "java"]:
        res = client.post("/api/execute", json={
            "problem_id": "two-sum",
            "code": "   ",
            "language": lang,
            "unique_hints_used": 0
        })
        assert res.status_code == 200
        data = res.json()
        assert data["overall_score"] == 0.0
        assert data["score_data"]["is_empty_submission"] is True
        assert data["score_data"]["scoring_status"] == "not_evaluated"
