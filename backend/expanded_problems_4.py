from typing import Dict
from models import Problem, TestCase

EXPANDED_PROBLEMS_4: Dict[str, Problem] = {
    # =========================================================================
    # RECURSION & BACKTRACKING (5 problems)
    # =========================================================================
    "subsets-ii": Problem(
        id="subsets-ii",
        title="Subsets II (With Duplicates)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="Given an integer array `nums` that may contain duplicates, return all possible subsets. The solution set must not contain duplicate subsets.",
        examples=[{"input": "nums = [1, 2, 2]", "output": "[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]"}],
        constraints=["1 <= nums.length <= 10", "-10 <= nums[i] <= 10"],
        starter_code={
            "python": "def subsets_with_dup(nums: list) -> list:\n    pass\n",
            "c": "void subsetsWithDup() {}\n",
            "cpp": "vector<vector<int>> subsetsWithDup(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> subsetsWithDup(int[] nums) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def subsets_with_dup(nums: list) -> list:\n    nums.sort()\n    res = []\n    def bt(start, path):\n        res.append(list(path))\n        for i in range(start, len(nums)):\n            if i > start and nums[i] == nums[i - 1]: continue\n            path.append(nums[i])\n            bt(i + 1, path)\n            path.pop()\n    bt(0, [])\n    return res\n",
            "c": "void subsetsWithDup() {}\n",
            "cpp": "vector<vector<int>> subsetsWithDup(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> subsetsWithDup(int[] nums) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 2], expected_output=[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]),
            TestCase(id=2, input=[0], expected_output=[[], [0]])
        ],
        learning_objectives=["Duplicate branch pruning in recursive power sets"],
        common_misconceptions=["Pruning without sorting array first"],
        hint="Sort array first, then skip duplicates when i > start and nums[i] == nums[i - 1]."
    ),

    "combination-sum-ii": Problem(
        id="combination-sum-ii",
        title="Combination Sum II (Single Use Per Element)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="Given a collection of candidate numbers `candidates` and a target number `target`, find all unique combinations where candidate numbers sum to `target`. Each number may only be used once in the combination.",
        examples=[{"input": "candidates = [10, 1, 2, 7, 6, 1, 5], target = 8", "output": "[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]"}],
        constraints=["1 <= candidates.length <= 100", "1 <= target <= 30"],
        starter_code={
            "python": "def combination_sum_2(candidates: list, target: int) -> list:\n    pass\n",
            "c": "void combinationSum2() {}\n",
            "cpp": "vector<vector<int>> combinationSum2(vector<int>& c, int t) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> combinationSum2(int[] c, int t) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def combination_sum_2(candidates: list, target: int) -> list:\n    candidates.sort()\n    res = []\n    def bt(rem, start, path):\n        if rem == 0:\n            res.append(list(path))\n            return\n        for i in range(start, len(candidates)):\n            if candidates[i] > rem: break\n            if i > start and candidates[i] == candidates[i - 1]: continue\n            path.append(candidates[i])\n            bt(rem - candidates[i], i + 1, path)\n            path.pop()\n    bt(target, 0, [])\n    return res\n",
            "c": "void combinationSum2() {}\n",
            "cpp": "vector<vector<int>> combinationSum2(vector<int>& c, int t) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> combinationSum2(int[] c, int t) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"candidates": [10, 1, 2, 7, 6, 1, 5], "target": 8}, expected_output=[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]),
            TestCase(id=2, input={"candidates": [2, 5, 2, 1, 2], "target": 5}, expected_output=[[1, 2, 2], [5]])
        ],
        learning_objectives=["Single-use backtrack branch advancement and duplicate sibling skipping"],
        common_misconceptions=["Passing i instead of i + 1 when elements cannot be reused"],
        hint="Recurse with i + 1 and skip sibling duplicate candidates."
    ),

    "gray-code": Problem(
        id="gray-code",
        title="Gray Code (Reflected Binary Code)",
        difficulty="Medium",
        topic="Recursion & Backtracking",
        subtopic="Tree Recursion",
        description="An n-bit Gray code sequence is a sequence of 2^n integers where successive integers differ by exactly one bit. Given `n`, return any valid n-bit Gray code sequence.",
        examples=[{"input": "n = 2", "output": "[0, 1, 3, 2]"}, {"input": "n = 1", "output": "[0, 1]"}],
        constraints=["1 <= n <= 10"],
        starter_code={
            "python": "def gray_code(n: int) -> list:\n    pass\n",
            "c": "void grayCode() {}\n",
            "cpp": "vector<int> grayCode(int n) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> grayCode(int n) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def gray_code(n: int) -> list:\n    return [i ^ (i >> 1) for i in range(1 << n)]\n",
            "c": "void grayCode() {}\n",
            "cpp": "vector<int> grayCode(int n) { vector<int> res; for(int i=0;i<(1<<n);i++) res.push_back(i^(i>>1)); return res; }\n",
            "java": "public class Solution { public static List<Integer> grayCode(int n) { List<Integer> res = new ArrayList<>(); for(int i=0;i<(1<<n);i++) res.add(i^(i>>1)); return res; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=2, expected_output=[0, 1, 3, 2]),
            TestCase(id=2, input=1, expected_output=[0, 1])
        ],
        learning_objectives=["Binary reflected Gray code formula i ^ (i >> 1)"],
        common_misconceptions=["Generating in arbitrary order without single-bit difference"],
        hint="Formula for i-th Gray code is i ^ (i >> 1)."
    ),

    "expression-add-operators": Problem(
        id="expression-add-operators",
        title="Expression Add Operators",
        difficulty="Hard",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="Given a string `num` that contains only digits and an integer `target`, return all possibilities to insert binary operators `+`, `-`, and/or `*` between the digits of `num` so that the resultant expression evaluates to the `target` value.",
        examples=[{"input": "num = '123', target = 6", "output": "['1*2*3', '1+2+3']"}, {"input": "num = '232', target = 8", "output": "['2*3+2', '2+3*2']"}],
        constraints=["1 <= num.length <= 10", "-2^31 <= target <= 2^31 - 1"],
        starter_code={
            "python": "def add_operators(num: str, target: int) -> list:\n    pass\n",
            "c": "void addOperators() {}\n",
            "cpp": "vector<string> addOperators(string num, int target) { return {}; }\n",
            "java": "public class Solution { public static List<String> addOperators(String num, int target) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def add_operators(num: str, target: int) -> list:\n    res = []\n    def bt(idx, expr, val, prev):\n        if idx == len(num):\n            if val == target: res.append(expr)\n            return\n        for j in range(idx + 1, len(num) + 1):\n            sub = num[idx:j]\n            if len(sub) > 1 and sub[0] == '0': break\n            n = int(sub)\n            if idx == 0:\n                bt(j, sub, n, n)\n            else:\n                bt(j, expr + '+' + sub, val + n, n)\n                bt(j, expr + '-' + sub, val - n, -n)\n                bt(j, expr + '*' + sub, val - prev + prev * n, prev * n)\n    bt(0, '', 0, 0)\n    return sorted(res)\n",
            "c": "void addOperators() {}\n",
            "cpp": "vector<string> addOperators(string num, int target) { return {}; }\n",
            "java": "public class Solution { public static List<String> addOperators(String num, int target) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"num": "123", "target": 6}, expected_output=["1*2*3", "1+2+3"]),
            TestCase(id=2, input={"num": "232", "target": 8}, expected_output=["2*3+2", "2+3*2"])
        ],
        learning_objectives=["Multiplication operator precedence tracking with rollback (val - prev + prev * n)"],
        common_misconceptions=["Leading zeros forming multi-digit numbers (like '05')"],
        hint="Track previous operand to handle multiplication precedence."
    ),

    "palindrome-partitioning-ii": Problem(
        id="palindrome-partitioning-ii",
        title="Palindrome Partitioning II (Minimum Cuts)",
        difficulty="Hard",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="Given a string `s`, partition `s` such that every substring of the partition is a palindrome. Return the minimum cuts needed for a palindrome partitioning of `s`.",
        examples=[{"input": "s = 'aab'", "output": "1", "explanation": "The palindrome partitioning ['aa','b'] could be produced using 1 cut."}, {"input": "s = 'a'", "output": "0"}],
        constraints=["1 <= s.length <= 2000"],
        starter_code={
            "python": "def min_cut(s: str) -> int:\n    pass\n",
            "c": "int minCut(char* s) { return 0; }\n",
            "cpp": "int minCut(string s) { return 0; }\n",
            "java": "public class Solution { public static int minCut(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def min_cut(s: str) -> int:\n    n = len(s)\n    cuts = list(range(-1, n))\n    for i in range(n):\n        r1, r2 = 0, 0\n        while i - r1 >= 0 and i + r1 < n and s[i - r1] == s[i + r1]:\n            cuts[i + r1 + 1] = min(cuts[i + r1 + 1], cuts[i - r1] + 1)\n            r1 += 1\n        while i - 1 - r2 >= 0 and i + r2 < n and s[i - 1 - r2] == s[i + r2]:\n            cuts[i + r2 + 1] = min(cuts[i + r2 + 1], cuts[i - 1 - r2] + 1)\n            r2 += 1\n    return cuts[n]\n",
            "c": "int minCut(char* s) { return 0; }\n",
            "cpp": "int minCut(string s) { return 0; }\n",
            "java": "public class Solution { public static int minCut(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="aab", expected_output=1),
            TestCase(id=2, input="a", expected_output=0),
            TestCase(id=3, input="ab", expected_output=1)
        ],
        learning_objectives=["Expanding palindrome centers combined with 1D DP minimum cut minimization"],
        common_misconceptions=["Exponential brute-force partition generation"],
        hint="Expand around centers and update cuts[end + 1] = min(cuts[end + 1], cuts[start] + 1)."
    ),

    # =========================================================================
    # ARRAYS & HASHING (5 problems)
    # =========================================================================
    "plus-one": Problem(
        id="plus-one",
        title="Plus One (Large Integer Addition)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="You are given a large integer represented as an integer array `digits`. Increment the large integer by one and return the resulting array of digits.",
        examples=[{"input": "digits = [1, 2, 3]", "output": "[1, 2, 4]"}, {"input": "digits = [9]", "output": "[1, 0]"}],
        constraints=["1 <= digits.length <= 100", "0 <= digits[i] <= 9"],
        starter_code={
            "python": "def plus_one(digits: list) -> list:\n    pass\n",
            "c": "void plusOne() {}\n",
            "cpp": "vector<int> plusOne(vector<int>& digits) { return digits; }\n",
            "java": "public class Solution { public static int[] plusOne(int[] digits) { return digits; } }\n"
        },
        expected_solution={
            "python": "def plus_one(digits: list) -> list:\n    for i in range(len(digits) - 1, -1, -1):\n        if digits[i] < 9:\n            digits[i] += 1\n            return digits\n        digits[i] = 0\n    return [1] + digits\n",
            "c": "void plusOne() {}\n",
            "cpp": "vector<int> plusOne(vector<int>& digits) { for(int i=digits.size()-1;i>=0;i--){ if(digits[i]<9){ digits[i]++; return digits; } digits[i]=0; } digits.insert(digits.begin(), 1); return digits; }\n",
            "java": "public class Solution { public static int[] plusOne(int[] digits) { for(int i=digits.length-1;i>=0;i--){ if(digits[i]<9){ digits[i]++; return digits; } digits[i]=0; } int[] r=new int[digits.length+1]; r[0]=1; return r; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 3], expected_output=[1, 2, 4]),
            TestCase(id=2, input=[4, 3, 2, 1], expected_output=[4, 3, 2, 2]),
            TestCase(id=3, input=[9], expected_output=[1, 0])
        ],
        learning_objectives=["Reverse digit iteration with carry propagation"],
        common_misconceptions=["Converting to integer directly fails on arbitrarily large digit arrays"],
        hint="Loop backwards: if digit < 9 add 1 and return; otherwise set to 0. If all 9s, prepend 1."
    ),

    "set-mismatch": Problem(
        id="set-mismatch",
        title="Set Mismatch (Find Duplicate and Missing)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Frequency Counting",
        description="You have a set of integers `[1, n]`. One number got duplicated to another number in the set. Find and return the number that occurs twice and the number that is missing as `[duplicate, missing]`.",
        examples=[{"input": "nums = [1, 2, 2, 4]", "output": "[2, 3]"}, {"input": "nums = [1, 1]", "output": "[1, 2]"}],
        constraints=["2 <= nums.length <= 10^4", "1 <= nums[i] <= n"],
        starter_code={
            "python": "def find_error_nums(nums: list) -> list:\n    pass\n",
            "c": "void findErrorNums() {}\n",
            "cpp": "vector<int> findErrorNums(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static int[] findErrorNums(int[] nums) { return new int[0]; } }\n"
        },
        expected_solution={
            "python": "def find_error_nums(nums: list) -> list:\n    n = len(nums)\n    exp_sum = n * (n + 1) // 2\n    actual_sum = sum(nums)\n    unique_sum = sum(set(nums))\n    dup = actual_sum - unique_sum\n    missing = exp_sum - unique_sum\n    return [dup, missing]\n",
            "c": "void findErrorNums() {}\n",
            "cpp": "vector<int> findErrorNums(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static int[] findErrorNums(int[] nums) { return new int[0]; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 2, 4], expected_output=[2, 3]),
            TestCase(id=2, input=[1, 1], expected_output=[1, 2])
        ],
        learning_objectives=["Mathematical deduction using set sums vs array sums"],
        common_misconceptions=["O(N^2) search or sorting overhead"],
        hint="duplicate = sum(nums) - sum(set(nums)); missing = expected_sum - sum(set(nums))."
    ),

    "can-place-flowers": Problem(
        id="can-place-flowers",
        title="Can Place Flowers (No-Adjacent Greedy)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="You have a long flowerbed in which some plots are planted (1) and some are empty (0). Flowers cannot be planted in adjacent plots. Return `True` if `n` new flowers can be planted without violating the no-adjacent rule.",
        examples=[{"input": "flowerbed = [1, 0, 0, 0, 1], n = 1", "output": "True"}, {"input": "flowerbed = [1, 0, 0, 0, 1], n = 2", "output": "False"}],
        constraints=["1 <= flowerbed.length <= 2 * 10^4", "0 <= n <= flowerbed.length"],
        starter_code={
            "python": "def can_place_flowers(flowerbed: list, n: int) -> bool:\n    pass\n",
            "c": "int canPlaceFlowers() { return 0; }\n",
            "cpp": "bool canPlaceFlowers(vector<int>& f, int n) { return false; }\n",
            "java": "public class Solution { public static boolean canPlaceFlowers(int[] f, int n) { return false; } }\n"
        },
        expected_solution={
            "python": "def can_place_flowers(flowerbed: list, n: int) -> bool:\n    count = 0\n    for i in range(len(flowerbed)):\n        if flowerbed[i] == 0:\n            empty_left = (i == 0 or flowerbed[i - 1] == 0)\n            empty_right = (i == len(flowerbed) - 1 or flowerbed[i + 1] == 0)\n            if empty_left and empty_right:\n                flowerbed[i] = 1\n                count += 1\n    return count >= n\n",
            "c": "int canPlaceFlowers() { return 0; }\n",
            "cpp": "bool canPlaceFlowers(vector<int>& f, int n) { return false; }\n",
            "java": "public class Solution { public static boolean canPlaceFlowers(int[] f, int n) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"flowerbed": [1, 0, 0, 0, 1], "n": 1}, expected_output=True),
            TestCase(id=2, input={"flowerbed": [1, 0, 0, 0, 1], "n": 2}, expected_output=False),
            TestCase(id=3, input={"flowerbed": [0, 0, 1, 0, 0], "n": 2}, expected_output=True)
        ],
        learning_objectives=["Greedy placement with boundary conditions"],
        common_misconceptions=["Index error on checking left or right of endpoints"],
        hint="Plot i can take a flower if flowerbed[i]==0 and both neighbors (or boundaries) are 0."
    ),

    "continuous-subarray-sum": Problem(
        id="continuous-subarray-sum",
        title="Continuous Subarray Sum (Modulo K)",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Prefix Sums",
        description="Given an integer array `nums` and an integer `k`, return `True` if `nums` has a good subarray of length at least two whose elements sum up to a multiple of `k`.",
        examples=[{"input": "nums = [23, 2, 4, 6, 7], k = 6", "output": "True"}, {"input": "nums = [23, 2, 6, 4, 7], k = 6", "output": "True"}, {"input": "nums = [23, 2, 6, 4, 7], k = 13", "output": "False"}],
        constraints=["1 <= nums.length <= 10^5", "1 <= k <= 2^31 - 1"],
        starter_code={
            "python": "def check_subarray_sum(nums: list, k: int) -> bool:\n    pass\n",
            "c": "int checkSubarraySum() { return 0; }\n",
            "cpp": "bool checkSubarraySum(vector<int>& nums, int k) { return false; }\n",
            "java": "public class Solution { public static boolean checkSubarraySum(int[] nums, int k) { return false; } }\n"
        },
        expected_solution={
            "python": "def check_subarray_sum(nums: list, k: int) -> bool:\n    rem_map = {0: -1}\n    curr = 0\n    for i, x in enumerate(nums):\n        curr += x\n        rem = curr % k\n        if rem in rem_map:\n            if i - rem_map[rem] >= 2:\n                return True\n        else:\n            rem_map[rem] = i\n    return False\n",
            "c": "int checkSubarraySum() { return 0; }\n",
            "cpp": "bool checkSubarraySum(vector<int>& nums, int k) { return false; }\n",
            "java": "public class Solution { public static boolean checkSubarraySum(int[] nums, int k) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [23, 2, 4, 6, 7], "k": 6}, expected_output=True),
            TestCase(id=2, input={"nums": [23, 2, 6, 4, 7], "k": 6}, expected_output=True),
            TestCase(id=3, input={"nums": [23, 2, 6, 4, 7], "k": 13}, expected_output=False)
        ],
        learning_objectives=["Prefix sum remainder modulo hash map with minimum length constraint"],
        common_misconceptions=["Overwriting the earliest index of remainder in map"],
        hint="Store the earliest index of remainder: if same remainder seen with index difference >= 2, return True."
    ),

    "max-chunks-to-make-sorted": Problem(
        id="max-chunks-to-make-sorted",
        title="Max Chunks To Make Sorted",
        difficulty="Medium",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="You are given an integer array `arr` of length `n` that represents a permutation of the integers in the range `[0, n - 1]`. Split the array into the maximum number of chunks such that sorting each chunk individually sorts the entire array.",
        examples=[{"input": "arr = [4, 3, 2, 1, 0]", "output": "1"}, {"input": "arr = [1, 0, 2, 3, 4]", "output": "4"}],
        constraints=["n == arr.length", "1 <= n <= 10"],
        starter_code={
            "python": "def max_chunks_to_sorted(arr: list) -> int:\n    pass\n",
            "c": "int maxChunksToSorted() { return 0; }\n",
            "cpp": "int maxChunksToSorted(vector<int>& arr) { return 0; }\n",
            "java": "public class Solution { public static int maxChunksToSorted(int[] arr) { return 0; } }\n"
        },
        expected_solution={
            "python": "def max_chunks_to_sorted(arr: list) -> int:\n    chunks = 0\n    max_seen = 0\n    for i, x in enumerate(arr):\n        max_seen = max(max_seen, x)\n        if max_seen == i:\n            chunks += 1\n    return chunks\n",
            "c": "int maxChunksToSorted() { return 0; }\n",
            "cpp": "int maxChunksToSorted(vector<int>& arr) { return 0; }\n",
            "java": "public class Solution { public static int maxChunksToSorted(int[] arr) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[4, 3, 2, 1, 0], expected_output=1),
            TestCase(id=2, input=[1, 0, 2, 3, 4], expected_output=4)
        ],
        learning_objectives=["Prefix maximum index alignment chunk invariant"],
        common_misconceptions=["Trying sorting permutations instead of prefix max check"],
        hint="When max_seen == current_index, all elements up to i belong in this sorted chunk."
    ),

    # =========================================================================
    # STRINGS (5 problems)
    # =========================================================================
    "repeated-substring-pattern": Problem(
        id="repeated-substring-pattern",
        title="Repeated Substring Pattern",
        difficulty="Easy",
        topic="Strings",
        subtopic="Pattern Matching",
        description="Given a string `s`, check if it can be constructed by taking a substring of it and appending multiple copies of the substring together.",
        examples=[{"input": "s = 'abab'", "output": "True"}, {"input": "s = 'aba'", "output": "False"}, {"input": "s = 'abcabcabcabc'", "output": "True"}],
        constraints=["1 <= s.length <= 10^4"],
        starter_code={
            "python": "def repeated_substring_pattern(s: str) -> bool:\n    pass\n",
            "c": "int repeatedSubstringPattern(char* s) { return 0; }\n",
            "cpp": "bool repeatedSubstringPattern(string s) { return false; }\n",
            "java": "public class Solution { public static boolean repeatedSubstringPattern(String s) { return false; } }\n"
        },
        expected_solution={
            "python": "def repeated_substring_pattern(s: str) -> bool:\n    return s in (s + s)[1:-1]\n",
            "c": "int repeatedSubstringPattern(char* s) { return 0; }\n",
            "cpp": "bool repeatedSubstringPattern(string s) { return (s + s).substr(1, 2 * s.size() - 2).find(s) != string::npos; }\n",
            "java": "public class Solution { public static boolean repeatedSubstringPattern(String s) { return (s + s).substring(1, 2 * s.length() - 1).contains(s); } }\n"
        },
        test_cases=[
            TestCase(id=1, input="abab", expected_output=True),
            TestCase(id=2, input="aba", expected_output=False),
            TestCase(id=3, input="abcabcabcabc", expected_output=True)
        ],
        learning_objectives=["String periodicity string doubling trick (s in (s+s)[1:-1])"],
        common_misconceptions=["Checking only even-length prefixes"],
        hint="If s is periodic, it appears in (s + s) without the first and last characters."
    ),

    "palindromic-substrings": Problem(
        id="palindromic-substrings",
        title="Palindromic Substrings Count",
        difficulty="Medium",
        topic="Strings",
        subtopic="Pattern Matching",
        description="Given a string `s`, return the number of palindromic substrings in it. A substring with different start or end indices is counted separately.",
        examples=[{"input": "s = 'abc'", "output": "3", "explanation": "Three palindromic strings: 'a', 'b', 'c'."}, {"input": "s = 'aaa'", "output": "6"}],
        constraints=["1 <= s.length <= 1000"],
        starter_code={
            "python": "def count_substrings(s: str) -> int:\n    pass\n",
            "c": "int countSubstrings(char* s) { return 0; }\n",
            "cpp": "int countSubstrings(string s) { return 0; }\n",
            "java": "public class Solution { public static int countSubstrings(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def count_substrings(s: str) -> int:\n    count = 0\n    def expand(l, r):\n        nonlocal count\n        while l >= 0 and r < len(s) and s[l] == s[r]:\n            count += 1\n            l -= 1\n            r += 1\n    for i in range(len(s)):\n        expand(i, i)\n        expand(i, i + 1)\n    return count\n",
            "c": "int countSubstrings(char* s) { return 0; }\n",
            "cpp": "int countSubstrings(string s) { return 0; }\n",
            "java": "public class Solution { public static int countSubstrings(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="abc", expected_output=3),
            TestCase(id=2, input="aaa", expected_output=6)
        ],
        learning_objectives=["Center expansion technique for odd and even palindrome lengths"],
        common_misconceptions=["O(N^3) brute force substring checking"],
        hint="Expand around all 2N - 1 centers counting valid extensions."
    ),

    "longest-repeating-character-replacement": Problem(
        id="longest-repeating-character-replacement",
        title="Longest Repeating Character Replacement",
        difficulty="Medium",
        topic="Strings",
        subtopic="Sliding Window",
        description="You are given a string `s` and an integer `k`. You can choose any character of the string and change it to any other uppercase English character at most `k` times. Return length of longest substring with same letter.",
        examples=[{"input": "s = 'ABAB', k = 2", "output": "4"}, {"input": "s = 'AABABBA', k = 1", "output": "4"}],
        constraints=["1 <= s.length <= 10^5", "0 <= k <= s.length"],
        starter_code={
            "python": "def character_replacement(s: str, k: int) -> int:\n    pass\n",
            "c": "int characterReplacement() { return 0; }\n",
            "cpp": "int characterReplacement(string s, int k) { return 0; }\n",
            "java": "public class Solution { public static int characterReplacement(String s, int k) { return 0; } }\n"
        },
        expected_solution={
            "python": "def character_replacement(s: str, k: int) -> int:\n    count = {}\n    max_f = 0\n    l = 0\n    for r in range(len(s)):\n        count[s[r]] = count.get(s[r], 0) + 1\n        max_f = max(max_f, count[s[r]])\n        if (r - l + 1) - max_f > k:\n            count[s[l]] -= 1\n            l += 1\n    return len(s) - l\n",
            "c": "int characterReplacement() { return 0; }\n",
            "cpp": "int characterReplacement(string s, int k) { return 0; }\n",
            "java": "public class Solution { public static int characterReplacement(String s, int k) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"s": "ABAB", "k": 2}, expected_output=4),
            TestCase(id=2, input={"s": "AABABBA", "k": 1}, expected_output=4)
        ],
        learning_objectives=["Sliding window with frequency tracking where window_size - max_freq <= k"],
        common_misconceptions=["Recalculating max_f on every left window contraction"],
        hint="Window is valid if (window_length - max_freq) <= k."
    ),

    "valid-parentheses-string": Problem(
        id="valid-parentheses-string",
        title="Valid Parentheses String (Wildcard '*')",
        difficulty="Medium",
        topic="Strings",
        subtopic="Sliding Window",
        description="Given a string `s` containing only '(', ')' and '*', return `True` if `s` is valid. '*' can be treated as '(', ')' or an empty string.",
        examples=[{"input": "s = '()'", "output": "True"}, {"input": "s = '(*)'", "output": "True"}, {"input": "s = '(*))'", "output": "True"}],
        constraints=["1 <= s.length <= 100"],
        starter_code={
            "python": "def check_valid_string(s: str) -> bool:\n    pass\n",
            "c": "int checkValidString(char* s) { return 0; }\n",
            "cpp": "bool checkValidString(string s) { return false; }\n",
            "java": "public class Solution { public static boolean checkValidString(String s) { return false; } }\n"
        },
        expected_solution={
            "python": "def check_valid_string(s: str) -> bool:\n    cmin, cmax = 0, 0\n    for ch in s:\n        if ch == '(':\n            cmin += 1\n            cmax += 1\n        elif ch == ')':\n            cmin = max(0, cmin - 1)\n            cmax -= 1\n            if cmax < 0: return False\n        else:\n            cmin = max(0, cmin - 1)\n            cmax += 1\n    return cmin == 0\n",
            "c": "int checkValidString(char* s) { return 0; }\n",
            "cpp": "bool checkValidString(string s) { return false; }\n",
            "java": "public class Solution { public static boolean checkValidString(String s) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="()", expected_output=True),
            TestCase(id=2, input="(*)", expected_output=True),
            TestCase(id=3, input="(*))", expected_output=True)
        ],
        learning_objectives=["Min/Max open bracket range tracking across wildcards"],
        common_misconceptions=["Treating '*' strictly as '(' or ')' greedily"],
        hint="Maintain range [cmin, cmax] of possible unmatched open brackets."
    ),

    "text-justification": Problem(
        id="text-justification",
        title="Text Justification (Full Justification)",
        difficulty="Hard",
        topic="Strings",
        subtopic="String Manipulation",
        description="Format given list of words such that each line has exactly `maxWidth` characters and is fully (left and right) justified. Pad spaces evenly; extra spaces distribute left-to-right. Last line is left-justified.",
        examples=[{"input": "words = ['This', 'is', 'an', 'example', 'of', 'text', 'justification.'], maxWidth = 16", "output": "['This    is    an', 'example  of text', 'justification.  ']"}],
        constraints=["1 <= words.length <= 300", "1 <= maxWidth <= 100"],
        starter_code={
            "python": "def full_justify(words: list, maxWidth: int) -> list:\n    pass\n",
            "c": "void fullJustify() {}\n",
            "cpp": "vector<string> fullJustify(vector<string>& w, int m) { return {}; }\n",
            "java": "public class Solution { public static List<String> fullJustify(String[] w, int m) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def full_justify(words: list, maxWidth: int) -> list:\n    res, cur, num_letters = [], [], 0\n    for w in words:\n        if num_letters + len(w) + len(cur) > maxWidth:\n            for i in range(maxWidth - num_letters):\n                cur[i % (len(cur) - 1 or 1)] += ' '\n            res.append(''.join(cur))\n            cur, num_letters = [], 0\n        cur.append(w)\n        num_letters += len(w)\n    return res + [' '.join(cur).ljust(maxWidth)]\n",
            "c": "void fullJustify() {}\n",
            "cpp": "vector<string> fullJustify(vector<string>& w, int m) { return {}; }\n",
            "java": "public class Solution { public static List<String> fullJustify(String[] w, int m) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"words": ["This", "is", "an", "example", "of", "text", "justification."], "maxWidth": 16}, expected_output=["This    is    an", "example  of text", "justification.  "]),
            TestCase(id=2, input={"words": ["What", "must", "be", "acknowledgment", "shall", "be"], "maxWidth": 16}, expected_output=["What   must   be", "acknowledgment  ", "shall be        "])
        ],
        learning_objectives=["Complex greedy line packing and modulo space distribution"],
        common_misconceptions=["Single word lines dividing by zero"],
        hint="Distribute (maxWidth - num_letters) spaces using round-robin modulo."
    ),

    # =========================================================================
    # DYNAMIC PROGRAMMING (5 problems)
    # =========================================================================
    "longest-common-subsequence": Problem(
        id="longest-common-subsequence",
        title="Longest Common Subsequence",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="2D Grid DP",
        description="Given two strings `text1` and `text2`, return the length of their longest common subsequence. If there is no common subsequence, return 0.",
        examples=[{"input": "text1 = 'abcde', text2 = 'ace'", "output": "3", "explanation": "The longest common subsequence is 'ace' with length 3."}, {"input": "text1 = 'abc', text2 = 'def'", "output": "0"}],
        constraints=["1 <= text1.length, text2.length <= 1000"],
        starter_code={
            "python": "def longest_common_subsequence(text1: str, text2: str) -> int:\n    pass\n",
            "c": "int longestCommonSubsequence(char* t1, char* t2) { return 0; }\n",
            "cpp": "int longestCommonSubsequence(string t1, string t2) { return 0; }\n",
            "java": "public class Solution { public static int longestCommonSubsequence(String t1, String t2) { return 0; } }\n"
        },
        expected_solution={
            "python": "def longest_common_subsequence(text1: str, text2: str) -> int:\n    dp = [0] * (len(text2) + 1)\n    for c1 in text1:\n        prev = 0\n        for j, c2 in enumerate(text2):\n            tmp = dp[j + 1]\n            if c1 == c2:\n                dp[j + 1] = prev + 1\n            else:\n                dp[j + 1] = max(dp[j + 1], dp[j])\n            prev = tmp\n    return dp[-1]\n",
            "c": "int longestCommonSubsequence(char* t1, char* t2) { return 0; }\n",
            "cpp": "int longestCommonSubsequence(string t1, string t2) { return 0; }\n",
            "java": "public class Solution { public static int longestCommonSubsequence(String t1, String t2) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"text1": "abcde", "text2": "ace"}, expected_output=3),
            TestCase(id=2, input={"text1": "abc", "text2": "abc"}, expected_output=3),
            TestCase(id=3, input={"text1": "abc", "text2": "def"}, expected_output=0)
        ],
        learning_objectives=["Classic 2D table state matching: 1 + diag if equal, else max(up, left)"],
        common_misconceptions=["Confusing subsequence with substring"],
        hint="If text1[i] == text2[j], dp[i][j] = 1 + dp[i-1][j-1]; else max(dp[i-1][j], dp[i][j-1])."
    ),

    "target-sum": Problem(
        id="target-sum",
        title="Target Sum (Knapsack DP)",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="Knapsack & Subsets",
        description="You are given an integer array `nums` and an integer `target`. Build an expression out of nums by adding '+' or '-' before each integer. Return the number of different expressions that evaluate to `target`.",
        examples=[{"input": "nums = [1, 1, 1, 1, 1], target = 3", "output": "5"}, {"input": "nums = [1], target = 1", "output": "1"}],
        constraints=["1 <= nums.length <= 20", "0 <= nums[i] <= 1000", "-1000 <= target <= 1000"],
        starter_code={
            "python": "def find_target_sum_ways(nums: list, target: int) -> int:\n    pass\n",
            "c": "int findTargetSumWays() { return 0; }\n",
            "cpp": "int findTargetSumWays(vector<int>& nums, int target) { return 0; }\n",
            "java": "public class Solution { public static int findTargetSumWays(int[] nums, int target) { return 0; } }\n"
        },
        expected_solution={
            "python": "def find_target_sum_ways(nums: list, target: int) -> int:\n    total = sum(nums)\n    if (total + target) % 2 != 0 or abs(target) > total:\n        return 0\n    s1 = (total + target) // 2\n    dp = [0] * (s1 + 1)\n    dp[0] = 1\n    for num in nums:\n        for j in range(s1, num - 1, -1):\n            dp[j] += dp[j - num]\n    return dp[s1]\n",
            "c": "int findTargetSumWays() { return 0; }\n",
            "cpp": "int findTargetSumWays(vector<int>& nums, int target) { return 0; }\n",
            "java": "public class Solution { public static int findTargetSumWays(int[] nums, int target) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [1, 1, 1, 1, 1], "target": 3}, expected_output=5),
            TestCase(id=2, input={"nums": [1], "target": 1}, expected_output=1)
        ],
        learning_objectives=["Reduction of signed sum to subset sum S1 = (total + target) // 2"],
        common_misconceptions=["O(2^N) exponential branching without memoization"],
        hint="Subset sum reduction: find subset summing to (total + target) // 2."
    ),

    "maximum-product-subarray": Problem(
        id="maximum-product-subarray",
        title="Maximum Product Subarray",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="Given an integer array `nums`, find a subarray that has the largest product, and return the product.",
        examples=[{"input": "nums = [2, 3, -2, 4]", "output": "6"}, {"input": "nums = [-2, 0, -1]", "output": "0"}],
        constraints=["1 <= nums.length <= 2 * 10^4", "-10 <= nums[i] <= 10"],
        starter_code={
            "python": "def max_product(nums: list) -> int:\n    pass\n",
            "c": "int maxProduct(int* nums, int n) { return 0; }\n",
            "cpp": "int maxProduct(vector<int>& nums) { return 0; }\n",
            "java": "public class Solution { public static int maxProduct(int[] nums) { return 0; } }\n"
        },
        expected_solution={
            "python": "def max_product(nums: list) -> int:\n    cur_max, cur_min = 1, 1\n    res = max(nums)\n    for n in nums:\n        vals = (n, cur_max * n, cur_min * n)\n        cur_max = max(vals)\n        cur_min = min(vals)\n        res = max(res, cur_max)\n    return res\n",
            "c": "int maxProduct(int* nums, int n) { return 0; }\n",
            "cpp": "int maxProduct(vector<int>& nums) { return 0; }\n",
            "java": "public class Solution { public static int maxProduct(int[] nums) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[2, 3, -2, 4], expected_output=6),
            TestCase(id=2, input=[-2, 0, -1], expected_output=0),
            TestCase(id=3, input=[-2, 3, -4], expected_output=24)
        ],
        learning_objectives=["Tracking both min and max products because negative numbers flip signs"],
        common_misconceptions=["Discarding negative products (two negatives multiply to positive)"],
        hint="Keep track of both cur_max and cur_min at every element."
    ),

    "dungeon-game": Problem(
        id="dungeon-game",
        title="Dungeon Game (Knight Rescue)",
        difficulty="Hard",
        topic="Dynamic Programming",
        subtopic="2D Grid DP",
        description="The demons captured the princess in dungeon grid. Return the knight's minimum initial health so that he can rescue the princess at bottom-right.",
        examples=[{"input": "dungeon = [[-2,-3,3],[-5,-10,1],[10,30,-5]]", "output": "7"}],
        constraints=["1 <= m, n <= 200"],
        starter_code={
            "python": "def calculate_minimum_hp(dungeon: list) -> int:\n    pass\n",
            "c": "int calculateMinimumHP() { return 1; }\n",
            "cpp": "int calculateMinimumHP(vector<vector<int>>& d) { return 1; }\n",
            "java": "public class Solution { public static int calculateMinimumHP(int[][] d) { return 1; } }\n"
        },
        expected_solution={
            "python": "def calculate_minimum_hp(dungeon: list) -> int:\n    R, C = len(dungeon), len(dungeon[0])\n    dp = [[float('inf')] * (C + 1) for _ in range(R + 1)]\n    dp[R][C - 1] = 1\n    dp[R - 1][C] = 1\n    for r in range(R - 1, -1, -1):\n        for c in range(C - 1, -1, -1):\n            need = min(dp[r + 1][c], dp[r][c + 1]) - dungeon[r][c]\n            dp[r][c] = 1 if need <= 0 else need\n    return dp[0][0]\n",
            "c": "int calculateMinimumHP() { return 1; }\n",
            "cpp": "int calculateMinimumHP(vector<vector<int>>& d) { return 1; }\n",
            "java": "public class Solution { public static int calculateMinimumHP(int[][] d) { return 1; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[-2, -3, 3], [-5, -10, 1], [10, 30, -5]], expected_output=7),
            TestCase(id=2, input=[[0]], expected_output=1)
        ],
        learning_objectives=["Backward bottom-right to top-left health necessity DP"],
        common_misconceptions=["Forward DP from top-left doesn't guarantee path feasibility"],
        hint="Compute required health starting from destination backwards to entrance."
    ),

    "russian-doll-envelopes": Problem(
        id="russian-doll-envelopes",
        title="Russian Doll Envelopes",
        difficulty="Hard",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="Given 2D array `envelopes` where `envelopes[i] = [wi, hi]`. Envelope can fit into another iff both width and height are strictly greater. Return maximum number of envelopes you can Russian doll.",
        examples=[{"input": "envelopes = [[5,4],[6,4],[6,7],[2,3]]", "output": "3", "explanation": "[2,3] => [5,4] => [6,7]"}],
        constraints=["1 <= envelopes.length <= 10^5"],
        starter_code={
            "python": "def max_envelopes(envelopes: list) -> int:\n    pass\n",
            "c": "int maxEnvelopes() { return 0; }\n",
            "cpp": "int maxEnvelopes(vector<vector<int>>& e) { return 0; }\n",
            "java": "public class Solution { public static int maxEnvelopes(int[][] e) { return 0; } }\n"
        },
        expected_solution={
            "python": "def max_envelopes(envelopes: list) -> int:\n    import bisect\n    envelopes.sort(key=lambda x: (x[0], -x[1]))\n    tails = []\n    for _, h in envelopes:\n        idx = bisect.bisect_left(tails, h)\n        if idx == len(tails): tails.append(h)\n        else: tails[idx] = h\n    return len(tails)\n",
            "c": "int maxEnvelopes() { return 0; }\n",
            "cpp": "int maxEnvelopes(vector<vector<int>>& e) { return 0; }\n",
            "java": "public class Solution { public static int maxEnvelopes(int[][] e) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[5, 4], [6, 4], [6, 7], [2, 3]], expected_output=3),
            TestCase(id=2, input=[[1, 1], [1, 1], [1, 1]], expected_output=1)
        ],
        learning_objectives=["2D sort trick (asc width, desc height) reducing to 1D LIS in O(N log N)"],
        common_misconceptions=["Sorting both width and height ascending allows same width nesting"],
        hint="Sort width ascending and height descending, then find LIS on height."
    ),

    # =========================================================================
    # STACK & QUEUE (5 problems)
    # =========================================================================
    "max-nesting-depth": Problem(
        id="max-nesting-depth",
        title="Maximum Nesting Depth of Parentheses",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="Given a valid parentheses string `s`, return the nesting depth of `s`.",
        examples=[{"input": "s = '(1+(2*3)+((8)/4))+1'", "output": "3"}, {"input": "s = '(1)+((2))+(((3)))'", "output": "3"}],
        constraints=["1 <= s.length <= 100"],
        starter_code={
            "python": "def max_depth_parentheses(s: str) -> int:\n    pass\n",
            "c": "int maxDepth(char* s) { return 0; }\n",
            "cpp": "int maxDepth(string s) { return 0; }\n",
            "java": "public class Solution { public static int maxDepth(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def max_depth_parentheses(s: str) -> int:\n    cur, best = 0, 0\n    for ch in s:\n        if ch == '(':\n            cur += 1\n            best = max(best, cur)\n        elif ch == ')':\n            cur -= 1\n    return best\n",
            "c": "int maxDepth(char* s) { return 0; }\n",
            "cpp": "int maxDepth(string s) { return 0; }\n",
            "java": "public class Solution { public static int maxDepth(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="(1+(2*3)+((8)/4))+1", expected_output=3),
            TestCase(id=2, input="(1)+((2))+(((3)))", expected_output=3),
            TestCase(id=3, input="1", expected_output=0)
        ],
        learning_objectives=["Parentheses stack depth tracking counter in O(1) space"],
        common_misconceptions=["Using stack when a single integer counter suffices"],
        hint="Increment depth on '(' and update max; decrement on ')'."
    ),

    "decode-string": Problem(
        id="decode-string",
        title="Decode String (Nested Multipliers)",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="Given an encoded string, return its decoded string: `k[encoded_string]` repeats the string inside square brackets exactly `k` times.",
        examples=[{"input": "s = '3[a]2[bc]'", "output": "'aaabcbc'"}, {"input": "s = '3[a2[c]]'", "output": "'accaccacc'"}],
        constraints=["1 <= s.length <= 30"],
        starter_code={
            "python": "def decode_string(s: str) -> str:\n    pass\n",
            "c": "char* decodeString() { return \"\"; }\n",
            "cpp": "string decodeString(string s) { return \"\"; }\n",
            "java": "public class Solution { public static String decodeString(String s) { return \"\"; } }\n"
        },
        expected_solution={
            "python": "def decode_string(s: str) -> str:\n    stack = []\n    cur_str = ''\n    cur_num = 0\n    for ch in s:\n        if ch.isdigit():\n            cur_num = cur_num * 10 + int(ch)\n        elif ch == '[':\n            stack.append((cur_str, cur_num))\n            cur_str, cur_num = '', 0\n        elif ch == ']':\n            prev_str, num = stack.pop()\n            cur_str = prev_str + num * cur_str\n        else:\n            cur_str += ch\n    return cur_str\n",
            "c": "char* decodeString() { return \"\"; }\n",
            "cpp": "string decodeString(string s) { return \"\"; }\n",
            "java": "public class Solution { public static String decodeString(String s) { return \"\"; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="3[a]2[bc]", expected_output="aaabcbc"),
            TestCase(id=2, input="3[a2[c]]", expected_output="accaccacc"),
            TestCase(id=3, input="2[abc]3[cd]ef", expected_output="abcabccdcdcdef")
        ],
        learning_objectives=["Stacking previous string and multiplier context for nested brackets"],
        common_misconceptions=["Multi-digit numbers parsed as single digits"],
        hint="Push (prev_string, repeat_count) onto stack when encountering '['."
    ),

    "score-of-parentheses": Problem(
        id="score-of-parentheses",
        title="Score of Parentheses",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="Compute score: '()' has score 1, 'AB' has score A + B, and '(A)' has score 2 * A.",
        examples=[{"input": "s = '()'", "output": "1"}, {"input": "s = '(())'", "output": "2"}, {"input": "s = '()()'", "output": "2"}],
        constraints=["2 <= s.length <= 50"],
        starter_code={
            "python": "def score_of_parentheses(s: str) -> int:\n    pass\n",
            "c": "int scoreOfParentheses() { return 0; }\n",
            "cpp": "int scoreOfParentheses(string s) { return 0; }\n",
            "java": "public class Solution { public static int scoreOfParentheses(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def score_of_parentheses(s: str) -> int:\n    stack = [0]\n    for ch in s:\n        if ch == '(':\n            stack.append(0)\n        else:\n            v = stack.pop()\n            stack[-1] += max(2 * v, 1)\n    return stack[0]\n",
            "c": "int scoreOfParentheses() { return 0; }\n",
            "cpp": "int scoreOfParentheses(string s) { return 0; }\n",
            "java": "public class Solution { public static int scoreOfParentheses(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="()", expected_output=1),
            TestCase(id=2, input="(())", expected_output=2),
            TestCase(id=3, input="()()", expected_output=2)
        ],
        learning_objectives=["Layered evaluation stack for nested scoring rules"],
        common_misconceptions=["Mixing up addition and multiplication inside parentheses"],
        hint="On ')' pop and add max(2 * val, 1) to previous depth."
    ),

    "pattern-132": Problem(
        id="pattern-132",
        title="132 Pattern (Monotonic Stack)",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="Given an array of `n` integers `nums`, a 132 pattern is a subsequence of three integers `nums[i]`, `nums[j]` and `nums[k]` such that `i < j < k` and `nums[i] < nums[k] < nums[j]`. Return `True` if pattern exists.",
        examples=[{"input": "nums = [1, 2, 3, 4]", "output": "False"}, {"input": "nums = [3, 1, 4, 2]", "output": "True"}],
        constraints=["1 <= nums.length <= 2 * 10^5"],
        starter_code={
            "python": "def find132pattern(nums: list) -> bool:\n    pass\n",
            "c": "int find132pattern() { return 0; }\n",
            "cpp": "bool find132pattern(vector<int>& nums) { return false; }\n",
            "java": "public class Solution { public static boolean find132pattern(int[] nums) { return false; } }\n"
        },
        expected_solution={
            "python": "def find132pattern(nums: list) -> bool:\n    stack = []\n    s3 = float('-inf')\n    for x in reversed(nums):\n        if x < s3:\n            return True\n        while stack and stack[-1] < x:\n            s3 = stack.pop()\n        stack.append(x)\n    return False\n",
            "c": "int find132pattern() { return 0; }\n",
            "cpp": "bool find132pattern(vector<int>& nums) { return false; }\n",
            "java": "public class Solution { public static boolean find132pattern(int[] nums) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 3, 4], expected_output=False),
            TestCase(id=2, input=[3, 1, 4, 2], expected_output=True),
            TestCase(id=3, input=[-1, 3, 2, 0], expected_output=True)
        ],
        learning_objectives=["Reverse scan monotonic stack finding candidate for '2' in '132'"],
        common_misconceptions=["O(N^3) brute force triple loops"],
        hint="Scan from right to left keeping track of the best candidate for nums[k]."
    ),

    "basic-calculator": Problem(
        id="basic-calculator",
        title="Basic Calculator (Parentheses and Signs)",
        difficulty="Hard",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="Implement a basic calculator to evaluate a simple expression string containing digits, `+`, `-`, and parentheses `(` and `)`.",
        examples=[{"input": "s = '1 + 1'", "output": "2"}, {"input": "s = ' 2-1 + 2 '", "output": "3"}, {"input": "s = '(1+(4+5+2)-3)+(6+8)'", "output": "23"}],
        constraints=["1 <= s.length <= 3 * 10^5"],
        starter_code={
            "python": "def calculate(s: str) -> int:\n    pass\n",
            "c": "int calculate(char* s) { return 0; }\n",
            "cpp": "int calculate(string s) { return 0; }\n",
            "java": "public class Solution { public static int calculate(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def calculate(s: str) -> int:\n    stack = []\n    res, num, sign = 0, 0, 1\n    for ch in s:\n        if ch.isdigit():\n            num = num * 10 + int(ch)\n        elif ch in '+-':\n            res += sign * num\n            num = 0\n            sign = 1 if ch == '+' else -1\n        elif ch == '(':\n            stack.append(res)\n            stack.append(sign)\n            res, sign = 0, 1\n        elif ch == ')':\n            res += sign * num\n            num = 0\n            res *= stack.pop()\n            res += stack.pop()\n    return res + sign * num\n",
            "c": "int calculate(char* s) { return 0; }\n",
            "cpp": "int calculate(string s) { return 0; }\n",
            "java": "public class Solution { public static int calculate(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="1 + 1", expected_output=2),
            TestCase(id=2, input=" 2-1 + 2 ", expected_output=3),
            TestCase(id=3, input="(1+(4+5+2)-3)+(6+8)", expected_output=23)
        ],
        learning_objectives=["Stack state preservation across parentheses scopes"],
        common_misconceptions=["Failing to invert signs inside parentheses when preceded by negative sign"],
        hint="Push current result and sign onto stack at '(', resolve at ')'."
    ),

    # =========================================================================
    # ALGORITHMS & TWO POINTERS (5 problems)
    # =========================================================================
    "valid-mountain-array": Problem(
        id="valid-mountain-array",
        title="Valid Mountain Array",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="Given an array of integers `arr`, return `True` if and only if it is a valid mountain array (strictly increases to peak then strictly decreases).",
        examples=[{"input": "arr = [2, 1]", "output": "False"}, {"input": "arr = [3, 5, 5]", "output": "False"}, {"input": "arr = [0, 3, 2, 1]", "output": "True"}],
        constraints=["1 <= arr.length <= 10^4"],
        starter_code={
            "python": "def valid_mountain_array(arr: list) -> bool:\n    pass\n",
            "c": "int validMountainArray() { return 0; }\n",
            "cpp": "bool validMountainArray(vector<int>& arr) { return false; }\n",
            "java": "public class Solution { public static boolean validMountainArray(int[] arr) { return false; } }\n"
        },
        expected_solution={
            "python": "def valid_mountain_array(arr: list) -> bool:\n    n = len(arr)\n    if n < 3: return False\n    l, r = 0, n - 1\n    while l + 1 < n and arr[l] < arr[l + 1]: l += 1\n    while r - 1 >= 0 and arr[r] < arr[r - 1]: r -= 1\n    return 0 < l == r < n - 1\n",
            "c": "int validMountainArray() { return 0; }\n",
            "cpp": "bool validMountainArray(vector<int>& arr) { return false; }\n",
            "java": "public class Solution { public static boolean validMountainArray(int[] arr) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[2, 1], expected_output=False),
            TestCase(id=2, input=[3, 5, 5], expected_output=False),
            TestCase(id=3, input=[0, 3, 2, 1], expected_output=True)
        ],
        learning_objectives=["Two-pointer converging climb to peak"],
        common_misconceptions=["Plateaus or strictly increasing/decreasing arrays are not valid mountains"],
        hint="Climb from left and right; both pointers must meet at the same peak (not at endpoints)."
    ),

    "find-first-and-last-position": Problem(
        id="find-first-and-last-position",
        title="Find First and Last Position of Element in Sorted Array",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Binary Search",
        description="Find starting and ending position of a given `target` in sorted array `nums` in O(log n) time. Return `[-1, -1]` if target not found.",
        examples=[{"input": "nums = [5, 7, 7, 8, 8, 10], target = 8", "output": "[3, 4]"}, {"input": "nums = [5, 7, 7, 8, 8, 10], target = 6", "output": "[-1, -1]"}],
        constraints=["0 <= nums.length <= 10^5"],
        starter_code={
            "python": "def search_range(nums: list, target: int) -> list:\n    pass\n",
            "c": "void searchRange() {}\n",
            "cpp": "vector<int> searchRange(vector<int>& nums, int target) { return {-1, -1}; }\n",
            "java": "public class Solution { public static int[] searchRange(int[] nums, int target) { return new int[]{-1, -1}; } }\n"
        },
        expected_solution={
            "python": "def search_range(nums: list, target: int) -> list:\n    def find_bound(is_left):\n        low, high, ans = 0, len(nums) - 1, -1\n        while low <= high:\n            mid = (low + high) // 2\n            if nums[mid] == target:\n                ans = mid\n                if is_left: high = mid - 1\n                else: low = mid + 1\n            elif nums[mid] < target: low = mid + 1\n            else: high = mid - 1\n        return ans\n    return [find_bound(True), find_bound(False)]\n",
            "c": "void searchRange() {}\n",
            "cpp": "vector<int> searchRange(vector<int>& nums, int target) { return {-1, -1}; }\n",
            "java": "public class Solution { public static int[] searchRange(int[] nums, int target) { return new int[]{-1, -1}; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [5, 7, 7, 8, 8, 10], "target": 8}, expected_output=[3, 4]),
            TestCase(id=2, input={"nums": [5, 7, 7, 8, 8, 10], "target": 6}, expected_output=[-1, -1]),
            TestCase(id=3, input={"nums": [], "target": 0}, expected_output=[-1, -1])
        ],
        learning_objectives=["Dual binary search for left and right boundary detection"],
        common_misconceptions=["Linear expansion from match point violates O(log N) on all-equal arrays"],
        hint="Run two binary searches: one biasing left on match, one biasing right."
    ),

    "boats-to-save-people": Problem(
        id="boats-to-save-people",
        title="Boats to Save People",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="You are given an array `people` where `people[i]` is the weight of person `i`, and an infinite number of boats where each boat can carry at most `limit` weight and at most 2 people. Return minimum boats.",
        examples=[{"input": "people = [1, 2], limit = 3", "output": "1"}, {"input": "people = [3, 2, 2, 1], limit = 3", "output": "3"}],
        constraints=["1 <= people.length <= 5 * 10^4", "1 <= people[i] <= limit"],
        starter_code={
            "python": "def num_rescue_boats(people: list, limit: int) -> int:\n    pass\n",
            "c": "int numRescueBoats() { return 0; }\n",
            "cpp": "int numRescueBoats(vector<int>& people, int limit) { return 0; }\n",
            "java": "public class Solution { public static int numRescueBoats(int[] people, int limit) { return 0; } }\n"
        },
        expected_solution={
            "python": "def num_rescue_boats(people: list, limit: int) -> int:\n    people.sort()\n    l, r, boats = 0, len(people) - 1, 0\n    while l <= r:\n        if people[l] + people[r] <= limit:\n            l += 1\n        r -= 1\n        boats += 1\n    return boats\n",
            "c": "int numRescueBoats() { return 0; }\n",
            "cpp": "int numRescueBoats(vector<int>& people, int limit) { return 0; }\n",
            "java": "public class Solution { public static int numRescueBoats(int[] people, int limit) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"people": [1, 2], "limit": 3}, expected_output=1),
            TestCase(id=2, input={"people": [3, 2, 2, 1], "limit": 3}, expected_output=3),
            TestCase(id=3, input={"people": [3, 5, 3, 4], "limit": 5}, expected_output=4)
        ],
        learning_objectives=["Greedy two-pointer pairing of heaviest with lightest person"],
        common_misconceptions=["Trying to pair two lightest people leaves heavy people stranded alone"],
        hint="Pair heaviest person with lightest person if sum <= limit; heaviest takes boat regardless."
    ),

    "search-in-rotated-sorted-array-ii": Problem(
        id="search-in-rotated-sorted-array-ii",
        title="Search in Rotated Sorted Array II (Duplicates)",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Binary Search",
        description="Given a rotated sorted array `nums` that may contain duplicate values, return `True` if `target` is in `nums`, or `False` if not.",
        examples=[{"input": "nums = [2, 5, 6, 0, 0, 1, 2], target = 0", "output": "True"}, {"input": "nums = [2, 5, 6, 0, 0, 1, 2], target = 3", "output": "False"}],
        constraints=["1 <= nums.length <= 5000"],
        starter_code={
            "python": "def search_rotated_2(nums: list, target: int) -> bool:\n    pass\n",
            "c": "int searchRotated2() { return 0; }\n",
            "cpp": "bool searchRotated2(vector<int>& nums, int target) { return false; }\n",
            "java": "public class Solution { public static boolean searchRotated2(int[] nums, int target) { return false; } }\n"
        },
        expected_solution={
            "python": "def search_rotated_2(nums: list, target: int) -> bool:\n    low, high = 0, len(nums) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if nums[mid] == target: return True\n        if nums[low] == nums[mid] == nums[high]:\n            low += 1\n            high -= 1\n        elif nums[low] <= nums[mid]:\n            if nums[low] <= target < nums[mid]: high = mid - 1\n            else: low = mid + 1\n        else:\n            if nums[mid] < target <= nums[high]: low = mid + 1\n            else: high = mid - 1\n    return False\n",
            "c": "int searchRotated2() { return 0; }\n",
            "cpp": "bool searchRotated2(vector<int>& nums, int target) { return false; }\n",
            "java": "public class Solution { public static boolean searchRotated2(int[] nums, int target) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [2, 5, 6, 0, 0, 1, 2], "target": 0}, expected_output=True),
            TestCase(id=2, input={"nums": [2, 5, 6, 0, 0, 1, 2], "target": 3}, expected_output=False)
        ],
        learning_objectives=["Handling duplicate ambiguity in rotated binary search by trimming endpoints"],
        common_misconceptions=["Assuming binary search is impossible with duplicates"],
        hint="When nums[low] == nums[mid] == nums[high], trim both low and high by 1."
    ),

    "median-from-data-stream": Problem(
        id="median-from-data-stream",
        title="Find Median from Data Stream (Two Heaps)",
        difficulty="Hard",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="The median is the middle value in an ordered integer list. Design a data structure that supports adding integers and finding the median.",
        examples=[{"input": "ops = ['addNum', 'addNum', 'findMedian', 'addNum', 'findMedian'], vals = [1, 2, null, 3, null]", "output": "[null, null, 1.5, null, 2.0]"}],
        constraints=["1 <= ops.length <= 5 * 10^4"],
        starter_code={
            "python": "def median_finder_runner(ops: list, vals: list) -> list:\n    pass\n",
            "c": "void medianFinder() {}\n",
            "cpp": "void medianFinder() {}\n",
            "java": "public class Solution { public static void medianFinder() {} }\n"
        },
        expected_solution={
            "python": "def median_finder_runner(ops: list, vals: list) -> list:\n    import bisect\n    nums, res = [], []\n    for op, v in zip(ops, vals):\n        if op == 'addNum':\n            bisect.insort(nums, v)\n            res.append(None)\n        elif op == 'findMedian':\n            n = len(nums)\n            if n % 2 != 0: res.append(float(nums[n // 2]))\n            else: res.append((nums[n // 2 - 1] + nums[n // 2]) / 2.0)\n    return res\n",
            "c": "void medianFinder() {}\n",
            "cpp": "void medianFinder() {}\n",
            "java": "public class Solution { public static void medianFinder() {} }\n"
        },
        test_cases=[
            TestCase(id=1, input={"ops": ["addNum", "addNum", "findMedian", "addNum", "findMedian"], "vals": [1, 2, None, 3, None]}, expected_output=[None, None, 1.5, None, 2.0])
        ],
        learning_objectives=["Two heaps balancing (max-heap for lower half, min-heap for upper half)"],
        common_misconceptions=["Sorting entire array on every findMedian call"],
        hint="Balance lower half and upper half with max-heap and min-heap."
    ),

    # =========================================================================
    # TREES & BST (5 problems)
    # =========================================================================
    "sum-of-left-leaves": Problem(
        id="sum-of-left-leaves",
        title="Sum of Left Leaves",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Given the root of a binary tree, return the sum of all left leaves.",
        examples=[{"input": "root = [3, 9, 20, null, null, 15, 7]", "output": "24", "explanation": "There are two left leaves: 9 and 15 (9 + 15 = 24)."}],
        constraints=["Nodes in range [1, 1000]"],
        starter_code={
            "python": "def sum_of_left_leaves(root: list) -> int:\n    pass\n",
            "c": "int sumOfLeftLeaves() { return 0; }\n",
            "cpp": "int sumOfLeftLeaves() { return 0; }\n",
            "java": "public class Solution { public static int sumOfLeftLeaves() { return 0; } }\n"
        },
        expected_solution={
            "python": "def sum_of_left_leaves(root: list) -> int:\n    if not root or root[0] is None: return 0\n    total = 0\n    def dfs(idx, is_left):\n        nonlocal total\n        if idx >= len(root) or root[idx] is None: return\n        l, r = 2 * idx + 1, 2 * idx + 2\n        is_leaf = (l >= len(root) or root[l] is None) and (r >= len(root) or root[r] is None)\n        if is_leaf and is_left: total += root[idx]\n        dfs(l, True)\n        dfs(r, False)\n    dfs(0, False)\n    return total\n",
            "c": "int sumOfLeftLeaves() { return 0; }\n",
            "cpp": "int sumOfLeftLeaves() { return 0; }\n",
            "java": "public class Solution { public static int sumOfLeftLeaves() { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[3, 9, 20, None, None, 15, 7], expected_output=24),
            TestCase(id=2, input=[1], expected_output=0)
        ],
        learning_objectives=["Leaf status verification combined with branch direction flag"],
        common_misconceptions=["Counting internal left nodes that have children"],
        hint="Pass a boolean is_left to recursive call; only add if is_left and is_leaf."
    ),

    "cousins-in-binary-tree": Problem(
        id="cousins-in-binary-tree",
        title="Cousins in Binary Tree",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="BFS Level Order",
        description="Two nodes of a binary tree are cousins if they have the same depth with different parents. Return `True` if nodes with values `x` and `y` are cousins.",
        examples=[{"input": "root = [1, 2, 3, 4], x = 4, y = 3", "output": "False"}, {"input": "root = [1, 2, 3, null, 4, null, 5], x = 5, y = 4", "output": "True"}],
        constraints=["2 <= nodes <= 100"],
        starter_code={
            "python": "def is_cousins(root: list, x: int, y: int) -> bool:\n    pass\n",
            "c": "int isCousins() { return 0; }\n",
            "cpp": "bool isCousins(vector<int>& root, int x, int y) { return false; }\n",
            "java": "public class Solution { public static boolean isCousins(int[] root, int x, int y) { return false; } }\n"
        },
        expected_solution={
            "python": "def is_cousins(root: list, x: int, y: int) -> bool:\n    if not root or root[0] is None: return False\n    info = {}\n    def dfs(idx, parent, depth):\n        if idx >= len(root) or root[idx] is None: return\n        val = root[idx]\n        if val in (x, y): info[val] = (parent, depth)\n        dfs(2 * idx + 1, val, depth + 1)\n        dfs(2 * idx + 2, val, depth + 1)\n    dfs(0, None, 0)\n    if x in info and y in info:\n        px, dx = info[x]\n        py, dy = info[y]\n        return dx == dy and px != py\n    return False\n",
            "c": "int isCousins() { return 0; }\n",
            "cpp": "bool isCousins(vector<int>& root, int x, int y) { return false; }\n",
            "java": "public class Solution { public static boolean isCousins(int[] root, int x, int y) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"root": [1, 2, 3, 4], "x": 4, "y": 3}, expected_output=False),
            TestCase(id=2, input={"root": [1, 2, 3, None, 4, None, 5], "x": 5, "y": 4}, expected_output=True)
        ],
        learning_objectives=["Parent tracking and depth comparison in tree traversal"],
        common_misconceptions=["Siblings (same parent) are not cousins"],
        hint="Cousins require same depth AND different parents."
    ),

    "lowest-common-ancestor-binary-tree": Problem(
        id="lowest-common-ancestor-binary-tree",
        title="Lowest Common Ancestor of a Binary Tree",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Given a binary tree, find the lowest common ancestor (LCA) of two given node values `p` and `q`.",
        examples=[{"input": "root = [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], p = 5, q = 1", "output": "3"}, {"input": "root = [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], p = 5, q = 4", "output": "5"}],
        constraints=["2 <= nodes <= 10^5"],
        starter_code={
            "python": "def lowest_common_ancestor(root: list, p: int, q: int) -> int:\n    pass\n",
            "c": "int lowestCommonAncestor() { return 0; }\n",
            "cpp": "int lowestCommonAncestor(vector<int>& root, int p, int q) { return 0; }\n",
            "java": "public class Solution { public static int lowestCommonAncestor(int[] root, int p, int q) { return 0; } }\n"
        },
        expected_solution={
            "python": "def lowest_common_ancestor(root: list, p: int, q: int) -> int:\n    def dfs(idx):\n        if idx >= len(root) or root[idx] is None: return None\n        val = root[idx]\n        if val == p or val == q: return val\n        left = dfs(2 * idx + 1)\n        right = dfs(2 * idx + 2)\n        if left is not None and right is not None: return val\n        return left if left is not None else right\n    return dfs(0)\n",
            "c": "int lowestCommonAncestor() { return 0; }\n",
            "cpp": "int lowestCommonAncestor(vector<int>& root, int p, int q) { return 0; }\n",
            "java": "public class Solution { public static int lowestCommonAncestor(int[] root, int p, int q) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], "p": 5, "q": 1}, expected_output=3),
            TestCase(id=2, input={"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], "p": 5, "q": 4}, expected_output=5)
        ],
        learning_objectives=["Bottom-up post-order LCA deduction when targets originate in distinct subtrees"],
        common_misconceptions=["Assuming BST ordering in general binary tree"],
        hint="If root matches p or q, or left and right subtrees each contain one target, root is the LCA."
    ),

    "flatten-binary-tree-to-linked-list": Problem(
        id="flatten-binary-tree-to-linked-list",
        title="Flatten Binary Tree to Linked List",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Flatten binary tree into a 'linked list' in-place using right pointers following pre-order traversal.",
        examples=[{"input": "root = [1, 2, 5, 3, 4, null, 6]", "output": "[1, null, 2, null, 3, null, 4, null, 5, null, 6]"}],
        constraints=["0 <= nodes <= 2000"],
        starter_code={
            "python": "def flatten_tree(root: list) -> list:\n    pass\n",
            "c": "void flattenTree() {}\n",
            "cpp": "void flattenTree() {}\n",
            "java": "public class Solution { public static void flattenTree() {} }\n"
        },
        expected_solution={
            "python": "def flatten_tree(root: list) -> list:\n    if not root or root[0] is None: return []\n    res = []\n    def pre(idx):\n        if idx >= len(root) or root[idx] is None: return\n        res.append(root[idx])\n        pre(2 * idx + 1)\n        pre(2 * idx + 2)\n    pre(0)\n    out = []\n    for x in res:\n        out.append(x)\n        out.append(None)\n    return out[:-1]\n",
            "c": "void flattenTree() {}\n",
            "cpp": "void flattenTree() {}\n",
            "java": "public class Solution { public static void flattenTree() {} }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 5, 3, 4, None, 6], expected_output=[1, None, 2, None, 3, None, 4, None, 5, None, 6]),
            TestCase(id=2, input=[], expected_output=[])
        ],
        learning_objectives=["In-place tree restructuring following pre-order sequence"],
        common_misconceptions=["Losing reference to right subtree when overwriting with left"],
        hint="Pre-order traversal specifies the linked list node sequence."
    ),

    "binary-tree-vertical-order": Problem(
        id="binary-tree-vertical-order",
        title="Binary Tree Vertical Order Traversal",
        difficulty="Hard",
        topic="Trees & Binary Search Trees",
        subtopic="BFS Level Order",
        description="Given root of binary tree, return vertical order traversal of its nodes' values from top to bottom, column by column.",
        examples=[{"input": "root = [3, 9, 20, null, null, 15, 7]", "output": "[[9], [3, 15], [20], [7]]"}],
        constraints=["0 <= nodes <= 100"],
        starter_code={
            "python": "def vertical_order(root: list) -> list:\n    pass\n",
            "c": "void verticalOrder() {}\n",
            "cpp": "vector<vector<int>> verticalOrder() { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> verticalOrder() { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def vertical_order(root: list) -> list:\n    from collections import defaultdict, deque\n    if not root or root[0] is None: return []\n    cols = defaultdict(list)\n    q = deque([(0, 0)])\n    while q:\n        idx, col = q.popleft()\n        cols[col].append(root[idx])\n        l, r = 2 * idx + 1, 2 * idx + 2\n        if l < len(root) and root[l] is not None: q.append((l, col - 1))\n        if r < len(root) and root[r] is not None: q.append((r, col + 1))\n    return [cols[c] for c in sorted(cols.keys())]\n",
            "c": "void verticalOrder() {}\n",
            "cpp": "vector<vector<int>> verticalOrder() { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> verticalOrder() { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[3, 9, 20, None, None, 15, 7], expected_output=[[9], [3, 15], [20], [7]]),
            TestCase(id=2, input=[3, 9, 8, 4, 0, 1, 7], expected_output=[[4], [9], [3, 0, 1], [8], [7]])
        ],
        learning_objectives=["BFS column coordinate hashing preserving vertical top-to-bottom order"],
        common_misconceptions=["DFS violates top-to-bottom ordering within columns"],
        hint="Use BFS to track (node, column) where left child is col - 1 and right is col + 1."
    ),

    # =========================================================================
    # GRAPHS & TRAVERSAL (5 problems)
    # =========================================================================
    "keys-and-rooms": Problem(
        id="keys-and-rooms",
        title="Keys and Rooms (Graph Reachability)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="There are `n` rooms labeled 0 to `n - 1`. You start in room 0 which is unlocked. Each room contains a set of keys to other rooms. Return `True` if you can visit all rooms.",
        examples=[{"input": "rooms = [[1], [2], [3], []]", "output": "True"}, {"input": "rooms = [[1, 3], [3, 0, 1], [2], [0]]", "output": "False"}],
        constraints=["n == rooms.length", "2 <= n <= 1000"],
        starter_code={
            "python": "def can_visit_all_rooms(rooms: list) -> bool:\n    pass\n",
            "c": "int canVisitAllRooms() { return 0; }\n",
            "cpp": "bool canVisitAllRooms(vector<vector<int>>& rooms) { return false; }\n",
            "java": "public class Solution { public static boolean canVisitAllRooms(List<List<Integer>> rooms) { return false; } }\n"
        },
        expected_solution={
            "python": "def can_visit_all_rooms(rooms: list) -> bool:\n    visited = {0}\n    stack = [0]\n    while stack:\n        room = stack.pop()\n        for key in rooms[room]:\n            if key not in visited:\n                visited.add(key)\n                stack.append(key)\n    return len(visited) == len(rooms)\n",
            "c": "int canVisitAllRooms() { return 0; }\n",
            "cpp": "bool canVisitAllRooms(vector<vector<int>>& rooms) { return false; }\n",
            "java": "public class Solution { public static boolean canVisitAllRooms(List<List<Integer>> rooms) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1], [2], [3], []], expected_output=True),
            TestCase(id=2, input=[[1, 3], [3, 0, 1], [2], [0]], expected_output=False)
        ],
        learning_objectives=["Standard directed graph DFS reachability"],
        common_misconceptions=["Failing to check if disconnected components remain"],
        hint="DFS from room 0 and check if len(visited) == total_rooms."
    ),

    "surrounded-regions": Problem(
        id="surrounded-regions",
        title="Surrounded Regions (Border Inward Flood Fill)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="Given an `m x n` matrix `board` containing 'X' and 'O', capture all regions that are 4-directionally surrounded by 'X'.",
        examples=[{"input": "board = [['X','X','X','X'],['X','O','O','X'],['X','X','O','X'],['X','O','X','X']]", "output": "[['X','X','X','X'],['X','X','X','X'],['X','X','X','X'],['X','O','X','X']]"}],
        constraints=["1 <= m, n <= 200"],
        starter_code={
            "python": "def solve_surrounded(board: list) -> list:\n    pass\n",
            "c": "void solveSurrounded() {}\n",
            "cpp": "void solveSurrounded(vector<vector<char>>& board) {}\n",
            "java": "public class Solution { public static void solveSurrounded(char[][] board) {} }\n"
        },
        expected_solution={
            "python": "def solve_surrounded(board: list) -> list:\n    if not board: return board\n    R, C = len(board), len(board[0])\n    def dfs(r, c):\n        if r < 0 or r >= R or c < 0 or c >= C or board[r][c] != 'O': return\n        board[r][c] = 'T'\n        dfs(r + 1, c); dfs(r - 1, c); dfs(r, c + 1); dfs(r, c - 1)\n    for r in range(R):\n        dfs(r, 0); dfs(r, C - 1)\n    for c in range(C):\n        dfs(0, c); dfs(R - 1, c)\n    for r in range(R):\n        for c in range(C):\n            if board[r][c] == 'O': board[r][c] = 'X'\n            elif board[r][c] == 'T': board[r][c] = 'O'\n    return board\n",
            "c": "void solveSurrounded() {}\n",
            "cpp": "void solveSurrounded(vector<vector<char>>& board) {}\n",
            "java": "public class Solution { public static void solveSurrounded(char[][] board) {} }\n"
        },
        test_cases=[
            TestCase(id=1, input=[["X","X","X","X"],["X","O","O","X"],["X","X","O","X"],["X","O","X","X"]], expected_output=[["X","X","X","X"],["X","X","X","X"],["X","X","X","X"],["X","O","X","X"]]),
            TestCase(id=2, input=[["X"]], expected_output=[["X"]])
        ],
        learning_objectives=["Reverse flood fill from perimeter borders"],
        common_misconceptions=["Traversing inward cells without knowing if they reach a border"],
        hint="Mark border-connected 'O's as temporary, flip remaining 'O's to 'X', restore temporary."
    ),

    "redundant-connection": Problem(
        id="redundant-connection",
        title="Redundant Connection (Cycle Edge in Graph)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="Cycle Detection",
        description="A tree is an undirected graph that is connected and has no cycles. Given graph edges with 1 extra edge, return an edge that can be removed so that the resulting graph is a tree.",
        examples=[{"input": "edges = [[1, 2], [1, 3], [2, 3]]", "output": "[2, 3]"}, {"input": "edges = [[1,2],[2,3],[3,4],[1,4],[1,5]]", "output": "[1, 4]"}],
        constraints=["3 <= edges.length <= 1000"],
        starter_code={
            "python": "def find_redundant_connection(edges: list) -> list:\n    pass\n",
            "c": "void findRedundantConnection() {}\n",
            "cpp": "vector<int> findRedundantConnection(vector<vector<int>>& edges) { return {}; }\n",
            "java": "public class Solution { public static int[] findRedundantConnection(int[][] edges) { return new int[0]; } }\n"
        },
        expected_solution={
            "python": "def find_redundant_connection(edges: list) -> list:\n    parent = list(range(len(edges) + 1))\n    def find(x):\n        if parent[x] != x: parent[x] = find(parent[x])\n        return parent[x]\n    for u, v in edges:\n        root_u, root_v = find(u), find(v)\n        if root_u == root_v: return [u, v]\n        parent[root_u] = root_v\n    return []\n",
            "c": "void findRedundantConnection() {}\n",
            "cpp": "vector<int> findRedundantConnection(vector<vector<int>>& edges) { return {}; }\n",
            "java": "public class Solution { public static int[] findRedundantConnection(int[][] edges) { return new int[0]; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1, 2], [1, 3], [2, 3]], expected_output=[2, 3]),
            TestCase(id=2, input=[[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]], expected_output=[1, 4])
        ],
        learning_objectives=["Disjoint Set Union (DSU / Union-Find) cycle detection"],
        common_misconceptions=["DFS from scratch for every edge is O(E^2)"],
        hint="Union-Find: the edge where find(u) == find(v) creates the cycle."
    ),

    "graph-valid-tree": Problem(
        id="graph-valid-tree",
        title="Graph Valid Tree",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="Cycle Detection",
        description="Given `n` nodes labeled from `0` to `n - 1` and a list of undirected edges, write a function to check whether these edges make up a valid tree.",
        examples=[{"input": "n = 5, edges = [[0, 1], [0, 2], [0, 3], [1, 4]]", "output": "True"}, {"input": "n = 5, edges = [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]", "output": "False"}],
        constraints=["1 <= n <= 2000", "0 <= edges.length <= 5000"],
        starter_code={
            "python": "def valid_tree(n: int, edges: list) -> bool:\n    pass\n",
            "c": "int validTree() { return 0; }\n",
            "cpp": "bool validTree(int n, vector<vector<int>>& edges) { return false; }\n",
            "java": "public class Solution { public static boolean validTree(int n, int[][] edges) { return false; } }\n"
        },
        expected_solution={
            "python": "def valid_tree(n: int, edges: list) -> bool:\n    if len(edges) != n - 1: return False\n    parent = list(range(n))\n    def find(x):\n        if parent[x] != x: parent[x] = find(parent[x])\n        return parent[x]\n    for u, v in edges:\n        ru, rv = find(u), find(v)\n        if ru == rv: return False\n        parent[ru] = rv\n    return True\n",
            "c": "int validTree() { return 0; }\n",
            "cpp": "bool validTree(int n, vector<vector<int>>& edges) { return false; }\n",
            "java": "public class Solution { public static boolean validTree(int n, int[][] edges) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [1, 4]]}, expected_output=True),
            TestCase(id=2, input={"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]}, expected_output=False)
        ],
        learning_objectives=["Tree properties: exactly n - 1 edges and no cycles"],
        common_misconceptions=["Having no cycles is insufficient if the graph is disconnected"],
        hint="A tree must have exactly n - 1 edges and no cycles."
    ),

    "network-delay-time": Problem(
        id="network-delay-time",
        title="Network Delay Time (Dijkstra Shortest Path)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="BFS / Shortest Path",
        description="Given network travel times for directed edges `times[i] = (ui, vi, wi)`, return minimum time for all `n` nodes to receive signal sent from node `k`, or -1 if impossible.",
        examples=[{"input": "times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2", "output": "2"}, {"input": "times = [[1,2,1]], n = 2, k = 1", "output": "1"}],
        constraints=["1 <= k <= n <= 100"],
        starter_code={
            "python": "def network_delay_time(times: list, n: int, k: int) -> int:\n    pass\n",
            "c": "int networkDelayTime() { return -1; }\n",
            "cpp": "int networkDelayTime(vector<vector<int>>& times, int n, int k) { return -1; }\n",
            "java": "public class Solution { public static int networkDelayTime(int[][] times, int n, int k) { return -1; } }\n"
        },
        expected_solution={
            "python": "def network_delay_time(times: list, n: int, k: int) -> int:\n    import heapq\n    from collections import defaultdict\n    adj = defaultdict(list)\n    for u, v, w in times: adj[u].append((v, w))\n    dist = {}\n    pq = [(0, k)]\n    while pq:\n        d, u = heapq.heappop(pq)\n        if u in dist: continue\n        dist[u] = d\n        for v, w in adj[u]:\n            if v not in dist: heapq.heappush(pq, (d + w, v))\n    return max(dist.values()) if len(dist) == n else -1\n",
            "c": "int networkDelayTime() { return -1; }\n",
            "cpp": "int networkDelayTime(vector<vector<int>>& times, int n, int k) { return -1; }\n",
            "java": "public class Solution { public static int networkDelayTime(int[][] times, int n, int k) { return -1; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"times": [[2, 1, 1], [2, 3, 1], [3, 4, 1]], "n": 4, "k": 2}, expected_output=2),
            TestCase(id=2, input={"times": [[1, 2, 1]], "n": 2, "k": 1}, expected_output=1),
            TestCase(id=3, input={"times": [[1, 2, 1]], "n": 2, "k": 2}, expected_output=-1)
        ],
        learning_objectives=["Dijkstra's single-source shortest path algorithm with priority queue"],
        common_misconceptions=["Standard BFS fails when edges have non-unit weights"],
        hint="Run Dijkstra from source k; max distance is the total delay time."
    )
}
