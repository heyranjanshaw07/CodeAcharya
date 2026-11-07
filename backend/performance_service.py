import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from database import (
    get_db,
    format_timestamp_ist,
    parse_utc_timestamp,
    compute_date_range_bounds,
    IST_TZ,
    get_ist_now
)
from scoring_engine import calculate_independent_score
import auth

def format_duration_human(seconds: Optional[int]) -> str:
    """Formats seconds into readable format: e.g. '02h 15m 30s', '04m 20s', or '15s'."""
    if not seconds or seconds <= 0:
        return "0s"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m}m {s}s" if s > 0 else f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s" if s > 0 else f"{m}m"
    return f"{s}s"

def format_duration_clock(seconds: Optional[int]) -> str:
    """Formats seconds into clock format MM:SS or HH:MM:SS."""
    if not seconds or seconds <= 0:
        return "00:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def get_student_performance_data(
    user_id: str,
    date_filter: str = "all",
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes comprehensive, genuine performance metrics for the authenticated student
    strictly within the requested date range, converted to Asia/Kolkata (IST).
    Never fabricates historical data. Empty states are explicitly signaled.
    """
    utc_start, utc_end, reporting_period_label = compute_date_range_bounds(
        date_filter, start_date_str, end_date_str
    )

    # Recover any stale-running attempts prior to report generation
    auth.recover_stale_attempts(user_id)

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Fetch Student User Details
        cursor.execute("SELECT id, email, full_name, created_at FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            raise ValueError("Student record not found.")

        user_info = {
            "id": user_row["id"],
            "email": user_row["email"],
            "full_name": user_row["full_name"],
            "joined_at_ist": format_timestamp_ist(user_row["created_at"])
        }

        # 2. Fetch ALL raw coding attempts for this user sorted chronologically to establish attempt numbers per question
        cursor.execute("""
            SELECT 
                a.id as attempt_id,
                a.user_id,
                a.question_id,
                a.language,
                a.attempt_status,
                a.start_time,
                a.end_time,
                a.elapsed_coding_time_seconds,
                a.is_completed,
                a.passed_count,
                a.total_count,
                a.test_results_summary,
                a.overall_score as attempt_score,
                a.score_breakdown,
                a.evaluator_type,
                a.unique_hints_used as attempt_hints,
                a.independent_score as attempt_indep_score,
                a.created_at,
                q.title as question_title,
                q.topic as question_topic,
                q.difficulty as question_difficulty,
                s.id as score_id,
                s.overall_score as evaluated_score,
                s.correctness_score,
                s.correctness_max,
                s.complexity_score,
                s.complexity_max,
                s.quality_score,
                s.quality_max,
                s.approach_score,
                s.approach_max,
                s.independent_score as score_indep,
                s.independent_max as score_indep_max,
                s.unique_hints_used as score_hints,
                s.memory_usage_mb,
                s.execution_time_ms,
                s.breakdown_json,
                s.feedback_json,
                s.tab_away_seconds
            FROM coding_attempts a
            JOIN coding_questions q ON a.question_id = q.id
            LEFT JOIN coding_scores s ON a.id = s.attempt_id
            WHERE a.user_id = ?
            ORDER BY a.start_time ASC, a.created_at ASC
        """, (user_id,))
        all_attempts_rows = cursor.fetchall()

        # Group attempts by question to track cumulative attempt sequence (Attempt #1, #2...)
        question_attempt_counter: Dict[str, int] = {}
        all_processed_attempts: List[Dict[str, Any]] = []

        for row in all_attempts_rows:
            qid = row["question_id"]
            question_attempt_counter[qid] = question_attempt_counter.get(qid, 0) + 1
            att_seq = question_attempt_counter[qid]

            # Determine timestamp
            raw_start = row["start_time"] or row["created_at"]
            start_dt = parse_utc_timestamp(raw_start)
            raw_end = row["end_time"]
            end_dt = parse_utc_timestamp(raw_end) if raw_end else None

            # Test summary parsing
            test_summary = {}
            if row["test_results_summary"]:
                try:
                    test_summary = json.loads(row["test_results_summary"])
                except Exception:
                    pass

            # Hints used
            u_hints = (
                row["score_hints"]
                if row["score_hints"] is not None
                else (row["attempt_hints"] if row["attempt_hints"] is not None else test_summary.get("unique_hints_used", 0))
            ) or 0

            # Independent score calculation using configured hint curve
            indep_score = calculate_independent_score(u_hints)
            if row["score_indep"] is not None:
                indep_score = float(row["score_indep"])
            elif row["attempt_indep_score"] is not None:
                indep_score = float(row["attempt_indep_score"])

            # Overall Score
            overall_score = None
            if row["evaluated_score"] is not None:
                overall_score = round(float(row["evaluated_score"]), 1)
            elif row["attempt_score"] is not None and float(row["attempt_score"]) > 0:
                overall_score = round(float(row["attempt_score"]), 1)
            elif test_summary.get("overall_score") is not None and float(test_summary["overall_score"]) > 0:
                overall_score = round(float(test_summary["overall_score"]), 1)

            # Score Breakdown
            breakdown = {}
            if row["breakdown_json"]:
                try:
                    breakdown = json.loads(row["breakdown_json"])
                except Exception:
                    pass
            elif row["score_breakdown"]:
                try:
                    breakdown = json.loads(row["score_breakdown"])
                except Exception:
                    pass

            # Execution time & Memory
            exec_ms = row["execution_time_ms"]
            mem_mb = row["memory_usage_mb"]

            # Tab switches and time away
            switches = test_summary.get("tab_switch_count", 0)
            away_secs = (
                row["tab_away_seconds"]
                if row["tab_away_seconds"] is not None and row["tab_away_seconds"] > 0
                else test_summary.get("total_time_away_seconds", 0)
            )

            # Pass counts & status
            passed_cnt = row["passed_count"] or 0
            total_cnt = row["total_count"] or 0

            # Normalized attempt status: completed, failed, abandoned, paused, running
            status_val = (row["attempt_status"] or ("completed" if row["is_completed"] else "running")).lower().strip()
            
            # Strict completion check: must pass all test cases if total_cnt > 0
            is_completed = (status_val == "completed" or bool(row["is_completed"])) and (passed_cnt == total_cnt and total_cnt > 0)
            if status_val in ("running", "paused"):
                is_completed = False
            elif status_val == "completed" and not is_completed:
                status_val = "failed"
            elif status_val not in ("completed", "failed", "abandoned", "paused", "running"):
                status_val = "completed" if is_completed else ("failed" if total_cnt > 0 else "running")

            # Determine IST start and end timestamps
            start_time_ist = format_timestamp_ist(raw_start)
            if status_val in ("running", "paused"):
                end_time_ist = "In progress"
            elif status_val == "abandoned":
                end_time_ist = "Abandoned"
            elif not raw_end:
                end_time_ist = "N/A"
            else:
                duration_s = row["elapsed_coding_time_seconds"] or 0
                if start_dt and end_dt and start_dt == end_dt and duration_s > 0:
                    computed_end = start_dt + timedelta(seconds=duration_s + (away_secs or 0))
                    end_time_ist = format_timestamp_ist(computed_end)
                else:
                    end_time_ist = format_timestamp_ist(raw_end) if raw_end else "N/A"

            all_processed_attempts.append({
                "attempt_id": row["attempt_id"],
                "question_id": qid,
                "question_title": row["question_title"],
                "topic": row["question_topic"],
                "difficulty": row["question_difficulty"],
                "language": (row["language"] or "python").lower(),
                "attempt_number": att_seq,
                "attempt_status": status_val,
                "is_completed": is_completed,
                "is_provisional": (status_val != "completed"),
                "start_time": raw_start,
                "start_time_dt": start_dt,
                "start_time_ist": start_time_ist,
                "end_time": raw_end if status_val not in ("running", "paused", "abandoned") else None,
                "end_time_ist": end_time_ist,
                "coding_duration_seconds": row["elapsed_coding_time_seconds"] or 0,
                "coding_duration_formatted": format_duration_clock(row["elapsed_coding_time_seconds"] or 0),
                "execution_time_ms": round(float(exec_ms), 2) if exec_ms is not None and exec_ms > 0 else None,
                "memory_usage_mb": round(float(mem_mb), 2) if mem_mb is not None and mem_mb > 0 else None,
                "passed_count": passed_cnt,
                "total_count": total_cnt,
                "pass_rate_percentage": round((passed_cnt / max(1, total_cnt)) * 100, 1) if total_cnt > 0 else None,
                "overall_score": overall_score,
                "score_breakdown": breakdown,
                "unique_hints_used": u_hints,
                "independent_score": indep_score,
                "tab_switch_count": switches,
                "time_away_seconds": away_secs,
                "time_away_formatted": format_duration_human(away_secs),
                "created_at": row["created_at"],
                "evaluator_type": row["evaluator_type"] or "automated"
            })

        # 3. Filter attempts by the date range
        filtered_attempts: List[Dict[str, Any]] = []
        for att in all_processed_attempts:
            dt = att["start_time_dt"]
            if not dt:
                filtered_attempts.append(att)
                continue
            if utc_start and dt < utc_start:
                continue
            if utc_end and dt > utc_end:
                continue
            filtered_attempts.append(att)

        # 4. Fetch Tab Switch Events for the user
        cursor.execute("""
            SELECT id, attempt_id, question_id, event_timestamp, return_timestamp, time_away_seconds, event_status
            FROM tab_switch_events
            WHERE user_id = ?
            ORDER BY event_timestamp ASC
        """, (user_id,))
        raw_tab_switches = cursor.fetchall()

        filtered_tab_events: List[Dict[str, Any]] = []
        tab_switches_by_attempt: Dict[str, List[Dict[str, Any]]] = {}

        # Build mapping of question_id to title
        q_titles = {row["question_id"]: row["question_title"] for row in all_attempts_rows}

        switch_seq = 1
        for ts_row in raw_tab_switches:
            ev_ts = ts_row["event_timestamp"]
            ev_dt = parse_utc_timestamp(ev_ts)
            if ev_dt and utc_start and ev_dt < utc_start:
                continue
            if ev_dt and utc_end and ev_dt > utc_end:
                continue

            att_id = ts_row["attempt_id"]
            q_id = ts_row["question_id"]
            ret_ts = ts_row["return_timestamp"]
            raw_status = (ts_row["event_status"] or "").lower().strip()

            ev_parsed = parse_utc_timestamp(ev_ts) if ev_ts else None
            ret_parsed = parse_utc_timestamp(ret_ts) if ret_ts else None
            is_legacy_unrecorded = False

            if not ret_ts or raw_status in ("incomplete", "away", "active"):
                status_ts = "incomplete" if raw_status not in ("away", "active") else raw_status
                ret_ist = "Awaiting return"
                away_s = 0
                dur_formatted = "Incomplete"
            elif (ev_parsed and ret_parsed and abs((ret_parsed - ev_parsed).total_seconds()) < 1 and (ts_row["time_away_seconds"] or 0) == 0) or raw_status == "historical_unrecorded":
                # Historical records with identical hidden and return timestamps have unrecoverable duration
                status_ts = "historical_unrecorded"
                ret_ist = format_timestamp_ist(ret_ts)
                away_s = 0
                dur_formatted = "N/A"
                is_legacy_unrecorded = True
            else:
                status_ts = "returned"
                ret_ist = format_timestamp_ist(ret_ts)
                if ev_parsed and ret_parsed:
                    diff_sec = max(0.0, (ret_parsed - ev_parsed).total_seconds())
                    away_s = max(0, int(round(diff_sec)))
                else:
                    away_s = max(0, int(round(float(ts_row["time_away_seconds"] or 0))))
                dur_formatted = format_duration_human(away_s)

            event_obj = {
                "switch_number": switch_seq,
                "id": ts_row["id"],
                "attempt_id": att_id,
                "question_id": q_id,
                "question_title": q_titles.get(q_id, (q_id.replace("-", " ").title() if q_id else "General IDE")),
                "date_ist": format_timestamp_ist(ev_ts).split(" ")[0] if format_timestamp_ist(ev_ts) else "N/A",
                "hidden_time_ist": format_timestamp_ist(ev_ts),
                "return_time_ist": ret_ist,
                "duration_away_seconds": away_s,
                "duration_away_formatted": dur_formatted,
                "status": status_ts,
                "is_unrecorded": is_legacy_unrecorded
            }
            switch_seq += 1
            filtered_tab_events.append(event_obj)

            if att_id:
                tab_switches_by_attempt.setdefault(att_id, []).append(event_obj)

        # Attach detailed tab-switch history to each attempt record and synchronize attempt away metrics
        for att in filtered_attempts:
            att_events = tab_switches_by_attempt.get(att["attempt_id"], [])
            att["tab_switch_history"] = att_events
            if att_events:
                att["tab_switch_count"] = len(att_events)
                att["time_away_seconds"] = sum(e["duration_away_seconds"] for e in att_events if e["duration_away_seconds"] > 0)
                att["time_away_formatted"] = format_duration_human(att["time_away_seconds"])

        # 5. Fetch AI Viva sessions
        cursor.execute("""
            SELECT id, question_id, attempt_id, questions_asked, student_answers,
                   overall_score, conceptual_score, code_understanding_score,
                   complexity_score, communication_score, evaluation_results, completed_at
            FROM ai_viva_results
            WHERE user_id = ?
            ORDER BY completed_at DESC
        """, (user_id,))
        raw_viva_rows = cursor.fetchall()

        filtered_viva_sessions: List[Dict[str, Any]] = []
        for v_row in raw_viva_rows:
            v_ts = v_row["completed_at"]
            v_dt = parse_utc_timestamp(v_ts)
            if v_dt and utc_start and v_dt < utc_start:
                continue
            if v_dt and utc_end and v_dt > utc_end:
                continue

            v_qid = v_row["question_id"]
            eval_dict = {}
            if v_row["evaluation_results"]:
                try:
                    eval_dict = json.loads(v_row["evaluation_results"])
                except Exception:
                    pass

            filtered_viva_sessions.append({
                "id": v_row["id"],
                "question_id": v_qid,
                "question_title": q_titles.get(v_qid, v_qid.replace("-", " ").title()),
                "attempt_id": v_row["attempt_id"],
                "overall_score": v_row["overall_score"] or 0,
                "conceptual_score": v_row["conceptual_score"],
                "code_understanding_score": v_row["code_understanding_score"],
                "complexity_score": v_row["complexity_score"],
                "communication_score": v_row["communication_score"],
                "completed_at": v_ts,
                "completed_at_ist": format_timestamp_ist(v_ts),
                "feedback_summary": eval_dict.get("feedback") or eval_dict.get("examinerRemarks") or "Viva evaluation completed successfully."
            })

        # 6. Fetch Session Lock and Proctoring Events
        cursor.execute("""
            SELECT id, attempt_id, question_id, event_type, event_timestamp, event_timestamp_ist, metadata_json, created_at
            FROM session_lock_events
            WHERE user_id = ?
            ORDER BY event_timestamp ASC
        """, (user_id,))
        raw_lock_rows = cursor.fetchall()

        filtered_lock_events: List[Dict[str, Any]] = []
        for l_row in raw_lock_rows:
            l_ts = l_row["event_timestamp"]
            l_dt = parse_utc_timestamp(l_ts)
            if l_dt and utc_start and l_dt < utc_start:
                continue
            if l_dt and utc_end and l_dt > utc_end:
                continue

            meta = {}
            if l_row["metadata_json"]:
                try:
                    meta = json.loads(l_row["metadata_json"])
                except Exception:
                    pass

            filtered_lock_events.append({
                "id": l_row["id"],
                "attempt_id": l_row["attempt_id"],
                "question_id": l_row["question_id"],
                "question_title": q_titles.get(l_row["question_id"], (l_row["question_id"] or "General Practice").replace("-", " ").title()),
                "event_type": l_row["event_type"],
                "event_timestamp": l_ts,
                "event_timestamp_ist": l_row["event_timestamp_ist"] or format_timestamp_ist(l_ts),
                "metadata": meta,
                "created_at": l_row["created_at"]
            })

        # 7. Calculate Aggregated Summary Statistics
        total_attempts = len(filtered_attempts)
        completed_attempts = sum(1 for a in filtered_attempts if a["attempt_status"] == "completed")
        failed_attempts = sum(1 for a in filtered_attempts if a["attempt_status"] == "failed")
        abandoned_attempts = sum(1 for a in filtered_attempts if a["attempt_status"] == "abandoned")
        running_attempts = sum(1 for a in filtered_attempts if a["attempt_status"] == "running")
        paused_attempts = sum(1 for a in filtered_attempts if a["attempt_status"] == "paused")
        other_attempts = running_attempts + paused_attempts

        # Solved unique questions
        solved_qids = set(a["question_id"] for a in filtered_attempts if a["is_completed"])
        total_unique_solved = len(solved_qids)

        # Mark each attempt if that question is solved
        for a in filtered_attempts:
            a["is_question_solved"] = a["question_id"] in solved_qids

        # Coding Score stats
        scored_attempts = [a["overall_score"] for a in filtered_attempts if a["overall_score"] is not None]
        avg_coding_score = round(sum(scored_attempts) / len(scored_attempts), 1) if scored_attempts else None
        best_coding_score = round(max(scored_attempts), 1) if scored_attempts else None

        completed_scored = [a["overall_score"] for a in filtered_attempts if a["is_completed"] and a["overall_score"] is not None]
        avg_completed_score = round(sum(completed_scored) / len(completed_scored), 1) if completed_scored else None

        # Coding duration stats
        total_active_coding_seconds = sum(a["coding_duration_seconds"] for a in filtered_attempts)
        completed_durations = [a["coding_duration_seconds"] for a in filtered_attempts if a["is_completed"]]
        avg_coding_time_completed = (
            round(sum(completed_durations) / len(completed_durations), 1) if completed_durations else 0.0
        )

        # Unique hints used
        total_unique_hints_used = sum(a["unique_hints_used"] for a in filtered_attempts)

        # Tab switches and total time away: strictly calculated from the persisted events shown in detailed table
        total_tab_switches = len(filtered_tab_events)
        total_time_away_seconds = sum(e["duration_away_seconds"] for e in filtered_tab_events if e.get("duration_away_seconds", 0) > 0)

        # Pass rate stats: based on actual executed test results
        sum_passed = sum(a["passed_count"] for a in filtered_attempts)
        sum_total = sum(a["total_count"] for a in filtered_attempts)
        pass_rate = round((sum_passed / sum_total) * 100, 1) if sum_total > 0 else 0.0

        # Viva performance stats
        viva_count = len(filtered_viva_sessions)
        avg_viva_score = (
            round(sum(v["overall_score"] for v in filtered_viva_sessions) / viva_count, 1)
            if viva_count > 0
            else None
        )
        best_viva_score = (
            max(v["overall_score"] for v in filtered_viva_sessions)
            if viva_count > 0
            else None
        )

        # 7. Generate Visualizations & Trend Datasets
        # Chronological score trend
        score_over_time = [
            {
                "timestamp_ist": a["start_time_ist"],
                "score": a["overall_score"],
                "question_title": a["question_title"],
                "attempt_number": a["attempt_number"]
            }
            for a in filtered_attempts
            if a["overall_score"] is not None
        ]

        # Coding time per question
        coding_time_per_question = [
            {
                "question_id": a["question_id"],
                "question_title": a["question_title"],
                "seconds": a["coding_duration_seconds"],
                "formatted": a["coding_duration_formatted"],
                "status": a["attempt_status"],
                "attempt_number": a["attempt_number"]
            }
            for a in filtered_attempts
        ]

        # Topic-wise accuracy & average score
        topic_groups: Dict[str, List[Dict[str, Any]]] = {}
        for a in filtered_attempts:
            t = a["topic"]
            topic_groups.setdefault(t, []).append(a)

        topic_accuracy = []
        for topic, atts in topic_groups.items():
            t_passed = sum(x["passed_count"] for x in atts)
            t_total = sum(x["total_count"] for x in atts)
            t_acc = round((t_passed / max(1, t_total)) * 100, 1) if t_total > 0 else 0.0
            t_scored = [x["overall_score"] for x in atts if x["overall_score"] is not None]
            t_avg_s = round(sum(t_scored) / len(t_scored), 1) if t_scored else 0.0
            t_solved = len(set(x["question_id"] for x in atts if x["is_completed"]))
            topic_accuracy.append({
                "topic": topic,
                "attempts_count": len(atts),
                "unique_solved": t_solved,
                "pass_rate_percentage": t_acc,
                "average_score": t_avg_s
            })

        # Hints used per question
        hints_per_question = [
            {
                "question_title": a["question_title"],
                "hints_used": a["unique_hints_used"],
                "independent_score": a["independent_score"],
                "attempt_number": a["attempt_number"]
            }
            for a in filtered_attempts
        ]

        # Tab switches per attempt
        tab_switches_per_attempt = [
            {
                "question_title": a["question_title"],
                "attempt_number": a["attempt_number"],
                "tab_switch_count": a["tab_switch_count"],
                "time_away_seconds": a["time_away_seconds"]
            }
            for a in filtered_attempts
        ]

        # Repeated attempts progress
        by_question: Dict[str, List[Dict[str, Any]]] = {}
        for a in filtered_attempts:
            by_question.setdefault(a["question_id"], []).append(a)

        repeated_progress = []
        for qid, q_atts in by_question.items():
            if len(q_atts) > 1:
                repeated_progress.append({
                    "question_id": qid,
                    "question_title": q_atts[0]["question_title"],
                    "attempts": [
                        {
                            "attempt_number": x["attempt_number"],
                            "score": x["overall_score"],
                            "status": x["attempt_status"],
                            "coding_duration_seconds": x["coding_duration_seconds"],
                            "date_ist": x["start_time_ist"]
                        }
                        for x in q_atts
                    ]
                })

        # Performance by Difficulty
        difficulty_stats = {}
        for diff in ("Easy", "Medium", "Hard"):
            diff_atts = [a for a in filtered_attempts if a["difficulty"] == diff]
            d_pass = sum(x["passed_count"] for x in diff_atts)
            d_tot = sum(x["total_count"] for x in diff_atts)
            d_rate = round((d_pass / max(1, d_tot)) * 100, 1) if d_tot > 0 else 0.0
            d_scored = [x["overall_score"] for x in diff_atts if x["overall_score"] is not None]
            d_avg = round(sum(d_scored) / len(d_scored), 1) if d_scored else 0.0
            difficulty_stats[diff] = {
                "attempts": len(diff_atts),
                "average_score": d_avg,
                "pass_rate_percentage": d_rate
            }

        # AI Viva trends
        viva_trends = [
            {
                "date_ist": v["completed_at_ist"],
                "question_title": v["question_title"],
                "overall_score": v["overall_score"],
                "conceptual": v["conceptual_score"],
                "code_understanding": v["code_understanding_score"],
                "complexity": v["complexity_score"],
                "communication": v["communication_score"]
            }
            for v in filtered_viva_sessions
        ]

        summary = {
            "total_unique_solved": total_unique_solved,
            "total_attempts": total_attempts,
            "completed_attempts": completed_attempts,
            "failed_attempts": failed_attempts,
            "abandoned_attempts": abandoned_attempts,
            "running_attempts": running_attempts,
            "paused_attempts": paused_attempts,
            "other_attempts": other_attempts,
            "average_coding_score": avg_coding_score,
            "average_completed_coding_score": avg_completed_score,
            "score_calculation_method": "All Evaluated Attempts (mean of all evaluated attempts in period)",
            "best_coding_score": best_coding_score,
            "total_active_coding_time_seconds": total_active_coding_seconds,
            "total_active_coding_time_formatted": format_duration_human(total_active_coding_seconds),
            "avg_coding_time_completed_seconds": avg_coding_time_completed,
            "avg_coding_time_completed_formatted": format_duration_human(round(avg_coding_time_completed)),
            "total_unique_hints_used": total_unique_hints_used,
            "total_tab_switches": total_tab_switches,
            "total_time_away_seconds": total_time_away_seconds,
            "total_time_away_formatted": format_duration_human(total_time_away_seconds),
            "overall_pass_rate_percentage": pass_rate,
            "total_test_cases_passed": sum_passed,
            "total_test_cases_evaluated": sum_total,
            "viva": {
                "sessions_count": viva_count,
                "average_score": avg_viva_score,
                "best_score": best_viva_score
            }
        }

        return {
            "date_filter": date_filter,
            "reporting_period_label": reporting_period_label,
            "user_info": user_info,
            "summary": summary,
            "questions_performance": list(reversed(filtered_attempts)),  # most recent attempts first
            "tab_switch_events": list(reversed(filtered_tab_events)),
            "session_lock_events": list(reversed(filtered_lock_events)),
            "viva_sessions": filtered_viva_sessions,
            "charts": {
                "score_over_time": score_over_time,
                "coding_time_per_question": coding_time_per_question,
                "topic_accuracy": topic_accuracy,
                "hints_per_question": hints_per_question,
                "tab_switches_per_attempt": tab_switches_per_attempt,
                "repeated_progress": repeated_progress,
                "difficulty_breakdown": difficulty_stats,
                "viva_trends": viva_trends
            }
        }
