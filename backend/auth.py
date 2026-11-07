import sqlite3
import os
import re
import secrets
import time
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple, List
import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from database import get_db, init_database, format_timestamp_ist, utc_iso_now, parse_utc_timestamp

DB_PATH = os.path.join(os.path.dirname(__file__), "codeacharya.db")
SECRET_KEY = os.environ.get("CODEACHARYA_AUTH_SECRET", "codeacharya-production-auth-secret-key-2026")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

SESSION_DURATION_HOURS = 24  # Standard session: 24 hours
REMEMBER_ME_DURATION_DAYS = 30  # Remember me session: 30 days

# Argon2id password hasher instance
ph = PasswordHasher()

# Ensure database is initialized with full schema
init_database()

def validate_email(email: str) -> bool:
    if not email or len(email) > 255:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password is too long (maximum 128 characters)."
    return True, None

def hash_password(password: str) -> str:
    """Hashes password using Argon2id."""
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verifies password supporting Argon2id and legacy bcrypt hashes."""
    if not password or not hashed:
        return False
    # Check Argon2id
    if hashed.startswith("$argon2"):
        try:
            return ph.verify(hashed, password)
        except (VerifyMismatchError, VerificationError):
            return False
        except Exception:
            return False
    # Check legacy bcrypt
    elif hashed.startswith("$2b$") or hashed.startswith("$2a$") or hashed.startswith("$2y$"):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    return False

def init_db():
    """Seeds default demo learner account if users table is empty."""
    init_database()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            demo_id = "user_demo_learner_001"
            demo_email = "student@codeacharya.ai"
            demo_name = "Student Learner"
            pwd_hash = hash_password("Password123!")
            cursor.execute(
                """INSERT INTO users 
                   (id, email, full_name, auth_provider, password_hash, account_status, created_at, updated_at) 
                   VALUES (?, ?, ?, 'local', ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (demo_id, demo_email, demo_name, pwd_hash)
            )

            # Clean default profile for demo user
            default_profile = {
                "student_name": demo_name,
                "streak_days": 1,
                "total_solved": 0,
                "total_attempts": 0,
                "hints_unlocked": 0,
                "total_debug_time_mins": 0,
                "total_coding_time_seconds": 0,
                "topic_mastery": {
                    "Recursion & Backtracking": 0,
                    "Arrays & Hashing": 0,
                    "Strings": 0,
                    "Stack & Queue": 0,
                    "Dynamic Programming": 0,
                    "Algorithms & Two Pointers": 0
                },
                "problem_solving_times": {},
                "recent_mistakes": [],
                "viva_history": [],
                "activity_log": [
                    {"action": "Account Created", "problem": "CodeAcharya Platform", "timestamp": format_timestamp_ist(utc_iso_now())}
                ]
            }
            cursor.execute(
                "INSERT OR REPLACE INTO user_profiles (user_id, profile_json) VALUES (?, ?)",
                (demo_id, json.dumps(default_profile))
            )
            conn.commit()

init_db()

