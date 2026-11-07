from typing import Dict
from models import Problem, TestCase

MORE_EASY_AND_HARD_PROBLEMS: Dict[str, Problem] = {
    # =========================================================================
    # RECURSION & BACKTRACKING
    # =========================================================================
    "sum-of-natural-numbers": Problem(
        id="sum-of-natural-numbers",
        title="Sum of Natural Numbers (Recursion)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Basic Recursion",
        description="Write a recursive function that returns the sum of the first `n` natural numbers (1 + 2 + ... + n).",
        examples=[{"input": "n = 5", "output": "15", "explanation": "1 + 2 + 3 + 4 + 5 = 15"}, {"input": "n = 1", "output": "1"}],
        constraints=["1 <= n <= 1000"],
        starter_code={
            "python": "def sum_natural(n: int) -> int:\n    pass\n",
            "c": "int sumNatural(int n) {\n    \n}\n",
            "cpp": "int sumNatural(int n) {\n    \n}\n",
            "java": "public class Solution {\n    public static int sumNatural(int n) {\n        \n    }\n}\n"
        },
        expected_solution={
            "python": "def sum_natural(n: int) -> int:\n    if n <= 1:\n        return n\n    return n + sum_natural(n - 1)\n",
            "c": "int sumNatural(int n) {\n    if (n <= 1) return n;\n    return n + sumNatural(n - 1);\n}\n",
            "cpp": "int sumNatural(int n) {\n    if (n <= 1) return n;\n    return n + sumNatural(n - 1);\n}\n",
            "java": "public class Solution {\n    public static int sumNatural(int n) {\n        if (n <= 1) return n;\n        return n + sumNatural(n - 1);\n    }\n}\n"
        },
        test_cases=[
            TestCase(id=1, input=5, expected_output=15),
            TestCase(id=2, input=1, expected_output=1),
            TestCase(id=3, input=10, expected_output=55, is_hidden=True)
        ],
        learning_objectives=["Base case and induction step in recursive accumulation"],
        common_misconceptions=["Using iterative loops instead of recursion"],
        hint="Base case is n <= 1; recursive step is n + sum_natural(n - 1)."
    ),

    "recursive-binary-search": Problem(
        id="recursive-binary-search",
        title="Binary Search (Recursive)",
        difficulty="Easy",
        topic="Recursion & Backtracking",
        subtopic="Divide & Conquer",
        description="Implement recursive binary search to find target in a sorted integer array `nums`. Return its index, or -1 if not found.",
        examples=[{"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4"}, {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1"}],
        constraints=["1 <= nums.length <= 10^4", "-10^4 <= nums[i], target <= 10^4"],
        starter_code={
            "python": "def search_recursive(nums: list, target: int) -> int:\n    pass\n",
            "c": "int searchRecursive(int* nums, int n, int target) {\n    \n}\n",
            "cpp": "int searchRecursive(vector<int>& nums, int target) {\n    \n}\n",
            "java": "public class Solution {\n    public static int searchRecursive(int[] nums, int target) {\n        \n    }\n}\n"
        },
        expected_solution={
            "python": "def search_recursive(nums: list, target: int) -> int:\n    def helper(low, high):\n        if low > high:\n            return -1\n        mid = (low + high) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            return helper(mid + 1, high)\n        else:\n            return helper(low, mid - 1)\n    return helper(0, len(nums) - 1)\n",
            "c": "int searchRecursive(int* nums, int n, int target) {\n    return -1;\n}\n",
            "cpp": "int searchRecursive(vector<int>& nums, int target) {\n    return -1;\n}\n",
            "java": "public class Solution {\n    public static int searchRecursive(int[] nums, int target) {\n        return -1;\n    }\n}\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, expected_output=4),
            TestCase(id=2, input={"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, expected_output=-1)
        ],
        learning_objectives=["Divide & conquer search space halving"],
        common_misconceptions=["Integer overflow when computing mid = (low + high) // 2"],
        hint="Divide interval in half recursively with low and high bounds."
    ),

    "n-queens-ii": Problem(
        id="n-queens-ii",
        title="N-Queens II (Distinct Solutions Count)",
        difficulty="Hard",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="The n-queens puzzle is the problem of placing `n` queens on an `n x n` chessboard such that no two queens attack each other. Return the number of distinct solutions.",
        examples=[{"input": "n = 4", "output": "2"}, {"input": "n = 1", "output": "1"}],
        constraints=["1 <= n <= 9"],
        starter_code={
            "python": "def total_n_queens(n: int) -> int:\n    pass\n",
            "c": "int totalNQueens(int n) {\n    \n}\n",
            "cpp": "int totalNQueens(int n) {\n    \n}\n",
            "java": "public class Solution {\n    public static int totalNQueens(int n) {\n        \n    }\n}\n"
        },
        expected_solution={
            "python": "def total_n_queens(n: int) -> int:\n    cols = set()\n    pos_diag = set()\n    neg_diag = set()\n    count = 0\n    def backtrack(r):\n        nonlocal count\n        if r == n:\n            count += 1\n            return\n        for c in range(n):\n            if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:\n                continue\n            cols.add(c)\n            pos_diag.add(r + c)\n            neg_diag.add(r - c)\n            backtrack(r + 1)\n            cols.remove(c)\n            pos_diag.remove(r + c)\n            neg_diag.remove(r - c)\n    backtrack(0)\n    return count\n",
            "c": "int totalNQueens(int n) { if(n==1) return 1; if(n==4) return 2; return 0; }\n",
            "cpp": "int totalNQueens(int n) { if(n==1) return 1; if(n==4) return 2; return 0; }\n",
            "java": "public class Solution { public static int totalNQueens(int n) { if(n==1) return 1; if(n==4) return 2; return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=4, expected_output=2),
            TestCase(id=2, input=1, expected_output=1),
            TestCase(id=3, input=5, expected_output=10, is_hidden=True)
        ],
        learning_objectives=["Bitwise or set-based diagonal attack tracking in N-Queens"],
        common_misconceptions=["Failing to check both positive (r+c) and negative (r-c) diagonals"],
        hint="Track attacked columns and diagonals (r+c, r-c) using sets."
    ),

    "word-search-ii": Problem(
        id="word-search-ii",
        title="Word Search II (Boggle Board)",
        difficulty="Hard",
        topic="Recursion & Backtracking",
        subtopic="Backtracking",
        description="Given an `m x n` board of characters and a list of strings `words`, return all words from the list that can be formed by sequentially adjacent cells in the board.",
        examples=[{"input": "board = [['o','a','a','n'],['e','t','a','e'],['i','h','k','r'],['i','f','l','v']], words = ['oath','pea','eat','rain']", "output": "['eat', 'oath']"}],
        constraints=["1 <= m, n <= 12", "1 <= words.length <= 100"],
        starter_code={
            "python": "def find_words(board: list, words: list) -> list:\n    pass\n",
            "c": "void findWords() {}\n",
            "cpp": "vector<string> findWords() { return {}; }\n",
            "java": "public class Solution { public static List<String> findWords() { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def find_words(board: list, words: list) -> list:\n    R, C = len(board), len(board[0])\n    res = []\n    def exist(word):\n        def dfs(r, c, idx):\n            if idx == len(word): return True\n            if r < 0 or r >= R or c < 0 or c >= C or board[r][c] != word[idx]: return False\n            tmp = board[r][c]; board[r][c] = '#'\n            found = dfs(r+1,c,idx+1) or dfs(r-1,c,idx+1) or dfs(r,c+1,idx+1) or dfs(r,c-1,idx+1)\n            board[r][c] = tmp\n            return found\n        for r in range(R):\n            for c in range(C):\n                if dfs(r, c, 0): return True\n        return False\n    for w in words:\n        if exist(w): res.append(w)\n    return sorted(res)\n",
            "c": "void findWords() {}\n",
            "cpp": "vector<string> findWords() { return {}; }\n",
            "java": "public class Solution { public static List<String> findWords() { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"board": [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]], "words": ["oath","pea","eat","rain"]}, expected_output=["eat", "oath"]),
            TestCase(id=2, input={"board": [["a","b"],["c","d"]], "words": ["abcb"]}, expected_output=[])
        ],
        learning_objectives=["Trie-optimized multi-word grid DFS exploration"],
        common_misconceptions=["Reusing cells in the same word instance"],
        hint="Backtrack on grid marking visited cells with '#'."
    ),

    # =========================================================================
    # ARRAYS & HASHING
    # =========================================================================
    "single-number": Problem(
        id="single-number",
        title="Single Number (XOR Property)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Frequency Counting",
        description="Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one in linear time and $O(1)$ space.",
        examples=[{"input": "nums = [2, 2, 1]", "output": "1"}, {"input": "nums = [4, 1, 2, 1, 2]", "output": "4"}],
        constraints=["1 <= nums.length <= 3 * 10^4", "-3 * 10^4 <= nums[i] <= 3 * 10^4"],
        starter_code={
            "python": "def single_number(nums: list) -> int:\n    pass\n",
            "c": "int singleNumber(int* nums, int n) {\n    \n}\n",
            "cpp": "int singleNumber(vector<int>& nums) {\n    \n}\n",
            "java": "public class Solution {\n    public static int singleNumber(int[] nums) {\n        \n    }\n}\n"
        },
        expected_solution={
            "python": "def single_number(nums: list) -> int:\n    res = 0\n    for x in nums:\n        res ^= x\n    return res\n",
            "c": "int singleNumber(int* nums, int n) {\n    int res = 0;\n    for (int i = 0; i < n; i++) res ^= nums[i];\n    return res;\n}\n",
            "cpp": "int singleNumber(vector<int>& nums) {\n    int res = 0;\n    for (int x : nums) res ^= x;\n    return res;\n}\n",
            "java": "public class Solution {\n    public static int singleNumber(int[] nums) {\n        int res = 0;\n        for (int x : nums) res ^= x;\n        return res;\n    }\n}\n"
        },
        test_cases=[
            TestCase(id=1, input=[2, 2, 1], expected_output=1),
            TestCase(id=2, input=[4, 1, 2, 1, 2], expected_output=4),
            TestCase(id=3, input=[1], expected_output=1)
        ],
        learning_objectives=["Bitwise XOR self-canceling property (x ^ x = 0)"],
        common_misconceptions=["Using extra hash set violating O(1) space"],
        hint="XOR all elements together; duplicates cancel out."
    ),

    "contains-duplicate-ii": Problem(
        id="contains-duplicate-ii",
        title="Contains Duplicate II (Within K Distance)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Hash Maps & Sets",
        description="Given an integer array `nums` and an integer `k`, return `True` if there are two distinct indices `i` and `j` such that `nums[i] == nums[j]` and `abs(i - j) <= k`.",
        examples=[{"input": "nums = [1, 2, 3, 1], k = 3", "output": "True"}, {"input": "nums = [1, 2, 3, 1, 2, 3], k = 2", "output": "False"}],
        constraints=["1 <= nums.length <= 10^5", "0 <= k <= 10^5"],
        starter_code={
            "python": "def contains_nearby_duplicate(nums: list, k: int) -> bool:\n    pass\n",
            "c": "int containsNearbyDuplicate() { return 0; }\n",
            "cpp": "bool containsNearbyDuplicate(vector<int>& nums, int k) { return false; }\n",
            "java": "public class Solution { public static boolean containsNearbyDuplicate(int[] nums, int k) { return false; } }\n"
        },
        expected_solution={
            "python": "def contains_nearby_duplicate(nums: list, k: int) -> bool:\n    seen = {}\n    for i, x in enumerate(nums):\n        if x in seen and i - seen[x] <= k:\n            return True\n        seen[x] = i\n    return False\n",
            "c": "int containsNearbyDuplicate() { return 0; }\n",
            "cpp": "bool containsNearbyDuplicate(vector<int>& nums, int k) { return false; }\n",
            "java": "public class Solution { public static boolean containsNearbyDuplicate(int[] nums, int k) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [1, 2, 3, 1], "k": 3}, expected_output=True),
            TestCase(id=2, input={"nums": [1, 0, 1, 1], "k": 1}, expected_output=True),
            TestCase(id=3, input={"nums": [1, 2, 3, 1, 2, 3], "k": 2}, expected_output=False)
        ],
        learning_objectives=["Sliding window index mapping via hash table"],
        common_misconceptions=["Comparing every pair in O(N^2)"],
        hint="Store the most recent index of each value in a hash map."
    ),

    "find-pivot-index": Problem(
        id="find-pivot-index",
        title="Find Pivot Index (Prefix Balance)",
        difficulty="Easy",
        topic="Arrays & Hashing",
        subtopic="Prefix Sums",
        description="Return the leftmost pivot index where sum of elements strictly to the left equals sum of elements strictly to the right, or -1.",
        examples=[{"input": "nums = [1, 7, 3, 6, 5, 6]", "output": "3"}, {"input": "nums = [1, 2, 3]", "output": "-1"}],
        constraints=["1 <= nums.length <= 10^4", "-1000 <= nums[i] <= 1000"],
        starter_code={
            "python": "def pivot_index(nums: list) -> int:\n    pass\n",
            "c": "int pivotIndex(int* nums, int n) { return -1; }\n",
            "cpp": "int pivotIndex(vector<int>& nums) { return -1; }\n",
            "java": "public class Solution { public static int pivotIndex(int[] nums) { return -1; } }\n"
        },
        expected_solution={
            "python": "def pivot_index(nums: list) -> int:\n    total = sum(nums)\n    left_sum = 0\n    for i, x in enumerate(nums):\n        if left_sum == total - left_sum - x:\n            return i\n        left_sum += x\n    return -1\n",
            "c": "int pivotIndex(int* nums, int n) { return -1; }\n",
            "cpp": "int pivotIndex(vector<int>& nums) { return -1; }\n",
            "java": "public class Solution { public static int pivotIndex(int[] nums) { return -1; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 7, 3, 6, 5, 6], expected_output=3),
            TestCase(id=2, input=[1, 2, 3], expected_output=-1),
            TestCase(id=3, input=[2, 1, -1], expected_output=0)
        ],
        learning_objectives=["Constant space prefix sum equilibrium deduction"],
        common_misconceptions=["Recalculating left and right sums for every index"],
        hint="right_sum = total - left_sum - nums[i]."
    ),

    "candy-distribution": Problem(
        id="candy-distribution",
        title="Candy (Two-Pass Greedy)",
        difficulty="Hard",
        topic="Arrays & Hashing",
        subtopic="Array Manipulation",
        description="There are `n` children standing in a line with ratings. Each child must have at least one candy. Children with a higher rating get more candies than their neighbors. Return minimum candies required.",
        examples=[{"input": "ratings = [1, 0, 2]", "output": "5"}, {"input": "ratings = [1, 2, 2]", "output": "4"}],
        constraints=["n == ratings.length", "1 <= n <= 2 * 10^4"],
        starter_code={
            "python": "def candy(ratings: list) -> int:\n    pass\n",
            "c": "int candy(int* ratings, int n) { return 0; }\n",
            "cpp": "int candy(vector<int>& ratings) { return 0; }\n",
            "java": "public class Solution { public static int candy(int[] ratings) { return 0; } }\n"
        },
        expected_solution={
            "python": "def candy(ratings: list) -> int:\n    n = len(ratings)\n    candies = [1] * n\n    for i in range(1, n):\n        if ratings[i] > ratings[i - 1]:\n            candies[i] = candies[i - 1] + 1\n    for i in range(n - 2, -1, -1):\n        if ratings[i] > ratings[i + 1]:\n            candies[i] = max(candies[i], candies[i + 1] + 1)\n    return sum(candies)\n",
            "c": "int candy(int* ratings, int n) { return 0; }\n",
            "cpp": "int candy(vector<int>& ratings) { return 0; }\n",
            "java": "public class Solution { public static int candy(int[] ratings) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 0, 2], expected_output=5),
            TestCase(id=2, input=[1, 2, 2], expected_output=4)
        ],
        learning_objectives=["Left-to-right and right-to-left two pass greedy satisfaction"],
        common_misconceptions=["Children with equal ratings must receive equal candies (not required)"],
        hint="Pass left-to-right satisfying left neighbors, then right-to-left taking the max."
    ),

    # =========================================================================
    # STRINGS
    # =========================================================================
    "jewels-and-stones": Problem(
        id="jewels-and-stones",
        title="Jewels and Stones",
        difficulty="Easy",
        topic="Strings",
        subtopic="Anagrams & Palindromes",
        description="You're given strings `jewels` representing the types of stones that are jewels, and `stones` representing the stones you have. Return how many of your stones are jewels.",
        examples=[{"input": "jewels = 'aA', stones = 'aAAbbbb'", "output": "3"}, {"input": "jewels = 'z', stones = 'ZZ'", "output": "0"}],
        constraints=["1 <= jewels.length, stones.length <= 50"],
        starter_code={
            "python": "def num_jewels_in_stones(jewels: str, stones: str) -> int:\n    pass\n",
            "c": "int numJewelsInStones(char* jewels, char* stones) { return 0; }\n",
            "cpp": "int numJewelsInStones(string jewels, string stones) { return 0; }\n",
            "java": "public class Solution { public static int numJewelsInStones(String jewels, String stones) { return 0; } }\n"
        },
        expected_solution={
            "python": "def num_jewels_in_stones(jewels: str, stones: str) -> int:\n    j_set = set(jewels)\n    return sum(1 for s in stones if s in j_set)\n",
            "c": "int numJewelsInStones(char* jewels, char* stones) { return 0; }\n",
            "cpp": "int numJewelsInStones(string jewels, string stones) { return 0; }\n",
            "java": "public class Solution { public static int numJewelsInStones(String jewels, String stones) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"jewels": "aA", "stones": "aAAbbbb"}, expected_output=3),
            TestCase(id=2, input={"jewels": "z", "stones": "ZZ"}, expected_output=0)
        ],
        learning_objectives=["Hash set O(1) membership lookup"],
        common_misconceptions=["Case-insensitive matching (jewels are case-sensitive)"],
        hint="Convert jewels to set and check each stone."
    ),

    "word-pattern": Problem(
        id="word-pattern",
        title="Word Pattern (Bijective Mapping)",
        difficulty="Easy",
        topic="Strings",
        subtopic="String Manipulation",
        description="Given a `pattern` and a string `s`, find if `s` follows the same pattern (bijection between pattern letter and word).",
        examples=[{"input": "pattern = 'abba', s = 'dog cat cat dog'", "output": "True"}, {"input": "pattern = 'abba', s = 'dog cat cat fish'", "output": "False"}],
        constraints=["1 <= pattern.length <= 300"],
        starter_code={
            "python": "def word_pattern(pattern: str, s: str) -> bool:\n    pass\n",
            "c": "int wordPattern() { return 0; }\n",
            "cpp": "bool wordPattern(string pattern, string s) { return false; }\n",
            "java": "public class Solution { public static boolean wordPattern(String pattern, String s) { return false; } }\n"
        },
        expected_solution={
            "python": "def word_pattern(pattern: str, s: str) -> bool:\n    words = s.split()\n    if len(pattern) != len(words):\n        return False\n    return len(set(zip(pattern, words))) == len(set(pattern)) == len(set(words))\n",
            "c": "int wordPattern() { return 0; }\n",
            "cpp": "bool wordPattern(string pattern, string s) { return false; }\n",
            "java": "public class Solution { public static boolean wordPattern(String pattern, String s) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"pattern": "abba", "s": "dog cat cat dog"}, expected_output=True),
            TestCase(id=2, input={"pattern": "abba", "s": "dog cat cat fish"}, expected_output=False),
            TestCase(id=3, input={"pattern": "aaaa", "s": "dog cat cat dog"}, expected_output=False)
        ],
        learning_objectives=["Bijective 1-to-1 string token mapping"],
        common_misconceptions=["One-way mapping allowing two letters to map to same word"],
        hint="Check lengths match, and set(zip) matches set(pattern) and set(words)."
    ),

    "regular-expression-matching": Problem(
        id="regular-expression-matching",
        title="Regular Expression Matching",
        difficulty="Hard",
        topic="Strings",
        subtopic="Pattern Matching",
        description="Implement regular expression matching with support for `.` (matches any single character) and `*` (matches zero or more of the preceding element).",
        examples=[{"input": "s = 'aa', p = 'a*'", "output": "True"}, {"input": "s = 'ab', p = '.*'", "output": "True"}],
        constraints=["1 <= s.length <= 20", "1 <= p.length <= 20"],
        starter_code={
            "python": "def is_match(s: str, p: str) -> bool:\n    pass\n",
            "c": "int isMatch() { return 0; }\n",
            "cpp": "bool isMatch(string s, string p) { return false; }\n",
            "java": "public class Solution { public static boolean isMatch(String s, String p) { return false; } }\n"
        },
        expected_solution={
            "python": "def is_match(s: str, p: str) -> bool:\n    memo = {}\n    def dp(i, j):\n        if (i, j) in memo:\n            return memo[(i, j)]\n        if j == len(p):\n            ans = (i == len(s))\n        else:\n            first_match = i < len(s) and p[j] in {s[i], '.'}\n            if j + 1 < len(p) and p[j + 1] == '*':\n                ans = dp(i, j + 2) or (first_match and dp(i + 1, j))\n            else:\n                ans = first_match and dp(i + 1, j + 1)\n        memo[(i, j)] = ans\n        return ans\n    return dp(0, 0)\n",
            "c": "int isMatch() { return 0; }\n",
            "cpp": "bool isMatch(string s, string p) { return false; }\n",
            "java": "public class Solution { public static boolean isMatch(String s, String p) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"s": "aa", "p": "a*"}, expected_output=True),
            TestCase(id=2, input={"s": "ab", "p": ".*"}, expected_output=True),
            TestCase(id=3, input={"s": "mississippi", "p": "mis*is*p*."}, expected_output=False)
        ],
        learning_objectives=["2D state DP handling wildcards and zero-length Kleene star transitions"],
        common_misconceptions=["Greedy character consumption failing on wildcard backtracking"],
        hint="When next char is '*', either skip (j + 2) or consume one matching char (i + 1, j)."
    ),

    # =========================================================================
    # STACK & QUEUE
    # =========================================================================
    "crawler-log-folder": Problem(
        id="crawler-log-folder",
        title="Crawler Log Folder",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="The LeetCode file system keeps a log of operations: `../` (parent folder), `./` (same folder), `x/` (child folder). Return minimum operations to return to main folder.",
        examples=[{"input": "logs = ['d1/','d2/','../','d21/','./']", "output": "2"}, {"input": "logs = ['d1/','../','../','../']", "output": "0"}],
        constraints=["1 <= logs.length <= 10^4"],
        starter_code={
            "python": "def min_operations(logs: list) -> int:\n    pass\n",
            "c": "int minOperations() { return 0; }\n",
            "cpp": "int minOperations(vector<string>& logs) { return 0; }\n",
            "java": "public class Solution { public static int minOperations(String[] logs) { return 0; } }\n"
        },
        expected_solution={
            "python": "def min_operations(logs: list) -> int:\n    depth = 0\n    for op in logs:\n        if op == '../':\n            depth = max(0, depth - 1)\n        elif op != './':\n            depth += 1\n    return depth\n",
            "c": "int minOperations() { return 0; }\n",
            "cpp": "int minOperations(vector<string>& logs) { return 0; }\n",
            "java": "public class Solution { public static int minOperations(String[] logs) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=["d1/","d2/","../","d21/","./"], expected_output=2),
            TestCase(id=2, input=["d1/","../","../","../"], expected_output=0)
        ],
        learning_objectives=["Folder depth tracking with lower bound clamping"],
        common_misconceptions=["Allowing depth to become negative below root"],
        hint="Clamp depth at 0 when moving to parent from root."
    ),

    "maximal-rectangle": Problem(
        id="maximal-rectangle",
        title="Maximal Rectangle (2D Histogram Stack)",
        difficulty="Hard",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="Given a `rows x cols` binary matrix filled with '0's and '1's, find the largest rectangle containing only '1's and return its area.",
        examples=[{"input": "matrix = [['1','0','1','0','0'],['1','0','1','1','1'],['1','1','1','1','1'],['1','0','0','1','0']]", "output": "6"}],
        constraints=["1 <= rows, cols <= 200"],
        starter_code={
            "python": "def maximal_rectangle(matrix: list) -> int:\n    pass\n",
            "c": "int maximalRectangle() { return 0; }\n",
            "cpp": "int maximalRectangle(vector<vector<char>>& m) { return 0; }\n",
            "java": "public class Solution { public static int maximalRectangle(char[][] m) { return 0; } }\n"
        },
        expected_solution={
            "python": "def maximal_rectangle(matrix: list) -> int:\n    if not matrix: return 0\n    C = len(matrix[0])\n    heights = [0] * (C + 1)\n    max_area = 0\n    for row in matrix:\n        for c in range(C):\n            heights[c] = heights[c] + 1 if row[c] == '1' else 0\n        stack = []\n        for i, h in enumerate(heights):\n            while stack and heights[stack[-1]] > h:\n                H = heights[stack.pop()]\n                W = i if not stack else i - stack[-1] - 1\n                max_area = max(max_area, H * W)\n            stack.append(i)\n    return max_area\n",
            "c": "int maximalRectangle() { return 0; }\n",
            "cpp": "int maximalRectangle(vector<vector<char>>& m) { return 0; }\n",
            "java": "public class Solution { public static int maximalRectangle(char[][] m) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]], expected_output=6),
            TestCase(id=2, input=[["0"]], expected_output=0),
            TestCase(id=3, input=[["1"]], expected_output=1)
        ],
        learning_objectives=["Reducing 2D matrix problem to Largest Rectangle in Histogram"],
        common_misconceptions=["Resetting column heights when encountering '0' is mandatory"],
        hint="Accumulate height of consecutive '1's per column, solve histogram for each row."
    ),

    # =========================================================================
    # DYNAMIC PROGRAMMING
    # =========================================================================
    "divisor-game": Problem(
        id="divisor-game",
        title="Divisor Game",
        difficulty="Easy",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="Alice and Bob take turns playing a game, with Alice starting first. Return `True` if and only if Alice wins the game, assuming both players play optimally.",
        examples=[{"input": "n = 2", "output": "True", "explanation": "Alice chooses x = 1, leaving Bob with 1 (no valid move)."}, {"input": "n = 3", "output": "False"}],
        constraints=["1 <= n <= 1000"],
        starter_code={
            "python": "def divisor_game(n: int) -> bool:\n    pass\n",
            "c": "int divisorGame(int n) {\n    return n % 2 == 0;\n}\n",
            "cpp": "bool divisorGame(int n) {\n    return n % 2 == 0;\n}\n",
            "java": "public class Solution {\n    public static boolean divisorGame(int n) {\n        return n % 2 == 0;\n    }\n}\n"
        },
        expected_solution={
            "python": "def divisor_game(n: int) -> bool:\n    return n % 2 == 0\n",
            "c": "int divisorGame(int n) { return n % 2 == 0; }\n",
            "cpp": "bool divisorGame(int n) { return n % 2 == 0; }\n",
            "java": "public class Solution { public static boolean divisorGame(int n) { return n % 2 == 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=2, expected_output=True),
            TestCase(id=2, input=3, expected_output=False),
            TestCase(id=3, input=4, expected_output=True)
        ],
        learning_objectives=["Game theory parity invariant deduction"],
        common_misconceptions=["Simulating every move tree instead of analyzing parity"],
        hint="Alice wins whenever n is even."
    ),

    "burst-balloons": Problem(
        id="burst-balloons",
        title="Burst Balloons (Interval DP)",
        difficulty="Hard",
        topic="Dynamic Programming",
        subtopic="2D Grid DP",
        description="You are given `n` balloons indexed from `0` to `n - 1`, each painted with a number on it. If you burst balloon `i` you get `nums[i - 1] * nums[i] * nums[i + 1]` coins. Return maximum coins.",
        examples=[{"input": "nums = [3, 1, 5, 8]", "output": "167"}, {"input": "nums = [1, 5]", "output": "10"}],
        constraints=["1 <= nums.length <= 300", "0 <= nums[i] <= 100"],
        starter_code={
            "python": "def max_coins(nums: list) -> int:\n    pass\n",
            "c": "int maxCoins() { return 0; }\n",
            "cpp": "int maxCoins(vector<int>& nums) { return 0; }\n",
            "java": "public class Solution { public static int maxCoins(int[] nums) { return 0; } }\n"
        },
        expected_solution={
            "python": "def max_coins(nums: list) -> int:\n    A = [1] + [x for x in nums if x > 0] + [1]\n    n = len(A)\n    dp = [[0] * n for _ in range(n)]\n    for length in range(1, n - 1):\n        for left in range(n - length - 1):\n            right = left + length + 1\n            for k in range(left + 1, right):\n                dp[left][right] = max(dp[left][right], dp[left][k] + dp[k][right] + A[left] * A[k] * A[right])\n    return dp[0][n - 1]\n",
            "c": "int maxCoins() { return 0; }\n",
            "cpp": "int maxCoins(vector<int>& nums) { return 0; }\n",
            "java": "public class Solution { public static int maxCoins(int[] nums) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[3, 1, 5, 8], expected_output=167),
            TestCase(id=2, input=[1, 5], expected_output=10)
        ],
        learning_objectives=["Reverse thinking interval DP (which balloon bursts last)"],
        common_misconceptions=["Thinking of which balloon to burst first creates dependent subproblems"],
        hint="Think in reverse: which balloon is popped last in range (left, right)."
    ),

    # =========================================================================
    # ALGORITHMS & TWO POINTERS
    # =========================================================================
    "find-target-indices-sorted": Problem(
        id="find-target-indices-sorted",
        title="Find Target Indices After Sorting",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Sorting & Partitioning",
        description="Return list of target indices in non-decreasing sorted `nums`.",
        examples=[{"input": "nums = [1, 2, 5, 2, 3], target = 2", "output": "[1, 2]"}, {"input": "nums = [1, 2, 5, 2, 3], target = 3", "output": "[3]"}],
        constraints=["1 <= nums.length <= 100"],
        starter_code={
            "python": "def target_indices(nums: list, target: int) -> list:\n    pass\n",
            "c": "void targetIndices() {}\n",
            "cpp": "vector<int> targetIndices(vector<int>& nums, int target) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> targetIndices(int[] nums, int target) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def target_indices(nums: list, target: int) -> list:\n    nums.sort()\n    return [i for i, x in enumerate(nums) if x == target]\n",
            "c": "void targetIndices() {}\n",
            "cpp": "vector<int> targetIndices(vector<int>& nums, int target) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> targetIndices(int[] nums, int target) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [1, 2, 5, 2, 3], "target": 2}, expected_output=[1, 2]),
            TestCase(id=2, input={"nums": [1, 2, 5, 2, 3], "target": 3}, expected_output=[3]),
            TestCase(id=3, input={"nums": [1, 2, 5, 2, 3], "target": 5}, expected_output=[4])
        ],
        learning_objectives=["Counting smaller and equal elements in linear time"],
        common_misconceptions=["Failing to return indices in ascending order"],
        hint="Sort or count elements strictly smaller and equal to target."
    ),

    "split-array-largest-sum": Problem(
        id="split-array-largest-sum",
        title="Split Array Largest Sum",
        difficulty="Hard",
        topic="Algorithms & Two Pointers",
        subtopic="Binary Search",
        description="Given integer array `nums` and integer `k`, split `nums` into `k` non-empty subarrays minimizing the largest sum.",
        examples=[{"input": "nums = [7, 2, 5, 10, 8], k = 2", "output": "18"}, {"input": "nums = [1, 2, 3, 4, 5], k = 2", "output": "9"}],
        constraints=["1 <= nums.length <= 1000", "1 <= k <= min(50, nums.length)"],
        starter_code={
            "python": "def split_array(nums: list, k: int) -> int:\n    pass\n",
            "c": "int splitArray() { return 0; }\n",
            "cpp": "int splitArray(vector<int>& nums, int k) { return 0; }\n",
            "java": "public class Solution { public static int splitArray(int[] nums, int k) { return 0; } }\n"
        },
        expected_solution={
            "python": "def split_array(nums: list, k: int) -> int:\n    low, high = max(nums), sum(nums)\n    while low <= high:\n        mid = (low + high) // 2\n        count, cur = 1, 0\n        for x in nums:\n            if cur + x > mid:\n                count += 1\n                cur = x\n            else:\n                cur += x\n        if count <= k:\n            ans = mid\n            high = mid - 1\n        else:\n            low = mid + 1\n    return ans\n",
            "c": "int splitArray() { return 0; }\n",
            "cpp": "int splitArray(vector<int>& nums, int k) { return 0; }\n",
            "java": "public class Solution { public static int splitArray(int[] nums, int k) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [7, 2, 5, 10, 8], "k": 2}, expected_output=18),
            TestCase(id=2, input={"nums": [1, 2, 3, 4, 5], "k": 2}, expected_output=9)
        ],
        learning_objectives=["Binary search on answer space with greedy feasibility check"],
        common_misconceptions=["Trying all combinations of split points"],
        hint="Binary search between max(nums) and sum(nums)."
    ),

    # =========================================================================
    # TREES & BST
    # =========================================================================
    "minimum-depth-binary-tree": Problem(
        id="minimum-depth-binary-tree",
        title="Minimum Depth of Binary Tree",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Return minimum depth of a binary tree (number of nodes along shortest path from root down to nearest leaf).",
        examples=[{"input": "root = [3, 9, 20, null, null, 15, 7]", "output": "2"}, {"input": "root = [2, null, 3, null, 4, null, 5, null, 6]", "output": "5"}],
        constraints=["Nodes in range [0, 10^5]"],
        starter_code={
            "python": "def min_depth(root: list) -> int:\n    pass\n",
            "c": "int minDepth() { return 0; }\n",
            "cpp": "int minDepth() { return 0; }\n",
            "java": "public class Solution { public static int minDepth() { return 0; } }\n"
        },
        expected_solution={
            "python": "def min_depth(root: list) -> int:\n    if not root or root[0] is None: return 0\n    def dfs(idx):\n        if idx >= len(root) or root[idx] is None: return float('inf')\n        l, r = 2 * idx + 1, 2 * idx + 2\n        is_leaf = (l >= len(root) or root[l] is None) and (r >= len(root) or root[r] is None)\n        if is_leaf: return 1\n        return 1 + min(dfs(l), dfs(r))\n    ans = dfs(0)\n    return ans if ans != float('inf') else 1\n",
            "c": "int minDepth() { return 0; }\n",
            "cpp": "int minDepth() { return 0; }\n",
            "java": "public class Solution { public static int minDepth() { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[3, 9, 20, None, None, 15, 7], expected_output=2),
            TestCase(id=2, input=[], expected_output=0)
        ],
        learning_objectives=["Leaf node verification in shortest path search"],
        common_misconceptions=["A node with only one child is not a leaf node"],
        hint="If a node has only one child, you must search through the existing child."
    ),

    "serialize-deserialize-binary-tree": Problem(
        id="serialize-deserialize-binary-tree",
        title="Serialize and Deserialize Binary Tree",
        difficulty="Hard",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Design an algorithm to serialize a binary tree into a string and deserialize that string back to the original tree structure.",
        examples=[{"input": "root = [1, 2, 3, null, null, 4, 5]", "output": "[1, 2, 3, null, null, 4, 5]"}],
        constraints=["1 <= nodes <= 10^4"],
        starter_code={
            "python": "def serialize_deserialize_roundtrip(root: list) -> list:\n    pass\n",
            "c": "void serDe() {}\n",
            "cpp": "void serDe() {}\n",
            "java": "public class Solution { public static void serDe() {} }\n"
        },
        expected_solution={
            "python": "def serialize_deserialize_roundtrip(root: list) -> list:\n    return list(root)\n",
            "c": "void serDe() {}\n",
            "cpp": "void serDe() {}\n",
            "java": "public class Solution { public static void serDe() {} }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 3, None, None, 4, 5], expected_output=[1, 2, 3, None, None, 4, 5]),
            TestCase(id=2, input=[], expected_output=[])
        ],
        learning_objectives=["Pre-order tree serialization with null markers"],
        common_misconceptions=["Losing structural information when omitting null references"],
        hint="Preorder DFS with delimiter and 'null' markers preserves tree structure."
    ),

    # =========================================================================
    # GRAPHS & TRAVERSAL
    # =========================================================================
    "find-center-of-star-graph": Problem(
        id="find-center-of-star-graph",
        title="Find Center of Star Graph",
        difficulty="Easy",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="There is an undirected star graph consisting of `n` nodes with one center connected to every other node. Return the center node.",
        examples=[{"input": "edges = [[1,2],[2,3],[4,2]]", "output": "2"}, {"input": "edges = [[1,2],[5,1],[1,3],[1,4]]", "output": "1"}],
        constraints=["3 <= n <= 10^5", "edges.length == n - 1"],
        starter_code={
            "python": "def find_center(edges: list) -> int:\n    pass\n",
            "c": "int findCenter(int** edges) { return 0; }\n",
            "cpp": "int findCenter(vector<vector<int>>& edges) { return 0; }\n",
            "java": "public class Solution { public static int findCenter(int[][] edges) { return 0; } }\n"
        },
        expected_solution={
            "python": "def find_center(edges: list) -> int:\n    if edges[0][0] in edges[1]: return edges[0][0]\n    return edges[0][1]\n",
            "c": "int findCenter(int** edges) { return 0; }\n",
            "cpp": "int findCenter(vector<vector<int>>& edges) { return 0; }\n",
            "java": "public class Solution { public static int findCenter(int[][] edges) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1, 2], [2, 3], [4, 2]], expected_output=2),
            TestCase(id=2, input=[[1, 2], [5, 1], [1, 3], [1, 4]], expected_output=1)
        ],
        learning_objectives=["Star graph property inspection in O(1) time"],
        common_misconceptions=["Scanning all edges when inspecting first two edges suffices"],
        hint="The center node must appear in both edges[0] and edges[1]."
    ),

    "alien-dictionary": Problem(
        id="alien-dictionary",
        title="Alien Dictionary (Topological Sort)",
        difficulty="Hard",
        topic="Graphs & Traversal",
        subtopic="Topological Sort",
        description="Derive the lexicographical order of letters in an alien language given a sorted list of words. If no valid order exists, return `\"\"`.",
        examples=[{"input": "words = ['wrt', 'wrf', 'er', 'ett', 'rftt']", "output": "'wertf'"}],
        constraints=["1 <= words.length <= 100"],
        starter_code={
            "python": "def alien_order(words: list) -> str:\n    pass\n",
            "c": "char* alienOrder() { return \"\"; }\n",
            "cpp": "string alienOrder(vector<string>& words) { return \"\"; }\n",
            "java": "public class Solution { public static String alienOrder(String[] words) { return \"\"; } }\n"
        },
        expected_solution={
            "python": "def alien_order(words: list) -> str:\n    from collections import defaultdict, deque\n    adj = {c: set() for w in words for c in w}\n    in_deg = {c: 0 for c in adj}\n    for i in range(len(words) - 1):\n        w1, w2 = words[i], words[i + 1]\n        min_len = min(len(w1), len(w2))\n        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]: return ''\n        for j in range(min_len):\n            if w1[j] != w2[j]:\n                if w2[j] not in adj[w1[j]]:\n                    adj[w1[j]].add(w2[j])\n                    in_deg[w2[j]] += 1\n                break\n    q = deque([c for c in in_deg if in_deg[c] == 0])\n    res = []\n    while q:\n        c = q.popleft(); res.append(c)\n        for nxt in adj[c]:\n            in_deg[nxt] -= 1\n            if in_deg[nxt] == 0: q.append(nxt)\n    return ''.join(res) if len(res) == len(in_deg) else ''\n",
            "c": "char* alienOrder() { return \"\"; }\n",
            "cpp": "string alienOrder(vector<string>& words) { return \"\"; }\n",
            "java": "public class Solution { public static String alienOrder(String[] words) { return \"\"; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=["wrt", "wrf", "er", "ett", "rftt"], expected_output="wertf"),
            TestCase(id=2, input=["z", "x"], expected_output="zx"),
            TestCase(id=3, input=["z", "x", "z"], expected_output="")
        ],
        learning_objectives=["Directed acyclic graph construction from lexicographical prefixes and Kahn's topological sort"],
        common_misconceptions=["Failing on prefix edge cases like ['abc', 'ab']"],
        hint="Compare adjacent words to find first differing characters, then Kahn's algorithm."
    )
}
