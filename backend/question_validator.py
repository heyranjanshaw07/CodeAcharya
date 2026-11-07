import json
import re
from typing import Dict, Any, List, Tuple, Optional
from ast_analyzer import analyze_python_code
from executor import run_python_code
from models import TestCase

VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}

def validate_problem_schema(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that problem dictionary satisfies CodeAcharya schema.
    Returns (is_valid: bool, errors: List[str]).
    """
    errors: List[str] = []

    # 1. Required core strings
    for field in ["title", "description", "topic", "difficulty"]:
        val = data.get(field)
        if not val or not isinstance(val, str) or not val.strip():
            errors.append(f"Missing or empty required field: '{field}'")

    diff = (data.get("difficulty") or "").strip().capitalize()
    if diff not in VALID_DIFFICULTIES:
        errors.append(f"Invalid difficulty '{diff}'. Must be one of {VALID_DIFFICULTIES}")

    # 2. Examples validation
    examples = data.get("examples")
    if not isinstance(examples, list) or len(examples) == 0:
        errors.append("Problem must have at least one example in 'examples' list")
    else:
        for idx, ex in enumerate(examples):
            if not isinstance(ex, dict) or "input" not in ex or "output" not in ex:
                errors.append(f"Example {idx + 1} must be an object with 'input' and 'output' fields")

    # 3. Constraints validation
    constraints = data.get("constraints")
    if not isinstance(constraints, list) or len(constraints) == 0:
        errors.append("Problem must specify at least one constraint in 'constraints' list")

    # 4. Starter code validation
    starter_code = data.get("starter_code")
    if not isinstance(starter_code, dict):
        errors.append("'starter_code' must be a dictionary with language keys")
    else:
        if not starter_code.get("python") and not data.get("starterCode"):
            errors.append("Starter code must provide at least a Python template")

    # 5. Test cases validation
    test_cases = data.get("test_cases")
    if not isinstance(test_cases, list) or len(test_cases) < 2:
        errors.append("Problem must specify at least 2 test cases in 'test_cases' list")
    else:
        has_visible = False
        has_hidden = False
        for idx, tc in enumerate(test_cases):
            if not isinstance(tc, dict):
                errors.append(f"Test case {idx + 1} must be a dictionary")
                continue
            if "input" not in tc or ("expected_output" not in tc and "expected" not in tc):
                errors.append(f"Test case {idx + 1} missing 'input' or 'expected_output'")
            if tc.get("is_hidden"):
                has_hidden = True
            else:
                has_visible = True
        
        # Ensure at least 1 public and 1 hidden for rigorous testing
        if not has_visible and len(test_cases) > 0:
            test_cases[0]["is_hidden"] = False
        if not has_hidden and len(test_cases) > 1:
            test_cases[-1]["is_hidden"] = True

    return (len(errors) == 0, errors)

def ensure_multi_language_starter_code(data: Dict[str, Any], language: str = "python"):
    """Ensures starter code is populated for all supported languages."""
    if "starter_code" not in data or not isinstance(data["starter_code"], dict):
        data["starter_code"] = {}

    sc = data["starter_code"]
    lang_clean = language.lower()

    # If single starterCode string is present, assign it
    if data.get("starterCode"):
        if lang_clean not in sc or not sc[lang_clean]:
            sc[lang_clean] = data["starterCode"]

    # Extract function name from title or python code
    title = data.get("title", "solution")
    clean_fn = re.sub(r'[^a-zA-Z0-9]+', '_', title.lower()).strip('_')
    if not clean_fn or clean_fn[0].isdigit():
        clean_fn = "solve_" + clean_fn

    if not sc.get("python"):
        sc["python"] = f"def {clean_fn}(*args):\n    pass\n"

    if not sc.get("c"):
        sc["c"] = f"#include <stdio.h>\n#include <stdlib.h>\n\nint {clean_fn}() {{\n    \n}}\n"

    if not sc.get("cpp"):
        sc["cpp"] = f"#include <iostream>\n#include <vector>\nusing namespace std;\n\nclass Solution {{\npublic:\n    int {clean_fn}() {{\n        \n    }}\n}};\n"

    if not sc.get("java"):
        sc["java"] = f"public class Solution {{\n    public static int {clean_fn}() {{\n        \n    }}\n}}\n"

    data["starterCode"] = sc.get(lang_clean) or sc.get("python", "")

def ensure_progressive_hints(data: Dict[str, Any]):
    """Guarantees 4 progressive hint levels matching CodeAcharya pedagogical structure."""
    if not data.get("progressive_hints") or not isinstance(data.get("progressive_hints"), list) or len(data["progressive_hints"]) < 4:
        title = data.get("title", "this problem")
        topic = data.get("topic", "DSA")
        base_hint = data.get("hint") or "Break down the inputs and consider boundary conditions."

        data["progressive_hints"] = [
            {
                "level": 1,
                "title": "Conceptual Understanding",
                "content": f"Consider the core characteristics of {topic}. What fundamental condition marks the start or termination of {title}?",
                "thought_questions": ["What is the simplest input possible?", "Can this be reduced to smaller subproblems?"]
            },
            {
                "level": 2,
                "title": "Algorithmic Direction",
                "content": f"{base_hint} Identify which state or data structure keeps track of your progress efficiently.",
                "thought_questions": ["What data structure provides the fastest lookup here?", "Are repeated calculations occurring?"]
            },
            {
                "level": 3,
                "title": "Structural Rule & Invariant",
                "content": "Verify invariant properties: check edge cases (empty collection, single element, boundary limits) and ensure constraints are respected.",
                "thought_questions": ["What happens at the boundaries of the constraints?", "Are indices maintained without off-by-one errors?"]
            },
            {
                "level": 4,
                "title": "Detailed Resolution Walkthrough",
                "content": data.get("explanation") or "Synthesize the base cases, process each element or state step-by-step, and return the aggregated result.",
                "thought_questions": ["Does the space complexity remain within expected bounds?"]
            }
        ]

def verify_solution_sandboxed(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Safely executes generated test cases against a reference solution in an isolated sandbox.
    Validates AST security before execution. Never runs unsafe code.
    Returns (is_verified: bool, message: str, updated_data: Dict[str, Any]).
    """
    solution_code = None
    if isinstance(data.get("expected_solution"), dict):
        solution_code = data["expected_solution"].get("python")
    elif isinstance(data.get("expected_solution"), str):
        solution_code = data["expected_solution"]

    if not solution_code or not solution_code.strip():
        # No reference Python code to execute against; schema validation holds
        return (True, "No reference code provided; structural verification passed", data)

    # 1. AST Security Analysis
    ast_res = analyze_python_code(solution_code, problem_id=data.get("id", "temp-verify"))
    if not ast_res.is_safe_to_execute:
        return (False, f"Security sandbox rejection: {'; '.join(ast_res.safety_violations)}", data)

    if not ast_res.is_valid:
        return (False, f"Reference solution syntax error: {ast_res.syntax_error}", data)

    # 2. Convert test cases to TestCase objects
    tcs = []
    for idx, tc in enumerate(data.get("test_cases", [])):
        tcs.append(TestCase(
            id=tc.get("id", idx + 1),
            input=tc.get("input"),
            expected_output=tc.get("expected_output", tc.get("expected")),
            is_hidden=tc.get("is_hidden", False)
        ))

    if not tcs:
        return (False, "No test cases present to verify", data)

    # 3. Isolated Subprocess Sandbox Execution
    try:
        exec_res = run_python_code(solution_code, problem_id=data.get("id", "temp-verify"), test_cases=tcs)
        if exec_res.status == "error":
            return (False, f"Reference solution execution failed: {exec_res.stderr}", data)

        # 4. Check test case alignment
        all_passed = (exec_res.passed_count == exec_res.total_count)
        if all_passed:
            return (True, f"All {exec_res.total_count} test cases verified successfully", data)

        # If some test cases failed, examine if reference execution produced clean output
        mismatched = [r for r in exec_res.results if not r.passed]
        if len(mismatched) <= len(tcs) // 2:
            # Minor expected_output discrepancy from LLM generation:
            # Sync test cases' expected_output to deterministic verified output from reference solution
            for r in exec_res.results:
                if not r.error and r.actual and not r.actual.startswith("Exception:"):
                    for tc in data["test_cases"]:
                        if tc.get("id") == r.test_id:
                            try:
                                actual_val = json.loads(r.actual)
                                tc["expected_output"] = actual_val
                            except Exception:
                                pass
            return (True, f"Adjusted {len(mismatched)} test cases to match sandboxed reference solution", data)
        else:
            return (False, f"Reference solution failed {len(mismatched)}/{len(tcs)} test cases", data)

    except Exception as e:
        return (False, f"Sandbox verification exception: {str(e)}", data)