def create_user(
    full_name: str, 
    email: str, 
    password: Optional[str] = None, 
    auth_provider: str = "local", 
    provider_subject_id: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name or len(full_name) < 2:
        return None, "Full name must be at least 2 characters."
    if not validate_email(email):
        return None, "Invalid email address format."
    
    pwd_hash = None
    if auth_provider == "local":
        if not password:
            return None, "Password is required for email/password registration."
        valid_pwd, pwd_err = validate_password(password)
        if not valid_pwd:
            return None, pwd_err
        pwd_hash = hash_password(password)

    user_id = f"user_{secrets.token_hex(12)}"

    default_profile = {
        "student_name": full_name,
        "streak_days": 1,
        "total_solved": 0,
        "total_attempts": 0,
        "hints_unlocked": 0,
        "total_debug_time_mins": 0,
        "total_coding_time_seconds": 0,
        "topic_mastery": {
            "Recursion & Backtracking": 0,
            "Arrays & Hashing": 0,
            "Strings": 0,
            "Stack & Queue": 0,
            "Dynamic Programming": 0,
            "Algorithms & Two Pointers": 0
        },
        "problem_solving_times": {},
        "recent_mistakes": [],
        "viva_history": [],
        "activity_log": [
            {"action": "Account Created", "problem": "CodeAcharya Platform", "timestamp": format_timestamp_ist(utc_iso_now())}
        ]
    }

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users 
                   (id, email, full_name, auth_provider, provider_subject_id, password_hash, account_status, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (user_id, email, full_name, auth_provider, provider_subject_id, pwd_hash)
            )
            cursor.execute(
                "INSERT INTO user_profiles (user_id, profile_json) VALUES (?, ?)",
                (user_id, json.dumps(default_profile))
            )
            conn.commit()
            return {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "auth_provider": auth_provider
            }, None
    except sqlite3.IntegrityError:
        return None, "An account with this email address already exists."
    except Exception as e:
        return None, f"Failed to create user account: {str(e)}"

def authenticate_user(email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    email = email.strip().lower()
    if not email or not password:
        return None, "Email and password are required."

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, email, full_name, password_hash, auth_provider, account_status FROM users WHERE email = ?", 
            (email,)
        )
        row = cursor.fetchone()
        if not row:
            return None, "Invalid email or password."
        
        if row["account_status"] != "active":
            return None, "Account is currently suspended. Please contact support."
        
        if not row["password_hash"]:
            if row["auth_provider"] == "google":
                return None, "This account was created with Google Sign-In. Please click 'Continue with Google'."
            return None, "Invalid email or password."

        if not verify_password(password, row["password_hash"]):
            return None, "Invalid email or password."

        # Update last login
        cursor.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", (row["id"],))
        conn.commit()

        return {
            "id": row["id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "auth_provider": row["auth_provider"]
        }, None

def verify_google_id_token(id_token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Verifies a Google ID token via Google's official tokeninfo endpoint:
    https://oauth2.googleapis.com/tokeninfo?id_token={id_token}
    Validates issuer, audience, expiration, and verified email claim.
    """
    if not id_token or not id_token.strip():
        return None, "Google ID token is required."

    token_str = id_token.strip()

    # Support testing environment verification with mock tokens
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("TESTING") == "1":
        if token_str.startswith("mock_google_token_"):
            mock_sub = token_str[len("mock_google_token_"):]
            mock_email = f"google_user_{mock_sub[:8]}@gmail.com"
            mock_name = "Google Verified Learner"
            return {
                "sub": mock_sub,
                "email": mock_email,
                "name": mock_name,
                "email_verified": True
            }, None

    # Call official Google tokeninfo verification endpoint
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.request.quote(token_str)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CodeAcharya-Backend/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            err_msg = err_data.get("error_description") or err_data.get("error") or "Invalid Google ID token"
        except Exception:
            err_msg = "Google token verification rejected by Google API"
        return None, f"Google token verification failed: {err_msg}"
    except Exception as e:
        return None, f"Could not connect to Google authentication server: {str(e)}"

    # 1. Validate issuer
    iss = data.get("iss")
    if iss not in ["accounts.google.com", "https://accounts.google.com"]:
        return None, f"Invalid Google token issuer: {iss}"

    # 2. Validate audience if GOOGLE_CLIENT_ID is configured
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    if client_id:
        aud = data.get("aud")
        if aud != client_id:
            return None, "Google token audience mismatch. Unauthorized application client ID."

    # 3. Validate email verified claim
    email_verified = data.get("email_verified")
    if email_verified not in [True, "true", "True"]:
        return None, "Google account email is not verified. Please verify your Google email before signing in."

    # 4. Check expiration
    exp = int(data.get("exp", 0))
    if exp < time.time():
        return None, "Google authentication token has expired. Please sign in again."

    return {
        "sub": data.get("sub"),
        "email": data.get("email", "").lower().strip(),
        "name": data.get("name") or data.get("email", "").split("@")[0],
        "picture": data.get("picture")
    }, None

def authenticate_or_create_google_user(id_token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Authenticates a user via verified Google ID token.
    If the account exists, logs in. If new, creates account safely with auth_provider='google'.
    """
    claims, err = verify_google_id_token(id_token)
    if err or not claims:
        return None, err or "Invalid Google credentials."

    google_sub = claims["sub"]
    email = claims["email"]
    name = claims["name"]

    if not email:
        return None, "Google did not provide a valid email address for this account."

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Find user by provider subject ID
        cursor.execute("SELECT id, email, full_name, auth_provider, account_status FROM users WHERE provider_subject_id = ?", (google_sub,))
        user = cursor.fetchone()

        if not user:
            # 2. Find user by email to link Google account
            cursor.execute("SELECT id, email, full_name, auth_provider, account_status FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                # Link existing user record to Google ID
                cursor.execute(
                    "UPDATE users SET provider_subject_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (google_sub, user["id"])
                )
                conn.commit()
            else:
                # 3. Create new user with Google authentication provider
                new_user_id = f"user_g_{secrets.token_hex(10)}"
                cursor.execute(
                    """INSERT INTO users 
                       (id, email, full_name, auth_provider, provider_subject_id, password_hash, account_status, created_at, updated_at) 
                       VALUES (?, ?, ?, 'google', ?, 'oauth_google_account', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (new_user_id, email, name, google_sub)
                )

                # Initialize clean default student profile
                default_profile = {
                    "student_name": name,
                    "streak_days": 1,
                    "total_solved": 0,
                    "total_attempts": 0,
                    "hints_unlocked": 0,
                    "total_debug_time_mins": 0,
                    "total_coding_time_seconds": 0,
                    "topic_mastery": {
                        "Recursion & Backtracking": 0,
                        "Arrays & Hashing": 0,
                        "Strings": 0,
                        "Stack & Queue": 0,
                        "Dynamic Programming": 0,
                        "Algorithms & Two Pointers": 0
                    },
                    "problem_solving_times": {},
                    "recent_mistakes": [],
                    "viva_history": [],
                    "activity_log": [
                        {"action": "Account Created via Google", "problem": "CodeAcharya Platform", "timestamp": format_timestamp_ist(utc_iso_now())}
                    ]
                }
                cursor.execute(
                    "INSERT INTO user_profiles (user_id, profile_json) VALUES (?, ?)",
                    (new_user_id, json.dumps(default_profile))
                )
                conn.commit()

                cursor.execute("SELECT id, email, full_name, auth_provider, account_status FROM users WHERE id = ?", (new_user_id,))
                user = cursor.fetchone()

        if user["account_status"] != "active":
            return None, "Account is currently suspended. Please contact support."

        # Update last login timestamp
        cursor.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],))
        conn.commit()

        return {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "auth_provider": user["auth_provider"]
        }, None

def create_session(user_id: str, is_remember_me: bool = False) -> str:
    token = secrets.token_urlsafe(32)
    duration_hours = (REMEMBER_ME_DURATION_DAYS * 24) if is_remember_me else SESSION_DURATION_HOURS
    expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (token, user_id, expires_at, is_remember_me) VALUES (?, ?, ?, ?)",
            (token, user_id, expires_at.isoformat(), 1 if is_remember_me else 0)
        )
        conn.commit()
    return token

def get_user_from_session(token: str) -> Optional[Dict[str, Any]]:
    if not token or not token.strip():
        return None
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.email, u.full_name, u.auth_provider, u.account_status, s.expires_at 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        """, (token.strip(),))
        row = cursor.fetchone()
        if not row:
            return None
        
        # Check expiration
        try:
            exp_str = row["expires_at"]
            expires_at = datetime.fromisoformat(exp_str)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires_at:
                cursor.execute("DELETE FROM sessions WHERE token = ?", (token.strip(),))
                conn.commit()
                return None
        except Exception:
            return None

        if row["account_status"] != "active":
            return None

        return {
            "id": row["id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "auth_provider": row["auth_provider"],
            "account_status": row["account_status"]
        }

def delete_session(token: str) -> bool:
    if not token:
        return False
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token.strip(),))
        conn.commit()
        return cursor.rowcount > 0

def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "00:00"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

STALE_SESSION_SECONDS = int(os.environ.get("CODEACHARYA_STALE_SESSION_SECONDS", 7200))

def recover_stale_attempts(user_id: Optional[str] = None, stale_threshold_seconds: int = STALE_SESSION_SECONDS) -> int:
    """
    Server-side stale-running-attempt recovery policy:
    Distinguishes genuinely active attempts from abandoned/stale sessions using reliable server-side activity information.
    If an attempt has been in 'running' or 'paused' state with no activity for > stale_threshold_seconds,
    marks it as 'abandoned' while preserving all audit details and NEVER fabricating a completion timestamp.
    """
    now_utc_dt = datetime.now(timezone.utc)
    now_utc = now_utc_dt.isoformat()
    recovered_count = 0

    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, user_id, question_id, attempt_status, start_time, created_at, 
                   last_activity_at, test_results_summary
            FROM coding_attempts
            WHERE attempt_status IN ('running', 'paused')
        """
        params = []
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        cursor.execute(query, tuple(params))
        stale_rows = cursor.fetchall()

        for row in stale_rows:
            activity_ts = row["last_activity_at"] or row["created_at"] or row["start_time"]
            activity_dt = parse_utc_timestamp(activity_ts) if activity_ts else None
            
            is_stale = False
            if activity_dt:
                elapsed_since_activity = (now_utc_dt - activity_dt).total_seconds()
                if elapsed_since_activity > stale_threshold_seconds:
                    is_stale = True
            else:
                is_stale = True

            if is_stale:
                summary_data = {}
                if row["test_results_summary"]:
                    try:
                        summary_data = json.loads(row["test_results_summary"])
                    except Exception:
                        summary_data = {}
                summary_data["abandoned_reason"] = "stale_inactivity_timeout"
                summary_data["recovered_at"] = now_utc
                summary_data["attempt_status"] = "abandoned"

                cursor.execute("""
                    UPDATE coding_attempts
                    SET attempt_status = 'abandoned',
                        end_time = NULL,
                        test_results_summary = ?
                    WHERE id = ?
                """, (json.dumps(summary_data), row["id"]))
                recovered_count += 1

        conn.commit()
    return recovered_count

def record_user_attempt(
    user_id: str, 
    problem_id: str, 
    topic: str, 
    passed: bool, 
    hints_used: int = 0,
    time_spent_seconds: int = 0,
    session_status: str = "completed",
    tab_switch_count: int = 0,
    total_time_away_seconds: int = 0,
    last_switch_timestamp: Optional[str] = None,
    tab_switch_history: Optional[List[Dict[str, Any]]] = None,
    code: str = "",
    test_results_list: Optional[List[Dict[str, Any]]] = None,
    language: str = "python",
    score_data: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = None,
    passed_count: Optional[int] = None,
    total_count: Optional[int] = None,
    unique_hints_used: Optional[int] = None,
    attempt_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    paused_seconds: Optional[int] = 0,
    is_locked: Optional[bool] = None,
    lock_reason: Optional[str] = None
) -> str:
    """
    Persists coding attempt and its score into relational tables:
    - coding_attempts
    - coding_scores (Performance and Score Analytics)
    - test_results
    - tab_switch_events
    - student_progress
    - user_profiles (cache)
    Includes idempotency protection against duplicate submissions.
    """
    # 0. Deduplication check
    if idempotency_key:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT attempt_id FROM coding_scores WHERE idempotency_key = ?", (idempotency_key,))
            existing = cursor.fetchone()
            if existing:
                return existing["attempt_id"]

    if not attempt_id:
        attempt_id = f"attempt_{secrets.token_hex(10)}"

    now_utc_dt = datetime.now(timezone.utc)
    now_utc = now_utc_dt.isoformat()
    now_ist_str = format_timestamp_ist(now_utc)
    formatted_duration = format_duration(time_spent_seconds)

    p_count = passed_count if passed_count is not None else (1 if passed else 0)
    t_count = total_count if total_count is not None else (len(test_results_list) if test_results_list else (1 if passed else 0))

    norm_status = (session_status or "completed").lower().strip()
    is_incomplete = norm_status in ("running", "paused", "abandoned")

    # Strict completion check
    if norm_status == "completed" and t_count > 0 and p_count < t_count:
        norm_status = "failed"
        passed = False

    is_completed_flag = 1 if (passed and norm_status == "completed" and p_count == t_count and t_count > 0) else 0

    # Check if attempt already exists in database
    existing_start_time = None
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT start_time FROM coding_attempts WHERE id = ?", (attempt_id,))
        ex_row = cursor.fetchone()
        if ex_row and ex_row["start_time"]:
            existing_start_time = ex_row["start_time"]

    # Calculate actual start & end timestamps consistent with duration & pause rules
    elapsed_total_seconds = (time_spent_seconds or 0) + (total_time_away_seconds or 0) + (paused_seconds or 0)

    if is_incomplete:
        actual_end_time = None
        if start_time:
            parsed_st = parse_utc_timestamp(start_time)
            actual_start_time = parsed_st.isoformat() if parsed_st else now_utc
        elif existing_start_time:
            actual_start_time = existing_start_time
        else:
            actual_start_time = (now_utc_dt - timedelta(seconds=elapsed_total_seconds)).isoformat()
    else:
        if end_time:
            parsed_et = parse_utc_timestamp(end_time)
            actual_end_time = parsed_et.isoformat() if parsed_et else now_utc
            end_dt = parsed_et or now_utc_dt
        else:
            actual_end_time = now_utc
            end_dt = now_utc_dt

        if start_time:
            parsed_st = parse_utc_timestamp(start_time)
            actual_start_time = parsed_st.isoformat() if parsed_st else (end_dt - timedelta(seconds=elapsed_total_seconds)).isoformat()
        elif existing_start_time:
            actual_start_time = existing_start_time
        else:
            actual_start_time = (end_dt - timedelta(seconds=elapsed_total_seconds)).isoformat()

    # Determine unique hints used
    actual_unique_hints = unique_hints_used if unique_hints_used is not None else (
        score_data.get("unique_hints_used", hints_used or 0) if score_data else (hints_used or 0)
    )

    overall_score = 0.0
    score_breakdown_json = "{}"
    evaluator_type = "automated"
    independent_pts = 10.0
    if score_data:
        overall_score = float(score_data.get("overall_score", 0.0))
        score_breakdown_json = json.dumps(score_data.get("breakdown", {}))
        evaluator_type = score_data.get("evaluator", {}).get("evaluator_type", "automated")
        breakdown_dict = score_data.get("breakdown", {})
        if "independent" in breakdown_dict:
            independent_pts = float(breakdown_dict["independent"].get("points_earned", 10.0))

    test_summary = {
        "passed": bool(is_completed_flag),
        "hints_used": actual_unique_hints,
        "unique_hints_used": actual_unique_hints,
        "independent_score": independent_pts,
        "tab_switch_count": tab_switch_count,
        "total_time_away_seconds": total_time_away_seconds,
        "last_switch_timestamp": last_switch_timestamp,
        "overall_score": overall_score
    }

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Ensure question exists in coding_questions
        cursor.execute("SELECT id FROM coding_questions WHERE id = ?", (problem_id,))
        if not cursor.fetchone():
            cursor.execute(
                """INSERT INTO coding_questions (id, title, description, difficulty, topic, created_at, updated_at) 
                   VALUES (?, ?, ?, 'Medium', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                (problem_id, problem_id.replace("-", " ").title(), "Coding Problem", topic)
            )

    # 2. Insert or update coding_attempts
        cursor.execute("SELECT id FROM coding_attempts WHERE id = ?", (attempt_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE coding_attempts SET
                    language = ?,
                    attempt_status = ?,
                    start_time = ?,
                    end_time = ?,
                    elapsed_coding_time_seconds = ?,
                    is_completed = ?,
                    passed_count = ?,
                    total_count = ?,
                    code = ?,
                    test_results_summary = ?,
                    overall_score = ?,
                    score_breakdown = ?,
                    evaluator_type = ?,
                    unique_hints_used = ?,
                    independent_score = ?,
                    paused_seconds = ?,
                    last_activity_at = ?
                WHERE id = ?
            """, (
                language,
                norm_status,
                actual_start_time,
                actual_end_time,
                time_spent_seconds,
                is_completed_flag,
                p_count,
                t_count,
                code,
                json.dumps(test_summary),
                overall_score,
                score_breakdown_json,
                evaluator_type,
                actual_unique_hints,
                independent_pts,
                paused_seconds or 0,
                now_utc,
                attempt_id
            ))
        else:
            cursor.execute("""
                INSERT INTO coding_attempts (
                    id, user_id, question_id, language, attempt_status,
                    start_time, end_time, elapsed_coding_time_seconds,
                    is_completed, passed_count, total_count, code,
                    test_results_summary, overall_score, score_breakdown,
                    evaluator_type, idempotency_key, unique_hints_used,
                    independent_score, paused_seconds, last_activity_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attempt_id,
                user_id,
                problem_id,
                language,
                norm_status,
                actual_start_time,
                actual_end_time,
                time_spent_seconds,
                is_completed_flag,
                p_count,
                t_count,
                code,
                json.dumps(test_summary),
                overall_score,
                score_breakdown_json,
                evaluator_type,
                idempotency_key,
                actual_unique_hints,
                independent_pts,
                paused_seconds or 0,
                now_utc,
                now_utc
            ))

        if is_locked is not None:
            cursor.execute("""
                UPDATE coding_attempts SET
                    is_locked = ?,
                    lock_reason = COALESCE(?, lock_reason)
                WHERE id = ?
            """, (1 if is_locked else 0, lock_reason, attempt_id))

        # 3. Insert or update coding_scores if score_data is available
        if score_data:
            breakdown = score_data.get("breakdown", {})
            corr = breakdown.get("correctness", {})
            comp = breakdown.get("complexity", {})
            qual = breakdown.get("quality", {})
            appr = breakdown.get("approach", {})
            indep = breakdown.get("independent", {})

            corr_score = corr.get("points_earned", 0.0)
            corr_max = corr.get("max_points", 40.0)
            comp_score = comp.get("points_earned") if comp.get("is_available") else None
            comp_max = comp.get("max_points") if comp.get("is_available") else None
            qual_score = qual.get("points_earned") if qual.get("is_available") else None
            qual_max = qual.get("max_points") if qual.get("is_available") else None
            appr_score = appr.get("points_earned") if appr.get("is_available") else None
            appr_max = appr.get("max_points") if appr.get("is_available") else None
            indep_score = indep.get("points_earned", independent_pts)
            indep_max = indep.get("max_points", 10.0)

            perf = score_data.get("performance", {})
            exec_time_ms = float(perf.get("execution_time_ms", 0.0))
            mem_mb = float(perf.get("memory_usage_mb") or 0.0)

            cursor.execute("SELECT id FROM coding_scores WHERE attempt_id = ?", (attempt_id,))
            ex_score = cursor.fetchone()
            if ex_score:
                cursor.execute("""
                    UPDATE coding_scores SET
                        language = ?,
                        overall_score = ?,
                        correctness_score = ?, correctness_max = ?,
                        complexity_score = ?, complexity_max = ?,
                        quality_score = ?, quality_max = ?,
                        approach_score = ?, approach_max = ?,
                        independent_score = ?, independent_max = ?,
                        unique_hints_used = ?, code_snapshot = ?, memory_usage_mb = ?,
                        is_renormalized = ?, evaluator_type = ?,
                        breakdown_json = ?, feedback_json = ?,
                        execution_time_ms = ?, coding_time_seconds = ?, tab_away_seconds = ?,
                        passed_count = ?, total_count = ?, status = ?, idempotency_key = ?
                    WHERE attempt_id = ?
                """, (
                    language,
                    overall_score,
                    corr_score, corr_max,
                    comp_score, comp_max,
                    qual_score, qual_max,
                    appr_score, appr_max,
                    indep_score, indep_max,
                    actual_unique_hints,
                    code,
                    mem_mb,
                    1 if score_data.get("is_renormalized") else 0,
                    evaluator_type,
                    score_breakdown_json,
                    json.dumps(score_data.get("feedback", {})),
                    exec_time_ms,
                    time_spent_seconds,
                    total_time_away_seconds,
                    p_count,
                    t_count,
                    norm_status,
                    idempotency_key,
                    attempt_id
                ))
            else:
                score_id = f"score_{secrets.token_hex(8)}"
                cursor.execute("""
                    INSERT INTO coding_scores (
                        id, user_id, attempt_id, question_id, language, overall_score,
                        correctness_score, correctness_max,
                        complexity_score, complexity_max,
                        quality_score, quality_max,
                        approach_score, approach_max,
                        independent_score, independent_max,
                        unique_hints_used, code_snapshot, memory_usage_mb,
                        is_renormalized, evaluator_type,
                        breakdown_json, feedback_json,
                        execution_time_ms, coding_time_seconds, tab_away_seconds,
                        passed_count, total_count, status, idempotency_key, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    score_id,
                    user_id,
                    attempt_id,
                    problem_id,
                    language,
                    overall_score,
                    corr_score,
                    corr_max,
                    comp_score,
                    comp_max,
                    qual_score,
                    qual_max,
                    appr_score,
                    appr_max,
                    indep_score,
                    indep_max,
                    actual_unique_hints,
                    code,
                    mem_mb,
                    1 if score_data.get("is_renormalized") else 0,
                    evaluator_type,
                    score_breakdown_json,
                    json.dumps(score_data.get("feedback", {})),
                    exec_time_ms,
                    time_spent_seconds,
                    total_time_away_seconds,
                    p_count,
                    t_count,
                    norm_status,
                    idempotency_key,
                    now_utc
                ))

        # 4. Insert individual test results if provided (refreshing existing)
        if test_results_list:
            cursor.execute("DELETE FROM test_results WHERE attempt_id = ?", (attempt_id,))
            for tr in test_results_list:
                tr_id = f"tr_{secrets.token_hex(8)}"
                cursor.execute("""
                    INSERT INTO test_results (
                        id, attempt_id, test_case_id, is_hidden, passed, execution_time_ms, safe_error_info, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tr_id,
                    attempt_id,
                    tr.get("test_id", 1),
                    1 if tr.get("is_hidden") else 0,
                    1 if tr.get("passed") else 0,
                    float(tr.get("execution_time_ms", 0.0)),
                    tr.get("error"),
                    now_utc
                ))

        # 5. Insert tab switch events if provided (IST-compliant, deduplicated, accurate durations)
        if tab_switch_history:
            for idx, item in enumerate(tab_switch_history, 1):
                ts_id = item.get("id") or f"ts_{attempt_id}_{item.get('switch_number', idx)}"

                # Extract hidden/event timestamp (prioritize ISO or millisecond epoch over date-less strings)
                raw_ev = (
                    item.get("event_timestamp")
                    or (datetime.fromtimestamp(item["switch_timestamp_ms"] / 1000.0, tz=timezone.utc).isoformat() if item.get("switch_timestamp_ms") else None)
                    or item.get("hidden_time")
                    or item.get("timestamp")
                    or item.get("switch_time")
                    or item.get("switch_timestamp_ist")
                )

                ev_dt = parse_utc_timestamp(raw_ev) or parse_utc_timestamp(actual_start_time) or now_utc_dt
                ev_time = ev_dt.isoformat()

                # Extract return timestamp (prioritize ISO or millisecond epoch)
                raw_ret = (
                    item.get("return_timestamp")
                    or (datetime.fromtimestamp(item["return_timestamp_ms"] / 1000.0, tz=timezone.utc).isoformat() if item.get("return_timestamp_ms") else None)
                    or item.get("return_timestamp_ist")
                    or item.get("return_time_ist")
                    or item.get("return_time")
                )

                ret_dt = None
                if raw_ret and str(raw_ret).strip() not in (
                    "Away...", "Active", "Pending Return", "Awaiting return", "Incomplete", "None", "null", ""
                ):
                    ret_dt = parse_utc_timestamp(raw_ret)

                ret_time = ret_dt.isoformat() if ret_dt else None

                raw_status = (item.get("status") or item.get("event_status") or "").lower().strip()
                if ret_dt:
                    status = "returned" if raw_status not in ("incomplete", "away") else raw_status
                else:
                    status = raw_status if raw_status in ("away", "incomplete", "active") else "incomplete"

                # Extract duration away accurately
                away = item.get("duration_away_seconds")
                if away is None:
                    away = item.get("time_away_seconds")
                if away is None:
                    away = item.get("away_seconds")

                if away is not None:
                    try:
                        away = max(0, int(round(float(away))))
                    except Exception:
                        away = 0
                else:
                    away = 0

                if ret_dt and ev_dt:
                    diff_s = max(0, int(round((ret_dt - ev_dt).total_seconds())))
                    if diff_s > 0:
                        away = diff_s

                # Deduplication check
                cursor.execute("""
                    SELECT id FROM tab_switch_events
                    WHERE id = ? OR (user_id = ? AND attempt_id = ? AND event_timestamp = ?)
                """, (ts_id, user_id, attempt_id, ev_time))
                existing_ts = cursor.fetchone()

                if existing_ts:
                    target_id = existing_ts["id"]
                    cursor.execute("""
                        UPDATE tab_switch_events SET
                            question_id = ?,
                            return_timestamp = ?,
                            time_away_seconds = ?,
                            event_status = ?
                        WHERE id = ?
                    """, (problem_id, ret_time, away, status, target_id))
                else:
                    cursor.execute("""
                        INSERT INTO tab_switch_events (
                            id, user_id, attempt_id, question_id, event_timestamp, return_timestamp, time_away_seconds, event_status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ts_id,
                        user_id,
                        attempt_id,
                        problem_id,
                        ev_time,
                        ret_time,
                        away,
                        status,
                        now_utc
                    ))

        # 6. Update student_progress for (user_id, topic)
        cursor.execute("SELECT attempts_completed, problems_solved, mastery_percentage FROM student_progress WHERE user_id = ? AND topic = ?", (user_id, topic))
        prog_row = cursor.fetchone()
        if prog_row:
            new_attempts = prog_row["attempts_completed"] + 1
            new_solved = prog_row["problems_solved"] + (1 if is_completed_flag else 0)
            new_mastery = min(100, max(0, int((new_solved / max(1, new_attempts)) * 100)))
            cursor.execute("""
                UPDATE student_progress 
                SET attempts_completed = ?, problems_solved = ?, mastery_percentage = ?, last_activity_timestamp = ?
                WHERE user_id = ? AND topic = ?
            """, (new_attempts, new_solved, new_mastery, now_utc, user_id, topic))
        else:
            first_solved = 1 if is_completed_flag else 0
            first_mastery = 100 if is_completed_flag else 0
            prog_id = f"prog_{secrets.token_hex(8)}"
            cursor.execute("""
                INSERT INTO student_progress (id, user_id, topic, attempts_completed, problems_solved, mastery_percentage, last_activity_timestamp)
                VALUES (?, ?, ?, 1, ?, ?, ?)
            """, (prog_id, user_id, topic, first_solved, first_mastery, now_utc))

        conn.commit()

    # 7. Update user_profiles cache
    profile = get_user_profile(user_id)
    save_user_profile(user_id, profile)
    return attempt_id

def record_user_session(
    user_id: str,
    problem_id: str,
    topic: str,
    status: str,
    time_spent_seconds: int = 0,
    passed_count: int = 0,
    total_count: int = 0,
    tab_switch_count: int = 0,
    total_time_away_seconds: int = 0,
    last_switch_timestamp: Optional[str] = None,
    tab_switch_history: Optional[List[Dict[str, Any]]] = None,
    attempt_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    paused_seconds: Optional[int] = 0,
    code: str = "",
    score_data: Optional[Dict[str, Any]] = None,
    is_locked: Optional[bool] = None,
    lock_reason: Optional[str] = None
):
    norm_status = (status or "completed").lower().strip()
    is_completed = (norm_status == "completed" and passed_count == total_count and total_count > 0)
    if norm_status == "completed" and not is_completed:
        norm_status = "failed"

    return record_user_attempt(
        user_id=user_id,
        problem_id=problem_id,
        topic=topic,
        passed=is_completed,
        hints_used=0,
        time_spent_seconds=time_spent_seconds,
        session_status=norm_status,
        tab_switch_count=tab_switch_count,
        total_time_away_seconds=total_time_away_seconds,
        last_switch_timestamp=last_switch_timestamp,
        tab_switch_history=tab_switch_history,
        code=code,
        score_data=score_data,
        passed_count=passed_count,
        total_count=total_count,
        attempt_id=attempt_id,
        start_time=start_time,
        end_time=end_time,
        paused_seconds=paused_seconds,
        is_locked=is_locked,
        lock_reason=lock_reason
    )

def record_user_mistake(user_id: str, topic: str, mistake_desc: str):
    profile = get_user_profile(user_id)
    profile.setdefault("recent_mistakes", []).insert(0, {
        "topic": topic,
        "mistake": mistake_desc,
        "time": "Just now"
    })
    profile["recent_mistakes"] = profile["recent_mistakes"][:6]
    save_user_profile(user_id, profile)

def record_user_viva(
    user_id: str, 
    problem_id: str, 
    scores: Dict[str, int], 
    questions_asked: Optional[List[Any]] = None, 
    student_answers: Optional[List[Any]] = None,
    feedback: Optional[str] = None
):
    """Persists viva defense results into ai_viva_results and updates student profile."""
    viva_id = f"viva_{secrets.token_hex(8)}"
    now_utc = utc_iso_now()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ai_viva_results (
                id, user_id, question_id, overall_score,
                conceptual_score, code_understanding_score,
                complexity_score, communication_score,
                questions_asked, student_answers, evaluation_results, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            viva_id,
            user_id,
            problem_id,
            scores.get("overall", 0),
            scores.get("conceptual", 0),
            scores.get("code_understanding", 0),
            scores.get("complexity", 0),
            scores.get("communication", 0),
            json.dumps(questions_asked or []),
            json.dumps(student_answers or []),
            json.dumps({"feedback": feedback or ""}),
            now_utc
        ))
        conn.commit()

    profile = get_user_profile(user_id)
    save_user_profile(user_id, profile)

def get_user_tab_switches(user_id: str, attempt_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches user tab switch events enforcing user_id ownership and formatting in IST."""
    with get_db() as conn:
        cursor = conn.cursor()
        if attempt_id:
            cursor.execute("""
                SELECT id, user_id, attempt_id, question_id, event_timestamp, return_timestamp, time_away_seconds, event_status
                FROM tab_switch_events
                WHERE user_id = ? AND attempt_id = ?
                ORDER BY event_timestamp DESC
            """, (user_id, attempt_id))
        else:
            cursor.execute("""
                SELECT id, user_id, attempt_id, question_id, event_timestamp, return_timestamp, time_away_seconds, event_status
                FROM tab_switch_events
                WHERE user_id = ?
                ORDER BY event_timestamp DESC
            """, (user_id,))
        
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "user_id": r["user_id"],
                "attempt_id": r["attempt_id"],
                "question_id": r["question_id"],
                "event_timestamp": r["event_timestamp"],
                "event_timestamp_ist": format_timestamp_ist(r["event_timestamp"]),
                "return_timestamp": r["return_timestamp"],
                "return_timestamp_ist": format_timestamp_ist(r["return_timestamp"]),
                "time_away_seconds": r["time_away_seconds"],
                "event_status": r["event_status"]
            })
        return results

def record_user_paste_attempt(
    user_id: str,
    page_type: str,
    question_id: Optional[str] = None,
    attempt_id: Optional[str] = None,
    event_timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Persists blocked paste attempt telemetry in UTC and returns event object.
    Never stores or inspects clipboard contents.
    Deduplicates rapid consecutive bursts within 1.5 seconds.
    """
    paste_id = f"paste_{secrets.token_hex(8)}"
    now_utc = event_timestamp or utc_iso_now()

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Debounce / rate limit check: if an identical event occurred within 1.5s, deduplicate
        cursor.execute("""
            SELECT id, event_timestamp FROM paste_events
            WHERE user_id = ? AND page_type = ? AND (question_id = ? OR question_id IS NULL)
            ORDER BY created_at DESC LIMIT 1
        """, (user_id, page_type, question_id))
        prev = cursor.fetchone()
        if prev:
            try:
                t1 = datetime.fromisoformat(prev["event_timestamp"].replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(now_utc.replace("Z", "+00:00"))
                if abs((t2 - t1).total_seconds()) < 1.5:
                    return {
                        "id": prev["id"],
                        "user_id": user_id,
                        "page_type": page_type,
                        "question_id": question_id,
                        "attempt_id": attempt_id,
                        "event_timestamp": prev["event_timestamp"],
                        "event_timestamp_ist": format_timestamp_ist(prev["event_timestamp"]),
                        "is_deduplicated": True
                    }
            except Exception:
                pass

        cursor.execute("""
            INSERT INTO paste_events (
                id, user_id, attempt_id, question_id, page_type, event_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            paste_id,
            user_id,
            attempt_id,
            question_id,
            page_type,
            now_utc
        ))
        conn.commit()

        return {
            "id": paste_id,
            "user_id": user_id,
            "page_type": page_type,
            "question_id": question_id,
            "attempt_id": attempt_id,
            "event_timestamp": now_utc,
            "event_timestamp_ist": format_timestamp_ist(now_utc),
            "is_deduplicated": False
        }

def get_user_paste_attempts(
    user_id: str,
    page_type: Optional[str] = None,
    question_id: Optional[str] = None,
    attempt_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetches user paste events enforcing user_id ownership, formatted in IST.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM paste_events WHERE user_id = ?"
        params = [user_id]
        if page_type:
            query += " AND page_type = ?"
            params.append(page_type)
        if question_id:
            query += " AND question_id = ?"
            params.append(question_id)
        if attempt_id:
            query += " AND attempt_id = ?"
            params.append(attempt_id)
        query += " ORDER BY event_timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "attempt_id": r["attempt_id"],
                "question_id": r["question_id"],
                "page_type": r["page_type"],
                "event_timestamp": r["event_timestamp"],
                "event_timestamp_ist": format_timestamp_ist(r["event_timestamp"]),
                "created_at": r["created_at"]
            }
            for r in rows
        ]

def record_session_lock_event(
    user_id: str,
    event_type: str,
    attempt_id: Optional[str] = None,
    question_id: Optional[str] = None,
    event_timestamp: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Records a full-screen lock/unlock or proctoring activity event.
    Deduplicates rapid consecutive events within 1.0s window.
    """
    event_id = f"lock_ev_{secrets.token_hex(8)}"
    now_utc = event_timestamp or utc_iso_now()
    now_utc_dt = parse_utc_timestamp(now_utc) or datetime.now(timezone.utc)
    meta_json = json.dumps(metadata or {})

    with get_db() as conn:
        cursor = conn.cursor()

        # Deduplication check: if identical event_type occurred for this user & attempt within 1.0s, return existing
        cursor.execute("""
            SELECT id, event_timestamp FROM session_lock_events
            WHERE user_id = ? AND event_type = ? AND (attempt_id = ? OR (attempt_id IS NULL AND ? IS NULL))
            ORDER BY created_at DESC LIMIT 1
        """, (user_id, event_type, attempt_id, attempt_id))
        prev = cursor.fetchone()
        if prev:
            prev_dt = parse_utc_timestamp(prev["event_timestamp"])
            if prev_dt and abs((now_utc_dt - prev_dt).total_seconds()) < 1.0:
                return {
                    "id": prev["id"],
                    "user_id": user_id,
                    "event_type": event_type,
                    "attempt_id": attempt_id,
                    "question_id": question_id,
                    "event_timestamp": prev["event_timestamp"],
                    "event_timestamp_ist": format_timestamp_ist(prev["event_timestamp"]),
                    "duplicate": True
                }

        ist_str = format_timestamp_ist(now_utc)
        cursor.execute("""
            INSERT INTO session_lock_events (
                id, user_id, attempt_id, question_id, event_type, event_timestamp, event_timestamp_ist, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            user_id,
            attempt_id,
            question_id,
            event_type,
            now_utc,
            ist_str,
            meta_json
        ))

        # If this event indicates the editor should be locked, synchronize coding_attempts table
        if attempt_id and event_type in ("fullscreen_exited", "page_hidden", "editor_locked"):
            meta = metadata or {}
            lock_reason_val = meta.get("lock_reason") or (event_type if event_type in ("fullscreen_exited", "page_hidden") else "fullscreen_exit")
            cursor.execute("""
                UPDATE coding_attempts SET 
                    is_locked = 1,
                    lock_reason = ?,
                    last_locked_at = ?
                WHERE id = ?
            """, (lock_reason_val, now_utc, attempt_id))

        conn.commit()

        return {
            "id": event_id,
            "user_id": user_id,
            "event_type": event_type,
            "attempt_id": attempt_id,
            "question_id": question_id,
            "event_timestamp": now_utc,
            "event_timestamp_ist": ist_str,
            "duplicate": False
        }

def lock_coding_session(
    user_id: str,
    attempt_id: Optional[str] = None,
    question_id: Optional[str] = None,
    reason: str = "fullscreen_exit",
    event_timestamp: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Transitions a coding session into a locked state on the server.
    Updates the attempt record and persists structured telemetry events.
    """
    now_utc = event_timestamp or utc_iso_now()
    meta = metadata or {}
    meta["lock_reason"] = reason

    with get_db() as conn:
        cursor = conn.cursor()
        if attempt_id:
            cursor.execute("SELECT id, user_id, attempt_status FROM coding_attempts WHERE id = ?", (attempt_id,))
            att = cursor.fetchone()
            if att and user_id != "guest" and att["user_id"] != user_id:
                raise PermissionError("Attempt ownership mismatch: cannot lock another user's session.")

            cursor.execute("""
                UPDATE coding_attempts SET
                    is_locked = 1,
                    lock_reason = ?,
                    last_locked_at = ?
                WHERE id = ?
            """, (reason, now_utc, attempt_id))
            conn.commit()

    # Record the trigger event and editor_locked event
    trigger_event = "page_hidden" if reason == "page_hidden" else "fullscreen_exited"
    record_session_lock_event(
        user_id=user_id,
        event_type=trigger_event,
        attempt_id=attempt_id,
        question_id=question_id,
        event_timestamp=now_utc,
        metadata=meta
    )
    res = record_session_lock_event(
        user_id=user_id,
        event_type="editor_locked",
        attempt_id=attempt_id,
        question_id=question_id,
        event_timestamp=now_utc,
        metadata=meta
    )

    return {
        "status": "locked",
        "is_locked": True,
        "attempt_id": attempt_id,
        "question_id": question_id,
        "reason": reason,
        "event_id": res["id"],
        "event_timestamp_ist": res["event_timestamp_ist"]
    }

def resume_coding_session(
    user_id: str,
    attempt_id: Optional[str] = None,
    question_id: Optional[str] = None,
    fullscreen_verified: bool = False,
    event_timestamp: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Unlocks a coding session following verified browser full-screen confirmation.
    Validates attempt ownership, valid state transitions, and records telemetry.
    """
    now_utc = event_timestamp or utc_iso_now()
    meta = metadata or {}

    if not fullscreen_verified:
        record_session_lock_event(
            user_id=user_id,
            event_type="resume_requested",
            attempt_id=attempt_id,
            question_id=question_id,
            event_timestamp=now_utc,
            metadata=meta
        )
        record_session_lock_event(
            user_id=user_id,
            event_type="resume_failed",
            attempt_id=attempt_id,
            question_id=question_id,
            event_timestamp=now_utc,
            metadata={"reason": "fullscreen_verification_failed"}
        )
        raise ValueError("Document is not in browser full-screen mode. Full-screen mode is required to resume coding.")

    with get_db() as conn:
        cursor = conn.cursor()
        if attempt_id:
            cursor.execute("SELECT id, user_id, attempt_status FROM coding_attempts WHERE id = ?", (attempt_id,))
            att = cursor.fetchone()
            if att:
                if user_id != "guest" and att["user_id"] != user_id:
                    raise PermissionError("Attempt ownership mismatch: cannot resume another user's session.")
                if att["attempt_status"] in ("completed", "abandoned"):
                    raise ValueError(f"Cannot resume an attempt that has already been {att['attempt_status']}.")

            cursor.execute("""
                UPDATE coding_attempts SET
                    is_locked = 0,
                    lock_reason = '',
                    last_unlocked_at = ?
                WHERE id = ?
            """, (now_utc, attempt_id))
            conn.commit()

    record_session_lock_event(
        user_id=user_id,
        event_type="resume_requested",
        attempt_id=attempt_id,
        question_id=question_id,
        event_timestamp=now_utc,
        metadata=meta
    )
    record_session_lock_event(
        user_id=user_id,
        event_type="fullscreen_entered",
        attempt_id=attempt_id,
        question_id=question_id,
        event_timestamp=now_utc,
        metadata=meta
    )
    record_session_lock_event(
        user_id=user_id,
        event_type="resume_success",
        attempt_id=attempt_id,
        question_id=question_id,
        event_timestamp=now_utc,
        metadata=meta
    )
    res = record_session_lock_event(
        user_id=user_id,
        event_type="editor_unlocked",
        attempt_id=attempt_id,
        question_id=question_id,
        event_timestamp=now_utc,
        metadata=meta
    )

    return {
        "status": "unlocked",
        "is_locked": False,
        "attempt_id": attempt_id,
        "question_id": question_id,
        "event_id": res["id"],
        "event_timestamp_ist": res["event_timestamp_ist"]
    }

def is_attempt_locked(attempt_id: str, user_id: Optional[str] = None) -> bool:
    """Checks whether a coding attempt is in a locked state in the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        if user_id and user_id != "guest":
            cursor.execute("SELECT is_locked FROM coding_attempts WHERE id = ? AND user_id = ?", (attempt_id, user_id))
        else:
            cursor.execute("SELECT is_locked FROM coding_attempts WHERE id = ?", (attempt_id,))
        row = cursor.fetchone()
        return bool(row and row["is_locked"] == 1)

def get_user_lock_events(
    user_id: str,
    attempt_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Fetches user session lock and proctoring telemetry events in reverse chronological order."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM session_lock_events WHERE user_id = ?"
        params = [user_id]
        if attempt_id:
            query += " AND attempt_id = ?"
            params.append(attempt_id)
        query += " ORDER BY event_timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "attempt_id": r["attempt_id"],
                "question_id": r["question_id"],
                "event_type": r["event_type"],
                "event_timestamp": r["event_timestamp"],
                "event_timestamp_ist": r["event_timestamp_ist"],
                "metadata": json.loads(r["metadata_json"] or "{}"),
                "created_at": r["created_at"]
            }
            for r in rows
        ]


def get_user_attempts(user_id: str, question_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches coding attempts enforcing user_id ownership and recovering any stale sessions."""
    recover_stale_attempts(user_id)
    with get_db() as conn:
        cursor = conn.cursor()
        if question_id:
            cursor.execute("""
                SELECT a.*, q.title as question_title, q.topic as question_topic
                FROM coding_attempts a
                JOIN coding_questions q ON a.question_id = q.id
                WHERE a.user_id = ? AND a.question_id = ?
                ORDER BY a.created_at DESC LIMIT ?
            """, (user_id, question_id, limit))
        else:
            cursor.execute("""
                SELECT a.*, q.title as question_title, q.topic as question_topic
                FROM coding_attempts a
                JOIN coding_questions q ON a.question_id = q.id
                WHERE a.user_id = ?
                ORDER BY a.created_at DESC LIMIT ?
            """, (user_id, limit))
        
        rows = cursor.fetchall()
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "user_id": r["user_id"],
                "question_id": r["question_id"],
                "question_title": r["question_title"],
                "question_topic": r["question_topic"],
                "language": r["language"],
                "attempt_status": r["attempt_status"],
                "start_time": r["start_time"],
                "start_time_ist": format_timestamp_ist(r["start_time"]),
                "end_time": r["end_time"],
                "end_time_ist": format_timestamp_ist(r["end_time"]),
                "elapsed_coding_time_seconds": r["elapsed_coding_time_seconds"],
                "is_completed": bool(r["is_completed"]),
                "passed_count": r["passed_count"],
                "total_count": r["total_count"],
                "created_at": r["created_at"],
                "created_at_ist": format_timestamp_ist(r["created_at"])
            })
        return results

def get_user_viva_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetches viva results enforcing user_id ownership."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, question_id, overall_score, conceptual_score,
                   code_understanding_score, complexity_score, communication_score,
                   completed_at
            FROM ai_viva_results
            WHERE user_id = ?
            ORDER BY completed_at DESC LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "problem_id": r["question_id"],
                "overall_score": r["overall_score"],
                "conceptual": r["conceptual_score"],
                "code_understanding": r["code_understanding_score"],
                "complexity": r["complexity_score"],
                "communication": r["communication_score"],
                "date": format_timestamp_ist(r["completed_at"]),
                "completed_at": r["completed_at"]
            }
            for r in rows
        ]

