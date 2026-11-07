import urllib.request
import json

def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def main():
    # 1. Start Viva Session
    start_res = post_json('http://127.0.0.1:8000/api/viva/start', {
        'problem_id': 'valid-parentheses',
        'code': 'class Solution:\n    def isValid(self, s):\n        stack = []\n        return len(stack) == 0',
        'language': 'python'
    })

    print(f'Started Viva: Received {len(start_res)} questions.')
    for q in start_res:
        print(f'  Q{q["id"]} [{q["category"]}]: {q["question"][:70]}...')

    # 2. Evaluate Question 1 (Conceptual) with Gibberish
    q1 = start_res[0]
    res_q1_gibberish = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'valid-parentheses',
        'code': 'code',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': 'kldfsdkjhfaskjf',
        'hint_guidance': q1.get('hint_guidance')
    })
    print('\n[Evaluation Q1 - Gibberish]:')
    print('  Overall Score:', res_q1_gibberish['overall_score'])
    print('  Conceptual Score:', res_q1_gibberish['conceptual_score'])
    print('  Complexity Score (N/A):', res_q1_gibberish['complexity_score'])
    print('  Relevance:', res_q1_gibberish['answer_relevance'])
    print('  Retry:', res_q1_gibberish['should_retry'])
    print('  Feedback:', res_q1_gibberish['feedback'])

    # 3. Evaluate Question 1 (Conceptual) with Solid Technical Answer
    res_q1_valid = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'valid-parentheses',
        'code': 'code',
        'question_id': q1['id'],
        'question': q1['question'],
        'category': q1['category'],
        'student_answer': 'A Stack is suitable because bracket matching adheres to Last-In First-Out (LIFO) order. The most recently opened bracket must be the first one closed. Simple counters cannot ensure relative order like ([)].',
        'hint_guidance': q1.get('hint_guidance')
    })
    print('\n[Evaluation Q1 - Solid Answer]:')
    print('  Overall Score:', res_q1_valid['overall_score'])
    print('  Conceptual Score:', res_q1_valid['conceptual_score'])
    print('  Communication Score:', res_q1_valid['communication_score'])
    print('  Points Recognized:', res_q1_valid['ideal_points_covered'])

    # 4. Evaluate Question 3 (Complexity) with Complexity Answer
    q3 = start_res[2]
    res_q3 = post_json('http://127.0.0.1:8000/api/viva/evaluate', {
        'problem_id': 'valid-parentheses',
        'code': 'code',
        'question_id': q3['id'],
        'question': q3['question'],
        'category': q3['category'],
        'student_answer': 'Time complexity is O(N) because we iterate through the N characters once. Space complexity is O(N) auxiliary space in the worst case when all brackets are opening brackets stored on the stack.',
        'hint_guidance': q3.get('hint_guidance')
    })
    print(f'\n[Evaluation Q3 ({q3["category"]})]:')
    print('  Overall Score:', res_q3['overall_score'])
    print('  Complexity Score:', res_q3['complexity_score'])
    print('  Code Understanding (N/A):', res_q3['code_understanding_score'])
    print('  Points Recognized:', res_q3['ideal_points_covered'])

if __name__ == '__main__':
    main()
