import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

PROFILE_FILE = "student_profile.json"

DEFAULT_PROFILE = {
    "student_name": "Student Learner",
    "streak_days": 4,
    "total_solved": 3,
    "total_attempts": 12,
    "hints_unlocked": 7,
    "total_debug_time_mins": 38,
    "topic_mastery": {
        "Recursion & Backtracking": 68,
        "Arrays & Hashing": 85,
        "Strings": 80,
        "Stack & Queue": 74,
        "Dynamic Programming": 52,
        "Algorithms & Two Pointers": 78
    },
    "recent_mistakes": [
        {"topic": "Recursion", "mistake": "Base case returned 0 causing zero-collapse in factorial", "time": "Today"},
        {"topic": "Dynamic Programming", "mistake": "Overlapping recursive calls without memoization table", "time": "Yesterday"},
        {"topic": "Stack", "mistake": "Missed empty-stack check before popping closing bracket", "time": "2 days ago"}
    ],
    "viva_history": [
        {
            "problem_id": "factorial-recursion",
            "date": "2026-10-08",
            "overall_score": 82,
            "conceptual": 85,
            "code_understanding": 90,
            "complexity": 75,
            "communication": 78
        }
    ],
    "activity_log": [
        {"action": "Solved", "problem": "Two Sum (Optimal Lookup)", "timestamp": "2026-10-07 16:30"},
        {"action": "Viva Passed", "problem": "Factorial of a Number", "timestamp": "2026-10-08 11:15"},
        {"action": "Attempted", "problem": "Valid Parentheses", "timestamp": "2026-10-08 14:20"}
    ]
}

