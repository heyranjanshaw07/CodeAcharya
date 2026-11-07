from typing import Dict, Any, List, Optional
from models import VivaQuestion

class QuestionRubric:
    """
    Structured rubric defining essential concepts, supporting concepts,
    common misconceptions, applicable dimensions, and dimension weights for a viva question.
    """
    def __init__(
        self,
        question_id: int,
        category: str,
        question: str,
        hint_guidance: str,
        essential_concepts: List[str],
        supporting_concepts: List[str],
        common_misconceptions: List[str],
        applicable_dimensions: List[str],
        dimension_weights: Dict[str, float],
        sample_strong_answer: Optional[str] = None
    ):
        self.question_id = question_id
        self.category = category
        self.question = question
        self.hint_guidance = hint_guidance
        self.essential_concepts = essential_concepts
        self.supporting_concepts = supporting_concepts
        self.common_misconceptions = common_misconceptions
        self.applicable_dimensions = applicable_dimensions
        self.dimension_weights = dimension_weights
        self.sample_strong_answer = sample_strong_answer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "category": self.category,
            "question": self.question,
            "hint_guidance": self.hint_guidance,
            "essential_concepts": self.essential_concepts,
            "supporting_concepts": self.supporting_concepts,
            "common_misconceptions": self.common_misconceptions,
            "applicable_dimensions": self.applicable_dimensions,
            "dimension_weights": self.dimension_weights,
            "sample_strong_answer": self.sample_strong_answer
        }


