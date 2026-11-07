from typing import Dict
from models import Problem, TestCase

EXPANDED_PROBLEMS_5: Dict[str, Problem] = {
    # =========================================================================
    # ALGORITHMS & TWO POINTERS (4 problems)
    # =========================================================================
    "minimum-size-subarray-sum": Problem(
        id="minimum-size-subarray-sum",
        title="Minimum Size Subarray Sum",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Sliding Window",
        description="Given an array of positive integers `nums` and a positive integer `target`, return the minimal length of a contiguous subarray of which the sum is greater than or equal to `target`. If there is no such subarray, return 0 instead.",
        examples=[
            {"input": "target = 7, nums = [2, 3, 1, 2, 4, 3]", "output": "2", "explanation": "The subarray [4, 3] has the minimal length under the problem constraint."},
            {"input": "target = 4, nums = [1, 4, 4]", "output": "1"},
            {"input": "target = 11, nums = [1, 1, 1, 1, 1, 1, 1, 1]", "output": "0"}
        ],
        constraints=["1 <= target <= 10^9", "1 <= nums.length <= 10^5", "1 <= nums[i] <= 10^4"],
        starter_code={
            "python": "def min_sub_array_len(target: int, nums: list) -> int:\n    pass\n",
            "c": "int minSubArrayLen(int target, int* nums, int numsSize) { return 0; }\n",
            "cpp": "int minSubArrayLen(int target, vector<int>& nums) { return 0; }\n",
            "java": "public class Solution { public static int minSubArrayLen(int target, int[] nums) { return 0; } }\n"
        },
        expected_solution={
            "python": """def min_sub_array_len(target: int, nums: list) -> int:
    l = 0
    cur_sum = 0
    res = float('inf')
    for r in range(len(nums)):
        cur_sum += nums[r]
        while cur_sum >= target:
            res = min(res, r - l + 1)
            cur_sum -= nums[l]
            l += 1
    return 0 if res == float('inf') else res
""",
            "c": "int minSubArrayLen(int target, int* nums, int numsSize) { return 0; }\n",
            "cpp": "int minSubArrayLen(int target, vector<int>& nums) { int l = 0, sum = 0, ans = 1e9; for(int r=0; r<nums.size(); r++){ sum += nums[r]; while(sum >= target){ ans = min(ans, r - l + 1); sum -= nums[l++]; } } return ans == 1e9 ? 0 : ans; }\n",
            "java": "public class Solution { public static int minSubArrayLen(int target, int[] nums) { int l = 0, sum = 0, ans = Integer.MAX_VALUE; for(int r=0; r<nums.length; r++){ sum += nums[r]; while(sum >= target){ ans = Math.min(ans, r - l + 1); sum -= nums[l++]; } } return ans == Integer.MAX_VALUE ? 0 : ans; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"target": 7, "nums": [2, 3, 1, 2, 4, 3]}, expected_output=2),
            TestCase(id=2, input={"target": 4, "nums": [1, 4, 4]}, expected_output=1),
            TestCase(id=3, input={"target": 11, "nums": [1, 1, 1, 1, 1, 1, 1, 1]}, expected_output=0)
        ],
        learning_objectives=["Dynamic sliding window expansion and contraction", "Achieving O(N) runtime over positive integers"],
        common_misconceptions=["Using fixed window size or binary search when two pointers suffices"],
        hint="Expand right until sum >= target, then shrink left to find minimal valid length."
    ),

    "4sum": Problem(
        id="4sum",
        title="4Sum (Unique Quadruplets)",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Two Pointers",
        description="Given an array `nums` of `n` integers and an integer `target`, return an array of all the unique quadruplets `[nums[a], nums[b], nums[c], nums[d]]` such that `a, b, c, d` are distinct and their sum is `target`.",
        examples=[
            {"input": "nums = [1, 0, -1, 0, -2, 2], target = 0", "output": "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"},
            {"input": "nums = [2, 2, 2, 2, 2], target = 8", "output": "[[2, 2, 2, 2]]"}
        ],
        constraints=["1 <= nums.length <= 200", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
        starter_code={
            "python": "def four_sum(nums: list, target: int) -> list:\n    pass\n",
            "c": "void fourSum() {}\n",
            "cpp": "vector<vector<int>> fourSum(vector<int>& nums, int target) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> fourSum(int[] nums, int target) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": """def four_sum(nums: list, target: int) -> list:
    nums.sort()
    res = []
    n = len(nums)
    for i in range(n - 3):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            l, r = j + 1, n - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s == target:
                    res.append([nums[i], nums[j], nums[l], nums[r]])
                    while l < r and nums[l] == nums[l + 1]:
                        l += 1
                    while l < r and nums[r] == nums[r - 1]:
                        r -= 1
                    l += 1
                    r -= 1
                elif s < target:
                    l += 1
                else:
                    r -= 1
    return res
""",
            "c": "void fourSum() {}\n",
            "cpp": "vector<vector<int>> fourSum(vector<int>& nums, int target) { return {}; }\n",
            "java": "public class Solution { public static List<List<Integer>> fourSum(int[] nums, int target) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [1, 0, -1, 0, -2, 2], "target": 0}, expected_output=[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]),
            TestCase(id=2, input={"nums": [2, 2, 2, 2, 2], "target": 8}, expected_output=[[2, 2, 2, 2]])
        ],
        learning_objectives=["Extending 2-pointer 3Sum pattern into 4Sum with nested loops and duplicate pruning"],
        common_misconceptions=["Integer overflow in languages like C/Java when summing 4 large numbers"],
        hint="Sort array, fix two outer pointers, and use two pointers for the remaining inner pair."
    ),

    "find-all-anagrams-in-a-string": Problem(
        id="find-all-anagrams-in-a-string",
        title="Find All Anagrams in a String",
        difficulty="Medium",
        topic="Algorithms & Two Pointers",
        subtopic="Sliding Window",
        description="Given two strings `s` and `p`, return an array of all the start indices of `p`'s anagrams in `s`.",
        examples=[
            {"input": "s = 'cbaebabacd', p = 'abc'", "output": "[0, 6]", "explanation": "The substring starting at index 0 is 'cba', which is an anagram of 'abc'. The substring with start index 6 is 'bac'."},
            {"input": "s = 'abab', p = 'ab'", "output": "[0, 1, 2]"}
        ],
        constraints=["1 <= s.length, p.length <= 3 * 10^4", "s and p consist of lowercase English letters."],
        starter_code={
            "python": "def find_anagrams(s: str, p: str) -> list:\n    pass\n",
            "c": "void findAnagrams() {}\n",
            "cpp": "vector<int> findAnagrams(string s, string p) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> findAnagrams(String s, String p) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": """def find_anagrams(s: str, p: str) -> list:
    if len(p) > len(s):
        return []
    p_count = {}
    s_count = {}
    for c in p:
        p_count[c] = p_count.get(c, 0) + 1
    k = len(p)
    for i in range(k):
        s_count[s[i]] = s_count.get(s[i], 0) + 1
    res = [0] if s_count == p_count else []
    for i in range(k, len(s)):
        s_count[s[i]] = s_count.get(s[i], 0) + 1
        old_char = s[i - k]
        s_count[old_char] -= 1
        if s_count[old_char] == 0:
            del s_count[old_char]
        if s_count == p_count:
            res.append(i - k + 1)
    return res
""",
            "c": "void findAnagrams() {}\n",
            "cpp": "vector<int> findAnagrams(string s, string p) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> findAnagrams(String s, String p) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"s": "cbaebabacd", "p": "abc"}, expected_output=[0, 6]),
            TestCase(id=2, input={"s": "abab", "p": "ab"}, expected_output=[0, 1, 2])
        ],
        learning_objectives=["Fixed-size sliding window frequency matching in O(26 * N)"],
        common_misconceptions=["Sorting each substring of length len(p) resulting in O(N * K log K) TLE"],
        hint="Slide a window of size len(p) across s, updating character frequencies."
    ),

    "sliding-window-maximum": Problem(
        id="sliding-window-maximum",
        title="Sliding Window Maximum",
        difficulty="Hard",
        topic="Algorithms & Two Pointers",
        subtopic="Sliding Window",
        description="You are given an array of integers `nums`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. Return the max sliding window.",
        examples=[
            {"input": "nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3", "output": "[3, 3, 5, 5, 6, 7]"},
            {"input": "nums = [1], k = 1", "output": "[1]"}
        ],
        constraints=["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4", "1 <= k <= nums.length"],
        starter_code={
            "python": "def max_sliding_window(nums: list, k: int) -> list:\n    pass\n",
            "c": "void maxSlidingWindow() {}\n",
            "cpp": "vector<int> maxSlidingWindow(vector<int>& nums, int k) { return {}; }\n",
            "java": "public class Solution { public static int[] maxSlidingWindow(int[] nums, int k) { return new int[0]; } }\n"
        },
        expected_solution={
            "python": """from collections import deque
def max_sliding_window(nums: list, k: int) -> list:
    q = deque()
    res = []
    for i, n in enumerate(nums):
        while q and nums[q[-1]] < n:
            q.pop()
        q.append(i)
        if q[0] <= i - k:
            q.popleft()
        if i >= k - 1:
            res.append(nums[q[0]])
    return res
""",
            "c": "void maxSlidingWindow() {}\n",
            "cpp": "vector<int> maxSlidingWindow(vector<int>& nums, int k) { return {}; }\n",
            "java": "public class Solution { public static int[] maxSlidingWindow(int[] nums, int k) { return new int[0]; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3}, expected_output=[3, 3, 5, 5, 6, 7]),
            TestCase(id=2, input={"nums": [1], "k": 1}, expected_output=[1])
        ],
        learning_objectives=["Monotonic decreasing deque to maintain window maximums in amortized O(N)"],
        common_misconceptions=["Using max-heap with lazy deletion which runs in O(N log K) instead of O(N)"],
        hint="Maintain a monotonic decreasing deque of indices."
    ),

    # =========================================================================
    # TREES & BINARY SEARCH TREES (4 problems)
    # =========================================================================
    "path-sum-iii": Problem(
        id="path-sum-iii",
        title="Path Sum III (Prefix Sum on Trees)",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="Binary Tree Traversal",
        description="Given the root of a binary tree and an integer `targetSum`, return the number of paths where the sum of the values along the path equals `targetSum`. The path does not need to start or end at the root or a leaf, but it must go downwards.",
        examples=[
            {"input": "root = [10, 5, -3, 3, 2, null, 11, 3, -2, null, 1], targetSum = 8", "output": "3", "explanation": "The 3 paths that sum to 8 are: 5 -> 3, 5 -> 2 -> 1, -3 -> 11."}
        ],
        constraints=["The number of nodes in the tree is in the range [0, 1000].", "-10^9 <= targetSum <= 10^9"],
        starter_code={
            "python": "def path_sum(root, targetSum: int) -> int:\n    pass\n",
            "c": "int pathSum() { return 0; }\n",
            "cpp": "int pathSum(TreeNode* root, int targetSum) { return 0; }\n",
            "java": "public class Solution { public static int pathSum(TreeNode root, int targetSum) { return 0; } }\n"
        },
        expected_solution={
            "python": """def path_sum(root, targetSum: int) -> int:
    from collections import defaultdict
    prefix = defaultdict(int)
    prefix[0] = 1
    count = 0
    def dfs(node, curr_sum):
        nonlocal count
        if not node:
            return
        curr_sum += node.val if hasattr(node, 'val') else (node['val'] if isinstance(node, dict) else node)
        count += prefix[curr_sum - targetSum]
        prefix[curr_sum] += 1
        left = getattr(node, 'left', None) or (node.get('left') if isinstance(node, dict) else None)
        right = getattr(node, 'right', None) or (node.get('right') if isinstance(node, dict) else None)
        dfs(left, curr_sum)
        dfs(right, curr_sum)
        prefix[curr_sum] -= 1
    dfs(root, 0)
    return count
""",
            "c": "int pathSum() { return 0; }\n",
            "cpp": "int pathSum(TreeNode* root, int targetSum) { return 0; }\n",
            "java": "public class Solution { public static int pathSum(TreeNode root, int targetSum) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"root": {"val": 10, "left": {"val": 5, "left": {"val": 3, "left": None, "right": None}, "right": {"val": 2, "left": None, "right": {"val": 1, "left": None, "right": None}}}, "right": {"val": -3, "left": None, "right": {"val": 11, "left": None, "right": None}}}, "targetSum": 8}, expected_output=3),
            TestCase(id=2, input={"root": None, "targetSum": 1}, expected_output=0)
        ],
        learning_objectives=["Transferring 1D subarray sum prefix hashmap technique to tree paths with backtracking"],
        common_misconceptions=["Forgetting to decrement prefix[curr_sum] when returning from recursion branch"],
        hint="Use a prefix sum hashmap during DFS; remove current sum when backtracking."
    ),

    "all-nodes-distance-k-in-binary-tree": Problem(
        id="all-nodes-distance-k-in-binary-tree",
        title="All Nodes Distance K in Binary Tree",
        difficulty="Medium",
        topic="Trees & Binary Search Trees",
        subtopic="Binary Tree Traversal",
        description="Given the root of a binary tree, the value of a target node `target`, and an integer `k`, return an array of the values of all nodes that have a distance `k` from the target node in any order.",
        examples=[
            {"input": "root = [3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], target = 5, k = 2", "output": "[7, 4, 1]"}
        ],
        constraints=["The number of nodes in the tree is in the range [1, 500].", "0 <= Node.val <= 500", "0 <= k <= 1000"],
        starter_code={
            "python": "def distance_k(root, target: int, k: int) -> list:\n    pass\n",
            "c": "void distanceK() {}\n",
            "cpp": "vector<int> distanceK(TreeNode* root, int target, int k) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> distanceK(TreeNode root, int target, int k) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": """from collections import deque, defaultdict
def distance_k(root, target: int, k: int) -> list:
    adj = defaultdict(list)
    def build_graph(node):
        if not node: return
        val = node.val if hasattr(node, 'val') else (node['val'] if isinstance(node, dict) else node)
        for child_attr in ('left', 'right'):
            child = getattr(node, child_attr, None) or (node.get(child_attr) if isinstance(node, dict) else None)
            if child:
                cval = child.val if hasattr(child, 'val') else (child['val'] if isinstance(child, dict) else child)
                adj[val].append(cval)
                adj[cval].append(val)
                build_graph(child)
    build_graph(root)
    queue = deque([(target, 0)])
    visited = {target}
    res = []
    while queue:
        curr, dist = queue.popleft()
        if dist == k:
            res.append(curr)
        elif dist < k:
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
    return sorted(res)
""",
            "c": "void distanceK() {}\n",
            "cpp": "vector<int> distanceK(TreeNode* root, int target, int k) { return {}; }\n",
            "java": "public class Solution { public static List<Integer> distanceK(TreeNode root, int target, int k) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"root": {"val": 3, "left": {"val": 5, "left": {"val": 6, "left": None, "right": None}, "right": {"val": 2, "left": {"val": 7, "left": None, "right": None}, "right": {"val": 4, "left": None, "right": None}}}, "right": {"val": 1, "left": {"val": 0, "left": None, "right": None}, "right": {"val": 8, "left": None, "right": None}}}, "target": 5, "k": 2}, expected_output=[1, 4, 7]),
            TestCase(id=2, input={"root": {"val": 1, "left": None, "right": None}, "target": 1, "k": 3}, expected_output=[])
        ],
        learning_objectives=["Converting directed tree to undirected adjacency graph and running level-order BFS"],
        common_misconceptions=["Searching only downwards in subtrees and missing ancestor paths"],
        hint="Convert tree to undirected graph by recording parent pointers, then run BFS from target."
    ),

    "binary-tree-cameras": Problem(
        id="binary-tree-cameras",
        title="Binary Tree Cameras (Min Camera Coverage)",
        difficulty="Hard",
        topic="Trees & Binary Search Trees",
        subtopic="Binary Tree Traversal",
        description="You are given the root of a binary tree. We install cameras on the tree nodes where each camera at a node can monitor its parent, itself, and its immediate children. Return the minimum number of cameras needed to monitor all nodes of the tree.",
        examples=[
            {"input": "root = [0, 0, null, 0, 0]", "output": "1", "explanation": "One camera is sufficient to monitor all nodes if placed at node 0's child."},
            {"input": "root = [0, 0, null, 0, null, 0, null, null, 0]", "output": "2"}
        ],
        constraints=["The number of nodes in the tree is in the range [1, 1000].", "Node.val == 0"],
        starter_code={
            "python": "def min_camera_cover(root) -> int:\n    pass\n",
            "c": "int minCameraCover(void* root) { return 0; }\n",
            "cpp": "int minCameraCover(TreeNode* root) { return 0; }\n",
            "java": "public class Solution { public static int minCameraCover(TreeNode root) { return 0; } }\n"
        },
        expected_solution={
            "python": """def min_camera_cover(root) -> int:
    cameras = 0
    # States: 0 = not covered, 1 = has camera, 2 = covered
    def dfs(node):
        nonlocal cameras
        if not node:
            return 2
        left = getattr(node, 'left', None) or (node.get('left') if isinstance(node, dict) else None)
        right = getattr(node, 'right', None) or (node.get('right') if isinstance(node, dict) else None)
        l_state = dfs(left)
        r_state = dfs(right)
        if l_state == 0 or r_state == 0:
            cameras += 1
            return 1
        if l_state == 1 or r_state == 1:
            return 2
        return 0
    if dfs(root) == 0:
        cameras += 1
    return cameras
""",
            "c": "int minCameraCover(void* root) { return 0; }\n",
            "cpp": "int minCameraCover(TreeNode* root) { return 0; }\n",
            "java": "public class Solution { public static int minCameraCover(TreeNode root) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"val": 0, "left": {"val": 0, "left": {"val": 0, "left": None, "right": None}, "right": {"val": 0, "left": None, "right": None}}, "right": None}, expected_output=1),
            TestCase(id=2, input={"val": 0, "left": None, "right": None}, expected_output=1)
        ],
        learning_objectives=["Greedy bottom-up post-order state machine for tree vertex cover"],
        common_misconceptions=["Placing cameras top-down starting from root which is suboptimal"],
        hint="Place cameras greedily at the parent of uncovered leaves using post-order DFS."
    ),


    "recover-binary-search-tree": Problem(
        id="recover-binary-search-tree",
        title="Recover Binary Search Tree",
        difficulty="Hard",
        topic="Trees & Binary Search Trees",
        subtopic="Binary Search Tree",
        description="You are given the root of a binary search tree (BST), where the values of exactly two nodes of the tree were swapped by mistake. Recover the tree without changing its structure.",
        examples=[
            {"input": "root = [1, 3, null, null, 2]", "output": "[3, 1, null, null, 2]"},
            {"input": "root = [3, 1, 4, null, null, 2]", "output": "[2, 1, 4, null, null, 3]"}
        ],
        constraints=["The number of nodes in the tree is in the range [2, 1000].", "-2^31 <= Node.val <= 2^31 - 1"],
        starter_code={
            "python": "def recover_tree(root):\n    pass\n",
            "c": "void recoverTree() {}\n",
            "cpp": "void recoverTree(TreeNode* root) {}\n",
            "java": "public class Solution { public static void recoverTree(TreeNode root) {}\n"
        },
        expected_solution={
            "python": """def recover_tree(root):
    nodes = []
    def inorder(node):
        if not node: return
        left = getattr(node, 'left', None) or (node.get('left') if isinstance(node, dict) else None)
        right = getattr(node, 'right', None) or (node.get('right') if isinstance(node, dict) else None)
        inorder(left)
        nodes.append(node)
        inorder(right)
    inorder(root)
    vals = [n.val if hasattr(n, 'val') else n['val'] for n in nodes]
    vals.sort()
    for i, n in enumerate(nodes):
        if hasattr(n, 'val'): n.val = vals[i]
        else: n['val'] = vals[i]
    return root
""",
            "c": "void recoverTree() {}\n",
            "cpp": "void recoverTree(TreeNode* root) {}\n",
            "java": "public class Solution { public static void recoverTree(TreeNode root) {}\n"
        },
        test_cases=[
            TestCase(id=1, input={"val": 1, "left": {"val": 3, "left": None, "right": {"val": 2, "left": None, "right": None}}, "right": None}, expected_output={"val": 3, "left": {"val": 1, "left": None, "right": {"val": 2, "left": None, "right": None}}, "right": None})
        ],
        learning_objectives=["Inorder traversal strictly increasing invariant of BST"],
        common_misconceptions=["Swapping pointers instead of node values"],
        hint="Inorder traversal of BST yields sorted values; detect where adjacent order is violated."
    ),

    # =========================================================================
    # GRAPHS & TRAVERSAL (5 problems)
    # =========================================================================
    "is-graph-bipartite": Problem(
        id="is-graph-bipartite",
        title="Is Graph Bipartite? (2-Coloring)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="BFS / Shortest Path",
        description="There is an undirected graph with `n` nodes. Return `True` if and only if it is bipartite (can partition nodes into two sets A and B such that every edge connects a node in A and a node in B).",
        examples=[
            {"input": "graph = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]", "output": "False"},
            {"input": "graph = [[1, 3], [0, 2], [1, 3], [0, 2]]", "output": "True"}
        ],
        constraints=["graph.length == n", "1 <= n <= 100"],
        starter_code={
            "python": "def is_bipartite(graph: list) -> bool:\n    pass\n",
            "c": "int isBipartite() { return 0; }\n",
            "cpp": "bool isBipartite(vector<vector<int>>& graph) { return false; }\n",
            "java": "public class Solution { public static boolean isBipartite(int[][] graph) { return false; } }\n"
        },
        expected_solution={
            "python": """def is_bipartite(graph: list) -> bool:
    n = len(graph)
    color = {}
    for i in range(n):
        if i not in color:
            color[i] = 0
            stack = [i]
            while stack:
                node = stack.pop()
                for neighbor in graph[node]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[node]
                        stack.append(neighbor)
                    elif color[neighbor] == color[node]:
                        return False
    return True
""",
            "c": "int isBipartite() { return 0; }\n",
            "cpp": "bool isBipartite(vector<vector<int>>& graph) { return false; }\n",
            "java": "public class Solution { public static boolean isBipartite(int[][] graph) { return false; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]], expected_output=False),
            TestCase(id=2, input=[[1, 3], [0, 2], [1, 3], [0, 2]], expected_output=True)
        ],
        learning_objectives=["2-coloring graph theorem and odd-cycle detection"],
        common_misconceptions=["Assuming graph is connected and not checking all components"],
        hint="Color nodes with 0 and 1; if any neighbor has the same color, graph is not bipartite."
    ),

    "shortest-path-in-binary-matrix": Problem(
        id="shortest-path-in-binary-matrix",
        title="Shortest Path in Binary Matrix (8-Directional)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="BFS / Shortest Path",
        description="Given an `n x n` binary matrix `grid`, return the length of the shortest clear path in the matrix from top-left `(0, 0)` to bottom-right `(n - 1, n - 1)`. All traversed cells must be 0. Path can step in 8 directions.",
        examples=[
            {"input": "grid = [[0, 1], [1, 0]]", "output": "2"},
            {"input": "grid = [[0, 0, 0], [1, 1, 0], [1, 1, 0]]", "output": "4"},
            {"input": "grid = [[1, 0, 0], [1, 1, 0], [1, 1, 0]]", "output": "-1"}
        ],
        constraints=["n == grid.length", "1 <= n <= 100", "grid[i][j] is 0 or 1"],
        starter_code={
            "python": "def shortest_path_binary_matrix(grid: list) -> int:\n    pass\n",
            "c": "int shortestPathBinaryMatrix() { return -1; }\n",
            "cpp": "int shortestPathBinaryMatrix(vector<vector<int>>& grid) { return -1; }\n",
            "java": "public class Solution { public static int shortestPathBinaryMatrix(int[][] grid) { return -1; } }\n"
        },
        expected_solution={
            "python": """from collections import deque
def shortest_path_binary_matrix(grid: list) -> int:
    n = len(grid)
    if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
        return -1
    if n == 1:
        return 1
    q = deque([(0, 0, 1)])
    grid[0][0] = 1
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while q:
        r, c, d = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                if nr == n - 1 and nc == n - 1:
                    return d + 1
                grid[nr][nc] = 1
                q.append((nr, nc, d + 1))
    return -1
""",
            "c": "int shortestPathBinaryMatrix() { return -1; }\n",
            "cpp": "int shortestPathBinaryMatrix(vector<vector<int>>& grid) { return -1; }\n",
            "java": "public class Solution { public static int shortestPathBinaryMatrix(int[][] grid) { return -1; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[0, 1], [1, 0]], expected_output=2),
            TestCase(id=2, input=[[0, 0, 0], [1, 1, 0], [1, 1, 0]], expected_output=4),
            TestCase(id=3, input=[[1, 0, 0], [1, 1, 0], [1, 1, 0]], expected_output=-1)
        ],
        learning_objectives=["Breadth-First Search guaranteeing shortest unweighted distance in 8 directions"],
        common_misconceptions=["Using DFS which does not guarantee shortest path and times out"],
        hint="Run BFS using 8 coordinate directions; mark visited immediately upon queuing."
    ),

    "accounts-merge": Problem(
        id="accounts-merge",
        title="Accounts Merge (Union Find)",
        difficulty="Medium",
        topic="Graphs & Traversal",
        subtopic="Graph Traversal (DFS/BFS)",
        description="Given a list of accounts where each element `accounts[i]` is a list of strings, the first element `accounts[i][0]` is a name, and the rest are emails. Merge accounts belonging to the same person.",
        examples=[
            {"input": "accounts = [['John', 'johnsmith@mail.com', 'john_newyork@mail.com'], ['John', 'johnsmith@mail.com', 'john00@mail.com'], ['Mary', 'mary@mail.com'], ['John', 'johnnybravo@mail.com']]", "output": "[['John', 'john00@mail.com', 'john_newyork@mail.com', 'johnsmith@mail.com'], ['John', 'johnnybravo@mail.com'], ['Mary', 'mary@mail.com']]"}
        ],
        constraints=["1 <= accounts.length <= 1000"],
        starter_code={
            "python": "def accounts_merge(accounts: list) -> list:\n    pass\n",
            "c": "void accountsMerge() {}\n",
            "cpp": "vector<vector<string>> accountsMerge(vector<vector<string>>& a) { return {}; }\n",
            "java": "public class Solution { public static List<List<String>> accountsMerge(List<List<String>> a) { return new ArrayList<>(); } }\n"
        },
        expected_solution={
            "python": """from collections import defaultdict
def accounts_merge(accounts: list) -> list:
    parent = {}
    email_to_name = {}
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry
    for acc in accounts:
        name = acc[0]
        first_email = acc[1]
        for email in acc[1:]:
            if email not in parent:
                parent[email] = email
            email_to_name[email] = name
            union(first_email, email)
    groups = defaultdict(list)
    for email in parent:
        groups[find(email)].append(email)
    res = []
    for root, emails in groups.items():
        res.append([email_to_name[root]] + sorted(emails))
    return sorted(res)
""",
            "c": "void accountsMerge() {}\n",
            "cpp": "vector<vector<string>> accountsMerge(vector<vector<string>>& a) { return {}; }\n",
            "java": "public class Solution { public static List<List<String>> accountsMerge(List<List<String>> a) { return new ArrayList<>(); } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"], ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]], expected_output=[["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"], ["John", "johnnybravo@mail.com"], ["Mary", "mary@mail.com"]])
        ],
        learning_objectives=["Disjoint Set Union (DSU) connecting emails shared across accounts"],
        common_misconceptions=["Assuming two accounts with identical names belong to same person even without shared emails"],
        hint="Union all emails within each account to the first email; group by DSU representative root."
    ),

    "longest-increasing-path-in-a-matrix": Problem(
        id="longest-increasing-path-in-a-matrix",
        title="Longest Increasing Path in a Matrix",
        difficulty="Hard",
        topic="Graphs & Traversal",
        subtopic="Graph Traversal (DFS/BFS)",
        description="Given an `m x n` integers `matrix`, return the length of the longest increasing path in matrix. From each cell, you can either move in four directions: left, right, up, or down.",
        examples=[
            {"input": "matrix = [[9, 9, 4], [6, 6, 8], [2, 1, 1]]", "output": "4", "explanation": "The longest increasing path is [1, 2, 6, 9]."},
            {"input": "matrix = [[3, 4, 5], [3, 2, 6], [2, 2, 1]]", "output": "4"}
        ],
        constraints=["m == matrix.length", "n == matrix[i].length", "1 <= m, n <= 200"],
        starter_code={
            "python": "def longest_increasing_path(matrix: list) -> int:\n    pass\n",
            "c": "int longestIncreasingPath() { return 0; }\n",
            "cpp": "int longestIncreasingPath(vector<vector<int>>& m) { return 0; }\n",
            "java": "public class Solution { public static int longestIncreasingPath(int[][] m) { return 0; } }\n"
        },
        expected_solution={
            "python": """def longest_increasing_path(matrix: list) -> int:
    if not matrix or not matrix[0]: return 0
    R, C = len(matrix), len(matrix[0])
    memo = {}
    def dfs(r, c):
        if (r, c) in memo:
            return memo[(r, c)]
        ans = 1
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and matrix[nr][nc] > matrix[r][c]:
                ans = max(ans, 1 + dfs(nr, nc))
        memo[(r, c)] = ans
        return ans
    return max(dfs(r, c) for r in range(R) for c in range(C))
""",
            "c": "int longestIncreasingPath() { return 0; }\n",
            "cpp": "int longestIncreasingPath(vector<vector<int>>& m) { return 0; }\n",
            "java": "public class Solution { public static int longestIncreasingPath(int[][] m) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[9, 9, 4], [6, 6, 8], [2, 1, 1]], expected_output=4),
            TestCase(id=2, input=[[3, 4, 5], [3, 2, 6], [2, 2, 1]], expected_output=4),
            TestCase(id=3, input=[[1]], expected_output=1)
        ],
        learning_objectives=["DAG topological longest path via DFS memoization"],
        common_misconceptions=["Assuming cycles exist: strictly increasing condition guarantees a DAG with no cycles"],
        hint="Since path must be strictly increasing, no cycles can exist; use DFS with memoization."
    ),

    "swim-in-rising-water": Problem(
        id="swim-in-rising-water",
        title="Swim in Rising Water (Minimax Elevation)",
        difficulty="Hard",
        topic="Graphs & Traversal",
        subtopic="BFS / Shortest Path",
        description="You are given an `n x n` integer matrix `grid` where each term represents elevation. At time `t`, depth of water everywhere is `t`. You can swim to adjacent square if elevation of both is at most `t`. Return least time until you can reach `(n - 1, n - 1)` from `(0, 0)`.",
        examples=[
            {"input": "grid = [[0, 2], [1, 3]]", "output": "3"},
            {"input": "grid = [[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]]", "output": "16"}
        ],
        constraints=["n == grid.length", "1 <= n <= 50"],
        starter_code={
            "python": "def swim_in_water(grid: list) -> int:\n    pass\n",
            "c": "int swimInWater() { return 0; }\n",
            "cpp": "int swimInWater(vector<vector<int>>& grid) { return 0; }\n",
            "java": "public class Solution { public static int swimInWater(int[][] grid) { return 0; } }\n"
        },
        expected_solution={
            "python": """import heapq
def swim_in_water(grid: list) -> int:
    n = len(grid)
    visited = {(0, 0)}
    pq = [(grid[0][0], 0, 0)]
    while pq:
        t, r, c = heapq.heappop(pq)
        if r == n - 1 and c == n - 1:
            return t
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in visited:
                visited.add((nr, nc))
                heapq.heappush(pq, (max(t, grid[nr][nc]), nr, nc))
    return 0
""",
            "c": "int swimInWater() { return 0; }\n",
            "cpp": "int swimInWater(vector<vector<int>>& grid) { return 0; }\n",
            "java": "public class Solution { public static int swimInWater(int[][] grid) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[[0, 2], [1, 3]], expected_output=3),
            TestCase(id=2, input=[[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]], expected_output=16)
        ],
        learning_objectives=["Modified Dijkstra algorithm tracking max-edge-weight bottleneck path"],
        common_misconceptions=["Using standard shortest path summing weights instead of bottleneck max"],
        hint="Dijkstra priority queue where edge cost is max(current_elevation, neighbor_elevation)."
    ),

    # =========================================================================
    # STACK & QUEUE (3 problems)
    # =========================================================================
    "car-fleet": Problem(
        id="car-fleet",
        title="Car Fleet",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="There are `n` cars at given miles away from starting mile 0, traveling towards target mile `target`. Return the number of car fleets that will arrive at the destination.",
        examples=[
            {"input": "target = 12, position = [10, 8, 0, 5, 3], speed = [2, 4, 1, 1, 3]", "output": "3"},
            {"input": "target = 10, position = [3], speed = [3]", "output": "1"},
            {"input": "target = 100, position = [0, 2, 4], speed = [4, 2, 1]", "output": "1"}
        ],
        constraints=["n == position.length", "1 <= n <= 10^5", "0 < target <= 10^6"],
        starter_code={
            "python": "def car_fleet(target: int, position: list, speed: list) -> int:\n    pass\n",
            "c": "int carFleet() { return 0; }\n",
            "cpp": "int carFleet(int target, vector<int>& p, vector<int>& s) { return 0; }\n",
            "java": "public class Solution { public static int carFleet(int target, int[] p, int[] s) { return 0; } }\n"
        },
        expected_solution={
            "python": """def car_fleet(target: int, position: list, speed: list) -> int:
    cars = sorted(zip(position, speed), reverse=True)
    stack = []
    for pos, spd in cars:
        time = (target - pos) / spd
        if not stack or time > stack[-1]:
            stack.append(time)
    return len(stack)
""",
            "c": "int carFleet() { return 0; }\n",
            "cpp": "int carFleet(int target, vector<int>& p, vector<int>& s) { return 0; }\n",
            "java": "public class Solution { public static int carFleet(int target, int[] p, int[] s) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"target": 12, "position": [10, 8, 0, 5, 3], "speed": [2, 4, 1, 1, 3]}, expected_output=3),
            TestCase(id=2, input={"target": 10, "position": [3], "speed": [3]}, expected_output=1),
            TestCase(id=3, input={"target": 100, "position": [0, 2, 4], "speed": [4, 2, 1]}, expected_output=1)
        ],
        learning_objectives=["Reverse sorting by position and monotonic time comparison"],
        common_misconceptions=["Simulating step-by-step floating point time steps which times out"],
        hint="Sort cars in reverse by position; calculate arrival time. A car catches up if its time <= predecessor time."
    ),

    "remove-all-adjacent-duplicates-in-string-ii": Problem(
        id="remove-all-adjacent-duplicates-in-string-ii",
        title="Remove All Adjacent Duplicates in String II",
        difficulty="Medium",
        topic="Stack & Queue",
        subtopic="Parentheses Matching",
        description="You are given a string `s` and an integer `k`. A `k` duplicate removal consists of choosing `k` adjacent and equal letters from `s` and removing them. Return final string after all possible removals.",
        examples=[
            {"input": "s = 'abcd', k = 2", "output": "'abcd'"},
            {"input": "s = 'deeedbbcccbdaa', k = 3", "output": "'aa'"},
            {"input": "s = 'pbbcggttciiippooaais', k = 2", "output": "'ps'"}
        ],
        constraints=["1 <= s.length <= 10^5", "2 <= k <= 10^4"],
        starter_code={
            "python": "def remove_duplicates(s: str, k: int) -> str:\n    pass\n",
            "c": "char* removeDuplicates(char* s, int k) { return s; }\n",
            "cpp": "string removeDuplicates(string s, int k) { return s; }\n",
            "java": "public class Solution { public static String removeDuplicates(String s, int k) { return s; } }\n"
        },
        expected_solution={
            "python": """def remove_duplicates(s: str, k: int) -> str:
    stack = []
    for c in s:
        if stack and stack[-1][0] == c:
            stack[-1][1] += 1
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append([c, 1])
    return ''.join(c * cnt for c, cnt in stack)
""",
            "c": "char* removeDuplicates(char* s, int k) { return s; }\n",
            "cpp": "string removeDuplicates(string s, int k) { return s; }\n",
            "java": "public class Solution { public static String removeDuplicates(String s, int k) { return s; } }\n"
        },
        test_cases=[
            TestCase(id=1, input={"s": "abcd", "k": 2}, expected_output="abcd"),
            TestCase(id=2, input={"s": "deeedbbcccbdaa", "k": 3}, expected_output="aa"),
            TestCase(id=3, input={"s": "pbbcggttciiippooaais", "k": 2}, expected_output="ps")
        ],
        learning_objectives=["Stack storing pairs of [character, count] to compress repetitive scanning into O(N)"],
        common_misconceptions=["Repeatedly searching for runs and re-slicing strings in O(N^2)"],
        hint="Keep a stack of [char, count]; when count reaches k, pop from stack."
    ),

    "sum-of-subarray-minimums": Problem(
        id="sum-of-subarray-minimums",
        title="Sum of Subarray Minimums",
        difficulty="Hard",
        topic="Stack & Queue",
        subtopic="Monotonic Stack",
        description="Given an array of integers `arr`, find the sum of `min(b)`, where `b` ranges over every contiguous subarray of `arr`. Since the answer may be large, return the answer modulo `10^9 + 7`.",
        examples=[
            {"input": "arr = [3, 1, 2, 4]", "output": "17", "explanation": "Subarrays are [3], [1], [2], [4], [3,1], [1,2], [2,4], [3,1,2], [1,2,4], [3,1,2,4]. Minimums are 3, 1, 2, 4, 1, 1, 2, 1, 1, 1. Sum is 17."},
            {"input": "arr = [11, 81, 94, 43, 3]", "output": "444"}
        ],
        constraints=["1 <= arr.length <= 3 * 10^4", "1 <= arr[i] <= 3 * 10^4"],
        starter_code={
            "python": "def sum_subarray_mins(arr: list) -> int:\n    pass\n",
            "c": "int sumSubarrayMins(int* arr, int arrSize) { return 0; }\n",
            "cpp": "int sumSubarrayMins(vector<int>& arr) { return 0; }\n",
            "java": "public class Solution { public static int sumSubarrayMins(int[] arr) { return 0; } }\n"
        },
        expected_solution={
            "python": """def sum_subarray_mins(arr: list) -> int:
    MOD = 10**9 + 7
    n = len(arr)
    left = [0] * n
    right = [0] * n
    s1, s2 = [], []
    for i in range(n):
        count = 1
        while s1 and s1[-1][0] > arr[i]:
            count += s1.pop()[1]
        s1.append((arr[i], count))
        left[i] = count
    for i in range(n - 1, -1, -1):
        count = 1
        while s2 and s2[-1][0] >= arr[i]:
            count += s2.pop()[1]
        s2.append((arr[i], count))
        right[i] = count
    return sum(a * l * r for a, l, r in zip(arr, left, right)) % MOD
""",
            "c": "int sumSubarrayMins(int* arr, int arrSize) { return 0; }\n",
            "cpp": "int sumSubarrayMins(vector<int>& arr) { return 0; }\n",
            "java": "public class Solution { public static int sumSubarrayMins(int[] arr) { return 0; } }\n"
        },
        test_cases=[
            TestCase(id=1, input=[3, 1, 2, 4], expected_output=17),
            TestCase(id=2, input=[11, 81, 94, 43, 3], expected_output=444)
        ],
        learning_objectives=["Contribution technique calculating how many subarrays an element is minimum for using monotonic stacks"],
        common_misconceptions=["Double counting duplicate elements: use strict inequality on one side and non-strict on other"],
        hint="Count how many subarrays have arr[i] as minimum using previous and next smaller elements."
    )
}
