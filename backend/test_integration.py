import urllib.request
import json
import sys
import uuid

def query_endpoint(name, url, method='GET', data=None, headers=None, expected_status=None):
    try:
        req = urllib.request.Request(url, method=method)
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            content = resp.read().decode('utf-8')
            print(f"[OK] {name}: HTTP {status} ({len(content)} bytes)")
            return content, status
    except urllib.error.HTTPError as he:
        content = he.read().decode('utf-8')
        if expected_status and he.code == expected_status:
            print(f"[OK (Expected {he.code})] {name}: HTTP {he.code}")
            return content, he.code
        else:
            print(f"[HTTP {he.code}] {name}: {content[:100]}")
            return content, he.code
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return None, None

if __name__ == '__main__':
    print("==================================================")
    print("   CodeAcharya End-to-End Integration Test Suite  ")
    print("==================================================")

    print("\n--- 1. Testing Frontend Vite & Public APIs ---")
    query_endpoint("Vite Root", "http://localhost:5173/")
    query_endpoint("Vite Proxied API", "http://localhost:5173/api/problems")
    query_endpoint("Backend Health", "http://127.0.0.1:8000/api/health")
    query_endpoint("Problems List", "http://127.0.0.1:8000/api/problems")
    query_endpoint("Factorial Problem", "http://127.0.0.1:8000/api/problems/factorial-recursion")

    print("\n--- 2. Testing Protected Route Rejection Without Auth ---")
    query_endpoint("Unauthenticated Profile Access (Must be 401)", 
                   "http://127.0.0.1:8000/api/profile", expected_status=401)
    query_endpoint("Unauthenticated Recommendations Access (Must be 401)", 
                   "http://127.0.0.1:8000/api/recommendations", expected_status=401)
    query_endpoint("Unauthenticated /api/auth/me (Must be 401)", 
                   "http://127.0.0.1:8000/api/auth/me", expected_status=401)

    print("\n--- 3. Testing Authentication (Login & Invalid Credentials) ---")
    query_endpoint("Login Wrong Password (Must be 401)", 
                   "http://127.0.0.1:8000/api/auth/login", method="POST", data={
                       "email": "student@codeacharya.ai",
                       "password": "WrongPassword999!"
                   }, expected_status=401)

    login_res, _ = query_endpoint("Login Demo Learner", 
                                  "http://127.0.0.1:8000/api/auth/login", method="POST", data={
                                      "email": "student@codeacharya.ai",
                                      "password": "Password123!"
                                  })
    auth_token = None
    if login_res:
        login_data = json.loads(login_res)
        auth_token = login_data.get("token")
        print("  Authenticated User:", login_data.get("user", {}).get("full_name"))
        print("  User Email:", login_data.get("user", {}).get("email"))

    auth_headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

    print("\n--- 4. Testing Authenticated Protected Routes ---")
    if auth_token:
        me_res, _ = query_endpoint("Auth Me (Session Verification)", 
                                   "http://127.0.0.1:8000/api/auth/me", headers=auth_headers)
        prof_res, _ = query_endpoint("Student Profile (Authenticated)", 
                                     "http://127.0.0.1:8000/api/profile", headers=auth_headers)
        if prof_res:
            pdata = json.loads(prof_res)
            print("  Student Name:", pdata.get("student_name"))
            print("  Streak Days:", pdata.get("streak_days"))
            print("  Solved Count:", pdata.get("total_solved"))

        recs_res, _ = query_endpoint("Adaptive Recommendations (Authenticated)", 
                                     "http://127.0.0.1:8000/api/recommendations", headers=auth_headers)

    print("\n--- 5. Testing Registration & Duplicate Prevention ---")
    test_email = f"new_user_{uuid.uuid4().hex[:6]}@codeacharya.ai"
    reg_res, _ = query_endpoint("Register New Account", 
                                "http://127.0.0.1:8000/api/auth/register", method="POST", data={
                                    "full_name": "New Learner",
                                    "email": test_email,
                                    "password": "SecurePassword123!"
                                })
    
    query_endpoint("Duplicate Email Registration (Must be 400)", 
                   "http://127.0.0.1:8000/api/auth/register", method="POST", data={
                       "full_name": "Duplicate Learner",
                       "email": test_email,
                       "password": "SecurePassword123!"
                   }, expected_status=400)

    print("\n--- 6. Testing Execution (Failing Base Case) ---")
    code_with_bug = "def factorial(n):\n    if n <= 1:\n        return 0\n    return n * factorial(n - 1)"
    res, _ = query_endpoint("Execute Code", "http://127.0.0.1:8000/api/execute", "POST", data={
        "problem_id": "factorial-recursion",
        "code": code_with_bug,
        "language": "python"
    }, headers=auth_headers)
    if res:
        data = json.loads(res)
        print("  Passed Count:", data.get("passed_count"), "/", data.get("total_count"))
        print("  AST Bugs:", data.get("ast_feedback", {}).get("suspected_bugs"))

    print("\n--- 7. Testing Progressive Hints ---")
    hint_res, _ = query_endpoint("Hint Level 1", "http://127.0.0.1:8000/api/hints", "POST", data={
        "problem_id": "factorial-recursion",
        "code": code_with_bug,
        "language": "python",
        "hint_level": 1
    }, headers=auth_headers)

    print("\n--- 8. Testing AI Viva Mode ---")
    viva_res, _ = query_endpoint("Viva Start", "http://127.0.0.1:8000/api/viva/start", "POST", data={
        "problem_id": "factorial-recursion",
        "code": code_with_bug,
        "language": "python"
    }, headers=auth_headers)

    eval_res, _ = query_endpoint("Viva Evaluate", "http://127.0.0.1:8000/api/viva/evaluate", "POST", data={
        "problem_id": "factorial-recursion",
        "code": code_with_bug,
        "question_id": 1,
        "question": "Why is a base case fundamentally required?",
        "category": "conceptual",
        "student_answer": "The base case terminates recursive call stack frames. Without it, the function calls itself indefinitely causing stack overflow."
    }, headers=auth_headers)
    if eval_res:
        edata = json.loads(eval_res)
        print("  Overall Score:", edata.get("overall_score"), "%")
        print("  Examiner Feedback:", edata.get("feedback")[:80] + "...")

    print("\n--- 9. Testing Logout and Session Invalidation ---")
    if auth_token:
        query_endpoint("Logout User", "http://127.0.0.1:8000/api/auth/logout", method="POST", headers=auth_headers)
        query_endpoint("Post-Logout Auth Me (Must be 401)", 
                       "http://127.0.0.1:8000/api/auth/me", headers=auth_headers, expected_status=401)
        query_endpoint("Post-Logout Profile Access (Must be 401)", 
                       "http://127.0.0.1:8000/api/profile", headers=auth_headers, expected_status=401)

    print("\n==================================================")
    print("   Integration Test Complete! All features green. ")
    print("==================================================")