# Curated question rubrics for flagship curriculum problems
CURATED_RUBRICS: Dict[str, Dict[int, QuestionRubric]] = {
    "factorial-recursion": {
        1: QuestionRubric(
            question_id=1,
            category="conceptual",
            question="Why is a base case fundamentally required in any recursive function, and what would happen at the operating system / runtime level without it?",
            hint_guidance="Discuss the call stack, stack frames, and RecursionError/StackOverflow.",
            essential_concepts=[
                "terminate recursive calls",
                "call stack",
                "stack frames",
                "stack overflow"
            ],
            supporting_concepts=[
                "activation record",
                "memory exhaustion",
                "base condition"
            ],
            common_misconceptions=[
                "A base case is only for returning zero",
                "The function automatically stops when memory gets full without crashing"
            ],
            applicable_dimensions=["conceptual_score", "communication_score"],
            dimension_weights={"conceptual_score": 0.70, "communication_score": 0.30}
        ),
        2: QuestionRubric(
            question_id=2,
            category="code_choice",
            question="Why does the base case return 1 instead of 0 for factorial? What mathematical property dictates this?",
            hint_guidance="Explain the multiplicative identity and the combinatorial definition of 0!.",
            essential_concepts=[
                "multiplicative identity",
                "zero annihilates multiplication",
                "factorial definition 0! = 1"
            ],
            supporting_concepts=[
                "empty product",
                "n * factorial(n-1)"
            ],
            common_misconceptions=[
                "Returning 0 would be fine because 0 * anything is 0",
                "Base case value does not matter as long as it stops"
            ],
            applicable_dimensions=["code_understanding_score", "conceptual_score", "communication_score"],
            dimension_weights={"code_understanding_score": 0.45, "conceptual_score": 0.35, "communication_score": 0.20}
        ),
        3: QuestionRubric(
            question_id=3,
            category="complexity",
            question="What is the space complexity of your recursive implementation, and why does it consume memory even though you don't allocate an array?",
            hint_guidance="Mention call stack depth and activation records: O(N) auxiliary space.",
            essential_concepts=[
                "O(N) space",
                "call stack depth",
                "activation records"
            ],
            supporting_concepts=[
                "stack frames",
                "linear memory",
                "auxiliary space"
            ],
            common_misconceptions=[
                "O(1) space because no list or array is explicitly declared",
                "Space complexity is only heap memory"
            ],
            applicable_dimensions=["complexity_score", "conceptual_score", "communication_score"],
            dimension_weights={"complexity_score": 0.60, "conceptual_score": 0.25, "communication_score": 0.15}
        ),
        4: QuestionRubric(
            question_id=4,
            category="optimization",
            question="How does this recursive version compare to an iterative loop in terms of performance and memory overhead?",
            hint_guidance="Iterative loop avoids stack frame allocation overhead and operates in O(1) space.",
            essential_concepts=[
                "O(1) space iterative",
                "avoids call stack frames",
                "lower overhead"
            ],
            supporting_concepts=[
                "loop variable",
                "stack overflow immunity",
                "function call overhead"
            ],
            common_misconceptions=[
                "Recursion is faster than iterative loops",
                "Both have identical memory footprints"
            ],
            applicable_dimensions=["conceptual_score", "complexity_score", "communication_score"],
            dimension_weights={"conceptual_score": 0.45, "complexity_score": 0.40, "communication_score": 0.15}
        )
    },
    "two-sum": {
        1: QuestionRubric(
            question_id=1,
            category="conceptual",
            question="Explain why using a Hash Map reduces the time complexity from O(N^2) brute force to O(N). What trade-off is made?",
            hint_guidance="Highlight time-space trade-off and constant-time average hash lookups.",
            essential_concepts=[
                "O(1) average lookup",
                "time-space trade-off",
                "O(N) auxiliary memory"
            ],
            supporting_concepts=[
                "complement lookup",
                "single pass",
                "hash table"
            ],
            common_misconceptions=[
                "Hash map lookups are always O(1) in the worst case regardless of collisions",
                "No extra memory is required"
            ],
            applicable_dimensions=["conceptual_score", "communication_score"],
            dimension_weights={"conceptual_score": 0.70, "communication_score": 0.30}
        ),
        2: QuestionRubric(
            question_id=2,
            category="code_choice",
            question="Why do you store `target - num` as the lookup key rather than checking every pair? Why check before inserting `num`?",
            hint_guidance="Prevents matching an element with itself when target is 2 * num.",
            essential_concepts=[
                "prevents self-pairing",
                "target equals 2 * num",
                "distinct indices"
            ],
            supporting_concepts=[
                "single element reuse",
                "complement check before insertion"
            ],
            common_misconceptions=[
                "Inserting first and checking later works without any special index validation"
            ],
            applicable_dimensions=["code_understanding_score", "conceptual_score", "communication_score"],
            dimension_weights={"code_understanding_score": 0.50, "conceptual_score": 0.30, "communication_score": 0.20}
        ),
        3: QuestionRubric(
            question_id=3,
            category="complexity",
            question="What is the worst-case time complexity of hash table lookup, and when can hash collisions degrade performance?",
            hint_guidance="O(N) worst case on severe hash collisions, O(1) amortized average.",
            essential_concepts=[
                "O(N) worst case",
                "hash collisions",
                "O(1) amortized average"
            ],
            supporting_concepts=[
                "bucket chaining",
                "poor hash function",
                "linear search in bucket"
            ],
            common_misconceptions=[
                "Hash table is strictly O(1) in all mathematical scenarios including adversarial inputs"
            ],
            applicable_dimensions=["complexity_score", "conceptual_score", "communication_score"],
            dimension_weights={"complexity_score": 0.60, "conceptual_score": 0.25, "communication_score": 0.15}
        ),
        4: QuestionRubric(
            question_id=4,
            category="optimization",
            question="If the input array were guaranteed to be sorted, could you solve this in O(1) extra space? Which technique would you employ?",
            hint_guidance="Two-pointer approach (left and right pointers moving inwards).",
            essential_concepts=[
                "two pointers",
                "left and right pointers",
                "O(1) auxiliary space",
                "sorted order enables monotonic sum adjustment"
            ],
            supporting_concepts=[
                "move inwards",
                "sum too small increment left",
                "sum too large decrement right",
                "O(N) time"
            ],
            common_misconceptions=[
                "Two pointers work on unsorted arrays without sorting first",
                "Binary search is always faster than two pointers on sorted arrays"
            ],
            applicable_dimensions=["conceptual_score", "complexity_score", "code_understanding_score", "communication_score"],
            dimension_weights={"conceptual_score": 0.35, "complexity_score": 0.30, "code_understanding_score": 0.20, "communication_score": 0.15}
        )
    },
    "valid-parentheses": {
        1: QuestionRubric(
            question_id=1,
            category="conceptual",
            question="Why is a Stack the natural data structure for matching parentheses, rather than a Queue or a set of counters?",
            hint_guidance="Nested brackets exhibit LIFO ordering; counters cannot enforce order like '([)]'.",
            essential_concepts=[
                "LIFO order",
                "most recently opened bracket closed first",
                "counters fail on interleaved brackets"
            ],
            supporting_concepts=[
                "nested structures",
                "stack top",
                "relative order"
            ],
            common_misconceptions=[
                "Three counters (one for each bracket type) are sufficient to validate nested strings"
            ],
            applicable_dimensions=["conceptual_score", "communication_score"],
            dimension_weights={"conceptual_score": 0.70, "communication_score": 0.30}
        ),
        2: QuestionRubric(
            question_id=2,
            category="code_choice",
            question="How does your code prevent an IndexError or exception when a closing bracket appears as the very first character in the string?",
            hint_guidance="Checking if stack is empty before popping or using a fallback dummy character.",
            essential_concepts=[
                "check stack is empty",
                "early return False or guard before pop",
                "prevents pop from empty stack"
            ],
            supporting_concepts=[
                "stack underflow",
                "if not stack"
            ],
            common_misconceptions=[
                "Popping without checking is fine because exception handling will return False automatically"
            ],
            applicable_dimensions=["code_understanding_score", "conceptual_score", "communication_score"],
            dimension_weights={"code_understanding_score": 0.50, "conceptual_score": 0.30, "communication_score": 0.20}
        ),
        3: QuestionRubric(
            question_id=3,
            category="complexity",
            question="What are the time and space complexities of this solution? Could the space complexity be improved if we only allowed one bracket type '()'?",
            hint_guidance="Both O(N). With single bracket type, a single integer counter in O(1) space suffices.",
            essential_concepts=[
                "O(N) time and O(N) space",
                "single integer counter",
                "O(1) space for single bracket type"
            ],
            supporting_concepts=[
                "single pass",
                "stack size up to N",
                "balance counter"
            ],
            common_misconceptions=[
                "Single bracket type still requires a stack because of nested structures"
            ],
            applicable_dimensions=["complexity_score", "conceptual_score", "communication_score"],
            dimension_weights={"complexity_score": 0.60, "conceptual_score": 0.25, "communication_score": 0.15}
        ),
        4: QuestionRubric(
            question_id=4,
            category="edge_case",
            question="What happens if the input string is `((((` with no closing brackets? Which line of your code detects this failure?",
            hint_guidance="The final check `len(stack) == 0` ensures unclosed open brackets trigger False.",
            essential_concepts=[
                "len(stack) == 0 final check",
                "unclosed open brackets remain",
                "evaluates to False"
            ],
            supporting_concepts=[
                "stack non-empty at end",
                "return not stack"
            ],
            common_misconceptions=[
                "Loop termination alone guarantees validity"
            ],
            applicable_dimensions=["code_understanding_score", "conceptual_score", "communication_score"],
            dimension_weights={"code_understanding_score": 0.50, "conceptual_score": 0.30, "communication_score": 0.20}
        )
    }
}


