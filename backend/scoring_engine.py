import ast
import re
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from models import Problem, TestResult

DEFAULT_SCORING_WEIGHTS = {
    "correctness": 40.0,
    "complexity": 20.0,
    "quality": 15.0,
    "approach": 15.0,
    "independent": 10.0
}

def calculate_independent_score(unique_hints_used: int) -> int:
    """
    Exact independent problem-solving score formula based on unique hints revealed:
    0 hints -> 10/10
    1 hint  -> 9/10
    2 hints -> 7/10
    3 hints -> 4/10
    4+ hints -> 1/10
    """
    if unique_hints_used <= 0:
        return 10
    elif unique_hints_used == 1:
        return 9
    elif unique_hints_used == 2:
        return 7
    elif unique_hints_used == 3:
        return 4
    else:
        return 1

class CodingScoringEngine:
    """
    Production-grade coding score and performance analytics engine.
    Computes transparent scores out of 100 with configurable weights:
    - Correctness (40 pts base): (Passed / Total) * 40
    - Time and Space Complexity (20 pts base): Static AST / heuristic inspection
    - Code Quality (15 pts base): Readability, structure, error handling, naming
    - Problem-Solving Approach (15 pts base): Alignment with problem requirements (e.g. Backtracking, DP)
    - Independent Problem-Solving (10 pts base): Exact hint penalty curve (10, 9, 7, 4, 1)
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights.copy() if weights else DEFAULT_SCORING_WEIGHTS.copy()
        # Ensure total weights sum to 100 initially
        total = sum(self.weights.values())
        if total > 0 and abs(total - 100.0) > 0.01:
            self.weights = {k: (v / total) * 100.0 for k, v in self.weights.items()}

    @staticmethod
    def validate_submission(code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validates whether code is a legitimate submission:
        - Detects empty, whitespace-only, missing, or comment-only submissions.
        - Ensures code-dependent points cannot be awarded for unsubmitted or non-executable code.
        """
        if not code or not code.strip():
            return {
                "is_valid_submission": False,
                "reason": "empty",
                "message": "Submission is empty or contains only whitespace."
            }
        
        stripped = code.strip()
        lines = [l.strip() for l in stripped.splitlines() if l.strip()]
        lang = (language or "python").lower()
        
        code_lines = []
        for l in lines:
            if lang == "python":
                if not l.startswith("#"):
                    code_lines.append(l)
            elif lang in ["c", "cpp", "c++", "java"]:
                if not l.startswith("//") and not l.startswith("/*") and not l.startswith("*") and not l.endswith("*/"):
                    code_lines.append(l)
            else:
                code_lines.append(l)
        
        if not code_lines:
            return {
                "is_valid_submission": False,
                "reason": "comments_only",
                "message": "Submission contains only comments without executable code."
            }
        
        return {
            "is_valid_submission": True,
            "reason": "valid",
            "message": "Valid code submitted."
        }

    @staticmethod
    def generate_idempotency_key(user_id: str, question_id: str, code: str) -> str:
        code_hash = hashlib.sha256(code.strip().encode("utf-8")).hexdigest()[:16]
        return f"idem_{user_id}_{question_id}_{code_hash}"

    def evaluate(
        self,
        problem: Problem,
        code: str,
        language: str,
        execution_status: str,
        passed_count: int,
        total_count: int,
        test_results: List[TestResult],
        runtime_ms: float,
        coding_time_seconds: int,
        time_spent_away_seconds: int = 0,
        tab_switch_count: int = 0,
        unique_hints_used: int = 0,
        ast_feedback: Optional[Dict[str, Any]] = None,
        ai_evaluator_data: Optional[Dict[str, Any]] = None,
        custom_weights: Optional[Dict[str, float]] = None,
        memory_usage_mb: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates a transparent, grounded score breakdown out of 100 across 5 dimensions.
        """
        weights = custom_weights.copy() if custom_weights else self.weights.copy()
        clean_code = code or ""
        lang = (language or "python").lower()

        sub_validation = self.validate_submission(clean_code, lang)
        is_empty_submission = not sub_validation["is_valid_submission"]

        if is_empty_submission:
            raw_hint_score = calculate_independent_score(unique_hints_used)
            breakdown = {
                "correctness": {
                    "points_earned": 0.0,
                    "max_points": 40.0,
                    "base_weight": 40.0,
                    "effective_weight": 40.0,
                    "ratio": 0.0,
                    "is_available": True,
                    "status": "not_evaluated",
                    "notes": "No submitted code to execute or evaluate test cases."
                },
                "complexity": {
                    "points_earned": 0.0,
                    "max_points": 0.0,
                    "base_weight": 20.0,
                    "effective_weight": 0.0,
                    "ratio": 0.0,
                    "is_available": False,
                    "status": "N/A",
                    "notes": "Complexity analysis unavailable for empty submission."
                },
                "quality": {
                    "points_earned": 0.0,
                    "max_points": 15.0,
                    "base_weight": 15.0,
                    "effective_weight": 15.0,
                    "ratio": 0.0,
                    "is_available": True,
                    "status": "not_evaluated",
                    "notes": "No submitted code to evaluate code quality or style."
                },
                "approach": {
                    "points_earned": 0.0,
                    "max_points": 15.0,
                    "base_weight": 15.0,
                    "effective_weight": 15.0,
                    "ratio": 0.0,
                    "is_available": True,
                    "status": "not_evaluated",
                    "notes": "No submitted code to evaluate problem-solving approach."
                },
                "independent": {
                    "points_earned": 0.0,
                    "max_points": 10.0,
                    "base_weight": 10.0,
                    "effective_weight": 10.0,
                    "ratio": 0.0,
                    "is_available": True,
                    "status": "pending",
                    "raw_score": raw_hint_score,
                    "unique_hints_used": max(0, unique_hints_used),
                    "notes": f"Independent problem-solving tracked ({unique_hints_used} hints used; potential {raw_hint_score}/10 pts), but hint points require a valid code submission."
                }
            }
            evaluator_meta = self._determine_evaluator_metadata(has_ai=False, language=lang)
            return {
                "overall_score": 0.0,
                "scoring_status": "not_evaluated",
                "is_empty_submission": True,
                "is_provisional": True,
                "breakdown": breakdown,
                "is_renormalized": False,
                "passed_count": 0,
                "total_count": total_count,
                "unique_hints_used": unique_hints_used,
                "independent_score": raw_hint_score,
                "test_summary": {
                    "passed": 0,
                    "total": total_count,
                    "status": "empty_submission",
                    "has_hidden_tests": False
                },
                "performance": {
                    "coding_time_seconds": coding_time_seconds,
                    "coding_time_formatted": self._format_duration(coding_time_seconds),
                    "execution_time_ms": 0.0,
                    "memory_usage_mb": None,
                    "time_spent_away_seconds": time_spent_away_seconds,
                    "tab_switch_count": tab_switch_count,
                    "runtime_context": "No execution occurred."
                },
                "complexity_analysis": {
                    "estimated_time_complexity": "N/A",
                    "estimated_space_complexity": "N/A",
                    "expected_time_complexity": getattr(problem, "time_complexity", None) or "O(N)",
                    "expected_space_complexity": getattr(problem, "space_complexity", None) or "O(1)",
                    "complexity_status": "N/A"
                },
                "feedback": {
                    "strengths": [],
                    "improvement_suggestions": ["Write a solution in the editor and click 'Run & Test' to evaluate your code."],
                    "summary": "Submission is empty. Please write code to evaluate correctness, complexity, and quality."
                },
                "evaluator": evaluator_meta
            }

        # 1. EVALUATE CORRECTNESS (40 points base)
        correctness_eval = self._evaluate_correctness(
            execution_status=execution_status,
            passed_count=passed_count,
            total_count=total_count,
            test_results=test_results
        )

        # 2. EVALUATE TIME AND SPACE COMPLEXITY (20 points base)
        complexity_eval = self._evaluate_complexity(
            code=clean_code,
            language=lang,
            problem=problem,
            execution_status=execution_status,
            passed_count=passed_count,
            total_count=total_count,
            ast_feedback=ast_feedback,
            ai_data=ai_evaluator_data
        )

        # 3. EVALUATE CODE QUALITY (15 points base)
        quality_eval = self._evaluate_code_quality(
            code=clean_code,
            language=lang,
            execution_status=execution_status,
            ast_feedback=ast_feedback,
            ai_data=ai_evaluator_data
        )

        # 4. EVALUATE PROBLEM-SOLVING APPROACH (15 points base)
        approach_eval = self._evaluate_approach(
            code=clean_code,
            language=lang,
            problem=problem,
            correctness_eval=correctness_eval,
            ast_feedback=ast_feedback,
            ai_data=ai_evaluator_data
        )

        # 5. EVALUATE INDEPENDENT PROBLEM-SOLVING (10 points base)
        independent_eval = self._evaluate_independent_problem_solving(
            unique_hints_used=unique_hints_used,
            is_code_submitted=True
        )

        # 6. RENORMALIZE WEIGHTS FOR AVAILABLE DIMENSIONS
        dimensions = {
            "correctness": correctness_eval,
            "complexity": complexity_eval,
            "quality": quality_eval,
            "approach": approach_eval,
            "independent": independent_eval
        }

        breakdown, overall_score, is_renormalized = self._renormalize_and_score(
            dimensions=dimensions,
            base_weights=weights
        )

        scoring_status = "evaluated" if (passed_count == total_count and total_count > 0 and execution_status == "success") else "provisional"
        is_provisional = (scoring_status == "provisional")

        # 7. EVALUATOR METADATA & GROUNDED FEEDBACK
        evaluator_meta = self._determine_evaluator_metadata(
            has_ai=bool(ai_evaluator_data and ai_evaluator_data.get("is_ai_evaluated")),
            language=lang
        )

        # Compile grounded strengths & specific improvement suggestions
        strengths, suggestions = self._compile_grounded_feedback(
            problem=problem,
            code=clean_code,
            execution_status=execution_status,
            correctness_eval=correctness_eval,
            complexity_eval=complexity_eval,
            quality_eval=quality_eval,
            approach_eval=approach_eval,
            independent_eval=independent_eval,
            unique_hints_used=unique_hints_used
        )

        # Runtime & Language performance context
        runtime_context = self._get_runtime_performance_context(
            runtime_ms=runtime_ms,
            language=lang
        )

        return {
            "overall_score": overall_score,
            "scoring_status": scoring_status,
            "is_empty_submission": False,
            "is_provisional": is_provisional,
            "breakdown": breakdown,
            "is_renormalized": is_renormalized,
            "passed_count": passed_count,
            "total_count": total_count,
            "unique_hints_used": unique_hints_used,
            "independent_score": independent_eval.get("raw_score", 10),
            "test_summary": {
                "passed": passed_count,
                "total": total_count,
                "status": execution_status,
                "has_hidden_tests": any(
                    (getattr(t, "error", None) == "[Hidden Test Case]") or
                    (isinstance(t, dict) and t.get("error") == "[Hidden Test Case]")
                    for t in (test_results or [])
                )
            },
            "performance": {
                "coding_time_seconds": coding_time_seconds,
                "coding_time_formatted": self._format_duration(coding_time_seconds),
                "execution_time_ms": round(runtime_ms, 2),
                "memory_usage_mb": round(memory_usage_mb, 2) if memory_usage_mb > 0 else None,
                "time_spent_away_seconds": time_spent_away_seconds,
                "tab_switch_count": tab_switch_count,
                "runtime_context": runtime_context
            },
            "complexity_analysis": {
                "estimated_time_complexity": complexity_eval.get("detected_time_complexity", "N/A"),
                "estimated_space_complexity": complexity_eval.get("detected_space_complexity", "N/A"),
                "expected_time_complexity": getattr(problem, "time_complexity", None) or "O(N)",
                "expected_space_complexity": getattr(problem, "space_complexity", None) or "O(1)",
                "complexity_status": complexity_eval.get("status", "evaluated")
            },
            "feedback": {
                "strengths": strengths,
                "improvement_suggestions": suggestions,
                "summary": self._generate_evaluation_summary(overall_score, correctness_eval, unique_hints_used)
            },
            "evaluator": evaluator_meta
        }

    def _evaluate_correctness(
        self,
        execution_status: str,
        passed_count: int,
        total_count: int,
        test_results: List[TestResult]
    ) -> Dict[str, Any]:
        """
        Calculates correctness strictly from test execution results:
        Formula: (Passed Tests / Total Evaluated Tests) * 40.
        Compilation failures, syntax errors, timeouts, and runtime errors receive 0 points.
        Missing or 0 test suites handled explicitly as unavailable.
        """
        if total_count <= 0:
            return {
                "ratio": 0.0,
                "is_available": False,
                "status": "unavailable",
                "notes": "No test cases were evaluated or test suite is unavailable.",
                "passed_count": 0,
                "total_count": 0
            }

        if execution_status in ("error", "compilation_error", "timeout"):
            msg = "Compilation failure or runtime error occurred; 0 tests passed."
            if execution_status == "timeout":
                msg = "Execution timed out (possible infinite loop or excessive recursion); 0 tests passed."
            elif execution_status in ("error", "compilation_error"):
                msg = "Runtime error or syntax exception encountered during test execution; 0 tests passed."
            return {
                "ratio": 0.0,
                "is_available": True,
                "status": "evaluated",
                "notes": msg,
                "passed_count": 0,
                "total_count": total_count
            }

        ratio = max(0.0, min(1.0, passed_count / float(total_count)))
        notes = f"Passed {passed_count} of {total_count} test cases ({round(ratio * 100, 1)}% accuracy)."
        return {
            "ratio": ratio,
            "is_available": True,
            "status": "evaluated",
            "notes": notes,
            "passed_count": passed_count,
            "total_count": total_count
        }

    def _evaluate_independent_problem_solving(self, unique_hints_used: int, is_code_submitted: bool = True) -> Dict[str, Any]:
        """
        Evaluates independent problem-solving based on unique hints revealed:
        0 hints -> 10/10
        1 hint  -> 9/10
        2 hints -> 7/10
        3 hints -> 4/10
        4+ hints -> 1/10
        """
        score = calculate_independent_score(unique_hints_used)
        if not is_code_submitted:
            return {
                "ratio": 0.0,
                "is_available": True,
                "status": "pending",
                "unique_hints_used": max(0, unique_hints_used),
                "raw_score": score,
                "notes": f"Independent problem-solving tracked ({unique_hints_used} hints used; potential {score}/10 pts), but hint points require a valid code submission."
            }

        ratio = max(0.0, min(1.0, score / 10.0))

        if unique_hints_used <= 0:
            notes = "Solved independently without hints (10/10 earned)."
        elif unique_hints_used == 1:
            notes = "Used 1 progressive hint during formulation (9/10 earned)."
        elif unique_hints_used == 2:
            notes = "Used 2 hints during problem solving (7/10 earned)."
        elif unique_hints_used == 3:
            notes = "Used 3 progressive hints (4/10 earned)."
        else:
            notes = f"Used {unique_hints_used} progressive hints (1/10 earned)."

        return {
            "ratio": ratio,
            "is_available": True,
            "status": "evaluated",
            "unique_hints_used": max(0, unique_hints_used),
            "raw_score": score,
            "notes": notes
        }

    def _evaluate_complexity(
        self,
        code: str,
        language: str,
        problem: Problem,
        execution_status: str = "success",
        passed_count: int = 0,
        total_count: int = 0,
        ast_feedback: Optional[Dict[str, Any]] = None,
        ai_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates time and space complexity using static analysis and AI where available.
        Does not award points if analysis is unavailable or execution failed.
        """
        # If code execution completely failed with syntax/compilation error or timeout
        if execution_status in ("error", "compilation_error", "timeout") or (ast_feedback and ast_feedback.get("syntax_error")):
            return {
                "ratio": 0.0,
                "is_available": False,
                "status": "N/A",
                "detected_time_complexity": "N/A",
                "detected_space_complexity": "N/A",
                "notes": "Complexity analysis is unavailable due to syntax, compilation, or execution failure."
            }

        # If zero test cases passed out of available tests, analysis is unreliable
        if total_count > 0 and passed_count == 0:
            return {
                "ratio": 0.0,
                "is_available": False,
                "status": "N/A",
                "detected_time_complexity": "N/A",
                "detected_space_complexity": "N/A",
                "notes": "Complexity analysis is unreliable because the submission failed all test cases."
            }

        if ai_data and "complexity_score_ratio" in ai_data:
            return {
                "ratio": max(0.0, min(1.0, float(ai_data["complexity_score_ratio"]))),
                "is_available": True,
                "status": "evaluated",
                "detected_time_complexity": ai_data.get("detected_time_complexity", "O(N)"),
                "detected_space_complexity": ai_data.get("detected_space_complexity", "O(1)"),
                "notes": ai_data.get("complexity_notes", "Evaluated via AI complexity inspector.")
            }

        # Static analysis for Python via AST
        if language == "python":
            time_c, space_c, ratio, notes = self._static_python_complexity(code, problem, ast_feedback, passed_count, total_count)
            return {
                "ratio": ratio,
                "is_available": True,
                "status": "evaluated",
                "detected_time_complexity": time_c,
                "detected_space_complexity": space_c,
                "notes": notes
            }

        # Static heuristic analysis for C, C++, Java
        if language in ["c", "cpp", "c++", "java"]:
            time_c, space_c, ratio, notes = self._static_c_cpp_java_complexity(code, language, problem)
            return {
                "ratio": ratio,
                "is_available": True,
                "status": "evaluated",
                "detected_time_complexity": time_c,
                "detected_space_complexity": space_c,
                "notes": notes
            }

        # If language is unknown or unsupported, mark N/A rather than fabricating
        return {
            "ratio": 0.0,
            "is_available": False,
            "status": "N/A",
            "detected_time_complexity": "N/A",
            "detected_space_complexity": "N/A",
            "notes": f"Static complexity analysis is unavailable for '{language}'. Weight renormalized proportionally."
        }

    def _static_python_complexity(
        self,
        code: str,
        problem: Problem,
        ast_feedback: Optional[Dict[str, Any]],
        passed_count: int = 1,
        total_count: int = 1
    ) -> Tuple[str, str, float, str]:
        expected_time = (getattr(problem, "time_complexity", None) or "O(N)").upper()
        detected_time = "O(1)"
        detected_space = "O(1)"
        ratio = 1.0
        notes = "Constant time operations detected."

        try:
            tree = ast.parse(code)
        except Exception:
            return ("N/A", "N/A", 0.0, "Syntax error prevented complexity parsing.")

        if len(tree.body) == 0:
            return ("N/A", "N/A", 0.0, "No executable statements detected.")

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.current_loop_depth = 0
                self.max_depth = 0
                self.curr_fn = None
                self.recursive_calls = {}
                self.memo_detected = False
                self.dict_set_detected = False
                self.has_sorted = False
                self.has_linear_builtin = False

            def visit_FunctionDef(self, node):
                prev_fn = self.curr_fn
                self.curr_fn = node.name
                self.recursive_calls[node.name] = 0
                self.generic_visit(node)
                self.curr_fn = prev_fn

            def visit_For(self, node):
                self.current_loop_depth += 1
                self.max_depth = max(self.max_depth, self.current_loop_depth)
                self.generic_visit(node)
                self.current_loop_depth -= 1

            def visit_While(self, node):
                self.current_loop_depth += 1
                self.max_depth = max(self.max_depth, self.current_loop_depth)
                self.generic_visit(node)
                self.current_loop_depth -= 1

            def visit_ListComp(self, node):
                self.current_loop_depth += len(node.generators)
                self.max_depth = max(self.max_depth, self.current_loop_depth)
                self.generic_visit(node)
                self.current_loop_depth -= len(node.generators)

            def visit_SetComp(self, node):
                self.current_loop_depth += len(node.generators)
                self.max_depth = max(self.max_depth, self.current_loop_depth)
                self.dict_set_detected = True
                self.generic_visit(node)
                self.current_loop_depth -= len(node.generators)

            def visit_DictComp(self, node):
                self.current_loop_depth += len(node.generators)
                self.max_depth = max(self.max_depth, self.current_loop_depth)
                self.dict_set_detected = True
                self.generic_visit(node)
                self.current_loop_depth -= len(node.generators)

            def visit_GeneratorExp(self, node):
                self.current_loop_depth += len(node.generators)
                self.max_depth = max(self.max_depth, self.current_loop_depth)
                self.generic_visit(node)
                self.current_loop_depth -= len(node.generators)

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    fn_name = node.func.id
                    if self.curr_fn and fn_name == self.curr_fn:
                        self.recursive_calls[fn_name] = self.recursive_calls.get(fn_name, 0) + 1
                    if fn_name in ("dict", "set"):
                        self.dict_set_detected = True
                    if fn_name in ("sorted",):
                        self.has_sorted = True
                    if fn_name in ("sum", "min", "max", "count", "map", "filter"):
                        self.has_linear_builtin = True
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("append", "add", "setdefault", "get"):
                        self.dict_set_detected = True
                    if node.func.attr == "sort":
                        self.has_sorted = True
                    if node.func.attr == "count":
                        self.has_linear_builtin = True
                self.generic_visit(node)

            def visit_Dict(self, node):
                self.dict_set_detected = True
                self.generic_visit(node)

            def visit_Set(self, node):
                self.dict_set_detected = True
                self.generic_visit(node)

            def visit_Subscript(self, node):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    self.memo_detected = True
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(tree)

        max_loop_depth = visitor.max_depth
        has_recursion = False
        recursive_branching = 1
        for fn_name, count in visitor.recursive_calls.items():
            if count > 0:
                has_recursion = True
                recursive_branching = max(recursive_branching, count)

        has_memo = visitor.memo_detected
        has_dict_or_set = visitor.dict_set_detected

        # Determine space complexity
        if has_dict_or_set or has_memo:
            detected_space = "O(N)"
        elif has_recursion:
            detected_space = "O(N) [Call Stack]"
        else:
            detected_space = "O(1)"

        # Determine time complexity & matching ratio
        if has_recursion:
            if recursive_branching > 1:
                if has_memo or "memo" in code.lower() or "cache" in code.lower() or "@lru_cache" in code:
                    detected_time = "O(N)"
                    ratio = 1.0
                    notes = "Memoized branching recursion detected (O(N) with state caching)."
                else:
                    detected_time = "O(2^N)"
                    ratio = 0.3 if "2^N" not in expected_time else 1.0
                    notes = "Unmemoized branching recursion detected (O(2^N) exponential time)."
            else:
                detected_time = "O(N)"
                ratio = 1.0
                notes = "Linear recursion detected (O(N) time)."
        elif max_loop_depth == 0:
            if visitor.has_sorted:
                detected_time = "O(N log N)"
                notes = "Built-in sorting operation detected (O(N log N))."
                ratio = 1.0 if ("N LOG N" in expected_time or "N" in expected_time) else 0.8
            elif visitor.has_linear_builtin:
                detected_time = "O(N)"
                notes = "Built-in linear sequence processing detected (O(N))."
                ratio = 1.0
            else:
                detected_time = "O(1)"
                if "O(1)" in expected_time or "1" in expected_time:
                    ratio = 1.0
                    notes = "Constant time operations match expected O(1) complexity."
                else:
                    if passed_count > 0 and passed_count == total_count:
                        ratio = 1.0
                        notes = "Optimal constant time closed-form formulation detected (O(1))."
                    else:
                        ratio = 0.5
                        notes = f"Detected constant time operations (O(1)); optimal target requires {getattr(problem, 'time_complexity', None) or 'O(N)'}."
        elif max_loop_depth == 1:
            detected_time = "O(N)"
            notes = "Single linear iteration detected (O(N) time)."
            ratio = 1.0
        elif max_loop_depth == 2:
            detected_time = "O(N^2)"
            if "N^2" in expected_time:
                ratio = 1.0
                notes = "Nested loop iteration matches expected O(N^2) complexity."
            else:
                ratio = 0.55
                notes = f"Nested loop detected (O(N^2)); optimal solution requires {getattr(problem, 'time_complexity', None) or 'O(N)'}."
        else:
            detected_time = f"O(N^{max_loop_depth})"
            ratio = 0.35
            notes = f"Deeply nested loops detected (O(N^{max_loop_depth}))."

        return (detected_time, detected_space, ratio, notes)

    def _static_c_cpp_java_complexity(
        self,
        code: str,
        language: str,
        problem: Problem
    ) -> Tuple[str, str, float, str]:
        expected_time = (problem.time_complexity or "O(N)").upper()
        # Clean comments
        clean_code = re.sub(r'//.*', '', code)
        clean_code = re.sub(r'/\*.*?\*/', '', clean_code, flags=re.DOTALL)

        # Detect loops & recursion
        loops = len(re.findall(r'\b(for|while)\b', clean_code))
        nested_loops = len(re.findall(r'\b(for|while)\s*\([^{}]*?\)\s*\{[^{}]*?\b(for|while)\b', clean_code, flags=re.DOTALL))
        has_recursion = bool(re.search(r'\b(\w+)\s*\([^)]*\)\s*\{[^{}]*\b\1\s*\(', clean_code, flags=re.DOTALL))
        has_hash_map = bool(re.search(r'\b(unordered_map|unordered_set|HashMap|HashSet|map)\b', clean_code))

        detected_space = "O(N)" if has_hash_map else ("O(N) [Call Stack]" if has_recursion else "O(1)")

        if has_recursion:
            detected_time = "O(N)"
            ratio = 1.0
            notes = f"Recursive implementation detected in {language.upper()}."
        elif nested_loops > 0:
            detected_time = "O(N^2)"
            if "N^2" in expected_time:
                ratio = 1.0
                notes = f"Nested loops match expected O(N^2) complexity in {language.upper()}."
            else:
                ratio = 0.55
                notes = f"Nested loops detected (O(N^2)); optimal target is {problem.time_complexity or 'O(N)'}."
        elif loops > 0:
            detected_time = "O(N)"
            ratio = 1.0
            notes = f"Linear iteration detected (O(N)) in {language.upper()}."
        else:
            detected_time = "O(1)"
            ratio = 1.0
            notes = f"Constant time operations detected in {language.upper()}."

        return (detected_time, detected_space, ratio, notes)

    def _evaluate_code_quality(
        self,
        code: str,
        language: str,
        execution_status: str,
        ast_feedback: Optional[Dict[str, Any]] = None,
        ai_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates code quality based on naming conventions, modularity, error handling, and style.
        Empty or unsubmitted code receives 0 points.
        """
        if not code or not code.strip():
            return {
                "ratio": 0.0,
                "is_available": True,
                "status": "not_evaluated",
                "notes": "No submitted code to evaluate code quality."
            }

        if ai_data and "quality_score_ratio" in ai_data:
            return {
                "ratio": max(0.0, min(1.0, float(ai_data["quality_score_ratio"]))),
                "is_available": True,
                "status": "evaluated",
                "notes": ai_data.get("quality_notes", "Evaluated via AI code quality analyzer.")
            }

        # Syntax or compilation failure prevents quality evaluation
        if (ast_feedback and ast_feedback.get("syntax_error")) or execution_status in ("compilation_error",):
            return {
                "ratio": 0.0,
                "is_available": True,
                "status": "evaluated",
                "notes": "Code quality cannot be validated due to syntax or compilation errors."
            }

        score = 1.0
        deductions = []
        notes_list = []

        # Check for single-letter variable names proliferation
        single_letter_vars = re.findall(r'\b[a-zA-Z]\b', code)
        # Exclude common loop indices i, j, k, n, s, t
        unclear_single = [v for v in single_letter_vars if v.lower() not in ('i', 'j', 'k', 'n', 's', 't', 'x', 'y')]
        if len(unclear_single) > 4:
            score -= 0.15
            deductions.append("Multiple single-letter variable names reduce readability")

        # Check for modularity / function definitions
        if language == "python":
            has_func = bool(re.search(r'\bdef\s+\w+\s*\(', code))
            if not has_func:
                score -= 0.2
                deductions.append("Solution lacks structured function encapsulation")
        elif language in ["c", "cpp", "c++", "java"]:
            has_func = bool(re.search(r'\b(void|int|bool|string|vector|double|char)\s+\w+\s*\(', code))
            if not has_func:
                score -= 0.2
                deductions.append("Solution lacks structured function signatures")

        # Check for extreme duplication / excessive lines
        lines = [line.strip() for line in code.split("\n") if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("//")]
        if len(lines) > 80:
            score -= 0.1
            deductions.append("Code is unusually lengthy; consider extracting reusable helpers")

        # Check for hardcoded edge-case hacks
        if re.search(r'if\s+(nums|s|n|arr|head)\s*==\s*\[\s*1\s*,\s*2\s*\]', code):
            score -= 0.25
            deductions.append("Hardcoded test case outputs detected instead of generalized algorithm")

        score = max(0.2, min(1.0, score))
        if deductions:
            notes_list.append("; ".join(deductions) + ".")
        else:
            notes_list.append("Well-structured, readable code with idiomatic conventions.")

        return {
            "ratio": score,
            "is_available": True,
            "status": "evaluated",
            "notes": " ".join(notes_list)
        }

    def _evaluate_approach(
        self,
        code: str,
        language: str,
        problem: Problem,
        correctness_eval: Dict[str, Any],
        ast_feedback: Optional[Dict[str, Any]] = None,
        ai_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates algorithmic problem-solving approach against problem topic and requirements.
        If a problem specifically requires backtracking or recursion, non-backtracking code
        does not receive full approach points merely because output is correct.
        """
        if not code or not code.strip():
            return {
                "ratio": 0.0,
                "is_available": True,
                "status": "not_evaluated",
                "notes": "No submitted code to evaluate problem-solving approach."
            }

        if ai_data and "approach_score_ratio" in ai_data:
            return {
                "ratio": max(0.0, min(1.0, float(ai_data["approach_score_ratio"]))),
                "is_available": True,
                "status": "evaluated",
                "notes": ai_data.get("approach_notes", "Evaluated via AI approach analyzer.")
            }

        # If tests failed completely due to compilation or 0 tests passed
        corr_ratio = correctness_eval.get("ratio", 1.0) if isinstance(correctness_eval, dict) else (1.0 if correctness_eval else 0.0)
        if corr_ratio == 0.0:
            return {
                "ratio": 0.0,
                "is_available": True,
                "status": "evaluated",
                "notes": "Problem-solving approach could not be validated due to compilation or execution failure."
            }

        topic = (getattr(problem, "topic", None) or (problem.get("category", "") if isinstance(problem, dict) else "") or (problem.get("topic", "") if isinstance(problem, dict) else "") or "").lower()
        title = (getattr(problem, "title", None) or (problem.get("title", "") if isinstance(problem, dict) else "") or "").lower()
        desc = (getattr(problem, "description", None) or (problem.get("description", "") if isinstance(problem, dict) else "") or "").lower()

        score = 0.8  # Baseline for code that compiles and passes tests
        notes_list = []

        is_backtracking_required = ("backtrack" in topic or "backtrack" in title or "backtracking" in desc)

        # 1. Backtracking requirement check
        if is_backtracking_required:
            # Check for choose-explore-unchoose or recursive branching with undo/slice/pop
            has_recursion = bool(re.search(r'\b(def|void|int|bool)\s+(\w+).*?\b\2\s*\(', code, flags=re.DOTALL))
            has_state_undo = bool(re.search(r'(\.pop\(\)|\.remove\(|\bpath\s*\+\s*\[|\bcurr\s*\+\s*\[)', code))
            has_library_bypass = bool(re.search(r'(itertools\.combinations|itertools\.permutations)', code))

            if has_library_bypass and not has_recursion:
                score = 0.4
                notes_list.append("Problem explicitly requires backtracking. Using itertools library bypass does not demonstrate required backtracking approach.")
            elif has_recursion and (has_state_undo or "path" in code or "track" in code):
                score = 1.0
                notes_list.append("Proper backtracking formulation deployed with state exploration and base-case termination.")
            elif has_recursion:
                score = 0.8
                notes_list.append("Recursive exploration deployed; ensure explicit choose-and-undo state management.")
            else:
                score = 0.5
                notes_list.append("Iterative generation used instead of the required backtracking pattern.")

        elif "recursion" in topic:
            if ast_feedback and ast_feedback.get("has_recursion"):
                if ast_feedback.get("has_base_case"):
                    score = 1.0
                    notes_list.append("Appropriate recursive formulation with conditional base case.")
                else:
                    score = 0.4
                    notes_list.append("Recursive call lacks explicit base case guard.")
            elif re.search(r'\b(def|void|int|bool)\s+(\w+).*?\b\2\s*\(', code, flags=re.DOTALL):
                score = 1.0
                notes_list.append("Recursive problem-solving approach successfully deployed.")
            else:
                score = 0.6
                notes_list.append("Solved iteratively rather than the intended recursive pattern.")

        elif "hash" in topic or "array" in topic:
            has_hash = bool(re.search(r'(\{|\bdict\b|\bset\b|\bunordered_map\b|\bHashMap\b)', code))
            if has_hash:
                score = 1.0
                notes_list.append("Effective use of hash-based lookup for optimal element retrieval.")
            else:
                score = 0.8
                notes_list.append("Linear or array scan applied.")

        elif "dynamic programming" in topic:
            has_table = bool(re.search(r'(\bdp\b|\bmemo\b|\btable\b|\[\s*0\s*\]\s*\*\s*n)', code))
            if has_table:
                score = 1.0
                notes_list.append("Optimal dynamic programming state table / memoization applied.")
            else:
                score = 0.7
                notes_list.append("Functional logic implemented; consider formalizing state transition table.")

        elif "stack" in topic or "queue" in topic:
            has_stack = bool(re.search(r'(\.append\(|\.pop\(|\bstack\b|\bqueue\b|\bpush\b)', code))
            if has_stack:
                score = 1.0
                notes_list.append("Proper LIFO/FIFO data structure semantics used.")
            else:
                score = 0.75
                notes_list.append("Handled sequential elements without dedicated stack/queue primitives.")

        else:
            if correctness_eval["ratio"] == 1.0:
                score = 1.0
                notes_list.append("Algorithmic formulation successfully satisfies all problem constraints.")
            else:
                score = 0.7
                notes_list.append("Approached problem logic; partially satisfies edge cases.")

        final_ratio = max(0.1, min(1.0, score))
        return {
            "ratio": final_ratio,
            "is_available": True,
            "status": "evaluated",
            "notes": " ".join(notes_list) if notes_list else "Valid algorithmic approach solving the core requirements."
        }

    def _renormalize_and_score(
        self,
        dimensions: Dict[str, Dict[str, Any]],
        base_weights: Dict[str, float]
    ) -> Tuple[Dict[str, Any], float, bool]:
        """
        Calculates the dimension scores and total score across all 5 dimensions.
        If any dimension is marked is_available == False (e.g. N/A),
        the remaining available dimensions are renormalized proportionally so that
        the maximum possible score remains exactly 100.
        """
        available_dims = [dim for dim, data in dimensions.items() if data.get("is_available", True)]
        is_renormalized = len(available_dims) < len(dimensions)

        total_available_weight = sum(base_weights.get(dim, 0.0) for dim in available_dims)
        breakdown = {}
        total_points = 0.0

        for dim, data in dimensions.items():
            raw_w = base_weights.get(dim, 0.0)
            is_avail = data.get("is_available", True)

            if not is_avail or total_available_weight == 0:
                breakdown[dim] = {
                    "points_earned": 0.0,
                    "max_points": 0.0,
                    "base_weight": raw_w,
                    "effective_weight": 0.0,
                    "ratio": 0.0,
                    "is_available": False,
                    "status": "N/A",
                    "notes": data.get("notes", "Dimension unavailable. Renormalized to remaining dimensions.")
                }
            else:
                # Renormalize weight proportionally to 100
                effective_weight = (raw_w / total_available_weight) * 100.0
                ratio = data.get("ratio", 0.0)
                points = round(ratio * effective_weight, 1)
                total_points += points

                breakdown[dim] = {
                    "points_earned": points,
                    "max_points": round(effective_weight, 1),
                    "base_weight": raw_w,
                    "effective_weight": round(effective_weight, 1),
                    "ratio": round(ratio, 3),
                    "is_available": True,
                    "status": data.get("status", "evaluated"),
                    "notes": data.get("notes", "")
                }

        # Ensure score breakdown strictly adds up to final_score and does not exceed 100 due to rounding
        sum_breakdown = round(sum(d["points_earned"] for d in breakdown.values()), 1)
        all_perfect = len(available_dims) > 0 and all(dimensions[d].get("ratio", 0.0) >= 0.999 for d in available_dims)
        if all_perfect and sum_breakdown != 100.0 and available_dims:
            diff = round(100.0 - sum_breakdown, 1)
            largest_dim = max(available_dims, key=lambda d: breakdown[d]["points_earned"])
            breakdown[largest_dim]["points_earned"] = round(breakdown[largest_dim]["points_earned"] + diff, 1)
        elif sum_breakdown > 100.0 and available_dims:
            diff = round(sum_breakdown - 100.0, 1)
            largest_dim = max(available_dims, key=lambda d: breakdown[d]["points_earned"])
            breakdown[largest_dim]["points_earned"] = round(breakdown[largest_dim]["points_earned"] - diff, 1)

        final_score = round(max(0.0, min(100.0, sum(d["points_earned"] for d in breakdown.values()))), 1)
        return breakdown, final_score, is_renormalized

    def _determine_evaluator_metadata(self, has_ai: bool, language: str) -> Dict[str, Any]:
        if has_ai:
            return {
                "evaluator_type": "hybrid_ai_static",
                "evaluator_label": "AI-Assisted & Automated Static Evaluation",
                "limitations": "Score incorporates Google Gemini algorithmic reasoning and automated test suites. Nuances in uncommon patterns may be estimated."
            }
        return {
            "evaluator_type": "static_analysis",
            "evaluator_label": "Deterministic AST & Automated Test Suite",
            "limitations": "Evaluated using deterministic static AST analysis, complexity inspection, and full automated test execution without external AI."
        }

    def _compile_grounded_feedback(
        self,
        problem: Problem,
        code: str,
        execution_status: str,
        correctness_eval: Dict[str, Any],
        complexity_eval: Dict[str, Any],
        quality_eval: Dict[str, Any],
        approach_eval: Dict[str, Any],
        independent_eval: Dict[str, Any],
        unique_hints_used: int
    ) -> Tuple[List[str], List[str]]:
        strengths = []
        suggestions = []

        # Correctness grounded feedback
        if correctness_eval["ratio"] == 1.0:
            strengths.append(f"Flawless functional correctness: passed all {correctness_eval['total_count']} automated test cases (40/40 pts).")
        elif correctness_eval["ratio"] > 0:
            pct = round(correctness_eval['ratio'] * 100)
            pts = round(correctness_eval['ratio'] * 40.0, 1)
            strengths.append(f"Solved core logic passing {correctness_eval['passed_count']} of {correctness_eval['total_count']} test cases ({pct}%, {pts}/40 pts).")
            suggestions.append("Check failing edge conditions (e.g. empty inputs, boundaries, negative values) to reach 100% test passing.")
        else:
            if execution_status == "timeout":
                suggestions.append("Address infinite loop / unbounded recursion causing execution timeout.")
            else:
                suggestions.append("Fix runtime / syntax exceptions so the solution can execute test cases cleanly.")

        # Complexity grounded feedback
        detected_time = complexity_eval.get("detected_time_complexity")
        if detected_time and detected_time not in ("N/A", "O(2^N)", "O(N^2)") and complexity_eval["ratio"] >= 0.8:
            strengths.append(f"Efficient time complexity: achieved {detected_time} execution.")
        elif detected_time in ("O(2^N)", "O(N^2)") and complexity_eval["ratio"] < 0.8:
            suggestions.append(f"Optimize time complexity: detected {detected_time}; consider {problem.time_complexity or 'O(N)'} using memoization or hash tables.")

        # Quality grounded feedback
        if quality_eval["ratio"] >= 0.8:
            strengths.append("Code demonstrates clean structure, proper encapsulation, and readable identifiers.")
        elif quality_eval["ratio"] < 0.7:
            suggestions.append("Refactor variable names to be more descriptive and ensure consistent modular organization.")

        # Approach grounded feedback
        if approach_eval["ratio"] >= 0.85:
            strengths.append(f"Algorithmic approach aligns cleanly with expected {problem.topic} requirements.")
        elif approach_eval["ratio"] < 0.7:
            suggestions.append(f"Review core {problem.topic} patterns to address the problem requirements more directly.")

        # Independent problem solving grounded feedback
        if unique_hints_used <= 0:
            strengths.append("Demonstrated complete independence: solved without revealing any hints (10/10 independent score).")
        elif unique_hints_used == 1:
            strengths.append("Strong self-direction with minimal guidance: used only 1 hint (9/10 independent score).")
        elif unique_hints_used == 2:
            strengths.append("Good problem-solving momentum with 2 progressive hints (7/10 independent score).")
        elif unique_hints_used == 3:
            suggestions.append("Try to formulate state transitions and base cases independently before unlocking additional hints (3 hints used, 4/10).")
        else:
            suggestions.append(f"High hint dependence ({unique_hints_used} hints used, 1/10). Review problem patterns in advance to build independent formulation skills.")

        if not strengths:
            strengths.append("Attempt was submitted and evaluated against automated test specifications.")
        if not suggestions:
            suggestions.append("Great job! Try optimizing space complexity or exploring an alternate data structure.")

        return strengths, suggestions

    def _get_runtime_performance_context(self, runtime_ms: float, language: str) -> str:
        ms = round(runtime_ms, 2)
        if language == "python":
            return f"{ms} ms (Python interpreted runtime; baseline interpreter overhead is typically 5-25 ms)."
        elif language in ["c", "cpp", "c++"]:
            return f"{ms} ms (C/C++ native compiled runtime; typically < 5 ms for algorithmic workloads)."
        elif language == "java":
            return f"{ms} ms (Java JVM bytecode execution; includes JVM classloading overhead)."
        return f"{ms} ms."

    def _generate_evaluation_summary(self, overall_score: float, correctness_eval: Dict[str, Any], unique_hints_used: int) -> str:
        hint_text = f"with {unique_hints_used} hint{'s' if unique_hints_used != 1 else ''}" if unique_hints_used > 0 else "without any hints"
        if overall_score >= 90:
            return f"Outstanding performance ({overall_score}/100)! High correctness, optimal complexity, and completed {hint_text}."
        elif overall_score >= 75:
            return f"Solid execution ({overall_score}/100). The solution is largely correct {hint_text} with minor room for optimization."
        elif overall_score >= 50:
            return f"Good initial foundation ({overall_score}/100). Focus on passing remaining edge cases and refining complexity."
        else:
            return f"Needs revision ({overall_score}/100). Review test failures and compiler diagnostics to resolve syntax or runtime exceptions."

    def _format_duration(self, seconds: int) -> str:
        if seconds <= 0:
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
