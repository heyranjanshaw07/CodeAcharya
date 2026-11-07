import pytest
from fastapi.testclient import TestClient
from main import app
from problems import PROBLEMS
from models import TestCase
from executor import (
    run_python_code,
    run_c_code,
    run_cpp_code,
    run_java_code,
    compare_output,
    format_stdin,
    find_c_compiler,
    find_cpp_compiler,
    find_java_compiler,
    find_java_runtime
)

client = TestClient(app)

# Helper simple test cases for reading two numbers and printing their sum
SUM_TEST_CASES = [
    TestCase(id=1, input={"a": 10, "b": 25}, expected_output=35),
    TestCase(id=2, input={"a": -5, "b": 15}, expected_output=10),
    TestCase(id=3, input={"a": 0, "b": 0}, expected_output=0),
]

# 1. Python valid input/output
def test_1_python_valid_execution():
    code = """def add_numbers(a, b):
    return a + b
"""
    res = run_python_code(code, "two-sum", SUM_TEST_CASES)
    assert res.status == "success"
    assert res.passed_count == 3
    assert len(res.results) == 3
    assert res.results[0].passed is True

# 2. C compilation and execution
def test_2_c_compilation_and_execution():
    code = """#include <stdio.h>
int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) {
        printf("%d\\n", a + b);
    }
    return 0;
}
"""
    res = run_c_code(code, "sum-test", SUM_TEST_CASES)
    assert res.status == "success"
    assert res.passed_count == 3
    assert res.results[0].actual == "35"
    assert res.results[1].actual == "10"

# 3. C compilation errors
def test_3_c_compilation_error():
    code = """#include <stdio.h>
int main(void) {
    this_is_an_invalid_c_statement;
    return 0;
}
"""
    res = run_c_code(code, "sum-test", SUM_TEST_CASES)
    assert res.status == "error"
    assert res.error_type == "CompilationError"
    assert "error" in res.stderr.lower() or "undeclared" in res.stderr.lower()

# 4. C++ compilation and execution
def test_4_cpp_compilation_and_execution():
    code = """#include <iostream>
using namespace std;
int main() {
    int a, b;
    if (cin >> a >> b) {
        cout << (a + b) << endl;
    }
    return 0;
}
"""
    res = run_cpp_code(code, "sum-test", SUM_TEST_CASES)
    assert res.status == "success"
    assert res.passed_count == 3
    assert res.results[0].passed is True
    assert res.results[0].actual == "35"

# 5. C++ compilation errors
def test_5_cpp_compilation_error():
    code = """#include <iostream>
int main() {
    std::cout << undeclared_identifier << std::endl
    return 0;
}
"""
    res = run_cpp_code(code, "sum-test", SUM_TEST_CASES)
    assert res.status == "error"
    assert res.error_type == "CompilationError"
    assert "undeclared" in res.stderr.lower() or "error" in res.stderr.lower()

# 6. Java compilation and execution
def test_6_java_compilation_and_execution():
    code = """import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        if (sc.hasNextInt()) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            System.out.println(a + b);
        }
    }
}
"""
    res = run_java_code(code, "sum-test", SUM_TEST_CASES)
    assert res.status == "success"
    assert res.passed_count == 3
    assert res.results[0].passed is True
    assert res.results[0].actual == "35"

# 7. Java compilation errors
def test_7_java_compilation_error():
    code = """public class Main {
    public static void main(String[] args) {
        int x = "incompatible types";
    }
}
"""
    res = run_java_code(code, "sum-test", SUM_TEST_CASES)
    assert res.status == "error"
    assert res.error_type == "CompilationError"
    assert "incompatible types" in res.stderr.lower() or "error" in res.stderr.lower()

# 8. Standard input handling in all four languages
def test_8_stdin_handling_all_four_languages():
    # Python
    py_code = """import sys
nums = [int(x) for x in sys.stdin.read().split()]
print(nums[0] + nums[1])
"""
    # C
    c_code = """#include <stdio.h>
int main(void) {
    int a, b;
    if (scanf("%d %d", &a, &b) == 2) {
        printf("%d\\n", a + b);
    }
    return 0;
}
"""
    # C++
    cpp_code = """#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""
    # Java
    java_code = """import java.util.Scanner;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}
"""
    test_cases = [TestCase(id=1, input="15 30", expected_output=45)]
    
    # Python via subprocess
    import subprocess, sys
    p_py = subprocess.run([sys.executable, "-c", py_code], input="15 30\n", text=True, capture_output=True)
    assert p_py.stdout.strip() == "45"

    # C
    res_c = run_c_code(c_code, "test", test_cases)
    assert res_c.status == "success"
    assert res_c.results[0].actual == "45"

    # C++
    res_cpp = run_cpp_code(cpp_code, "test", test_cases)
    assert res_cpp.status == "success"
    assert res_cpp.results[0].actual == "45"

    # Java
    res_java = run_java_code(java_code, "test", test_cases)
    assert res_java.status == "success"
    assert res_java.results[0].actual == "45"

# 9. Wrong answers and edge cases
def test_9_wrong_answers_and_edge_cases():
    wrong_c = """#include <stdio.h>
