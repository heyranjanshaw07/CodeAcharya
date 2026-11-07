"""
Comprehensive Test Suite for CodeAcharya BharatCode Provider-Neutral LLM Integration

Covers all 14 specification cases:
1. Successful BharatCode API response produces a valid coding question.
2. Missing API key activates blueprint fallback.
3. API timeout activates fallback.
4. HTTP 401 authentication error activates fallback.
5. HTTP 429 rate limit activates fallback.
6. Server-side API error activates fallback.
7. Empty API response activates fallback.
8. Invalid JSON activates fallback.
9. Invalid question schema activates fallback.
10. Duplicate question triggers retry.
11. Sandbox verification failure triggers retry/fallback.
12. Batch generation still works.
13. Multiple generated questions remain deduplicated.
14. Existing blueprint generation works without any API credentials.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
import requests

from llm_client import call_llm, extract_text_from_response, get_llm_config
from question_generator import (
    generate_coding_problem_service,
    generate_coding_problems_batch,
    generate_blueprint_fallback
)
from mentor_ai import MentorAI


SAMPLE_VALID_AI_PROBLEM = {
    "id": "valid-bracket-sequence",
    "title": "Valid Bracket Sequence",
    "topic": "Stack & Queue",
    "subtopic": "Parentheses Matching",
    "difficulty": "Easy",
    "language": "python",
    "description": "Given a string `s` containing just characters '(', ')', determine if the input string is valid.",
    "inputFormat": "A string `s` containing parentheses.",
    "outputFormat": "A boolean indicating whether string is valid.",
    "constraints": ["1 <= len(s) <= 10^4"],
    "examples": [
        {"input": "s = '()'", "output": "True", "explanation": "Matching pair"}
    ],
    "hint": "Use a stack or count balance.",
    "progressive_hints": [
        {"level": 1, "title": "Conceptual", "content": "Track opening vs closing.", "thought_questions": ["What is balanced?"]},
        {"level": 2, "title": "Direction", "content": "Counter approach.", "thought_questions": ["Can balance be negative?"]},
        {"level": 3, "title": "Invariant", "content": "Balance never below 0.", "thought_questions": ["Final balance?"]},
        {"level": 4, "title": "Step-by-Step", "content": "Iterate chars.", "thought_questions": ["Return balance == 0"]}
    ],
    "starter_code": {
        "python": "def is_valid_brackets(s: str) -> bool:\n    pass\n",
        "c": "#include <stdbool.h>\nbool is_valid_brackets(const char* s) { return false; }\n",
        "cpp": "#include <string>\nbool is_valid_brackets(std::string s) { return false; }\n",
        "java": "public class Solution { public static boolean is_valid_brackets(String s) { return false; } }\n"
    },
    "expected_solution": {
        "python": "def is_valid_brackets(s: str) -> bool:\n    b = 0\n    for c in s:\n        if c == '(':\n            b += 1\n        elif c == ')':\n            b -= 1\n        if b < 0:\n            return False\n    return b == 0\n"
    },
    "test_cases": [
        {"id": 1, "input": "()", "expected_output": True, "is_hidden": False},
        {"id": 2, "input": ")(", "expected_output": False, "is_hidden": False},
        {"id": 3, "input": "(())", "expected_output": True, "is_hidden": True}
    ],
    "explanation": "Greedy balance counter.",
    "time_complexity": "O(N)",
    "space_complexity": "O(1)",
    "relevant_concepts": ["Stack & Queue"]
}


# =============================================================================
# CASE 1: Successful BharatCode API response produces a valid coding question
# =============================================================================
def test_case_1_successful_bharatcode_response():
    """Verify that a successful BharatCode API response produces an AI Generated question."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps(SAMPLE_VALID_AI_PROBLEM)
                }
            }
        ]
    }

    with patch("requests.post", return_value=mock_response):
        raw_text = call_llm(
            system_instruction="System prompt",
            prompt="Generate problem",
            api_key="bc_live_mock_key_12345",
            base_url="https://bharatcode.ai/api/model/v1",
            model="qwen-3.8-27b"
        )
        assert raw_text is not None
        assert "valid-bracket-sequence" in raw_text

        # Test generation service
        problem = generate_coding_problem_service(
            api_key="bc_live_mock_key_12345",
            call_llm_fn=lambda s, p: raw_text,
            topic="Stack & Queue",
            difficulty="Easy",
            language="python"
        )
        assert problem is not None
        assert problem["id"] == "valid-bracket-sequence"
        assert problem["source"] == "ai_generated"
        assert problem["badge"] == "AI Generated"
        assert problem["is_generated"] is True


