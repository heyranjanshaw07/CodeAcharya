import json
import sqlite3
from typing import Dict, Any
from database import get_db, init_database
from problems import PROBLEMS

def seed_questions():
    """
    Seeds curated coding questions into the coding_questions table.
    Ensures safe upsert/preservation: existing questions are preserved.
    """
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        seeded_count = 0

        for pid, prob in PROBLEMS.items():
            cursor.execute("SELECT id FROM coding_questions WHERE id = ?", (pid,))
            if cursor.fetchone():
                continue

            # Convert test cases
            test_cases_data = []
            for tc in getattr(prob, "test_cases", []):
                if hasattr(tc, "dict"):
                    test_cases_data.append(tc.dict())
                elif hasattr(tc, "model_dump"):
                    test_cases_data.append(tc.model_dump())
                elif isinstance(tc, dict):
                    test_cases_data.append(tc)

            is_gen = 1 if getattr(prob, "is_generated", False) else 0
            source = getattr(prob, "source", "curated") or "curated"

            cursor.execute("""
                INSERT INTO coding_questions (
                    id, title, description, difficulty, topic, subtopic,
                    tags, supported_languages, starter_code, test_cases,
                    learning_objectives, common_misconceptions, input_format,
                    output_format, hint, progressive_hints, explanation,
                    expected_solution, time_complexity, space_complexity,
                    relevant_concepts, is_generated, source, is_active
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, 1
                )
            """, (
                prob.id,
                prob.title,
                prob.description,
                prob.difficulty,
                prob.topic,
                getattr(prob, "subtopic", "") or "",
                json.dumps(getattr(prob, "tags", []) or []),
                json.dumps(list(prob.starter_code.keys()) if hasattr(prob, "starter_code") and prob.starter_code else ["python", "c", "cpp", "java"]),
                json.dumps(getattr(prob, "starter_code", {}) or {}),
                json.dumps(test_cases_data),
                json.dumps(getattr(prob, "learning_objectives", []) or []),
                json.dumps(getattr(prob, "common_misconceptions", []) or []),
                getattr(prob, "input_format", "") or "",
                getattr(prob, "output_format", "") or "",
                getattr(prob, "hint", "") or "",
                json.dumps([h if isinstance(h, dict) else h.dict() for h in (getattr(prob, "progressive_hints", []) or [])]),
                getattr(prob, "explanation", "") or "",
                json.dumps(getattr(prob, "expected_solution", {}) or {}),
                getattr(prob, "time_complexity", "") or "O(N)",
                getattr(prob, "space_complexity", "") or "O(1)",
                json.dumps(getattr(prob, "relevant_concepts", []) or []),
                is_gen,
                source
            ))
            seeded_count += 1

        conn.commit()
        return seeded_count

if __name__ == "__main__":
    count = seed_questions()
    print(f"Seeded {count} coding questions successfully.")