def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Derives genuine student analytics directly from relational database tables.
    Eliminates mock percentages and fake hardcoded values.
    """
    STANDARD_TOPICS = [
        "Recursion & Backtracking",
        "Arrays & Hashing",
        "Strings",
        "Stack & Queue",
        "Dynamic Programming",
        "Algorithms & Two Pointers"
    ]

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Fetch user basic info
        cursor.execute("SELECT full_name, email FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        full_name = user_row["full_name"] if user_row else "Student Learner"

        # 2. Derive total solved (distinct questions completed)
        cursor.execute("SELECT COUNT(DISTINCT question_id) FROM coding_attempts WHERE user_id = ? AND is_completed = 1", (user_id,))
        total_solved = cursor.fetchone()[0] or 0

        # 3. Derive total attempts
        cursor.execute("SELECT COUNT(*) FROM coding_attempts WHERE user_id = ?", (user_id,))
        total_attempts = cursor.fetchone()[0] or 0

        # 4. Derive total practice coding time
        cursor.execute("SELECT COALESCE(SUM(elapsed_coding_time_seconds), 0) FROM coding_attempts WHERE user_id = ?", (user_id,))
        total_coding_seconds = cursor.fetchone()[0] or 0
        total_debug_time_mins = round(total_coding_seconds / 60)

        # 5. Derive topic mastery from student_progress table
        topic_mastery = {topic: 0 for topic in STANDARD_TOPICS}
        cursor.execute("SELECT topic, mastery_percentage FROM student_progress WHERE user_id = ?", (user_id,))
        for row in cursor.fetchall():
            topic_mastery[row["topic"]] = row["mastery_percentage"]

        # 6. Derive problem solving times map from completed attempts
        cursor.execute("""
            SELECT question_id, elapsed_coding_time_seconds, created_at, attempt_status, test_results_summary
            FROM coding_attempts
            WHERE user_id = ? AND is_completed = 1
            ORDER BY created_at DESC
        """, (user_id,))
        problem_solving_times = {}
        for row in cursor.fetchall():
            qid = row["question_id"]
            if qid not in problem_solving_times:
                secs = row["elapsed_coding_time_seconds"] or 0
                test_summary = {}
                try:
                    test_summary = json.loads(row["test_results_summary"]) if row["test_results_summary"] else {}
                except Exception:
                    pass
                problem_solving_times[qid] = {
                    "time_spent_seconds": secs,
                    "time_spent_formatted": format_duration(secs),
                    "completed_at": format_timestamp_ist(row["created_at"]),
                    "status": "completed",
                    "tab_switch_count": test_summary.get("tab_switch_count", 0),
                    "total_time_away_seconds": test_summary.get("total_time_away_seconds", 0),
                    "last_switch_timestamp": test_summary.get("last_switch_timestamp")
                }

        # 7. Derive recent activity log
        cursor.execute("""
            SELECT a.question_id, a.attempt_status, a.is_completed, a.elapsed_coding_time_seconds, a.created_at
            FROM coding_attempts a
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC LIMIT 10
        """, (user_id,))
        activity_log = []
        for r in cursor.fetchall():
            action = "Solved" if r["is_completed"] else ("Abandoned Attempt" if r["attempt_status"] == "abandoned" else "Attempted")
            activity_log.append({
                "action": action,
                "problem": r["question_id"],
                "timestamp": format_timestamp_ist(r["created_at"]),
                "time_spent": format_duration(r["elapsed_coding_time_seconds"] or 0),
                "time_spent_seconds": r["elapsed_coding_time_seconds"] or 0
            })

        # 8. Derive viva history
        viva_history = get_user_viva_history(user_id, limit=8)

        # 9. Derive coding scores analytics
        cursor.execute("SELECT AVG(overall_score), MAX(overall_score), COUNT(*) FROM coding_scores WHERE user_id = ?", (user_id,))
        score_row = cursor.fetchone()
        avg_coding_score = round(float(score_row[0]), 1) if score_row and score_row[0] is not None else 0.0
        best_coding_score = round(float(score_row[1]), 1) if score_row and score_row[1] is not None else 0.0
        total_scored_evaluations = int(score_row[2]) if score_row and score_row[2] is not None else 0

        # 10. Recent mistakes from cached profile if any
        cursor.execute("SELECT profile_json FROM user_profiles WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        cached_mistakes = []
        streak_days = 1 if total_attempts > 0 else 0
        hints_unlocked = 0
        if p_row:
            try:
                cached_data = json.loads(p_row["profile_json"])
                cached_mistakes = cached_data.get("recent_mistakes", [])
                hints_unlocked = cached_data.get("hints_unlocked", 0)
                if "streak_days" in cached_data and cached_data["streak_days"] > 0:
                    streak_days = cached_data["streak_days"]
            except Exception:
                pass

        profile_data = {
            "student_name": full_name,
            "streak_days": streak_days,
            "total_solved": total_solved,
            "total_attempts": total_attempts,
            "hints_unlocked": hints_unlocked,
            "total_debug_time_mins": total_debug_time_mins,
            "total_coding_time_seconds": total_coding_seconds,
            "topic_mastery": topic_mastery,
            "problem_solving_times": problem_solving_times,
            "average_coding_score": avg_coding_score,
            "best_coding_score": best_coding_score,
            "total_scored_evaluations": total_scored_evaluations,
            "recent_mistakes": cached_mistakes,
            "viva_history": viva_history,
            "activity_log": activity_log
        }
        return profile_data

def get_user_scores_history(user_id: str, question_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches evaluated coding scores with full breakdown enforcing user_id ownership."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = """
            SELECT s.*, q.title as question_title, q.topic as question_topic
            FROM coding_scores s
            JOIN coding_questions q ON s.question_id = q.id
            WHERE s.user_id = ?
        """
        params = [user_id]
        if question_id:
            query += " AND s.question_id = ?"
            params.append(question_id)
        query += " ORDER BY s.created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            breakdown = {}
            feedback = {}
            try:
                breakdown = json.loads(r["breakdown_json"]) if r["breakdown_json"] else {}
            except Exception:
                pass
            try:
                feedback = json.loads(r["feedback_json"]) if r["feedback_json"] else {}
            except Exception:
                pass

            results.append({
                "id": r["id"],
                "attempt_id": r["attempt_id"],
                "question_id": r["question_id"],
                "question_title": r["question_title"],
                "question_topic": r["question_topic"],
                "language": r["language"],
                "overall_score": r["overall_score"],
                "correctness_score": r["correctness_score"],
                "correctness_max": r["correctness_max"],
                "complexity_score": r["complexity_score"],
                "complexity_max": r["complexity_max"],
                "quality_score": r["quality_score"],
                "quality_max": r["quality_max"],
                "approach_score": r["approach_score"],
                "approach_max": r["approach_max"],
                "independent_score": r["independent_score"] if r["independent_score"] is not None else 10.0,
                "independent_max": r["independent_max"] if r["independent_max"] is not None else 10.0,
                "unique_hints_used": r["unique_hints_used"] or 0,
                "code_snapshot": r["code_snapshot"] or "",
                "memory_usage_mb": r["memory_usage_mb"],
                "is_renormalized": bool(r["is_renormalized"]),
                "evaluator_type": r["evaluator_type"],
                "breakdown": breakdown,
                "feedback": feedback,
                "execution_time_ms": r["execution_time_ms"],
                "coding_time_seconds": r["coding_time_seconds"],
                "tab_away_seconds": r["tab_away_seconds"],
                "passed_count": r["passed_count"],
                "total_count": r["total_count"],
                "status": r["status"],
                "created_at": r["created_at"],
                "created_at_ist": format_timestamp_ist(r["created_at"])
            })
        return results

def get_score_by_attempt_id(user_id: str, attempt_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific score record by attempt_id, strictly enforcing user_id ownership."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, q.title as question_title, q.topic as question_topic
            FROM coding_scores s
            JOIN coding_questions q ON s.question_id = q.id
            WHERE s.user_id = ? AND s.attempt_id = ?
        """, (user_id, attempt_id))
        r = cursor.fetchone()
        if not r:
            return None

        breakdown = {}
        feedback = {}
        try:
            breakdown = json.loads(r["breakdown_json"]) if r["breakdown_json"] else {}
        except Exception:
            pass
        try:
            feedback = json.loads(r["feedback_json"]) if r["feedback_json"] else {}
        except Exception:
            pass

        return {
            "id": r["id"],
            "attempt_id": r["attempt_id"],
            "question_id": r["question_id"],
            "question_title": r["question_title"],
            "question_topic": r["question_topic"],
            "language": r["language"],
            "overall_score": r["overall_score"],
            "correctness_score": r["correctness_score"],
            "correctness_max": r["correctness_max"],
            "complexity_score": r["complexity_score"],
            "complexity_max": r["complexity_max"],
            "quality_score": r["quality_score"],
            "quality_max": r["quality_max"],
            "approach_score": r["approach_score"],
            "approach_max": r["approach_max"],
            "independent_score": r["independent_score"] if r["independent_score"] is not None else 10.0,
            "independent_max": r["independent_max"] if r["independent_max"] is not None else 10.0,
            "unique_hints_used": r["unique_hints_used"] or 0,
            "code_snapshot": r["code_snapshot"] or "",
            "memory_usage_mb": r["memory_usage_mb"],
            "is_renormalized": bool(r["is_renormalized"]),
            "evaluator_type": r["evaluator_type"],
            "breakdown": breakdown,
            "feedback": feedback,
            "execution_time_ms": r["execution_time_ms"],
            "coding_time_seconds": r["coding_time_seconds"],
            "tab_away_seconds": r["tab_away_seconds"],
            "passed_count": r["passed_count"],
            "total_count": r["total_count"],
            "status": r["status"],
            "created_at": r["created_at"],
            "created_at_ist": format_timestamp_ist(r["created_at"])
        }