# =============================================================================
# CASE 2: Missing API key activates blueprint fallback
# =============================================================================
def test_case_2_missing_api_key_activates_fallback():
    """Verify missing API key safely triggers blueprint fallback."""
    with patch.dict(os.environ, {}, clear=True):
        problem = generate_coding_problem_service(
            api_key=None,
            call_llm_fn=None,
            topic="Recursion & Backtracking",
            difficulty="Easy",
            language="python"
        )
        assert problem is not None
        assert problem["source"] == "blueprint_fallback"
        assert problem["badge"] == "Predefined Blueprint"
        assert problem["is_generated"] is True


# =============================================================================
# CASE 3: API timeout activates fallback
# =============================================================================
def test_case_3_api_timeout_activates_fallback():
    """Verify API request timeout triggers blueprint fallback."""
    with patch("requests.post", side_effect=requests.exceptions.Timeout("Request timed out")):
        res = call_llm("sys", "prompt", api_key="bc_test_key")
        assert res is None

        problem = generate_coding_problem_service(
            api_key="bc_test_key",
            call_llm_fn=lambda s, p: call_llm(s, p, api_key="bc_test_key"),
            topic="Dynamic Programming",
            difficulty="Medium",
            language="python"
        )
        assert problem["source"] == "blueprint_fallback"


# =============================================================================
# CASE 4: HTTP 401 authentication error activates fallback
# =============================================================================
def test_case_4_http_401_auth_error_activates_fallback():
    """Verify HTTP 401 Invalid Key safely logs and activates blueprint fallback."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized: Invalid API key"

    with patch("requests.post", return_value=mock_resp):
        res = call_llm("sys", "prompt", api_key="invalid_key")
        assert res is None

        problem = generate_coding_problem_service(
            api_key="invalid_key",
            call_llm_fn=lambda s, p: call_llm(s, p, api_key="invalid_key"),
            topic="Arrays & Hashing",
            difficulty="Easy",
            language="python"
        )
        assert problem["source"] == "blueprint_fallback"


# =============================================================================
# CASE 5: HTTP 429 rate limit activates fallback
# =============================================================================
def test_case_5_http_429_rate_limit_activates_fallback():
    """Verify HTTP 429 Quota/Rate limit activates blueprint fallback."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Rate limit exceeded"

    with patch("requests.post", return_value=mock_resp):
        res = call_llm("sys", "prompt", api_key="bc_key")
        assert res is None

        problem = generate_coding_problem_service(
            api_key="bc_key",
            call_llm_fn=lambda s, p: call_llm(s, p, api_key="bc_key"),
            topic="Trees & Binary Search Trees",
            difficulty="Easy",
            language="python"
        )
        assert problem["source"] == "blueprint_fallback"


# =============================================================================
# CASE 6: Server-side API error activates fallback
# =============================================================================
def test_case_6_server_error_activates_fallback():
    """Verify HTTP 500 / 502 / 503 upstream errors activate blueprint fallback."""
    mock_resp = MagicMock()
    mock_resp.status_code = 502
    mock_resp.text = "Bad Gateway"

    with patch("requests.post", return_value=mock_resp):
        res = call_llm("sys", "prompt", api_key="bc_key")
        assert res is None

        problem = generate_coding_problem_service(
            api_key="bc_key",
            call_llm_fn=lambda s, p: call_llm(s, p, api_key="bc_key"),
            topic="Strings",
            difficulty="Easy",
            language="python"
        )
        assert problem["source"] == "blueprint_fallback"


# =============================================================================
# CASE 7: Empty API response activates fallback
# =============================================================================
def test_case_7_empty_response_activates_fallback():
    """Verify empty string or whitespace response from LLM activates fallback."""
    mock_call_llm = MagicMock(return_value="   ")
    problem = generate_coding_problem_service(
        api_key="bc_key",
        call_llm_fn=mock_call_llm,
        topic="Graphs & Traversal",
        difficulty="Medium",
        language="python"
    )
    assert problem["source"] == "blueprint_fallback"
    assert mock_call_llm.call_count == 2  # Retried twice before fallback


# =============================================================================
# CASE 8: Invalid JSON activates fallback
# =============================================================================
def test_case_8_invalid_json_activates_fallback():
    """Verify malformed JSON from LLM activates fallback."""
    mock_call_llm = MagicMock(return_value="Here is your problem: {broken json ...")
    problem = generate_coding_problem_service(
        api_key="bc_key",
        call_llm_fn=mock_call_llm,
        topic="Recursion & Backtracking",
        difficulty="Easy",
        language="python"
    )
    assert problem["source"] == "blueprint_fallback"
    assert mock_call_llm.call_count == 2


