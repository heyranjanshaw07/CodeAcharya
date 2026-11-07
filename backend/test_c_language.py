import pytest
from fastapi.testclient import TestClient
from main import app
from problems import PROBLEMS
from executor import run_c_code, run_python_code, run_cpp_code, run_java_code

client = TestClient(app)

def test_language_endpoint_allows_c():
    """Verify that /api/problems/generate allows 'c' and rejects 'javascript'."""
    # Test valid language 'c'
    res = client.post("/api/problems/generate", json={
        "topic": "Recursion & Backtracking",
        "difficulty": "Easy",
        "language": "c"
    })
    assert res.status_code == 200
    data = res.json()
    assert "c" in data["starter_code"]
    assert "python" in data["starter_code"]
    assert "cpp" in data["starter_code"]
    assert "java" in data["starter_code"]
    assert "javascript" not in data["starter_code"]

def test_language_endpoint_rejects_javascript():
    """Verify that requesting 'javascript' is rejected as unsupported."""
    res = client.post("/api/problems/generate", json={
        "topic": "Recursion & Backtracking",
        "difficulty": "Easy",
        "language": "javascript"
    })
    assert res.status_code == 400
    assert "Unsupported language" in res.json()["detail"]

def test_all_problems_have_c_starter_code():
    """Verify that all curated problems have C starter code and no javascript."""
    for pid, problem in PROBLEMS.items():
        assert "c" in problem.starter_code, f"Problem {pid} missing C starter code"
        assert "python" in problem.starter_code, f"Problem {pid} missing Python starter code"
        assert "cpp" in problem.starter_code, f"Problem {pid} missing C++ starter code"
        assert "java" in problem.starter_code, f"Problem {pid} missing Java starter code"
        assert "javascript" not in problem.starter_code, f"Problem {pid} still contains javascript"

def test_c_code_execution_with_main_gcc():
    """Verify compiling and running a valid C program with main() via GCC."""
    code = """#include <stdio.h>

int main(void) {
    long long n;
    if (scanf("%lld", &n) == 1) {
        long long res = 1;
        for (long long i = 2; i <= n; i++) {
            res *= i;
        }
        printf("%lld", res);
    }
    return 0;
}
"""
    problem = PROBLEMS["factorial-recursion"]
    res = run_c_code(code, "factorial-recursion", problem.test_cases)
    assert res.status == "success"
    assert res.passed_count == res.total_count
    assert len(res.results) == len(problem.test_cases)
    assert res.runtime_ms >= 0

def test_c_code_compilation_error_gcc():
    """Verify that invalid C syntax captures compilation errors from GCC."""
    code = """#include <stdio.h>

int main(void) {
    // Missing semicolon and undeclared identifier
    undeclared_variable = 42
    return 0;
}
"""
    problem = PROBLEMS["factorial-recursion"]
    res = run_c_code(code, "factorial-recursion", problem.test_cases)
    assert res.status == "error"
    assert res.error_type == "CompilationError"
    assert "undeclared" in res.stderr.lower() or "error" in res.stderr.lower()

def test_c_code_unmatched_braces():
    """Verify syntax validation catches unmatched curly braces."""
    code = """#include <stdio.h>

int main(void) {
    return 0;
"""
    problem = PROBLEMS["factorial-recursion"]
    res = run_c_code(code, "factorial-recursion", problem.test_cases)
    assert res.status == "error"
    assert res.error_type == "CompilationError"
    assert "curly braces" in res.stderr.lower()

def test_c_code_execution_function_based():
    """Verify that a C function submission passes test verification."""
    code = """#include <stdio.h>

long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""
    problem = PROBLEMS["factorial-recursion"]
    res = run_c_code(code, "factorial-recursion", problem.test_cases)
    assert res.status == "success"
    assert res.passed_count == res.total_count

def test_c_code_execution_base_case_error():
    """Verify that a C function returning 0 in factorial base case is flagged."""
    code = """#include <stdio.h>

long long factorial(int n) {
    if (n <= 1) return 0; // BUG!
    return n * factorial(n - 1);
}
"""
    problem = PROBLEMS["factorial-recursion"]
    res = run_c_code(code, "factorial-recursion", problem.test_cases)
    assert res.status == "failed"
    assert res.passed_count == 0
    assert any("Base Case Error" in (r.error or "") for r in res.results)

def test_api_execute_c_code():
    """Verify POST /api/execute runs C code properly."""
    code = """#include <stdio.h>

long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""
    res = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": code,
        "language": "c"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["passed_count"] == data["total_count"]

def test_debug_guide_and_explain_c():
    """Verify Debug Guide and Explain Code work seamlessly with C."""
    # Debug guide for C code with base case bug
    debug_res = client.post("/api/debug", json={
        "problem_id": "factorial-recursion",
        "code": "long long factorial(int n) { if (n <= 1) return 0; return n * factorial(n - 1); }",
        "language": "c"
    })
    assert debug_res.status_code == 200
    debug_data = debug_res.json()
    assert "bug_summary" in debug_data or "primary_symptom" in debug_data

    # Explain code for C code
    explain_res = client.post("/api/explain", json={
        "problem_id": "factorial-recursion",
        "code": "long long factorial(int n) { if (n <= 1) return 1; return n * factorial(n - 1); }",
        "language": "c"
    })
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert "summary" in explain_data

def test_python_cpp_java_still_work():
    """Ensure existing Python, C++, and Java executions remain fully functional."""
    problem = PROBLEMS["factorial-recursion"]
    
    # Python
    py_code = problem.expected_solution["python"]
    py_res = run_python_code(py_code, "factorial-recursion", problem.test_cases)
    assert py_res.status == "success"
    
    # C++
    cpp_code = problem.expected_solution["cpp"]
    cpp_res = run_cpp_code(cpp_code, "factorial-recursion", problem.test_cases)
    assert cpp_res.status == "success"
    
    # Java
    java_code = problem.expected_solution["java"]
    java_res = run_java_code(java_code, "factorial-recursion", problem.test_cases)
    assert java_res.status == "success"
