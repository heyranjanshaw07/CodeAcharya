from typing import Dict
from models import Problem, TestCase

MORE_PROBLEMS: Dict[str, Problem] = {
    # =========================================================================
    # STACK & QUEUE (6 more -> total 15+)
    # =========================================================================
    "implement-queue-using-stacks": Problem(
        id="implement-queue-using-stacks",
        title="Implement Queue using Stacks",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="BFS Queue",
        description="Implement a first in first out (FIFO) queue using only two stacks.",
        examples=[{"input": "ops = ['push', 'push', 'peek', 'pop', 'empty'], vals = [1, 2, null, null, null]", "output": "[null, null, 1, 1, false]"}],
        constraints=["1 <= x <= 9", "At most 100 calls will be made"],
        starter_code={
            "python": "def queue_stacks(ops: list, vals: list) -> list:\n    pass\n",
            "c": "void queueStacks() {}\n",
            "cpp": "void queueStacks() {}\n",
            "java": "public class Solution { public static void queueStacks() {} }\n"
        },
        expected_solution={
            "python": "def queue_stacks(ops: list, vals: list) -> list:\n    s1, s2, out = [], [], []\n    for op, v in zip(ops, vals):\n        if op == 'push': s1.append(v); out.append(None)\n        elif op == 'pop':\n            if not s2:\n                while s1: s2.append(s1.pop())\n            out.append(s2.pop())\n        elif op == 'peek':\n            if not s2:\n                while s1: s2.append(s1.pop())\n            out.append(s2[-1])\n        elif op == 'empty': out.append(not s1 and not s2)\n    return out\n",
            "c": "void queueStacks() {}\n",
            "cpp": "void queueStacks() {}\n",
            "java": "public class Solution { public static void queueStacks() {} }\n"
        },
        test_cases=[
            TestCase(id=1, input={"ops": ["push", "push", "peek", "pop", "empty"], "vals": [1, 2, None, None, None]}, expected_output=[None, None, 1, 1, False])
        ],
        learning_objectives=["Amortized O(1) queue operations using two stacks"],
        common_misconceptions=["Shuffling elements on every single operation"],
        hint="Transfer elements from s1 to s2 only when s2 is empty."
    ),

    "remove-outermost-parentheses": Problem(
        id="remove-outermost-parentheses",
        title="Remove Outermost Parentheses",
        difficulty="Easy",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="A valid parentheses string is primitive if it is non-empty and cannot be split into two valid parentheses strings. Remove the outermost parentheses of every primitive component.",
        examples=[{"input": "s = '(()())(())'", "output": "'()()()'"}],
        constraints=["1 <= s.length <= 10^5"],
        starter_code={
            "python": "def remove_outer_parentheses(s: str) -> str:\n    pass\n",
            "c": "char* removeOuterParentheses() { return \"\"; }\n",
            "cpp": "string removeOuterParentheses(string s) { return \"\"; }\n",
            "java": "public class Solution { public static String removeOuterParentheses(String s) { return \"\"; } }\n"
        },
        expected_solution={
            "python": "def remove_outer_parentheses(s: str) -> str:\n    res, depth = [], 0\n    for ch in s:\n        if ch == '(':\n            if depth > 0: res.append(ch)\n            depth += 1\n        else:\n            depth -= 1\n            if depth > 0: res.append(ch)\n    return ''.join(res)\n",
            "c": "char* removeOuterParentheses() { return \"\"; }\n",
            "cpp": "string removeOuterParentheses(string s) { return \"\"; }\n",
            "java": "public class Solution { public static String removeOuterParentheses(String s) { return \"\"; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="(()())(())", expected_output="()()()"),
            TestCase(id=2, input="(()())(())(()(()))", expected_output="()()()()(())")
        ],
        learning_objectives=["Parentheses depth tracking"],
        common_misconceptions=["Incorrectly retaining outer parentheses"],
        hint="Track depth. Append '(' if depth > 0; append ')' if depth > 1."
    ),

    "next-greater-element-ii": Problem(
        id="next-greater-element-ii",
        title="Next Greater Element II (Circular)",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="Given a circular integer array `nums`, return the next greater number for every element.",
        examples=[{"input": "nums = [1, 2, 1]", "output": "[2, -1, 2]"}],
        constraints=["1 <= nums.length <= 10^4"],
        starter_code={
            "python": "def next_greater_circular(nums: list) -> list:\n    pass\n",
            "c": "void nextGreaterCircular() {}\n",
            "cpp": "vector<int> nextGreaterCircular(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static int[] nextGreaterCircular(int[] nums) { return new int[0]; } }\n"
        },
        expected_solution={
            "python": "def next_greater_circular(nums: list) -> list:\n    n = len(nums)\n    res = [-1] * n\n    st = []\n    for i in range(2 * n):\n        idx = i % n\n        while st and nums[st[-1]] < nums[idx]:\n            res[st.pop()] = nums[idx]\n        if i < n: st.append(idx)\n    return res\n",
            "c": "void nextGreaterCircular() {}\n",
            "cpp": "vector<int> nextGreaterCircular(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static int[] nextGreaterCircular(int[] nums) { return new int[0]; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 1], expected_output=[2, -1, 2]),
            TestCase(id=2, input=[1, 2, 3, 4, 3], expected_output=[2, 3, 4, -1, 4])
        ],
        learning_objectives=["Monotonic stack over circular arrays using 2*N modulo indexing"],
        common_misconceptions=["Failing to check elements before current index in circular wrap"],
        hint="Loop from 0 to 2*n - 1 using index modulo n."
    ),

    "online-stock-span": Problem(
        id="online-stock-span",
        title="Online Stock Span",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="Calculate the span of stock's price today (maximum number of consecutive days price was <= today).",
        examples=[{"input": "prices = [100, 80, 60, 70, 60, 75, 85]", "output": "[1, 1, 1, 2, 1, 4, 6]"}],
        constraints=["1 <= prices.length <= 10^4"],
        starter_code={
            "python": "def stock_spanner_runner(prices: list) -> list:\n    pass\n",
            "c": "void stockSpanner() {}\n",
            "cpp": "vector<int> stockSpanner(vector<int>& p) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> stockSpanner(int[] p) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def stock_spanner_runner(prices: list) -> list:\n    st, res = [], []\n    for p in prices:\n        span = 1\n        while st and st[-1][0] <= p:\n            span += st.pop()[1]\n        st.append((p, span))\n        res.append(span)\n    return res\n",
            "c": "void stockSpanner() {}\n",
            "cpp": "vector<int> stockSpanner(vector<int>& p) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> stockSpanner(int[] p) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[100, 80, 60, 70, 60, 75, 85], expected_output=[1, 1, 1, 2, 1, 4, 6])
        ],
        learning_objectives=["Monotonic decreasing stack caching cumulative spans"],
        common_misconceptions=["Traversing back linearly every day in O(N^2)"],
        hint="Push (price, span) tuples onto stack."
    ),

    "simplify-path": Problem(
        id="simplify-path",
        title="Simplify Path (Unix File System)",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="Given an absolute Unix-style file path, simplify it to its canonical path.",
        examples=[{"input": "path = '/home/'", "output": "'/home'"}, {"input": "path = '/../'", "output": "'/'"}],
        constraints=["1 <= path.length <= 3000"],
        starter_code={
            "python": "def simplify_path(path: str) -> str:\n    pass\n",
            "c": "char* simplifyPath() { return \"/\"; }\n",
            "cpp": "string simplifyPath(string p) { return \"/\"; }\n",
            "java": "public class Solution { public static String simplifyPath(String p) { return \"/\"; } }\n"
        },
        expected_solution={
            "python": "def simplify_path(path: str) -> str:\n    st = []\n    for p in path.split('/'):\n        if not p or p == '.': continue\n        elif p == '..':\n            if st: st.pop()\n        else: st.append(p)\n    return '/' + '/'.join(st)\n",
            "c": "char* simplifyPath() { return \"/\"; }\n",
            "cpp": "string simplifyPath(string p) { return \"/\"; }\n",
            "java": "public class Solution { public static String simplifyPath(String p) { return \"/\"; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="/home/", expected_output="/home"),
            TestCase(id=2, input="/../", expected_output="/"),
            TestCase(id=3, input="/home//foo/", expected_output="/home/foo"),
            TestCase(id=4, input="/a/./b/../../c/", expected_output="/c")
        ],
        learning_objectives=["Stack directory path navigation resolution"],
        common_misconceptions=["Popping root slash or leaving multiple consecutive slashes"],
        hint="Split by '/' and push directory names, pop on '..'."
    ),

    # =========================================================================
    # STRINGS (5 more -> total 16+)
    # =========================================================================
    "ransom-note": Problem(
        id="ransom-note",
        title="Ransom Note",
        difficulty="Easy",
        topic="Strings",
        subtopic="Anagrams & Palindromes",
        description="Return `True` if `ransomNote` can be constructed by using characters from `magazine`.",
        examples=[{"input": "ransomNote = 'a', magazine = 'b'", "output": "False"}, {"input": "ransomNote = 'aa', magazine = 'aab'", "output": "True"}],
        constraints=["1 <= ransomNote.length, magazine.length <= 10^5"],
        starter_code={
            "python": "def can_construct(ransomNote: str, magazine: str) -> bool:\n    pass\n",
            "c": "int canConstruct() { return 0; }\n",
            "cpp": "bool canConstruct(string r, string m) { return false; }\n",
            "java": "public class Solution { public static boolean canConstruct(String r, String m) { return false; } }\n"
        },
        expected_solution={
            "python": "def can_construct(ransomNote: str, magazine: str) -> bool:\n    from collections import Counter\n    cr, cm = Counter(ransomNote), Counter(magazine)\n    return all(cm[k] >= v for k, v in cr.items())\n",
            "c": "int canConstruct() { return 0; }\n",
            "cpp": "bool canConstruct(string r, string m) { return false; }\n",
            "java": "public class Solution { public static boolean canConstruct(String r, String m) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"ransomNote": "a", "magazine": "b"}, expected_output=False),
            TestCase(id=2, input={"ransomNote": "aa", "magazine": "aab"}, expected_output=True)
        ],
        learning_objectives=["Letter frequency sufficiency check"],
        common_misconceptions=["Reusing magazine characters without decrementing"],
        hint="Count magazine character frequencies and ensure they cover ransomNote."
    ),

    "length-of-last-word": Problem(
        id="length-of-last-word",
        title="Length of Last Word",
        difficulty="Easy",
        topic="Strings",
        subtopic="String Manipulation",
        description="Given a string `s` consisting of words and spaces, return the length of the last word in the string.",
        examples=[{"input": "s = 'Hello World'", "output": "5"}, {"input": "s = '   fly me   to   the moon  '", "output": "4"}],
        constraints=["1 <= s.length <= 10^4"],
        starter_code={
            "python": "def length_of_last_word(s: str) -> int:\n    pass\n",
            "c": "int lengthOfLastWord(char* s) { return 0; }\n",
            "cpp": "int lengthOfLastWord(string s) { return 0; }\n",
            "java": "public class Solution { public static int lengthOfLastWord(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def length_of_last_word(s: str) -> int:\n    w = s.strip().split()\n    return len(w[-1]) if w else 0\n",
            "c": "int lengthOfLastWord(char* s) { return 0; }\n",
            "cpp": "int lengthOfLastWord(string s) { return 0; }\n",
            "java": "public class Solution { public static int lengthOfLastWord(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="Hello World", expected_output=5),
            TestCase(id=2, input="   fly me   to   the moon  ", expected_output=4),
            TestCase(id=3, input="luffy is still joyboy", expected_output=6)
        ],
        learning_objectives=["String trimming and tokenization"],
        common_misconceptions=["Counting trailing whitespace as characters"],
        hint="Trim trailing spaces and scan backwards until next space."
    ),

    "reverse-vowels-of-string": Problem(
        id="reverse-vowels-of-string",
        title="Reverse Vowels of a String",
        difficulty="Easy",
        topic="Strings",
        subtopic="String Manipulation",
        description="Given string `s`, reverse only all the vowels in the string and return it.",
        examples=[{"input": "s = 'hello'", "output": "'holle'"}, {"input": "s = 'leetcode'", "output": "'leotcede'"}],
        constraints=["1 <= s.length <= 3 * 10^5"],
        starter_code={
            "python": "def reverse_vowels(s: str) -> str:\n    pass\n",
            "c": "char* reverseVowels() { return \"\"; }\n",
            "cpp": "string reverseVowels(string s) { return \"\"; }\n",
            "java": "public class Solution { public static String reverseVowels(String s) { return \"\"; } }\n"
        },
        expected_solution={
            "python": "def reverse_vowels(s: str) -> str:\n    v = set('aeiouAEIOU')\n    chars = list(s)\n    l, r = 0, len(chars) - 1\n    while l < r:\n        while l < r and chars[l] not in v: l += 1\n        while l < r and chars[r] not in v: r -= 1\n        chars[l], chars[r] = chars[r], chars[l]\n        l += 1; r -= 1\n    return ''.join(chars)\n",
            "c": "char* reverseVowels() { return \"\"; }\n",
            "cpp": "string reverseVowels(string s) { return \"\"; }\n",
            "java": "public class Solution { public static String reverseVowels(String s) { return \"\"; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="hello", expected_output="holle"),
            TestCase(id=2, input="leetcode", expected_output="leotcede")
        ],
        learning_objectives=["Two-pointer inward traversal on selected characters"],
        common_misconceptions=["Missing uppercase vowels like 'E'"],
        hint="Skip consonants, swap vowels from left and right."
    ),

    "minimum-window-substring": Problem(
        id="minimum-window-substring",
        title="Minimum Window Substring",
        difficulty="Hard",
        topic="Strings",
        subtopic="Sliding Window",
        description="Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window.",
        examples=[{"input": "s = 'ADOBECODEBANC', t = 'ABC'", "output": "'BANC'"}],
        constraints=["1 <= s.length, t.length <= 10^5"],
        starter_code={
            "python": "def min_window(s: str, t: str) -> str:\n    pass\n",
            "c": "char* minWindow() { return \"\"; }\n",
            "cpp": "string minWindow(string s, string t) { return \"\"; }\n",
            "java": "public class Solution { public static String minWindow(String s, String t) { return \"\"; } }\n"
        },
        expected_solution={
            "python": "def min_window(s: str, t: str) -> str:\n    from collections import Counter\n    if not t or not s: return ''\n    t_count = Counter(t)\n    window = {}\n    have, need = 0, len(t_count)\n    res, res_len = [-1, -1], float('inf')\n    l = 0\n    for r in range(len(s)):\n        c = s[r]\n        window[c] = window.get(c, 0) + 1\n        if c in t_count and window[c] == t_count[c]: have += 1\n        while have == need:\n            if (r - l + 1) < res_len:\n                res = [l, r]; res_len = r - l + 1\n            window[s[l]] -= 1\n            if s[l] in t_count and window[s[l]] < t_count[s[l]]: have -= 1\n            l += 1\n    return s[res[0]:res[1] + 1] if res_len != float('inf') else ''\n",
            "c": "char* minWindow() { return \"\"; }\n",
            "cpp": "string minWindow(string s, string t) { return \"\"; }\n",
            "java": "public class Solution { public static String minWindow(String s, String t) { return \"\"; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"s": "ADOBECODEBANC", "t": "ABC"}, expected_output="BANC"),
            TestCase(id=2, input={"s": "a", "t": "a"}, expected_output="a"),
            TestCase(id=3, input={"s": "a", "t": "aa"}, expected_output="")
        ],
        learning_objectives=["Variable size sliding window with frequency matching"],
        common_misconceptions=["Premature window contraction before condition is met"],
        hint="Expand right until all characters of t are matched, then shrink left."
    ),

    # =========================================================================
    # DYNAMIC PROGRAMMING (5 more -> total 17+)
    # =========================================================================
    "counting-bits-dp": Problem(
        id="counting-bits-dp",
        title="Counting Bits (DP)",
        difficulty="Easy",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="Given integer `n`, return an array `ans` of length `n + 1` where `ans[i]` is the number of 1's in the binary representation of `i`.",
        examples=[{"input": "n = 2", "output": "[0, 1, 1]"}, {"input": "n = 5", "output": "[0, 1, 1, 2, 1, 2]"}],
        constraints=["0 <= n <= 10^5"],
        starter_code={
            "python": "def count_bits(n: int) -> list:\n    pass\n",
            "c": "void countBits() {}\n",
            "cpp": "vector<int> countBits(int n) { return {}; }\n",
            "java": "public class Solution { public static int[] countBits(int n) { return new int[0]; } }\n"
        },
        expected_solution={
            "python": "def count_bits(n: int) -> list:\n    dp = [0] * (n + 1)\n    for i in range(1, n + 1): dp[i] = dp[i >> 1] + (i & 1)\n    return dp\n",
            "c": "void countBits() {}\n",
            "cpp": "vector<int> countBits(int n) { vector<int> dp(n+1,0); for(int i=1;i<=n;i++) dp[i]=dp[i>>1]+(i&1); return dp; }\n",
            "java": "public class Solution { public static int[] countBits(int n) { int[] dp=new int[n+1]; for(int i=1;i<=n;i++) dp[i]=dp[i>>1]+(i&1); return dp; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=2, expected_output=[0, 1, 1]),
            TestCase(id=2, input=5, expected_output=[0, 1, 1, 2, 1, 2])
        ],
        learning_objectives=["Bitwise DP recurrence dp[i] = dp[i >> 1] + (i & 1)"],
        common_misconceptions=["Calling bin().count() individually per number"],
        hint="dp[i] = dp[i // 2] + (i % 2)."
    ),

    "partition-equal-subset-sum": Problem(
        id="partition-equal-subset-sum",
        title="Partition Equal Subset Sum",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="Knapsack & Subsets",
        description="Given an integer array `nums`, return `True` if it can be partitioned into two subsets with equal sum.",
        examples=[{"input": "nums = [1, 5, 11, 5]", "output": "True"}, {"input": "nums = [1, 2, 3, 5]", "output": "False"}],
        constraints=["1 <= nums.length <= 200", "1 <= nums[i] <= 100"],
        starter_code={
            "python": "def can_partition(nums: list) -> bool:\n    pass\n",
            "c": "int canPartition() { return 0; }\n",
            "cpp": "bool canPartition(vector<int>& nums) { return false; }\n",
            "java": "public class Solution { public static boolean canPartition(int[] nums) { return false; } }\n"
        },
        expected_solution={
            "python": "def can_partition(nums: list) -> bool:\n    total = sum(nums)\n    if total % 2 != 0: return False\n    target = total // 2\n    dp = {0}\n    for x in nums:\n        dp |= {curr + x for curr in dp if curr + x <= target}\n        if target in dp: return True\n    return False\n",
            "c": "int canPartition() { return 0; }\n",
            "cpp": "bool canPartition(vector<int>& nums) { return false; }\n",
            "java": "public class Solution { public static boolean canPartition(int[] nums) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 5, 11, 5], expected_output=True),
            TestCase(id=2, input=[1, 2, 3, 5], expected_output=False)
        ],
        learning_objectives=["0/1 Knapsack reduction to subset sum target"],
        common_misconceptions=["Odd total sum cannot be partitioned"],
        hint="If total sum is odd return False. Check if subset sums to total // 2."
    ),

    "minimum-path-sum": Problem(
        id="minimum-path-sum",
        title="Minimum Path Sum (2D Grid)",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="2D Grid DP",
        description="Find path from top left to bottom right of `m x n` grid minimizing sum of numbers along path.",
        examples=[{"input": "grid = [[1,3,1],[1,5,1],[4,2,1]]", "output": "7"}],
        constraints=["1 <= m, n <= 200"],
        starter_code={
            "python": "def min_path_sum(grid: list) -> int:\n    pass\n",
            "c": "int minPathSum() { return 0; }\n",
            "cpp": "int minPathSum(vector<vector<int>>& g) { return 0; }\n",
            "java": "public class Solution { public static int minPathSum(int[][] g) { return 0; } }\n"
        },
        expected_solution={
            "python": "def min_path_sum(grid: list) -> int:\n    R, C = len(grid), len(grid[0])\n    for r in range(R):\n        for c in range(C):\n            if r == 0 and c == 0: continue\n            elif r == 0: grid[r][c] += grid[r][c - 1]\n            elif c == 0: grid[r][c] += grid[r - 1][c]\n            else: grid[r][c] += min(grid[r - 1][c], grid[r][c - 1])\n    return grid[-1][-1]\n",
            "c": "int minPathSum() { return 0; }\n",
            "cpp": "int minPathSum(vector<vector<int>>& g) { return 0; }\n",
            "java": "public class Solution { public static int minPathSum(int[][] g) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1, 3, 1], [1, 5, 1], [4, 2, 1]], expected_output=7),
            TestCase(id=2, input=[[1, 2, 3], [4, 5, 6]], expected_output=12)
        ],
        learning_objectives=["2D grid in-place dynamic programming"],
        common_misconceptions=["Greedy step selection failing on future high costs"],
        hint="grid[r][c] += min(top_cell, left_cell)."
    ),

    "decode-ways": Problem(
        id="decode-ways",
        title="Decode Ways",
        difficulty="Medium",
        topic="Dynamic Programming",
        subtopic="1D DP",
        description="A message containing letters from A-Z is being encoded to numbers using 'A' -> '1', 'B' -> '2', ..., 'Z' -> '26'. Return total ways to decode it.",
        examples=[{"input": "s = '12'", "output": "2"}, {"input": "s = '226'", "output": "3"}, {"input": "s = '06'", "output": "0"}],
        constraints=["1 <= s.length <= 100"],
        starter_code={
            "python": "def num_decodings(s: str) -> int:\n    pass\n",
            "c": "int numDecodings(char* s) { return 0; }\n",
            "cpp": "int numDecodings(string s) { return 0; }\n",
            "java": "public class Solution { public static int numDecodings(String s) { return 0; } }\n"
        },
        expected_solution={
            "python": "def num_decodings(s: str) -> int:\n    if not s or s[0] == '0': return 0\n    dp = [0] * (len(s) + 1)\n    dp[0] = 1; dp[1] = 1\n    for i in range(2, len(s) + 1):\n        one = int(s[i-1:i])\n        two = int(s[i-2:i])\n        if 1 <= one <= 9: dp[i] += dp[i - 1]\n        if 10 <= two <= 26: dp[i] += dp[i - 2]\n    return dp[len(s)]\n",
            "c": "int numDecodings(char* s) { return 0; }\n",
            "cpp": "int numDecodings(string s) { return 0; }\n",
            "java": "public class Solution { public static int numDecodings(String s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input="12", expected_output=2),
            TestCase(id=2, input="226", expected_output=3),
            TestCase(id=3, input="06", expected_output=0),
            TestCase(id=4, input="10", expected_output=1)
        ],
        learning_objectives=["Single and double digit sequence DP transition"],
        common_misconceptions=["Leading zeros can decode to letters (they cannot)"],
        hint="Combine transitions from dp[i-1] (valid 1-digit) and dp[i-2] (valid 10-26)."
    ),

    # =========================================================================
    # ALGORITHMS & TWO POINTERS (5 more -> total 16+)
    # =========================================================================
    "merge-sorted-array": Problem(
        id="merge-sorted-array",
        title="Merge Sorted Array (In-Place)",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="Merge sorted array `nums2` into `nums1` as one sorted array in-place from the back.",
        examples=[{"input": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3", "output": "[1,2,2,3,5,6]"}],
        constraints=["nums1.length == m + n"],
        starter_code={
            "python": "def merge_sorted(nums1: list, m: int, nums2: list, n: int) -> list:\n    pass\n",
            "c": "void mergeSorted() {}\n",
            "cpp": "vector<int> mergeSorted(vector<int>& n1, int m, vector<int>& n2, int n) { return n1; }\n",
            "java": "public class Solution { public static int[] mergeSorted(int[] n1, int m, int[] n2, int n) { return n1; } }\n"
        },
        expected_solution={
            "python": "def merge_sorted(nums1: list, m: int, nums2: list, n: int) -> list:\n    p1, p2, p = m - 1, n - 1, m + n - 1\n    while p2 >= 0:\n        if p1 >= 0 and nums1[p1] > nums2[p2]:\n            nums1[p] = nums1[p1]; p1 -= 1\n        else:\n            nums1[p] = nums2[p2]; p2 -= 1\n        p -= 1\n    return nums1\n",
            "c": "void mergeSorted() {}\n",
            "cpp": "vector<int> mergeSorted(vector<int>& n1, int m, vector<int>& n2, int n) { return n1; }\n",
            "java": "public class Solution { public static int[] mergeSorted(int[] n1, int m, int[] n2, int n) { return n1; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums1": [1, 2, 3, 0, 0, 0], "m": 3, "nums2": [2, 5, 6], "n": 3}, expected_output=[1, 2, 2, 3, 5, 6]),
            TestCase(id=2, input={"nums1": [1], "m": 1, "nums2": [], "n": 0}, expected_output=[1])
        ],
        learning_objectives=["Reverse two pointer merge avoiding auxiliary memory"],
        common_misconceptions=["Merging from front overwriting elements"],
        hint="Place the largest element at index m + n - 1."
    ),

    "squares-of-sorted-array": Problem(
        id="squares-of-sorted-array",
        title="Squares of a Sorted Array",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="Given sorted array `nums`, return squares of each number sorted in non-decreasing order in O(n) time.",
        examples=[{"input": "nums = [-4, -1, 0, 3, 10]", "output": "[0, 1, 9, 16, 100]"}],
        constraints=["1 <= nums.length <= 10^4"],
        starter_code={
            "python": "def sorted_squares(nums: list) -> list:\n    pass\n",
            "c": "void sortedSquares() {}\n",
            "cpp": "vector<int> sortedSquares(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static int[] sortedSquares(int[] nums) { return new int[0]; } }\n"
        },
        expected_solution={
            "python": "def sorted_squares(nums: list) -> list:\n    n = len(nums)\n    res = [0] * n\n    l, r, p = 0, n - 1, n - 1\n    while l <= r:\n        if abs(nums[l]) > abs(nums[r]):\n            res[p] = nums[l] * nums[l]; l += 1\n        else:\n            res[p] = nums[r] * nums[r]; r -= 1\n        p -= 1\n    return res\n",
            "c": "void sortedSquares() {}\n",
            "cpp": "vector<int> sortedSquares(vector<int>& nums) { return {}; }\n",
            "java": "public class Solution { public static int[] sortedSquares(int[] nums) { return new int[0]; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[-4, -1, 0, 3, 10], expected_output=[0, 1, 9, 16, 100]),
            TestCase(id=2, input=[-7, -3, 2, 3, 11], expected_output=[4, 9, 9, 49, 121])
        ],
        learning_objectives=["Two-pointer converging comparison on sorted signed arrays"],
        common_misconceptions=["Squaring elements then sorting in O(N log N)"],
        hint="Fill result from the right using the larger absolute value."
    ),

    "is-subsequence": Problem(
        id="is-subsequence",
        title="Is Subsequence",
        difficulty="Easy",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="Return `True` if string `s` is a subsequence of string `t`.",
        examples=[{"input": "s = 'abc', t = 'ahbgdc'", "output": "True"}, {"input": "s = 'axc', t = 'ahbgdc'", "output": "False"}],
        constraints=["0 <= s.length <= 100", "0 <= t.length <= 10^4"],
        starter_code={
            "python": "def is_subsequence(s: str, t: str) -> bool:\n    pass\n",
            "c": "int isSubsequence(char* s, char* t) { return 0; }\n",
            "cpp": "bool isSubsequence(string s, string t) { return false; }\n",
            "java": "public class Solution { public static boolean isSubsequence(String s, String t) { return false; } }\n"
        },
        expected_solution={
            "python": "def is_subsequence(s: str, t: str) -> bool:\n    i, j = 0, 0\n    while i < len(s) and j < len(t):\n        if s[i] == t[j]: i += 1\n        j += 1\n    return i == len(s)\n",
            "c": "int isSubsequence(char* s, char* t) { return 0; }\n",
            "cpp": "bool isSubsequence(string s, string t) { return false; }\n",
            "java": "public class Solution { public static boolean isSubsequence(String s, String t) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"s": "abc", "t": "ahbgdc"}, expected_output=True),
            TestCase(id=2, input={"s": "axc", "t": "ahbgdc"}, expected_output=False),
            TestCase(id=3, input={"s": "", "t": "ahbgdc"}, expected_output=True)
        ],
        learning_objectives=["Greedy subsequence character matching in linear time"],
        common_misconceptions=["Non-linear backtracking when greedy traversal suffices"],
        hint="Increment pointer in s only when matching character in t is seen."
    ),

    "search-a-2d-matrix": Problem(
        id="search-a-2d-matrix",
        title="Search a 2D Matrix (Binary Search)",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Binary Search",
        description="Search for a `target` value in an `m x n` sorted matrix in O(log(m*n)) time.",
        examples=[{"input": "matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3", "output": "True"}],
        constraints=["1 <= m, n <= 100"],
        starter_code={
            "python": "def search_matrix(matrix: list, target: int) -> bool:\n    pass\n",
            "c": "int searchMatrix() { return 0; }\n",
            "cpp": "bool searchMatrix(vector<vector<int>>& m, int t) { return false; }\n",
            "java": "public class Solution { public static boolean searchMatrix(int[][] m, int t) { return false; } }\n"
        },
        expected_solution={
            "python": "def search_matrix(matrix: list, target: int) -> bool:\n    if not matrix: return False\n    R, C = len(matrix), len(matrix[0])\n    l, r = 0, R * C - 1\n    while l <= r:\n        mid = (l + r) // 2\n        val = matrix[mid // C][mid % C]\n        if val == target: return True\n        elif val < target: l = mid + 1\n        else: r = mid - 1\n    return False\n",
            "c": "int searchMatrix() { return 0; }\n",
            "cpp": "bool searchMatrix(vector<vector<int>>& m, int t) { return false; }\n",
            "java": "public class Solution { public static boolean searchMatrix(int[][] m, int t) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"matrix": [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], "target": 3}, expected_output=True),
            TestCase(id=2, input={"matrix": [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], "target": 13}, expected_output=False)
        ],
        learning_objectives=["Mapping 2D matrix indices to virtual 1D binary search space"],
        common_misconceptions=["Searching rows linearly in O(M * log N)"],
        hint="Index mid corresponds to row mid // cols and col mid % cols."
    ),

    # =========================================================================
    # TREES & BST (5 more -> total 16+)
    # =========================================================================
    "symmetric-tree": Problem(
        id="symmetric-tree",
        title="Symmetric Tree (Mirror Reflection)",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Check whether a binary tree is a mirror of itself (symmetric around its center).",
        examples=[{"input": "root = [1, 2, 2, 3, 4, 4, 3]", "output": "True"}],
        constraints=["1 <= nodes <= 1000"],
        starter_code={
            "python": "def is_symmetric(root: list) -> bool:\n    pass\n",
            "c": "int isSymmetric() { return 1; }\n",
            "cpp": "bool isSymmetric() { return true; }\n",
            "java": "public class Solution { public static boolean isSymmetric() { return true; } }\n"
        },
        expected_solution={
            "python": "def is_symmetric(root: list) -> bool:\n    if not root or root[0] is None: return True\n    def is_mirror(t1, t2):\n        if t1 >= len(root) and t2 >= len(root): return True\n        v1 = root[t1] if t1 < len(root) else None\n        v2 = root[t2] if t2 < len(root) else None\n        if v1 is None and v2 is None: return True\n        if v1 is None or v2 is None or v1 != v2: return False\n        return is_mirror(2 * t1 + 1, 2 * t2 + 2) and is_mirror(2 * t1 + 2, 2 * t2 + 1)\n    return is_mirror(1, 2)\n",
            "c": "int isSymmetric() { return 1; }\n",
            "cpp": "bool isSymmetric() { return true; }\n",
            "java": "public class Solution { public static boolean isSymmetric() { return true; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 2, 3, 4, 4, 3], expected_output=True),
            TestCase(id=2, input=[1, 2, 2, None, 3, None, 3], expected_output=False)
        ],
        learning_objectives=["Dual pointer mirror recursion on binary trees"],
        common_misconceptions=["Comparing left child to left child instead of right child"],
        hint="Recursively verify left.left == right.right and left.right == right.left."
    ),

    "diameter-of-binary-tree": Problem(
        id="diameter-of-binary-tree",
        title="Diameter of Binary Tree",
        difficulty="Easy",
        topic="Trees & Binary Search Trees",
        subtopic="DFS Traversal",
        description="Return length of diameter of the binary tree (longest path between any two nodes in a tree).",
        examples=[{"input": "root = [1, 2, 3, 4, 5]", "output": "3"}],
        constraints=["1 <= nodes <= 10^4"],
        starter_code={
            "python": "def diameter_of_binary_tree(root: list) -> int:\n    pass\n",
            "c": "int diameterOfBinaryTree() { return 0; }\n",
            "cpp": "int diameterOfBinaryTree() { return 0; }\n",
            "java": "public class Solution { public static int diameterOfBinaryTree() { return 0; } }\n"
        },
        expected_solution={
            "python": "def diameter_of_binary_tree(root: list) -> int:\n    if not root or root[0] is None: return 0\n    max_d = [0]\n    def height(idx):\n        if idx >= len(root) or root[idx] is None: return 0\n        lh = height(2 * idx + 1)\n        rh = height(2 * idx + 2)\n        max_d[0] = max(max_d[0], lh + rh)\n        return 1 + max(lh, rh)\n    height(0)\n    return max_d[0]\n",
            "c": "int diameterOfBinaryTree() { return 0; }\n",
            "cpp": "int diameterOfBinaryTree() { return 0; }\n",
            "java": "public class Solution { public static int diameterOfBinaryTree() { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 3, 4, 5], expected_output=3),
            TestCase(id=2, input=[1, 2], expected_output=1)
        ],
        learning_objectives=["Post-order tree traversal returning height and updating diameter"],
        common_misconceptions=["Assuming longest path must pass through root"],
        hint="Diameter through node is left_height + right_height."
    ),

    "kth-smallest-element-in-bst": Problem(
        id="kth-smallest-element-in-bst",
        title="Kth Smallest Element in a BST",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="BST Properties",
        description="Given root of BST and integer `k`, return the `k`-th smallest value in the tree.",
        examples=[{"input": "root = [3, 1, 4, null, 2], k = 1", "output": "1"}],
        constraints=["1 <= k <= nodes <= 10^4"],
        starter_code={
            "python": "def kth_smallest(root: list, k: int) -> int:\n    pass\n",
            "c": "int kthSmallest() { return 0; }\n",
            "cpp": "int kthSmallest() { return 0; }\n",
            "java": "public class Solution { public static int kthSmallest() { return 0; } }\n"
        },
        expected_solution={
            "python": "def kth_smallest(root: list, k: int) -> int:\n    vals = sorted([x for x in root if x is not None])\n    return vals[k - 1]\n",
            "c": "int kthSmallest() { return 0; }\n",
            "cpp": "int kthSmallest() { return 0; }\n",
            "java": "public class Solution { public static int kthSmallest() { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"root": [3, 1, 4, None, 2], "k": 1}, expected_output=1),
            TestCase(id=2, input={"root": [5, 3, 6, 2, 4, None, None, 1], "k": 3}, expected_output=3)
        ],
        learning_objectives=["In-order BST monotonic property"],
        common_misconceptions=["Traversing in arbitrary order"],
        hint="In-order traversal visits BST nodes in ascending order."
    ),

    "binary-tree-right-side-view": Problem(
        id="binary-tree-right-side-view",
        title="Binary Tree Right Side View",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="BFS Level Order",
        description="Return values of nodes visible from the right side, ordered from top to bottom.",
        examples=[{"input": "root = [1, 2, 3, null, 5, null, 4]", "output": "[1, 3, 4]"}],
        constraints=["0 <= nodes <= 100"],
        starter_code={
            "python": "def right_side_view(root: list) -> list:\n    pass\n",
            "c": "void rightSideView() {}\n",
            "cpp": "vector<int> rightSideView() { return {}; }\n",
            "java": "public class Solution { public static List<Integer> rightSideView() { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def right_side_view(root: list) -> list:\n    if not root or root[0] is None: return []\n    res = []\n    level = [0]\n    while level:\n        res.append(root[level[-1]])\n        nxt = []\n        for idx in level:\n            l, r = 2 * idx + 1, 2 * idx + 2\n            if l < len(root) and root[l] is not None: nxt.append(l)\n            if r < len(root) and root[r] is not None: nxt.append(r)\n        level = nxt\n    return res\n",
            "c": "void rightSideView() {}\n",
            "cpp": "vector<int> rightSideView() { return {}; }\n",
            "java": "public class Solution { public static List<Integer> rightSideView() { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[1, 2, 3, None, 5, None, 4], expected_output=[1, 3, 4]),
            TestCase(id=2, input=[1, None, 3], expected_output=[1, 3])
        ],
        learning_objectives=["BFS level order boundary extraction"],
        common_misconceptions=["Following only the right child pointer"],
        hint="Take the last node at each level of BFS."
    ),

    # =========================================================================
    # GRAPHS & TRAVERSAL (4 more -> total 16+)
    # =========================================================================
    "find-if-path-exists-graph": Problem(
        id="find-if-path-exists-graph",
        title="Find if Path Exists in Graph",
        difficulty="Easy",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="Return `True` if there is a valid path from `source` to `destination` in the graph.",
        examples=[{"input": "n = 3, edges = [[0,1],[1,2],[2,0]], source = 0, destination = 2", "output": "True"}],
        constraints=["1 <= n <= 2 * 10^5"],
        starter_code={
            "python": "def valid_path(n: int, edges: list, source: int, destination: int) -> bool:\n    pass\n",
            "c": "int validPath() { return 1; }\n",
            "cpp": "bool validPath(int n, vector<vector<int>>& e, int s, int d) { return true; }\n",
            "java": "public class Solution { public static boolean validPath(int n, int[][] e, int s, int d) { return true; } }\n"
        },
        expected_solution={
            "python": "def valid_path(n: int, edges: list, source: int, destination: int) -> bool:\n    from collections import defaultdict, deque\n    if source == destination: return True\n    adj = defaultdict(list)\n    for u, v in edges: adj[u].append(v); adj[v].append(u)\n    visited = {source}\n    q = deque([source])\n    while q:\n        node = q.popleft()\n        if node == destination: return True\n        for nxt in adj[node]:\n            if nxt not in visited: visited.add(nxt); q.append(nxt)\n    return False\n",
            "c": "int validPath() { return 1; }\n",
            "cpp": "bool validPath(int n, vector<vector<int>>& e, int s, int d) { return true; }\n",
            "java": "public class Solution { public static boolean validPath(int n, int[][] e, int s, int d) { return true; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"n": 3, "edges": [[0, 1], [1, 2], [2, 0]], "source": 0, "destination": 2}, expected_output=True),
            TestCase(id=2, input={"n": 6, "edges": [[0, 1], [0, 2], [3, 5], [5, 4], [4, 3]], "source": 0, "destination": 5}, expected_output=False)
        ],
        learning_objectives=["Breadth-first search connectivity checking"],
        common_misconceptions=["Failing to track visited nodes on cyclic graphs"],
        hint="Run BFS from source and return True if destination is reached."
    ),

    "number-of-provinces": Problem(
        id="number-of-provinces",
        title="Number of Provinces",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="Return the total number of connected components (provinces) in given connectivity matrix.",
        examples=[{"input": "isConnected = [[1,1,0],[1,1,0],[0,0,1]]", "output": "2"}],
        constraints=["1 <= n <= 200"],
        starter_code={
            "python": "def find_circle_num(isConnected: list) -> int:\n    pass\n",
            "c": "int findCircleNum() { return 0; }\n",
            "cpp": "int findCircleNum(vector<vector<int>>& isConnected) { return 0; }\n",
            "java": "public class Solution { public static int findCircleNum(int[][] isConnected) { return 0; } }\n"
        },
        expected_solution={
            "python": "def find_circle_num(isConnected: list) -> int:\n    n = len(isConnected)\n    visited = set()\n    count = 0\n    def dfs(i):\n        for j in range(n):\n            if isConnected[i][j] == 1 and j not in visited:\n                visited.add(j); dfs(j)\n    for i in range(n):\n        if i not in visited:\n            visited.add(i); dfs(i); count += 1\n    return count\n",
            "c": "int findCircleNum() { return 0; }\n",
            "cpp": "int findCircleNum(vector<vector<int>>& isConnected) { return 0; }\n",
            "java": "public class Solution { public static int findCircleNum(int[][] isConnected) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1, 1, 0], [1, 1, 0], [0, 0, 1]], expected_output=2),
            TestCase(id=2, input=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], expected_output=3)
        ],
        learning_objectives=["Counting connected components with graph DFS"],
        common_misconceptions=["Double counting visited cities"],
        hint="Iterate over unvisited cities, run DFS to mark entire province, increment count."
    ),

    "pacific-atlantic-water-flow": Problem(
        id="pacific-atlantic-water-flow",
        title="Pacific Atlantic Water Flow",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="DFS Traversal",
        description="Return coordinates where rain water can flow to both Pacific (top/left) and Atlantic (bottom/right) oceans.",
        examples=[{"input": "heights = [[1]]", "output": "[[0,0]]"}],
        constraints=["1 <= m, n <= 200"],
        starter_code={
            "python": "def pacific_atlantic(heights: list) -> list:\n    pass\n",
            "c": "void pacificAtlantic() {}\n",
            "cpp": "vector<vector<int>> pacificAtlantic(vector<vector<int>>& h) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> pacificAtlantic(int[][] h) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": "def pacific_atlantic(heights: list) -> list:\n    if not heights: return []\n    R, C = len(heights), len(heights[0])\n    pac, atl = set(), set()\n    def dfs(r, c, visit, prev_h):\n        if (r, c) in visit or r < 0 or r >= R or c < 0 or c >= C or heights[r][c] < prev_h: return\n        visit.add((r, c))\n        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:\n            dfs(r + dr, c + dc, visit, heights[r][c])\n    for c in range(C):\n        dfs(0, c, pac, heights[0][c])\n        dfs(R - 1, c, atl, heights[R - 1][c])\n    for r in range(R):\n        dfs(r, 0, pac, heights[r][0])\n        dfs(r, C - 1, atl, heights[r][C - 1])\n    return sorted([list(cell) for cell in (pac & atl)])\n",
            "c": "void pacificAtlantic() {}\n",
            "cpp": "vector<vector<int>> pacificAtlantic(vector<vector<int>>& h) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> pacificAtlantic(int[][] h) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1]], expected_output=[[0, 0]]),
            TestCase(id=2, input=[[2, 1], [1, 2]], expected_output=[[0, 0], [0, 1], [1, 0], [1, 1]])
        ],
        learning_objectives=["Multi-boundary inward DFS reachability intersection"],
        common_misconceptions=["Flowing downward from every internal cell separately"],
        hint="Search uphill from ocean boundaries and find the intersection."
    )
}
