import sqlite3
import os
import json
import secrets
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "codeacharya.db")
_db_lock = threading.Lock()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Conversion helper for UTC to Asia/Kolkata (IST = UTC + 05:30)
IST_OFFSET = timedelta(hours=5, minutes=30)
IST_TZ = timezone(IST_OFFSET, name="IST")

def utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def parse_utc_timestamp(utc_iso_or_str: Optional[Any]) -> Optional[datetime]:
    """Parses an ISO, epoch, datetime object, or IST timestamp string into a timezone-aware UTC datetime."""
    if utc_iso_or_str is None:
        return None
    if isinstance(utc_iso_or_str, datetime):
        if utc_iso_or_str.tzinfo is None:
            return utc_iso_or_str.replace(tzinfo=timezone.utc)
        return utc_iso_or_str.astimezone(timezone.utc)
    try:
        clean = str(utc_iso_or_str).strip()
        if not clean or clean.lower() in ("none", "null", "n/a", "in progress"):
            return None

        # Check for numeric epoch (seconds or milliseconds)
        if clean.isdigit() or (clean.startswith("-") and clean[1:].isdigit()):
            num = int(clean)
            if num > 1e11:  # Milliseconds timestamp
                return datetime.fromtimestamp(num / 1000.0, tz=timezone.utc)
            return datetime.fromtimestamp(num, tz=timezone.utc)

        # Check for existing IST suffix
        if clean.endswith(" IST"):
            clean_core = clean[:-4].strip()
            # Try common formats
            for fmt in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%d %b %Y, %I:%M:%S %p",
                "%d %b %Y %H:%M:%S",
                "%I:%M:%S %p"
            ):
                try:
                    dt_naive = datetime.strptime(clean_core, fmt)
                    if fmt == "%I:%M:%S %p":
                        today = get_ist_now().date()
                        dt_naive = datetime.combine(today, dt_naive.time())
                    return dt_naive.replace(tzinfo=IST_TZ).astimezone(timezone.utc)
                except Exception:
                    pass
            try:
                dt = datetime.fromisoformat(clean_core)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=IST_TZ)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass

        # Try standard ISO
        if clean.endswith("Z"):
            clean = clean[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(clean)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass

        # Try other standard date/time formats
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
            "%d %b %Y, %I:%M:%S %p",
            "%d %b %Y %H:%M:%S",
            "%I:%M:%S %p"
        ):
            try:
                dt_naive = datetime.strptime(clean, fmt)
                if fmt == "%I:%M:%S %p":
                    today = get_ist_now().date()
                    dt_naive = datetime.combine(today, dt_naive.time())
                return dt_naive.replace(tzinfo=timezone.utc)
            except Exception:
                pass
        return None
    except Exception:
        return None

def get_ist_now() -> datetime:
    """Returns current datetime in Asia/Kolkata timezone."""
    return datetime.now(timezone.utc).astimezone(IST_TZ)

