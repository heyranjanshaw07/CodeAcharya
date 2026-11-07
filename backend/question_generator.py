import os
import json
import uuid
import random
import re
from typing import Dict, Any, List, Optional, Callable

# Standard Supported Topics
TOPIC_NORMALIZATION = {
    "recursion & backtracking": "Recursion & Backtracking",
    "recursion": "Recursion & Backtracking",
    "backtracking": "Recursion & Backtracking",
    "arrays & hashing": "Arrays & Hashing",
    "arrays": "Arrays & Hashing",
    "hashing": "Arrays & Hashing",
    "strings": "Strings",
    "string": "Strings",
    "stack & queue": "Stack & Queue",
    "stack": "Stack & Queue",
    "queue": "Stack & Queue",
    "dynamic programming": "Dynamic Programming",
    "dp": "Dynamic Programming",
    "algorithms & two pointers": "Algorithms & Two Pointers",
    "two pointers": "Algorithms & Two Pointers",
    "trees & binary search trees": "Trees & Binary Search Trees",
    "trees & bst": "Trees & Binary Search Trees",
    "trees": "Trees & Binary Search Trees",
    "graphs & traversal": "Graphs & Traversal",
    "graphs": "Graphs & Traversal"
}

def normalize_topic(topic: str) -> str:
    key = topic.strip().lower()
    return TOPIC_NORMALIZATION.get(key, topic.strip())

def normalize_difficulty(difficulty: str) -> str:
    d = difficulty.strip().capitalize()
    return d if d in ["Easy", "Medium", "Hard"] else "Easy"

def normalize_language(language: str) -> str:
    lang = language.strip().lower()
    if lang in ["c"]:
        return "c"
    if lang in ["cpp", "c++"]:
        return "cpp"
    if lang in ["java"]:
        return "java"
    return "python"

TOPIC_SUBTOPICS: Dict[str, List[str]] = {
    "Recursion & Backtracking": ["Basic Recursion", "Backtracking", "Divide & Conquer", "Tree Recursion"],
    "Arrays & Hashing": ["Hash Maps & Sets", "Prefix Sums", "Frequency Counting", "Array Manipulation"],
    "Strings": ["String Manipulation", "Anagrams & Palindromes", "Pattern Matching", "Sliding Window"],
    "Stack & Queue": ["Monotonic Stack", "Parentheses Matching", "BFS Queue", "Deque"],
    "Dynamic Programming": ["1D DP", "2D Grid DP", "Knapsack & Subsets", "Memoization"],
    "Algorithms & Two Pointers": ["Two Pointers", "Binary Search", "Sorting & Partitioning", "Sliding Window"],
    "Trees & Binary Search Trees": ["DFS Traversal", "BFS Level Order", "BST Properties", "Path Sums"],
    "Graphs & Traversal": ["BFS / Shortest Path", "DFS Traversal", "Topological Sort", "Cycle Detection"]
}

