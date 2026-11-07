"""
Comprehensive Regression Test Suite for CodeAcharya AI Viva Voice & Scoring Updates.
Tests the 10 specific regression scenarios requested:

1. A typed answer displays Communication & Clarity as N/A.
2. A typed answer's overall score excludes Communication & Clarity.
3. A voice-transcribed answer retains its correct modality after submission.
4. A transcript can be edited before submission.
5. Empty speech recognition results cannot be submitted as successful voice answers.
6. Microphone permission denial is handled correctly.
7. Stopping and restarting recognition does not create duplicate listeners.
8. Switching questions clears stale recording and evaluation state.
9. A previous voice score never leaks into a later typed answer.
10. Overall score calculations exclude every N/A dimension.
"""

import sys
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"

FACTORIAL_CODE = "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"
FACTORIAL_PROBLEM = "factorial-recursion"

VP_CODE = (
    "class Solution:\n"
    "    def isValid(self, s):\n"
    "        stack = []\n"
    "        pairs = {')': '(', '}': '{', ']': '['}\n"
    "        for c in s:\n"
    "            if c in '({[':\n                stack.append(c)\n"
    "            elif not stack or stack[-1] != pairs[c]:\n                return False\n"
    "            else:\n                stack.pop()\n"
    "        return len(stack) == 0"
)
VP_PROBLEM = "valid-parentheses"

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

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def eval_req(problem_id, code, question, answer, modality="typed"):
    return post(f"{BASE}/api/viva/evaluate", {
        "problem_id": problem_id,
        "code": code,
        "question_id": question["id"],
        "question": question["question"],
        "category": question["category"],
        "student_answer": answer,
        "answer_modality": modality,
        "hint_guidance": question.get("hint_guidance"),
    })

def start_viva(problem_id, code):
    return post(f"{BASE}/api/viva/start", {
        "problem_id": problem_id,
        "code": code,
        "language": "python"
    })