def compute_date_range_bounds(
    filter_type: str,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None
) -> Tuple[Optional[datetime], Optional[datetime], str]:
    """
    Computes exact UTC start and end datetime bounds for dashboard & PDF filters based on Asia/Kolkata timezone.
    Returns: (utc_start_datetime, utc_end_datetime, human_readable_ist_label)
    """
    now_ist = get_ist_now()
    today_ist = now_ist.date()

    clean_filter = (filter_type or "all").lower().strip()

    if clean_filter in ("today", "day"):
        start_ist = datetime(today_ist.year, today_ist.month, today_ist.day, 0, 0, 0, tzinfo=IST_TZ)
        end_ist = datetime(today_ist.year, today_ist.month, today_ist.day, 23, 59, 59, 999999, tzinfo=IST_TZ)
        ist_label = f"Today ({start_ist.strftime('%d %b %Y')} IST)"
    elif clean_filter in ("last_7_days", "7days", "week"):
        s_date = today_ist - timedelta(days=6)
        start_ist = datetime(s_date.year, s_date.month, s_date.day, 0, 0, 0, tzinfo=IST_TZ)
        end_ist = datetime(today_ist.year, today_ist.month, today_ist.day, 23, 59, 59, 999999, tzinfo=IST_TZ)
        ist_label = f"Last 7 Days ({start_ist.strftime('%d %b')} - {end_ist.strftime('%d %b %Y')} IST)"
    elif clean_filter in ("last_30_days", "30days", "month30"):
        s_date = today_ist - timedelta(days=29)
        start_ist = datetime(s_date.year, s_date.month, s_date.day, 0, 0, 0, tzinfo=IST_TZ)
        end_ist = datetime(today_ist.year, today_ist.month, today_ist.day, 23, 59, 59, 999999, tzinfo=IST_TZ)
        ist_label = f"Last 30 Days ({start_ist.strftime('%d %b')} - {end_ist.strftime('%d %b %Y')} IST)"
    elif clean_filter in ("this_month", "current_month"):
        start_ist = datetime(today_ist.year, today_ist.month, 1, 0, 0, 0, tzinfo=IST_TZ)
        end_ist = datetime(today_ist.year, today_ist.month, today_ist.day, 23, 59, 59, 999999, tzinfo=IST_TZ)
        ist_label = f"This Month ({start_ist.strftime('%d %b')} - {end_ist.strftime('%d %b %Y')} IST)"
    elif clean_filter in ("previous_month", "last_month"):
        first_this_month = datetime(today_ist.year, today_ist.month, 1, 0, 0, 0, tzinfo=IST_TZ)
        last_prev_month = first_this_month - timedelta(days=1)
        start_ist = datetime(last_prev_month.year, last_prev_month.month, 1, 0, 0, 0, tzinfo=IST_TZ)
        end_ist = datetime(last_prev_month.year, last_prev_month.month, last_prev_month.day, 23, 59, 59, 999999, tzinfo=IST_TZ)
        ist_label = f"Previous Month ({start_ist.strftime('%d %b')} - {end_ist.strftime('%d %b %Y')} IST)"
    elif clean_filter == "custom":
        if not start_date_str or not end_date_str:
            raise ValueError("Custom date range requires valid 'start_date' and 'end_date' in YYYY-MM-DD format.")
        try:
            s_d = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
            e_d = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {str(e)}")
        if s_d > e_d:
            raise ValueError("Invalid date range: start_date cannot be later than end_date.")
        start_ist = datetime(s_d.year, s_d.month, s_d.day, 0, 0, 0, tzinfo=IST_TZ)
        end_ist = datetime(e_d.year, e_d.month, e_d.day, 23, 59, 59, 999999, tzinfo=IST_TZ)
        ist_label = f"Custom: {start_ist.strftime('%d %b %Y')} - {end_ist.strftime('%d %b %Y')} (IST)"
    elif clean_filter in ("all", "all_time", ""):
        return None, None, "All Time (IST)"
    else:
        raise ValueError(f"Unsupported date filter '{filter_type}'. Allowed values: today, last_7_days, last_30_days, this_month, previous_month, custom, all.")

    utc_start = start_ist.astimezone(timezone.utc)
    utc_end = end_ist.astimezone(timezone.utc)
    return utc_start, utc_end, ist_label

def format_timestamp_ist(utc_iso_or_str: Optional[Any]) -> Optional[str]:
    """Converts a UTC ISO or epoch string to an Asia/Kolkata (IST) human-readable format without double-offsetting."""
    if utc_iso_or_str is None:
        return None
    try:
        clean_str = str(utc_iso_or_str).strip()
        if not clean_str:
            return None

        # If already formatted as 'YYYY-MM-DD HH:MM:SS IST', return directly to prevent double offset
        if clean_str.endswith(" IST") and len(clean_str.split()) == 3:
            try:
                datetime.strptime(clean_str[:-4], "%Y-%m-%d %H:%M:%S")
                return clean_str
            except Exception:
                pass

        dt = parse_utc_timestamp(clean_str)
        if dt is not None:
            ist_dt = dt.astimezone(IST_TZ)
            return ist_dt.strftime("%Y-%m-%d %H:%M:%S IST")
        return clean_str
    except Exception:
        return str(utc_iso_or_str)

