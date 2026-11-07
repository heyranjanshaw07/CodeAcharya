import urllib.request
import urllib.error
import json

def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def post_json_expect_error(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return False, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return True, (e.code, body)


def run_tests():
    print("==================================================")
    print("RUNNING VIVA SUITE: TESTS A THROUGH G")
    print("==================================================")

    # 1. Start session for factorial-recursion
    start_res = post_json('http://127.0.0.1:8000/api/viva/start', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)',
        'language': 'python'
    })
    print(f"Viva Started: {len(start_res)} questions returned.")
    q1 = start_res[0]
    q3 = start_res[2]

    # TEST A — Correct answer
    ans_a = "A base case is fundamentally required to terminate recursive calls on the call stack. Without a base case, the function calls itself indefinitely, exhausting stack frames and triggering a stack overflow error."
    res_a = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_a,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST A - Correct Answer]:")
    print("  Overall Score:", res_a['overall_score'])
    print("  Conceptual:", res_a['conceptual_score'])
    print("  Relevance:", res_a['answer_relevance'])
    print("  Feedback:", res_a['feedback'])
    assert res_a['overall_score'] >= 80, f"Expected >= 80, got {res_a['overall_score']}"
    assert res_a['answer_relevance'] == 'relevant'

    # TEST B — Partially correct answer (only mentions base case returns number)
    ans_b = "A base case returns a number."
    res_b = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_b,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST B - Partially Correct]:")
    print("  Overall Score:", res_b['overall_score'])
    print("  Conceptual:", res_b['conceptual_score'])
    print("  Relevance:", res_b['answer_relevance'])
    print("  Missing:", res_b['missing_concepts'])
    assert res_b['overall_score'] < 50, f"Expected < 50, got {res_b['overall_score']}"
    assert res_b['answer_relevance'] in ['partially_relevant', 'irrelevant']

    # TEST C — Random text / Gibberish (e.g. kldfsdkjhfaskjf)
    ans_c = "kldfsdkjhfaskjf"
    res_c = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_c,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST C - Random Text / Gibberish]:")
    print("  Overall Score:", res_c['overall_score'])
    print("  Conceptual:", res_c['conceptual_score'])
    print("  Relevance:", res_c['answer_relevance'])
    print("  Feedback:", res_c['feedback'])
    assert res_c['overall_score'] == 0, f"Expected 0, got {res_c['overall_score']}"
    assert res_c['answer_relevance'] == 'irrelevant'
    assert "Good effort" not in res_c['feedback']

    # TEST D — Empty answer
    ans_d = "   "
    res_d = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_d,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST D - Empty Answer]:")
    print("  Overall Score:", res_d['overall_score'])
    print("  Feedback:", res_d['feedback'])
    assert res_d['overall_score'] == 0, f"Expected 0, got {res_d['overall_score']}"

    # TEST E — Explicit uncertainty ("I don't know.")
    ans_e = "I don't know."
    res_e = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_e,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST E - Explicit Uncertainty]:")
    print("  Overall Score:", res_e['overall_score'])
    print("  Conceptual:", res_e['conceptual_score'])
    print("  Relevance:", res_e['answer_relevance'])
    print("  Feedback:", res_e['feedback'])
    assert res_e['overall_score'] == 0, f"Expected 0, got {res_e['overall_score']}"
    assert res_e['answer_relevance'] == 'uncertain'

    # TEST F — Different questions (Conceptual Q1 vs Complexity Q3)
    ans_f_comp = "The space complexity is O(N) auxiliary memory because recursion creates N call stack frames on the call stack."
    res_f_comp = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q3['id'],
        'question': q3['question'],
        'category': q3['category'],
        'student_answer': ans_f_comp,
        'hint_guidance': q3.get('hint_guidance')
    })
    print("\n[TEST F - Complexity Question]:")
    print("  Overall Score:", res_f_comp['overall_score'])
    print("  Complexity Score:", res_f_comp['complexity_score'])
    print("  Code Understanding (N/A):", res_f_comp['code_understanding_score'])
    assert res_f_comp['complexity_score'] >= 80, f"Expected >= 80, got {res_f_comp['complexity_score']}"
    assert res_f_comp['code_understanding_score'] is None, "Expected code understanding to be None"

    # TEST G — AI Provider failure (simulated 502)
    err_occurred, err_data = post_json_expect_error('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': 'valid answer',
        'hint_guidance': q1.get('hint_guidance'),
        'simulate_failure': True
    })
    print("\n[TEST G - Provider Failure Simulation]:")
    print("  Error Raised:", err_occurred)
    print("  Status Code & Response:", err_data)
    assert err_occurred is True
    assert err_data[0] == 502

    # TEST H — Random English Text (e.g. "The weather is nice today and I love eating pizza")
    ans_h = "The weather is nice today and I love eating pizza"
    res_h = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_h,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST H - Random English Text]:")
    print("  Overall Score:", res_h['overall_score'])
    print("  Relevance:", res_h['answer_relevance'])
    print("  Feedback:", res_h['feedback'])
    assert res_h['overall_score'] == 0, f"Expected 0, got {res_h['overall_score']}"
    assert res_h['answer_relevance'] == 'irrelevant'
    assert res_h['conceptual_score'] == 0

    # TEST I — Off-topic programming text for factorial
    ans_i = "I like printing hello world and creating integer variables in python."
    res_i = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'factorial-recursion',
        'code': 'def factorial(n): ...',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': ans_i,
        'hint_guidance': q1.get('hint_guidance')
    })
    print("\n[TEST I - Off-Topic Programming Text]:")
    print("  Overall Score:", res_i['overall_score'])
    print("  Relevance:", res_i['answer_relevance'])
    assert res_i['overall_score'] == 0
    assert res_i['answer_relevance'] == 'irrelevant'

    # TEST J — Valid Parentheses Q1 (Conceptual) & Q4 (Edge Case)
    vp_start = post_json('http://127.0.0.1:8000/api/viva/start', {
        'problem_id': 'valid-parentheses',
        'code': 'class Solution:\n    def isValid(self, s):\n        stack = []\n        return len(stack) == 0',
        'language': 'python'
    })
    vp_q1 = vp_start[0]
    vp_q4 = vp_start[3]

    ans_j1 = "A Stack is suitable because bracket matching adheres to Last-In First-Out (LIFO) order. The most recently opened bracket must be the first one closed. Simple counters cannot ensure relative order like ([)]."
    res_j1 = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'valid-parentheses',
        'code': 'code',
        'question_id': vp_q1['id'],
        'question': vp_q1['question'],
        'category': vp_q1['category'],
        'student_answer': ans_j1,
        'hint_guidance': vp_q1.get('hint_guidance')
    })
    print("\n[TEST J1 - Valid Parentheses Conceptual]:")
    print("  Overall Score:", res_j1['overall_score'])
    print("  Conceptual:", res_j1['conceptual_score'])
    assert res_j1['overall_score'] >= 80

    ans_j4 = "If the input is ((((, the stack retains unclosed open brackets. At the end, len(stack) == 0 evaluates to False, detecting the unclosed brackets."
    res_j4 = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'valid-parentheses',
        'code': 'code',
        'question_id': vp_q4['id'],
        'question': vp_q4['question'],
        'category': vp_q4['category'],
        'student_answer': ans_j4,
        'hint_guidance': vp_q4.get('hint_guidance')
    })
    print("\n[TEST J4 - Valid Parentheses Edge Case]:")
    print("  Overall Score:", res_j4['overall_score'])
    print("  Code Understanding:", res_j4['code_understanding_score'])
    assert res_j4['overall_score'] >= 80
    assert res_j4['code_understanding_score'] >= 80

    # TEST K — Two Sum Q1
    ts_start = post_json('http://127.0.0.1:8000/api/viva/start', {
        'problem_id': 'two-sum',
        'code': 'def twoSum(nums, target): ...',
        'language': 'python'
    })
    ts_q1 = ts_start[0]
    ans_k = "A Hash Map reduces time complexity to O(N) by storing previously seen elements for O(1) average lookup time. The trade-off is O(N) auxiliary space."
    res_k = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'two-sum',
        'code': 'code',
        'question_id': ts_q1['id'],
        'question': ts_q1['question'],
        'category': ts_q1['category'],
        'student_answer': ans_k,
        'hint_guidance': ts_q1.get('hint_guidance')
    })
    print("\n[TEST K - Two Sum Q1]:")
    print("  Overall Score:", res_k['overall_score'])
    print("  Conceptual:", res_k['conceptual_score'])
    assert res_k['overall_score'] >= 80

    print("\n>>> ALL TESTS A THROUGH K PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_tests()