class AnalyticsManager:
    def __init__(self, filepath: str = PROFILE_FILE):
        self.filepath = filepath
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_PROFILE.copy()

    def _save_profile(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.profile, f, indent=2)
        except Exception:
            pass

    def get_profile(self) -> Dict[str, Any]:
        return self.profile

    def format_duration(self, seconds: int) -> str:
        if seconds <= 0:
            return "00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def record_attempt(
        self, 
        problem_id: str, 
        topic: str, 
        passed: bool, 
        hints_used: int = 0, 
        time_spent_seconds: int = 0, 
        session_status: str = "completed",
        tab_switch_count: int = 0,
        total_time_away_seconds: int = 0,
        last_switch_timestamp: Optional[str] = None,
        tab_switch_history: Optional[List[Dict[str, Any]]] = None
    ):
        self.profile["total_attempts"] += 1
        self.profile["hints_unlocked"] += hints_used

        if time_spent_seconds > 0:
            self.profile["total_coding_time_seconds"] = self.profile.get("total_coding_time_seconds", 0) + time_spent_seconds
            self.profile["total_debug_time_mins"] = round(self.profile.get("total_coding_time_seconds", 0) / 60)

        formatted_time = self.format_duration(time_spent_seconds)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        solving_times = self.profile.setdefault("problem_solving_times", {})
        current_mastery = self.profile["topic_mastery"].get(topic, 50)
        history_list = tab_switch_history or []
        if passed:
            self.profile["total_solved"] += 1
            # Increase mastery
            delta = max(2, 8 - hints_used * 2)
            self.profile["topic_mastery"][topic] = min(100, current_mastery + delta)
            
            solving_times[problem_id] = {
                "time_spent_seconds": time_spent_seconds,
                "time_spent_formatted": formatted_time,
                "completed_at": now_str,
                "status": "completed",
                "tab_switch_count": tab_switch_count,
                "total_time_away_seconds": total_time_away_seconds,
                "last_switch_timestamp": last_switch_timestamp,
                "tab_switch_history": history_list
            }

            self.profile["activity_log"].insert(0, {
                "action": "Solved",
                "problem": problem_id,
                "timestamp": now_str,
                "time_spent_seconds": time_spent_seconds,
                "time_spent": formatted_time,
                "tab_switch_count": tab_switch_count,
                "total_time_away_seconds": total_time_away_seconds,
                "last_switch_timestamp": last_switch_timestamp,
                "tab_switch_history": history_list
            })
        else:
            # Decrease slightly or mark mistake
            self.profile["topic_mastery"][topic] = max(10, current_mastery - 2)
            action_name = "Abandoned Attempt" if session_status == "abandoned" else "Failed Attempt"
            self.profile["activity_log"].insert(0, {
                "action": action_name,
                "problem": problem_id,
                "timestamp": now_str,
                "time_spent_seconds": time_spent_seconds,
                "time_spent": formatted_time,
                "tab_switch_count": tab_switch_count,
                "total_time_away_seconds": total_time_away_seconds,
                "last_switch_timestamp": last_switch_timestamp,
                "tab_switch_history": history_list
            })

        self.profile["activity_log"] = self.profile["activity_log"][:15]
        self._save_profile()

    def record_session(
        self, 
        problem_id: str, 
        topic: str, 
        status: str, 
        time_spent_seconds: int = 0, 
        passed_count: int = 0, 
        total_count: int = 0,
        tab_switch_count: int = 0,
        total_time_away_seconds: int = 0,
        last_switch_timestamp: Optional[str] = None,
        tab_switch_history: Optional[List[Dict[str, Any]]] = None
    ):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted_time = self.format_duration(time_spent_seconds)
        history_list = tab_switch_history or []

        if time_spent_seconds > 0:
            self.profile["total_coding_time_seconds"] = self.profile.get("total_coding_time_seconds", 0) + time_spent_seconds
            self.profile["total_debug_time_mins"] = round(self.profile.get("total_coding_time_seconds", 0) / 60)

        if status == "abandoned":
            self.profile.setdefault("activity_log", []).insert(0, {
                "action": "Abandoned Attempt",
                "problem": problem_id,
                "timestamp": now_str,
                "time_spent_seconds": time_spent_seconds,
                "time_spent": formatted_time,
                "tab_switch_count": tab_switch_count,
                "total_time_away_seconds": total_time_away_seconds,
                "last_switch_timestamp": last_switch_timestamp,
                "tab_switch_history": history_list
            })
            self.profile["activity_log"] = self.profile["activity_log"][:15]
            self._save_profile()
        elif status == "completed":
            self.record_attempt(
                problem_id=problem_id,
                topic=topic,
                passed=True,
                hints_used=0,
                time_spent_seconds=time_spent_seconds,
                session_status="completed",
                tab_switch_count=tab_switch_count,
                total_time_away_seconds=total_time_away_seconds,
                last_switch_timestamp=last_switch_timestamp,
                tab_switch_history=history_list
            )

    def record_mistake(self, topic: str, mistake_desc: str):
        self.profile["recent_mistakes"].insert(0, {
            "topic": topic,
            "mistake": mistake_desc,
            "time": "Just now"
        })
        self.profile["recent_mistakes"] = self.profile["recent_mistakes"][:6]
        self._save_profile()

    def record_viva(self, problem_id: str, scores: Dict[str, int]):
        self.profile["viva_history"].insert(0, {
            "problem_id": problem_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "overall_score": scores.get("overall", 0),
            "conceptual": scores.get("conceptual", 0),
            "code_understanding": scores.get("code_understanding", 0),
            "complexity": scores.get("complexity", 0),
            "communication": scores.get("communication", 0)
        })
        self.profile["viva_history"] = self.profile["viva_history"][:8]
        self._save_profile()

    def get_recommendations(self, all_problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies student weak areas and recommends optimal target problems."""
        # Find topics sorted ascending by mastery
        topic_mastery = self.profile.get("topic_mastery", {})
        sorted_topics = sorted(topic_mastery.items(), key=lambda item: item[1])
        weakest_topic = sorted_topics[0][0] if sorted_topics else "Dynamic Programming"
        second_weakest = sorted_topics[1][0] if len(sorted_topics) > 1 else "Recursion"

        recommendations = []
        for p in all_problems:
            if p["topic"] == weakest_topic:
                recommendations.append({
                    "problem": p,
                    "reason": f"Strengthen your lowest mastery topic: {weakest_topic} ({topic_mastery.get(weakest_topic, 50)}%)",
                    "priority": "High"
                })
            elif p["topic"] == second_weakest:
                recommendations.append({
                    "problem": p,
                    "reason": f"Follow-up practice for {second_weakest} ({topic_mastery.get(second_weakest, 50)}%)",
                    "priority": "Medium"
                })
        
        # If still few, add remaining
        if len(recommendations) < 3:
            for p in all_problems:
                if not any(r["problem"]["id"] == p["id"] for r in recommendations):
                    recommendations.append({
                        "problem": p,
                        "reason": f"Build breadth in {p['topic']}",
                        "priority": "Low"
                    })
                    if len(recommendations) >= 3:
                        break

        return recommendations