def init_database():
    """
    Initializes and migrates the normalized CodeAcharya database schema.
    Applies non-destructive alterations for existing deployments.
    """
    with _db_lock:
        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    auth_provider TEXT NOT NULL DEFAULT 'local',
                    provider_subject_id TEXT,
                    password_hash TEXT,
                    account_status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TIMESTAMP
                )
            """)

            # Safe migration for existing users table columns
            cursor.execute("PRAGMA table_info(users)")
            existing_user_cols = {row["name"] for row in cursor.fetchall()}
            if "auth_provider" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT NOT NULL DEFAULT 'local'")
            if "provider_subject_id" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN provider_subject_id TEXT")
            if "account_status" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN account_status TEXT NOT NULL DEFAULT 'active'")
            if "last_login_at" not in existing_user_cols:
                cursor.execute("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP")

            # 2. Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_remember_me INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("PRAGMA table_info(sessions)")
            existing_session_cols = {row["name"] for row in cursor.fetchall()}
            if "is_remember_me" not in existing_session_cols:
                cursor.execute("ALTER TABLE sessions ADD COLUMN is_remember_me INTEGER DEFAULT 0")

            # 3. Coding Questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coding_questions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    subtopic TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    supported_languages TEXT DEFAULT '["python","c","cpp","java"]',
                    starter_code TEXT DEFAULT '{}',
                    test_cases TEXT DEFAULT '[]',
                    learning_objectives TEXT DEFAULT '[]',
                    common_misconceptions TEXT DEFAULT '[]',
                    input_format TEXT DEFAULT '',
                    output_format TEXT DEFAULT '',
                    hint TEXT DEFAULT '',
                    progressive_hints TEXT DEFAULT '[]',
                    explanation TEXT DEFAULT '',
                    expected_solution TEXT DEFAULT '{}',
                    time_complexity TEXT DEFAULT '',
                    space_complexity TEXT DEFAULT '',
                    relevant_concepts TEXT DEFAULT '[]',
                    is_generated INTEGER DEFAULT 0,
                    source TEXT DEFAULT 'curated',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 4. Coding Attempts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coding_attempts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    attempt_status TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    elapsed_coding_time_seconds INTEGER DEFAULT 0,
                    is_completed INTEGER DEFAULT 0,
                    passed_count INTEGER DEFAULT 0,
                    total_count INTEGER DEFAULT 0,
                    code TEXT DEFAULT '',
                    test_results_summary TEXT DEFAULT '{}',
                    overall_score REAL DEFAULT 0.0,
                    score_breakdown TEXT DEFAULT '{}',
                    evaluator_type TEXT DEFAULT 'automated',
                    idempotency_key TEXT,
                    unique_hints_used INTEGER DEFAULT 0,
                    independent_score REAL DEFAULT 10.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES coding_questions(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("PRAGMA table_info(coding_attempts)")
            existing_attempt_cols = {row["name"] for row in cursor.fetchall()}
            if "overall_score" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN overall_score REAL DEFAULT 0.0")
            if "score_breakdown" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN score_breakdown TEXT DEFAULT '{}'")
            if "evaluator_type" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN evaluator_type TEXT DEFAULT 'automated'")
            if "idempotency_key" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN idempotency_key TEXT")
            if "unique_hints_used" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN unique_hints_used INTEGER DEFAULT 0")
            if "independent_score" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN independent_score REAL DEFAULT 10.0")
            if "paused_seconds" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN paused_seconds INTEGER DEFAULT 0")
            if "last_activity_at" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN last_activity_at TIMESTAMP")
            if "is_locked" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN is_locked INTEGER DEFAULT 0")
            if "lock_reason" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN lock_reason TEXT DEFAULT ''")
            if "last_locked_at" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN last_locked_at TIMESTAMP")
            if "last_unlocked_at" not in existing_attempt_cols:
                cursor.execute("ALTER TABLE coding_attempts ADD COLUMN last_unlocked_at TIMESTAMP")

            # 5. Tab Switch Events table (IST Asia/Kolkata compliant)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tab_switch_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    attempt_id TEXT,
                    question_id TEXT,
                    event_timestamp TIMESTAMP NOT NULL,
                    return_timestamp TIMESTAMP,
                    time_away_seconds INTEGER DEFAULT 0,
                    event_status TEXT DEFAULT 'returned',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (attempt_id) REFERENCES coding_attempts(id) ON DELETE SET NULL
                )
            """)

            # 6. Test Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id TEXT PRIMARY KEY,
                    attempt_id TEXT NOT NULL,
                    test_case_id INTEGER NOT NULL,
                    is_hidden INTEGER DEFAULT 0,
                    passed INTEGER NOT NULL,
                    execution_time_ms REAL DEFAULT 0.0,
                    safe_error_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (attempt_id) REFERENCES coding_attempts(id) ON DELETE CASCADE
                )
            """)

            # 7. Student Progress table (Derived metrics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student_progress (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    attempts_completed INTEGER DEFAULT 0,
                    problems_solved INTEGER DEFAULT 0,
                    mastery_percentage INTEGER DEFAULT 0,
                    last_activity_timestamp TIMESTAMP,
                    UNIQUE(user_id, topic),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # 8. AI Viva Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_viva_results (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    attempt_id TEXT,
                    questions_asked TEXT DEFAULT '[]',
                    student_answers TEXT DEFAULT '[]',
                    overall_score INTEGER DEFAULT 0,
                    conceptual_score INTEGER DEFAULT 0,
                    code_understanding_score INTEGER DEFAULT 0,
                    complexity_score INTEGER DEFAULT 0,
                    communication_score INTEGER DEFAULT 0,
                    evaluation_results TEXT DEFAULT '{}',
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (attempt_id) REFERENCES coding_attempts(id) ON DELETE SET NULL
                )
            """)

            # 9. Coding Scores table (Detailed Performance & Evaluation Persistence)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coding_scores (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    attempt_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    correctness_score REAL NOT NULL,
                    correctness_max REAL NOT NULL,
                    complexity_score REAL,
                    complexity_max REAL,
                    quality_score REAL,
                    quality_max REAL,
                    approach_score REAL,
                    approach_max REAL,
                    independent_score REAL DEFAULT 10.0,
                    independent_max REAL DEFAULT 10.0,
                    unique_hints_used INTEGER DEFAULT 0,
                    code_snapshot TEXT DEFAULT '',
                    memory_usage_mb REAL DEFAULT 0.0,
                    is_renormalized INTEGER DEFAULT 0,
                    evaluator_type TEXT NOT NULL,
                    breakdown_json TEXT NOT NULL,
                    feedback_json TEXT NOT NULL,
                    execution_time_ms REAL DEFAULT 0.0,
                    coding_time_seconds INTEGER DEFAULT 0,
                    tab_away_seconds INTEGER DEFAULT 0,
                    passed_count INTEGER NOT NULL,
                    total_count INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    idempotency_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (attempt_id) REFERENCES coding_attempts(id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES coding_questions(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("PRAGMA table_info(coding_scores)")
            existing_score_cols = {row["name"] for row in cursor.fetchall()}
            if "independent_score" not in existing_score_cols:
                cursor.execute("ALTER TABLE coding_scores ADD COLUMN independent_score REAL DEFAULT 10.0")
            if "independent_max" not in existing_score_cols:
                cursor.execute("ALTER TABLE coding_scores ADD COLUMN independent_max REAL DEFAULT 10.0")
            if "unique_hints_used" not in existing_score_cols:
                cursor.execute("ALTER TABLE coding_scores ADD COLUMN unique_hints_used INTEGER DEFAULT 0")
            if "code_snapshot" not in existing_score_cols:
                cursor.execute("ALTER TABLE coding_scores ADD COLUMN code_snapshot TEXT DEFAULT ''")
            if "memory_usage_mb" not in existing_score_cols:
                cursor.execute("ALTER TABLE coding_scores ADD COLUMN memory_usage_mb REAL DEFAULT 0.0")

            # 10. User Profiles (legacy/cached profile synchronization)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_json TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # 11. Paste Attempt Events table (Assessment Mode tracking, IST Asia/Kolkata compliant)
            cursor.execute("PRAGMA foreign_key_list(paste_events)")
            fk_list = cursor.fetchall()
            if any(row["table"] == "coding_attempts" for row in fk_list):
                cursor.execute("DROP TABLE paste_events")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paste_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    attempt_id TEXT,
                    question_id TEXT,
                    page_type TEXT NOT NULL, -- 'coding' or 'viva'
                    event_timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # 12. Session Lock and Full-Screen Proctoring Events table (IST Asia/Kolkata compliant)
            cursor.execute("PRAGMA foreign_key_list(session_lock_events)")
            fk_list_lock = cursor.fetchall()
            if any(row["table"] == "coding_attempts" for row in fk_list_lock):
                cursor.execute("DROP TABLE session_lock_events")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_lock_events (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    attempt_id TEXT,
                    question_id TEXT,
                    event_type TEXT NOT NULL,
                    event_timestamp TIMESTAMP NOT NULL,
                    event_timestamp_ist TEXT,
                    metadata_json TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # 12. Indexes for fast, scalable queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_paste_events_user ON paste_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_paste_events_attempt ON paste_events(attempt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_provider ON users(auth_provider, provider_subject_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON coding_attempts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_question_id ON coding_attempts(question_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tab_switch_user_id ON tab_switch_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tab_switch_attempt_id ON tab_switch_events(attempt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_test_results_attempt_id ON test_results(attempt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_progress_user ON student_progress(user_id, topic)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_viva_user_id ON ai_viva_results(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_scores_user ON coding_scores(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_scores_question ON coding_scores(question_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_scores_attempt ON coding_scores(attempt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_scores_created ON coding_scores(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_scores_idempotency ON coding_scores(idempotency_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_topic ON coding_questions(topic)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON coding_questions(difficulty)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user_created ON coding_attempts(user_id, created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user_start ON coding_attempts(user_id, start_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tab_switch_user_event ON tab_switch_events(user_id, event_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_viva_user_completed ON ai_viva_results(user_id, completed_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_lock_user ON session_lock_events(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_lock_attempt ON session_lock_events(attempt_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_lock_type ON session_lock_events(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_lock_user_event ON session_lock_events(user_id, event_timestamp)")

            conn.commit()

init_database()