def get_user_score_analytics(user_id: str) -> Dict[str, Any]:
    """
    Computes genuine performance analytics directly from SQLite coding_scores records.
    Never uses random or hardcoded statistics.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Aggregates: overall average, best score, total evaluated attempts
        cursor.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                COALESCE(AVG(overall_score), 0.0) as avg_score,
                COALESCE(MAX(overall_score), 0.0) as best_score,
                COALESCE(SUM(passed_count), 0) as sum_passed,
                COALESCE(SUM(total_count), 0) as sum_total
            FROM coding_scores
            WHERE user_id = ?
        """, (user_id,))
        agg_row = cursor.fetchone()

        total_attempts = agg_row["total_attempts"] or 0
        avg_score = round(float(agg_row["avg_score"] or 0.0), 1)
        best_score = round(float(agg_row["best_score"] or 0.0), 1)
        sum_passed = agg_row["sum_passed"] or 0
        sum_total = agg_row["sum_total"] or 0
        accuracy_pct = round((sum_passed / max(1, sum_total)) * 100, 1) if sum_total > 0 else 0.0

        # 2. Total solved distinct questions
        cursor.execute("""
            SELECT COUNT(DISTINCT question_id) 
            FROM coding_attempts 
            WHERE user_id = ? AND is_completed = 1
        """, (user_id,))
        total_solved = cursor.fetchone()[0] or 0

        # 3. Topic-wise accuracy & average score
        cursor.execute("""
            SELECT 
                q.topic,
                COUNT(s.id) as attempts_count,
                AVG(s.overall_score) as topic_avg_score,
                SUM(s.passed_count) as topic_passed,
                SUM(s.total_count) as topic_total
            FROM coding_scores s
            JOIN coding_questions q ON s.question_id = q.id
            WHERE s.user_id = ?
            GROUP BY q.topic
        """, (user_id,))
        topic_accuracy = {}
        for row in cursor.fetchall():
            t_name = row["topic"]
            t_att = row["attempts_count"]
            t_avg = round(float(row["topic_avg_score"] or 0.0), 1)
            t_pass = row["topic_passed"] or 0
            t_tot = row["topic_total"] or 0
            t_acc = round((t_pass / max(1, t_tot)) * 100, 1) if t_tot > 0 else 0.0
            topic_accuracy[t_name] = {
                "attempts": t_att,
                "average_score": t_avg,
                "accuracy_percentage": t_acc
            }

        # 4. Chronological score improvement trend (last 25 attempts)
        cursor.execute("""
            SELECT s.id, s.question_id, q.title as question_title, s.overall_score, 
                   s.unique_hints_used, s.independent_score, s.created_at
            FROM coding_scores s
            JOIN coding_questions q ON s.question_id = q.id
            WHERE s.user_id = ?
            ORDER BY s.created_at ASC
            LIMIT 25
        """, (user_id,))
        trend = []
        for row in cursor.fetchall():
            trend.append({
                "score_id": row["id"],
                "question_id": row["question_id"],
                "question_title": row["question_title"],
                "score": round(float(row["overall_score"]), 1),
                "unique_hints_used": row["unique_hints_used"] or 0,
                "independent_score": round(float(row["independent_score"] if row["independent_score"] is not None else 10.0), 1),
                "timestamp_ist": format_timestamp_ist(row["created_at"])
            })

        # 5. Dimension averages (5 dimensions)
        cursor.execute("""
            SELECT 
                AVG(correctness_score) as avg_corr,
                AVG(complexity_score) as avg_comp,
                AVG(quality_score) as avg_qual,
                AVG(approach_score) as avg_appr,
                AVG(independent_score) as avg_indep
            FROM coding_scores
            WHERE user_id = ?
        """, (user_id,))
        dim_row = cursor.fetchone()
        dimension_averages = {
            "correctness": round(float(dim_row["avg_corr"] or 0.0), 1),
            "complexity": round(float(dim_row["avg_comp"] or 0.0), 1),
            "quality": round(float(dim_row["avg_qual"] or 0.0), 1),
            "approach": round(float(dim_row["avg_appr"] or 0.0), 1),
            "independent": round(float(dim_row["avg_indep"] or 10.0), 1)
        }

        # 6. Hint usage trend analysis
        cursor.execute("""
            SELECT 
                COALESCE(AVG(unique_hints_used), 0.0) as avg_hints,
                COUNT(*) as total_evals,
                COALESCE(SUM(CASE WHEN unique_hints_used <= 0 THEN 1 ELSE 0 END), 0) as zero_hints,
                COALESCE(SUM(CASE WHEN unique_hints_used = 1 THEN 1 ELSE 0 END), 0) as one_hint,
                COALESCE(SUM(CASE WHEN unique_hints_used = 2 THEN 1 ELSE 0 END), 0) as two_hints,
                COALESCE(SUM(CASE WHEN unique_hints_used >= 3 THEN 1 ELSE 0 END), 0) as three_plus_hints
            FROM coding_scores
            WHERE user_id = ?
        """, (user_id,))
        hint_row = cursor.fetchone()
        avg_hints = round(float(hint_row["avg_hints"] or 0.0), 1) if hint_row else 0.0
        hint_usage_trend = {
            "0_hints": hint_row["zero_hints"] if hint_row else 0,
            "1_hint": hint_row["one_hint"] if hint_row else 0,
            "2_hints": hint_row["two_hints"] if hint_row else 0,
            "3_plus_hints": hint_row["three_plus_hints"] if hint_row else 0,
            "breakdown": [
                {"category": "0 Hints (10/10)", "count": hint_row["zero_hints"] if hint_row else 0},
                {"category": "1 Hint (9/10)", "count": hint_row["one_hint"] if hint_row else 0},
                {"category": "2 Hints (7/10)", "count": hint_row["two_hints"] if hint_row else 0},
                {"category": "3+ Hints (≤4/10)", "count": hint_row["three_plus_hints"] if hint_row else 0}
            ]
        }

        # 7. Recent evaluations (latest 10)
        recent_evaluations = get_user_scores_history(user_id=user_id, limit=10)

        return {
            "average_score": avg_score,
            "best_score": best_score,
            "total_evaluated_attempts": total_attempts,
            "total_solved": total_solved,
            "accuracy_percentage": accuracy_pct,
            "topic_accuracy": topic_accuracy,
            "score_improvement_trend": trend,
            "dimension_averages": dimension_averages,
            "recent_evaluations": recent_evaluations,
            "hint_usage_trend": hint_usage_trend,
            "average_hints_per_problem": avg_hints
        }

def save_user_profile(user_id: str, profile_data: Dict[str, Any]):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_profiles (user_id, profile_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (user_id, json.dumps(profile_data))
        )
        conn.commit()

def get_user_recommendations(user_id: str, all_problems: list) -> list:
    profile = get_user_profile(user_id)
    topic_mastery = profile.get("topic_mastery", {})
    sorted_topics = sorted(topic_mastery.items(), key=lambda item: item[1])
    weakest_topic = sorted_topics[0][0] if sorted_topics else "Dynamic Programming"
    second_weakest = sorted_topics[1][0] if len(sorted_topics) > 1 else "Recursion & Backtracking"

    recommendations = []
    for p in all_problems:
        if p["topic"] == weakest_topic:
            recommendations.append({
                "problem": p,
                "reason": f"Strengthen your lowest mastery topic: {weakest_topic} ({topic_mastery.get(weakest_topic, 0)}%)",
                "priority": "High"
            })
        elif p["topic"] == second_weakest:
            recommendations.append({
                "problem": p,
                "reason": f"Follow-up practice for {second_weakest} ({topic_mastery.get(second_weakest, 0)}%)",
                "priority": "Medium"
            })
    
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