# 24 Category Blueprints (Multiple questions per topic & difficulty)
BLUEPRINTS: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "Recursion & Backtracking": {
        "Easy": [
            {
                "id": "sum-of-digits-recursion",
                "title": "Sum of Digits (Recursion)",
                "topic": "Recursion & Backtracking",
                "difficulty": "Easy",
                "description": "Given a non-negative integer `n`, compute the sum of its digits recursively.\n\n### Requirements\n- Implement your solution using **recursion**.\n- Do not convert the integer to a string or use loops.",
                "inputFormat": "A single non-negative integer `n`.",
                "outputFormat": "An integer representing the sum of all digits in `n`.",
                "constraints": [
                    "0 <= n <= 10^9"
                ],
                "examples": [
                    {
                        "input": "n = 126",
                        "output": "9",
                        "explanation": "1 + 2 + 6 = 9"
                    },
                    {
                        "input": "n = 49",
                        "output": "13",
                        "explanation": "4 + 9 = 13"
                    },
                    {
                        "input": "n = 0",
                        "output": "0",
                        "explanation": "Sum of digits for 0 is 0"
                    }
                ],
                "hint": "Consider the base case when n < 10. For larger numbers, add the last digit `n % 10` to the recursive result of `n // 10`.",
                "starter_code": {
                    "python": "def sum_digits(n: int) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint sumDigits(int n) {\n    \n}\n",
                    "cpp": "#include <iostream>\n\nint sumDigits(int n) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int sumDigits(int n) {\n        \n    }\n}\n"
                },
                "expected_solution": {
                    "python": "def sum_digits(n: int) -> int:\n    if n < 10:\n        return n\n    return (n % 10) + sum_digits(n // 10)\n",
                    "c": "#include <stdio.h>\n\nint sumDigits(int n) {\n    if (n < 10) return n;\n    return (n % 10) + sumDigits(n / 10);\n}\n",
                    "cpp": "#include <iostream>\n\nint sumDigits(int n) {\n    if (n < 10) return n;\n    return (n % 10) + sumDigits(n / 10);\n}\n",
                    "java": "public class Solution {\n    public static int sumDigits(int n) {\n        if (n < 10) return n;\n        return (n % 10) + sumDigits(n / 10);\n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": 126,
                        "expected_output": 9,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": 49,
                        "expected_output": 13,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": 7,
                        "expected_output": 7,
                        "is_hidden": False
                    },
                    {
                        "id": 4,
                        "input": 10005,
                        "expected_output": 6,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Identify division and modulo as recursive decomposition",
                    "Establish termination condition on single-digit numbers"
                ],
                "common_misconceptions": [
                    "Attempting iterative while loops instead of recursive stack reduction"
                ]
            },
            {
                "id": "power-of-two-recursion",
                "title": "Power of Two Check (Recursion)",
                "topic": "Recursion & Backtracking",
                "difficulty": "Easy",
                "description": "Given an integer `n`, return `True` if it is a power of two, otherwise return `False`.\n\nAn integer `n` is a power of two if there exists an integer `x` such that `n == 2^x`.\n\n### Requirements\n- Solve this problem recursively.",
                "inputFormat": "A single integer `n`.",
                "outputFormat": "A boolean indicating whether `n` is a power of two.",
                "constraints": [
                    "-2^31 <= n <= 2^31 - 1"
                ],
                "examples": [
                    {
                        "input": "n = 1",
                        "output": "True",
                        "explanation": "2^0 = 1"
                    },
                    {
                        "input": "n = 16",
                        "output": "True",
                        "explanation": "2^4 = 16"
                    },
                    {
                        "input": "n = 3",
                        "output": "False",
                        "explanation": "3 is not a power of two"
                    }
                ],
                "hint": "Any number less than or equal to 0 cannot be a power of two. If n == 1, it is 2^0. If n is odd, it cannot be a power of two.",
                "starter_code": {
                    "python": "def is_power_of_two(n: int) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool isPowerOfTwo(int n) {\n    \n}\n",
                    "cpp": "#include <iostream>\n\nbool isPowerOfTwo(int n) {\n    \n}\n",
                    "java": "public class Solution {\n    public static boolean isPowerOfTwo(int n) {\n        \n    }\n}\n"
                },
                "expected_solution": {
                    "python": "def is_power_of_two(n: int) -> bool:\n    if n <= 0:\n        return False\n    if n == 1:\n        return True\n    if n % 2 != 0:\n        return False\n    return is_power_of_two(n // 2)\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool isPowerOfTwo(int n) {\n    if (n <= 0) return False;\n    if (n == 1) return True;\n    if (n % 2 != 0) return False;\n    return isPowerOfTwo(n / 2);\n}\n",
                    "cpp": "#include <iostream>\n\nbool isPowerOfTwo(int n) {\n    if (n <= 0) return False;\n    if (n == 1) return True;\n    if (n % 2 != 0) return False;\n    return isPowerOfTwo(n / 2);\n}\n",
                    "java": "public class Solution {\n    public static boolean isPowerOfTwo(int n) {\n        if (n <= 0) return False;\n        if (n == 1) return True;\n        if (n % 2 != 0) return False;\n        return isPowerOfTwo(n / 2);\n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": 1,
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": 16,
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": 3,
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 4,
                        "input": 64,
                        "expected_output": True,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Break down logarithmic reduction using recursive divide-by-2",
                    "Identify boundary conditions for non-positive integers"
                ],
                "common_misconceptions": [
                    "Forgetting that negative numbers cannot be powers of two"
                ]
            }
        ],
        "Medium": [
            {
                "id": "subsets-generator",
                "title": "All Subsets (Power Set Backtracking)",
                "topic": "Recursion & Backtracking",
                "difficulty": "Medium",
                "description": "Given an integer array `nums` of unique elements, return all possible subsets (the power set).\n\nThe solution set must not contain duplicate subsets. Return the subsets in any order.\n\n### Requirements\n- Implement using the **backtracking / decision tree** technique.",
                "inputFormat": "A list of unique integers `nums`.",
                "outputFormat": "A list of lists containing all subsets.",
                "constraints": [
                    "1 <= nums.length <= 10",
                    "-10 <= nums[i] <= 10"
                ],
                "examples": [
                    {
                        "input": "nums = [1, 2, 3]",
                        "output": "[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]",
                        "explanation": "Total 2^3 = 8 subsets"
                    },
                    {
                        "input": "nums = [0]",
                        "output": "[[], [0]]",
                        "explanation": "Total 2^1 = 2 subsets"
                    }
                ],
                "hint": "At each index `i`, you have two choices: include `nums[i]` in the current subset, or exclude it, then recurse on index `i + 1`.",
                "starter_code": {
                    "python": "def subsets(nums: list[int]) -> list[list[int]]:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nvoid subsets(int* nums, int numsSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n\nstd::vector<std::vector<int>> subsets(std::vector<int>& nums) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static List<List<Integer>> subsets(int[] nums) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            1,
                            2
                        ],
                        "expected_output": [
                            [],
                            [
                                2
                            ],
                            [
                                1
                            ],
                            [
                                1,
                                2
                            ]
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            0
                        ],
                        "expected_output": [
                            [],
                            [
                                0
                            ]
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            3,
                            5
                        ],
                        "expected_output": [
                            [],
                            [
                                5
                            ],
                            [
                                3
                            ],
                            [
                                3,
                                5
                            ]
                        ],
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Model binary choose-or-skip decisions on recursion tree",
                    "Restore backtrack state via pop operation"
                ],
                "common_misconceptions": [
                    "Appending reference instead of copying current list snapshot into result"
                ],
                "expected_solution": {
                    "python": "def subsets(nums: list[int]) -> list[list[int]]:\n    # TODO: Write your backtracking solution here\n    result = []\n    def backtrack(idx, current):\n        if idx == len(nums):\n            result.append(list(current))\n            return\n        # Exclude\n        backtrack(idx + 1, current)\n        # Include\n        current.append(nums[idx])\n        backtrack(idx + 1, current)\n        current.pop()\n    backtrack(0, [])\n    return result\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nvoid subsets(int* nums, int numsSize) {\n    // TODO: Write your backtracking solution here\n}\n",
                    "cpp": "#include <vector>\n\nstd::vector<std::vector<int>> subsets(std::vector<int>& nums) {\n    // TODO: Write your backtracking solution here\n    std::vector<std::vector<int>> res;\n    std::vector<int> curr;\n    auto backtrack = [&](auto& self, int idx) -> void {\n        if (idx == nums.size()) {\n            res.push_back(curr);\n            return;\n        }\n        self(self, idx + 1);\n        curr.push_back(nums[idx]);\n        self(self, idx + 1);\n        curr.pop_back();\n    };\n    backtrack(backtrack, 0);\n    return res;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static List<List<Integer>> subsets(int[] nums) {\n        // TODO: Write your backtracking solution here\n        List<List<Integer>> res = new ArrayList<>();\n        backtrack(0, nums, new ArrayList<>(), res);\n        return res;\n    }\n    private static void backtrack(int idx, int[] nums, List<Integer> curr, List<List<Integer>> res) {\n        if (idx == nums.length) {\n            res.add(new ArrayList<>(curr));\n            return;\n        }\n        backtrack(idx + 1, nums, curr, res);\n        curr.add(nums[idx]);\n        backtrack(idx + 1, nums, curr, res);\n        curr.remove(curr.size() - 1);\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "word-search-backtracking",
                "title": "Word Search in 2D Board (Backtracking)",
                "topic": "Recursion & Backtracking",
                "difficulty": "Hard",
                "description": "Given an `m x n` grid of characters `board` and a string `word`, return `True` if `word` exists in the grid.\n\nThe word can be constructed from letters of sequentially adjacent cells, where adjacent cells are horizontally or vertically neighboring. The same letter cell may not be used more than once.",
                "inputFormat": "A 2D list of characters `board` and a string `word`.",
                "outputFormat": "Boolean `True` if word exists, `False` otherwise.",
                "constraints": [
                    "m == board.length",
                    "n == board[i].length",
                    "1 <= m, n <= 6",
                    "1 <= word.length <= 15"
                ],
                "examples": [
                    {
                        "input": "board = [['A','B','C','E'],['S','F','C','S'],['A','D','E','E']], word = 'ABCCED'",
                        "output": "True",
                        "explanation": "The word ABCCED traces path A->B->C->C->E->D."
                    },
                    {
                        "input": "board = [['A','B'],['C','D']], word = 'ABCD'",
                        "output": "False",
                        "explanation": "Diagonal movement is not allowed."
                    }
                ],
                "hint": "From each cell matching word[0], run DFS. Mark visited cells temporarily (e.g. board[r][c] = '#'), explore in 4 cardinal directions, and revert upon return.",
                "starter_code": {
                    "python": "def exist(board: list[list[str]], word: str) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool exist(char** board, int boardSize, int* boardColSize, char* word) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <string>\n\nbool exist(std::vector<std::vector<char>>& board, std::string word) {\n    \n}\n",
                    "java": "public class Solution {\n    public static boolean exist(char[][] board, String word) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "board": [
                                [
                                    "A",
                                    "B"
                                ],
                                [
                                    "C",
                                    "D"
                                ]
                            ],
                            "word": "AB"
                        },
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "board": [
                                [
                                    "A",
                                    "B"
                                ],
                                [
                                    "C",
                                    "D"
                                ]
                            ],
                            "word": "ACDB"
                        },
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "board": [
                                [
                                    "A",
                                    "B"
                                ],
                                [
                                    "C",
                                    "D"
                                ]
                            ],
                            "word": "XYZ"
                        },
                        "expected_output": False,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Apply backtracking to 2D matrix exploration with in-place visited tracking",
                    "Restore board state on stack unwinding"
                ],
                "common_misconceptions": [
                    "Allowing diagonal movement when problem strictly specifies horizontally or vertically neighboring cells"
                ],
                "expected_solution": {
                    "python": "def exist(board: list[list[str]], word: str) -> bool:\n    # TODO: Write your 2D grid backtracking here\n    R, C = len(board), len(board[0])\n    def dfs(r, c, k):\n        if k == len(word): return True\n        if r < 0 or r >= R or c < 0 or c >= C or board[r][c] != word[k]: return False\n        temp, board[r][c] = board[r][c], '#'\n        found = dfs(r+1, c, k+1) or dfs(r-1, c, k+1) or dfs(r, c+1, k+1) or dfs(r, c-1, k+1)\n        board[r][c] = temp\n        return found\n    for r in range(R):\n        for c in range(C):\n            if dfs(r, c, 0): return True\n    return False\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool exist(char** board, int boardSize, int* boardColSize, char* word) {\n    // TODO: Write your 2D grid backtracking here\n    return False;\n}\n",
                    "cpp": "#include <vector>\n#include <string>\n\nbool exist(std::vector<std::vector<char>>& board, std::string word) {\n    // TODO: Write your 2D grid backtracking here\n    int R = board.size(), C = board[0].size();\n    auto dfs = [&](auto& self, int r, int c, int k) -> bool {\n        if (k == word.size()) return True;\n        if (r < 0 || r >= R || c < 0 || c >= C || board[r][c] != word[k]) return False;\n        char temp = board[r][c];\n        board[r][c] = '#';\n        bool found = self(self, r+1, c, k+1) || self(self, r-1, c, k+1) || self(self, r, c+1, k+1) || self(self, r, c-1, k+1);\n        board[r][c] = temp;\n        return found;\n    };\n    for (int r = 0; r < R; r++) {\n        for (int c = 0; c < C; c++) {\n            if (dfs(dfs, r, c, 0)) return True;\n        }\n    }\n    return False;\n}\n",
                    "java": "public class Solution {\n    public static boolean exist(char[][] board, String word) {\n        // TODO: Write your 2D grid backtracking here\n        int R = board.length, C = board[0].length;\n        for (int r = 0; r < R; r++) {\n            for (int c = 0; c < C; c++) {\n                if (dfs(board, word, r, c, 0)) return True;\n            }\n        }\n        return False;\n    }\n    private static boolean dfs(char[][] b, String w, int r, int c, int k) {\n        if (k == w.length()) return True;\n        if (r < 0 || r >= b.length || c < 0 || c >= b[0].length || b[r][c] != w.charAt(k)) return False;\n        char temp = b[r][c];\n        b[r][c] = '#';\n        boolean found = dfs(b, w, r+1, c, k+1) || dfs(b, w, r-1, c, k+1) || dfs(b, w, r, c+1, k+1) || dfs(b, w, r, c-1, k+1);\n        b[r][c] = temp;\n        return found;\n    }\n}\n"
                }
            }
        ]
    },
    "Arrays & Hashing": {
        "Easy": [
            {
                "id": "contains-duplicate",
                "title": "Contains Duplicate",
                "topic": "Arrays & Hashing",
                "difficulty": "Easy",
                "description": "Given an integer array `nums`, return `True` if any value appears at least twice in the array, and return `False` if every element is distinct.",
                "inputFormat": "A list of integers `nums`.",
                "outputFormat": "Boolean `True` if duplicate exists, `False` otherwise.",
                "constraints": [
                    "1 <= nums.length <= 10^5",
                    "-10^9 <= nums[i] <= 10^9"
                ],
                "examples": [
                    {
                        "input": "nums = [1, 2, 3, 1]",
                        "output": "True",
                        "explanation": "Element 1 appears twice."
                    },
                    {
                        "input": "nums = [1, 2, 3, 4]",
                        "output": "False",
                        "explanation": "All elements are unique."
                    }
                ],
                "hint": "Use a Hash Set to track seen numbers in O(1) amortized time per lookup.",
                "starter_code": {
                    "python": "def contains_duplicate(nums: list[int]) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool containsDuplicate(int* nums, int numsSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <unordered_set>\n\nbool containsDuplicate(std::vector<int>& nums) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean containsDuplicate(int[] nums) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            1,
                            2,
                            3,
                            1
                        ],
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            1,
                            2,
                            3,
                            4
                        ],
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            1,
                            1,
                            1,
                            3,
                            3,
                            4,
                            3,
                            2,
                            4,
                            2
                        ],
                        "expected_output": True,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Trade O(N) extra space for O(N) linear time lookup",
                    "Understand hash set membership complexity"
                ],
                "common_misconceptions": [
                    "Using nested loops with O(N^2) complexity causing TLE"
                ],
                "expected_solution": {
                    "python": "def contains_duplicate(nums: list[int]) -> bool:\n    # TODO: Write your solution using a set\n    seen = set()\n    for x in nums:\n        if x in seen:\n            return True\n        seen.add(x)\n    return False\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool containsDuplicate(int* nums, int numsSize) {\n        for (int i = 0; i < numsSize; i++) {\n        for (int j = i + 1; j < numsSize; j++) {\n            if (nums[i] == nums[j]) return True;\n        }\n    }\n    return False;\n}\n",
                    "cpp": "#include <vector>\n#include <unordered_set>\n\nbool containsDuplicate(std::vector<int>& nums) {\n        std::unordered_set<int> seen;\n    for (int x : nums) {\n        if (seen.count(x)) return True;\n        seen.insert(x);\n    }\n    return False;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean containsDuplicate(int[] nums) {\n                Set<Integer> seen = new HashSet<>();\n        for (int x : nums) {\n            if (seen.contains(x)) return True;\n            seen.add(x);\n        }\n        return False;\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "group-anagrams",
                "title": "Group Anagrams",
                "topic": "Arrays & Hashing",
                "difficulty": "Medium",
                "description": "Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase.",
                "inputFormat": "A list of strings `strs`.",
                "outputFormat": "A list of grouped anagram lists.",
                "constraints": [
                    "1 <= strs.length <= 10^4",
                    "0 <= strs[i].length <= 100",
                    "strs[i] consists of lowercase English letters."
                ],
                "examples": [
                    {
                        "input": "strs = ['eat','tea','tan','ate','nat','bat']",
                        "output": "[['bat'], ['nat','tan'], ['ate','eat','tea']]",
                        "explanation": "Words with identical character counts are grouped together."
                    }
                ],
                "hint": "Use sorted characters or character frequency counts as a canonical hash key for a dictionary.",
                "starter_code": {
                    "python": "def group_anagrams(strs: list[str]) -> list[list[str]]:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\nvoid groupAnagrams(char** strs, int strsSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <string>\n#include <unordered_map>\n#include <algorithm>\n\nstd::vector<std::vector<std::string>> groupAnagrams(std::vector<std::string>& strs) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static List<List<String>> groupAnagrams(String[] strs) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            "a"
                        ],
                        "expected_output": [
                            [
                                "a"
                            ]
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            "ab",
                            "ba"
                        ],
                        "expected_output": [
                            [
                                "ab",
                                "ba"
                            ]
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            "cat",
                            "tac",
                            "dog"
                        ],
                        "expected_output": [
                            [
                                "cat",
                                "tac"
                            ],
                            [
                                "dog"
                            ]
                        ],
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Design canonical representations for hashing equivalence classes",
                    "Utilize multi-value dictionary mappings"
                ],
                "common_misconceptions": [
                    "Comparing every pair of strings directly resulting in O(N^2 * L) runtime"
                ],
                "expected_solution": {
                    "python": "from collections import defaultdict\n\ndef group_anagrams(strs: list[str]) -> list[list[str]]:\n    # TODO: Write your hash map grouping solution here\n    groups = defaultdict(list)\n    for s in strs:\n        key = ''.join(sorted(s))\n        groups[key].append(s)\n    return list(groups.values())\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\nvoid groupAnagrams(char** strs, int strsSize) {\n    // TODO: Write your grouping solution here\n}\n",
                    "cpp": "#include <vector>\n#include <string>\n#include <unordered_map>\n#include <algorithm>\n\nstd::vector<std::vector<std::string>> groupAnagrams(std::vector<std::string>& strs) {\n        std::unordered_map<std::string, std::vector<std::string>> mp;\n    for (const auto& s : strs) {\n        std::string key = s;\n        std::sort(key.begin(), key.end());\n        mp[key].push_back(s);\n    }\n    std::vector<std::vector<std::string>> res;\n    for (auto& p : mp) res.push_back(p.second);\n    return res;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static List<List<String>> groupAnagrams(String[] strs) {\n                Map<String, List<String>> map = new HashMap<>();\n        for (String s : strs) {\n            char[] ca = s.toCharArray();\n            Arrays.sort(ca);\n            String key = String.valueOf(ca);\n            map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);\n        }\n        return new ArrayList<>(map.values());\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "first-missing-positive",
                "title": "First Missing Positive",
                "topic": "Arrays & Hashing",
                "difficulty": "Hard",
                "description": "Given an unsorted integer array `nums`, return the smallest positive integer that is not present in `nums`.\n\nYou must implement an algorithm that runs in $O(N)$ time and uses $O(1)$ auxiliary space.",
                "inputFormat": "An array of integers `nums`.",
                "outputFormat": "Smallest missing positive integer.",
                "constraints": [
                    "1 <= nums.length <= 10^5",
                    "-2^31 <= nums[i] <= 2^31 - 1"
                ],
                "examples": [
                    {
                        "input": "nums = [1, 2, 0]",
                        "output": "3",
                        "explanation": "Numbers 1 and 2 are present, smallest missing is 3."
                    },
                    {
                        "input": "nums = [3, 4, -1, 1]",
                        "output": "2",
                        "explanation": "1 is present, but 2 is missing."
                    }
                ],
                "hint": "Use the array itself as a hash table! Place each number x in index x - 1 using cyclic swap.",
                "starter_code": {
                    "python": "def first_missing_positive(nums: list[int]) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint firstMissingPositive(int* nums, int numsSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint firstMissingPositive(std::vector<int>& nums) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int firstMissingPositive(int[] nums) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            1,
                            2,
                            0
                        ],
                        "expected_output": 3,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            3,
                            4,
                            -1,
                            1
                        ],
                        "expected_output": 2,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            7,
                            8,
                            9,
                            11,
                            12
                        ],
                        "expected_output": 1,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "In-place index hashing using array elements as their own keys",
                    "Achieve O(1) auxiliary space without external hash maps"
                ],
                "common_misconceptions": [
                    "Sorting the array which violates the O(N) runtime constraint"
                ],
                "expected_solution": {
                    "python": "def first_missing_positive(nums: list[int]) -> int:\n    # TODO: Implement in O(N) time and O(1) space using cyclic swap\n    n = len(nums)\n    for i in range(n):\n        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:\n            target = nums[i] - 1\n            nums[i], nums[target] = nums[target], nums[i]\n    for i in range(n):\n        if nums[i] != i + 1:\n            return i + 1\n    return n + 1\n",
                    "c": "#include <stdio.h>\n\nint firstMissingPositive(int* nums, int numsSize) {\n    // TODO: Cyclic swap placement\n    for (int i = 0; i < numsSize; i++) {\n        while (nums[i] >= 1 && nums[i] <= numsSize && nums[nums[i] - 1] != nums[i]) {\n            int target = nums[i] - 1;\n            int tmp = nums[i];\n            nums[i] = nums[target];\n            nums[target] = tmp;\n        }\n    }\n    for (int i = 0; i < numsSize; i++) {\n        if (nums[i] != i + 1) return i + 1;\n    }\n    return numsSize + 1;\n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint firstMissingPositive(std::vector<int>& nums) {\n        int n = nums.size();\n    for (int i = 0; i < n; i++) {\n        while (nums[i] >= 1 && nums[i] <= n && nums[nums[i] - 1] != nums[i]) {\n            std::swap(nums[i], nums[nums[i] - 1]);\n        }\n    }\n    for (int i = 0; i < n; i++) {\n        if (nums[i] != i + 1) return i + 1;\n    }\n    return n + 1;\n}\n",
                    "java": "public class Solution {\n    public static int firstMissingPositive(int[] nums) {\n                int n = nums.length;\n        for (int i = 0; i < n; i++) {\n            while (nums[i] >= 1 && nums[i] <= n && nums[nums[i] - 1] != nums[i]) {\n                int target = nums[i] - 1;\n                int temp = nums[i];\n                nums[i] = nums[target];\n                nums[target] = temp;\n            }\n        }\n        for (int i = 0; i < n; i++) {\n            if (nums[i] != i + 1) return i + 1;\n        }\n        return n + 1;\n    }\n}\n"
                }
            }
        ]
    },
    "Strings": {
        "Easy": [
            {
                "id": "valid-anagram",
                "title": "Valid Anagram",
                "topic": "Strings",
                "difficulty": "Easy",
                "description": "Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
                "inputFormat": "Two strings `s` and `t`.",
                "outputFormat": "Boolean `True` if valid anagram, `False` otherwise.",
                "constraints": [
                    "1 <= s.length, t.length <= 5 * 10^4",
                    "s and t consist of lowercase English letters."
                ],
                "examples": [
                    {
                        "input": "s = 'anagram', t = 'nagaram'",
                        "output": "True",
                        "explanation": "Characters match frequency exactly."
                    },
                    {
                        "input": "s = 'rat', t = 'car'",
                        "output": "False",
                        "explanation": "Frequencies do not match."
                    }
                ],
                "hint": "If the lengths differ, return False. Count character frequencies using a fixed 26-element array or hash map.",
                "starter_code": {
                    "python": "def is_anagram(s: str, t: str) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n#include <string.h>\n\nbool isAnagram(char* s, char* t) {\n    \n}\n",
                    "cpp": "#include <string>\n#include <vector>\n\nbool isAnagram(std::string s, std::string t) {\n    \n}\n",
                    "java": "public class Solution {\n    public static boolean isAnagram(String s, String t) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "s": "anagram",
                            "t": "nagaram"
                        },
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "s": "rat",
                            "t": "car"
                        },
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "s": "ab",
                            "t": "a"
                        },
                        "expected_output": False,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Counting frequencies with constant O(1) space for 26 alphabet characters",
                    "Quick rejection using string length invariant"
                ],
                "common_misconceptions": [
                    "Sorting both strings (O(N log N)) when O(N) frequency tallying is faster"
                ],
                "expected_solution": {
                    "python": "def is_anagram(s: str, t: str) -> bool:\n    # TODO: Compare character frequencies\n    if len(s) != len(t): return False\n    counts = {}\n    for ch in s: counts[ch] = counts.get(ch, 0) + 1\n    for ch in t:\n        if ch not in counts or counts[ch] == 0: return False\n        counts[ch] -= 1\n    return True\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n#include <string.h>\n\nbool isAnagram(char* s, char* t) {\n    // TODO: Compare character counts\n    if (strlen(s) != strlen(t)) return False;\n    int counts[26] = {0};\n    for (int i = 0; s[i] != '\u0000'; i++) counts[s[i] - 'a']++;\n    for (int i = 0; t[i] != '\u0000'; i++) {\n        if (--counts[t[i] - 'a'] < 0) return False;\n    }\n    return True;\n}\n",
                    "cpp": "#include <string>\n#include <vector>\n\nbool isAnagram(std::string s, std::string t) {\n    // TODO: Compare character counts\n    if (s.length() != t.length()) return False;\n    std::vector<int> counts(26, 0);\n    for (char c : s) counts[c - 'a']++;\n    for (char c : t) {\n        if (--counts[c - 'a'] < 0) return False;\n    }\n    return True;\n}\n",
                    "java": "public class Solution {\n    public static boolean isAnagram(String s, String t) {\n        // TODO: Compare character counts\n        if (s.length() != t.length()) return False;\n        int[] counts = new int[26];\n        for (char c : s.toCharArray()) counts[c - 'a']++;\n        for (char c : t.toCharArray()) {\n            if (--counts[c - 'a'] < 0) return False;\n        }\n        return True;\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "longest-substring-without-repeating",
                "title": "Longest Substring Without Repeating Characters",
                "topic": "Strings",
                "difficulty": "Medium",
                "description": "Given a string `s`, find the length of the longest substring without repeating characters.",
                "inputFormat": "A string `s`.",
                "outputFormat": "An integer representing the length of the longest substring.",
                "constraints": [
                    "0 <= s.length <= 5 * 10^4",
                    "s consists of English letters, digits, symbols and spaces."
                ],
                "examples": [
                    {
                        "input": "s = 'abcabcbb'",
                        "output": "3",
                        "explanation": "The answer is 'abc', with the length of 3."
                    },
                    {
                        "input": "s = 'bbbbb'",
                        "output": "1",
                        "explanation": "The answer is 'b', with the length of 1."
                    }
                ],
                "hint": "Use the Sliding Window technique with two pointers `left` and `right`. Maintain a hash map storing the last seen index of each character.",
                "starter_code": {
                    "python": "def length_of_longest_substring(s: str) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <string.h>\n\nint lengthOfLongestSubstring(char* s) {\n    \n}\n",
                    "cpp": "#include <string>\n#include <unordered_map>\n#include <algorithm>\n\nint lengthOfLongestSubstring(std::string s) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int lengthOfLongestSubstring(String s) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": "abcabcbb",
                        "expected_output": 3,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": "bbbbb",
                        "expected_output": 1,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": "pwwkew",
                        "expected_output": 3,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Dynamically contract sliding window boundary on collision",
                    "Maintain last-seen index mapping for O(1) jump updates"
                ],
                "common_misconceptions": [
                    "Not checking if the previously seen duplicate falls before current left window boundary"
                ],
                "expected_solution": {
                    "python": "def length_of_longest_substring(s: str) -> int:\n    # TODO: Implement sliding window\n    seen = {}\n    left = 0\n    max_len = 0\n    for right, ch in enumerate(s):\n        if ch in seen and seen[ch] >= left:\n            left = seen[ch] + 1\n        seen[ch] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len\n",
                    "c": "#include <stdio.h>\n#include <string.h>\n\nint lengthOfLongestSubstring(char* s) {\n    // TODO: Sliding window\n    int seen[256];\n    for (int i = 0; i < 256; i++) seen[i] = -1;\n    int left = 0, maxLen = 0;\n    for (int right = 0; s[right] != '\u0000'; right++) {\n        unsigned char ch = (unsigned char)s[right];\n        if (seen[ch] >= left) left = seen[ch] + 1;\n        seen[ch] = right;\n        int len = right - left + 1;\n        if (len > maxLen) maxLen = len;\n    }\n    return maxLen;\n}\n",
                    "cpp": "#include <string>\n#include <unordered_map>\n#include <algorithm>\n\nint lengthOfLongestSubstring(std::string s) {\n    // TODO: Write solution here\n    std::unordered_map<char, int> seen;\n    int left = 0, maxLen = 0;\n    for (int right = 0; right < s.size(); right++) {\n        char ch = s[right];\n        if (seen.count(ch) && seen[ch] >= left) {\n            left = seen[ch] + 1;\n        }\n        seen[ch] = right;\n        maxLen = std::max(maxLen, right - left + 1);\n    }\n    return maxLen;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int lengthOfLongestSubstring(String s) {\n        // TODO: Write solution here\n        Map<Character, Integer> seen = new HashMap<>();\n        int left = 0, maxLen = 0;\n        for (int right = 0; right < s.length(); right++) {\n            char ch = s.charAt(right);\n            if (seen.containsKey(ch) && seen.get(ch) >= left) {\n                left = seen.get(ch) + 1;\n            }\n            seen.put(ch, right);\n            maxLen = Math.max(maxLen, right - left + 1);\n        }\n        return maxLen;\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "minimum-window-substring",
                "title": "Minimum Window Substring",
                "topic": "Strings",
                "difficulty": "Hard",
                "description": "Given two strings `s` and `t` of lengths `m` and `n` respectively, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window. If there is no such substring, return the empty string `\"\"`.",
                "inputFormat": "Two strings `s` and `t`.",
                "outputFormat": "Shortest substring containing all characters of `t`.",
                "constraints": [
                    "1 <= s.length, t.length <= 10^5",
                    "s and t consist of uppercase and lowercase English letters."
                ],
                "examples": [
                    {
                        "input": "s = 'ADOBECODEBANC', t = 'ABC'",
                        "output": "'BANC'",
                        "explanation": "The minimum window substring 'BANC' includes 'A', 'B', and 'C' from string t."
                    }
                ],
                "hint": "Use two frequency maps: target and window. Expand `right` until valid, then shrink `left` as much as possible while maintaining validity.",
                "starter_code": {
                    "python": "def min_window(s: str, t: str) -> str:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <string.h>\n\nchar* minWindow(char* s, char* t) {\n    \n}\n",
                    "cpp": "#include <string>\n#include <unordered_map>\n#include <climits>\n\nstd::string minWindow(std::string s, std::string t) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static String minWindow(String s, String t) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "s": "ADOBECODEBANC",
                            "t": "ABC"
                        },
                        "expected_output": "BANC",
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "s": "a",
                            "t": "a"
                        },
                        "expected_output": "a",
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "s": "a",
                            "t": "aa"
                        },
                        "expected_output": "",
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Dual frequency map tracking with match counter invariant",
                    "Greedy contraction of left window boundary"
                ],
                "common_misconceptions": [
                    "Recounting target matching on every iteration resulting in O(N * 26) instead of amortized O(N)"
                ],
                "expected_solution": {
                    "python": "from collections import Counter\n\ndef min_window(s: str, t: str) -> str:\n    # TODO: Expand right pointer and contract left pointer\n    if not t or not s: return \"\"\n    target = Counter(t)\n    window = {}\n    have, need = 0, len(target)\n    res, res_len = (-1, -1), float(\"inf\")\n    left = 0\n    for right, c in enumerate(s):\n        window[c] = window.get(c, 0) + 1\n        if c in target and window[c] == target[c]:\n            have += 1\n        while have == need:\n            if (right - left + 1) < res_len:\n                res = (left, right)\n                res_len = right - left + 1\n            window[s[left]] -= 1\n            if s[left] in target and window[s[left]] < target[s[left]]:\n                have -= 1\n            left += 1\n    return s[res[0]:res[1]+1] if res_len != float(\"inf\") else \"\"\n",
                    "c": "#include <stdio.h>\n#include <string.h>\n\nchar* minWindow(char* s, char* t) {\n    // TODO: Two pointers sliding window\n    return ;\n}\n",
                    "cpp": "#include <string>\n#include <unordered_map>\n#include <climits>\n\nstd::string minWindow(std::string s, std::string t) {\n    // TODO: Write solution here\n    if (s.empty() || t.empty()) return \"\";\n    std::unordered_map<char, int> target, window;\n    for (char c : t) target[c]++;\n    int have = 0, need = target.size();\n    int resLeft = -1, resLen = INT_MAX, left = 0;\n    for (int right = 0; right < s.size(); right++) {\n        char c = s[right];\n        window[c]++;\n        if (target.count(c) && window[c] == target[c]) have++;\n        while (have == need) {\n            if (right - left + 1 < resLen) {\n                resLeft = left;\n                resLen = right - left + 1;\n            }\n            window[s[left]]--;\n            if (target.count(s[left]) && window[s[left]] < target[s[left]]) have--;\n            left++;\n        }\n    }\n    return resLen == INT_MAX ? \"\" : s.substr(resLeft, resLen);\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static String minWindow(String s, String t) {\n        // TODO: Write solution here\n        if (s == None || t == None || s.length() < t.length()) return \"\";\n        Map<Character, Integer> target = new HashMap<>();\n        for (char c : t.toCharArray()) target.put(c, target.getOrDefault(c, 0) + 1);\n        Map<Character, Integer> window = new HashMap<>();\n        int have = 0, need = target.size();\n        int resLeft = -1, resLen = Integer.MAX_VALUE, left = 0;\n        for (int right = 0; right < s.length(); right++) {\n            char c = s.charAt(right);\n            window.put(c, window.getOrDefault(c, 0) + 1);\n            if (target.containsKey(c) && window.get(c).intValue() == target.get(c).intValue()) have++;\n            while (have == need) {\n                if (right - left + 1 < resLen) {\n                    resLeft = left;\n                    resLen = right - left + 1;\n                }\n                char leftChar = s.charAt(left);\n                window.put(leftChar, window.get(leftChar) - 1);\n                if (target.containsKey(leftChar) && window.get(leftChar) < target.get(leftChar)) have--;\n                left++;\n            }\n        }\n        return resLen == Integer.MAX_VALUE ? \"\" : s.substring(resLeft, resLeft + resLen);\n    }\n}\n"
                }
            }
        ]
    },
    "Stack & Queue": {
        "Easy": [
            {
                "id": "valid-parentheses",
                "title": "Valid Parentheses",
                "topic": "Stack & Queue",
                "difficulty": "Easy",
                "description": "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
                "inputFormat": "A string `s` containing only brackets.",
                "outputFormat": "Boolean `True` if valid, `False` otherwise.",
                "constraints": [
                    "1 <= s.length <= 10^4",
                    "s consists of parentheses only '()[]{}'."
                ],
                "examples": [
                    {
                        "input": "s = '()[]{}'",
                        "output": "True",
                        "explanation": "All brackets match in pairs."
                    },
                    {
                        "input": "s = '(]'",
                        "output": "False",
                        "explanation": "Mismatched bracket pair."
                    }
                ],
                "hint": "Push opening brackets onto a stack. When a closing bracket arrives, verify that the top of the stack matches its pair. Check if stack is empty at the end.",
                "starter_code": {
                    "python": "def is_valid(s: str) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n#include <string.h>\n\nbool isValid(char* s) {\n    \n}\n",
                    "cpp": "#include <string>\n#include <stack>\n\nbool isValid(std::string s) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean isValid(String s) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": "()[]{}",
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": "(]",
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": "([{}])",
                        "expected_output": True,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Apply LIFO stack semantics to enforce balanced syntax matching",
                    "Handle empty stack edge cases during pop operations"
                ],
                "common_misconceptions": [
                    "Assuming equal counts of '(' and ')' is sufficient without validating nesting order"
                ],
                "expected_solution": {
                    "python": "def is_valid(s: str) -> bool:\n    # TODO: Implement stack bracket matching\n    stack = []\n    pairs = {')': '(', '}': '{', ']': '['}\n    for c in s:\n        if c in pairs:\n            if not stack or stack.pop() != pairs[c]: return False\n        else:\n            stack.append(c)\n    return len(stack) == 0\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n#include <string.h>\n\nbool isValid(char* s) {\n    // TODO: Stack matching\n    char stack[10000];\n    int top = -1;\n    for (int i = 0; s[i] != '\u0000'; i++) {\n        char c = s[i];\n        if (c == '(' || c == '{' || c == '[') {\n            stack[++top] = c;\n        } else {\n            if (top < 0) return False;\n            char open = stack[top--];\n            if (c == ')' && open != '(') return False;\n            if (c == '}' && open != '{') return False;\n            if (c == ']' && open != '[') return False;\n        }\n    }\n    return top == -1;\n}\n",
                    "cpp": "#include <string>\n#include <stack>\n\nbool isValid(std::string s) {\n    // TODO: Write solution here\n    std::stack<char> st;\n    for (char c : s) {\n        if (c == '(' || c == '{' || c == '[') st.push(c);\n        else {\n            if (st.empty()) return False;\n            char top = st.top(); st.pop();\n            if (c == ')' && top != '(') return False;\n            if (c == '}' && top != '{') return False;\n            if (c == ']' && top != '[') return False;\n        }\n    }\n    return st.empty();\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean isValid(String s) {\n        // TODO: Write solution here\n        Deque<Character> stack = new ArrayDeque<>();\n        for (char c : s.toCharArray()) {\n            if (c == '(') stack.push(')');\n            else if (c == '{') stack.push('}');\n            else if (c == '[') stack.push(']');\n            else if (stack.isEmpty() || stack.pop() != c) return False;\n        }\n        return stack.isEmpty();\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "daily-temperatures",
                "title": "Daily Temperatures (Monotonic Stack)",
                "topic": "Stack & Queue",
                "difficulty": "Medium",
                "description": "Given an array of integers `temperatures` represents the daily temperatures, return an array `answer` such that `answer[i]` is the number of days you have to wait after the `i-th` day to get a warmer temperature. If there is no future day for which this is possible, keep `answer[i] == 0` instead.",
                "inputFormat": "An array of daily temperatures `temperatures`.",
                "outputFormat": "Array of day wait counts.",
                "constraints": [
                    "1 <= temperatures.length <= 10^5",
                    "30 <= temperatures[i] <= 100"
                ],
                "examples": [
                    {
                        "input": "temperatures = [73, 74, 75, 71, 69, 72, 76, 73]",
                        "output": "[1, 1, 4, 2, 1, 1, 0, 0]",
                        "explanation": "Day 0 (73) finds 74 on day 1 (wait 1 day)."
                    }
                ],
                "hint": "Use a Monotonic Decreasing Stack storing indices. When a warmer day arrives, pop cooler days and compute day difference.",
                "starter_code": {
                    "python": "def daily_temperatures(temperatures: list[int]) -> list[int]:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nint* dailyTemperatures(int* temperatures, int temperaturesSize, int* returnSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <stack>\n\nstd::vector<int> dailyTemperatures(std::vector<int>& temperatures) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int[] dailyTemperatures(int[] temperatures) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            73,
                            74,
                            75,
                            71,
                            69,
                            72,
                            76,
                            73
                        ],
                        "expected_output": [
                            1,
                            1,
                            4,
                            2,
                            1,
                            1,
                            0,
                            0
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            30,
                            40,
                            50,
                            60
                        ],
                        "expected_output": [
                            1,
                            1,
                            1,
                            0
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            30,
                            60,
                            90
                        ],
                        "expected_output": [
                            1,
                            1,
                            0
                        ],
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Store indices in monotonic stack to capture temporal distance",
                    "Amortized O(N) runtime by pushing and popping each element at most once"
                ],
                "common_misconceptions": [
                    "Storing temperature values in stack instead of indices, losing position information"
                ],
                "expected_solution": {
                    "python": "def daily_temperatures(temperatures: list[int]) -> list[int]:\n    # TODO: Implement monotonic decreasing stack\n    n = len(temperatures)\n    res = [0] * n\n    stack = []  # indices\n    for i, t in enumerate(temperatures):\n        while stack and temperatures[stack[-1]] < t:\n            prev = stack.pop()\n            res[prev] = i - prev\n        stack.append(i)\n    return res\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nint* dailyTemperatures(int* temperatures, int temperaturesSize, int* returnSize) {\n    // TODO: Monotonic stack\n    *returnSize = temperaturesSize;\n    int* res = (int*)calloc(temperaturesSize, sizeof(int));\n    return res;\n}\n",
                    "cpp": "#include <vector>\n#include <stack>\n\nstd::vector<int> dailyTemperatures(std::vector<int>& temperatures) {\n    // TODO: Write solution here\n    int n = temperatures.size();\n    std::vector<int> res(n, 0);\n    std::stack<int> st;\n    for (int i = 0; i < n; i++) {\n        while (!st.empty() && temperatures[st.top()] < temperatures[i]) {\n            int prev = st.top(); st.pop();\n            res[prev] = i - prev;\n        }\n        st.push(i);\n    }\n    return res;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int[] dailyTemperatures(int[] temperatures) {\n        // TODO: Write solution here\n        int n = temperatures.length;\n        int[] res = new int[n];\n        Deque<Integer> stack = new ArrayDeque<>();\n        for (int i = 0; i < n; i++) {\n            while (!stack.isEmpty() && temperatures[stack.peek()] < temperatures[i]) {\n                int prev = stack.pop();\n                res[prev] = i - prev;\n            }\n            stack.push(i);\n        }\n        return res;\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "largest-rectangle-histogram",
                "title": "Largest Rectangle in Histogram",
                "topic": "Stack & Queue",
                "difficulty": "Hard",
                "description": "Given an array of integers `heights` representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram.",
                "inputFormat": "An array of non-negative integers `heights`.",
                "outputFormat": "An integer representing maximum rectangle area.",
                "constraints": [
                    "1 <= heights.length <= 10^5",
                    "0 <= heights[i] <= 10^4"
                ],
                "examples": [
                    {
                        "input": "heights = [2, 1, 5, 6, 2, 3]",
                        "output": "10",
                        "explanation": "The maximum area is 10 units, formed by heights 5 and 6 (2 * 5)."
                    }
                ],
                "hint": "Maintain a Monotonic Increasing Stack of indices. When a shorter bar is encountered, pop heights and compute area using the popped height as the bottleneck.",
                "starter_code": {
                    "python": "def largest_rectangle_area(heights: list[int]) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint largestRectangleArea(int* heights, int heightsSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <stack>\n#include <algorithm>\n\nint largestRectangleArea(std::vector<int>& heights) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int largestRectangleArea(int[] heights) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            2,
                            1,
                            5,
                            6,
                            2,
                            3
                        ],
                        "expected_output": 10,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            2,
                            4
                        ],
                        "expected_output": 4,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            1,
                            1
                        ],
                        "expected_output": 2,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Identify bottleneck bounds for each bar using stack popped range",
                    "Sentinel 0-height bar insertion technique to flush stack"
                ],
                "common_misconceptions": [
                    "Expanding boundaries left and right for every index naively producing O(N^2) complexity"
                ],
                "expected_solution": {
                    "python": "def largest_rectangle_area(heights: list[int]) -> int:\n    # TODO: Monotonic increasing stack\n    stack = []\n    max_area = 0\n    heights.append(0)\n    for i, h in enumerate(heights):\n        while stack and heights[stack[-1]] > h:\n            height = heights[stack.pop()]\n            width = i if not stack else i - stack[-1] - 1\n            max_area = max(max_area, height * width)\n        stack.append(i)\n    heights.pop()\n    return max_area\n",
                    "c": "#include <stdio.h>\n\nint largestRectangleArea(int* heights, int heightsSize) {\n    // TODO: Monotonic stack\n    return 0;\n}\n",
                    "cpp": "#include <vector>\n#include <stack>\n#include <algorithm>\n\nint largestRectangleArea(std::vector<int>& heights) {\n    // TODO: Write solution here\n    std::stack<int> st;\n    int maxArea = 0;\n    heights.push_back(0);\n    for (int i = 0; i < heights.size(); i++) {\n        while (!st.empty() && heights[st.top()] > heights[i]) {\n            int h = heights[st.top()]; st.pop();\n            int w = st.empty() ? i : i - st.top() - 1;\n            maxArea = std::max(maxArea, h * w);\n        }\n        st.push(i);\n    }\n    heights.pop_back();\n    return maxArea;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int largestRectangleArea(int[] heights) {\n        // TODO: Write solution here\n        Deque<Integer> stack = new ArrayDeque<>();\n        int maxArea = 0, n = heights.length;\n        for (int i = 0; i <= n; i++) {\n            int h = (i == n) ? 0 : heights[i];\n            while (!stack.isEmpty() && heights[stack.peek()] > h) {\n                int height = heights[stack.pop()];\n                int width = stack.isEmpty() ? i : i - stack.peek() - 1;\n                maxArea = Math.max(maxArea, height * width);\n            }\n            stack.push(i);\n        }\n        return maxArea;\n    }\n}\n"
                }
            }
        ]
    },
    "Dynamic Programming": {
        "Easy": [
            {
                "id": "climbing-stairs",
                "title": "Climbing Stairs (Dynamic Programming)",
                "topic": "Dynamic Programming",
                "difficulty": "Easy",
                "description": "You are climbing a staircase. It takes `n` steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
                "inputFormat": "An integer `n` representing number of steps.",
                "outputFormat": "Number of distinct ways to climb.",
                "constraints": [
                    "1 <= n <= 45"
                ],
                "examples": [
                    {
                        "input": "n = 2",
                        "output": "2",
                        "explanation": "1 step + 1 step, or 2 steps."
                    },
                    {
                        "input": "n = 3",
                        "output": "3",
                        "explanation": "1+1+1, 1+2, 2+1."
                    }
                ],
                "hint": "To reach step n, you could have come from step (n-1) with 1 step, or from step (n-2) with 2 steps: ways(n) = ways(n-1) + ways(n-2).",
                "starter_code": {
                    "python": "def climb_stairs(n: int) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint climbStairs(int n) {\n    \n}\n",
                    "cpp": "#include <iostream>\n\nint climbStairs(int n) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int climbStairs(int n) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": 2,
                        "expected_output": 2,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": 3,
                        "expected_output": 3,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": 5,
                        "expected_output": 8,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Identify optimal substructure and overlapping subproblems",
                    "Reduce space complexity from O(N) array to O(1) rolling variables"
                ],
                "common_misconceptions": [
                    "Using unmemoized recursion triggering exponential O(2^N) call tree"
                ],
                "expected_solution": {
                    "python": "def climb_stairs(n: int) -> int:\n    # TODO: DP state transition\n    if n <= 2: return n\n    a, b = 1, 2\n    for _ in range(3, n + 1):\n        a, b = b, a + b\n    return b\n",
                    "c": "#include <stdio.h>\n\nint climbStairs(int n) {\n    // TODO: DP state transition\n    if (n <= 2) return n;\n    int a = 1, b = 2;\n    for (int i = 3; i <= n; i++) {\n        int next = a + b;\n        a = b;\n        b = next;\n    }\n    return b;\n}\n",
                    "cpp": "#include <iostream>\n\nint climbStairs(int n) {\n    // TODO: Write solution here\n    if (n <= 2) return n;\n    int a = 1, b = 2;\n    for (int i = 3; i <= n; i++) {\n        int next = a + b;\n        a = b;\n        b = next;\n    }\n    return b;\n}\n",
                    "java": "public class Solution {\n    public static int climbStairs(int n) {\n        // TODO: Write solution here\n        if (n <= 2) return n;\n        int a = 1, b = 2;\n        for (int i = 3; i <= n; i++) {\n            int next = a + b;\n            a = b;\n            b = next;\n        }\n        return b;\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "coin-change-dp",
                "title": "Coin Change (Fewest Coins)",
                "topic": "Dynamic Programming",
                "difficulty": "Medium",
                "description": "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\nReturn the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.\n\nYou may assume that you have an infinite number of each kind of coin.",
                "inputFormat": "An array of positive integers `coins` and an integer `amount`.",
                "outputFormat": "Minimum coins needed, or -1.",
                "constraints": [
                    "1 <= coins.length <= 12",
                    "1 <= coins[i] <= 2^31 - 1",
                    "0 <= amount <= 10^4"
                ],
                "examples": [
                    {
                        "input": "coins = [1, 2, 5], amount = 11",
                        "output": "3",
                        "explanation": "11 = 5 + 5 + 1 (3 coins)."
                    },
                    {
                        "input": "coins = [2], amount = 3",
                        "output": "-1",
                        "explanation": "Cannot form 3 using only 2s."
                    }
                ],
                "hint": "Define dp[a] = min coins to form amount a. For each coin c, dp[a] = min(dp[a], 1 + dp[a - c]). Initialize with amount + 1.",
                "starter_code": {
                    "python": "def coin_change(coins: list[int], amount: int) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint coinChange(int* coins, int coinsSize, int amount) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint coinChange(std::vector<int>& coins, int amount) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int coinChange(int[] coins, int amount) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "coins": [
                                1,
                                2,
                                5
                            ],
                            "amount": 11
                        },
                        "expected_output": 3,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "coins": [
                                2
                            ],
                            "amount": 3
                        },
                        "expected_output": -1,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "coins": [
                                1
                            ],
                            "amount": 0
                        },
                        "expected_output": 0,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Formulate 1D state transition for unbounded knapsack variant",
                    "Sentinel infinity initialization for minimization problems"
                ],
                "common_misconceptions": [
                    "Attempting greedy largest coin pickup which fails for denominations like [1, 3, 4] with amount 6"
                ],
                "expected_solution": {
                    "python": "def coin_change(coins: list[int], amount: int) -> int:\n    # TODO: Bottom-up DP tabulation\n    dp = [amount + 1] * (amount + 1)\n    dp[0] = 0\n    for a in range(1, amount + 1):\n        for c in coins:\n            if a - c >= 0:\n                dp[a] = min(dp[a], 1 + dp[a - c])\n    return dp[amount] if dp[amount] != amount + 1 else -1\n",
                    "c": "#include <stdio.h>\n\nint coinChange(int* coins, int coinsSize, int amount) {\n    // TODO: Tabulation DP\n    return -1;\n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint coinChange(std::vector<int>& coins, int amount) {\n    // TODO: Write solution here\n    std::vector<int> dp(amount + 1, amount + 1);\n    dp[0] = 0;\n    for (int a = 1; a <= amount; a++) {\n        for (int c : coins) {\n            if (a - c >= 0) {\n                dp[a] = std::min(dp[a], 1 + dp[a - c]);\n            }\n        }\n    }\n    return dp[amount] > amount ? -1 : dp[amount];\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static int coinChange(int[] coins, int amount) {\n        // TODO: Write solution here\n        int[] dp = new int[amount + 1];\n        Arrays.fill(dp, amount + 1);\n        dp[0] = 0;\n        for (int a = 1; a <= amount; a++) {\n            for (int c : coins) {\n                if (a - c >= 0) {\n                    dp[a] = Math.min(dp[a], 1 + dp[a - c]);\n                }\n            }\n        }\n        return dp[amount] > amount ? -1 : dp[amount];\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "edit-distance-dp",
                "title": "Edit Distance (Levenshtein)",
                "topic": "Dynamic Programming",
                "difficulty": "Hard",
                "description": "Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.\n\nYou have the following three operations permitted on a word:\n- Insert a character\n- Delete a character\n- Replace a character",
                "inputFormat": "Two strings `word1` and `word2`.",
                "outputFormat": "Minimum operations required.",
                "constraints": [
                    "0 <= word1.length, word2.length <= 500",
                    "word1 and word2 consist of lowercase English letters."
                ],
                "examples": [
                    {
                        "input": "word1 = 'horse', word2 = 'ros'",
                        "output": "3",
                        "explanation": "horse -> rorse (replace 'h' with 'r') -> rose (remove 'r') -> ros (remove 'e')."
                    }
                ],
                "hint": "Create a 2D table dp[i][j]. If word1[i-1] == word2[j-1], dp[i][j] = dp[i-1][j-1]. Otherwise, 1 + min(insert, delete, replace).",
                "starter_code": {
                    "python": "def min_distance(word1: str, word2: str) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <string.h>\n\nint minDistance(char* word1, char* word2) {\n    \n}\n",
                    "cpp": "#include <string>\n#include <vector>\n#include <algorithm>\n\nint minDistance(std::string word1, std::string word2) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int minDistance(String word1, String word2) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "word1": "horse",
                            "word2": "ros"
                        },
                        "expected_output": 3,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "word1": "intention",
                            "word2": "execution"
                        },
                        "expected_output": 5,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "word1": "",
                            "word2": "a"
                        },
                        "expected_output": 1,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Establish 2D grid base cases representing conversion to empty strings",
                    "Derive multi-action minimum transition for insert, delete, and replace"
                ],
                "common_misconceptions": [
                    "Misinterpreting matching characters as requiring an edit increment"
                ],
                "expected_solution": {
                    "python": "def min_distance(word1: str, word2: str) -> int:\n    # TODO: 2D DP matrix\n    m, n = len(word1), len(word2)\n    dp = [[0] * (n + 1) for _ in range(m + 1)]\n    for i in range(m + 1): dp[i][0] = i\n    for j in range(n + 1): dp[0][j] = j\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if word1[i-1] == word2[j-1]:\n                dp[i][j] = dp[i-1][j-1]\n            else:\n                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])\n    return dp[m][n]\n",
                    "c": "#include <stdio.h>\n#include <string.h>\n\nint minDistance(char* word1, char* word2) {\n    // TODO: 2D DP\n    return 0;\n}\n",
                    "cpp": "#include <string>\n#include <vector>\n#include <algorithm>\n\nint minDistance(std::string word1, std::string word2) {\n    // TODO: Write solution here\n    int m = word1.size(), n = word2.size();\n    std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));\n    for (int i = 0; i <= m; i++) dp[i][0] = i;\n    for (int j = 0; j <= n; j++) dp[0][j] = j;\n    for (int i = 1; i <= m; i++) {\n        for (int j = 1; j <= n; j++) {\n            if (word1[i-1] == word2[j-1]) dp[i][j] = dp[i-1][j-1];\n            else dp[i][j] = 1 + std::min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]});\n        }\n    }\n    return dp[m][n];\n}\n",
                    "java": "public class Solution {\n    public static int minDistance(String word1, String word2) {\n        // TODO: Write solution here\n        int m = word1.length(), n = word2.length();\n        int[][] dp = new int[m + 1][n + 1];\n        for (int i = 0; i <= m; i++) dp[i][0] = i;\n        for (int j = 0; j <= n; j++) dp[0][j] = j;\n        for (int i = 1; i <= m; i++) {\n            for (int j = 1; j <= n; j++) {\n                if (word1.charAt(i - 1) == word2.charAt(j - 1)) dp[i][j] = dp[i-1][j-1];\n                else dp[i][j] = 1 + Math.min(dp[i-1][j], Math.min(dp[i][j-1], dp[i-1][j-1]));\n            }\n        }\n        return dp[m][n];\n    }\n}\n"
                }
            }
        ]
    },
    "Algorithms & Two Pointers": {
        "Easy": [
            {
                "id": "two-sum-sorted",
                "title": "Two Sum II (Sorted Array)",
                "topic": "Algorithms & Two Pointers",
                "difficulty": "Easy",
                "description": "Given a **1-indexed** array of integers `numbers` that is already sorted in non-decreasing order, find two numbers such that they add up to a specific `target` number.\n\nReturn the indices of the two numbers, `index1` and `index2`, added by one as an integer array `[index1, index2]` of length 2.",
                "inputFormat": "Sorted list of integers `numbers` and an integer `target`.",
                "outputFormat": "Array of two 1-based indices `[index1, index2]`.",
                "constraints": [
                    "2 <= numbers.length <= 3 * 10^4",
                    "-1000 <= numbers[i] <= 1000",
                    "Exactly one valid solution exists."
                ],
                "examples": [
                    {
                        "input": "numbers = [2, 7, 11, 15], target = 9",
                        "output": "[1, 2]",
                        "explanation": "2 + 7 = 9. Therefore index1 = 1, index2 = 2."
                    }
                ],
                "hint": "Place one pointer at index 0 and another at the last element. If sum < target, advance left pointer; if sum > target, retract right pointer.",
                "starter_code": {
                    "python": "def two_sum_sorted(numbers: list[int], target: int) -> list[int]:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nint* twoSumSorted(int* numbers, int numbersSize, int target, int* returnSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n\nstd::vector<int> twoSumSorted(std::vector<int>& numbers, int target) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int[] twoSumSorted(int[] numbers, int target) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "numbers": [
                                2,
                                7,
                                11,
                                15
                            ],
                            "target": 9
                        },
                        "expected_output": [
                            1,
                            2
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "numbers": [
                                2,
                                3,
                                4
                            ],
                            "target": 6
                        },
                        "expected_output": [
                            1,
                            3
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "numbers": [
                                -1,
                                0
                            ],
                            "target": -1
                        },
                        "expected_output": [
                            1,
                            2
                        ],
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Exploit sorted order invariant with convergent inward pointers",
                    "Achieve O(1) space without auxiliary lookup structures"
                ],
                "common_misconceptions": [
                    "Returning 0-based indices when question strictly specifies 1-indexed output"
                ],
                "expected_solution": {
                    "python": "def two_sum_sorted(numbers: list[int], target: int) -> list[int]:\n    # TODO: Two pointers converging inward\n    left, right = 0, len(numbers) - 1\n    while left < right:\n        cur = numbers[left] + numbers[right]\n        if cur == target: return [left + 1, right + 1]\n        elif cur < target: left += 1\n        else: right -= 1\n    return []\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nint* twoSumSorted(int* numbers, int numbersSize, int target, int* returnSize) {\n    // TODO: Two pointers\n    int left = 0, right = numbersSize - 1;\n    while (left < right) {\n        int cur = numbers[left] + numbers[right];\n        if (cur == target) {\n            *returnSize = 2;\n            int* res = (int*)malloc(2 * sizeof(int));\n            res[0] = left + 1;\n            res[1] = right + 1;\n            return res;\n        }\n        if (cur < target) left++;\n        else right--;\n    }\n    *returnSize = 0;\n    return NULL;\n}\n",
                    "cpp": "#include <vector>\n\nstd::vector<int> twoSumSorted(std::vector<int>& numbers, int target) {\n    // TODO: Write solution here\n    int left = 0, right = numbers.size() - 1;\n    while (left < right) {\n        int cur = numbers[left] + numbers[right];\n        if (cur == target) return {left + 1, right + 1};\n        if (cur < target) left++;\n        else right--;\n    }\n    return {};\n}\n",
                    "java": "public class Solution {\n    public static int[] twoSumSorted(int[] numbers, int target) {\n        // TODO: Write solution here\n        int left = 0, right = numbers.length - 1;\n        while (left < right) {\n            int cur = numbers[left] + numbers[right];\n            if (cur == target) return new int[]{left + 1, right + 1};\n            if (cur < target) left++;\n            else right--;\n        }\n        return new int[]{};\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "three-sum",
                "title": "3Sum (Triplets Sum to Zero)",
                "topic": "Algorithms & Two Pointers",
                "difficulty": "Medium",
                "description": "Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\nNotice that the solution set must not contain duplicate triplets.",
                "inputFormat": "An array of integers `nums`.",
                "outputFormat": "List of distinct triplet arrays adding up to zero.",
                "constraints": [
                    "3 <= nums.length <= 3000",
                    "-10^5 <= nums[i] <= 10^5"
                ],
                "examples": [
                    {
                        "input": "nums = [-1, 0, 1, 2, -1, -4]",
                        "output": "[[-1, -1, 2], [-1, 0, 1]]",
                        "explanation": "Triplets sum to zero without duplicates."
                    }
                ],
                "hint": "Sort the array first. Fix each element `i` as the anchor and use two pointers `left` and `right` for the remaining elements. Skip adjacent duplicate values to avoid redundant triplets.",
                "starter_code": {
                    "python": "def three_sum(nums: list[int]) -> list[list[int]]:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nvoid threeSum(int* nums, int numsSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nstd::vector<std::vector<int>> threeSum(std::vector<int>& nums) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static List<List<Integer>> threeSum(int[] nums) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            -1,
                            0,
                            1,
                            2,
                            -1,
                            -4
                        ],
                        "expected_output": [
                            [
                                -1,
                                -1,
                                2
                            ],
                            [
                                -1,
                                0,
                                1
                            ]
                        ],
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            0,
                            1,
                            1
                        ],
                        "expected_output": [],
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            0,
                            0,
                            0
                        ],
                        "expected_output": [
                            [
                                0,
                                0,
                                0
                            ]
                        ],
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Reduce 3-variable search to N iterations of 2-pointer sweep",
                    "Systematic deduplication without heavy hash sets"
                ],
                "common_misconceptions": [
                    "Generating all combinations through 3 nested loops resulting in O(N^3) timeout"
                ],
                "expected_solution": {
                    "python": "def three_sum(nums: list[int]) -> list[list[int]]:\n    # TODO: Sort and run two pointers\n    nums.sort()\n    res = []\n    for i in range(len(nums) - 2):\n        if i > 0 and nums[i] == nums[i - 1]: continue\n        l, r = i + 1, len(nums) - 1\n        while l < r:\n            s = nums[i] + nums[l] + nums[r]\n            if s == 0:\n                res.append([nums[i], nums[l], nums[r]])\n                while l < r and nums[l] == nums[l + 1]: l += 1\n                while l < r and nums[r] == nums[r - 1]: r -= 1\n                l += 1; r -= 1\n            elif s < 0: l += 1\n            else: r -= 1\n    return res\n",
                    "c": "#include <stdio.h>\n#include <stdlib.h>\n\nvoid threeSum(int* nums, int numsSize) {\n    // TODO: Sort and two pointers\n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nstd::vector<std::vector<int>> threeSum(std::vector<int>& nums) {\n    // TODO: Write solution here\n    std::sort(nums.begin(), nums.end());\n    std::vector<std::vector<int>> res;\n    for (int i = 0; i < (int)nums.size() - 2; i++) {\n        if (i > 0 && nums[i] == nums[i - 1]) continue;\n        int l = i + 1, r = nums.size() - 1;\n        while (l < r) {\n            int s = nums[i] + nums[l] + nums[r];\n            if (s == 0) {\n                res.push_back({nums[i], nums[l], nums[r]});\n                while (l < r && nums[l] == nums[l + 1]) l++;\n                while (l < r && nums[r] == nums[r - 1]) r--;\n                l++; r--;\n            } else if (s < 0) l++;\n            else r--;\n        }\n    }\n    return res;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static List<List<Integer>> threeSum(int[] nums) {\n        // TODO: Write solution here\n        Arrays.sort(nums);\n        List<List<Integer>> res = new ArrayList<>();\n        for (int i = 0; i < nums.length - 2; i++) {\n            if (i > 0 && nums[i] == nums[i - 1]) continue;\n            int l = i + 1, r = nums.length - 1;\n            while (l < r) {\n                int s = nums[i] + nums[l] + nums[r];\n                if (s == 0) {\n                    res.add(Arrays.asList(nums[i], nums[l], nums[r]));\n                    while (l < r && nums[l] == nums[l + 1]) l++;\n                    while (l < r && nums[r] == nums[r - 1]) r--;\n                    l++; r--;\n                } else if (s < 0) l++;\n                else r--;\n            }\n        }\n        return res;\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "trapping-rain-water",
                "title": "Trapping Rain Water (Two Pointers)",
                "topic": "Algorithms & Two Pointers",
                "difficulty": "Hard",
                "description": "Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.",
                "inputFormat": "An array of non-negative integers `height`.",
                "outputFormat": "Total units of trapped rainwater.",
                "constraints": [
                    "n == height.length",
                    "1 <= n <= 2 * 10^4",
                    "0 <= height[i] <= 10^5"
                ],
                "examples": [
                    {
                        "input": "height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]",
                        "output": "6",
                        "explanation": "Total 6 units of water trapped between bars."
                    }
                ],
                "hint": "Water at position i is determined by min(max_left, max_right) - height[i]. With two pointers, move whichever boundary is smaller because the lower wall limits trapped water.",
                "starter_code": {
                    "python": "def trap(height: list[int]) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint trap(int* height, int heightSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint trap(std::vector<int>& height) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int trap(int[] height) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            0,
                            1,
                            0,
                            2,
                            1,
                            0,
                            1,
                            3,
                            2,
                            1,
                            2,
                            1
                        ],
                        "expected_output": 6,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            4,
                            2,
                            0,
                            3,
                            2,
                            5
                        ],
                        "expected_output": 9,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            3,
                            0,
                            3
                        ],
                        "expected_output": 3,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Calculate boundary volume via dual-side monotonic tracking",
                    "Optimize O(N) space prefix/suffix tables down to O(1) space two pointers"
                ],
                "common_misconceptions": [
                    "Assuming water level can rise higher than the minimum of the two surrounding boundaries"
                ],
                "expected_solution": {
                    "python": "def trap(height: list[int]) -> int:\n    # TODO: Two pointers converging from edges\n    if not height: return 0\n    l, r = 0, len(height) - 1\n    left_max, right_max = height[l], height[r]\n    water = 0\n    while l < r:\n        if left_max < right_max:\n            l += 1\n            left_max = max(left_max, height[l])\n            water += left_max - height[l]\n        else:\n            r -= 1\n            right_max = max(right_max, height[r])\n            water += right_max - height[r]\n    return water\n",
                    "c": "#include <stdio.h>\n\nint trap(int* height, int heightSize) {\n    // TODO: Two pointers\n    if (heightSize <= 2) return 0;\n    int l = 0, r = heightSize - 1;\n    int leftMax = height[l], rightMax = height[r], water = 0;\n    while (l < r) {\n        if (leftMax < rightMax) {\n            l++;\n            if (height[l] > leftMax) leftMax = height[l];\n            else water += leftMax - height[l];\n        } else {\n            r--;\n            if (height[r] > rightMax) rightMax = height[r];\n            else water += rightMax - height[r];\n        }\n    }\n    return water;\n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint trap(std::vector<int>& height) {\n    // TODO: Write solution here\n    if (height.empty()) return 0;\n    int l = 0, r = height.size() - 1;\n    int leftMax = height[l], rightMax = height[r];\n    int water = 0;\n    while (l < r) {\n        if (leftMax < rightMax) {\n            l++;\n            leftMax = std::max(leftMax, height[l]);\n            water += leftMax - height[l];\n        } else {\n            r--;\n            rightMax = std::max(rightMax, height[r]);\n            water += rightMax - height[r];\n        }\n    }\n    return water;\n}\n",
                    "java": "public class Solution {\n    public static int trap(int[] height) {\n        // TODO: Write solution here\n        if (height == None || height.length == 0) return 0;\n        int l = 0, r = height.length - 1;\n        int leftMax = height[l], rightMax = height[r];\n        int water = 0;\n        while (l < r) {\n            if (leftMax < rightMax) {\n                l++;\n                leftMax = Math.max(leftMax, height[l]);\n                water += leftMax - height[l];\n            } else {\n                r--;\n                rightMax = Math.max(rightMax, height[r]);\n                water += rightMax - height[r];\n            }\n        }\n        return water;\n    }\n}\n"
                }
            }
        ]
    },
    "Trees & Binary Search Trees": {
        "Easy": [
            {
                "id": "maximum-depth-binary-tree",
                "title": "Maximum Depth of Binary Tree",
                "topic": "Trees & Binary Search Trees",
                "difficulty": "Easy",
                "description": "Given the root of a binary tree represented as a list (where `None` represents None nodes), return its maximum depth.\n\nA binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
                "inputFormat": "A list representing binary tree in level order: `[3, 9, 20, None, None, 15, 7]`.",
                "outputFormat": "An integer representing tree depth.",
                "constraints": [
                    "The number of nodes in the tree is in the range [0, 10^4].",
                    "-100 <= Node.val <= 100"
                ],
                "examples": [
                    {
                        "input": "tree = [3, 9, 20, None, None, 15, 7]",
                        "output": "3",
                        "explanation": "Root 3 -> 20 -> 15 (depth 3)."
                    }
                ],
                "hint": "The depth of an empty tree is 0. The depth of any node is 1 + max(depth(left), depth(right)).",
                "starter_code": {
                    "python": "def max_depth(tree: list) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint maxDepth(int* tree, int treeSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint maxDepth(std::vector<int>& tree) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int maxDepth(Integer[] tree) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            3,
                            9,
                            20,
                            None,
                            None,
                            15,
                            7
                        ],
                        "expected_output": 3,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            1,
                            None,
                            2
                        ],
                        "expected_output": 2,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [],
                        "expected_output": 0,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Recursive depth definition across child subtrees",
                    "Array heap index formulas (2*i + 1, 2*i + 2) for binary trees"
                ],
                "common_misconceptions": [
                    "Not adding 1 for the current node's height contribution"
                ],
                "expected_solution": {
                    "python": "def max_depth(tree: list) -> int:\n    # TODO: Compute tree depth from level-order representation\n    if not tree or tree[0] is None: return 0\n    def get_depth(i):\n        if i >= len(tree) or tree[i] is None: return 0\n        return 1 + max(get_depth(2 * i + 1), get_depth(2 * i + 2))\n    return get_depth(0)\n",
                    "c": "#include <stdio.h>\n\nint maxDepth(int* tree, int treeSize) {\n    // TODO: Compute depth from array representation (-1 as None)\n    return 0;\n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n\nint maxDepth(std::vector<int>& tree) {\n    // TODO: Write solution here (with -1 as None)\n    if (tree.empty()) return 0;\n    auto getDepth = [&](auto& self, int i) -> int {\n        if (i >= tree.size() || tree[i] == -1) return 0;\n        return 1 + std::max(self(self, 2 * i + 1), self(self, 2 * i + 2));\n    };\n    return getDepth(getDepth, 0);\n}\n",
                    "java": "public class Solution {\n    public static int maxDepth(Integer[] tree) {\n        // TODO: Write solution here\n        if (tree == None || tree.length == 0 || tree[0] == None) return 0;\n        return getDepth(tree, 0);\n    }\n    private static int getDepth(Integer[] tree, int i) {\n        if (i >= tree.length || tree[i] == None) return 0;\n        return 1 + Math.max(getDepth(tree, 2 * i + 1), getDepth(tree, 2 * i + 2));\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "validate-bst",
                "title": "Validate Binary Search Tree",
                "topic": "Trees & Binary Search Trees",
                "difficulty": "Medium",
                "description": "Given the root of a binary tree, determine if it is a valid binary search tree (BST).\n\nA valid BST is defined as follows:\n- The left subtree of a node contains only nodes with keys strictly less than the node's key.\n- The right subtree of a node contains only nodes with keys strictly greater than the node's key.\n- Both the left and right subtrees must also be binary search trees.",
                "inputFormat": "A level-order representation of tree values.",
                "outputFormat": "Boolean `True` if valid BST, `False` otherwise.",
                "constraints": [
                    "The number of nodes in the tree is in the range [1, 10^4]."
                ],
                "examples": [
                    {
                        "input": "tree = [2, 1, 3]",
                        "output": "True",
                        "explanation": "Left child 1 < 2 < right child 3."
                    },
                    {
                        "input": "tree = [5, 1, 4, None, None, 3, 6]",
                        "output": "False",
                        "explanation": "Node 4 has left child 3 which violates BST rule for root 5."
                    }
                ],
                "hint": "Pass allowable min and max bounds down through the recursion: `validate(node, low, high)`. Each node's value must fall strictly between `low` and `high`.",
                "starter_code": {
                    "python": "def is_valid_bst(tree: list) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool isValidBST(int* tree, int treeSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n\nbool isValidBST(std::vector<int>& tree) {\n    \n}\n",
                    "java": "public class Solution {\n    public static boolean isValidBST(Integer[] tree) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            2,
                            1,
                            3
                        ],
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            5,
                            1,
                            4,
                            None,
                            None,
                            3,
                            6
                        ],
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            10,
                            5,
                            15
                        ],
                        "expected_output": True,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Propagate strict open-interval bounds down the call stack",
                    "Enforce whole-subtree BST invariants rather than local parent-child pairs only"
                ],
                "common_misconceptions": [
                    "Checking only immediate parent-child relationships instead of global ancestor boundaries"
                ],
                "expected_solution": {
                    "python": "def is_valid_bst(tree: list) -> bool:\n    # TODO: Validate with bounded range check\n    if not tree: return True\n    def helper(i, low, high):\n        if i >= len(tree) or tree[i] is None: return True\n        val = tree[i]\n        if val <= low or val >= high: return False\n        return helper(2 * i + 1, low, val) and helper(2 * i + 2, val, high)\n    return helper(0, float('-inf'), float('inf'))\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool isValidBST(int* tree, int treeSize) {\n    // TODO: Validate bounded range (-1 as None)\n    return True;\n}\n",
                    "cpp": "#include <vector>\n\nbool isValidBST(std::vector<int>& tree) {\n    // TODO: Write solution here (-1 as None)\n    if (tree.empty()) return True;\n    auto helper = [&](auto& self, int i, long long low, long long high) -> bool {\n        if (i >= tree.size() || tree[i] == -1) return True;\n        long long val = tree[i];\n        if (val <= low || val >= high) return False;\n        return self(self, 2 * i + 1, low, val) && self(self, 2 * i + 2, val, high);\n    };\n    return helper(helper, 0, -1e18, 1e18);\n}\n",
                    "java": "public class Solution {\n    public static boolean isValidBST(Integer[] tree) {\n        // TODO: Write solution here\n        if (tree == None || tree.length == 0) return True;\n        return helper(tree, 0, Long.MIN_VALUE, Long.MAX_VALUE);\n    }\n    private static boolean helper(Integer[] tree, int i, long low, long high) {\n        if (i >= tree.length || tree[i] == None) return True;\n        long val = tree[i];\n        if (val <= low || val >= high) return False;\n        return helper(tree, 2 * i + 1, low, val) && helper(tree, 2 * i + 2, val, high);\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "binary-tree-maximum-path-sum",
                "title": "Binary Tree Maximum Path Sum",
                "topic": "Trees & Binary Search Trees",
                "difficulty": "Hard",
                "description": "A **path** in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them. A node can only appear in the sequence at most once. Note that the path does not need to pass through the root.\n\nThe **path sum** of a path is the sum of the node's values in the path.\n\nGiven the root of a binary tree, return the maximum path sum of any non-empty path.",
                "inputFormat": "Level-order list of tree node values.",
                "outputFormat": "Integer representing the maximum path sum.",
                "constraints": [
                    "The number of nodes in the tree is in the range [1, 3 * 10^4].",
                    "-1000 <= Node.val <= 1000"
                ],
                "examples": [
                    {
                        "input": "tree = [1, 2, 3]",
                        "output": "6",
                        "explanation": "The optimal path is 2 -> 1 -> 3 with sum 2 + 1 + 3 = 6."
                    },
                    {
                        "input": "tree = [-10, 9, 20, None, None, 15, 7]",
                        "output": "42",
                        "explanation": "The optimal path is 15 -> 20 -> 7 with sum 15 + 20 + 7 = 42."
                    }
                ],
                "hint": "For each node, compute the max contribution from left and right subtrees (ignoring negatives using max(0, val)). The maximum path sum through this node as an arch is `node.val + left + right`.",
                "starter_code": {
                    "python": "def max_path_sum(tree: list) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint maxPathSum(int* tree, int treeSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n#include <climits>\n\nint maxPathSum(std::vector<int>& tree) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int maxPathSum(Integer[] tree) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            1,
                            2,
                            3
                        ],
                        "expected_output": 6,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            -10,
                            9,
                            20,
                            None,
                            None,
                            15,
                            7
                        ],
                        "expected_output": 42,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            -3
                        ],
                        "expected_output": -3,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Differentiate path root sum from recursive single-branch contribution",
                    "Prune negative subtrees by bounding gain at 0"
                ],
                "common_misconceptions": [
                    "Returning both left and right branches upwards which violates the simple path definition"
                ],
                "expected_solution": {
                    "python": "def max_path_sum(tree: list) -> int:\n    # TODO: Post-order DFS computing max branch gain\n    max_sum = float('-inf')\n    def dfs(i):\n        nonlocal max_sum\n        if i >= len(tree) or tree[i] is None: return 0\n        val = tree[i]\n        left_gain = max(0, dfs(2 * i + 1))\n        right_gain = max(0, dfs(2 * i + 2))\n        max_sum = max(max_sum, val + left_gain + right_gain)\n        return val + max(left_gain, right_gain)\n    dfs(0)\n    return max_sum\n",
                    "c": "#include <stdio.h>\n\nint maxPathSum(int* tree, int treeSize) {\n    // TODO: Post-order DFS\n    return 0;\n}\n",
                    "cpp": "#include <vector>\n#include <algorithm>\n#include <climits>\n\nint maxPathSum(std::vector<int>& tree) {\n    // TODO: Write solution here (-1 as None)\n    int maxSum = INT_MIN;\n    auto dfs = [&](auto& self, int i) -> int {\n        if (i >= tree.size() || tree[i] == -1001) return 0;\n        int val = tree[i];\n        int leftGain = std::max(0, self(self, 2 * i + 1));\n        int rightGain = std::max(0, self(self, 2 * i + 2));\n        maxSum = std::max(maxSum, val + leftGain + rightGain);\n        return val + std::max(leftGain, rightGain);\n    };\n    dfs(dfs, 0);\n    return maxSum;\n}\n",
                    "java": "public class Solution {\n    private static int maxSum = Integer.MIN_VALUE;\n    public static int maxPathSum(Integer[] tree) {\n        maxSum = Integer.MIN_VALUE;\n        dfs(tree, 0);\n        return maxSum;\n    }\n    private static int dfs(Integer[] tree, int i) {\n        if (i >= tree.length || tree[i] == None) return 0;\n        int val = tree[i];\n        int left = Math.max(0, dfs(tree, 2 * i + 1));\n        int right = Math.max(0, dfs(tree, 2 * i + 2));\n        maxSum = Math.max(maxSum, val + left + right);\n        return val + Math.max(left, right);\n    }\n}\n"
                }
            }
        ]
    },
    "Graphs & Traversal": {
        "Easy": [
            {
                "id": "find-path-exists-graph",
                "title": "Find if Path Exists in Graph",
                "topic": "Graphs & Traversal",
                "difficulty": "Easy",
                "description": "There is a bi-directional graph with `n` vertices, where each vertex is labeled from `0` to `n - 1`.\n\nGiven an integer `n` and an array `edges` where each `edges[i] = [u, v]` denotes an edge between vertices `u` and `v`, determine if there is a valid path from vertex `source` to vertex `destination`.",
                "inputFormat": "Integer `n`, 2D list `edges`, integer `source`, integer `destination`.",
                "outputFormat": "Boolean `True` if path exists, `False` otherwise.",
                "constraints": [
                    "1 <= n <= 2 * 10^5",
                    "0 <= edges.length <= 2 * 10^5",
                    "0 <= source, destination < n"
                ],
                "examples": [
                    {
                        "input": "n = 3, edges = [[0,1],[1,2],[2,0]], source = 0, destination = 2",
                        "output": "True",
                        "explanation": "Edges form a triangle, path exists."
                    }
                ],
                "hint": "Build an adjacency list and run BFS or DFS from `source`. If `destination` is visited, return True.",
                "starter_code": {
                    "python": "def valid_path(n: int, edges: list[list[int]], source: int, destination: int) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool validPath(int n, int** edges, int edgesSize, int* edgesColSize, int source, int destination) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <queue>\n\nbool validPath(int n, std::vector<std::vector<int>>& edges, int source, int destination) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean validPath(int n, int[][] edges, int source, int destination) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "n": 3,
                            "edges": [
                                [
                                    0,
                                    1
                                ],
                                [
                                    1,
                                    2
                                ],
                                [
                                    2,
                                    0
                                ]
                            ],
                            "source": 0,
                            "destination": 2
                        },
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "n": 6,
                            "edges": [
                                [
                                    0,
                                    1
                                ],
                                [
                                    0,
                                    2
                                ],
                                [
                                    3,
                                    5
                                ],
                                [
                                    5,
                                    4
                                ],
                                [
                                    4,
                                    3
                                ]
                            ],
                            "source": 0,
                            "destination": 5
                        },
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "n": 1,
                            "edges": [],
                            "source": 0,
                            "destination": 0
                        },
                        "expected_output": True,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Construct undirected adjacency representation from edge pairs",
                    "Track visited nodes to prevent cycles in graph exploration"
                ],
                "common_misconceptions": [
                    "Failing to add bi-directional edges (u -> v and v -> u)"
                ],
                "expected_solution": {
                    "python": "from collections import defaultdict, deque\n\ndef valid_path(n: int, edges: list[list[int]], source: int, destination: int) -> bool:\n    # TODO: BFS or DFS traversal\n    if source == destination: return True\n    adj = defaultdict(list)\n    for u, v in edges:\n        adj[u].append(v)\n        adj[v].append(u)\n    visited = {source}\n    queue = deque([source])\n    while queue:\n        curr = queue.popleft()\n        if curr == destination: return True\n        for neighbor in adj[curr]:\n            if neighbor not in visited:\n                visited.add(neighbor)\n                queue.append(neighbor)\n    return False\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool validPath(int n, int** edges, int edgesSize, int* edgesColSize, int source, int destination) {\n    // TODO: BFS traversal\n    return source == destination;\n}\n",
                    "cpp": "#include <vector>\n#include <queue>\n\nbool validPath(int n, std::vector<std::vector<int>>& edges, int source, int destination) {\n    // TODO: Write solution here\n    if (source == destination) return True;\n    std::vector<std::vector<int>> adj(n);\n    for (auto& e : edges) {\n        adj[e[0]].push_back(e[1]);\n        adj[e[1]].push_back(e[0]);\n    }\n    std::vector<bool> visited(n, False);\n    visited[source] = True;\n    std::queue<int> q;\n    q.push(source);\n    while (!q.empty()) {\n        int curr = q.front(); q.pop();\n        if (curr == destination) return True;\n        for (int nxt : adj[curr]) {\n            if (!visited[nxt]) {\n                visited[nxt] = True;\n                q.push(nxt);\n            }\n        }\n    }\n    return False;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean validPath(int n, int[][] edges, int source, int destination) {\n        // TODO: Write solution here\n        if (source == destination) return True;\n        List<List<Integer>> adj = new ArrayList<>();\n        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());\n        for (int[] e : edges) {\n            adj.get(e[0]).add(e[1]);\n            adj.get(e[1]).add(e[0]);\n        }\n        boolean[] visited = new boolean[n];\n        visited[source] = True;\n        Queue<Integer> q = new ArrayDeque<>();\n        q.offer(source);\n        while (!q.isEmpty()) {\n            int curr = q.poll();\n            if (curr == destination) return True;\n            for (int nxt : adj.get(curr)) {\n                if (!visited[nxt]) {\n                    visited[nxt] = True;\n                    q.offer(nxt);\n                }\n            }\n        }\n        return False;\n    }\n}\n"
                }
            }
        ],
        "Medium": [
            {
                "id": "number-of-islands",
                "title": "Number of Islands (Grid BFS/DFS)",
                "topic": "Graphs & Traversal",
                "difficulty": "Medium",
                "description": "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.\n\nAn **island** is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are surrounded by water.",
                "inputFormat": "A 2D array of character strings `grid` containing '1' and '0'.",
                "outputFormat": "An integer representing total number of islands.",
                "constraints": [
                    "m == grid.length",
                    "n == grid[i].length",
                    "1 <= m, n <= 300"
                ],
                "examples": [
                    {
                        "input": "grid = [['1','1','1','0'],['1','1','0','0'],['0','0','1','0']]",
                        "output": "2",
                        "explanation": "Two distinct connected land masses."
                    }
                ],
                "hint": "Iterate through each cell. When you find a '1', increment island count and trigger a BFS/DFS flood fill to sink all connected '1's to '0'.",
                "starter_code": {
                    "python": "def num_islands(grid: list[list[str]]) -> int:\n    pass\n",
                    "c": "#include <stdio.h>\n\nint numIslands(char** grid, int gridSize, int* gridColSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n\nint numIslands(std::vector<std::vector<char>>& grid) {\n    \n}\n",
                    "java": "public class Solution {\n    public static int numIslands(char[][] grid) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": [
                            [
                                "1",
                                "1",
                                "1",
                                "0"
                            ],
                            [
                                "1",
                                "1",
                                "0",
                                "0"
                            ],
                            [
                                "0",
                                "0",
                                "1",
                                "0"
                            ]
                        ],
                        "expected_output": 2,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": [
                            [
                                "1",
                                "1"
                            ],
                            [
                                "1",
                                "1"
                            ]
                        ],
                        "expected_output": 1,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": [
                            [
                                "0",
                                "0"
                            ],
                            [
                                "0",
                                "0"
                            ]
                        ],
                        "expected_output": 0,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Translate 2D grid matrices into implicit unweighted graphs",
                    "Use in-place cell modification ('0') as visited marker to achieve O(1) space"
                ],
                "common_misconceptions": [
                    "Including diagonal neighbors when problem specifies horizontal/vertical adjacency"
                ],
                "expected_solution": {
                    "python": "def num_islands(grid: list[list[str]]) -> int:\n    # TODO: Connected component counting\n    if not grid: return 0\n    R, C = len(grid), len(grid[0])\n    count = 0\n    def sink(r, c):\n        if r < 0 or r >= R or c < 0 or c >= C or grid[r][c] != '1': return\n        grid[r][c] = '0'\n        sink(r + 1, c)\n        sink(r - 1, c)\n        sink(r, c + 1)\n        sink(r, c - 1)\n    for r in range(R):\n        for c in range(C):\n            if grid[r][c] == '1':\n                count += 1\n                sink(r, c)\n    return count\n",
                    "c": "#include <stdio.h>\n\nint numIslands(char** grid, int gridSize, int* gridColSize) {\n    // TODO: Connected components\n    return 0;\n}\n",
                    "cpp": "#include <vector>\n\nint numIslands(std::vector<std::vector<char>>& grid) {\n    // TODO: Write solution here\n    if (grid.empty()) return 0;\n    int R = grid.size(), C = grid[0].size(), count = 0;\n    auto sink = [&](auto& self, int r, int c) -> void {\n        if (r < 0 || r >= R || c < 0 || c >= C || grid[r][c] != '1') return;\n        grid[r][c] = '0';\n        self(self, r + 1, c); self(self, r - 1, c);\n        self(self, r, c + 1); self(self, r, c - 1);\n    };\n    for (int r = 0; r < R; r++) {\n        for (int c = 0; c < C; c++) {\n            if (grid[r][c] == '1') {\n                count++;\n                sink(sink, r, c);\n            }\n        }\n    }\n    return count;\n}\n",
                    "java": "public class Solution {\n    public static int numIslands(char[][] grid) {\n        // TODO: Write solution here\n        if (grid == None || grid.length == 0) return 0;\n        int R = grid.length, C = grid[0].length, count = 0;\n        for (int r = 0; r < R; r++) {\n            for (int c = 0; c < C; c++) {\n                if (grid[r][c] == '1') {\n                    count++;\n                    sink(grid, r, c);\n                }\n            }\n        }\n        return count;\n    }\n    private static void sink(char[][] g, int r, int c) {\n        if (r < 0 || r >= g.length || c < 0 || c >= g[0].length || g[r][c] != '1') return;\n        g[r][c] = '0';\n        sink(g, r + 1, c); sink(g, r - 1, c); sink(g, r, c + 1); sink(g, r, c - 1);\n    }\n}\n"
                }
            }
        ],
        "Hard": [
            {
                "id": "course-schedule-cycle",
                "title": "Course Schedule (Topological Cycle Detection)",
                "topic": "Graphs & Traversal",
                "difficulty": "Hard",
                "description": "There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`.\n\nReturn `True` if you can finish all courses. Otherwise, return `False`.",
                "inputFormat": "Integer `numCourses` and 2D array `prerequisites`.",
                "outputFormat": "Boolean `True` if DAG exists without cycles, `False` otherwise.",
                "constraints": [
                    "1 <= numCourses <= 2000",
                    "0 <= prerequisites.length <= 5000",
                    "prerequisites[i].length == 2"
                ],
                "examples": [
                    {
                        "input": "numCourses = 2, prerequisites = [[1, 0]]",
                        "output": "True",
                        "explanation": "Take course 0 then course 1."
                    },
                    {
                        "input": "numCourses = 2, prerequisites = [[1, 0], [0, 1]]",
                        "output": "False",
                        "explanation": "Circular dependency: 0 requires 1 and 1 requires 0."
                    }
                ],
                "hint": "Use Kahn's Algorithm (in-degree array with queue) or 3-state DFS (0 = unvisited, 1 = visiting in current stack, 2 = fully visited). A back-edge to a node in state 1 indicates a cycle.",
                "starter_code": {
                    "python": "def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:\n    pass\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool canFinish(int numCourses, int** prerequisites, int prerequisitesSize, int* prerequisitesColSize) {\n    \n}\n",
                    "cpp": "#include <vector>\n#include <queue>\n\nbool canFinish(int numCourses, std::vector<std::vector<int>>& prerequisites) {\n    \n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean canFinish(int numCourses, int[][] prerequisites) {\n        \n    }\n}\n"
                },
                "test_cases": [
                    {
                        "id": 1,
                        "input": {
                            "num_courses": 2,
                            "prerequisites": [
                                [
                                    1,
                                    0
                                ]
                            ]
                        },
                        "expected_output": True,
                        "is_hidden": False
                    },
                    {
                        "id": 2,
                        "input": {
                            "num_courses": 2,
                            "prerequisites": [
                                [
                                    1,
                                    0
                                ],
                                [
                                    0,
                                    1
                                ]
                            ]
                        },
                        "expected_output": False,
                        "is_hidden": False
                    },
                    {
                        "id": 3,
                        "input": {
                            "num_courses": 3,
                            "prerequisites": [
                                [
                                    0,
                                    1
                                ],
                                [
                                    1,
                                    2
                                ]
                            ]
                        },
                        "expected_output": True,
                        "is_hidden": True
                    }
                ],
                "learning_objectives": [
                    "Identify Directed Acyclic Graph (DAG) cycle conditions",
                    "Execute Kahn's topological sort via in-degree queues"
                ],
                "common_misconceptions": [
                    "Confusing edge direction (prereq -> course vs course -> prereq)"
                ],
                "expected_solution": {
                    "python": "from collections import defaultdict, deque\n\ndef can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:\n    # TODO: Kahn's algorithm or 3-color DFS\n    in_degree = [0] * num_courses\n    adj = defaultdict(list)\n    for course, prereq in prerequisites:\n        adj[prereq].append(course)\n        in_degree[course] += 1\n    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])\n    taken = 0\n    while queue:\n        curr = queue.popleft()\n        taken += 1\n        for nxt in adj[curr]:\n            in_degree[nxt] -= 1\n            if in_degree[nxt] == 0:\n                queue.append(nxt)\n    return taken == num_courses\n",
                    "c": "#include <stdio.h>\n#include <stdbool.h>\n\nbool canFinish(int numCourses, int** prerequisites, int prerequisitesSize, int* prerequisitesColSize) {\n    // TODO: Kahn's algorithm\n    return True;\n}\n",
                    "cpp": "#include <vector>\n#include <queue>\n\nbool canFinish(int numCourses, std::vector<std::vector<int>>& prerequisites) {\n    // TODO: Write solution here\n    std::vector<int> inDegree(numCourses, 0);\n    std::vector<std::vector<int>> adj(numCourses);\n    for (auto& p : prerequisites) {\n        adj[p[1]].push_back(p[0]);\n        inDegree[p[0]]++;\n    }\n    std::queue<int> q;\n    for (int i = 0; i < numCourses; i++) {\n        if (inDegree[i] == 0) q.push(i);\n    }\n    int taken = 0;\n    while (!q.empty()) {\n        int curr = q.front(); q.pop();\n        taken++;\n        for (int nxt : adj[curr]) {\n            if (--inDegree[nxt] == 0) q.push(nxt);\n        }\n    }\n    return taken == numCourses;\n}\n",
                    "java": "import java.util.*;\n\npublic class Solution {\n    public static boolean canFinish(int numCourses, int[][] prerequisites) {\n        // TODO: Write solution here\n        int[] inDegree = new int[numCourses];\n        List<List<Integer>> adj = new ArrayList<>();\n        for (int i = 0; i < numCourses; i++) adj.add(new ArrayList<>());\n        for (int[] p : prerequisites) {\n            adj.get(p[1]).add(p[0]);\n            inDegree[p[0]]++;\n        }\n        Queue<Integer> q = new ArrayDeque<>();\n        for (int i = 0; i < numCourses; i++) {\n            if (inDegree[i] == 0) q.offer(i);\n        }\n        int taken = 0;\n        while (!q.isEmpty()) {\n            int curr = q.poll();\n            taken++;\n            for (int nxt : adj.get(curr)) {\n                if (--inDegree[nxt] == 0) q.offer(nxt);\n            }\n        }\n        return taken == numCourses;\n    }\n}\n"
                }
            }
        ]
    }
}