int main(void) {
    printf("99999\\n");
    return 0;
}
"""
    res = run_c_code(wrong_c, "sum-test", SUM_TEST_CASES)
    assert res.status == "failed"
    assert res.passed_count == 0
    assert res.results[0].passed is False
    assert res.results[0].actual == "99999"

    # Base case factorial error in C
    buggy_factorial = """#include <stdio.h>
long long factorial(int n) {
    if (n <= 1) return 0;
    return n * factorial(n - 1);
}
"""
    problem = PROBLEMS["factorial-recursion"]
    res_fact = run_c_code(buggy_factorial, "factorial-recursion", problem.test_cases)
    assert res_fact.status == "failed"
    assert res_fact.passed_count == 0
    assert any("Base Case Error" in (r.error or "") for r in res_fact.results)

# 10. Runtime errors and timeouts
def test_10_runtime_errors_and_timeouts():
    # Runtime error in C (non-zero exit)
    c_runtime_err = """#include <stdlib.h>
int main(void) {
    exit(42);
}
"""
    res_err = run_c_code(c_runtime_err, "sum-test", SUM_TEST_CASES)
    assert res_err.status == "failed"
    assert "exit code 42" in res_err.results[0].actual

    # Timeout in C (infinite loop)
    c_timeout = """#include <stdio.h>
int main(void) {
    while(1) {}
    return 0;
}
"""
    # Test single test case with short timeout logic
    res_to = run_c_code(c_timeout, "sum-test", [TestCase(id=1, input="1 1", expected_output=2)])
    assert res_to.status == "failed"
    assert res_to.results[0].actual == "Time Limit Exceeded"

# 11. Output normalization
def test_11_output_normalization():
    # Direct match
    assert compare_output("120\n", 120) is True
    assert compare_output("  120  \r\n", "120") is True
    # Floats and ints
    assert compare_output("120.0", 120) is True
    assert compare_output("3.1415", 3.1415) is True
    # Booleans
    assert compare_output("true\n", True) is True
    assert compare_output("1\n", True) is True
    assert compare_output("false\n", False) is True
    assert compare_output("0\n", False) is True
    # Lists
    assert compare_output("[0, 1]\n", [0, 1]) is True
    assert compare_output("0 1\n", [0, 1]) is True

# 12. Multiple test cases
def test_12_multiple_test_cases():
    problem = PROBLEMS["factorial-recursion"]
    solution_c = problem.expected_solution["c"]
    res = run_c_code(solution_c, "factorial-recursion", problem.test_cases)
    assert res.status == "success"
    assert res.passed_count == len(problem.test_cases)
    assert len(res.results) == len(problem.test_cases)

# 13. Missing compiler or runtime handling
def test_13_missing_compiler_handling(monkeypatch):
    import executor
    # Simulate missing compiler
    monkeypatch.setattr(executor, "find_c_compiler", lambda: None)
    res = executor.run_c_code("int main() { return 0; }", "test", [TestCase(id=1, input="1", expected_output=1)])
    assert res.status == "error"
    assert res.error_type == "CompilerNotFound"
    assert "not installed" in res.stderr

# 14. Correct frontend-to-backend language mapping via /api/execute
def test_14_api_execute_language_routing():
    problem = PROBLEMS["factorial-recursion"]
    
    # Python
    res_py = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": problem.expected_solution["python"],
        "language": "python"
    })
    assert res_py.status_code == 200
    assert res_py.json()["status"] == "success"

    # C
    res_c = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": problem.expected_solution["c"],
        "language": "c"
    })
    assert res_c.status_code == 200
    assert res_c.json()["status"] == "success"

    # C++
    res_cpp = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": problem.expected_solution["cpp"],
        "language": "cpp"
    })
    assert res_cpp.status_code == 200
    assert res_cpp.json()["status"] == "success"

    # Java
    res_java = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": problem.expected_solution["java"],
        "language": "java"
    })
    assert res_java.status_code == 200
    assert res_java.json()["status"] == "success"

    # Rejected language
    res_js = client.post("/api/execute", json={
        "problem_id": "factorial-recursion",
        "code": "console.log('hi')",
        "language": "javascript"
    })
    assert res_js.status_code == 400
    assert "not currently supported" in res_js.json()["detail"]

# 15. Python regression baseline continues to pass
def test_15_python_regression_baseline():
    problem = PROBLEMS["factorial-recursion"]
    res = run_python_code(problem.expected_solution["python"], "factorial-recursion", problem.test_cases)
    assert res.status == "success"
    assert res.passed_count == len(problem.test_cases)

    # Security AST check regression test
    malicious = "import os\nos.system('echo hacked')"
    sec_res = run_python_code(malicious, "factorial-recursion", problem.test_cases)
    assert sec_res.status == "error"
    assert sec_res.error_type == "SecurityError"