# =============================================================================
# CASE 9: Invalid question schema activates fallback
# =============================================================================
def test_case_9_invalid_schema_activates_fallback():
    """Verify response missing required fields (e.g. constraints, test_cases) fails validation and activates fallback."""
    invalid_schema_obj = {
        "title": "Incomplete Problem",
        "description": "Missing test cases and starter code"
    }
    mock_call_llm = MagicMock(return_value=json.dumps(invalid_schema_obj))
    problem = generate_coding_problem_service(
        api_key="bc_key",
        call_llm_fn=mock_call_llm,
        topic="Arrays & Hashing",
        difficulty="Easy",
        language="python"
    )
    assert problem["source"] == "blueprint_fallback"
    assert mock_call_llm.call_count == 2


# =============================================================================
# CASE 10: Duplicate question triggers retry
# =============================================================================
def test_case_10_duplicate_triggers_retry():
    """Verify that a duplicate problem triggers a second attempt with distinct problem accepted."""
    dup_problem = dict(SAMPLE_VALID_AI_PROBLEM)
    dup_problem["title"] = "Existing Problem"

    fresh_problem = dict(SAMPLE_VALID_AI_PROBLEM)
    fresh_problem["id"] = "fresh-bracket-sequence"
    fresh_problem["title"] = "Brand New Unique Problem"

    # Attempt 1 returns duplicate title, Attempt 2 returns unique title
    mock_call_llm = MagicMock(side_effect=[json.dumps(dup_problem), json.dumps(fresh_problem)])

    problem = generate_coding_problem_service(
        api_key="bc_key",
        call_llm_fn=mock_call_llm,
        topic="Stack & Queue",
        difficulty="Easy",
        language="python",
        previous_titles=["Existing Problem"]
    )
    assert mock_call_llm.call_count == 2
    assert problem["id"] == "fresh-bracket-sequence"
    assert problem["source"] == "ai_generated"


# =============================================================================
# CASE 11: Sandbox verification failure triggers retry/fallback
# =============================================================================
def test_case_11_sandbox_failure_triggers_fallback():
    """Verify that reference solution failing sandboxed execution triggers fallback."""
    broken_solution_problem = dict(SAMPLE_VALID_AI_PROBLEM)
    # Solution produces wrong result (always False when expected is True)
    broken_solution_problem["expected_solution"] = {
        "python": "def is_valid_brackets(s: str) -> bool:\n    return False\n"
    }

    mock_call_llm = MagicMock(return_value=json.dumps(broken_solution_problem))
    problem = generate_coding_problem_service(
        api_key="bc_key",
        call_llm_fn=mock_call_llm,
        topic="Stack & Queue",
        difficulty="Easy",
        language="python"
    )
    assert problem["source"] == "blueprint_fallback"
    assert mock_call_llm.call_count == 2


# =============================================================================
# CASE 12: Batch generation still works
# =============================================================================
def test_case_12_batch_generation():
    """Verify batch generation service generates specified number of problems."""
    batch = generate_coding_problems_batch(
        api_key=None,
        topic="Dynamic Programming",
        difficulty="Easy",
        language="python",
        count=3
    )
    assert len(batch) == 3
    for p in batch:
        assert p["topic"] == "Dynamic Programming"
        assert p["difficulty"] == "Easy"
        assert "starter_code" in p
        assert "progressive_hints" in p


# =============================================================================
# CASE 13: Multiple generated questions remain deduplicated
# =============================================================================
def test_case_13_batch_deduplication():
    """Verify all questions generated in a batch have distinct IDs and titles."""
    batch = generate_coding_problems_batch(
        api_key=None,
        topic="Recursion & Backtracking",
        difficulty="Easy",
        language="python",
        count=4
    )
    assert len(batch) == 4
    ids = [p["id"] for p in batch]
    titles = [p["title"].lower().strip() for p in batch]
    assert len(set(ids)) == 4, f"IDs in batch should be distinct: {ids}"
    assert len(set(titles)) == 4, f"Titles in batch should be distinct: {titles}"


# =============================================================================
# CASE 14: Existing blueprint generation works without any API credentials
# =============================================================================
def test_case_14_blueprint_generation_without_credentials():
    """Verify deterministic blueprint fallback generates complete schema without any API credentials."""
    with patch.dict(os.environ, {}, clear=True):
        problem = generate_blueprint_fallback(
            topic="Algorithms & Two Pointers",
            difficulty="Medium",
            language="cpp"
        )
        assert problem is not None
        assert problem["topic"] == "Algorithms & Two Pointers"
        assert problem["difficulty"] == "Medium"
        assert problem["language"] == "cpp"
        assert problem["source"] == "blueprint_fallback"
        assert "starter_code" in problem
        assert "cpp" in problem["starter_code"]
        assert "python" in problem["starter_code"]
        assert "c" in problem["starter_code"]
        assert "java" in problem["starter_code"]
        assert len(problem["progressive_hints"]) == 4
        assert len(problem["test_cases"]) >= 2
        assert problem["expected_solution"] is not None