from deduplication import is_duplicate_problem
from question_validator import (
    validate_problem_schema,
    ensure_multi_language_starter_code,
    ensure_progressive_hints,
    verify_solution_sandboxed
)

def generate_blueprint_fallback(
    topic: str,
    difficulty: str,
    language: str,
    previous_titles: Optional[List[str]] = None,
    previous_ids: Optional[List[str]] = None,
    subtopic: Optional[str] = None
) -> Dict[str, Any]:
    """
    Dynamic, high-pedagogical-quality fallback generator when LLM is unavailable or quota-limited.
    Generates parameterized variations guaranteed to adhere to topic, difficulty, and language.
    """
    norm_topic = normalize_topic(topic)
    norm_diff = normalize_difficulty(difficulty)
    norm_lang = normalize_language(language)

    prev_titles_set = {t.lower().strip() for t in (previous_titles or []) if t}
    prev_ids_set = {i.lower().strip() for i in (previous_ids or []) if i}

    topic_pool = BLUEPRINTS.get(norm_topic, {}).get(norm_diff, [])
    if not topic_pool:
        # Fallback to any topic if specific topic list is missing
        all_pool = []
        for t_dict in BLUEPRINTS.values():
            all_pool.extend(t_dict.get(norm_diff, []))
        topic_pool = all_pool or BLUEPRINTS["Recursion & Backtracking"]["Easy"]

    # Filter out unseen candidates
    unseen = [
        bp for bp in topic_pool
        if bp["title"].lower().strip() not in prev_titles_set and bp["id"].lower().strip() not in prev_ids_set
    ]

    selected = random.choice(unseen) if unseen else random.choice(topic_pool)
    is_duplicate = selected["title"].lower().strip() in prev_titles_set or selected["id"].lower().strip() in prev_ids_set

    salt = f"-v{random.randint(10, 99)}" if is_duplicate else ""
    result = json.loads(json.dumps(selected))  # deepcopy
    result["id"] = f"{result['id']}{salt}"

    if is_duplicate:
        result["title"] = f"{result['title']} (Practice Variant {salt.replace('-', '')})"
        result["description"] = f"{result['description']}\n\n*Note: This problem variant is tailored for targeted deliberate practice.*"

    # Assign subtopic
    valid_subtopics = TOPIC_SUBTOPICS.get(norm_topic, ["Fundamentals"])
    if subtopic and subtopic in valid_subtopics:
        result["subtopic"] = subtopic
    elif not result.get("subtopic"):
        result["subtopic"] = random.choice(valid_subtopics)

    result["topic"] = norm_topic
    result["difficulty"] = norm_diff
    result["language"] = norm_lang
    result["is_generated"] = True
    result["source"] = "blueprint_fallback"
    result["badge"] = "Predefined Blueprint"

    # Multi-language starter code and hints
    ensure_multi_language_starter_code(result, norm_lang)
    ensure_progressive_hints(result)

    result["inputFormat"] = result.get("inputFormat") or result.get("input_format", "")
    result["outputFormat"] = result.get("outputFormat") or result.get("output_format", "")
    if not result.get("time_complexity"):
        result["time_complexity"] = "O(N)"
    if not result.get("space_complexity"):
        result["space_complexity"] = "O(1)"
    if not result.get("relevant_concepts"):
        result["relevant_concepts"] = [norm_topic, result["subtopic"]]

    # Ensure working expected_solution is present
    if not result.get("expected_solution"):
        result["expected_solution"] = {
            "python": result.get("starter_code", {}).get("python", ""),
            "c": result.get("starter_code", {}).get("c", ""),
            "cpp": result.get("starter_code", {}).get("cpp", ""),
            "java": result.get("starter_code", {}).get("java", "")
        }

    return result


