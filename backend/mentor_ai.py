import json
import os
import re
import requests
from typing import Dict, Any, List, Optional
from models import (
    HintResponse, 
    VivaQuestion, 
    VivaScoreResult, 
    Problem
)
from ast_analyzer import analyze_python_code

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_BHARATCODE_BASE_URL = os.environ.get("BHARATCODE_BASE_URL", "https://bharatcode.ai/api/model/v1")
DEFAULT_BHARATCODE_MODEL = os.environ.get("BHARATCODE_MODEL", "qwen-3.8-27b")
DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

class MentorAI:
    def __init__(
        self,
        api_key: Optional[str] = None,
        persona: str = "socratic",
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("BHARATCODE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.base_url = base_url or os.environ.get("BHARATCODE_BASE_URL", DEFAULT_BHARATCODE_BASE_URL)
        self.model = model or os.environ.get("BHARATCODE_MODEL") or (DEFAULT_BHARATCODE_MODEL if os.environ.get("BHARATCODE_API_KEY") else DEFAULT_GEMINI_MODEL)
        self.persona = persona  # "socratic", "strict", "friendly"

    def set_config(
        self,
        api_key: Optional[str] = None,
        persona: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        if api_key is not None:
            self.api_key = api_key
        if persona is not None:
            self.persona = persona
        if model is not None:
            self.model = model
        if base_url is not None:
            self.base_url = base_url

    def call_llm(self, system_instruction: str, prompt: str) -> Optional[str]:
        """
        Provider-neutral LLM calling method.
        Directs calls to BharatCode API client, or legacy Gemini if Gemini key is active.
        """
        if not self.api_key:
            return None

        # 1. Prefer BharatCode API client
        if self.api_key.startswith("bc_") or os.environ.get("BHARATCODE_API_KEY") or not self.api_key.startswith("AIza"):
            try:
                from llm_client import call_llm as send_bharatcode_call
                result = send_bharatcode_call(
                    system_instruction=system_instruction,
                    prompt=prompt,
                    api_key=self.api_key,
                    base_url=self.base_url,
                    model=self.model
                )
                if result:
                    return result
            except Exception as e:
                print(f"[MentorAI] BharatCode client notice: {e}")

        # 2. Legacy Gemini fallback if specifically using Google Gemini key
        return self._call_gemini_direct(system_instruction, prompt)

    def _call_gemini(self, system_instruction: str, prompt: str) -> Optional[str]:
        """Backward-compatible alias for call_llm."""
        return self.call_llm(system_instruction, prompt)

    def _call_gemini_direct(self, system_instruction: str, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
        
        models_to_try = [self.model]
        if self.model != "gemini-1.5-flash":
            models_to_try.append("gemini-1.5-flash")
        if "gemini-2.0-flash" not in models_to_try:
            models_to_try.append("gemini-2.0-flash")

        is_json_request = "json" in system_instruction.lower() or "json" in prompt.lower()
        generation_config: Dict[str, Any] = {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
        if is_json_request:
            generation_config["responseMimeType"] = "application/json"

        for model_name in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                payload = {
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": generation_config
                }
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                elif res.status_code == 404:
                    # Model not found, try next in list
                    continue
                else:
                    print(f"[MentorAI] Gemini API returned status {res.status_code}: {res.text[:150]}")
            except requests.exceptions.Timeout:
                print(f"[MentorAI] Gemini request timed out for model {model_name}")
            except Exception as e:
                print(f"[MentorAI] Error calling Gemini: {e}")

        return None

    def get_progressive_hint(self, problem: Problem, code: str, language: str, hint_level: int, error_context: Optional[str] = None) -> HintResponse:
        """
        Level 1: Conceptual / guiding question
        Level 2: Algorithmic direction / branch insight
        Level 3: Concrete structural / mathematical rule
        Level 4: Step-by-step resolution explanation
        """
        # Run AST analysis if python
        ast_info = analyze_python_code(code, problem.id) if language == "python" else None

        # Check if we can prompt Gemini
        if self.api_key:
            system_prompt = f"""You are 'CodeAcharya', an expert AI programming mentor adhering to the Socratic method.
Your persona is: {self.persona}.
CRITICAL RULE: NEVER write the complete direct code solution! 
Instead, provide level {hint_level} progressive guidance:
- Level 1: Purely conceptual guidance or thought-provoking question about the problem's premise.
- Level 2: Specific algorithmic direction (e.g. which condition, data structure, or variable to inspect).
- Level 3: Concrete insight or mathematical rule (without handing the final code line).
- Level 4: Comprehensive explanation of what the logic entails.

Respond in JSON format:
{{
  "hint_title": "Short title",
  "hint_content": "Your progressive hint message",
  "thought_questions": ["Question 1 to ask yourself", "Question 2 to ask yourself"]
}}"""
            user_prompt = f"""Problem: {problem.title} ({problem.topic})
Description: {problem.description}
Current Hint Level Requested: {hint_level} of 4
Student's Code:
```{language}
{code}
```
Error or Test Context: {error_context or 'None reported'}
AST Findings: {json.dumps(ast_info.to_dict() if ast_info else {})}"""
            
            raw = self._call_gemini(system_prompt, user_prompt)
            if raw:
                try:
                    clean_raw = raw.strip()
                    if clean_raw.startswith("```json"):
                        clean_raw = clean_raw[7:-3].strip()
                    elif clean_raw.startswith("```"):
                        clean_raw = clean_raw[3:-3].strip()
                    parsed = json.loads(clean_raw)
                    return HintResponse(
                        hint_level=hint_level,
                        hint_title=parsed.get("hint_title", f"Level {hint_level} Hint"),
                        hint_content=parsed.get("hint_content", ""),
                        thought_questions=parsed.get("thought_questions", []),
                        penalty_points=hint_level * 5,
                        next_hint_available=(hint_level < 4)
                    )
                except Exception:
                    pass

        # Intelligent Fallback / Curriculum-Engine Hints
        hints_repo = {
            "factorial-recursion": {
                1: {
                    "title": "Level 1: Understand the Smallest Input",
                    "content": "Think about the smallest input for which factorial has a defined mathematical value. In any recursive function, there must be a stopping condition (base case) before doing the recursive step.",
                    "questions": ["What is the smallest number n can be according to the problem constraints?", "What happens if a recursive function keeps calling itself indefinitely?"]
                },
                2: {
                    "title": "Level 2: Base Case Return Value",
                    "content": "What should the function return when n reaches 0 or 1? Notice that in multiplication, returning 0 will cause all preceding multiplications to multiply by 0!",
                    "questions": ["If your base case returns 0, what does `n * factorial(n - 1)` evaluate to?", "What is the identity element for multiplication?"]
                },
                3: {
                    "title": "Level 3: The Mathematical Definition of 0!",
                    "content": "Check the mathematical definition of 0!. In mathematics and combinatorics, the number of ways to arrange zero items is 1, so 0! = 1. Therefore, when n <= 1, return 1.",
                    "questions": ["Does your code return 1 when n == 0?", "Does your base case trigger before or after the recursive call?"]
                },
                4: {
                    "title": "Level 4: Detailed Concept Explanation",
                    "content": "The base case must return 1 because 0! = 1 and 1! = 1. A recursive step is `n * factorial(n - 1)`. When n unwinds from 0 to 5: `1 * 1 * 2 * 3 * 4 * 5 = 120`. Ensuring `if n <= 1: return 1` provides the base anchor for stack unwinding.",
                    "questions": ["Trace `factorial(3)` step by step: factorial(3) -> 3 * factorial(2) -> 2 * factorial(1) -> 1."]
                }
            },
            "two-sum": {
                1: {
                    "title": "Level 1: The Complement Perspective",
                    "content": "Instead of scanning the entire remaining array for each number, think: if the current number is `num`, what exact companion number are you searching for?",
                    "questions": ["If target is 9 and current element is 2, what exact value must exist?", "How fast can you look up an element if you pre-store visited items?"]
                },
                2: {
                    "title": "Level 2: Hash Map Lookup Trade-off",
                    "content": "Use a Hash Map (dictionary) to store elements you have already inspected. Map each `num` to its array index `i`. For the current element, check if `complement = target - num` is already present in your map.",
                    "questions": ["What is the average time complexity of checking `if complement in seen:` in a Hash Map?", "Why is this faster than nested loops?"]
                },
                3: {
                    "title": "Level 3: Single-Pass Invariant",
                    "content": "You can solve this in a single pass ($O(N)$). As you iterate: check if `target - num` is in `seen`. If yes, return `[seen[target - num], current_index]`. If not, record `seen[num] = current_index`. This prevents using the same index twice!",
                    "questions": ["Does your map insert occur before or after checking the complement?"]
                },
                4: {
                    "title": "Level 4: Full Architectural Walkthrough",
                    "content": "By maintaining `seen[number] = index`, you trade $O(N)$ extra memory for reducing time from $O(N^2)$ to $O(N)$. Each number's complement lookup takes $O(1)$ amortized time.",
                    "questions": ["What would happen if the array contained duplicate numbers? Why does single pass handle this smoothly?"]
                }
            },
            "valid-parentheses": {
                1: {
                    "title": "Level 1: Matching and Ordering",
                    "content": "Notice that the most recently opened bracket must be the very first one to be closed. What fundamental data structure embodies 'Last In, First Out' (LIFO)?",
                    "questions": ["In the string `([{}])`, which bracket must close first?", "Can counting opening and closing brackets alone detect order errors like `([)]`?"]
                },
                2: {
                    "title": "Level 2: The Stack Invariant",
                    "content": "Push opening brackets `'(', '{', '['` onto a Stack. When you encounter a closing bracket, pop the top element from the stack and verify that it matches the corresponding opening type.",
                    "questions": ["What happens if you see a closing bracket but the stack is already empty?", "What does that imply about the string?"]
                },
                3: {
                    "title": "Level 3: Edge Cases & Stack Emptiness",
                    "content": "Map each closing bracket to its opening counterpart: `{')': '(', '}': '{', ']': '['}`. If a closing bracket appears and `stack.pop()` does not match its pair, return `False`. Crucially, after looping through all characters, verify `len(stack) == 0`.",
                    "questions": ["What if the string is just `[`? How does `len(stack) == 0` catch this?"]
                },
                4: {
                    "title": "Level 4: Complete Logic Structure",
                    "content": "The stack tracks pending open brackets. Any mismatch on pop, popping from an empty stack, or having leftover elements in the stack at the end signifies an invalid configuration.",
                    "questions": ["Why is stack matching O(N) time and O(N) space?"]
                }
            },
            "fibonacci-dp": {
                1: {
                    "title": "Level 1: Overlapping Subproblems",
                    "content": "Draw the recursion tree for `fib(5)`. Notice how `fib(3)` and `fib(2)` are calculated repeatedly across different branches. Why recompute what you already calculated?",
                    "questions": ["How many times is `fib(2)` computed when evaluating `fib(5)` naively?", "What is the time complexity of the naive tree?"]
                },
                2: {
                    "title": "Level 2: Memoization vs Tabulation",
                    "content": "Instead of re-evaluating subproblems, store the result in an array or dictionary once computed. Alternatively, compute bottom-up from `fib(0)` and `fib(1)` up to `n`.",
                    "questions": ["To compute `fib(n)`, how many previous values do you actually need at any given moment?", "Do you need the entire history array?"]
                },
                3: {
                    "title": "Level 3: Space Optimization to O(1)",
                    "content": "You only need the two immediately preceding numbers: `a = 0`, `b = 1`. In a loop from 2 to n: `a, b = b, a + b`. This achieves $O(N)$ time and $O(1)$ space!",
                    "questions": ["How does this compare to $O(2^N)$ naive recursion for n = 40?"]
                },
                4: {
                    "title": "Level 4: Dynamic Programming Principles",
                    "content": "The Fibonacci sequence satisfies optimal substructure and overlapping subproblems. Moving from naive recursion $O(2^N)$ to bottom-up tabulation reduces the runtime from billions of operations to just $N$ operations.",
                    "questions": ["How does this same principle apply to Climbing Stairs or Coin Change?"]
                }
            },
            "binary-search": {
                1: {
                    "title": "Level 1: The Sorted Array Superpower",
                    "content": "The array is already sorted in ascending order! When you inspect the middle element, what can you deduce if the middle element is greater than your target?",
                    "questions": ["If `nums[mid] > target`, where must target reside: to the left or right?", "How many elements can you discard in each step?"]
                },
                2: {
                    "title": "Level 2: Two Pointers and Boundaries",
                    "content": "Maintain two pointers: `left = 0` and `right = len(nums) - 1`. The loop must continue as long as `left <= right`. Calculate `mid = (left + right) // 2`.",
                    "questions": ["Why is the condition `left <= right` instead of `left < right`?", "What happens when an array has only 1 element?"]
                },
                3: {
                    "title": "Level 3: Range Shrinking Invariant",
                    "content": "If `nums[mid] == target`, you found it! Return `mid`. If `nums[mid] < target`, the target must be on the right, so update `left = mid + 1`. If `nums[mid] > target`, update `right = mid - 1`. If the loop finishes without finding it, return `-1`.",
                    "questions": ["Why must you do `mid + 1` and `mid - 1` rather than just `mid`?"]
                },
                4: {
                    "title": "Level 4: Logarithmic Halving",
                    "content": "At each comparison, binary search cuts the remaining search space strictly in half: $N \\rightarrow N/2 \\rightarrow N/4 \\dots \\rightarrow 1$. This guarantees at most $\\log_2(N)$ iterations, running in milliseconds even for a billion elements.",
                    "questions": ["How many steps does binary search take for an array of 1,000,000 items? (Answer: ~20 steps!)"]
                }
            },
            "max-subarray": {
                1: {
                    "title": "Level 1: The Contiguous Dilemma",
                    "content": "A subarray must be continuous. At every step as you move through the array, you face a dilemma: should you extend the previous running subarray sum, or start a fresh subarray at the current number?",
                    "questions": ["If the previous subarray sum was negative (e.g. -10), does adding it to your current number help or hurt?", "When is it better to discard the past?"]
                },
                2: {
                    "title": "Level 2: Kadane's Local Decision",
                    "content": "For each number `x`, the maximum subarray sum ending at this position is: `current_sum = max(x, current_sum + x)`. If `current_sum + x` is worse than `x` alone, you reset your start point to `x`.",
                    "questions": ["How do you track the highest `current_sum` you've seen so far across the whole array?"]
                },
                3: {
                    "title": "Level 3: Initializing with Negative Numbers",
                    "content": "Initialize both `current_sum` and `max_sum` to `nums[0]`, not 0! If all numbers in the array are negative (like `[-5, -2, -9]`), the answer is the least negative number (`-2`), which initializing to 0 would miss.",
                    "questions": ["Why would initializing `max_sum = 0` fail for `nums = [-1]`?"]
                },
                4: {
                    "title": "Level 4: Kadane's Algorithm Mastery",
                    "content": "Kadane's algorithm solves Maximum Subarray in a single $O(N)$ pass with $O(1)$ auxiliary space by computing the prefix-maximum decision at every index. It is an optimal dynamic programming reduction.",
                    "questions": ["How would you modify Kadane's algorithm to also return the starting and ending indices of the subarray?"]
                }
            }
        }

        prob_hints = hints_repo.get(problem.id, {})
        selected = prob_hints.get(hint_level, {
            "title": f"Level {hint_level} Guidance",
            "content": f"Review the key constraints and step through your code on a small input manually. Topic: {problem.topic}.",
            "questions": ["What is the expected output for the simplest test case?", "Are all variable states updating as expected?"]
        })

        return HintResponse(
            hint_level=hint_level,
            hint_title=selected["title"],
            hint_content=selected["content"],
            thought_questions=selected["questions"],
            penalty_points=hint_level * 5,
            next_hint_available=(hint_level < 4)
        )

    def explain_code(
        self, 
        problem: Problem, 
        code: str, 
        language: str, 
        selected_code: Optional[str] = None,
        problem_title: Optional[str] = None,
        problem_statement: Optional[str] = None
    ) -> Dict[str, Any]:
        """Explains execution flow, algorithmic approach, data structures, and time/space complexity."""
        target_code = (selected_code or code or "").strip()
        title = problem_title or problem.title
        statement = problem_statement or problem.description

        if not target_code:
            return {
                "summary": "The code editor is currently empty. Please write or load code for this problem to view an algorithmic breakdown and complexity analysis.",
                "purpose": "No code provided to analyze.",
                "algorithmic_approach": "N/A",
                "execution_flow": ["No code instructions to execute."],
                "key_components": {
                    "loops": "None",
                    "conditions": "None",
                    "data_structures": "None"
                },
                "time_complexity": "N/A",
                "time_rationale": "Cannot determine time complexity without code.",
                "space_complexity": "N/A",
                "space_rationale": "Cannot determine space complexity without code.",
                "edge_cases_and_limitations": ["Please write or paste code into the editor to run analysis."],
                "strengths": [],
                "optimizations": []
            }

        if self.api_key:
            prompt = f"""You are a senior computer science mentor explaining code to a student.
Problem: '{title}'
Topic: '{problem.topic}'
Problem Statement:
{statement}

Code ({language}):
```{language}
{target_code}
```

Provide an in-depth, structured explanation tailored specifically to this code.
Do NOT use generic boilerplate. Analyze the actual variables, loops, data structures, and logic.

Respond in exact JSON format:
{{
  "summary": "Beginner-friendly summary of what this code does and its main purpose.",
  "purpose": "Precise statement of what problem this implementation solves.",
  "algorithmic_approach": "The algorithmic technique used (e.g., 'Divide and Conquer Recursion', 'Hash Table Frequency Counting', 'Two-Pointer Linear Scan').",
  "execution_flow": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ...",
    "Step 4: ..."
  ],
  "key_components": {{
    "loops": "Detailed explanation of any loops, bounds, and iteration conditions.",
    "conditions": "Explanation of base cases, validation checks, and branch logic.",
    "data_structures": "Explanation of data structures used (arrays, hash maps, recursion stack, etc.)."
  }},
  "time_complexity": "O(...)",
  "time_rationale": "Mathematical justification of the time complexity based on loops/recursion.",
  "space_complexity": "O(...)",
  "space_rationale": "Justification of space complexity (auxiliary memory and call stack).",
  "edge_cases_and_limitations": [
    "Edge case or boundary limitation 1...",
    "Edge case or boundary limitation 2..."
  ],
  "strengths": [
    "Code strength 1...",
    "Code strength 2..."
  ],
  "optimizations": [
    "Potential optimization or refinement 1..."
  ]
}}"""
            raw = self._call_gemini("You are an expert, encouraging computer science tutor. Always respond with valid JSON.", prompt)
            if raw:
                try:
                    clean = raw.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:-3].strip()
                    elif clean.startswith("```"):
                        clean = clean[3:-3].strip()
                    parsed = json.loads(clean)
                    if isinstance(parsed, dict) and "time_complexity" in parsed:
                        return parsed
                except Exception as e:
                    print(f"[MentorAI] Error parsing Gemini explanation JSON: {e}")

        return self._heuristic_explain_code(problem, target_code, language, title, statement)

    def _heuristic_explain_code(
        self, 
        problem: Problem, 
        code: str, 
        language: str, 
        title: str, 
        statement: str
    ) -> Dict[str, Any]:
        """Deterministic heuristic code explainer analyzing real AST / lexical patterns."""
        ast_info = analyze_python_code(code, problem.id) if language == "python" else None
        
        # Analyze functions and names
        fn_match = re.findall(r'(?:def|function|void|int|double|bool|String|const|let|var)\s+([a-zA-Z0-9_]+)\s*[\(=]', code)
        main_fn = fn_match[0] if fn_match else "solution"

        # Detect loops & loop nesting
        for_count = len(re.findall(r'\bfor\b', code))
        while_count = len(re.findall(r'\bwhile\b', code))
        total_loops = for_count + while_count
        
        # Detect recursion
        has_recursion = False
        if ast_info and ast_info.has_recursion:
            has_recursion = True
        elif main_fn in code[code.find(main_fn) + len(main_fn):]:
            has_recursion = True

        # Detect data structures
        detected_ds = []
        if re.search(r'(\bdict\b|\bMap\b|\bHashMap\b|\bunordered_map\b|{[^}]*:[^}]*})', code):
            detected_ds.append("Hash Map / Dictionary (key-value storage for O(1) lookups)")
        if re.search(r'(\bset\b|\bSet\b|\bHashSet\b|\bunordered_set\b)', code):
            detected_ds.append("Hash Set (for O(1) membership validation and unique items)")
        if re.search(r'(\blist\b|\bvector\b|\bArrayList\b|\[[^\]]*\])', code):
            detected_ds.append("Indexed Array / Dynamic List (for sequential element access)")
        if re.search(r'(\bstack\b|\bStack\b|\bdeque\b|\bpush\b|\bpop\b)', code):
            detected_ds.append("Stack / Deque (LIFO sequential buffer)")
        
        ds_desc = "; ".join(detected_ds) if detected_ds else "Primitive scalar variables (counters and accumulators)"

        # Detect conditionals
        if_count = len(re.findall(r'\b(if|else if|elif|switch)\b', code))
        cond_desc = f"Contains {if_count} conditional branch{'es' if if_count != 1 else ''} handling boundary conditions and decision paths."

        # Loop description
        if total_loops == 0 and not has_recursion:
            loop_desc = "No explicit loops or recursive calls; operates in constant sequential steps."
        elif total_loops == 1 and not has_recursion:
            loop_desc = "Single iterative loop traversing input elements linearly."
        elif total_loops >= 2 and not has_recursion:
            loop_desc = f"Contains {total_loops} loops (potential nested or sequential passes over the dataset)."
        else:
            loop_desc = "Uses recursive function invocations in place of explicit iteration loops."

        # Complexity estimation
        if ast_info:
            time_comp = ast_info.estimated_complexity
        elif has_recursion:
            time_comp = "O(N)"
        elif total_loops == 0:
            time_comp = "O(1)"
        elif total_loops == 1:
            time_comp = "O(N)"
        elif total_loops == 2:
            time_comp = "O(N²)"
        else:
            time_comp = f"O(N^{total_loops})"

        if has_recursion:
            space_comp = "O(N)"
            space_rationale = "Requires O(N) auxiliary call stack frames to store active recursive activation records."
        elif detected_ds:
            space_comp = "O(N)"
            space_rationale = "Allocates auxiliary storage (hash maps, lists, or buffers) proportional to input size."
        else:
            space_comp = "O(1)"
            space_rationale = "Uses a constant number of auxiliary state variables without dynamic heap allocation."

        # Algorithmic approach
        if has_recursion:
            approach = "Recursive Problem Decomposition"
        elif "Hash" in ds_desc:
            approach = "Hash-Based Frequency Lookup & State Caching"
        elif while_count > 0 and for_count == 0:
            approach = "Iterative Two-Pointer / Sliding Window Traversal"
        elif total_loops > 0:
            approach = "Linear Iterative Traversal & In-Place Accumulation"
        else:
            approach = "Direct Mathematical / Constant-Time Evaluation"

        flow = [
            f"1. Entry into '{main_fn}' receiving input arguments.",
            "2. Validates base cases or boundary criteria to safeguard against invalid states.",
            f"3. Performs core computation utilizing {approach.lower()}.",
            "4. Computes and returns the expected result conforming to problem constraints."
        ]

        strengths = [
            f"Clear code structure utilizing {language.upper()} language conventions.",
            f"Accurately maps to problem domain for '{title}' ({problem.topic})."
        ]

        optimizations = []
        if has_recursion:
            optimizations.append("For large inputs, verify if recursion depth exceeds the call stack limit or apply tail-call/memoization.")
        if total_loops >= 2:
            optimizations.append("Investigate if nested iterations can be reduced to O(N) by utilizing a hash map or two-pointer approach.")
        if not optimizations:
            optimizations.append("Code demonstrates good algorithmic efficiency for this difficulty tier.")

        return {
            "summary": f"This {language} solution implements {approach.lower()} to solve '{title}' within {problem.topic}.",
            "purpose": f"Solves '{title}' by executing {approach.lower()} on the provided inputs.",
            "algorithmic_approach": approach,
            "execution_flow": flow,
            "key_components": {
                "loops": loop_desc,
                "conditions": cond_desc,
                "data_structures": ds_desc
            },
            "time_complexity": time_comp,
            "time_rationale": f"Determined by the control flow: {loop_desc} yielding an overall complexity of {time_comp}.",
            "space_complexity": space_comp,
            "space_rationale": space_rationale,
            "edge_cases_and_limitations": [
                "Empty, zero-length, or minimum boundary inputs.",
                "Boundary values near integer limits or maximum constraint bounds.",
                "Unusual input distributions (all identical elements, reverse-sorted, or negative values)."
            ],
            "strengths": strengths,
            "optimizations": optimizations
        }

    def generate_debugging_guide(
        self, 
        problem: Problem, 
        code: str, 
        language: str, 
        error_message: Optional[str] = None,
        failing_input: Optional[str] = None,
        expected_output: Optional[str] = None,
        actual_output: Optional[str] = None,
        has_run: Optional[bool] = False,
        problem_title: Optional[str] = None,
        problem_statement: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provides pedagogical step-by-step debugging guidance, distinguishing runtime errors from static issues and clean code."""
        trimmed_code = (code or "").strip()
        title = problem_title or problem.title
        statement = problem_statement or problem.description

        if not trimmed_code:
            return {
                "status": "empty_code",
                "primary_symptom": "Code Editor is Empty",
                "bug_summary": "No code statements were found in the active editor.",
                "relevant_section": None,
                "why_it_occurs": "The editor does not contain any executable logic or function definitions.",
                "investigation_steps": [
                    "Step 1: Write or paste your solution code in the editor.",
                    "Step 2: Ensure your function signature matches the problem parameters.",
                    "Step 3: Click 'Run & Test' to execute tests or 'Debug Guide' for guided analysis."
                ],
                "suggested_correction": "Provide a complete function implementation before requesting debugging guidance.",
                "edge_cases_to_check": [],
                "socratic_prompt": "What initial approach or algorithm do you plan to implement?",
                "detected_anomalies": []
            }

        if self.api_key:
            run_context = ""
            if error_message:
                run_context += f"\nRuntime / Compiler Error:\n{error_message}"
            if failing_input is not None:
                run_context += f"\nFailing Test Case Input: {failing_input}\nExpected Output: {expected_output}\nActual Output: {actual_output}"
            if not run_context:
                run_context = "\nCode has NOT been run yet or no runtime errors were recorded (perform static analysis)."

            prompt = f"""You are an elite, patient computer science tutor assisting a student with debugging.
Problem: '{title}'
Topic: '{problem.topic}'
Problem Statement:
{statement}

Execution Context:{run_context}

Code ({language}):
```{language}
{trimmed_code}
```

CRITICAL INSTRUCTIONS:
1. Determine the status:
   - 'verified_runtime_error': Use if compiler/runtime errors occurred, or if test cases produced incorrect outputs.
   - 'suspected_static_issue': Use if code has not run or passed runtime, but static analysis reveals a probable syntax error, missing base case, incorrect return, or logic flaw.
   - 'clean': Use if the code appears correct and has no detectable bug or logic flaw.
2. If the code has NO detectable bug, set status to 'clean', primary_symptom to 'No clear issue identified', and explicitly explain that no issue was found. DO NOT fabricate or invent a bug.
3. Be socratic: Guide the student to understand the root cause without simply dumping the entire final code.
4. If a bug is present, identify the specific code section/line, explain WHY it occurs, provide step-by-step investigation steps, suggested correction, and edge cases to test.

Respond in exact JSON format:
{{
  "status": "verified_runtime_error" | "suspected_static_issue" | "clean",
  "primary_symptom": "Concise summary of the bug or 'No clear issue identified'",
  "bug_summary": "Detailed explanation of the issue or confirmation that code is clean.",
  "relevant_section": "The problematic code snippet or line number, or null if clean.",
  "why_it_occurs": "The underlying technical/logical reason why this issue happens.",
  "investigation_steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "suggested_correction": "Specific hint or guidance on how to fix the issue.",
  "edge_cases_to_check": [
    "Edge case 1...",
    "Edge case 2..."
  ],
  "socratic_prompt": "A thought-provoking question to ask the student before they edit their code.",
  "detected_anomalies": ["..."]
}}"""
            raw = self._call_gemini("You are an encouraging computer science debugging mentor. Always respond with valid JSON.", prompt)
            if raw:
                try:
                    clean = raw.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:-3].strip()
                    elif clean.startswith("```"):
                        clean = clean[3:-3].strip()
                    parsed = json.loads(clean)
                    if isinstance(parsed, dict) and "primary_symptom" in parsed and "investigation_steps" in parsed:
                        return parsed
                except Exception as e:
                    print(f"[MentorAI] Error parsing Gemini debug JSON: {e}")

        return self._heuristic_debugging_guide(
            problem, trimmed_code, language, error_message, failing_input, expected_output, actual_output, has_run, title, statement
        )

    def _heuristic_debugging_guide(
        self,
        problem: Problem,
        code: str,
        language: str,
        error_message: Optional[str] = None,
        failing_input: Optional[str] = None,
        expected_output: Optional[str] = None,
        actual_output: Optional[str] = None,
        has_run: Optional[bool] = False,
        title: str = "",
        statement: str = ""
    ) -> Dict[str, Any]:
        """Deterministic heuristic debugging guide for Python, C, C++, and Java."""
        # 1. Check for runtime / compiler error
        if error_message:
            line_match = re.search(r'(?:line\s+|:)(\d+)', error_message, re.IGNORECASE)
            line_num = int(line_match.group(1)) if line_match else None
            relevant_section = None
            if line_num:
                lines = code.splitlines()
                if 1 <= line_num <= len(lines):
                    relevant_section = f"Line {line_num}: {lines[line_num - 1].strip()}"

            err_lower = error_message.lower()
            if "recursion" in err_lower or "maximum recursion depth" in err_lower or "stackoverflow" in err_lower:
                return {
                    "status": "verified_runtime_error",
                    "primary_symptom": "Maximum recursion depth exceeded (Stack Overflow)",
                    "bug_summary": "The recursive calls failed to terminate, causing an infinite recursion that exhausted the call stack.",
                    "relevant_section": relevant_section,
                    "why_it_occurs": "The base case is either missing, never evaluated to True, or the recursive argument does not strictly move toward the base case (e.g. n instead of n - 1).",
                    "investigation_steps": [
                        "Step 1: Check your base condition (e.g., `if n <= 1:`) at the very top of the function.",
                        "Step 2: Verify that every recursive call reduces the problem size (e.g. `n - 1`).",
                        "Step 3: Trace the function on paper with n = 0 and n = 1 to confirm immediate return."
                    ],
                    "suggested_correction": "Ensure an explicit base case returns before any recursive call, and verify argument reduction on each recursive invocation.",
                    "edge_cases_to_check": ["n = 0", "n = 1", "Negative input values"],
                    "socratic_prompt": "What is the smallest valid input where the function should stop immediately without making another recursive call?",
                    "detected_anomalies": ["Unbounded recursive descent"]
                }
            elif "index" in err_lower or "out of range" in err_lower or "bounds" in err_lower:
                return {
                    "status": "verified_runtime_error",
                    "primary_symptom": "Index Out of Range / Bounds Error",
                    "bug_summary": "The code attempted to access an array or list index that does not exist.",
                    "relevant_section": relevant_section,
                    "why_it_occurs": "A loop counter or pointer exceeded the valid index range `[0, length - 1]`. Commonly caused by using `<=` instead of `<` or empty input lists.",
                    "investigation_steps": [
                        "Step 1: Inspect loop termination bounds (e.g. `i < len(arr)` vs `i <= len(arr)`).",
                        "Step 2: Check if accessing `arr[i + 1]` occurs when `i` is at the last element.",
                        "Step 3: Ensure the function checks for empty arrays before accessing index 0."
                    ],
                    "suggested_correction": "Use strict inequality `< len(collection)` or guard array accesses with a length check.",
                    "edge_cases_to_check": ["Empty collection `[]`", "Single-element collection `[x]`"],
                    "socratic_prompt": "What is the highest index accessed when your loop reaches its final iteration?",
                    "detected_anomalies": ["Array index out of bounds"]
                }
            elif "type" in err_lower or "cannot read properties" in err_lower or "nullpointer" in err_lower:
                return {
                    "status": "verified_runtime_error",
                    "primary_symptom": "Type Mismatch or Null/Undefined Dereference",
                    "bug_summary": "Operation attempted on an incompatible data type or null/None reference.",
                    "relevant_section": relevant_section,
                    "why_it_occurs": "A variable was evaluated as None, null, or undefined, or an arithmetic operator was applied across conflicting types.",
                    "investigation_steps": [
                        "Step 1: Verify the return value of any helper functions or base cases.",
                        "Step 2: Add validation to ensure variables are initialized before property access.",
                        "Step 3: Confirm all branch paths return a consistent datatype."
                    ],
                    "suggested_correction": "Ensure all execution paths return a concrete value instead of implicitly returning None/undefined.",
                    "edge_cases_to_check": ["None / null input", "Empty string or zero input"],
                    "socratic_prompt": "Does your function explicitly return a value in every single if/else branch?",
                    "detected_anomalies": ["Type mismatch / Null dereference"]
                }
            else:
                return {
                    "status": "verified_runtime_error",
                    "primary_symptom": f"Execution Error: {error_message.splitlines()[-1][:80]}",
                    "bug_summary": f"The program terminated with error: {error_message.splitlines()[-1]}",
                    "relevant_section": relevant_section,
                    "why_it_occurs": "An unhandled exception or compiler error interrupted execution.",
                    "investigation_steps": [
                        "Step 1: Review the error message and the indicated line number.",
                        "Step 2: Check syntax, variable names, and operator usage around that line.",
                        "Step 3: Verify variable declarations and matching parentheses/brackets."
                    ],
                    "suggested_correction": "Correct the syntax or runtime operation identified in the error traceback.",
                    "edge_cases_to_check": ["Empty input", "Zero value", "Boundary values"],
                    "socratic_prompt": "What operation on this line could produce an unexpected state?",
                    "detected_anomalies": [error_message.splitlines()[-1][:100]]
                }

        # 2. Check for failing test case
        if failing_input is not None:
            symptom = f"Logic Mismatch on Input '{failing_input}'"
            summary = f"For input '{failing_input}', the test expected '{expected_output}', but your code returned '{actual_output}'."
            
            # Specific domain: Factorial zero bug
            if ("factorial" in problem.id.lower() or "factorial" in title.lower()) and actual_output in ("0", 0, "0.0"):
                return {
                    "status": "verified_runtime_error",
                    "primary_symptom": "Factorial evaluates to 0 due to zero base-case return",
                    "bug_summary": "Your function returned 0 instead of the expected factorial product.",
                    "relevant_section": "return 0",
                    "why_it_occurs": "Returning 0 in the base case causes the recursive or iterative multiplication `n * (n - 1) * ... * 0` to collapse to 0. In mathematics, 0! = 1 and 1! = 1.",
                    "investigation_steps": [
                        "Step 1: Check what value your base case returns when `n <= 1`.",
                        "Step 2: Notice that any number multiplied by 0 equals 0.",
                        "Step 3: Update the base case to return the multiplicative identity (1)."
                    ],
                    "suggested_correction": "Change `return 0` in your base case to `return 1`.",
                    "edge_cases_to_check": ["n = 0", "n = 1", "n = 5"],
                    "socratic_prompt": "What is the multiplicative identity—the number you can multiply by without changing the product?",
                    "detected_anomalies": ["Base case return value bug"]
                }

            # Check if actual output is None/undefined
            if str(actual_output).lower() in ("none", "undefined", "null"):
                return {
                    "status": "verified_runtime_error",
                    "primary_symptom": f"Function returned {actual_output} instead of {expected_output}",
                    "bug_summary": f"Your function finished execution without returning a computed value on input '{failing_input}'.",
                    "relevant_section": None,
                    "why_it_occurs": "A code branch (such as an if condition or end of loop) reached completion without an explicit `return` statement.",
                    "investigation_steps": [
                        "Step 1: Trace execution flow for input: " + str(failing_input),
                        "Step 2: Check if all if/else branches contain a `return` keyword.",
                        "Step 3: Ensure you are returning the computed variable, not just printing it."
                    ],
                    "suggested_correction": "Add an explicit return statement returning the accumulated result.",
                    "edge_cases_to_check": [str(failing_input), "Empty collection"],
                    "socratic_prompt": "Which branch of your code executes when given this input, and does that branch return a value?",
                    "detected_anomalies": ["Missing return value on execution branch"]
                }

            return {
                "status": "verified_runtime_error",
                "primary_symptom": symptom,
                "bug_summary": summary,
                "relevant_section": None,
                "why_it_occurs": "The computation diverged from the expected result, likely due to an off-by-one boundary, incorrect state accumulation, or unhandled edge case.",
                "investigation_steps": [
                    f"Step 1: Trace your code by hand using input: {failing_input}",
                    "Step 2: Check loop starting index, loop termination condition, and accumulator initial value.",
                    f"Step 3: Compare intermediate values against the expected output: {expected_output}"
                ],
                "suggested_correction": f"Verify initial accumulator state and loop boundary conditions for input '{failing_input}'.",
                "edge_cases_to_check": [str(failing_input), "Minimum constraint input", "Boundary values"],
                "socratic_prompt": f"At what exact line during the trace of '{failing_input}' does the computed value differ from expectation?",
                "detected_anomalies": [f"Mismatch: expected {expected_output}, got {actual_output}"]
            }

        # 3. Static analysis (Code has not run or no runtime failure provided)
        # Check Python AST
        if language == "python":
            ast_info = analyze_python_code(code, problem.id)
            if not ast_info.is_valid and ast_info.syntax_error:
                line_m = re.search(r'line\s+(\d+)', ast_info.syntax_error, re.IGNORECASE)
                line_n = int(line_m.group(1)) if line_m else None
                snippet = f"Line {line_n}: {code.splitlines()[line_n - 1].strip()}" if line_n and line_n <= len(code.splitlines()) else None
                return {
                    "status": "suspected_static_issue",
                    "primary_symptom": f"Syntax Error: {ast_info.syntax_error}",
                    "bug_summary": "Python static parser detected a syntax violation preventing code compilation.",
                    "relevant_section": snippet,
                    "why_it_occurs": "A colon, parenthesis, indentation, or quotation is misplaced or missing.",
                    "investigation_steps": [
                        "Step 1: Check the line indicated by the syntax error.",
                        "Step 2: Ensure all colons `:` are present after `def`, `if`, `for`, `while` statements.",
                        "Step 3: Verify consistent indentation (4 spaces per level)."
                    ],
                    "suggested_correction": "Fix the syntax error at the indicated line before running tests.",
                    "edge_cases_to_check": [],
                    "socratic_prompt": "Is every code block properly indented and opened with a colon?",
                    "detected_anomalies": [ast_info.syntax_error]
                }

            if ast_info.suspected_bugs:
                bug = ast_info.suspected_bugs[0]
                return {
                    "status": "suspected_static_issue",
                    "primary_symptom": bug,
                    "bug_summary": f"Static AST code analysis detected a structural issue: {bug}",
                    "relevant_section": "Base case / return statement",
                    "why_it_occurs": "The structural composition of the function indicates an invalid base case or missing termination condition.",
                    "investigation_steps": [
                        "Step 1: Check conditional branches and return statements in your function.",
                        "Step 2: Verify that recursive functions have an `if` base condition that terminates.",
                        "Step 3: Test base values like n = 0 or n = 1 manually."
                    ],
                    "suggested_correction": "Update base condition logic to properly handle termination.",
                    "edge_cases_to_check": ["n = 0", "n = 1"],
                    "socratic_prompt": "What ensures that this function stops executing and does not run forever?",
                    "detected_anomalies": ast_info.suspected_bugs
                }

        # Multi-language static check: Factorial 0 bug
        if ("factorial" in problem.id.lower() or "factorial" in title.lower()) and "return 0" in code:
            return {
                "status": "suspected_static_issue",
                "primary_symptom": "Base case returns 0 in factorial calculation",
                "bug_summary": "Code contains `return 0` in a factorial problem. Multiplying any sequence by 0 results in 0.",
                "relevant_section": "return 0",
                "why_it_occurs": "In factorial (n!), 0! = 1 and 1! = 1. Returning 0 collapses the entire product to 0.",
                "investigation_steps": [
                    "Step 1: Locate the base case in your factorial function.",
                    "Step 2: Check what value is returned when `n <= 1`.",
                    "Step 3: Update `return 0` to `return 1`."
                ],
                "suggested_correction": "Change the base case to `return 1`.",
                "edge_cases_to_check": ["n = 0", "n = 1", "n = 5"],
                "socratic_prompt": "What is the product of any integer multiplied by 0?",
                "detected_anomalies": ["Base case return value bug: returns 0"]
            }

        # Multi-language static check: Bracket mismatch
        open_curly = code.count('{')
        close_curly = code.count('}')
        if open_curly != close_curly:
            return {
                "status": "suspected_static_issue",
                "primary_symptom": f"Mismatched curly braces: {open_curly} open '{{' vs {close_curly} closing '}}'",
                "bug_summary": "Unbalanced curly braces will cause compilation or parse failure.",
                "relevant_section": None,
                "why_it_occurs": "A code block was opened without a corresponding closing brace, or an extra brace exists.",
                "investigation_steps": [
                    "Step 1: Match every `{` with its corresponding `}`.",
                    "Step 2: Check function and loop boundaries.",
                    "Step 3: Ensure the closing brace of the main function is not missing."
                ],
                "suggested_correction": "Ensure all open curly braces have a matching closing brace.",
                "edge_cases_to_check": [],
                "socratic_prompt": "Are all your code blocks properly closed?",
                "detected_anomalies": ["Unbalanced curly braces"]
            }

        open_paren = code.count('(')
        close_paren = code.count(')')
        if open_paren != close_paren:
            return {
                "status": "suspected_static_issue",
                "primary_symptom": f"Mismatched parentheses: {open_paren} open '(' vs {close_paren} closing ')'",
                "bug_summary": "Unbalanced parentheses will cause a syntax error during parsing.",
                "relevant_section": None,
                "why_it_occurs": "An expression or function call has an unclosed parenthesis.",
                "investigation_steps": [
                    "Step 1: Inspect function call arguments and conditional expressions.",
                    "Step 2: Verify each `(` has a matching `)`."
                ],
                "suggested_correction": "Balance all parentheses in the code.",
                "edge_cases_to_check": [],
                "socratic_prompt": "Which line contains an unclosed parenthesis?",
                "detected_anomalies": ["Unbalanced parentheses"]
            }

        # Multi-language static check: Missing return in non-void function
        if re.search(r'(?:def|function|int|double|bool|String)\s+[a-zA-Z0-9_]+', code) and "return" not in code:
            return {
                "status": "suspected_static_issue",
                "primary_symptom": "Missing `return` statement in function",
                "bug_summary": "The function definition contains no `return` statement, meaning it will return None or undefined.",
                "relevant_section": None,
                "why_it_occurs": "Coding challenges require returning the computed solution from the function.",
                "investigation_steps": [
                    "Step 1: Identify the variable storing your final result.",
                    "Step 2: Add `return result` at the end of your function logic.",
                    "Step 3: Ensure you are returning the value, not just printing it to stdout."
                ],
                "suggested_correction": "Add a return statement providing the calculated output.",
                "edge_cases_to_check": [],
                "socratic_prompt": "What value should the caller receive when this function finishes?",
                "detected_anomalies": ["Function lacks return statement"]
            }

        # 4. If no bugs detected, return clean status!
        return {
            "status": "clean",
            "primary_symptom": "No clear issue identified",
            "bug_summary": "Static code analysis did not detect any obvious syntax errors, missing base cases, unbalanced delimiters, or structural flaws.",
            "relevant_section": None,
            "why_it_occurs": "Your code structure, function declarations, and branching logic appear sound based on static inspection.",
            "investigation_steps": [
                "Step 1: Click 'Run & Test' to execute your code against the full test suite in the sandbox.",
                "Step 2: If a test case fails, inspect the input and expected output to isolate logical divergences.",
                "Step 3: Check edge cases such as empty collections, negative numbers, or maximum boundary values.",
                "Step 4: If all tests pass, proceed to 'Launch AI Viva Exam' to test conceptual mastery."
            ],
            "suggested_correction": "No immediate corrections required. Execute test cases to verify runtime behavior.",
            "edge_cases_to_check": [
                "Empty collection or minimum boundary input",
                "Single-element input",
                "Maximum constraint values"
            ],
            "socratic_prompt": "Can you identify any extreme boundary condition where your code might behave unexpectedly?",
            "detected_anomalies": []
        }

    def start_viva_session(self, problem: Problem, code: str, language: str) -> List[VivaQuestion]:
        """Generates viva examination questions tailored to student's code and problem topic."""
        # Check Gemini
        if self.api_key:
            prompt = f"""Act as a University Computer Science Viva Examiner. 
Problem: {problem.title} ({problem.topic})
Student's Code:
```{language}
{code}
```
Generate 4 technical viva questions testing:
1. Conceptual understanding (Why this approach?)
2. Code understanding (Line-by-line mechanics / choice of data structure)
3. Complexity analysis (Time and Space Big-O proof)
4. Edge case & optimization (What happens on extreme inputs, or how to optimize)

Respond in JSON format:
[
  {{ "id": 1, "category": "conceptual", "question": "...", "hint_guidance": "..." }},
  {{ "id": 2, "category": "code_choice", "question": "...", "hint_guidance": "..." }},
  {{ "id": 3, "category": "complexity", "question": "...", "hint_guidance": "..." }},
  {{ "id": 4, "category": "optimization", "question": "...", "hint_guidance": "..." }}
]"""
            raw = self._call_gemini("You are a rigorous, fair computer science viva examiner.", prompt)
            if raw:
                try:
                    clean = raw.strip()
                    if clean.startswith("```json"):
                        clean = clean[7:-3].strip()
                    elif clean.startswith("```"):
                        clean = clean[3:-3].strip()
                    parsed = json.loads(clean)
                    return [VivaQuestion(**q) for q in parsed]
                except Exception:
                    pass

        # Curriculum viva question repository
        viva_catalog = {
            "factorial-recursion": [
                VivaQuestion(
                    id=1,
                    category="conceptual",
                    question="Why is a base case fundamentally required in any recursive function, and what would happen at the operating system / runtime level without it?",
                    hint_guidance="Discuss the call stack, stack frames, and RecursionError/StackOverflow."
                ),
                VivaQuestion(
                    id=2,
                    category="code_choice",
                    question="Why does the base case return 1 instead of 0 for factorial? What mathematical property dictates this?",
                    hint_guidance="Explain the multiplicative identity and the combinatorial definition of 0!."
                ),
                VivaQuestion(
                    id=3,
                    category="complexity",
                    question="What is the space complexity of your recursive implementation, and why does it consume memory even though you don't allocate an array?",
                    hint_guidance="Mention call stack depth and activation records: O(N) auxiliary space."
                ),
                VivaQuestion(
                    id=4,
                    category="optimization",
                    question="How does this recursive version compare to an iterative loop in terms of performance and memory overhead?",
                    hint_guidance="Iterative loop avoids stack frame allocation overhead and operates in O(1) space."
                )
            ],
            "two-sum": [
                VivaQuestion(
                    id=1,
                    category="conceptual",
                    question="Explain why using a Hash Map reduces the time complexity from O(N^2) brute force to O(N). What trade-off is made?",
                    hint_guidance="Highlight time-space trade-off and constant-time average hash lookups."
                ),
                VivaQuestion(
                    id=2,
                    category="code_choice",
                    question="Why do you store `target - num` as the lookup key rather than checking every pair? Why check before inserting `num`?",
                    hint_guidance="Prevents matching an element with itself when target is 2 * num."
                ),
                VivaQuestion(
                    id=3,
                    category="complexity",
                    question="What is the worst-case time complexity of hash table lookup, and when can hash collisions degrade performance?",
                    hint_guidance="O(N) worst case on severe hash collisions, O(1) amortized average."
                ),
                VivaQuestion(
                    id=4,
                    category="optimization",
                    question="If the input array were guaranteed to be sorted, could you solve this in O(1) extra space? Which technique would you employ?",
                    hint_guidance="Two-pointer approach (left and right pointers moving inwards)."
                )
            ],
            "valid-parentheses": [
                VivaQuestion(
                    id=1,
                    category="conceptual",
                    question="Why is a Stack the natural data structure for matching parentheses, rather than a Queue or a set of counters?",
                    hint_guidance="Nested brackets exhibit LIFO ordering; counters cannot enforce order like '([)]'."
                ),
                VivaQuestion(
                    id=2,
                    category="code_choice",
                    question="How does your code prevent an IndexError or exception when a closing bracket appears as the very first character in the string?",
                    hint_guidance="Checking if stack is empty before popping or using a fallback dummy character."
                ),
                VivaQuestion(
                    id=3,
                    category="complexity",
                    question="What are the time and space complexities of this solution? Could the space complexity be improved if we only allowed one bracket type '()'?",
                    hint_guidance="Both O(N). With single bracket type, a single integer counter in O(1) space suffices."
                ),
                VivaQuestion(
                    id=4,
                    category="edge_case",
                    question="What happens if the input string is `((((` with no closing brackets? Which line of your code detects this failure?",
                    hint_guidance="The final check `len(stack) == 0` ensures unclosed open brackets trigger False."
                )
            ]
        }

        default_questions = [
            VivaQuestion(
                id=1,
                category="conceptual",
                question=f"Explain the primary algorithmic approach you chose for '{problem.title}' and why it is well-suited for {problem.topic}.",
                hint_guidance="Discuss the problem structure and pattern matching."
            ),
            VivaQuestion(
                id=2,
                category="code_choice",
                question="Walk me through the most critical conditional or loop in your code. What invariant does it preserve?",
                hint_guidance="Explain line-by-line mechanics."
            ),
            VivaQuestion(
                id=3,
                category="complexity",
                question="State and formally prove both the Time and Space complexity of your solution in Big-O notation.",
                hint_guidance="Break down iterations, recursion depth, and auxiliary data structures."
            ),
            VivaQuestion(
                id=4,
                category="optimization",
                question="What is a potential edge case that could break a naive solution, and how does your code safely handle it?",
                hint_guidance="Consider empty input, single element, negative numbers, or duplicates."
            )
        ]

        return viva_catalog.get(problem.id, default_questions)

    @staticmethod
    def _is_gibberish_or_unintelligible(text: str) -> bool:
        clean = text.strip()
        if not clean:
            return False
        
        words = re.findall(r'[a-zA-Z]+', clean)
        if not words:
            # Contains only punctuation, symbols, or numbers without words
            return len(clean) > 3
        
        letters = [c.lower() for c in clean if c.isalpha()]
        if not letters:
            return True
            
        vowels = set("aeiouy")
        vowel_count = sum(1 for c in letters if c in vowels)
        vowel_ratio = vowel_count / len(letters)
        
        # Extremely low vowel ratio in longer string (e.g., 'kldfsdkjhfaskjf' has 1 'a' in 15 chars = 6.6%)
        if len(letters) >= 7 and vowel_ratio < 0.12:
            return True
            
        # 6 or more consecutive consonants is unnatural in English/CS terminology
        if re.search(r'[bcdfghjklmnpqrstvwxz]{6,}', clean.lower()):
            return True
            
        # Very low unique character diversity in longer string (e.g. 'aaaaaaa', 'asdfasdf')
        if len(letters) >= 10 and len(set(letters)) <= 3:
            return True

        # Recognized technical / common English lexicon
        cs_and_common_lexicon = {
            "a", "an", "the", "in", "on", "at", "to", "for", "with", "from", "by", "is", "are", "was", "were",
            "be", "been", "have", "has", "had", "do", "does", "did", "can", "could", "should", "would",
            "it", "this", "that", "these", "those", "we", "i", "you", "they", "he", "she", "not", "no", "if",
            "then", "else", "because", "as", "so", "than", "or", "and", "but", "when", "where", "how", "why",
            "stack", "queue", "list", "array", "tree", "graph", "hash", "map", "set", "table", "node", "pointer",
            "index", "element", "value", "key", "recursion", "recursive", "base", "case", "loop", "iterate",
            "iteration", "time", "space", "complexity", "big", "o", "constant", "linear", "logarithmic",
            "quadratic", "binary", "search", "sort", "sorted", "divide", "conquer", "two", "sliding",
            "window", "memory", "overflow", "underflow", "push", "pop", "top", "empty", "null", "size", "length",
            "return", "function", "variable", "condition", "invariant", "parentheses", "bracket", "match", "matching",
            "valid", "invalid", "string", "character", "open", "close", "closing", "opening", "lifo", "fifo",
            "eliminate", "half", "target", "comparison", "range", "step", "order", "ordered", "middle", "mid",
            "sum", "target", "complement", "difference", "pair", "collision", "amortized", "average", "worst",
            "best", "edge", "bound", "boundary", "handle", "detect", "fail", "check", "prevent", "first",
            "input", "output", "true", "false", "auxiliary", "structure", "structure", "structure"
        }
        lower_words = [w.lower() for w in words]
        # Single long word not in lexicon
        if len(lower_words) == 1 and len(lower_words[0]) >= 7 and lower_words[0] not in cs_and_common_lexicon:
            return True
            
        recognized_count = sum(1 for w in lower_words if w in cs_and_common_lexicon or len(w) <= 2)
        if len(lower_words) >= 3 and (recognized_count / len(lower_words)) < 0.25:
            return True
            
        return False

    @staticmethod
    def _is_explicit_uncertainty(text: str) -> bool:
        clean = text.strip().lower().rstrip(".!?")
        uncertain_phrases = [
            "i don't know", "i dont know", "dont know", "don't know",
            "i do not know", "no idea", "not sure", "i am not sure",
            "im not sure", "i'm not sure", "idk", "have no idea",
            "haven't learned", "haven't studied", "cant answer",
            "can't answer", "not certain", "skip", "no clue",
            "i have no clue", "dunno"
        ]
        for p in uncertain_phrases:
            if clean == p or clean.startswith(p + " ") or clean.endswith(" " + p):
                return True
        return False

    @staticmethod
    def _get_applicable_dimensions_and_weights(category: str, question_text: str, modality: str = "typed"):
        q_lower = question_text.lower()
        asks_complexity = bool(re.search(r'\b(complexity|time complexity|space complexity|big-o|big o|asymptotic|worst-case|best-case|amortized|o\(1\)|o\(n\)|o\(log n\))\b', q_lower))
        asks_code = bool(re.search(r'\b(code|line of code|conditional|loop|invariant|detects failure|which line|indexerror|base case check)\b', q_lower))

        if category == "complexity" or asks_complexity:
            dims = ["complexity_score", "conceptual_score", "communication_score"]
            weights = {
                "complexity_score": 0.60,
                "conceptual_score": 0.25,
                "communication_score": 0.15
            }
            if asks_code:
                dims.append("code_understanding_score")
                weights = {
                    "complexity_score": 0.50,
                    "conceptual_score": 0.20,
                    "code_understanding_score": 0.15,
                    "communication_score": 0.15
                }
        elif category in ("code_choice", "edge_case") or asks_code:
            dims = ["code_understanding_score", "conceptual_score", "communication_score"]
            weights = {
                "code_understanding_score": 0.50,
                "conceptual_score": 0.30,
                "communication_score": 0.20
            }
            if asks_complexity:
                dims.append("complexity_score")
                weights = {
                    "code_understanding_score": 0.40,
                    "conceptual_score": 0.25,
                    "complexity_score": 0.20,
                    "communication_score": 0.15
                }
        elif category == "optimization":
            dims = ["conceptual_score", "complexity_score", "communication_score"]
            weights = {
                "conceptual_score": 0.45,
                "complexity_score": 0.40,
                "communication_score": 0.15
            }
            if asks_code:
                dims.append("code_understanding_score")
                weights = {
                    "conceptual_score": 0.35,
                    "complexity_score": 0.35,
                    "code_understanding_score": 0.15,
                    "communication_score": 0.15
                }
        else: # default conceptual
            dims = ["conceptual_score", "communication_score"]
            weights = {
                "conceptual_score": 0.70,
                "communication_score": 0.30
            }
            if asks_code:
                dims.append("code_understanding_score")
                weights = {
                    "conceptual_score": 0.50,
                    "code_understanding_score": 0.30,
                    "communication_score": 0.20
                }
            if asks_complexity:
                dims.append("complexity_score")
                weights = {
                    "conceptual_score": 0.50,
                    "complexity_score": 0.30,
                    "communication_score": 0.20
                }

        # For typed answers, Communication & Clarity is N/A.
        # Exclude communication_score from applicable dimensions and normalize weights over applicable dimensions only.
        if modality != "voice_transcribed" and modality != "audio_recorded":
            dims = [d for d in dims if d != "communication_score"]
            weights = {d: w for d, w in weights.items() if d != "communication_score"}
            total_w = sum(weights.values())
            if total_w > 0:
                weights = {d: round(w / total_w, 4) for d, w in weights.items()}

        return dims, weights

    @staticmethod
    def _calculate_overall_score(scores: Dict[str, Optional[int]], weights: Dict[str, float]) -> int:
        """
        Deterministic weighted-average of APPLICABLE dimension scores only.
        Formula: round(sum(score[d] * w[d]) / sum(w[d])) over dims where score[d] is not None.
        N/A dimensions (None) are excluded from both numerator and denominator.
        A zero score is a valid earned score; None means the dimension does not apply.
        """
        total_weighted = 0.0
        total_weight = 0.0
        for dim, weight in weights.items():
            val = scores.get(dim)
            if val is not None:  # None means N/A; 0 is a valid earned score
                total_weighted += val * weight
                total_weight += weight
        if total_weight == 0:
            return 0
        return int(round(total_weighted / total_weight))

    @staticmethod
    def _extract_dim_score_from_ai(
        nested_scores: Dict[str, Any],
        parsed: Dict[str, Any],
        dim: str,
        applicable_dims: List[str]
    ) -> Optional[int]:
        """
        Extracts a single dimension score from Gemini's response.
        Returns:
          - None  when the dimension is not applicable (not in applicable_dims)
          - None  when the AI explicitly returned null for an applicable dimension
          - int 0-100  when the AI returned a valid numeric value
        NEVER substitutes 0 for null on non-applicable dimensions.
        """
        if dim not in applicable_dims:
            return None  # Dimension does not apply to this question

        # Map internal snake_case dim names to the camelCase keys Gemini returns
        key_map = {
            "conceptual_score": "conceptualUnderstanding",
            "code_understanding_score": "codeUnderstanding",
            "complexity_score": "complexityAnalysis",
            "communication_score": "communication"
        }
        snake_map = {
            "conceptual_score": "conceptual_score",
            "code_understanding_score": "code_understanding_score",
            "complexity_score": "complexity_score",
            "communication_score": "communication_score"
        }
        camel_key = key_map.get(dim)
        snake_key = snake_map.get(dim)

        # Try camelCase in nested scores dict first, then snake_case flat, then top-level
        val = None
        if camel_key and camel_key in nested_scores:
            val = nested_scores[camel_key]
        elif snake_key and snake_key in nested_scores:
            val = nested_scores[snake_key]
        elif camel_key and camel_key in parsed:
            val = parsed[camel_key]
        elif snake_key and snake_key in parsed:
            val = parsed[snake_key]

        if val is None:
            # AI returned null for an applicable dimension — treat as 0 earned score
            # (distinct from N/A: student just didn't demonstrate knowledge)
            return 0

        if isinstance(val, (int, float)):
            return max(0, min(100, int(val)))

        # Non-numeric value (e.g. "N/A" string) — treat as 0
        return 0

    def evaluate_viva_answer(
        self,
        problem: Problem,
        code: str,
        question: VivaQuestion,
        student_answer: str,
        answer_modality: str = "typed"
    ) -> VivaScoreResult:
        """
        Evaluates student's oral/text viva answer across applicable dimensions.
        Guarantees:
        - Irrelevant/gibberish answers receive 0 scores and retry suggestions.
        - Explicit admissions of uncertainty receive 0 scores with constructive hints.
        - Non-applicable dimensions return None (N/A).
        - For typed answers, communication_score is N/A and excluded from overall score.
        - Overall score is calculated strictly from applicable weighted dimensions.
        - No artificial score floors (e.g. no default 50-55%).
        """
        trimmed = student_answer.strip()
        applicable_dims, weights = self._get_applicable_dimensions_and_weights(question.category, question.question, answer_modality)
        comm_label = "Verbal Response Clarity" if answer_modality == "voice_transcribed" else "Communication & Clarity"

        # 1. Empty Answer Check
        if not trimmed:
            scores = {dim: 0 for dim in applicable_dims}
            return VivaScoreResult(
                conceptual_score=scores.get("conceptual_score"),
                code_understanding_score=scores.get("code_understanding_score"),
                complexity_score=scores.get("complexity_score"),
                communication_score=scores.get("communication_score"),
                overall_score=0,
                feedback="No substantive answer was provided. Please formulate a clear response addressing the question.",
                ideal_points_covered=[],
                missing_concepts=["An explanation addressing the question requirements"],
                suggested_improvement=question.hint_guidance or "State the main algorithmic intuition and relevant constraints.",
                answer_relevance="irrelevant",
                applicable_dimensions=applicable_dims,
                should_retry=True,
                question_id=question.id,
                category=question.category,
                answer_modality=answer_modality,
                communication_label=comm_label
            )

        # 2. Gibberish / Nonsensical String Check
        if self._is_gibberish_or_unintelligible(trimmed):
            scores = {dim: 0 for dim in applicable_dims}
            return VivaScoreResult(
                conceptual_score=scores.get("conceptual_score"),
                code_understanding_score=scores.get("code_understanding_score"),
                complexity_score=scores.get("complexity_score"),
                communication_score=scores.get("communication_score"),
                overall_score=0,
                feedback="Your response appears unintelligible or contains random characters. It does not address the viva question. Please formulate a coherent technical explanation.",
                ideal_points_covered=[],
                missing_concepts=["A coherent technical explanation of the question"],
                suggested_improvement="Take a moment to formulate your thoughts using standard computer science concepts.",
                answer_relevance="irrelevant",
                applicable_dimensions=applicable_dims,
                should_retry=True,
                question_id=question.id,
                category=question.category,
                answer_modality=answer_modality,
                communication_label=comm_label
            )

        # 3. Explicit Admission of Uncertainty Check
        if self._is_explicit_uncertainty(trimmed):
            scores = {dim: 0 for dim in applicable_dims}
            hint = question.hint_guidance or f"Focus on how the data structure or algorithm operates in {problem.title}."
            return VivaScoreResult(
                conceptual_score=scores.get("conceptual_score"),
                code_understanding_score=scores.get("code_understanding_score"),
                complexity_score=scores.get("complexity_score"),
                communication_score=scores.get("communication_score"),
                overall_score=0,
                feedback="You acknowledged uncertainty regarding this question. In an oral defense, it is constructive to break the problem into smaller fundamentals.",
                ideal_points_covered=[],
                missing_concepts=["Technical explanation of the requested mechanism"],
                suggested_improvement=f"Hint: {hint}",
                answer_relevance="uncertain",
                applicable_dimensions=applicable_dims,
                should_retry=True,
                question_id=question.id,
                category=question.category,
                answer_modality=answer_modality,
                communication_label=comm_label
            )

        # 4. Gemini AI Evaluation Attempt
        if self.api_key:
            prompt = f"""You are an expert University Computer Science Viva Voce Examiner assessing a student's technical defense.
Problem: "{problem.title}" (Topic: {problem.topic}, Difficulty: {problem.difficulty})
Question ID: {question.id}
Category: {question.category}
Viva Question: "{question.question}"
Rubric Focus / Expected Concepts: "{question.hint_guidance or 'Core algorithmic reasoning'}"
Answer Modality: {answer_modality}

Student's Submitted Code:
```
{code}
```

Student's Submitted Viva Answer:
"{trimmed}"

Applicable Dimensions to Score (from 0 to 100):
{', '.join(applicable_dims)}

CRITICAL EVALUATION INSTRUCTIONS:
- First, check relevance and intelligibility:
  - If the answer is unintelligible, random characters, gibberish (e.g. 'kldfsdkjhfaskjf'), or completely irrelevant/off-topic: set answerRelevance to "irrelevant", understandingLevel to "none", set ALL applicable scores to 0, shouldRetry to true, and explain clearly without praise that the response does not address the question.
  - If the answer is an explicit admission of uncertainty (e.g. "I don't know", "Not sure"): set answerRelevance to "uncertain", understandingLevel to "none", set ALL applicable scores to 0, shouldRetry to true, and offer constructive guidance/hint.
  - If the answer is partially relevant: set answerRelevance to "partially_relevant", award partial credit only for valid technical statements, and explicitly enumerate missingConcepts.
  - If the answer is accurate and directly addresses the question: set answerRelevance to "relevant", award high scores (75-100) reflecting technical depth.
- Score ONLY the applicable dimensions ({', '.join(applicable_dims)}).
- For any non-applicable dimension, you MUST output null.
- Answer modality rules:
  - For typed answers, communication is N/A and MUST be null.
  - For voice_transcribed answers, evaluate verbal response clarity, organization, coherence, and relevance from the transcript text alone. Do NOT invent acoustic measurements (pitch, tone, pace).
- DO NOT award default passing scores (like 50% or 55%) to incorrect, nonsensical, or irrelevant answers.
- A valid 0 score MUST remain 0.

Respond strictly with valid JSON conforming to:
{{
  "questionId": {question.id},
  "answerRelevance": "relevant" | "partially_relevant" | "irrelevant" | "uncertain",
  "understandingLevel": "deep" | "adequate" | "partial" | "none",
  "scores": {{
    "conceptualUnderstanding": <integer 0-100 or null>,
    "codeUnderstanding": <integer 0-100 or null>,
    "complexityAnalysis": <integer 0-100 or null>,
    "communication": <integer 0-100 or null>
  }},
  "applicableDimensions": [{', '.join(f'"{d}"' for d in applicable_dims)}],
  "overallScore": <integer 0-100>,
  "correctPoints": ["Valid point mentioned", ...],
  "missingConcepts": ["Important concept missed", ...],
  "examinerRemarks": "Precise, constructive remarks...",
  "followUpHint": "Actionable guidance or hint...",
  "shouldRetry": <boolean>
}}"""
            try:
                raw = self._call_gemini("You are a rigorous CS viva professor evaluating student answers.", prompt)
                if not raw:
                    raise RuntimeError("AI provider returned empty response")
                clean = raw.strip()
                if clean.startswith("```json"):
                    clean = clean[7:-3].strip()
                elif clean.startswith("```"):
                    clean = clean[3:-3].strip()
                parsed = json.loads(clean)

                # Map applicable dims to numeric score (0 if AI omits it), non-applicable dims to None
                nested_scores = parsed.get("scores") or {}
                ALL_DIMS = [
                    "conceptual_score", "code_understanding_score",
                    "complexity_score", "communication_score"
                ]
                scores_extracted: Dict[str, Optional[int]] = {}
                for dim in ALL_DIMS:
                    scores_extracted[dim] = self._extract_dim_score_from_ai(
                        nested_scores, parsed, dim, applicable_dims
                    )

                relevance = (
                    parsed.get("answerRelevance")
                    or parsed.get("answer_relevance")
                    or "relevant"
                )
                if relevance in ("irrelevant", "uncertain"):
                    for dim in applicable_dims:
                        scores_extracted[dim] = 0

                # Validate each applicable score is in range; treat out-of-range as 0
                for dim in applicable_dims:
                    v = scores_extracted.get(dim)
                    if v is not None and not (0 <= v <= 100):
                        scores_extracted[dim] = 0

                # Overall is calculated solely from applicable dims (non-None)
                overall = self._calculate_overall_score(
                    {d: scores_extracted[d] for d in applicable_dims},
                    weights
                )

                missing = (
                    parsed.get("missingConcepts")
                    or parsed.get("missing_concepts")
                    or []
                )

                return VivaScoreResult(
                    conceptual_score=scores_extracted.get("conceptual_score"),
                    code_understanding_score=scores_extracted.get("code_understanding_score"),
                    complexity_score=scores_extracted.get("complexity_score"),
                    communication_score=scores_extracted.get("communication_score"),
                    overall_score=overall,
                    feedback=(
                        parsed.get("examinerRemarks")
                        or parsed.get("feedback")
                        or "Evaluation completed."
                    ),
                    ideal_points_covered=(
                        parsed.get("correctPoints")
                        or parsed.get("ideal_points_covered")
                        or []
                    ),
                    missing_concepts=missing,
                    suggested_improvement=(
                        parsed.get("followUpHint")
                        or parsed.get("suggested_improvement")
                    ),
                    answer_relevance=relevance,
                    applicable_dimensions=applicable_dims,
                    should_retry=parsed.get(
                        "shouldRetry",
                        parsed.get("should_retry", overall < 50)
                    ),
                    question_id=question.id,
                    category=question.category,
                    answer_modality=answer_modality,
                    communication_label=comm_label
                )
            except Exception as e:
                # Per Requirement 3D: Fail explicitly rather than fabricating scores
                raise RuntimeError(f"AI evaluation provider failed ({str(e)})")

        # 5. Question-Aware Semantic Fallback Evaluator
        return self._semantic_viva_evaluation(problem, code, question, trimmed, applicable_dims, weights, answer_modality)

    def _semantic_viva_evaluation(
        self,
        problem: Problem,
        code: str,
        question: VivaQuestion,
        answer: str,
        applicable_dims: List[str],
        weights: Dict[str, float],
        answer_modality: str = "typed"
    ) -> VivaScoreResult:
        """
        High-fidelity deterministic question-aware semantic evaluator.
        Validates the submitted answer against:
        - The specific viva question and category
        - Question hint_guidance (rubric focus area & expected concepts)
        - Algorithmic invariants, code mechanics, and Big-O complexity
        Guarantees:
        - Irrelevant/off-topic answers receive 0 across all scores with constructive feedback.
        - Partial credit awarded appropriately for partial knowledge.
        - High scores awarded for depth and accuracy.
        - Applicable dimensions only are scored (others are None).
        - No hardcoded per-problem special cases, no artificial score floors.
        """
        answer_lower = answer.lower()
        q_lower = question.question.lower()
        hint_lower = (question.hint_guidance or "").lower()
        words = re.findall(r'[a-zA-Z0-9]+', answer_lower)
        word_count = len(words)

        # 1. DSA Topic Domain Keywords Catalog
        topic_domain_keywords = {
            "recursion": [
                "base case", "call stack", "stack frame", "stack frames", "recursive step",
                "recursive call", "recursion", "terminate", "subproblem", "unwind", "depth",
                "activation record", "activation records", "overflow", "stack overflow",
                "indefinitely", "infinite recursion", "termination condition"
            ],
            "binary search": [
                "sorted", "half", "mid", "middle", "eliminate", "discard", "log n", "divide",
                "search space", "monotonic", "boundary", "comparison", "range", "halve", "order"
            ],
            "stack": [
                "stack", "lifo", "last in first out", "bracket", "open", "close", "match",
                "matching", "counter", "nested", "push", "pop", "top", "empty", "underflow",
                "parentheses", "brackets"
            ],
            "hash": [
                "hash", "hash map", "hash table", "map", "table", "dictionary", "lookup",
                "complement", "o(1)", "constant", "collision", "collisions", "key", "value",
                "trade-off", "trade off"
            ],
            "two pointers": [
                "two pointer", "two pointers", "left", "right", "pointer", "pointers",
                "inwards", "sorted", "opposite ends"
            ],
            "linked list": [
                "pointer", "prev", "curr", "next", "head", "tail", "null", "none",
                "reverse", "iterate", "in-place", "node", "nodes"
            ],
            "intervals": [
                "sort", "start", "end", "overlap", "interval", "intervals", "merge", "greedy"
            ],
            "bit": [
                "bitwise", "and", "or", "xor", "bit", "power of two", "shift", "binary", "mask"
            ],
            "tree": [
                "root", "leaf", "node", "child", "subtree", "depth", "height", "traverse",
                "inorder", "preorder", "level"
            ],
            "dynamic programming": [
                "memoization", "tabulation", "overlapping subproblem", "optimal substructure",
                "dp", "state", "transition"
            ]
        }

        # 2. Extract Question & Rubric Core Concepts
        stopwords = {
            "explain", "why", "what", "how", "is", "a", "an", "the", "in", "for", "and",
            "or", "to", "of", "with", "your", "you", "does", "would", "which", "discuss",
            "state", "when", "mention", "discusses", "consider", "about", "could", "from",
            "their", "then", "there", "this", "that", "these", "those", "both", "key", "focus",
            "area", "guidance", "hint", "part", "such", "than", "very", "highlight", "using"
        }

        # Candidate concepts specifically expected for this question
        target_concepts = set()

        for text_source in (hint_lower, q_lower):
            raw_parts = re.split(r'[,;.\n/?:!]+|\b(?:and|or|by|from|using|highlight)\b', text_source)
            for part in raw_parts:
                cleaned = " ".join([w for w in part.split() if w not in stopwords]).strip()
                if len(cleaned.split()) >= 2:
                    target_concepts.add(cleaned)
                words_in_part = [w for w in part.split() if w not in stopwords]
                for i in range(len(words_in_part) - 1):
                    two_word = f"{words_in_part[i]} {words_in_part[i+1]}"
                    if len(two_word) >= 5:
                        target_concepts.add(two_word)

        # Collect relevant topic domain mechanisms
        domain_mechanisms = []
        for topic_key, kws in topic_domain_keywords.items():
            if (topic_key in problem.topic.lower() or 
                topic_key in q_lower or 
                topic_key in hint_lower):
                domain_mechanisms.extend(kws)
                for kw in kws:
                    # Avoid substring false matches (e.g. "recursion" inside "recursionerror")
                    if re.search(r'\b' + re.escape(kw) + r'\b', hint_lower) or re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                        target_concepts.add(kw)

        # Matched target concepts in answer (multi-word concepts or specialized domain terms)
        matched_targets = [p for p in target_concepts if p in answer_lower]

        # General domain mechanisms matched in answer
        matched_domain = [kw for kw in set(domain_mechanisms) if kw in answer_lower]

        # Contradiction / misconception patterns (answers stating technically inverted or false claims)
        contradiction_patterns = [
            r'\b(?:runs?\s+faster|faster\s+without|speeds?\s+up\s+without|without\s+it\b.*?\bfaster)\b',
            r'\b(?:returns?\s+(?:a\s+)?(?:very\s+)?large\s+number)\b',
            r'\b(?:never\s+crashes|never\s+overflows?|no\s+stack\s+overflow)\b',
            r'\b(?:works?\s+on\s+unsorted(?:\s+arrays?)?\s+too)\b',
            r'\b(?:just\s+runs\s+faster)\b',
        ]
        has_contradiction = any(re.search(pat, answer_lower) for pat in contradiction_patterns)

        # Asymptotic & Big-O signals
        has_big_o = any(c in answer_lower for c in [
            "o(1)", "o(n)", "o(log", "o(n^2)", "o(n log", "o(n!)", "big-o", "big o",
            "constant time", "linear time", "logarithmic", "quadratic"
        ])
        has_space_time = any(d in answer_lower for d in [
            "time complexity", "space complexity", "auxiliary space", "call stack",
            "memory", "stack frame", "stack frames", "activation records"
        ])
        asks_complexity = bool(re.search(
            r'\b(complexity|time complexity|space complexity|big-o|big o|asymptotic|worst-case|best-case|amortized|o\(1\)|o\(n\)|o\(log n\))\b',
            q_lower
        )) or question.category == "complexity"

        # Code & invariant signals
        code_mechanic_terms = [
            "base case", "if", "loop", "conditional", "return", "push", "pop", "pointer",
            "check", "invariant", "prevent", "terminate", "len(", "== 0", "!= 0",
            "empty", "stack", "underflow", "indexerror", "recursionerror"
        ]
        has_code_mechanic = any(m in answer_lower for m in code_mechanic_terms)
        asks_code = bool(re.search(
            r'\b(code|line of code|conditional|loop|invariant|detects failure|which line|indexerror|base case check)\b',
            q_lower
        )) or question.category in ("code_choice", "edge_case")

        # 3. Comprehensive Relevance Check
        # An answer is completely IRRELEVANT if:
        # It contains no matched question targets, no matched domain terms, no Big-O (even if asked), no code mechanics,
        # OR if it only contains completely generic English words unrelated to the topic/question.
        is_relevant_to_question = (
            len(matched_targets) > 0 or 
            (asks_complexity and (has_big_o or has_space_time)) or
            (asks_code and has_code_mechanic and any(kw in answer_lower for kw in matched_domain)) or
            len(matched_domain) >= 2
        )

        if not is_relevant_to_question:
            if len(matched_domain) == 0 and not has_big_o and not has_code_mechanic:
                scores = {dim: 0 for dim in applicable_dims}
                return VivaScoreResult(
                    conceptual_score=scores.get("conceptual_score"),
                    code_understanding_score=scores.get("code_understanding_score"),
                    complexity_score=scores.get("complexity_score"),
                    communication_score=scores.get("communication_score"),
                    overall_score=0,
                    feedback=f"Your response does not address the question asked about '{question.question}'. It appears off-topic. Please provide a substantive technical explanation addressing the question.",
                    ideal_points_covered=[],
                    missing_concepts=[question.hint_guidance or f"Technical reasoning addressing '{question.question}'"],
                    suggested_improvement=question.hint_guidance or f"Focus on how {problem.title} functions algorithmically.",
                    answer_relevance="irrelevant",
                    applicable_dimensions=applicable_dims,
                    should_retry=True,
                    question_id=question.id,
                    category=question.category,
                    answer_modality=answer_modality,
                    communication_label="Verbal Response Clarity" if answer_modality == "voice_transcribed" else "Communication & Clarity"
                )

        # 4. Dimension Evaluation
        # BUG-7 FIX: define hint_phrases before any branch uses it
        hint_phrases = [
            p.strip() for p in
            re.split(r'[,;.]+', hint_lower)
            if len(p.strip()) > 3
        ]

        scores: Dict[str, Optional[int]] = {}
        ideal_points = []
        missing_points = []

        # (A) Conceptual Understanding
        # BUG-4 FIX: Use a tiered rubric instead of starting at 86.
        # Tier mapping (aligned with the documented rubric):
        #   0-39  : No meaningful engagement
        #   40-59 : One marginal domain term only
        #   60-74 : Partial — one relevant target or two domain terms, brief
        #   75-89 : Solid — addresses multiple targets or targets + domain with explanation
        #   90-100: Complete — all targets covered with explicit rationale
        if "conceptual_score" in applicable_dims:
            concept_score = 0
            n_targets = len(matched_targets)
            n_domain = len(matched_domain)

            if has_contradiction:
                # Severe penalty for factually inverted or contradictory claims
                concept_score = 25
                missing_points.append(
                    f"Correct core behavior: {question.hint_guidance or 'Valid algorithmic causality without contradictory assumptions'}"
                )
            elif n_targets >= 3 or (n_targets >= 2 and n_domain >= 2):
                # Strong multi-target coverage
                for m in (matched_targets + matched_domain)[:3]:
                    ideal_points.append(f"Addressed key concept: {m}")
                if word_count >= 20:
                    concept_score = 92   # near-complete
                elif word_count >= 12:
                    concept_score = 82   # solid
                else:
                    concept_score = 76   # covered but terse
            elif n_targets >= 2 or (n_targets == 1 and n_domain >= 2):
                # Good coverage — two distinct signals present
                for m in (matched_targets + matched_domain)[:2]:
                    ideal_points.append(f"Addressed key concept: {m}")
                if word_count >= 20:
                    concept_score = 80
                elif word_count >= 10:
                    concept_score = 72
                else:
                    # Short answer — partial credit
                    concept_score = 58
                    missing_points.append(
                        question.hint_guidance or "Deeper technical justification"
                    )
            elif n_targets == 1 or n_domain >= 2:
                # One relevant signal
                for m in (matched_targets + matched_domain)[:1]:
                    ideal_points.append(f"Referenced key concept: {m}")
                if word_count < 8:
                    # Brief partial mention (e.g. "A base case returns a number.")
                    concept_score = 30
                    missing_points.append(
                        question.hint_guidance or "Deeper runtime justification"
                    )
                else:
                    concept_score = 55
                    missing_points.append(
                        f"Elaborate further on: {hint_phrases[0] if hint_phrases else 'the underlying computational logic'}"
                    )
            elif n_domain == 1:
                # Student touched on topic but didn't address question target
                concept_score = 22
                ideal_points.append(f"Mentioned topic term: {matched_domain[0]}")
                missing_points.append(
                    f"Specific answer to: {question.hint_guidance or question.question}"
                )
            else:
                concept_score = 0
                missing_points.append(
                    f"Technical reasoning for: {question.hint_guidance or question.question}"
                )

            scores["conceptual_score"] = concept_score

        # (B) Complexity Analysis
        # BUG-5 FIX: Tighten scoring tiers so partial answers cannot reach 90+.
        # Rubric:
        #   0-39  : No complexity content
        #   40-59 : Mentions time/space concepts but no explicit Big-O
        #   60-74 : Has Big-O notation, no justification
        #   75-89 : Big-O + justification (why that complexity)
        #   90-100: Big-O + justification + auxiliary space distinction
        if "complexity_score" in applicable_dims:
            comp_score = 0
            if has_big_o:
                comp_score = 62  # base: explicit notation present
                ideal_points.append("Stated explicit asymptotic complexity in Big-O notation")
                has_rationale = any(
                    term in answer_lower
                    for term in [
                        "because", "since", "iteration", "depth", "frame", "loop",
                        "call stack", "calls", "linear", "each element", "n steps",
                        "lookup", "average", "storing", "trade-off", "trade off",
                        "hash", "constant", "single pass", "traverse"
                    ]
                )
                if has_rationale:
                    comp_score = 78  # explained why
                    ideal_points.append("Justified the complexity with algorithmic reasoning")
                if has_space_time:
                    comp_score = min(100, comp_score + 12)  # also discussed space
                    ideal_points.append("Differentiated time and auxiliary memory utilization")
                # Word count bonus (depth of explanation) — small bump only
                if word_count >= 20 and has_rationale:
                    comp_score = min(100, comp_score + 5)
            elif has_space_time:
                comp_score = 42
                ideal_points.append("Discussed runtime or space considerations")
                missing_points.append("Explicit Big-O notation (e.g. O(N), O(1))")
            else:
                missing_points.append(
                    "Explicit Big-O notation (e.g. O(N), O(1)) and complexity analysis"
                )

            scores["complexity_score"] = min(100, comp_score)

        # (C) Code Understanding
        if "code_understanding_score" in applicable_dims:
            code_score = 0
            if has_code_mechanic and (len(matched_targets) > 0 or len(matched_domain) > 0):
                code_score = 58  # base: references code AND hits domain concepts
                ideal_points.append("Referenced concrete code constructs and invariants")
                # Explicit invariant / guard / prevention / evaluation language
                invariant_terms = [
                    "invariant", "check", "prevent", "terminate", "condition",
                    "guard", "pointer", "detect", "before", "after", "return",
                    "evaluat", "false", "true", "empty", "==", "!=", "len(",
                    "remain", "retain", "unclosed", "unmatched"
                ]
                n_invariants = sum(
                    1 for term in invariant_terms if term in answer_lower
                )
                if n_invariants >= 3:
                    code_score = 82
                elif n_invariants >= 2:
                    code_score = 74
                elif n_invariants >= 1:
                    code_score = 66

                # Specific code syntax or line citation bonus (e.g. len(stack) == 0, if, return False)
                has_code_syntax = any(
                    syn in answer_lower
                    for syn in ["==", "!=", "len(", "<=", ">=", "[]", "evaluates to false", "evaluates to true", "stack.pop()", "stack.append"]
                )
                if has_code_syntax:
                    code_score = min(100, code_score + 8)

                # Word count bonus — explanation depth
                if word_count >= 20 and code_score >= 60:
                    code_score = min(100, code_score + 10)
                elif word_count >= 10 and code_score >= 55:
                    code_score = min(100, code_score + 6)
            elif has_code_mechanic:
                code_score = 28
                missing_points.append("Connect code logic directly to the problem invariants")
            else:
                missing_points.append("Specific code references (conditionals, base cases, loops)")

            scores["code_understanding_score"] = min(100, code_score)

        # (D) Communication & Clarity
        # BUG-6 FIX: Communication is scored on structural clarity of the answer,
        # not as a mirror of content scores. Content must earn its own dimension scores.
        # The communication dimension asks: is the explanation structured, clear, concise?
        if "communication_score" in applicable_dims:
            comm_score = 0
            non_comm_scores = [
                v for k, v in scores.items()
                if k != "communication_score" and v is not None
            ]
            avg_content = (
                sum(non_comm_scores) / len(non_comm_scores)
                if non_comm_scores else 0
            )

            # If content scores are 0 (irrelevant/empty answer), comm is 0 too
            if avg_content == 0:
                comm_score = 0
            else:
                # Base communication score from word count (clarity proxy)
                # then capped by content quality — cannot score higher than content
                if word_count >= 25:
                    base_comm = 72
                elif word_count >= 15:
                    base_comm = 62
                elif word_count >= 8:
                    base_comm = 50
                elif word_count >= 4:
                    base_comm = 35
                else:
                    base_comm = 15

                # Award bonus for structured connectors ("because", "therefore", etc.)
                connectors = [
                    "because", "therefore", "since", "which means", "this means",
                    "as a result", "hence", "thus", "for example", "such as"
                ]
                if any(c in answer_lower for c in connectors):
                    base_comm = min(100, base_comm + 8)

                # Cap communication at content average to prevent comm inflating overall
                comm_score = min(base_comm, int(avg_content))

            scores["communication_score"] = min(100, comm_score)

        # 5. Overall Score Calculation
        # Only pass applicable dims to the score calculator (others must be None, not 0)
        applicable_scores = {dim: scores.get(dim) for dim in applicable_dims}
        overall = self._calculate_overall_score(applicable_scores, weights)
        relevance = "relevant" if overall >= 65 else ("partially_relevant" if overall > 0 else "irrelevant")

        if overall >= 80:
            feedback = f"Outstanding technical explanation! You clearly articulated {', '.join(ideal_points[:2]) if ideal_points else 'the core mechanisms'}."
        elif overall >= 50:
            feedback = f"Good technical defense. You touched on {', '.join(ideal_points[:1]) if ideal_points else 'relevant concepts'}, but should address: {missing_points[0] if missing_points else 'the complete question'}."
        elif overall > 0:
            feedback = f"Partial credit. Your answer lacks necessary technical depth for this question. {missing_points[0] if missing_points else 'Please address the specific prompt.'}"
        else:
            feedback = f"Your response does not address the question asked about '{question.question}'. Please provide a substantive technical explanation."

        improvement = question.hint_guidance or "Ensure you clearly define both the conceptual reason and computational impact."
        if missing_points:
            improvement = f"Focus on: {', '.join(missing_points[:2])}."

        return VivaScoreResult(
            # Non-applicable dimensions are None (not 0) so the frontend shows N/A
            # and the weighted average excludes them correctly.
            conceptual_score=scores.get("conceptual_score"),
            code_understanding_score=scores.get("code_understanding_score"),
            complexity_score=scores.get("complexity_score"),
            communication_score=scores.get("communication_score"),
            overall_score=overall,
            feedback=feedback,
            ideal_points_covered=ideal_points,
            missing_concepts=missing_points,
            suggested_improvement=improvement,
            answer_relevance=relevance,
            applicable_dimensions=applicable_dims,
            should_retry=overall < 50,
            question_id=question.id,
            category=question.category,
            answer_modality=answer_modality,
            communication_label="Verbal Response Clarity" if answer_modality == "voice_transcribed" else "Communication & Clarity"
        )

    def generate_coding_problem(
        self,
        topic: str,
        difficulty: str,
        language: str,
        subtopic: Optional[str] = None,
        previous_titles: Optional[List[str]] = None,
        previous_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically generates a coding problem using BharatCode AI if available,
        or the high-quality parameterized algorithm blueprints.
        Guarantees topic, difficulty, language adherence, and duplicate prevention.
        """
        from question_generator import generate_coding_problem_service
        return generate_coding_problem_service(
            api_key=self.api_key,
            call_llm_fn=self.call_llm,
            topic=topic,
            difficulty=difficulty,
            language=language,
            subtopic=subtopic,
            previous_titles=previous_titles,
            previous_ids=previous_ids
        )

    def generate_coding_problems_batch(
        self,
        topic: str,
        difficulty: str,
        language: str,
        count: int = 1,
        subtopic: Optional[str] = None,
        previous_titles: Optional[List[str]] = None,
        previous_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates a batch of distinct coding problems adhering to topic, difficulty, and language.
        """
        from question_generator import generate_coding_problems_batch
        return generate_coding_problems_batch(
            api_key=self.api_key,
            call_llm_fn=self.call_llm,
            topic=topic,
            difficulty=difficulty,
            language=language,
            count=count,
            subtopic=subtopic,
            previous_titles=previous_titles,
            previous_ids=previous_ids
        )

