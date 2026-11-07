# CodeAcharya Curated Expanded Problems Bank
from typing import Dict
from models import Problem, TestCase

EXPANDED_PROBLEMS: Dict[str, Problem] = {
    "sum-of-digits-recursion": Problem(
        id="sum-of-digits-recursion",
        title="Sum of Digits (Recursion)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Basic Recursion",
        description="""Given a non-negative integer `n`, return the sum of its digits recursively.

Do not convert `n` into a string.""",
        examples=[
            {
                        "input": "n = 123",
                        "output": "6"
            },
            {
                        "input": "n = 0",
                        "output": "0"
            }
],
        constraints=[
            "0 <= n <= 10^9"
],
        starter_code={
            "python": """def sum_of_digits(n: int) -> int:
    pass
""",
            "c": """int sumOfDigits(int n) {
    
}
""",
            "cpp": """int sumOfDigits(int n) {
    
}
""",
            "java": """public class Solution {
    public static int sumOfDigits(int n) {
        
    }
}
"""
        },
        expected_solution={
            "python": """def sum_of_digits(n: int) -> int:
    if n < 10: return n
    return (n % 10) + sum_of_digits(n // 10)
""",
            "c": """int sumOfDigits(int n) {
    if (n < 10) return n;
    return (n % 10) + sumOfDigits(n / 10);
}
""",
            "cpp": """int sumOfDigits(int n) {
    if (n < 10) return n;
    return (n % 10) + sumOfDigits(n / 10);
}
""",
            "java": """public class Solution {
    public static int sumOfDigits(int n) {
        if (n < 10) return n;
        return (n % 10) + sumOfDigits(n / 10);
    }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=123, expected_output=6, is_hidden=False),
            TestCase(id=2, input=0, expected_output=0, is_hidden=False),
            TestCase(id=3, input=999, expected_output=27, is_hidden=False),
            TestCase(id=4, input=10005, expected_output=6, is_hidden=True)
        ],
        learning_objectives=[
            "Decompose base-10 integer recursively"
],
        common_misconceptions=[
            "Using loops instead of recursion"
],
        hint="""Base case is n < 10.""",
        source="curated",
        is_generated=False
    ),
    "power-of-two-recursion": Problem(
        id="power-of-two-recursion",
        title="Power of Two Check (Recursion)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Divide & Conquer",
        description="""Given an integer `n`, return `True` if it is a power of two, otherwise return `False`. Implement recursively.""",
        examples=[
            {
                        "input": "n = 1",
                        "output": "True"
            },
            {
                        "input": "n = 16",
                        "output": "True"
            },
            {
                        "input": "n = 3",
                        "output": "False"
            }
],
        constraints=[
            "-2^31 <= n <= 2^31 - 1"
],
        starter_code={
            "python": """def is_power_of_two(n: int) -> bool:
    pass
""",
            "c": """int isPowerOfTwo(int n) {
    
}
""",
            "cpp": """bool isPowerOfTwo(int n) {
    
}
""",
            "java": """public class Solution {
    public static boolean isPowerOfTwo(int n) {
        
    }
}
"""
        },
        expected_solution={
            "python": """def is_power_of_two(n: int) -> bool:
    if n <= 0: return False
    if n == 1: return True
    if n % 2 != 0: return False
    return is_power_of_two(n // 2)
""",
            "c": """int isPowerOfTwo(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    if (n % 2 != 0) return 0;
    return isPowerOfTwo(n / 2);
}
""",
            "cpp": """bool isPowerOfTwo(int n) {
    if (n <= 0) return false;
    if (n == 1) return true;
    if (n % 2 != 0) return false;
    return isPowerOfTwo(n / 2);
}
""",
            "java": """public class Solution {
    public static boolean isPowerOfTwo(int n) {
        if (n <= 0) return false;
        if (n == 1) return true;
        if (n % 2 != 0) return false;
        return isPowerOfTwo(n / 2);
    }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=1, expected_output=True, is_hidden=False),
            TestCase(id=2, input=16, expected_output=True, is_hidden=False),
            TestCase(id=3, input=3, expected_output=False, is_hidden=False),
            TestCase(id=4, input=1024, expected_output=True, is_hidden=True)
        ],
        learning_objectives=[
            "Divide-and-conquer base-2 halving"
],
        common_misconceptions=[
            "Negative powers and 0"
],
        hint="""Base case n == 1.""",
        source="curated",
        is_generated=False
    ),
    "fibonacci-number-recursion": Problem(
        id="fibonacci-number-recursion",
        title="Fibonacci Number (Recursion)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Basic Recursion",
        description="""The Fibonacci numbers form a sequence starting with 0 and 1. Compute `F(n)`.""",
        examples=[
            {
                        "input": "n = 4",
                        "output": "3"
            }
],
        constraints=[
            "0 <= n <= 30"
],
        starter_code={
            "python": """def fib(n: int) -> int:
    pass
""",
            "c": """int fib(int n) {
    
}
""",
            "cpp": """int fib(int n) {
    
}
""",
            "java": """public class Solution {
    public static int fib(int n) {
        
    }
}
"""
        },
        expected_solution={
            "python": """def fib(n: int) -> int:
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(2, n + 1): a, b = b, a + b
    return b
""",
            "c": """int fib(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) { c = a + b; a = b; b = c; }
    return b;
}
""",
            "cpp": """int fib(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) { c = a + b; a = b; b = c; }
    return b;
}
""",
            "java": """public class Solution {
    public static int fib(int n) {
        if (n <= 1) return n;
        int a = 0, b = 1, c;
        for (int i = 2; i <= n; i++) { c = a + b; a = b; b = c; }
        return b;
    }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=0, expected_output=0, is_hidden=False),
            TestCase(id=2, input=1, expected_output=1, is_hidden=False),
            TestCase(id=3, input=4, expected_output=3, is_hidden=False),
            TestCase(id=4, input=10, expected_output=55, is_hidden=True)
        ],
        learning_objectives=[
            "Fibonacci recurrence relation"
],
        common_misconceptions=[
            "Stack overflow on deep recursion"
],
        hint="""F(0)=0, F(1)=1.""",
        source="curated",
        is_generated=False
    ),
    "count-digits-recursion": Problem(
        id="count-digits-recursion",
        title="Count Digits (Recursion)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Basic Recursion",
        description="""Given a non-negative integer `n`, return the total number of digits in `n` using recursion.""",
        examples=[
            {
                        "input": "n = 12345",
                        "output": "5"
            },
            {
                        "input": "n = 0",
                        "output": "1"
            }
],
        constraints=[
            "0 <= n <= 10^9"
],
        starter_code={
            "python": """def count_digits(n: int) -> int:
    pass
""",
            "c": """int countDigits(int n) {
    
}
""",
            "cpp": """int countDigits(int n) {
    
}
""",
            "java": """public class Solution {
    public static int countDigits(int n) {
        
    }
}
"""
        },
        expected_solution={
            "python": """def count_digits(n: int) -> int:
    if n < 10: return 1
    return 1 + count_digits(n // 10)
""",
            "c": """int countDigits(int n) {
    if (n < 10) return 1;
    return 1 + countDigits(n / 10);
}
""",
            "cpp": """int countDigits(int n) {
    if (n < 10) return 1;
    return 1 + countDigits(n / 10);
}
""",
            "java": """public class Solution {
    public static int countDigits(int n) {
        if (n < 10) return 1;
        return 1 + countDigits(n / 10);
    }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=12345, expected_output=5, is_hidden=False),
            TestCase(id=2, input=0, expected_output=1, is_hidden=False),
            TestCase(id=3, input=987654321, expected_output=9, is_hidden=True)
        ],
        learning_objectives=[
            "Count length via recursive floor division"
],
        common_misconceptions=[
            "Off-by-one errors"
],
        hint="""Single digit numbers have 1 digit.""",
        source="curated",
        is_generated=False
    ),
    "reverse-string-recursion": Problem(
        id="reverse-string-recursion",
        title="Reverse String (Recursion)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Basic Recursion",
        description="""Write a recursive function that returns the reverse of a string `s`.""",
        examples=[
            {
                        "input": "s = 'hello'",
                        "output": "'olleh'"
            }
],
        constraints=[
            "0 <= len(s) <= 1000"
],
        starter_code={
            "python": """def reverse_str(s: str) -> str:
    pass
""",
            "c": """char* reverseStr(char* s) { return s; }
""",
            "cpp": """string reverseStr(string s) { return s; }
""",
            "java": """public class Solution {
    public static String reverseStr(String s) { return s; }
}
"""
        },
        expected_solution={
            "python": """def reverse_str(s: str) -> str:
    if len(s) <= 1: return s
    return reverse_str(s[1:]) + s[0]
""",
            "c": """char* reverseStr(char* s) { return s; }
""",
            "cpp": """string reverseStr(string s) { if (s.length() <= 1) return s; return reverseStr(s.substr(1)) + s[0]; }
""",
            "java": """public class Solution {
    public static String reverseStr(String s) { if (s.length() <= 1) return s; return reverseStr(s.substring(1)) + s.charAt(0); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='hello', expected_output='olleh', is_hidden=False),
            TestCase(id=2, input='a', expected_output='a', is_hidden=False),
            TestCase(id=3, input='', expected_output='', is_hidden=False)
        ],
        learning_objectives=[
            "String slicing recursion"
],
        common_misconceptions=[
            "Base case of empty or 1 char string"
],
        hint="""Reverse s[1:] + s[0].""",
        source="curated",
        is_generated=False
    ),
    "power-x-n": Problem(
        id="power-x-n",
        title="Pow(x, n) (Divide & Conquer)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Divide & Conquer",
        description="""Calculate `x` raised to the power `n` in O(log n) time.""",
        examples=[
            {
                        "input": "x = 2.0, n = 10",
                        "output": "1024.0"
            }
],
        constraints=[
            "-100.0 < x < 100.0",
            "-2^31 <= n <= 2^31 - 1"
],
        starter_code={
            "python": """def my_pow(x: float, n: int) -> float:
    pass
""",
            "c": """double myPow(double x, int n) { return 0; }
""",
            "cpp": """double myPow(double x, int n) { return 0; }
""",
            "java": """public class Solution {
    public static double myPow(double x, int n) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def my_pow(x: float, n: int) -> float:
    if n == 0: return 1.0
    if n < 0: x, n = 1.0 / x, -n
    half = my_pow(x, n // 2)
    return round(half * half if n % 2 == 0 else half * half * x, 5)
""",
            "c": """double myPow(double x, int n) { return 0; }
""",
            "cpp": """double myPow(double x, int n) { return 0; }
""",
            "java": """public class Solution {
    public static double myPow(double x, int n) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'x': 2.0, 'n': 10}, expected_output=1024.0, is_hidden=False),
            TestCase(id=2, input={'x': 2.0, 'n': -2}, expected_output=0.25, is_hidden=False),
            TestCase(id=3, input={'x': 2.0, 'n': 0}, expected_output=1.0, is_hidden=False)
        ],
        learning_objectives=[
            "Binary exponentiation"
],
        common_misconceptions=[
            "O(n) linear loop timeouts"
],
        hint="""Calculate half = pow(x, n // 2).""",
        source="curated",
        is_generated=False
    ),
    "permutations": Problem(
        id="permutations",
        title="Permutations (Backtracking)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Given an array `nums` of distinct integers, return all possible permutations.""",
        examples=[
            {
                        "input": "nums = [1, 2, 3]",
                        "output": "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]"
            }
],
        constraints=[
            "1 <= nums.length <= 6"
],
        starter_code={
            "python": """def permute(nums: list) -> list:
    pass
""",
            "c": """void permute() {}
""",
            "cpp": """vector<vector<int>> permute(vector<int>& nums) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> permute(int[] nums) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def permute(nums: list) -> list:
    res = []
    def bt(curr, used):
        if len(curr) == len(nums): res.append(list(curr)); return
        for x in nums:
            if x not in used:
                used.add(x); curr.append(x); bt(curr, used); curr.pop(); used.remove(x)
    bt([], set())
    return sorted(res)
""",
            "c": """void permute() {}
""",
            "cpp": """vector<vector<int>> permute(vector<int>& nums) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> permute(int[] nums) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[1], expected_output=[[1]], is_hidden=False),
            TestCase(id=2, input=[1, 2], expected_output=[[1, 2], [2, 1]], is_hidden=False)
        ],
        learning_objectives=[
            "N! permutation state tree"
],
        common_misconceptions=[
            "Missing backtrack pop"
],
        hint="""Maintain visited set.""",
        source="curated",
        is_generated=False
    ),
    "combination-sum": Problem(
        id="combination-sum",
        title="Combination Sum (Backtracking)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Find all unique combinations in `candidates` where candidate numbers sum to `target`.""",
        examples=[
            {
                        "input": "candidates = [2, 3, 6, 7], target = 7",
                        "output": "[[2, 2, 3], [7]]"
            }
],
        constraints=[
            "1 <= candidates.length <= 30"
],
        starter_code={
            "python": """def combination_sum(candidates: list, target: int) -> list:
    pass
""",
            "c": """void combinationSum() {}
""",
            "cpp": """vector<vector<int>> combinationSum(vector<int>& c, int t) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> combinationSum(int[] c, int t) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def combination_sum(candidates: list, target: int) -> list:
    res = []
    candidates.sort()
    def bt(rem, start, path):
        if rem == 0: res.append(list(path)); return
        for i in range(start, len(candidates)):
            if candidates[i] > rem: break
            path.append(candidates[i]); bt(rem - candidates[i], i, path); path.pop()
    bt(target, 0, [])
    return res
""",
            "c": """void combinationSum() {}
""",
            "cpp": """vector<vector<int>> combinationSum(vector<int>& c, int t) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> combinationSum(int[] c, int t) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'candidates': [2, 3, 6, 7], 'target': 7}, expected_output=[[2, 2, 3], [7]], is_hidden=False),
            TestCase(id=2, input={'candidates': [2], 'target': 1}, expected_output=[], is_hidden=False)
        ],
        learning_objectives=[
            "Branch pruning with sorted candidates"
],
        common_misconceptions=[
            "Duplicates in combinations"
],
        hint="""Pass index i to reuse current element.""",
        source="curated",
        is_generated=False
    ),
    "combinations-n-k": Problem(
        id="combinations-n-k",
        title="Combinations (n choose k)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Given two integers `n` and `k`, return all possible combinations of `k` numbers chosen from the range `[1, n]`.""",
        examples=[
            {
                        "input": "n = 4, k = 2",
                        "output": "[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]"
            }
],
        constraints=[
            "1 <= n <= 20",
            "1 <= k <= n"
],
        starter_code={
            "python": """def combine(n: int, k: int) -> list:
    pass
""",
            "c": """void combine() {}
""",
            "cpp": """vector<vector<int>> combine(int n, int k) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> combine(int n, int k) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def combine(n: int, k: int) -> list:
    res = []
    def bt(start, path):
        if len(path) == k: res.append(list(path)); return
        for i in range(start, n + 1):
            path.append(i); bt(i + 1, path); path.pop()
    bt(1, [])
    return res
""",
            "c": """void combine() {}
""",
            "cpp": """vector<vector<int>> combine(int n, int k) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> combine(int n, int k) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'n': 4, 'k': 2}, expected_output=[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]], is_hidden=False),
            TestCase(id=2, input={'n': 1, 'k': 1}, expected_output=[[1]], is_hidden=False)
        ],
        learning_objectives=[
            "n choose k subsets generation"
],
        common_misconceptions=[
            "Permutation vs combination order"
],
        hint="""Only pick forward numbers (start + 1).""",
        source="curated",
        is_generated=False
    ),
    "letter-combinations-phone": Problem(
        id="letter-combinations-phone",
        title="Letter Combinations of a Phone Number",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Given a digit string 2-9, return all possible letter combinations on a phone keypad.""",
        examples=[
            {
                        "input": "digits = '23'",
                        "output": "['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']"
            }
],
        constraints=[
            "0 <= digits.length <= 4"
],
        starter_code={
            "python": """def letter_combinations(digits: str) -> list:
    pass
""",
            "c": """void letterCombinations() {}
""",
            "cpp": """vector<string> letterCombinations(string digits) { return {}; }
""",
            "java": """public class Solution {
    public static List<String> letterCombinations(String d) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def letter_combinations(digits: str) -> list:
    if not digits: return []
    m = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}
    res = []
    def bt(idx, path):
        if idx == len(digits): res.append(''.join(path)); return
        for ch in m[digits[idx]]:
            path.append(ch); bt(idx + 1, path); path.pop()
    bt(0, [])
    return sorted(res)
""",
            "c": """void letterCombinations() {}
""",
            "cpp": """vector<string> letterCombinations(string digits) { return {}; }
""",
            "java": """public class Solution {
    public static List<String> letterCombinations(String d) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='2', expected_output=['a', 'b', 'c'], is_hidden=False),
            TestCase(id=2, input='', expected_output=[], is_hidden=False),
            TestCase(id=3, input='23', expected_output=['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf'], is_hidden=True)
        ],
        learning_objectives=[
            "Cartesian mapping backtracking"
],
        common_misconceptions=[
            "Digit out of bounds"
],
        hint="""Map each digit and recurse idx + 1.""",
        source="curated",
        is_generated=False
    ),
    "word-search": Problem(
        id="word-search",
        title="Word Search (Backtracking)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Given an `m x n` grid of characters and a string `word`, return `True` if `word` exists in the grid.""",
        examples=[
            {
                        "input": "board = [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']], word = 'ABCCED'",
                        "output": "True"
            }
],
        constraints=[
            "1 <= m, n <= 6"
],
        starter_code={
            "python": """def exist(board: list, word: str) -> bool:
    pass
""",
            "c": """int exist() { return 0; }
""",
            "cpp": """bool exist() { return false; }
""",
            "java": """public class Solution {
    public static boolean exist() { return false; }
}
"""
        },
        expected_solution={
            "python": """def exist(board: list, word: str) -> bool:
    R, C = len(board), len(board[0])
    def dfs(r, c, idx):
        if idx == len(word): return True
        if r < 0 or r >= R or c < 0 or c >= C or board[r][c] != word[idx]: return False
        temp = board[r][c]; board[r][c] = '#'
        found = dfs(r+1,c,idx+1) or dfs(r-1,c,idx+1) or dfs(r,c+1,idx+1) or dfs(r,c-1,idx+1)
        board[r][c] = temp
        return found
    for r in range(R):
        for c in range(C):
            if dfs(r, c, 0): return True
    return False
""",
            "c": """int exist() { return 0; }
""",
            "cpp": """bool exist() { return false; }
""",
            "java": """public class Solution {
    public static boolean exist() { return false; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'board': [['A', 'B'], ['C', 'D']], 'word': 'ABDC'}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'board': [['A', 'B'], ['C', 'D']], 'word': 'ABCD'}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "2D grid DFS backtracking"
],
        common_misconceptions=[
            "Not resetting visited cells"
],
        hint="""Temporarily mark board[r][c]='#' and restore.""",
        source="curated",
        is_generated=False
    ),
    "tower-of-hanoi": Problem(
        id="tower-of-hanoi",
        title="Tower of Hanoi (Recursion)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Basic Recursion",
        description="""Return the minimum number of moves required to solve Tower of Hanoi with `n` disks.""",
        examples=[
            {
                        "input": "n = 3",
                        "output": "7"
            }
],
        constraints=[
            "1 <= n <= 30"
],
        starter_code={
            "python": """def tower_of_hanoi_moves(n: int) -> int:
    pass
""",
            "c": """int towerOfHanoiMoves(int n) { if (n == 1) return 1; return 2 * towerOfHanoiMoves(n-1) + 1; }
""",
            "cpp": """int towerOfHanoiMoves(int n) { if (n == 1) return 1; return 2 * towerOfHanoiMoves(n-1) + 1; }
""",
            "java": """public class Solution {
    public static int towerOfHanoiMoves(int n) { if (n == 1) return 1; return 2 * towerOfHanoiMoves(n-1) + 1; }
}
"""
        },
        expected_solution={
            "python": """def tower_of_hanoi_moves(n: int) -> int:
    if n == 1: return 1
    return 2 * tower_of_hanoi_moves(n - 1) + 1
""",
            "c": """int towerOfHanoiMoves(int n) { if (n == 1) return 1; return 2 * towerOfHanoiMoves(n-1) + 1; }
""",
            "cpp": """int towerOfHanoiMoves(int n) { if (n == 1) return 1; return 2 * towerOfHanoiMoves(n-1) + 1; }
""",
            "java": """public class Solution {
    public static int towerOfHanoiMoves(int n) { if (n == 1) return 1; return 2 * towerOfHanoiMoves(n-1) + 1; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=1, expected_output=1, is_hidden=False),
            TestCase(id=2, input=3, expected_output=7, is_hidden=False),
            TestCase(id=3, input=4, expected_output=15, is_hidden=False),
            TestCase(id=4, input=10, expected_output=1023, is_hidden=True)
        ],
        learning_objectives=[
            "Recurrence 2*T(n-1) + 1"
],
        common_misconceptions=[
            "Linear moves scaling"
],
        hint="""Moves = 2^n - 1.""",
        source="curated",
        is_generated=False
    ),
    "palindrome-partitioning": Problem(
        id="palindrome-partitioning",
        title="Palindrome Partitioning",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Partition string `s` such that every substring is a palindrome. Return all partitions.""",
        examples=[
            {
                        "input": "s = 'aab'",
                        "output": "[['a', 'a', 'b'], ['aa', 'b']]"
            }
],
        constraints=[
            "1 <= s.length <= 16"
],
        starter_code={
            "python": """def partition(s: str) -> list:
    pass
""",
            "c": """void partition() {}
""",
            "cpp": """vector<vector<string>> partition(string s) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<String>> partition(String s) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def partition(s: str) -> list:
    res = []
    def is_pal(sub): return sub == sub[::-1]
    def bt(start, path):
        if start == len(s): res.append(list(path)); return
        for end in range(start + 1, len(s) + 1):
            sub = s[start:end]
            if is_pal(sub): path.append(sub); bt(end, path); path.pop()
    bt(0, [])
    return res
""",
            "c": """void partition() {}
""",
            "cpp": """vector<vector<string>> partition(string s) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<String>> partition(String s) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='a', expected_output=[['a']], is_hidden=False),
            TestCase(id=2, input='aab', expected_output=[['a', 'a', 'b'], ['aa', 'b']], is_hidden=False)
        ],
        learning_objectives=[
            "Palindrome prefix backtracking"
],
        common_misconceptions=[
            "Non-contiguous cuts"
],
        hint="""Check prefix palindrome then recurse on remainder.""",
        source="curated",
        is_generated=False
    ),
    "kth-symbol-in-grammar": Problem(
        id="kth-symbol-in-grammar",
        title="K-th Symbol in Grammar",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Tree Recursion",
        description="""Row 1 is 0. Each 0 becomes 01 and 1 becomes 10. Find the k-th indexed symbol in row n.""",
        examples=[
            {
                        "input": "n = 2, k = 1",
                        "output": "0"
            },
            {
                        "input": "n = 2, k = 2",
                        "output": "1"
            }
],
        constraints=[
            "1 <= n <= 30",
            "1 <= k <= 2^(n - 1)"
],
        starter_code={
            "python": """def kth_grammar(n: int, k: int) -> int:
    pass
""",
            "c": """int kthGrammar(int n, int k) { if (n == 1) return 0; int p = kthGrammar(n-1, (k+1)/2); return (k%2 != 0) ? p : (1 - p); }
""",
            "cpp": """int kthGrammar(int n, int k) { if (n == 1) return 0; int p = kthGrammar(n-1, (k+1)/2); return (k%2 != 0) ? p : (1 - p); }
""",
            "java": """public class Solution {
    public static int kthGrammar(int n, int k) { if (n == 1) return 0; int p = kthGrammar(n-1, (k+1)/2); return (k%2 != 0) ? p : (1 - p); }
}
"""
        },
        expected_solution={
            "python": """def kth_grammar(n: int, k: int) -> int:
    if n == 1: return 0
    parent = kth_grammar(n - 1, (k + 1) // 2)
    return parent if k % 2 != 0 else (1 - parent)
""",
            "c": """int kthGrammar(int n, int k) { if (n == 1) return 0; int p = kthGrammar(n-1, (k+1)/2); return (k%2 != 0) ? p : (1 - p); }
""",
            "cpp": """int kthGrammar(int n, int k) { if (n == 1) return 0; int p = kthGrammar(n-1, (k+1)/2); return (k%2 != 0) ? p : (1 - p); }
""",
            "java": """public class Solution {
    public static int kthGrammar(int n, int k) { if (n == 1) return 0; int p = kthGrammar(n-1, (k+1)/2); return (k%2 != 0) ? p : (1 - p); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'n': 1, 'k': 1}, expected_output=0, is_hidden=False),
            TestCase(id=2, input={'n': 2, 'k': 1}, expected_output=0, is_hidden=False),
            TestCase(id=3, input={'n': 2, 'k': 2}, expected_output=1, is_hidden=False)
        ],
        learning_objectives=[
            "Binary tree traversal parent relation"
],
        common_misconceptions=[
            "Building full 2^n string in memory"
],
        hint="""Parent is at index (k + 1) // 2 in row n - 1.""",
        source="curated",
        is_generated=False
    ),
    "sudoku-solver": Problem(
        id="sudoku-solver",
        title="Sudoku Solver Validity Check",
        difficulty="Hard",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="""Validate whether a proposed digit placement is valid in a 9x9 Sudoku grid according to row, column, and 3x3 box rules.""",
        examples=[
            {
                        "input": "r = 0, c = 0, val = 5",
                        "output": "True"
            }
],
        constraints=[
            "Grid values 1-9"
],
        starter_code={
            "python": """def is_valid_sudoku_move(board: list, r: int, c: int, val: int) -> bool:
    pass
""",
            "c": """int isValidSudokuMove() { return 1; }
""",
            "cpp": """bool isValidSudokuMove() { return true; }
""",
            "java": """public class Solution {
    public static boolean isValidSudokuMove() { return true; }
}
"""
        },
        expected_solution={
            "python": """def is_valid_sudoku_move(board: list, r: int, c: int, val: int) -> bool:
    for i in range(9):
        if board[r][i] == val or board[i][c] == val: return False
        box_r, box_c = 3 * (r // 3) + i // 3, 3 * (c // 3) + i % 3
        if board[box_r][box_c] == val: return False
    return True
""",
            "c": """int isValidSudokuMove() { return 1; }
""",
            "cpp": """bool isValidSudokuMove() { return true; }
""",
            "java": """public class Solution {
    public static boolean isValidSudokuMove() { return true; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'board': [[0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0]], 'r': 0, 'c': 0, 'val': 5}, expected_output=True, is_hidden=False)
        ],
        learning_objectives=[
            "Row, column, and 3x3 block check"
],
        common_misconceptions=[
            "Overlooking 3x3 box coordinates"
],
        hint="""Check row, column, and 3*(r//3) + 3*(c//3).""",
        source="curated",
        is_generated=False
    ),
    "majority-element": Problem(
        id="majority-element",
        title="Majority Element (Boyer-Moore)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Frequency Counting",
        description="""Given an array `nums` of size `n`, return the majority element (> n/2 times).""",
        examples=[
            {
                        "input": "nums = [3, 2, 3]",
                        "output": "3"
            }
],
        constraints=[
            "1 <= nums.length <= 5 * 10^4"
],
        starter_code={
            "python": """def majority_element(nums: list) -> int:
    pass
""",
            "c": """int majorityElement(int* nums, int n) { int c = 0, cand = 0; for(int i=0;i<n;i++){ if(c==0) cand=nums[i]; c += (nums[i]==cand?1:-1); } return cand; }
""",
            "cpp": """int majorityElement(vector<int>& nums) { int c = 0, cand = 0; for(int x:nums){ if(c==0) cand=x; c += (x==cand?1:-1); } return cand; }
""",
            "java": """public class Solution {
    public static int majorityElement(int[] nums) { int c = 0, cand = 0; for(int x:nums){ if(c==0) cand=x; c += (x==cand?1:-1); } return cand; }
}
"""
        },
        expected_solution={
            "python": """def majority_element(nums: list) -> int:
    count, cand = 0, None
    for x in nums:
        if count == 0: cand = x
        count += (1 if x == cand else -1)
    return cand
""",
            "c": """int majorityElement(int* nums, int n) { int c = 0, cand = 0; for(int i=0;i<n;i++){ if(c==0) cand=nums[i]; c += (nums[i]==cand?1:-1); } return cand; }
""",
            "cpp": """int majorityElement(vector<int>& nums) { int c = 0, cand = 0; for(int x:nums){ if(c==0) cand=x; c += (x==cand?1:-1); } return cand; }
""",
            "java": """public class Solution {
    public static int majorityElement(int[] nums) { int c = 0, cand = 0; for(int x:nums){ if(c==0) cand=x; c += (x==cand?1:-1); } return cand; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[3, 2, 3], expected_output=3, is_hidden=False),
            TestCase(id=2, input=[2, 2, 1, 1, 1, 2, 2], expected_output=2, is_hidden=False)
        ],
        learning_objectives=[
            "Boyer-Moore O(1) space"
],
        common_misconceptions=[
            "Sorting in O(N log N)"
],
        hint="""Maintain candidate and count.""",
        source="curated",
        is_generated=False
    ),
    "missing-number": Problem(
        id="missing-number",
        title="Missing Number",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="""Given `nums` containing `n` distinct numbers in `[0, n]`, return the missing number.""",
        examples=[
            {
                        "input": "nums = [3, 0, 1]",
                        "output": "2"
            }
],
        constraints=[
            "n == nums.length"
],
        starter_code={
            "python": """def missing_number(nums: list) -> int:
    pass
""",
            "c": """int missingNumber(int* nums, int n) { int exp = n*(n+1)/2, s=0; for(int i=0;i<n;i++) s+=nums[i]; return exp - s; }
""",
            "cpp": """int missingNumber(vector<int>& nums) { int n = nums.size(), exp = n*(n+1)/2, s=0; for(int x:nums) s+=x; return exp - s; }
""",
            "java": """public class Solution {
    public static int missingNumber(int[] nums) { int n = nums.length, exp = n*(n+1)/2, s=0; for(int x:nums) s+=x; return exp - s; }
}
"""
        },
        expected_solution={
            "python": """def missing_number(nums: list) -> int:
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)
""",
            "c": """int missingNumber(int* nums, int n) { int exp = n*(n+1)/2, s=0; for(int i=0;i<n;i++) s+=nums[i]; return exp - s; }
""",
            "cpp": """int missingNumber(vector<int>& nums) { int n = nums.size(), exp = n*(n+1)/2, s=0; for(int x:nums) s+=x; return exp - s; }
""",
            "java": """public class Solution {
    public static int missingNumber(int[] nums) { int n = nums.length, exp = n*(n+1)/2, s=0; for(int x:nums) s+=x; return exp - s; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[3, 0, 1], expected_output=2, is_hidden=False),
            TestCase(id=2, input=[0, 1], expected_output=2, is_hidden=False),
            TestCase(id=3, input=[9, 6, 4, 2, 3, 5, 7, 0, 1], expected_output=8, is_hidden=False)
        ],
        learning_objectives=[
            "Gauss summation formula"
],
        common_misconceptions=[
            "O(N) space hash set"
],
        hint="""Expected sum is n*(n+1)//2.""",
        source="curated",
        is_generated=False
    ),
    "move-zeroes": Problem(
        id="move-zeroes",
        title="Move Zeroes (In-Place)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="""Move all 0's to the end of array maintaining relative order of non-zero elements.""",
        examples=[
            {
                        "input": "nums = [0, 1, 0, 3, 12]",
                        "output": "[1, 3, 12, 0, 0]"
            }
],
        constraints=[
            "1 <= nums.length <= 10^4"
],
        starter_code={
            "python": """def move_zeroes(nums: list) -> list:
    pass
""",
            "c": """void moveZeroes(int* nums, int n) { int pos = 0; for(int i=0;i<n;i++) if(nums[i]!=0) nums[pos++]=nums[i]; while(pos<n) nums[pos++]=0; }
""",
            "cpp": """vector<int> moveZeroes(vector<int>& nums) { int pos = 0; for(int x:nums) if(x!=0) nums[pos++]=x; while(pos<(int)nums.size()) nums[pos++]=0; return nums; }
""",
            "java": """public class Solution {
    public static int[] moveZeroes(int[] nums) { int pos = 0; for(int x:nums) if(x!=0) nums[pos++]=x; while(pos<nums.length) nums[pos++]=0; return nums; }
}
"""
        },
        expected_solution={
            "python": """def move_zeroes(nums: list) -> list:
    pos = 0
    for x in nums:
        if x != 0: nums[pos] = x; pos += 1
    while pos < len(nums): nums[pos] = 0; pos += 1
    return nums
""",
            "c": """void moveZeroes(int* nums, int n) { int pos = 0; for(int i=0;i<n;i++) if(nums[i]!=0) nums[pos++]=nums[i]; while(pos<n) nums[pos++]=0; }
""",
            "cpp": """vector<int> moveZeroes(vector<int>& nums) { int pos = 0; for(int x:nums) if(x!=0) nums[pos++]=x; while(pos<(int)nums.size()) nums[pos++]=0; return nums; }
""",
            "java": """public class Solution {
    public static int[] moveZeroes(int[] nums) { int pos = 0; for(int x:nums) if(x!=0) nums[pos++]=x; while(pos<nums.length) nums[pos++]=0; return nums; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[0, 1, 0, 3, 12], expected_output=[1, 3, 12, 0, 0], is_hidden=False),
            TestCase(id=2, input=[0], expected_output=[0], is_hidden=False)
        ],
        learning_objectives=[
            "Two pointer overwrite in O(1) space"
],
        common_misconceptions=[
            "Extra array allocation"
],
        hint="""Write non-zeros forward then pad zeroes.""",
        source="curated",
        is_generated=False
    ),
    "running-sum-1d-array": Problem(
        id="running-sum-1d-array",
        title="Running Sum of 1d Array",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Prefix Sums",
        description="""Return running sum array where `runningSum[i] = sum(nums[0]...nums[i])`.""",
        examples=[
            {
                        "input": "nums = [1, 2, 3, 4]",
                        "output": "[1, 3, 6, 10]"
            }
],
        constraints=[
            "1 <= nums.length <= 1000"
],
        starter_code={
            "python": """def running_sum(nums: list) -> list:
    pass
""",
            "c": """void runningSum() {}
""",
            "cpp": """vector<int> runningSum(vector<int>& nums) { vector<int> res; int c = 0; for(int x:nums){ c+=x; res.push_back(c); } return res; }
""",
            "java": """public class Solution {
    public static int[] runningSum(int[] nums) { int[] res = new int[nums.length]; int c = 0; for(int i=0;i<nums.length;i++){ c+=nums[i]; res[i]=c; } return res; }
}
"""
        },
        expected_solution={
            "python": """def running_sum(nums: list) -> list:
    res, curr = [], 0
    for x in nums: curr += x; res.append(curr)
    return res
""",
            "c": """void runningSum() {}
""",
            "cpp": """vector<int> runningSum(vector<int>& nums) { vector<int> res; int c = 0; for(int x:nums){ c+=x; res.push_back(c); } return res; }
""",
            "java": """public class Solution {
    public static int[] runningSum(int[] nums) { int[] res = new int[nums.length]; int c = 0; for(int i=0;i<nums.length;i++){ c+=nums[i]; res[i]=c; } return res; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 3, 4], expected_output=[1, 3, 6, 10], is_hidden=False),
            TestCase(id=2, input=[1, 1, 1, 1], expected_output=[1, 2, 3, 4], is_hidden=False)
        ],
        learning_objectives=[
            "Cumulative sum accumulation"
],
        common_misconceptions=[
            "Nested loop sum recalculation"
],
        hint="""Accumulate sum element by element.""",
        source="curated",
        is_generated=False
    ),
    "intersection-two-arrays": Problem(
        id="intersection-two-arrays",
        title="Intersection of Two Arrays",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Hash Maps & Sets",
        description="""Given two integer arrays `nums1` and `nums2`, return an array of their unique intersection.""",
        examples=[
            {
                        "input": "nums1 = [1, 2, 2, 1], nums2 = [2, 2]",
                        "output": "[2]"
            }
],
        constraints=[
            "1 <= nums1.length, nums2.length <= 1000"
],
        starter_code={
            "python": """def intersection(nums1: list, nums2: list) -> list:
    pass
""",
            "c": """void intersection() {}
""",
            "cpp": """vector<int> intersection(vector<int>& a, vector<int>& b) { return {}; }
""",
            "java": """public class Solution {
    public static int[] intersection(int[] a, int[] b) { return new int[0]; }
}
"""
        },
        expected_solution={
            "python": """def intersection(nums1: list, nums2: list) -> list:
    return sorted(list(set(nums1) & set(nums2)))
""",
            "c": """void intersection() {}
""",
            "cpp": """vector<int> intersection(vector<int>& a, vector<int>& b) { return {}; }
""",
            "java": """public class Solution {
    public static int[] intersection(int[] a, int[] b) { return new int[0]; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'nums1': [1, 2, 2, 1], 'nums2': [2, 2]}, expected_output=[2], is_hidden=False),
            TestCase(id=2, input={'nums1': [4, 9, 5], 'nums2': [9, 4, 9, 8, 4]}, expected_output=[4, 9], is_hidden=False)
        ],
        learning_objectives=[
            "Set intersection in O(N + M)"
],
        common_misconceptions=[
            "Duplicates in result array"
],
        hint="""Use hash set intersection.""",
        source="curated",
        is_generated=False
    ),
    "group-anagrams": Problem(
        id="group-anagrams",
        title="Group Anagrams (Hash Map)",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Hash Maps & Sets",
        description="""Given an array of strings `strs`, group the anagrams together.""",
        examples=[
            {
                        "input": "strs = ['eat','tea','tan','ate','nat','bat']",
                        "output": "[['ate','eat','tea'],['bat'],['nat','tan']]"
            }
],
        constraints=[
            "1 <= strs.length <= 10^4"
],
        starter_code={
            "python": """def group_anagrams(strs: list) -> list:
    pass
""",
            "c": """void groupAnagrams() {}
""",
            "cpp": """vector<vector<string>> groupAnagrams(vector<string>& strs) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<String>> groupAnagrams(String[] s) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def group_anagrams(strs: list) -> list:
    from collections import defaultdict
    groups = defaultdict(list)
    for s in strs: groups[''.join(sorted(s))].append(s)
    return sorted([sorted(g) for g in groups.values()])
""",
            "c": """void groupAnagrams() {}
""",
            "cpp": """vector<vector<string>> groupAnagrams(vector<string>& strs) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<String>> groupAnagrams(String[] s) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=['eat', 'tea', 'tan', 'ate', 'nat', 'bat'], expected_output=[['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']], is_hidden=False)
        ],
        learning_objectives=[
            "Canonical sorted string key in hash map"
],
        common_misconceptions=[
            "Pairwise string checks"
],
        hint="""Sort characters of each word as hash key.""",
        source="curated",
        is_generated=False
    ),
    "top-k-frequent-elements": Problem(
        id="top-k-frequent-elements",
        title="Top K Frequent Elements",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Frequency Counting",
        description="""Given an integer array `nums` and an integer `k`, return the `k` most frequent elements.""",
        examples=[
            {
                        "input": "nums = [1,1,1,2,2,3], k = 2",
                        "output": "[1, 2]"
            }
],
        constraints=[
            "1 <= nums.length <= 10^5"
],
        starter_code={
            "python": """def top_k_frequent(nums: list, k: int) -> list:
    pass
""",
            "c": """void topKFrequent() {}
""",
            "cpp": """vector<int> topKFrequent(vector<int>& nums, int k) { return {}; }
""",
            "java": """public class Solution {
    public static int[] topKFrequent(int[] nums, int k) { return new int[0]; }
}
"""
        },
        expected_solution={
            "python": """def top_k_frequent(nums: list, k: int) -> list:
    from collections import Counter
    return [x[0] for x in Counter(nums).most_common(k)]
""",
            "c": """void topKFrequent() {}
""",
            "cpp": """vector<int> topKFrequent(vector<int>& nums, int k) { return {}; }
""",
            "java": """public class Solution {
    public static int[] topKFrequent(int[] nums, int k) { return new int[0]; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'nums': [1, 1, 1, 2, 2, 3], 'k': 2}, expected_output=[1, 2], is_hidden=False),
            TestCase(id=2, input={'nums': [1], 'k': 1}, expected_output=[1], is_hidden=False)
        ],
        learning_objectives=[
            "Hash map frequency table + bucket selection"
],
        common_misconceptions=[
            "Full sorting array"
],
        hint="""Count elements and pick top k.""",
        source="curated",
        is_generated=False
    ),
    "longest-consecutive-sequence": Problem(
        id="longest-consecutive-sequence",
        title="Longest Consecutive Sequence",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Hash Maps & Sets",
        description="""Find length of longest consecutive elements sequence in O(n) time.""",
        examples=[
            {
                        "input": "nums = [100, 4, 200, 1, 3, 2]",
                        "output": "4"
            }
],
        constraints=[
            "0 <= nums.length <= 10^5"
],
        starter_code={
            "python": """def longest_consecutive(nums: list) -> int:
    pass
""",
            "c": """int longestConsecutive() { return 0; }
""",
            "cpp": """int longestConsecutive(vector<int>& nums) { return 0; }
""",
            "java": """public class Solution {
    public static int longestConsecutive(int[] nums) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def longest_consecutive(nums: list) -> int:
    num_set = set(nums)
    best = 0
    for n in num_set:
        if (n - 1) not in num_set:
            cur = 1
            while (n + cur) in num_set: cur += 1
            best = max(best, cur)
    return best
""",
            "c": """int longestConsecutive() { return 0; }
""",
            "cpp": """int longestConsecutive(vector<int>& nums) { return 0; }
""",
            "java": """public class Solution {
    public static int longestConsecutive(int[] nums) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[100, 4, 200, 1, 3, 2], expected_output=4, is_hidden=False),
            TestCase(id=2, input=[0, 3, 7, 2, 5, 8, 4, 6, 0, 1], expected_output=9, is_hidden=False)
        ],
        learning_objectives=[
            "Sequence start detection using set check (n - 1)"
],
        common_misconceptions=[
            "Counting every number as sequence root"
],
        hint="""Only count if n - 1 not in set.""",
        source="curated",
        is_generated=False
    ),
    "subarray-sum-equals-k": Problem(
        id="subarray-sum-equals-k",
        title="Subarray Sum Equals K",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Prefix Sums",
        description="""Return the total number of subarrays whose sum equals `k`.""",
        examples=[
            {
                        "input": "nums = [1, 1, 1], k = 2",
                        "output": "2"
            }
],
        constraints=[
            "1 <= nums.length <= 2 * 10^4"
],
        starter_code={
            "python": """def subarray_sum(nums: list, k: int) -> int:
    pass
""",
            "c": """int subarraySum() { return 0; }
""",
            "cpp": """int subarraySum(vector<int>& nums, int k) { return 0; }
""",
            "java": """public class Solution {
    public static int subarraySum(int[] nums, int k) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def subarray_sum(nums: list, k: int) -> int:
    count, curr = 0, 0
    pref = {0: 1}
    for x in nums:
        curr += x
        count += pref.get(curr - k, 0)
        pref[curr] = pref.get(curr, 0) + 1
    return count
""",
            "c": """int subarraySum() { return 0; }
""",
            "cpp": """int subarraySum(vector<int>& nums, int k) { return 0; }
""",
            "java": """public class Solution {
    public static int subarraySum(int[] nums, int k) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'nums': [1, 1, 1], 'k': 2}, expected_output=2, is_hidden=False),
            TestCase(id=2, input={'nums': [1, 2, 3], 'k': 3}, expected_output=2, is_hidden=False)
        ],
        learning_objectives=[
            "Prefix sum frequency hash map lookup"
],
        common_misconceptions=[
            "Two pointer failure on negative numbers"
],
        hint="""Map stores frequency of prefix sums.""",
        source="curated",
        is_generated=False
    ),
    "rotate-array": Problem(
        id="rotate-array",
        title="Rotate Array (Right by K)",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="""Rotate array to the right by `k` steps in-place.""",
        examples=[
            {
                        "input": "nums = [1, 2, 3, 4, 5, 6, 7], k = 3",
                        "output": "[5, 6, 7, 1, 2, 3, 4]"
            }
],
        constraints=[
            "1 <= nums.length <= 10^5"
],
        starter_code={
            "python": """def rotate(nums: list, k: int) -> list:
    pass
""",
            "c": """void rotate() {}
""",
            "cpp": """vector<int> rotate(vector<int>& nums, int k) { return nums; }
""",
            "java": """public class Solution {
    public static int[] rotate(int[] nums, int k) { return nums; }
}
"""
        },
        expected_solution={
            "python": """def rotate(nums: list, k: int) -> list:
    k %= len(nums)
    def rev(l, r):
        while l < r: nums[l], nums[r] = nums[r], nums[l]; l += 1; r -= 1
    rev(0, len(nums) - 1); rev(0, k - 1); rev(k, len(nums) - 1)
    return nums
""",
            "c": """void rotate() {}
""",
            "cpp": """vector<int> rotate(vector<int>& nums, int k) { return nums; }
""",
            "java": """public class Solution {
    public static int[] rotate(int[] nums, int k) { return nums; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'nums': [1, 2, 3, 4, 5, 6, 7], 'k': 3}, expected_output=[5, 6, 7, 1, 2, 3, 4], is_hidden=False)
        ],
        learning_objectives=[
            "Triple reversal algorithm"
],
        common_misconceptions=[
            "O(k*n) shift timeout"
],
        hint="""Reverse all, reverse first k, reverse remaining.""",
        source="curated",
        is_generated=False
    ),
    "first-missing-positive": Problem(
        id="first-missing-positive",
        title="First Missing Positive",
        difficulty="Hard",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="""Given unsorted integer array `nums`, return the smallest positive integer that is not present in O(n) time and O(1) space.""",
        examples=[
            {
                        "input": "nums = [1, 2, 0]",
                        "output": "3"
            },
            {
                        "input": "nums = [3, 4, -1, 1]",
                        "output": "2"
            }
],
        constraints=[
            "1 <= nums.length <= 10^5"
],
        starter_code={
            "python": """def first_missing_positive(nums: list) -> int:
    pass
""",
            "c": """int firstMissingPositive() { return 1; }
""",
            "cpp": """int firstMissingPositive(vector<int>& nums) { return 1; }
""",
            "java": """public class Solution {
    public static int firstMissingPositive(int[] nums) { return 1; }
}
"""
        },
        expected_solution={
            "python": """def first_missing_positive(nums: list) -> int:
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            idx = nums[i] - 1
            nums[i], nums[idx] = nums[idx], nums[i]
    for i in range(n):
        if nums[i] != i + 1: return i + 1
    return n + 1
""",
            "c": """int firstMissingPositive() { return 1; }
""",
            "cpp": """int firstMissingPositive(vector<int>& nums) { return 1; }
""",
            "java": """public class Solution {
    public static int firstMissingPositive(int[] nums) { return 1; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 0], expected_output=3, is_hidden=False),
            TestCase(id=2, input=[3, 4, -1, 1], expected_output=2, is_hidden=False),
            TestCase(id=3, input=[7, 8, 9, 11, 12], expected_output=1, is_hidden=False)
        ],
        learning_objectives=[
            "Cycle sort array indexing as hash table"
],
        common_misconceptions=[
            "Using O(N) hash set"
],
        hint="""Place each number x at index x - 1.""",
        source="curated",
        is_generated=False
    ),
    "find-all-numbers-disappeared": Problem(
        id="find-all-numbers-disappeared",
        title="Find All Numbers Disappeared in an Array",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Hash Maps & Sets",
        description="""Given array `nums` of `n` integers where `nums[i]` is in `[1, n]`, return an array of all integers in `[1, n]` that do not appear in `nums`.""",
        examples=[
            {
                        "input": "nums = [4, 3, 2, 7, 8, 2, 3, 1]",
                        "output": "[5, 6]"
            }
],
        constraints=[
            "n == nums.length"
],
        starter_code={
            "python": """def find_disappeared_numbers(nums: list) -> list:
    pass
""",
            "c": """void findDisappearedNumbers() {}
""",
            "cpp": """vector<int> findDisappearedNumbers(vector<int>& nums) { return {}; }
""",
            "java": """public class Solution {
    public static List<Integer> findDisappearedNumbers(int[] nums) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def find_disappeared_numbers(nums: list) -> list:
    s = set(nums)
    return [i for i in range(1, len(nums) + 1) if i not in s]
""",
            "c": """void findDisappearedNumbers() {}
""",
            "cpp": """vector<int> findDisappearedNumbers(vector<int>& nums) { return {}; }
""",
            "java": """public class Solution {
    public static List<Integer> findDisappearedNumbers(int[] nums) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[4, 3, 2, 7, 8, 2, 3, 1], expected_output=[5, 6], is_hidden=False),
            TestCase(id=2, input=[1, 1], expected_output=[2], is_hidden=False)
        ],
        learning_objectives=[
            "Range verification against 1 to n"
],
        common_misconceptions=[
            "1-based index offsets"
],
        hint="""Identify missing numbers from 1 to n.""",
        source="curated",
        is_generated=False
    ),
    "longest-common-prefix": Problem(
        id="longest-common-prefix",
        title="Longest Common Prefix",
        difficulty="Easy",
        topic="Strings",
        subtopic="String Manipulation",
        description="""Find longest common prefix string amongst an array of strings.""",
        examples=[
            {
                        "input": "strs = ['flower', 'flow', 'flight']",
                        "output": "'fl'"
            }
],
        constraints=[
            "1 <= strs.length <= 200"
],
        starter_code={
            "python": """def longest_common_prefix(strs: list) -> str:
    pass
""",
            "c": """char* longestCommonPrefix() { return ""; }
""",
            "cpp": """string longestCommonPrefix(vector<string>& strs) { return ""; }
""",
            "java": """public class Solution {
    public static String longestCommonPrefix(String[] strs) { return ""; }
}
"""
        },
        expected_solution={
            "python": """def longest_common_prefix(strs: list) -> str:
    if not strs: return ''
    p = strs[0]
    for s in strs[1:]:
        while not s.startswith(p):
            p = p[:-1]
            if not p: return ''
    return p
""",
            "c": """char* longestCommonPrefix() { return ""; }
""",
            "cpp": """string longestCommonPrefix(vector<string>& strs) { return ""; }
""",
            "java": """public class Solution {
    public static String longestCommonPrefix(String[] strs) { return ""; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=['flower', 'flow', 'flight'], expected_output='fl', is_hidden=False),
            TestCase(id=2, input=['dog', 'racecar', 'car'], expected_output='', is_hidden=False)
        ],
        learning_objectives=[
            "Horizontal prefix trimming"
],
        common_misconceptions=[
            "Assuming match anywhere in string"
],
        hint="""Trim prefix while startswith fails.""",
        source="curated",
        is_generated=False
    ),
    "first-unique-character": Problem(
        id="first-unique-character",
        title="First Unique Character in a String",
        difficulty="Easy",
        topic="Strings",
        subtopic="Anagrams & Palindromes",
        description="""Find first non-repeating character in string `s` and return its index, or -1.""",
        examples=[
            {
                        "input": "s = 'leetcode'",
                        "output": "0"
            }
],
        constraints=[
            "1 <= s.length <= 10^5"
],
        starter_code={
            "python": """def first_uniq_char(s: str) -> int:
    pass
""",
            "c": """int firstUniqChar(char* s) { return -1; }
""",
            "cpp": """int firstUniqChar(string s) { return -1; }
""",
            "java": """public class Solution {
    public static int firstUniqChar(String s) { return -1; }
}
"""
        },
        expected_solution={
            "python": """def first_uniq_char(s: str) -> int:
    from collections import Counter
    c = Counter(s)
    for i, ch in enumerate(s):
        if c[ch] == 1: return i
    return -1
""",
            "c": """int firstUniqChar(char* s) { return -1; }
""",
            "cpp": """int firstUniqChar(string s) { return -1; }
""",
            "java": """public class Solution {
    public static int firstUniqChar(String s) { return -1; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='leetcode', expected_output=0, is_hidden=False),
            TestCase(id=2, input='loveleetcode', expected_output=2, is_hidden=False),
            TestCase(id=3, input='aabb', expected_output=-1, is_hidden=False)
        ],
        learning_objectives=[
            "Two-pass frequency map"
],
        common_misconceptions=[
            "Nested O(N^2) loops"
],
        hint="""Count frequencies, then scan for count == 1.""",
        source="curated",
        is_generated=False
    ),
    "isomorphic-strings": Problem(
        id="isomorphic-strings",
        title="Isomorphic Strings",
        difficulty="Easy",
        topic="Strings",
        subtopic="String Manipulation",
        description="""Determine if strings `s` and `t` are isomorphic.""",
        examples=[
            {
                        "input": "s = 'egg', t = 'add'",
                        "output": "True"
            }
],
        constraints=[
            "t.length == s.length"
],
        starter_code={
            "python": """def is_isomorphic(s: str, t: str) -> bool:
    pass
""",
            "c": """int isIsomorphic() { return 0; }
""",
            "cpp": """bool isIsomorphic() { return false; }
""",
            "java": """public class Solution {
    public static boolean isIsomorphic() { return false; }
}
"""
        },
        expected_solution={
            "python": """def is_isomorphic(s: str, t: str) -> bool:
    return len(set(zip(s, t))) == len(set(s)) == len(set(t))
""",
            "c": """int isIsomorphic() { return 0; }
""",
            "cpp": """bool isIsomorphic() { return false; }
""",
            "java": """public class Solution {
    public static boolean isIsomorphic() { return false; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'s': 'egg', 't': 'add'}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'s': 'foo', 't': 'bar'}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Bijective mapping check"
],
        common_misconceptions=[
            "One-way mapping collisions"
],
        hint="""Check unique mappings both ways.""",
        source="curated",
        is_generated=False
    ),
    "valid-palindrome-ii": Problem(
        id="valid-palindrome-ii",
        title="Valid Palindrome II (At Most 1 Deletion)",
        difficulty="Easy",
        topic="Strings",
        subtopic="Anagrams & Palindromes",
        description="""Given string `s`, return `True` if it can be a palindrome after deleting at most one character.""",
        examples=[
            {
                        "input": "s = 'aba'",
                        "output": "True"
            },
            {
                        "input": "s = 'abca'",
                        "output": "True"
            }
],
        constraints=[
            "1 <= s.length <= 10^5"
],
        starter_code={
            "python": """def valid_palindrome_ii(s: str) -> bool:
    pass
""",
            "c": """int validPalindromeII() { return 1; }
""",
            "cpp": """bool validPalindromeII() { return true; }
""",
            "java": """public class Solution {
    public static boolean validPalindromeII() { return true; }
}
"""
        },
        expected_solution={
            "python": """def valid_palindrome_ii(s: str) -> bool:
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]:
            s1, s2 = s[l+1:r+1], s[l:r]
            return s1 == s1[::-1] or s2 == s2[::-1]
        l += 1; r -= 1
    return True
""",
            "c": """int validPalindromeII() { return 1; }
""",
            "cpp": """bool validPalindromeII() { return true; }
""",
            "java": """public class Solution {
    public static boolean validPalindromeII() { return true; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='aba', expected_output=True, is_hidden=False),
            TestCase(id=2, input='abca', expected_output=True, is_hidden=False),
            TestCase(id=3, input='abc', expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Greedy mismatch branch check"
],
        common_misconceptions=[
            "Trying all character deletions"
],
        hint="""When mismatch occurs, test skipping left or right character.""",
        source="curated",
        is_generated=False
    ),
    "longest-palindromic-substring": Problem(
        id="longest-palindromic-substring",
        title="Longest Palindromic Substring",
        difficulty="Medium",
        topic="Strings",
        subtopic="Pattern Matching",
        description="""Return the longest palindromic substring in string `s`.""",
        examples=[
            {
                        "input": "s = 'babad'",
                        "output": "'bab'"
            }
],
        constraints=[
            "1 <= s.length <= 1000"
],
        starter_code={
            "python": """def longest_palindrome(s: str) -> str:
    pass
""",
            "c": """char* longestPalindrome() { return ""; }
""",
            "cpp": """string longestPalindrome(string s) { return ""; }
""",
            "java": """public class Solution {
    public static String longestPalindrome(String s) { return ""; }
}
"""
        },
        expected_solution={
            "python": """def longest_palindrome(s: str) -> str:
    if not s: return ''
    start, end = 0, 0
    def exp(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]: l -= 1; r += 1
        return l + 1, r - 1
    for i in range(len(s)):
        l1, r1 = exp(i, i)
        l2, r2 = exp(i, i + 1)
        if r1 - l1 > end - start: start, end = l1, r1
        if r2 - l2 > end - start: start, end = l2, r2
    return s[start:end+1]
""",
            "c": """char* longestPalindrome() { return ""; }
""",
            "cpp": """string longestPalindrome(string s) { return ""; }
""",
            "java": """public class Solution {
    public static String longestPalindrome(String s) { return ""; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='babad', expected_output='bab', is_hidden=False),
            TestCase(id=2, input='cbbd', expected_output='bb', is_hidden=False)
        ],
        learning_objectives=[
            "Expand around 2N - 1 centers"
],
        common_misconceptions=[
            "O(N^3) brute force"
],
        hint="""Expand around i and i+1.""",
        source="curated",
        is_generated=False
    ),
    "string-to-integer-atoi": Problem(
        id="string-to-integer-atoi",
        title="String to Integer (atoi)",
        difficulty="Medium",
        topic="Strings",
        subtopic="String Manipulation",
        description="""Convert a string to a 32-bit signed integer with clamping.""",
        examples=[
            {
                        "input": "s = '42'",
                        "output": "42"
            },
            {
                        "input": "s = '   -42'",
                        "output": "-42"
            }
],
        constraints=[
            "0 <= s.length <= 200"
],
        starter_code={
            "python": """def my_atoi(s: str) -> int:
    pass
""",
            "c": """int myAtoi() { return 0; }
""",
            "cpp": """int myAtoi(string s) { return 0; }
""",
            "java": """public class Solution {
    public static int myAtoi(String s) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def my_atoi(s: str) -> int:
    s = s.strip()
    if not s: return 0
    sign, idx = 1, 0
    if s[0] == '-': sign, idx = -1, 1
    elif s[0] == '+': idx = 1
    val = 0
    while idx < len(s) and s[idx].isdigit():
        val = val * 10 + int(s[idx]); idx += 1
    val *= sign
    return max(-2**31, min(2**31 - 1, val))
""",
            "c": """int myAtoi() { return 0; }
""",
            "cpp": """int myAtoi(string s) { return 0; }
""",
            "java": """public class Solution {
    public static int myAtoi(String s) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input='42', expected_output=42, is_hidden=False),
            TestCase(id=2, input='   -42', expected_output=-42, is_hidden=False),
            TestCase(id=3, input='4193 with words', expected_output=4193, is_hidden=False)
        ],
        learning_objectives=[
            "State machine parser with overflow handling"
],
        common_misconceptions=[
            "Unchecked integer overflow"
],
        hint="""Handle leading spaces, sign, digits, and clamp.""",
        source="curated",
        is_generated=False
    ),
    "permutation-in-string": Problem(
        id="permutation-in-string",
        title="Permutation in String",
        difficulty="Medium",
        topic="Strings",
        subtopic="Sliding Window",
        description="""Return `True` if `s2` contains a permutation of `s1`.""",
        examples=[
            {
                        "input": "s1 = 'ab', s2 = 'eidbaooo'",
                        "output": "True"
            }
],
        constraints=[
            "1 <= s1.length, s2.length <= 10^4"
],
        starter_code={
            "python": """def check_inclusion(s1: str, s2: str) -> bool:
    pass
""",
            "c": """int checkInclusion() { return 0; }
""",
            "cpp": """bool checkInclusion(string s1, string s2) { return false; }
""",
            "java": """public class Solution {
    public static boolean checkInclusion(String s1, String s2) { return false; }
}
"""
        },
        expected_solution={
            "python": """def check_inclusion(s1: str, s2: str) -> bool:
    from collections import Counter
    n1, n2 = len(s1), len(s2)
    if n1 > n2: return False
    c1 = Counter(s1)
    c2 = Counter(s2[:n1])
    if c1 == c2: return True
    for i in range(n1, n2):
        c2[s2[i]] += 1
        c2[s2[i - n1]] -= 1
        if c2[s2[i - n1]] == 0: del c2[s2[i - n1]]
        if c1 == c2: return True
    return False
""",
            "c": """int checkInclusion() { return 0; }
""",
            "cpp": """bool checkInclusion(string s1, string s2) { return false; }
""",
            "java": """public class Solution {
    public static boolean checkInclusion(String s1, String s2) { return false; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'s1': 'ab', 's2': 'eidbaooo'}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'s1': 'ab', 's2': 'eidboaoo'}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Fixed size sliding window counter"
],
        common_misconceptions=[
            "Generating all permutations of s1"
],
        hint="""Sliding window of length len(s1).""",
        source="curated",
        is_generated=False
    ),
    "find-all-anagrams": Problem(
        id="find-all-anagrams",
        title="Find All Anagrams in a String",
        difficulty="Medium",
        topic="Strings",
        subtopic="Sliding Window",
        description="""Given strings `s` and `p`, return an array of all the start indices of `p`'s anagrams in `s`.""",
        examples=[
            {
                        "input": "s = 'cbaebabacd', p = 'abc'",
                        "output": "[0, 6]"
            }
],
        constraints=[
            "1 <= s.length, p.length <= 3 * 10^4"
],
        starter_code={
            "python": """def find_anagrams(s: str, p: str) -> list:
    pass
""",
            "c": """void findAnagrams() {}
""",
            "cpp": """vector<int> findAnagrams(string s, string p) { return {}; }
""",
            "java": """public class Solution {
    public static List<Integer> findAnagrams(String s, String p) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def find_anagrams(s: str, p: str) -> list:
    from collections import Counter
    ns, np = len(s), len(p)
    if np > ns: return []
    cp = Counter(p)
    cs = Counter(s[:np])
    res = [0] if cs == cp else []
    for i in range(np, ns):
        cs[s[i]] += 1
        cs[s[i - np]] -= 1
        if cs[s[i - np]] == 0: del cs[s[i - np]]
        if cs == cp: res.append(i - np + 1)
    return res
""",
            "c": """void findAnagrams() {}
""",
            "cpp": """vector<int> findAnagrams(string s, string p) { return {}; }
""",
            "java": """public class Solution {
    public static List<Integer> findAnagrams(String s, String p) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'s': 'cbaebabacd', 'p': 'abc'}, expected_output=[0, 6], is_hidden=False),
            TestCase(id=2, input={'s': 'abab', 'p': 'ab'}, expected_output=[0, 1, 2], is_hidden=False)
        ],
        learning_objectives=[
            "Sliding window character frequency matching"
],
        common_misconceptions=[
            "Sorting each substring"
],
        hint="""Slide window of size len(p) updating frequencies.""",
        source="curated",
        is_generated=False
    ),
    "min-stack": Problem(
        id="min-stack",
        title="Min Stack (O(1) Retrieval)",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="""Design a stack supporting push, pop, top, and retrieving the minimum element in constant time.""",
        examples=[
            {
                        "input": "ops = ['push', 'push', 'getMin'], vals = [-2, 0, null]",
                        "output": "[null, null, -2]"
            }
],
        constraints=[
            "Stack methods are valid"
],
        starter_code={
            "python": """def min_stack_runner(ops: list, vals: list) -> list:
    pass
""",
            "c": """void minStackRunner() {}
""",
            "cpp": """vector<int> minStackRunner() { return {}; }
""",
            "java": """public class Solution {
    public static List<Integer> minStackRunner() { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def min_stack_runner(ops: list, vals: list) -> list:
    st, mst, out = [], [], []
    for op, v in zip(ops, vals):
        if op == 'push':
            st.append(v)
            mst.append(v if not mst or v <= mst[-1] else mst[-1])
            out.append(None)
        elif op == 'pop':
            st.pop(); mst.pop(); out.append(None)
        elif op == 'top': out.append(st[-1])
        elif op == 'getMin': out.append(mst[-1])
    return out
""",
            "c": """void minStackRunner() {}
""",
            "cpp": """vector<int> minStackRunner() { return {}; }
""",
            "java": """public class Solution {
    public static List<Integer> minStackRunner() { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'ops': ['push', 'push', 'getMin'], 'vals': [-2, 0, None]}, expected_output=[None, None, -2], is_hidden=False)
        ],
        learning_objectives=[
            "Synchronized companion min-stack"
],
        common_misconceptions=[
            "Linear scan min lookups"
],
        hint="""Companion stack stores current minimum.""",
        source="curated",
        is_generated=False
    ),
    "evaluate-reverse-polish-notation": Problem(
        id="evaluate-reverse-polish-notation",
        title="Evaluate Reverse Polish Notation",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="""Evaluate arithmetic expression in Reverse Polish Notation (`+`, `-`, `*`, `/`).""",
        examples=[
            {
                        "input": "tokens = ['2', '1', '+', '3', '*']",
                        "output": "9"
            }
],
        constraints=[
            "1 <= tokens.length <= 10^4"
],
        starter_code={
            "python": """def eval_rpn(tokens: list) -> int:
    pass
""",
            "c": """int evalRPN() { return 0; }
""",
            "cpp": """int evalRPN(vector<string>& tokens) { return 0; }
""",
            "java": """public class Solution {
    public static int evalRPN(String[] tokens) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def eval_rpn(tokens: list) -> int:
    st = []
    for t in tokens:
        if t in '+-*/':
            b, a = st.pop(), st.pop()
            if t == '+': st.append(a + b)
            elif t == '-': st.append(a - b)
            elif t == '*': st.append(a * b)
            elif t == '/': st.append(int(a / b))
        else: st.append(int(t))
    return st[0]
""",
            "c": """int evalRPN() { return 0; }
""",
            "cpp": """int evalRPN(vector<string>& tokens) { return 0; }
""",
            "java": """public class Solution {
    public static int evalRPN(String[] tokens) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=['2', '1', '+', '3', '*'], expected_output=9, is_hidden=False),
            TestCase(id=2, input=['4', '13', '5', '/', '+'], expected_output=6, is_hidden=False)
        ],
        learning_objectives=[
            "Operand stack evaluation"
],
        common_misconceptions=[
            "Reversing operand order on subtract/divide"
],
        hint="""First pop is right operand, second pop is left operand.""",
        source="curated",
        is_generated=False
    ),
    "next-greater-element-i": Problem(
        id="next-greater-element-i",
        title="Next Greater Element I",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="""Find next greater element to the right for `nums1` inside `nums2`.""",
        examples=[
            {
                        "input": "nums1 = [4, 1, 2], nums2 = [1, 3, 4, 2]",
                        "output": "[-1, 3, -1]"
            }
],
        constraints=[
            "1 <= nums1.length <= nums2.length <= 1000"
],
        starter_code={
            "python": """def next_greater_element(nums1: list, nums2: list) -> list:
    pass
""",
            "c": """void nextGreaterElement() {}
""",
            "cpp": """vector<int> nextGreaterElement(vector<int>& a, vector<int>& b) { return {}; }
""",
            "java": """public class Solution {
    public static int[] nextGreaterElement(int[] a, int[] b) { return new int[0]; }
}
"""
        },
        expected_solution={
            "python": """def next_greater_element(nums1: list, nums2: list) -> list:
    nxt, st = {}, []
    for x in nums2:
        while st and st[-1] < x: nxt[st.pop()] = x
        st.append(x)
    return [nxt.get(x, -1) for x in nums1]
""",
            "c": """void nextGreaterElement() {}
""",
            "cpp": """vector<int> nextGreaterElement(vector<int>& a, vector<int>& b) { return {}; }
""",
            "java": """public class Solution {
    public static int[] nextGreaterElement(int[] a, int[] b) { return new int[0]; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'nums1': [4, 1, 2], 'nums2': [1, 3, 4, 2]}, expected_output=[-1, 3, -1], is_hidden=False)
        ],
        learning_objectives=[
            "Monotonic decreasing stack caching next greater"
],
        common_misconceptions=[
            "Repeated rightward linear scans"
],
        hint="""Decreasing stack maps elements to their first greater neighbor.""",
        source="curated",
        is_generated=False
    ),
    "asteroid-collision": Problem(
        id="asteroid-collision",
        title="Asteroid Collision",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="""Simulate asteroid row collisions where magnitude is size and sign is direction.""",
        examples=[
            {
                        "input": "asteroids = [5, 10, -5]",
                        "output": "[5, 10]"
            }
],
        constraints=[
            "2 <= asteroids.length <= 10^4"
],
        starter_code={
            "python": """def asteroid_collision(asteroids: list) -> list:
    pass
""",
            "c": """void asteroidCollision() {}
""",
            "cpp": """vector<int> asteroidCollision(vector<int>& a) { return {}; }
""",
            "java": """public class Solution {
    public static int[] asteroidCollision(int[] a) { return new int[0]; }
}
"""
        },
        expected_solution={
            "python": """def asteroid_collision(asteroids: list) -> list:
    st = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and st and st[-1] > 0:
            if st[-1] < -a: st.pop()
            elif st[-1] == -a: st.pop(); alive = False
            else: alive = False
        if alive: st.append(a)
    return st
""",
            "c": """void asteroidCollision() {}
""",
            "cpp": """vector<int> asteroidCollision(vector<int>& a) { return {}; }
""",
            "java": """public class Solution {
    public static int[] asteroidCollision(int[] a) { return new int[0]; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[5, 10, -5], expected_output=[5, 10], is_hidden=False),
            TestCase(id=2, input=[8, -8], expected_output=[], is_hidden=False)
        ],
        learning_objectives=[
            "Stack collision simulation"
],
        common_misconceptions=[
            "Colliding asteroids moving in same direction"
],
        hint="""Only rightwards (>0) collides with incoming leftwards (<0).""",
        source="curated",
        is_generated=False
    ),
    "baseball-game": Problem(
        id="baseball-game",
        title="Baseball Game (Stack Records)",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="""Keep score using operations: integer, '+', 'D', 'C'. Return sum of all scores.""",
        examples=[
            {
                        "input": "ops = ['5', '2', 'C', 'D', '+']",
                        "output": "30"
            }
],
        constraints=[
            "1 <= ops.length <= 1000"
],
        starter_code={
            "python": """def cal_points(ops: list) -> int:
    pass
""",
            "c": """int calPoints() { return 0; }
""",
            "cpp": """int calPoints(vector<string>& ops) { return 0; }
""",
            "java": """public class Solution {
    public static int calPoints(String[] ops) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def cal_points(ops: list) -> int:
    st = []
    for op in ops:
        if op == '+': st.append(st[-1] + st[-2])
        elif op == 'D': st.append(2 * st[-1])
        elif op == 'C': st.pop()
        else: st.append(int(op))
    return sum(st)
""",
            "c": """int calPoints() { return 0; }
""",
            "cpp": """int calPoints(vector<string>& ops) { return 0; }
""",
            "java": """public class Solution {
    public static int calPoints(String[] ops) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=['5', '2', 'C', 'D', '+'], expected_output=30, is_hidden=False),
            TestCase(id=2, input=['5', '-2', '4', 'C', 'D', '9', '+', '+'], expected_output=27, is_hidden=False)
        ],
        learning_objectives=[
            "Stack state rollback and double score operations"
],
        common_misconceptions=[
            "Index error when stack has fewer than 2 items on +"
],
        hint="""Use stack to record scores.""",
        source="curated",
        is_generated=False
    ),
    "backspace-string-compare": Problem(
        id="backspace-string-compare",
        title="Backspace String Compare",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="""Given strings `s` and `t`, return `True` if equal when typed into empty text editors ('#' is backspace).""",
        examples=[
            {
                        "input": "s = 'ab#c', t = 'ad#c'",
                        "output": "True"
            }
],
        constraints=[
            "1 <= s.length, t.length <= 200"
],
        starter_code={
            "python": """def backspace_compare(s: str, t: str) -> bool:
    pass
""",
            "c": """int backspaceCompare() { return 1; }
""",
            "cpp": """bool backspaceCompare(string s, string t) { return true; }
""",
            "java": """public class Solution {
    public static boolean backspaceCompare(String s, String t) { return true; }
}
"""
        },
        expected_solution={
            "python": """def backspace_compare(s: str, t: str) -> bool:
    def build(st_str):
        st = []
        for ch in st_str:
            if ch != '#': st.append(ch)
            elif st: st.pop()
        return ''.join(st)
    return build(s) == build(t)
""",
            "c": """int backspaceCompare() { return 1; }
""",
            "cpp": """bool backspaceCompare(string s, string t) { return true; }
""",
            "java": """public class Solution {
    public static boolean backspaceCompare(String s, String t) { return true; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'s': 'ab#c', 't': 'ad#c'}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'s': 'ab##', 't': 'c#d#'}, expected_output=True, is_hidden=False),
            TestCase(id=3, input={'s': 'a#c', 't': 'b'}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Stack simulation of typing and backspacing"
],
        common_misconceptions=[
            "Popping on empty stack causes index error"
],
        hint="""Build final string using stack.""",
        source="curated",
        is_generated=False
    ),
    "min-cost-climbing-stairs": Problem(
        id="min-cost-climbing-stairs",
        title="Min Cost Climbing Stairs",
        difficulty="Easy",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="""Given cost array, return minimum cost to reach the top of the staircase (can take 1 or 2 steps).""",
        examples=[
            {
                        "input": "cost = [10, 15, 20]",
                        "output": "15"
            }
],
        constraints=[
            "2 <= cost.length <= 1000"
],
        starter_code={
            "python": """def min_cost_climbing_stairs(cost: list) -> int:
    pass
""",
            "c": """int minCostClimbingStairs(int* cost, int n) { int c1=0, c2=0; for(int i=n-1;i>=0;i--){ int t = cost[i] + (c1<c2?c1:c2); c2=c1; c1=t; } return c1<c2?c1:c2; }
""",
            "cpp": """int minCostClimbingStairs(vector<int>& cost) { int c1=0, c2=0; for(int i=(int)cost.size()-1;i>=0;i--){ int t = cost[i] + min(c1, c2); c2=c1; c1=t; } return min(c1, c2); }
""",
            "java": """public class Solution {
    public static int minCostClimbingStairs(int[] cost) { int c1=0, c2=0; for(int i=cost.length-1;i>=0;i--){ int t = cost[i] + Math.min(c1, c2); c2=c1; c1=t; } return Math.min(c1, c2); }
}
"""
        },
        expected_solution={
            "python": """def min_cost_climbing_stairs(cost: list) -> int:
    c1, c2 = 0, 0
    for x in reversed(cost): c1, c2 = x + min(c1, c2), c1
    return min(c1, c2)
""",
            "c": """int minCostClimbingStairs(int* cost, int n) { int c1=0, c2=0; for(int i=n-1;i>=0;i--){ int t = cost[i] + (c1<c2?c1:c2); c2=c1; c1=t; } return c1<c2?c1:c2; }
""",
            "cpp": """int minCostClimbingStairs(vector<int>& cost) { int c1=0, c2=0; for(int i=(int)cost.size()-1;i>=0;i--){ int t = cost[i] + min(c1, c2); c2=c1; c1=t; } return min(c1, c2); }
""",
            "java": """public class Solution {
    public static int minCostClimbingStairs(int[] cost) { int c1=0, c2=0; for(int i=cost.length-1;i>=0;i--){ int t = cost[i] + Math.min(c1, c2); c2=c1; c1=t; } return Math.min(c1, c2); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[10, 15, 20], expected_output=15, is_hidden=False),
            TestCase(id=2, input=[1, 100, 1, 1, 1, 100, 1, 1, 100, 1], expected_output=6, is_hidden=False)
        ],
        learning_objectives=[
            "Rolling 2-variable bottom-up DP"
],
        common_misconceptions=[
            "Greedy step choices"
],
        hint="""dp[i] = cost[i] + min(dp[i+1], dp[i+2]).""",
        source="curated",
        is_generated=False
    ),
    "tribonacci-number": Problem(
        id="tribonacci-number",
        title="N-th Tribonacci Number",
        difficulty="Easy",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="""T_0 = 0, T_1 = 1, T_2 = 1, and T_{n+3} = T_n + T_{n+1} + T_{n+2}. Return T_n.""",
        examples=[
            {
                        "input": "n = 4",
                        "output": "4"
            },
            {
                        "input": "n = 25",
                        "output": "1389537"
            }
],
        constraints=[
            "0 <= n <= 37"
],
        starter_code={
            "python": """def tribonacci(n: int) -> int:
    pass
""",
            "c": """int tribonacci(int n) { if(n==0) return 0; if(n<=2) return 1; int a=0, b=1, c=1, d; for(int i=3;i<=n;i++){ d=a+b+c; a=b; b=c; c=d; } return c; }
""",
            "cpp": """int tribonacci(int n) { if(n==0) return 0; if(n<=2) return 1; int a=0, b=1, c=1, d; for(int i=3;i<=n;i++){ d=a+b+c; a=b; b=c; c=d; } return c; }
""",
            "java": """public class Solution {
    public static int tribonacci(int n) { if(n==0) return 0; if(n<=2) return 1; int a=0, b=1, c=1, d; for(int i=3;i<=n;i++){ d=a+b+c; a=b; b=c; c=d; } return c; }
}
"""
        },
        expected_solution={
            "python": """def tribonacci(n: int) -> int:
    if n == 0: return 0
    if n <= 2: return 1
    a, b, c = 0, 1, 1
    for _ in range(3, n + 1): a, b, c = b, c, a + b + c
    return c
""",
            "c": """int tribonacci(int n) { if(n==0) return 0; if(n<=2) return 1; int a=0, b=1, c=1, d; for(int i=3;i<=n;i++){ d=a+b+c; a=b; b=c; c=d; } return c; }
""",
            "cpp": """int tribonacci(int n) { if(n==0) return 0; if(n<=2) return 1; int a=0, b=1, c=1, d; for(int i=3;i<=n;i++){ d=a+b+c; a=b; b=c; c=d; } return c; }
""",
            "java": """public class Solution {
    public static int tribonacci(int n) { if(n==0) return 0; if(n<=2) return 1; int a=0, b=1, c=1, d; for(int i=3;i<=n;i++){ d=a+b+c; a=b; b=c; c=d; } return c; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=4, expected_output=4, is_hidden=False),
            TestCase(id=2, input=25, expected_output=1389537, is_hidden=False),
            TestCase(id=3, input=0, expected_output=0, is_hidden=False),
            TestCase(id=4, input=1, expected_output=1, is_hidden=False)
        ],
        learning_objectives=[
            "Constant space linear recurrence"
],
        common_misconceptions=[
            "Overlapping recursive overhead"
],
        hint="""Track last 3 numbers.""",
        source="curated",
        is_generated=False
    ),
    "longest-increasing-subsequence": Problem(
        id="longest-increasing-subsequence",
        title="Longest Increasing Subsequence",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="""Return the length of the longest strictly increasing subsequence.""",
        examples=[
            {
                        "input": "nums = [10, 9, 2, 5, 3, 7, 101, 18]",
                        "output": "4"
            }
],
        constraints=[
            "1 <= nums.length <= 2500"
],
        starter_code={
            "python": """def length_of_lis(nums: list) -> int:
    pass
""",
            "c": """int lengthOfLIS() { return 0; }
""",
            "cpp": """int lengthOfLIS(vector<int>& nums) { return 0; }
""",
            "java": """public class Solution {
    public static int lengthOfLIS(int[] nums) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def length_of_lis(nums: list) -> int:
    import bisect
    tails = []
    for x in nums:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails): tails.append(x)
        else: tails[idx] = x
    return len(tails)
""",
            "c": """int lengthOfLIS() { return 0; }
""",
            "cpp": """int lengthOfLIS(vector<int>& nums) { return 0; }
""",
            "java": """public class Solution {
    public static int lengthOfLIS(int[] nums) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[10, 9, 2, 5, 3, 7, 101, 18], expected_output=4, is_hidden=False),
            TestCase(id=2, input=[0, 1, 0, 3, 2, 3], expected_output=4, is_hidden=False)
        ],
        learning_objectives=[
            "Patience sorting with binary search in O(N log N)"
],
        common_misconceptions=[
            "Confusing subsequence with substring"
],
        hint="""Binary search smallest tails.""",
        source="curated",
        is_generated=False
    ),
    "unique-paths": Problem(
        id="unique-paths",
        title="Unique Paths (Grid DP)",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="2D Grid DP",
        description="""Return number of possible unique paths from top-left to bottom-right of `m x n` grid.""",
        examples=[
            {
                        "input": "m = 3, n = 7",
                        "output": "28"
            }
],
        constraints=[
            "1 <= m, n <= 100"
],
        starter_code={
            "python": """def unique_paths(m: int, n: int) -> int:
    pass
""",
            "c": """int uniquePaths(int m, int n) { return 0; }
""",
            "cpp": """int uniquePaths(int m, int n) { return 0; }
""",
            "java": """public class Solution {
    public static int uniquePaths(int m, int n) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def unique_paths(m: int, n: int) -> int:
    row = [1] * n
    for _ in range(m - 1):
        for j in range(1, n): row[j] += row[j - 1]
    return row[-1]
""",
            "c": """int uniquePaths(int m, int n) { return 0; }
""",
            "cpp": """int uniquePaths(int m, int n) { return 0; }
""",
            "java": """public class Solution {
    public static int uniquePaths(int m, int n) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'m': 3, 'n': 7}, expected_output=28, is_hidden=False),
            TestCase(id=2, input={'m': 3, 'n': 2}, expected_output=3, is_hidden=False)
        ],
        learning_objectives=[
            "2D grid transition dp[i][j] = dp[i-1][j] + dp[i][j-1] in 1D array"
],
        common_misconceptions=[
            "Combinatorics factorial overflow"
],
        hint="""row[j] += row[j-1].""",
        source="curated",
        is_generated=False
    ),
    "word-break": Problem(
        id="word-break",
        title="Word Break (DP)",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="""Return `True` if string `s` can be segmented into words from `wordDict`.""",
        examples=[
            {
                        "input": "s = 'leetcode', wordDict = ['leet', 'code']",
                        "output": "True"
            }
],
        constraints=[
            "1 <= s.length <= 300"
],
        starter_code={
            "python": """def word_break(s: str, wordDict: list) -> bool:
    pass
""",
            "c": """int wordBreak() { return 0; }
""",
            "cpp": """bool wordBreak() { return false; }
""",
            "java": """public class Solution {
    public static boolean wordBreak() { return false; }
}
"""
        },
        expected_solution={
            "python": """def word_break(s: str, wordDict: list) -> bool:
    w = set(wordDict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in w:
                dp[i] = True; break
    return dp[len(s)]
""",
            "c": """int wordBreak() { return 0; }
""",
            "cpp": """bool wordBreak() { return false; }
""",
            "java": """public class Solution {
    public static boolean wordBreak() { return false; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'s': 'leetcode', 'wordDict': ['leet', 'code']}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'s': 'catsandog', 'wordDict': ['cats', 'dog', 'sand', 'and', 'cat']}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Prefix segmentation reachability table"
],
        common_misconceptions=[
            "Greedy prefix consumption"
],
        hint="""dp[i] = True if dp[j] and s[j:i] in dict.""",
        source="curated",
        is_generated=False
    ),
    "house-robber-ii": Problem(
        id="house-robber-ii",
        title="House Robber II (Circular DP)",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="""Houses are arranged in a circle. Cannot rob two adjacent houses. Return maximum loot.""",
        examples=[
            {
                        "input": "nums = [2, 3, 2]",
                        "output": "3"
            },
            {
                        "input": "nums = [1, 2, 3, 1]",
                        "output": "4"
            }
],
        constraints=[
            "1 <= nums.length <= 100"
],
        starter_code={
            "python": """def rob_circular(nums: list) -> int:
    pass
""",
            "c": """int robCircular() { return 0; }
""",
            "cpp": """int robCircular(vector<int>& nums) { return 0; }
""",
            "java": """public class Solution {
    public static int robCircular(int[] nums) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def rob_circular(nums: list) -> int:
    if not nums: return 0
    if len(nums) <= 2: return max(nums)
    def rob_line(h):
        r1, r2 = 0, 0
        for x in h: r1, r2 = r2, max(r2, r1 + x)
        return r2
    return max(rob_line(nums[:-1]), rob_line(nums[1:]))
""",
            "c": """int robCircular() { return 0; }
""",
            "cpp": """int robCircular(vector<int>& nums) { return 0; }
""",
            "java": """public class Solution {
    public static int robCircular(int[] nums) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[2, 3, 2], expected_output=3, is_hidden=False),
            TestCase(id=2, input=[1, 2, 3, 1], expected_output=4, is_hidden=False)
        ],
        learning_objectives=[
            "Decomposing circular DP into two linear DP passes"
],
        common_misconceptions=[
            "Simultaneously robbing first and last house"
],
        hint="""max(rob(nums[:-1]), rob(nums[1:])).""",
        source="curated",
        is_generated=False
    ),
    "two-sum-ii-sorted": Problem(
        id="two-sum-ii-sorted",
        title="Two Sum II - Input Array Is Sorted",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="""Find 1-indexed positions of two numbers adding up to `target` in sorted array.""",
        examples=[
            {
                        "input": "numbers = [2, 7, 11, 15], target = 9",
                        "output": "[1, 2]"
            }
],
        constraints=[
            "2 <= numbers.length <= 3 * 10^4"
],
        starter_code={
            "python": """def two_sum_sorted(numbers: list, target: int) -> list:
    pass
""",
            "c": """void twoSumSorted() {}
""",
            "cpp": """vector<int> twoSumSorted(vector<int>& n, int t) { return {}; }
""",
            "java": """public class Solution {
    public static int[] twoSumSorted(int[] n, int t) { return new int[0]; }
}
"""
        },
        expected_solution={
            "python": """def two_sum_sorted(numbers: list, target: int) -> list:
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target: return [l + 1, r + 1]
        elif s < target: l += 1
        else: r -= 1
    return []
""",
            "c": """void twoSumSorted() {}
""",
            "cpp": """vector<int> twoSumSorted(vector<int>& n, int t) { return {}; }
""",
            "java": """public class Solution {
    public static int[] twoSumSorted(int[] n, int t) { return new int[0]; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'numbers': [2, 7, 11, 15], 'target': 9}, expected_output=[1, 2], is_hidden=False),
            TestCase(id=2, input={'numbers': [2, 3, 4], 'target': 6}, expected_output=[1, 3], is_hidden=False)
        ],
        learning_objectives=[
            "Converging two pointers in O(N)"
],
        common_misconceptions=[
            "1-indexed output conversion"
],
        hint="""Adjust pointers based on sum vs target.""",
        source="curated",
        is_generated=False
    ),
    "remove-duplicates-sorted-array": Problem(
        id="remove-duplicates-sorted-array",
        title="Remove Duplicates from Sorted Array",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="""Remove duplicates in-place such that each unique element appears once. Return unique count.""",
        examples=[
            {
                        "input": "nums = [1, 1, 2]",
                        "output": "2"
            }
],
        constraints=[
            "1 <= nums.length <= 3 * 10^4"
],
        starter_code={
            "python": """def remove_duplicates(nums: list) -> int:
    pass
""",
            "c": """int removeDuplicates(int* nums, int n) { if(n==0) return 0; int k=1; for(int i=1;i<n;i++) if(nums[i]!=nums[i-1]) nums[k++]=nums[i]; return k; }
""",
            "cpp": """int removeDuplicates(vector<int>& nums) { if(nums.empty()) return 0; int k=1; for(int i=1;i<(int)nums.size();i++) if(nums[i]!=nums[i-1]) nums[k++]=nums[i]; return k; }
""",
            "java": """public class Solution {
    public static int removeDuplicates(int[] nums) { if(nums.length==0) return 0; int k=1; for(int i=1;i<nums.length;i++) if(nums[i]!=nums[i-1]) nums[k++]=nums[i]; return k; }
}
"""
        },
        expected_solution={
            "python": """def remove_duplicates(nums: list) -> int:
    if not nums: return 0
    k = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[i - 1]:
            nums[k] = nums[i]; k += 1
    return k
""",
            "c": """int removeDuplicates(int* nums, int n) { if(n==0) return 0; int k=1; for(int i=1;i<n;i++) if(nums[i]!=nums[i-1]) nums[k++]=nums[i]; return k; }
""",
            "cpp": """int removeDuplicates(vector<int>& nums) { if(nums.empty()) return 0; int k=1; for(int i=1;i<(int)nums.size();i++) if(nums[i]!=nums[i-1]) nums[k++]=nums[i]; return k; }
""",
            "java": """public class Solution {
    public static int removeDuplicates(int[] nums) { if(nums.length==0) return 0; int k=1; for(int i=1;i<nums.length;i++) if(nums[i]!=nums[i-1]) nums[k++]=nums[i]; return k; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[1, 1, 2], expected_output=2, is_hidden=False),
            TestCase(id=2, input=[0, 0, 1, 1, 1, 2, 2, 3, 3, 4], expected_output=5, is_hidden=False)
        ],
        learning_objectives=[
            "Slow and fast pointer overwrite"
],
        common_misconceptions=[
            "Creating a new list"
],
        hint="""k tracks next insertion slot.""",
        source="curated",
        is_generated=False
    ),
    "container-with-most-water": Problem(
        id="container-with-most-water",
        title="Container With Most Water",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="""Find two lines that together with x-axis contain the most water. Return max area.""",
        examples=[
            {
                        "input": "height = [1,8,6,2,5,4,8,3,7]",
                        "output": "49"
            }
],
        constraints=[
            "2 <= height.length <= 10^5"
],
        starter_code={
            "python": """def max_area(height: list) -> int:
    pass
""",
            "c": """int maxArea() { return 0; }
""",
            "cpp": """int maxArea(vector<int>& h) { return 0; }
""",
            "java": """public class Solution {
    public static int maxArea(int[] h) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def max_area(height: list) -> int:
    l, r, best = 0, len(height) - 1, 0
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]: l += 1
        else: r -= 1
    return best
""",
            "c": """int maxArea() { return 0; }
""",
            "cpp": """int maxArea(vector<int>& h) { return 0; }
""",
            "java": """public class Solution {
    public static int maxArea(int[] h) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[1, 8, 6, 2, 5, 4, 8, 3, 7], expected_output=49, is_hidden=False),
            TestCase(id=2, input=[1, 1], expected_output=1, is_hidden=False)
        ],
        learning_objectives=[
            "Greedy shrinking of limiting height boundary"
],
        common_misconceptions=[
            "O(N^2) pairwise checks"
],
        hint="""Always increment shorter bar.""",
        source="curated",
        is_generated=False
    ),
    "sort-colors": Problem(
        id="sort-colors",
        title="Sort Colors (Dutch National Flag)",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Sorting & Partitioning",
        description="""Sort array with 0s, 1s, and 2s in-place in a single pass.""",
        examples=[
            {
                        "input": "nums = [2, 0, 2, 1, 1, 0]",
                        "output": "[0, 0, 1, 1, 2, 2]"
            }
],
        constraints=[
            "1 <= nums.length <= 300"
],
        starter_code={
            "python": """def sort_colors(nums: list) -> list:
    pass
""",
            "c": """void sortColors() {}
""",
            "cpp": """vector<int> sortColors(vector<int>& nums) { return nums; }
""",
            "java": """public class Solution {
    public static int[] sortColors(int[] nums) { return nums; }
}
"""
        },
        expected_solution={
            "python": """def sort_colors(nums: list) -> list:
    l, m, h = 0, 0, len(nums) - 1
    while m <= h:
        if nums[m] == 0: nums[l], nums[m] = nums[m], nums[l]; l += 1; m += 1
        elif nums[m] == 1: m += 1
        else: nums[m], nums[h] = nums[h], nums[m]; h -= 1
    return nums
""",
            "c": """void sortColors() {}
""",
            "cpp": """vector<int> sortColors(vector<int>& nums) { return nums; }
""",
            "java": """public class Solution {
    public static int[] sortColors(int[] nums) { return nums; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[2, 0, 2, 1, 1, 0], expected_output=[0, 0, 1, 1, 2, 2], is_hidden=False)
        ],
        learning_objectives=[
            "3-way partitioning with low, mid, high pointers"
],
        common_misconceptions=[
            "Sorting in O(N log N)"
],
        hint="""Maintain boundaries for 0s, 1s, 2s.""",
        source="curated",
        is_generated=False
    ),
    "three-sum": Problem(
        id="three-sum",
        title="3Sum (Two Pointers)",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="""Return all unique triplets `[nums[i], nums[j], nums[k]]` such that they sum to 0.""",
        examples=[
            {
                        "input": "nums = [-1, 0, 1, 2, -1, -4]",
                        "output": "[[-1, -1, 2], [-1, 0, 1]]"
            }
],
        constraints=[
            "3 <= nums.length <= 3000"
],
        starter_code={
            "python": """def three_sum(nums: list) -> list:
    pass
""",
            "c": """void threeSum() {}
""",
            "cpp": """vector<vector<int>> threeSum(vector<int>& nums) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> threeSum(int[] nums) { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def three_sum(nums: list) -> list:
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]: continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s == 0:
                res.append([nums[i], nums[l], nums[r]])
                while l < r and nums[l] == nums[l + 1]: l += 1
                while l < r and nums[r] == nums[r - 1]: r -= 1
                l += 1; r -= 1
            elif s < 0: l += 1
            else: r -= 1
    return res
""",
            "c": """void threeSum() {}
""",
            "cpp": """vector<vector<int>> threeSum(vector<int>& nums) { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> threeSum(int[] nums) { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[-1, 0, 1, 2, -1, -4], expected_output=[[-1, -1, 2], [-1, 0, 1]], is_hidden=False),
            TestCase(id=2, input=[0, 1, 1], expected_output=[], is_hidden=False),
            TestCase(id=3, input=[0, 0, 0], expected_output=[[0, 0, 0]], is_hidden=False)
        ],
        learning_objectives=[
            "Sort + 2-pointer scan with duplicate skipping"
],
        common_misconceptions=[
            "O(N^3) combinations"
],
        hint="""Fix first element, use two pointers for remaining two.""",
        source="curated",
        is_generated=False
    ),
    "same-tree": Problem(
        id="same-tree",
        title="Same Tree (Tree DFS)",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="""Return `True` if two binary trees are structurally identical and have the same node values.""",
        examples=[
            {
                        "input": "p = [1, 2, 3], q = [1, 2, 3]",
                        "output": "True"
            }
],
        constraints=[
            "Node counts 0 to 100"
],
        starter_code={
            "python": """def is_same_tree(p: list, q: list) -> bool:
    pass
""",
            "c": """int isSameTree() { return 1; }
""",
            "cpp": """bool isSameTree() { return true; }
""",
            "java": """public class Solution {
    public static boolean isSameTree() { return true; }
}
"""
        },
        expected_solution={
            "python": """def is_same_tree(p: list, q: list) -> bool:
    return p == q
""",
            "c": """int isSameTree() { return 1; }
""",
            "cpp": """bool isSameTree() { return true; }
""",
            "java": """public class Solution {
    public static boolean isSameTree() { return true; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'p': [1, 2, 3], 'q': [1, 2, 3]}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'p': [1, 2], 'q': [1, None, 2]}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Structural & value tree isomorphism"
],
        common_misconceptions=[
            "Comparing values on null nodes"
],
        hint="""Traverse both trees simultaneously.""",
        source="curated",
        is_generated=False
    ),
    "path-sum": Problem(
        id="path-sum",
        title="Path Sum (Root-to-Leaf)",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="Path Sums",
        description="""Return `True` if tree has root-to-leaf path summing to `targetSum`.""",
        examples=[
            {
                        "input": "root = [1, 2, 3], targetSum = 3",
                        "output": "True"
            }
],
        constraints=[
            "Nodes 0 to 5000"
],
        starter_code={
            "python": """def has_path_sum(root: list, targetSum: int) -> bool:
    pass
""",
            "c": """int hasPathSum() { return 0; }
""",
            "cpp": """bool hasPathSum() { return false; }
""",
            "java": """public class Solution {
    public static boolean hasPathSum() { return false; }
}
"""
        },
        expected_solution={
            "python": """def has_path_sum(root: list, targetSum: int) -> bool:
    if not root or root[0] is None: return False
    def dfs(idx, rem):
        if idx >= len(root) or root[idx] is None: return False
        rem -= root[idx]
        l, r = 2 * idx + 1, 2 * idx + 2
        is_leaf = (l >= len(root) or root[l] is None) and (r >= len(root) or root[r] is None)
        if is_leaf: return rem == 0
        return dfs(l, rem) or dfs(r, rem)
    return dfs(0, targetSum)
""",
            "c": """int hasPathSum() { return 0; }
""",
            "cpp": """bool hasPathSum() { return false; }
""",
            "java": """public class Solution {
    public static boolean hasPathSum() { return false; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'root': [1, 2], 'targetSum': 3}, expected_output=True, is_hidden=False),
            TestCase(id=2, input={'root': [1, 2, 3], 'targetSum': 5}, expected_output=False, is_hidden=False)
        ],
        learning_objectives=[
            "Root to leaf path sum tracking"
],
        common_misconceptions=[
            "Stopping at non-leaf nodes"
],
        hint="""Subtract node val and check leaf == 0.""",
        source="curated",
        is_generated=False
    ),
    "range-sum-of-bst": Problem(
        id="range-sum-of-bst",
        title="Range Sum of BST",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="BST Properties",
        description="""Return sum of values of all nodes with value in inclusive range `[low, high]`.""",
        examples=[
            {
                        "input": "root = [10, 5, 15, 3, 7, null, 18], low = 7, high = 15",
                        "output": "32"
            }
],
        constraints=[
            "Node values distinct"
],
        starter_code={
            "python": """def range_sum_bst(root: list, low: int, high: int) -> int:
    pass
""",
            "c": """int rangeSumBST() { return 0; }
""",
            "cpp": """int rangeSumBST() { return 0; }
""",
            "java": """public class Solution {
    public static int rangeSumBST() { return 0; }
}
"""
        },
        expected_solution={
            "python": """def range_sum_bst(root: list, low: int, high: int) -> int:
    s = 0
    for x in root:
        if x is not None and low <= x <= high: s += x
    return s
""",
            "c": """int rangeSumBST() { return 0; }
""",
            "cpp": """int rangeSumBST() { return 0; }
""",
            "java": """public class Solution {
    public static int rangeSumBST() { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'root': [10, 5, 15, 3, 7, None, 18], 'low': 7, 'high': 15}, expected_output=32, is_hidden=False)
        ],
        learning_objectives=[
            "BST pruning based on low and high boundaries"
],
        common_misconceptions=[
            "Visiting branches out of range"
],
        hint="""Sum valid values within range.""",
        source="curated",
        is_generated=False
    ),
    "binary-tree-level-order-traversal": Problem(
        id="binary-tree-level-order-traversal",
        title="Binary Tree Level Order Traversal",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="BFS Level Order",
        description="""Return level order traversal of node values (left to right, level by level).""",
        examples=[
            {
                        "input": "root = [3, 9, 20, null, null, 15, 7]",
                        "output": "[[3], [9, 20], [15, 7]]"
            }
],
        constraints=[
            "0 to 2000 nodes"
],
        starter_code={
            "python": """def level_order(root: list) -> list:
    pass
""",
            "c": """void levelOrder() {}
""",
            "cpp": """vector<vector<int>> levelOrder() { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> levelOrder() { return new ArrayList<>(); }
}
"""
        },
        expected_solution={
            "python": """def level_order(root: list) -> list:
    if not root or root[0] is None: return []
    res, level, i = [], [0], 0
    while level:
        vals = [root[idx] for idx in level if idx < len(root) and root[idx] is not None]
        if vals: res.append(vals)
        nxt = []
        for idx in level:
            l, r = 2 * idx + 1, 2 * idx + 2
            if l < len(root) and root[l] is not None: nxt.append(l)
            if r < len(root) and root[r] is not None: nxt.append(r)
        level = nxt
    return res
""",
            "c": """void levelOrder() {}
""",
            "cpp": """vector<vector<int>> levelOrder() { return {}; }
""",
            "java": """public class Solution {
    public static List<List<Integer>> levelOrder() { return new ArrayList<>(); }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[3, 9, 20, None, None, 15, 7], expected_output=[[3], [9, 20], [15, 7]], is_hidden=False),
            TestCase(id=2, input=[1], expected_output=[[1]], is_hidden=False),
            TestCase(id=3, input=[], expected_output=[], is_hidden=False)
        ],
        learning_objectives=[
            "Queue-based BFS level grouping"
],
        common_misconceptions=[
            "Mixing nodes across levels"
],
        hint="""Process queue size elements per level.""",
        source="curated",
        is_generated=False
    ),
    "island-perimeter": Problem(
        id="island-perimeter",
        title="Island Perimeter",
        difficulty="Easy",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="""Calculate perimeter of an island in a grid where 1 is land and 0 is water.""",
        examples=[
            {
                        "input": "grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0],[1,1,0,0]]",
                        "output": "16"
            }
],
        constraints=[
            "1 <= m, n <= 100"
],
        starter_code={
            "python": """def island_perimeter(grid: list) -> int:
    pass
""",
            "c": """int islandPerimeter(int** g, int r, int* c) { return 0; }
""",
            "cpp": """int islandPerimeter(vector<vector<int>>& grid) { return 0; }
""",
            "java": """public class Solution {
    public static int islandPerimeter(int[][] grid) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def island_perimeter(grid: list) -> int:
    R, C = len(grid), len(grid[0])
    p = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 1:
                p += 4
                if r > 0 and grid[r - 1][c] == 1: p -= 2
                if c > 0 and grid[r][c - 1] == 1: p -= 2
    return p
""",
            "c": """int islandPerimeter(int** g, int r, int* c) { return 0; }
""",
            "cpp": """int islandPerimeter(vector<vector<int>>& grid) { return 0; }
""",
            "java": """public class Solution {
    public static int islandPerimeter(int[][] grid) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]], expected_output=16, is_hidden=False),
            TestCase(id=2, input=[[1]], expected_output=4, is_hidden=False)
        ],
        learning_objectives=[
            "Shared boundary subtraction 4 - 2*neighbors"
],
        common_misconceptions=[
            "Overcounting inner edges"
],
        hint="""+4 for each cell, -2 for each shared edge.""",
        source="curated",
        is_generated=False
    ),
    "rotting-oranges": Problem(
        id="rotting-oranges",
        title="Rotting Oranges (BFS Multi-Source)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="BFS / Shortest Path",
        description="""Return minimum minutes until all oranges rot, or -1 if impossible.""",
        examples=[
            {
                        "input": "grid = [[2,1,1],[1,1,0],[0,1,1]]",
                        "output": "4"
            }
],
        constraints=[
            "1 <= m, n <= 10"
],
        starter_code={
            "python": """def oranges_rotting(grid: list) -> int:
    pass
""",
            "c": """int orangesRotting() { return 0; }
""",
            "cpp": """int orangesRotting(vector<vector<int>>& grid) { return 0; }
""",
            "java": """public class Solution {
    public static int orangesRotting(int[][] grid) { return 0; }
}
"""
        },
        expected_solution={
            "python": """def oranges_rotting(grid: list) -> int:
    from collections import deque
    R, C = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 2: q.append((r, c, 0))
            elif grid[r][c] == 1: fresh += 1
    if fresh == 0: return 0
    mins = 0
    while q:
        r, c, m = q.popleft(); mins = max(mins, m)
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:
                grid[nr][nc] = 2; fresh -= 1; q.append((nr, nc, m + 1))
    return mins if fresh == 0 else -1
""",
            "c": """int orangesRotting() { return 0; }
""",
            "cpp": """int orangesRotting(vector<vector<int>>& grid) { return 0; }
""",
            "java": """public class Solution {
    public static int orangesRotting(int[][] grid) { return 0; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[[2, 1, 1], [1, 1, 0], [0, 1, 1]], expected_output=4, is_hidden=False),
            TestCase(id=2, input=[[2, 1, 1], [0, 1, 1], [1, 0, 1]], expected_output=-1, is_hidden=False)
        ],
        learning_objectives=[
            "Simultaneous multi-source BFS wave propagation"
],
        common_misconceptions=[
            "Starting independent BFS per rotten orange"
],
        hint="""Enque all rotten oranges at minute 0.""",
        source="curated",
        is_generated=False
    ),
    "clone-graph": Problem(
        id="clone-graph",
        title="Clone Graph (DFS Traversal)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="BFS / Shortest Path",
        description="""Return a deep copy clone of the connected undirected graph.""",
        examples=[
            {
                        "input": "adjList = [[2,4],[1,3],[2,4],[1,3]]",
                        "output": "[[2,4],[1,3],[2,4],[1,3]]"
            }
],
        constraints=[
            "0 <= nodes <= 100"
],
        starter_code={
            "python": """def clone_graph_adj(adjList: list) -> list:
    pass
""",
            "c": """void cloneGraph() {}
""",
            "cpp": """void cloneGraph() {}
""",
            "java": """public class Solution {
    public static void cloneGraph() {}
}
"""
        },
        expected_solution={
            "python": """def clone_graph_adj(adjList: list) -> list:
    if not adjList: return []
    return [list(n) for n in adjList]
""",
            "c": """void cloneGraph() {}
""",
            "cpp": """void cloneGraph() {}
""",
            "java": """public class Solution {
    public static void cloneGraph() {}
}
"""
        },
        test_cases=[
            TestCase(id=1, input=[[2, 4], [1, 3], [2, 4], [1, 3]], expected_output=[[2, 4], [1, 3], [2, 4], [1, 3]], is_hidden=False),
            TestCase(id=2, input=[], expected_output=[], is_hidden=False)
        ],
        learning_objectives=[
            "Visited map preventing infinite recursion on cycles"
],
        common_misconceptions=[
            "Shallow copying node pointers"
],
        hint="""Clone each node and save in hash map.""",
        source="curated",
        is_generated=False
    ),
    "course-schedule-ii": Problem(
        id="course-schedule-ii",
        title="Course Schedule II (Topological Sort)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="Topological Sort",
        description="""Return the ordering of courses you should take to finish all courses (Kahn's BFS).""",
        examples=[
            {
                        "input": "numCourses = 2, prerequisites = [[1, 0]]",
                        "output": "[0, 1]"
            }
],
        constraints=[
            "1 <= numCourses <= 2000"
],
        starter_code={
            "python": """def find_order(numCourses: int, prerequisites: list) -> list:
    pass
""",
            "c": """void findOrder() {}
""",
            "cpp": """vector<int> findOrder(int n, vector<vector<int>>& p) { return {}; }
""",
            "java": """public class Solution {
    public static int[] findOrder(int n, int[][] p) { return new int[0]; }
}
"""
        },
        expected_solution={
            "python": """def find_order(numCourses: int, prerequisites: list) -> list:
    from collections import deque
    adj = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for dest, src in prerequisites:
        adj[src].append(dest)
        indegree[dest] += 1
    q = deque([i for i in range(numCourses) if indegree[i] == 0])
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in adj[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0: q.append(nxt)
    return order if len(order) == numCourses else []
""",
            "c": """void findOrder() {}
""",
            "cpp": """vector<int> findOrder(int n, vector<vector<int>>& p) { return {}; }
""",
            "java": """public class Solution {
    public static int[] findOrder(int n, int[][] p) { return new int[0]; }
}
"""
        },
        test_cases=[
            TestCase(id=1, input={'numCourses': 2, 'prerequisites': [[1, 0]]}, expected_output=[0, 1], is_hidden=False),
            TestCase(id=2, input={'numCourses': 1, 'prerequisites': []}, expected_output=[0], is_hidden=False)
        ],
        learning_objectives=[
            "Kahn's algorithm in-degree topological order"
],
        common_misconceptions=[
            "Failing to detect cycles"
],
        hint="""Push 0 in-degree nodes into queue.""",
        source="curated",
        is_generated=False
    ),
}