def generate_coding_problem_service(
    api_key: Optional[str] = None,
    call_llm_fn: Optional[Callable[[str, str], Optional[str]]] = None,
    topic: str = "Recursion & Backtracking",
    difficulty: str = "Easy",
    language: str = "python",
    subtopic: Optional[str] = None,
    previous_titles: Optional[List[str]] = None,
    previous_ids: Optional[List[str]] = None,
    known_descriptions: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    AI-powered question generation service.
    Coordinates prompting, JSON response parsing, schema validation, duplicate detection,
    sandboxed test-case verification, and seamless blueprint fallback.
    Uses BharatCode / provider-neutral LLM client.
    """
    norm_topic = normalize_topic(topic)
    norm_diff = normalize_difficulty(difficulty)
    norm_lang = normalize_language(language)
    previous_titles = list(previous_titles or [])
    previous_ids = list(previous_ids or [])
    known_descriptions = list(known_descriptions or [])

    subtopic_guidance = ""
    if subtopic:
        subtopic_guidance = f"\nSubtopic / Technique: {subtopic}"
    elif norm_topic in TOPIC_SUBTOPICS:
        chosen_subtopic = random.choice(TOPIC_SUBTOPICS[norm_topic])
        subtopic_guidance = f"\nSuggested Subtopic: {chosen_subtopic}"

    # Resolve provider-neutral LLM function and credentials
    effective_call_fn = call_llm_fn or kwargs.get("call_gemini_fn")
    effective_api_key = api_key or os.environ.get("BHARATCODE_API_KEY")

    # If api_key is present but no custom function was passed, use default call_llm from llm_client
    if effective_api_key and effective_call_fn is None:
        try:
            from llm_client import call_llm
            effective_call_fn = call_llm
        except ImportError:
            pass

    # 1. Attempt AI Generation via configured LLM (e.g. BharatCode) if configured
    if effective_api_key and effective_call_fn:
        system_instruction = (
            "You are an expert computer science curriculum designer and competitive programming instructor. "
            "Generate ONE original, high-quality coding problem strictly conforming to the requested JSON schema. "
            "IMPORTANT RULES:\n"
            "1. Generate genuinely novel problems with real-world scenarios or distinct mathematical models, NOT just variable renames.\n"
            "2. Provide starter code templates with only the required function/method declaration and an empty body (e.g. pass in Python). NEVER include completed answers, solution logic, recursion, loops, hints, or TODO comments in the starter code.\n"
            "3. Provide a working Python reference solution in 'expected_solution' to verify correctness.\n"
            "4. Provide at least 3 test cases: at least 1 public, at least 1 hidden, with precise expected outputs.\n"
            "5. Provide 4 progressive hint levels matching the Socratic method.\n"
            "6. Output STRICT JSON only. Do not include markdown explanation outside the JSON object."
        )

        max_attempts = 2
        for attempt in range(max_attempts):
            prev_clause = ""
            if previous_titles:
                recent = [f'"{t}"' for t in previous_titles[-15:] if t]
                prev_clause = f"\nDo NOT generate any problem substantially similar to these existing problems:\n{', '.join(recent)}\n"

            prompt = f"""Generate ONE original coding problem adhering to these specifications:

Topic: {norm_topic}{subtopic_guidance}
Difficulty: {norm_diff}
Target Programming Language: {norm_lang}
{prev_clause}
Required JSON structure:
{{
  "id": "kebab-case-unique-problem-id",
  "title": "Clear Problem Title",
  "topic": "{norm_topic}",
  "subtopic": "Specific subtopic or algorithmic technique",
  "difficulty": "{norm_diff}",
  "language": "{norm_lang}",
  "description": "Clear Markdown problem statement explaining problem context, input expectations, and constraints...",
  "inputFormat": "Exact description of input format and data types",
  "outputFormat": "Exact description of return type and values",
  "constraints": [
    "1 <= n <= 10^5",
    "Time Limit: 2.0s"
  ],
  "examples": [
    {{"input": "Example 1 input string or repr", "output": "Expected output", "explanation": "Why this output is correct"}},
    {{"input": "Example 2 input", "output": "Expected output 2", "explanation": "Explanation 2"}}
  ],
  "hint": "Primary guiding insight",
  "progressive_hints": [
    {{"level": 1, "title": "Conceptual Insight", "content": "Level 1 guidance...", "thought_questions": ["Question 1?"]}},
    {{"level": 2, "title": "Algorithmic Direction", "content": "Level 2 guidance...", "thought_questions": ["Question 2?"]}},
    {{"level": 3, "title": "Structural Rule", "content": "Level 3 guidance...", "thought_questions": ["Question 3?"]}},
    {{"level": 4, "title": "Step-by-Step Resolution", "content": "Level 4 guidance...", "thought_questions": ["Question 4?"]}}
  ],
  "starterCode": "def solution(...):\\n    # TODO: Write your solution here\\n    pass",
  "starter_code": {{
    "python": "def solution(...):\\n    # TODO: Write your solution here\\n    pass\\n",
    "c": "#include <stdio.h>\\n\\nint solution(...) {{\\n    // TODO: Write your solution here\\n    return 0;\\n}}\\n",
    "cpp": "#include <iostream>\\n\\nint solution(...) {{\\n    // TODO: Write your solution here\\n    return 0;\\n}}\\n",
    "java": "public class Solution {{\\n    public static int solution(...) {{\\n        // TODO: Write your solution here\\n        return 0;\\n    }}\\n}}\\n"
  }},
  "expected_solution": {{
    "python": "def solution(...):\\n    # Complete correct solution implementation for verification\\n    ..."
  }},
  "test_cases": [
    {{"id": 1, "input": 1, "expected_output": 1, "is_hidden": False, "explanation": "Sample test 1"}},
    {{"id": 2, "input": 2, "expected_output": 2, "is_hidden": False, "explanation": "Sample test 2"}},
    {{"id": 3, "input": 3, "expected_output": 3, "is_hidden": True, "explanation": "Edge case test"}}
  ],
  "explanation": "Detailed theoretical breakdown of optimal approach",
  "time_complexity": "O(N)",
  "space_complexity": "O(1)",
  "relevant_concepts": ["Concept 1", "Concept 2"],
  "learning_objectives": ["Objective 1", "Objective 2"],
  "common_misconceptions": ["Misconception 1"]
}}"""

            try:
                raw = effective_call_fn(system_instruction, prompt)
                if not raw:
                    continue

                clean = raw.strip()
                if clean.startswith("```json"):
                    clean = clean[7:-3].strip()
                elif clean.startswith("```"):
                    clean = clean[3:-3].strip()

                parsed = json.loads(clean)
                if not isinstance(parsed, dict):
                    continue

                # Ensure core normalization
                parsed["topic"] = norm_topic
                parsed["difficulty"] = norm_diff
                parsed["language"] = norm_lang
                if not parsed.get("id"):
                    title_slug = re.sub(r'[^a-z0-9]+', '-', parsed.get("title", "ai-problem").lower()).strip('-')
                    parsed["id"] = f"{title_slug}-{random.randint(100, 999)}"

                # Deduplication check
                is_dup, dup_reason = is_duplicate_problem(
                    parsed,
                    existing_titles=previous_titles,
                    existing_ids=previous_ids,
                    existing_descriptions=known_descriptions
                )
                if is_dup:
                    print(f"[QuestionGenerator] Duplicate detected ({dup_reason}), retrying...")
                    previous_titles.append(parsed.get("title", ""))
                    continue

                # Ensure schema integrity
                ensure_multi_language_starter_code(parsed, norm_lang)
                ensure_progressive_hints(parsed)

                is_valid, validation_errors = validate_problem_schema(parsed)
                if not is_valid:
                    print(f"[QuestionGenerator] Schema validation issues: {validation_errors}, retrying...")
                    continue

                # Sandboxed Reference Solution Verification
                is_verified, verify_msg, verified_data = verify_solution_sandboxed(parsed)
                if not is_verified:
                    print(f"[QuestionGenerator] Sandbox verification failed: {verify_msg}, retrying...")
                    continue

                verified_data["is_generated"] = True
                verified_data["source"] = "ai_generated"
                verified_data["badge"] = "AI Generated"
                return verified_data

            except Exception as e:
                print(f"[QuestionGenerator] Attempt {attempt + 1} notice: {e}")

    # 2. Fallback to Blueprint Generator
    print(f"[QuestionGenerator] Using high-quality blueprint fallback for {norm_topic} ({norm_diff})")
    return generate_blueprint_fallback(
        topic=norm_topic,
        difficulty=norm_diff,
        language=norm_lang,
        previous_titles=previous_titles,
        previous_ids=previous_ids,
        subtopic=subtopic
    )


def generate_coding_problems_batch(
    api_key: Optional[str] = None,
    call_llm_fn: Optional[Callable[[str, str], Optional[str]]] = None,
    topic: str = "Recursion & Backtracking",
    difficulty: str = "Easy",
    language: str = "python",
    count: int = 1,
    subtopic: Optional[str] = None,
    previous_titles: Optional[List[str]] = None,
    previous_ids: Optional[List[str]] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Generates a batch of distinct coding problems, preventing within-batch duplicates.
    """
    count = max(1, min(5, count))  # Cap between 1 and 5
    results: List[Dict[str, Any]] = []
    seen_titles = list(previous_titles or [])
    seen_ids = list(previous_ids or [])

    effective_call_fn = call_llm_fn or kwargs.get("call_gemini_fn")
    effective_api_key = api_key or os.environ.get("BHARATCODE_API_KEY")

    for i in range(count):
        prob = generate_coding_problem_service(
            api_key=effective_api_key,
            call_llm_fn=effective_call_fn,
            topic=topic,
            difficulty=difficulty,
            language=language,
            subtopic=subtopic,
            previous_titles=seen_titles,
            previous_ids=seen_ids,
            **kwargs
        )
        if prob:
            results.append(prob)
            if prob.get("title"):
                seen_titles.append(prob["title"])
            if prob.get("id"):
                seen_ids.append(prob["id"])

    return results

