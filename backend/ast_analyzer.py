import ast
from typing import Dict, Any, List, Optional

class ASTAnalysisResult:
    def __init__(self):
        self.is_valid: bool = True
        self.syntax_error: Optional[str] = None
        self.has_recursion: bool = False
        self.recursive_functions: List[str] = []
        self.has_base_case: bool = False
        self.base_case_notes: List[str] = []
        self.suspected_bugs: List[str] = []
        self.loop_depth: int = 0
        self.estimated_complexity: str = "O(1)"
        self.code_smells: List[str] = []
        self.is_safe_to_execute: bool = True
        self.safety_violations: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "syntax_error": self.syntax_error,
            "has_recursion": self.has_recursion,
            "recursive_functions": self.recursive_functions,
            "has_base_case": self.has_base_case,
            "base_case_notes": self.base_case_notes,
            "suspected_bugs": self.suspected_bugs,
            "loop_depth": self.loop_depth,
            "estimated_complexity": self.estimated_complexity,
            "code_smells": self.code_smells,
            "is_safe_to_execute": self.is_safe_to_execute,
            "safety_violations": self.safety_violations
        }

class CodeInspector(ast.NodeVisitor):
    def __init__(self, problem_id: str = ""):
        self.problem_id = problem_id
        self.res = ASTAnalysisResult()
        self.current_function: Optional[str] = None
        self.function_calls: Dict[str, List[str]] = {}
        self.function_has_if: Dict[str, bool] = {}
        self.function_returns: Dict[str, List[Any]] = {}
        self.loop_depth = 0
        self.max_loop_depth = 0

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in ["os", "subprocess", "sys", "shutil", "socket", "http"]:
                self.res.is_safe_to_execute = False
                self.res.safety_violations.append(f"Importing restricted module: '{alias.name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in ["os", "subprocess", "sys", "shutil", "socket", "http"]:
            self.res.is_safe_to_execute = False
            self.res.safety_violations.append(f"Importing from restricted module: '{node.module}'")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        prev_fn = self.current_function
        self.current_function = node.name
        self.function_calls[node.name] = []
        self.function_has_if[node.name] = False
        self.function_returns[node.name] = []
        
        self.generic_visit(node)

        # Check for recursion
        if node.name in self.function_calls.get(node.name, []):
            self.res.has_recursion = True
            self.res.recursive_functions.append(node.name)
            
            # Check base case existence
            if self.function_has_if.get(node.name, False):
                self.res.has_base_case = True
            else:
                self.res.has_base_case = False
                self.res.suspected_bugs.append(
                    f"Recursive function '{node.name}' has no conditional base case (if statement). This will cause infinite recursion and stack overflow."
                )

            # Specific check for factorial zero-bug mentioned in PDF
            if "factorial" in self.problem_id.lower() or "factorial" in node.name.lower():
                returns = self.function_returns.get(node.name, [])
                for r in returns:
                    if isinstance(r, ast.Constant) and r.value == 0:
                        self.res.suspected_bugs.append(
                            "Base case returns 0! Multiplying by 0 will cause the entire factorial to collapse to 0. Recall that 0! = 1."
                        )

            # Check overlapping recursive subproblems (e.g. fib(n-1) + fib(n-2))
            calls_to_self = self.function_calls.get(node.name, []).count(node.name)
            if calls_to_self >= 2:
                self.res.code_smells.append(
                    f"Function '{node.name}' branches into {calls_to_self} recursive calls without memoization (O(2^N) exponential time)."
                )

        self.current_function = prev_fn

    def visit_If(self, node):
        if self.current_function:
            self.function_has_if[self.current_function] = True
        self.generic_visit(node)

    def visit_Return(self, node):
        if self.current_function and node.value:
            self.function_returns[self.current_function].append(node.value)
        self.generic_visit(node)

    def visit_Call(self, node):
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and self.current_function:
            self.function_calls[self.current_function].append(func_name)

        if func_name in ["exec", "eval", "compile", "__import__"]:
            self.res.is_safe_to_execute = False
            self.res.safety_violations.append(f"Dangerous built-in function '{func_name}' is not permitted.")

        self.generic_visit(node)

    def visit_For(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        
        # Check while True without break
        if isinstance(node.test, ast.Constant) and bool(node.test.value) is True:
            has_break_or_return = False
            for child in ast.walk(node):
                if isinstance(child, (ast.Break, ast.Return)):
                    has_break_or_return = True
                    break
            if not has_break_or_return:
                self.res.suspected_bugs.append("Detected an unconditional 'while True' loop with no 'break' or 'return'. This will run infinitely.")

        self.generic_visit(node)
        self.loop_depth -= 1


def analyze_python_code(code: str, problem_id: str = "") -> ASTAnalysisResult:
    result = ASTAnalysisResult()
    if not code or not code.strip():
        result.is_valid = False
        result.syntax_error = "Empty code submission"
        result.estimated_complexity = "N/A"
        return result

    try:
        tree = ast.parse(code)
    except SyntaxError as se:
        result.is_valid = False
        result.syntax_error = f"Line {se.lineno}, Col {se.offset}: {se.msg}"
        result.suspected_bugs.append(f"Syntax Error on line {se.lineno}: {se.msg}")
        return result
    except Exception as e:
        result.is_valid = False
        result.syntax_error = str(e)
        return result

    if len(tree.body) == 0:
        result.is_valid = False
        result.syntax_error = "No executable statements found"
        result.estimated_complexity = "N/A"
        return result

    inspector = CodeInspector(problem_id=problem_id)
    inspector.visit(tree)
    inspector.res.loop_depth = inspector.max_loop_depth

    # Complexity estimation
    if inspector.res.has_recursion:
        calls = sum(inspector.function_calls.get(f, []).count(f) for f in inspector.res.recursive_functions)
        if calls > 1:
            inspector.res.estimated_complexity = "O(2^N) [Branching Recursion]"
        else:
            inspector.res.estimated_complexity = "O(N) [Linear Recursion]"
    elif inspector.max_loop_depth == 0:
        inspector.res.estimated_complexity = "O(1) [Constant Time]"
    elif inspector.max_loop_depth == 1:
        inspector.res.estimated_complexity = "O(N) [Single Loop]"
    elif inspector.max_loop_depth == 2:
        inspector.res.estimated_complexity = "O(N^2) [Nested Loops]"
    else:
        inspector.res.estimated_complexity = f"O(N^{inspector.max_loop_depth}) [Deeply Nested Loops]"

    return inspector.res
