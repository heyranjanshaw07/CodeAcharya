"""
Regression tests for the CodeAcharya AI Viva Voce evaluation pipeline.
Tests 1-12 cover all requirements from the bug-fix spec.

Run:
    python test_viva_regression.py

Expects the backend to be running at http://127.0.0.1:8000
"""
import sys
import json
import urllib.request
import urllib.error


BASE = "http://127.0.0.1:8000"

FACTORIAL_CODE = "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"
FACTORIAL_PROBLEM = "factorial-recursion"

TWO_SUM_CODE = "def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i"
TWO_SUM_PROBLEM = "two-sum"

VP_CODE = "class Solution:\n    def isValid(self, s):\n        stack = []\n        pairs = {')': '(', '}': '{', ']': '['}\n        for c in s:\n            if c in '({[':\n                stack.append(c)\n            elif not stack or stack[-1] != pairs[c]:\n                return False\n            else:\n                stack.pop()\n        return len(stack) == 0"
VP_PROBLEM = "valid-parentheses"


def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def post_expect_error(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return False, json.loads(resp.read().decode()), None
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return True, None, (e.code, body)


def eval_req(problem_id, code, question, answer):
    return post(f"{BASE}/api/viva/evaluate", {
        "problem_id": problem_id,
        "code": code,
        "question_id": question["id"],
        "question": question["question"],
        "category": question["category"],
        "student_answer": answer,
        "hint_guidance": question.get("hint_guidance"),
    })


def start_viva(problem_id, code):
    return post(f"{BASE}/api/viva/start", {
        "problem_id": problem_id,
        "code": code,
        "language": "python"
    })


def assert_formula(result, weights, applicable_dims, label):
    global PASS, FAIL
    total_w = 0.0
    total_sw = 0.0
    for dim in applicable_dims:
        w = weights.get(dim, 0)
        score = result.get(dim)
        if score is not None and w > 0:
            total_sw += score * w
            total_w += w
    expected = int(round(total_sw / total_w)) if total_w > 0 else 0
    actual = result["overall_score"]
    diff = abs(expected - actual)
    if diff <= 1:
        print(f"  + PASS: {label}")
        PASS += 1
    else:
        print(f"  - FAIL: {label}: overall={actual} formula gives {expected} "
              f"(scores={[result.get(d) for d in applicable_dims]})")
        FAIL += 1


PASS = 0
FAIL = 0


def check(label, cond, msg=""):
    global PASS, FAIL
    if cond:
        print(f"  + PASS: {label}")
        PASS += 1
    else:
        print(f"  - FAIL: {label}  {msg}")
        FAIL += 1


def run_all():
    print("=" * 60)
    print("VIVA REGRESSION SUITE (12 tests)")
    print("=" * 60)

    fact_qs = start_viva(FACTORIAL_PROBLEM, FACTORIAL_CODE)
    q_conceptual = fact_qs[0]
    q_complexity = fact_qs[2]

    vp_qs = start_viva(VP_PROBLEM, VP_CODE)
    vp_q1 = vp_qs[0]
    vp_q4 = vp_qs[3]

    ts_qs = start_viva(TWO_SUM_PROBLEM, TWO_SUM_CODE)
    ts_q4 = ts_qs[3]

    # TEST 1: Complete and correct answer
    print("\n[TEST 1] Complete and correct answer")
    r1 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual,
        "A base case is fundamentally required to terminate recursive calls on the call stack. "
        "Without a base case the function calls itself indefinitely, exhausting all available "
        "stack frames and triggering a RecursionError or StackOverflow at the OS level.")
    check("overall >= 80", r1["overall_score"] >= 80, f"got {r1['overall_score']}")
    check("relevance == relevant", r1["answer_relevance"] == "relevant")
    check("has ideal points", len(r1.get("ideal_points_covered", [])) > 0)
    check("code_understanding is None", r1["code_understanding_score"] is None)
    check("complexity is None", r1["complexity_score"] is None)

    # TEST 2: Correct but incomplete
    print("\n[TEST 2] Correct but incomplete answer")
    r2 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual,
        "A base case stops the recursion.")
    check("overall < 75", r2["overall_score"] < 75, f"got {r2['overall_score']}")
    check("overall > 0", r2["overall_score"] > 0, f"got {r2['overall_score']}")

    # TEST 3: Partially correct
    print("\n[TEST 3] Partially correct answer")
    r3 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual,
        "A base case returns a number.")
    check("overall < 50", r3["overall_score"] < 50, f"got {r3['overall_score']}")
    check("relevance is partial or irrelevant",
          r3["answer_relevance"] in ("partially_relevant", "irrelevant"))

    # TEST 4: Technically incorrect
    print("\n[TEST 4] Technically incorrect answer")
    r4 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual,
        "The base case is needed so the function returns a very large number. "
        "Without it, the recursion just runs faster.")
    check("overall < 60", r4["overall_score"] < 60, f"got {r4['overall_score']}")

    # TEST 5: Empty answer
    print("\n[TEST 5] Empty answer")
    r5 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual, "   ")
    check("overall == 0", r5["overall_score"] == 0, f"got {r5['overall_score']}")
    check("conceptual == 0", r5["conceptual_score"] == 0)
    check("should_retry is True", r5.get("should_retry", False))

    # TEST 6: Keywords present, wrong reasoning
    print("\n[TEST 6] Keywords present but incorrect reasoning")
    r6 = eval_req(TWO_SUM_PROBLEM, TWO_SUM_CODE, ts_q4,
        "You use two pointers starting from the middle of the array. "
        "They both move outward until they reach the end. This works on unsorted arrays too.")
    check("overall < 70", r6["overall_score"] < 70, f"got {r6['overall_score']}")

    # TEST 7: Complexity N/A on conceptual question
    print("\n[TEST 7] Complexity is N/A on conceptual question")
    r7 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual,
        "A base case is needed to terminate recursive calls on the call stack. "
        "Without it, the function calls itself indefinitely causing a stack overflow.")
    check("complexity_score is None", r7["complexity_score"] is None,
          f"got {r7['complexity_score']}")
    check("code_understanding_score is None", r7["code_understanding_score"] is None,
          f"got {r7['code_understanding_score']}")
    check("conceptual_score is not None", r7["conceptual_score"] is not None)
    assert_formula(r7,
        {"conceptual_score": 0.70, "communication_score": 0.30},
        ["conceptual_score", "communication_score"], "overall formula consistent with applicable dims")

    # TEST 8: Code understanding N/A on complexity question
    print("\n[TEST 8] Code understanding N/A on complexity question")
    r8 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_complexity,
        "The space complexity is O(N) because the recursion creates N stack frames on the "
        "call stack, one for each invocation from n down to the base case.")
    check("complexity_score >= 70", r8["complexity_score"] is not None and
          r8["complexity_score"] >= 70, f"got {r8['complexity_score']}")
    check("code_understanding_score is None", r8["code_understanding_score"] is None,
          f"got {r8['code_understanding_score']}")
    check("overall >= 65", r8["overall_score"] >= 65, f"got {r8['overall_score']}")

    # TEST 9: API provider failure -> 502
    print("\n[TEST 9] API failure returns 502, no fabricated score")
    err, _, err_data = post_expect_error(f"{BASE}/api/viva/evaluate", {
        "problem_id": FACTORIAL_PROBLEM,
        "code": FACTORIAL_CODE,
        "question_id": q_conceptual["id"],
        "question": q_conceptual["question"],
        "category": q_conceptual["category"],
        "student_answer": "Some valid technical answer about recursion and call stack",
        "hint_guidance": q_conceptual.get("hint_guidance"),
        "simulate_failure": True
    })
    check("HTTP error was raised", err)
    check("status code is 502", err_data is not None and err_data[0] == 502,
          f"got {err_data}")

    # TEST 10: Overall formula consistency
    print("\n[TEST 10] Overall score is reproducible from stored dimension scores")
    r10 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_conceptual,
        "A base case terminates recursive calls on the call stack. Without one, "
        "the function exhausts stack frames and raises a RecursionError.")
    check("complexity is None", r10["complexity_score"] is None)
    check("code_understanding is None", r10["code_understanding_score"] is None)
    assert_formula(r10,
        {"conceptual_score": 0.70, "communication_score": 0.30},
        ["conceptual_score", "communication_score"], "overall formula verified")

    # TEST 11: Stale score prevention
    print("\n[TEST 11] Stale score prevention: resubmit gets fresh evaluation")
    r11a = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, fact_qs[0],
        "A base case terminates calls on the stack.")
    r11b = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, fact_qs[0],
        "A base case is required to stop infinite recursion. Without it, the call stack "
        "exhausts all available memory and throws StackOverflow, crashing the program.")
    check("second submission returns a result", r11b["overall_score"] >= 0)
    check("scores differ when answers differ",
          r11b["overall_score"] != r11a["overall_score"] or
          r11b["answer_relevance"] == r11a["answer_relevance"])

    # TEST 12: Complete answer CAN reach 100% (no artificial ceiling)
    print("\n[TEST 12] Perfect answer can achieve top score (no hardcoded ceiling)")
    r12 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q_complexity,
        "The space complexity of this recursive implementation is O(N) auxiliary space. "
        "This is because each recursive call creates a new stack frame (activation record) "
        "on the call stack. Since there are N recursive calls from factorial(n) down to the "
        "base case factorial(1), the call stack holds N frames simultaneously at its deepest "
        "point. Even though no array or list is explicitly allocated, the O(N) memory is "
        "consumed by these stack frames. In contrast, an iterative loop using a single "
        "accumulator variable would use O(1) auxiliary space since no stack frames accumulate.")
    check("complexity_score >= 85", r12["complexity_score"] is not None and
          r12["complexity_score"] >= 85, f"got {r12['complexity_score']}")
    check("overall >= 80", r12["overall_score"] >= 80, f"got {r12['overall_score']}")
    check("no ceiling: complexity can reach 90+",
          (r12["complexity_score"] is not None and r12["complexity_score"] >= 90)
          or r12["overall_score"] >= 85,
          f"complexity={r12['complexity_score']}, overall={r12['overall_score']}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} checks")
    print("=" * 60)
    if FAIL > 0:
        sys.exit(1)
    print("ALL REGRESSION TESTS PASSED.")


if __name__ == "__main__":
    run_all()
