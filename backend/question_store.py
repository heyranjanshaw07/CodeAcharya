import os
import json
import threading
from typing import Dict, List, Optional, Any
from models import Problem, TestCase

DEFAULT_STORE_PATH = os.path.join(os.path.dirname(__file__), "generated_questions.json")

class QuestionStore:
    """
    Thread-safe persistent store and cache for AI-generated coding problems.
    Caches problems in memory and persists them to JSON storage.
    """
    def __init__(self, filepath: str = DEFAULT_STORE_PATH):
        self.filepath = filepath
        self._lock = threading.Lock()
        self._generated_cache: Dict[str, Problem] = {}
        self._load()

    def _problem_to_dict(self, p: Problem) -> Dict[str, Any]:
        return {
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "topic": p.topic,
            "subtopic": p.subtopic or "",
            "description": p.description,
            "examples": p.examples,
            "constraints": p.constraints,
            "starter_code": p.starter_code,
            "test_cases": [
                {
                    "id": tc.id,
                    "input": tc.input,
                    "expected_output": tc.expected_output,
                    "is_hidden": tc.is_hidden,
                    "explanation": tc.explanation
                }
                for tc in p.test_cases
            ],
            "learning_objectives": p.learning_objectives or [],
            "common_misconceptions": p.common_misconceptions or [],
            "input_format": p.input_format or "",
            "output_format": p.output_format or "",
            "hint": p.hint or "",
            "progressive_hints": p.progressive_hints or [],
            "explanation": p.explanation or "",
            "expected_solution": p.expected_solution or {},
            "time_complexity": p.time_complexity or "",
            "space_complexity": p.space_complexity or "",
            "relevant_concepts": p.relevant_concepts or [],
            "is_generated": True,
            "source": p.source or "ai_generated"
        }

    def _dict_to_problem(self, d: Dict[str, Any]) -> Problem:
        tcs = []
        for tc_data in d.get("test_cases", []):
            if isinstance(tc_data, dict):
                tcs.append(TestCase(
                    id=tc_data.get("id", len(tcs) + 1),
                    input=tc_data.get("input"),
                    expected_output=tc_data.get("expected_output", tc_data.get("expected")),
                    is_hidden=tc_data.get("is_hidden", False),
                    explanation=tc_data.get("explanation")
                ))
            elif isinstance(tc_data, TestCase):
                tcs.append(tc_data)

        sc = dict(d.get("starter_code", {}))
        if "javascript" in sc:
            del sc["javascript"]
        if "c" not in sc:
            sc["c"] = "#include <stdio.h>\n#include <stdlib.h>\n\nint solution() {\n    \n}\n"

        return Problem(
            id=d["id"],
            title=d["title"],
            difficulty=d["difficulty"],
            topic=d["topic"],
            subtopic=d.get("subtopic", ""),
            description=d["description"],
            examples=d.get("examples", []),
            constraints=d.get("constraints", []),
            starter_code=sc,
            test_cases=tcs,
            learning_objectives=d.get("learning_objectives", []),
            common_misconceptions=d.get("common_misconceptions", []),
            input_format=d.get("input_format", d.get("inputFormat", "")),
            output_format=d.get("output_format", d.get("outputFormat", "")),
            hint=d.get("hint", ""),
            progressive_hints=d.get("progressive_hints", []),
            explanation=d.get("explanation", ""),
            expected_solution=d.get("expected_solution", {}),
            time_complexity=d.get("time_complexity", ""),
            space_complexity=d.get("space_complexity", ""),
            relevant_concepts=d.get("relevant_concepts", []),
            is_generated=True,
            source=d.get("source", "ai_generated")
        )

    def _load(self):
        with self._lock:
            if not os.path.exists(self.filepath):
                return
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "id" in item:
                                prob = self._dict_to_problem(item)
                                self._generated_cache[prob.id] = prob
            except Exception as e:
                print(f"[QuestionStore] Notice loading questions file: {e}")

    def load_into_problems(self, problems_registry: Dict[str, Problem]):
        """Populates the main in-memory problems dictionary with all persisted generated problems."""
        with self._lock:
            for pid, prob in self._generated_cache.items():
                problems_registry[pid] = prob

    def save_problem(self, problem: Problem):
        """Thread-safely saves a problem to memory and persists to disk."""
        with self._lock:
            problem.is_generated = True
            self._generated_cache[problem.id] = problem
            
            # Atomic save to prevent corruption
            temp_path = self.filepath + ".tmp"
            try:
                data = [self._problem_to_dict(p) for p in self._generated_cache.values()]
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(temp_path, self.filepath)
            except Exception as e:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
                print(f"[QuestionStore] Error saving problem {problem.id}: {e}")
                raise e

    def exists(self, problem_id: str) -> bool:
        with self._lock:
            return problem_id in self._generated_cache

    def get(self, problem_id: str) -> Optional[Problem]:
        with self._lock:
            return self._generated_cache.get(problem_id)

    def get_recent_titles(self, topic: Optional[str] = None, limit: int = 50) -> List[str]:
        with self._lock:
            titles = []
            for p in reversed(list(self._generated_cache.values())):
                if not topic or p.topic.lower() == topic.lower():
                    titles.append(p.title)
                    if len(titles) >= limit:
                        break
            return titles

    def get_recent_ids(self, topic: Optional[str] = None, limit: int = 50) -> List[str]:
        with self._lock:
            ids = []
            for p in reversed(list(self._generated_cache.values())):
                if not topic or p.topic.lower() == topic.lower():
                    ids.append(p.id)
                    if len(ids) >= limit:
                        break
            return ids

    def get_all(self, topic: Optional[str] = None, difficulty: Optional[str] = None) -> List[Problem]:
        with self._lock:
            res = []
            for p in self._generated_cache.values():
                if topic and p.topic.lower() != topic.lower():
                    continue
                if difficulty and p.difficulty.lower() != difficulty.lower():
                    continue
            return res

    def clear_all(self, problems_registry: Optional[Dict[str, Problem]] = None) -> int:
        """Purges all generated questions from cache, persistent storage, and optionally the main problems registry."""
        with self._lock:
            count = len(self._generated_cache)
            if problems_registry is not None:
                for pid in list(self._generated_cache.keys()):
                    problems_registry.pop(pid, None)
                for pid in list(problems_registry.keys()):
                    if getattr(problems_registry[pid], "is_generated", False):
                        problems_registry.pop(pid, None)
                        count += 1
            self._generated_cache.clear()
            try:
                temp_path = self.filepath + ".tmp"
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
                os.replace(temp_path, self.filepath)
            except Exception as e:
                print(f"[QuestionStore] Error emptying storage file: {e}")
            return count

# Global default instance
question_store = QuestionStore()

def get_question_store() -> QuestionStore:
    return question_store