def get_question_rubric(problem_id: str, question: VivaQuestion, modality: str = "typed") -> QuestionRubric:
    """
    Retrieves or dynamically builds a specific rubric for a viva question,
    accounting for answer modality (typed vs voice_transcribed).
    """
    if problem_id in CURATED_RUBRICS and question.id in CURATED_RUBRICS[problem_id]:
        rubric = CURATED_RUBRICS[problem_id][question.id]
        dims = list(rubric.applicable_dimensions)
        weights = dict(rubric.dimension_weights)
        if modality != "voice_transcribed" and modality != "audio_recorded":
            dims = [d for d in dims if d != "communication_score"]
            weights = {d: w for d, w in weights.items() if d != "communication_score"}
            total_w = sum(weights.values())
            if total_w > 0:
                weights = {d: round(w / total_w, 4) for d, w in weights.items()}
        return QuestionRubric(
            question_id=rubric.question_id,
            category=rubric.category,
            question=rubric.question,
            hint_guidance=rubric.hint_guidance,
            essential_concepts=rubric.essential_concepts,
            supporting_concepts=rubric.supporting_concepts,
            common_misconceptions=rubric.common_misconceptions,
            applicable_dimensions=dims,
            dimension_weights=weights,
            sample_strong_answer=rubric.sample_strong_answer
        )

    # Dynamically build question-specific rubric
    q_text = question.question
    q_lower = q_text.lower()
    cat = (question.category or "conceptual").lower()
    hint = question.hint_guidance or "Core algorithmic reasoning and technical justification"

    asks_complexity = any(k in q_lower for k in ["complexity", "big-o", "big o", "asymptotic", "o(n)", "o(1)", "o(log", "space", "time"])
    asks_code = any(k in q_lower for k in ["code", "line", "conditional", "loop", "invariant", "detects", "exception", "which line", "how does your code"])

    if cat == "complexity" or asks_complexity:
        dims = ["complexity_score", "conceptual_score", "communication_score"]
        weights = {"complexity_score": 0.60, "conceptual_score": 0.25, "communication_score": 0.15}
        if asks_code:
            dims.append("code_understanding_score")
            weights = {"complexity_score": 0.45, "conceptual_score": 0.25, "code_understanding_score": 0.15, "communication_score": 0.15}
    elif cat in ("code_choice", "edge_case") or asks_code:
        dims = ["code_understanding_score", "conceptual_score", "communication_score"]
        weights = {"code_understanding_score": 0.50, "conceptual_score": 0.30, "communication_score": 0.20}
        if asks_complexity:
            dims.append("complexity_score")
            weights = {"code_understanding_score": 0.40, "conceptual_score": 0.25, "complexity_score": 0.20, "communication_score": 0.15}
    elif cat == "optimization":
        dims = ["conceptual_score", "complexity_score", "communication_score"]
        weights = {"conceptual_score": 0.45, "complexity_score": 0.40, "communication_score": 0.15}
        if asks_code:
            dims.append("code_understanding_score")
            weights = {"conceptual_score": 0.35, "complexity_score": 0.35, "code_understanding_score": 0.15, "communication_score": 0.15}
    else:
        dims = ["conceptual_score", "communication_score"]
        weights = {"conceptual_score": 0.70, "communication_score": 0.30}
        if asks_code:
            dims.append("code_understanding_score")
            weights = {"conceptual_score": 0.50, "code_understanding_score": 0.30, "communication_score": 0.20}
        if asks_complexity:
            dims.append("complexity_score")
            weights = {"conceptual_score": 0.50, "complexity_score": 0.30, "communication_score": 0.20}

    if modality != "voice_transcribed" and modality != "audio_recorded":
        dims = [d for d in dims if d != "communication_score"]
        weights = {d: w for d, w in weights.items() if d != "communication_score"}
        total_w = sum(weights.values())
        if total_w > 0:
            weights = {d: round(w / total_w, 4) for d, w in weights.items()}

    # Extract essential concepts from hint guidance
    parts = [p.strip() for p in hint.replace(";", ".").replace(",", ".").split(".") if len(p.strip()) > 3]
    essential = parts[:3] if parts else [hint]

    return QuestionRubric(
        question_id=question.id,
        category=cat,
        question=q_text,
        hint_guidance=hint,
        essential_concepts=essential,
        supporting_concepts=["Accurate technical reasoning", "Directly answering prompt"],
        common_misconceptions=["Generic answers lacking technical rationale", "Vague claims without mechanism"],
        applicable_dimensions=dims,
        dimension_weights=weights
    )