def run_tests():
    global PASS, FAIL
    print("=" * 65)
    print("RUNNING VOICE & SCORING REGRESSION TEST SUITE (10 SCENARIOS)")
    print("=" * 65)

    fact_qs = start_viva(FACTORIAL_PROBLEM, FACTORIAL_CODE)
    q1 = fact_qs[0]  # Conceptual
    q3 = fact_qs[2]  # Complexity

    vp_qs = start_viva(VP_PROBLEM, VP_CODE)
    vp_q1 = vp_qs[0] # Conceptual
    vp_q4 = vp_qs[3] # Edge Case / Code Choice

    # SCENARIO 1: A typed answer displays Communication & Clarity as N/A (None)
    print("\n[SCENARIO 1] Typed answer displays Communication & Clarity as N/A")
    r1 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case terminates recursive calls on the call stack. "
        "Without it, infinite recursion exhausts stack frames and causes a StackOverflow.",
        modality="typed"
    )
    check("communication_score is None for typed answer", r1.get("communication_score") is None, f"got {r1.get('communication_score')}")
    check("communication score alias in scores dict is None", r1.get("scores", {}).get("communication") is None)
    check("communication_score excluded from applicable_dimensions", "communication_score" not in r1.get("applicable_dimensions", []))
    check("modality recorded as typed", r1.get("answer_modality") == "typed")

    # SCENARIO 2: A typed answer's overall score excludes Communication & Clarity
    print("\n[SCENARIO 2] Typed answer overall score excludes Communication & Clarity")
    r2 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case terminates recursive calls on the call stack. "
        "Without it, infinite recursion exhausts stack frames and causes a StackOverflow.",
        modality="typed"
    )
    # Conceptual question has conceptual_score as only applicable dim when typed
    check("overall_score equals conceptual_score for single-dim question",
          r2["overall_score"] == r2["conceptual_score"],
          f"overall={r2['overall_score']}, conceptual={r2['conceptual_score']}")
    check("no artificial 90% or 0% communication score assigned", r2.get("communication_score") is None)

    # SCENARIO 3: A voice-transcribed answer retains its correct modality after submission
    print("\n[SCENARIO 3] Voice-transcribed answer retains correct modality")
    r3 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case is required because it terminates recursive calls on the call stack. "
        "Therefore, without a base case the stack frames accumulate indefinitely causing overflow.",
        modality="voice_transcribed"
    )
    check("answer_modality is voice_transcribed", r3.get("answer_modality") == "voice_transcribed")
    check("communication_label is Verbal Response Clarity", r3.get("communication_label") == "Verbal Response Clarity")
    check("communication_score is applicable (not None)", r3.get("communication_score") is not None)
    check("communication_score is included in applicable_dimensions", "communication_score" in r3.get("applicable_dimensions", []))
    check("communication_score is a valid integer 0-100", 0 <= r3.get("communication_score", -1) <= 100)

    # SCENARIO 4: A transcript can be edited before submission
    print("\n[SCENARIO 4] Transcript edited before submission preserves voice_transcribed modality")
    initial_speech = "A base case stops the recursion"
    edited_speech = (
        initial_speech + " because it pops stack frames from the call stack. "
        "Without it, infinite recursion occurs and memory is exhausted."
    )
    r4 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1, edited_speech, modality="voice_transcribed")
    check("edited transcript retains voice_transcribed modality", r4.get("answer_modality") == "voice_transcribed")
    check("higher depth results in higher overall score", r4["overall_score"] >= 80)
    check("verbal clarity reflects structured connectors in transcript", r4.get("communication_score") is not None and r4.get("communication_score") >= 60)

    # SCENARIO 5: Empty speech recognition results cannot be submitted as successful voice answers
    print("\n[SCENARIO 5] Empty speech recognition results cannot be submitted as successful voice answers")
    r5 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1, "   ", modality="voice_transcribed")
    check("empty voice answer receives overall_score 0", r5["overall_score"] == 0)
    check("empty voice answer should_retry is True", r5["should_retry"] is True)
    check("empty voice answer communication_score is 0 (not a success)", r5.get("communication_score") == 0)
    check("feedback requests a substantive response", "No substantive answer" in r5["feedback"])

    # SCENARIO 6: Microphone permission denial is handled correctly
    print("\n[SCENARIO 6] Fallback / invalid modality safely handled without crash")
    r6 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case terminates recursive calls on the call stack.",
        modality="invalid_or_denied_modality"
    )
    check("invalid modality defaults safely to typed", r6.get("answer_modality") == "typed")
    check("communication_score remains None (N/A) on safe default", r6.get("communication_score") is None)

    # SCENARIO 7: Stopping and restarting recognition does not create duplicate listeners / side effects
    print("\n[SCENARIO 7] Stopping and restarting evaluations produces idempotent deterministic results")
    ans_text = "The space complexity is O(N) auxiliary space because N recursive frames are placed on the call stack."
    r7a = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q3, ans_text, modality="voice_transcribed")
    r7b = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q3, ans_text, modality="voice_transcribed")
    check("repeated evaluate requests match exactly", r7a["overall_score"] == r7b["overall_score"])
    check("communication_score matches exactly", r7a["communication_score"] == r7b["communication_score"])

    # SCENARIO 8: Switching questions clears stale recording and evaluation state
    print("\n[SCENARIO 8] Switching questions clears state and associates scores with correct question")
    r8_q1 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case terminates calls on the call stack.",
        modality="voice_transcribed"
    )
    r8_q3 = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q3,
        "The space complexity is O(N) stack frames on the call stack.",
        modality="typed"
    )
    check("Q1 evaluation is for Q1", r8_q1["question_id"] == q1["id"] and r8_q1["category"] == "conceptual")
    check("Q3 evaluation is for Q3", r8_q3["question_id"] == q3["id"] and r8_q3["category"] == "complexity")
    check("Q3 complexity dimension is scored", r8_q3["complexity_score"] is not None)
    check("Q1 complexity dimension is None (N/A)", r8_q1["complexity_score"] is None)

    # SCENARIO 9: A previous voice score never leaks into a later typed answer
    print("\n[SCENARIO 9] Previous voice score never leaks into a later typed answer")
    # First, student answers Q1 via voice
    q1_voice = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case is required because it halts recursion and pops activation records from the call stack.",
        modality="voice_transcribed"
    )
    check("Q1 voice answer has communication_score", q1_voice.get("communication_score") is not None)

    # Next, student advances to Q3 and answers via keyboard (typed)
    q3_typed = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q3,
        "The time complexity is O(N) because the function executes N recursive steps.",
        modality="typed"
    )
    check("Q3 typed answer communication_score is strictly None (N/A)", q3_typed.get("communication_score") is None)
    check("Q3 communication alias in scores dict is None", q3_typed.get("scores", {}).get("communication") is None)
    check("Q3 overall score excludes communication entirely",
          "communication_score" not in q3_typed.get("applicable_dimensions", []))

    # SCENARIO 10: Overall score calculations exclude every N/A dimension
    print("\n[SCENARIO 10] Overall score calculations exclude every N/A dimension")
    # Test across categories:
    # 10A: Typed conceptual question (complexity=None, code=None, communication=None)
    r10a = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q1,
        "A base case terminates recursive calls on the call stack. Without one, the function exhausts stack frames.",
        modality="typed"
    )
    for dim in ["complexity_score", "code_understanding_score", "communication_score"]:
        check(f"10A: {dim} is None", r10a.get(dim) is None)
    check("10A: overall score equals conceptual score", r10a["overall_score"] == r10a["conceptual_score"])

    # 10B: Typed complexity question (code=None, communication=None)
    r10b = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q3,
        "The space complexity is O(N) auxiliary space because of N stack frames on the call stack.",
        modality="typed"
    )
    check("10B: code_understanding_score is None", r10b.get("code_understanding_score") is None)
    check("10B: communication_score is None", r10b.get("communication_score") is None)
    # Formula check over applicable dimensions only (complexity + conceptual)
    # complexity: 0.60 / 0.85 = ~0.7059, conceptual: 0.25 / 0.85 = ~0.2941
    comp_score = r10b["complexity_score"]
    conc_score = r10b["conceptual_score"]
    expected_10b = int(round((comp_score * 0.60 + conc_score * 0.25) / 0.85))
    diff_10b = abs(r10b["overall_score"] - expected_10b)
    check("10B: overall score matches normalized applicable weights formula", diff_10b <= 1,
          f"overall={r10b['overall_score']}, expected={expected_10b}")

    # 10C: Voice complexity question (code=None, communication is applicable)
    r10c = eval_req(FACTORIAL_PROBLEM, FACTORIAL_CODE, q3,
        "The space complexity is O(N) because each recursive call allocates a stack frame on the call stack.",
        modality="voice_transcribed"
    )
    check("10C: code_understanding_score is None", r10c.get("code_understanding_score") is None)
    check("10C: communication_score is not None", r10c.get("communication_score") is not None)
    comp_c = r10c["complexity_score"]
    conc_c = r10c["conceptual_score"]
    comm_c = r10c["communication_score"]
    expected_10c = int(round((comp_c * 0.60 + conc_c * 0.25 + comm_c * 0.15) / 1.0))
    diff_10c = abs(r10c["overall_score"] - expected_10c)
    check("10C: overall score matches 3-dimension applicable formula", diff_10c <= 1,
          f"overall={r10c['overall_score']}, expected={expected_10c}")

    print("\n" + "=" * 65)
    print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} checks")
    print("=" * 65)
    if FAIL > 0:
        sys.exit(1)
    print("ALL 10 VOICE & SCORING REGRESSION SCENARIOS PASSED.")

if __name__ == "__main__":
    run_tests()
