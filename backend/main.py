from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import os
import random

from models import (
    Problem,
    TestCase,
    ExecuteRequest,
    ExecuteResponse,
    SessionRecordRequest,
    HintRequest,
    HintResponse,
    ExplainRequest,
    DebugGuideRequest,
    VivaStartRequest,
    VivaEvaluateRequest,
    VivaScoreResult,
    UpdateSettingsRequest,
    VivaQuestion,
    GenerateQuestionRequest,
    GenerateQuestionResponse,
    GenerateQuestionBatchResponse,
    RegisterRequest,
    LoginRequest,
    GoogleAuthRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    TabSwitchRecordRequest,
    UserResponse,
    AuthResponse,
    CodingScoreRecord,
    CodingScoreAnalyticsResponse,
    PasteAttemptRecordRequest,
    PasteAttemptResponse,
    PasteAttemptEvent,
    PDFReportRequest,
    SessionLockRequest,
    SessionLockResponse,
    SessionResumeRequest,
    SessionResumeResponse,
    SessionLockEventRequest,
    SessionLockEventResponse
)
from datetime import datetime, timezone
from problems import PROBLEMS
from executor import run_python_code, run_c_code, run_cpp_code, run_java_code
from mentor_ai import MentorAI
from analytics import AnalyticsManager
from question_store import QuestionStore
from rate_limiter import RateLimiter
from question_generator import TOPIC_SUBTOPICS, normalize_topic
from seed_data import seed_questions
from scoring_engine import CodingScoringEngine
import auth
import performance_service
import pdf_generator
from database import get_db, utc_iso_now, format_timestamp_ist, parse_utc_timestamp

app = FastAPI(
    title="CodeAcharya — AI Coding Mentor API",
    description="An Intelligent Personalized Programming Learning and Debugging Platform",
    version="1.0.0"
)

# Seed curated questions on startup into relational database
@app.on_event("startup")
def on_startup():
    try:
        seed_questions()
    except Exception as e:
        print(f"[Startup] Warning during question seeding: {e}")

# Enable CORS for frontend Vite app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mentor_ai = MentorAI()
scoring_engine = CodingScoringEngine()
analytics_mgr = AnalyticsManager()
question_store = QuestionStore()
rate_limiter = RateLimiter(max_requests=25, window_seconds=60)
auth_rate_limiter = RateLimiter(max_requests=30, window_seconds=60)


# Pre-load all persisted AI-generated questions into the in-memory problems registry
question_store.load_into_problems(PROBLEMS)

@app.get("/")
@app.get("/api/health")
def health_check():
    curated_count = sum(1 for p in PROBLEMS.values() if not getattr(p, "is_generated", False))
    generated_count = sum(1 for p in PROBLEMS.values() if getattr(p, "is_generated", False))
    return {
        "status": "online",
        "service": "CodeAcharya AI Coding Mentor API",
        "has_gemini_key": bool(mentor_ai.api_key),
        "has_bharatcode_key": bool(mentor_ai.api_key),
        "has_llm_key": bool(mentor_ai.api_key),
        "provider": "bharatcode",
        "persona": mentor_ai.persona,
        "model": mentor_ai.model,
        "total_problems": len(PROBLEMS),
        "curated_problems_count": curated_count,
        "generated_problems_count": generated_count
    }

# ----------------- Authentication & Session Dependencies -----------------
def get_token_from_request(request: Request) -> Optional[str]:
    # 1. Bearer token in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token:
            return token
    # 2. Cookie
    cookie_token = request.cookies.get("codeacharya_session")
    if cookie_token:
        return cookie_token.strip()
    return None

def get_current_user(request: Request) -> Dict[str, Any]:
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = auth.get_user_from_session(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_optional_current_user(request: Request) -> Optional[Dict[str, Any]]:
    token = get_token_from_request(request)
    if not token:
        return None
    return auth.get_user_from_session(token)

@app.post("/api/auth/register", response_model=AuthResponse)
def register_user(req: RegisterRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "global"
    allowed, retry_after = auth_rate_limiter.is_allowed(f"register_{client_ip}")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many registration attempts. Please wait {retry_after} seconds."
        )

    user, err = auth.create_user(req.full_name, req.email, req.password)
    if err or not user:
        raise HTTPException(status_code=400, detail=err or "Registration failed.")
    
    token = auth.create_session(user["id"])
    response.set_cookie(
        key="codeacharya_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=auth.SESSION_DURATION_HOURS * 3600,
        secure=False
    )
    return AuthResponse(
        user=UserResponse(**user),
        token=token,
        message="Registration successful"
    )

@app.post("/api/auth/login", response_model=AuthResponse)
def login_user(req: LoginRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "global"
    allowed, retry_after = auth_rate_limiter.is_allowed(f"login_{client_ip}")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Please wait {retry_after} seconds."
        )

    user, err = auth.authenticate_user(req.email, req.password)
    if err or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err or "Invalid email or password."
        )
    
    is_remember = bool(req.remember_me)
    token = auth.create_session(user["id"], is_remember_me=is_remember)
    cookie_duration = (auth.REMEMBER_ME_DURATION_DAYS * 86400) if is_remember else (auth.SESSION_DURATION_HOURS * 3600)
    response.set_cookie(
        key="codeacharya_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=cookie_duration,
        secure=False
    )
    return AuthResponse(
        user=UserResponse(**user),
        token=token,
        message="Login successful"
    )

@app.post("/api/auth/google", response_model=AuthResponse)
def google_auth(req: GoogleAuthRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "global"
    allowed, retry_after = auth_rate_limiter.is_allowed(f"google_{client_ip}")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many authentication attempts. Please wait {retry_after} seconds."
        )

    user, err = auth.authenticate_or_create_google_user(req.id_token)
    if err or not user:
        raise HTTPException(
            status_code=400,
            detail=err or "Google authentication failed. Please verify credentials."
        )

    is_remember = bool(req.remember_me)
    token = auth.create_session(user["id"], is_remember_me=is_remember)
    cookie_duration = (auth.REMEMBER_ME_DURATION_DAYS * 86400) if is_remember else (auth.SESSION_DURATION_HOURS * 3600)
    response.set_cookie(
        key="codeacharya_session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=cookie_duration,
        secure=False
    )
    return AuthResponse(
        user=UserResponse(**user),
        token=token,
        message="Google authentication successful"
    )

@app.get("/api/auth/google/config")
def get_google_auth_config():
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    return {
        "client_id": client_id,
        "configured": bool(client_id)
    }

@app.post("/api/auth/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(req: ForgotPasswordRequest, request: Request):
    client_ip = request.client.host if request.client else "global"
    allowed, retry_after = auth_rate_limiter.is_allowed(f"forgot_{client_ip}")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many password reset requests. Please wait {retry_after} seconds."
        )

    # Safe response: avoid account enumeration
    return ForgotPasswordResponse(
        status="success",
        message="If an account exists with this email, instructions to reset your password have been sent."
    )

@app.post("/api/auth/logout")
def logout_user(request: Request, response: Response):
    token = get_token_from_request(request)
    if token:
        auth.delete_session(token)
    response.delete_cookie(key="codeacharya_session")
    return {"message": "Logged out successfully", "status": "success"}

@app.get("/api/auth/me")
def get_current_authenticated_user(user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": user}


def _problem_dict_to_problem_obj(problem_dict: Dict[str, Any], language: str) -> Problem:
    """Helper to convert generated problem dict to Problem model."""
    tcs = []
    for tc_data in problem_dict.get("test_cases", []):
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

    if not tcs:
        tcs = [TestCase(id=1, input=1, expected_output=1, is_hidden=False)]

    prob_obj = Problem(
        id=problem_dict["id"],
        title=problem_dict["title"],
        difficulty=problem_dict["difficulty"],
        topic=problem_dict["topic"],
        subtopic=problem_dict.get("subtopic", ""),
        description=problem_dict["description"],
        examples=problem_dict.get("examples", []),
        constraints=problem_dict.get("constraints", []),
        starter_code=problem_dict.get("starter_code", {}),
        test_cases=tcs,
        learning_objectives=problem_dict.get("learning_objectives", []),
        common_misconceptions=problem_dict.get("common_misconceptions", []),
        input_format=problem_dict.get("inputFormat") or problem_dict.get("input_format", ""),
        output_format=problem_dict.get("outputFormat") or problem_dict.get("output_format", ""),
        hint=problem_dict.get("hint", ""),
        progressive_hints=problem_dict.get("progressive_hints", []),
        explanation=problem_dict.get("explanation", ""),
        expected_solution=problem_dict.get("expected_solution", {}),
        time_complexity=problem_dict.get("time_complexity", "O(N)"),
        space_complexity=problem_dict.get("space_complexity", "O(1)"),
        relevant_concepts=problem_dict.get("relevant_concepts", []),
        is_generated=True,
        source=problem_dict.get("source", "ai_generated")
    )
    return prob_obj

def _problem_obj_to_response(prob_obj: Problem, language: str) -> GenerateQuestionResponse:
    """Helper to convert Problem model to GenerateQuestionResponse."""
    starter_code_for_lang = (
        prob_obj.starter_code.get(language) or
        prob_obj.starter_code.get("python") or
        next(iter(prob_obj.starter_code.values()), "")
    )
    return GenerateQuestionResponse(
        id=prob_obj.id,
        title=prob_obj.title,
        topic=prob_obj.topic,
        subtopic=prob_obj.subtopic or "",
        difficulty=prob_obj.difficulty,
        language=language,
        description=prob_obj.description,
        inputFormat=prob_obj.input_format or "",
        outputFormat=prob_obj.output_format or "",
        constraints=prob_obj.constraints,
        examples=prob_obj.examples,
        hint=prob_obj.hint or "",
        progressive_hints=prob_obj.progressive_hints or [],
        explanation=prob_obj.explanation or "",
        expected_solution=prob_obj.expected_solution or {},
        time_complexity=prob_obj.time_complexity or "",
        space_complexity=prob_obj.space_complexity or "",
        relevant_concepts=prob_obj.relevant_concepts or [],
        starterCode=starter_code_for_lang,
        starter_code=prob_obj.starter_code,
        test_cases=[tc.dict() if hasattr(tc, 'dict') else tc for tc in prob_obj.test_cases],
        learning_objectives=prob_obj.learning_objectives,
        common_misconceptions=prob_obj.common_misconceptions,
        is_generated=True,
        source=prob_obj.source or "ai_generated",
        badge="AI Generated" if prob_obj.source == "ai_generated" else "Predefined Blueprint"
    )

@app.post("/api/generate-question", response_model=GenerateQuestionResponse)
@app.post("/api/problems/generate", response_model=GenerateQuestionResponse)
def generate_question(req: GenerateQuestionRequest):
    # 1. Rate Limiting Protection
    allowed, retry_after = rate_limiter.is_allowed("global")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Generation rate limit exceeded. Please wait {retry_after} seconds before requesting more questions."
        )

    # 2. Validation
    if not req.topic or not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic must be specified.")
    
    topic = normalize_topic(req.topic.strip())
    difficulty = req.difficulty.strip().capitalize()
    if difficulty not in ["Easy", "Medium", "Hard"]:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty '{req.difficulty}'. Must be Easy, Medium, or Hard.")
    
    language = req.language.strip().lower()
    if language in ["c++"]:
        language = "cpp"
    if language not in ["python", "c", "cpp", "java"]:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'. Supported languages: Python, C, C++, Java.")

    # 3. Aggregate session & persisted deduplication context
    all_prev_titles = list(req.previous_titles or [])
    all_prev_titles.extend(question_store.get_recent_titles(topic=topic, limit=20))
    # Include titles of existing static problems in this topic
    for p in PROBLEMS.values():
        if p.topic.lower() == topic.lower() and p.title not in all_prev_titles:
            all_prev_titles.append(p.title)

    all_prev_ids = list(req.previous_ids or [])
    all_prev_ids.extend(question_store.get_recent_ids(topic=topic, limit=30))

    known_descriptions = [
        p.description for p in PROBLEMS.values()
        if p.topic.lower() == topic.lower()
    ][:10]

    # 4. Generate problem via MentorAI
    try:
        problem_dict = mentor_ai.generate_coding_problem(
            topic=topic,
            difficulty=difficulty,
            language=language,
            subtopic=req.subtopic,
            previous_titles=all_prev_titles,
            previous_ids=all_prev_ids
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate problem: {str(e)}")

    if not problem_dict or not problem_dict.get("id"):
        raise HTTPException(status_code=500, detail="AI generator returned empty problem data.")

    # 5. Create Problem model & persist thread-safely
    try:
        prob_obj = _problem_dict_to_problem_obj(problem_dict, language)
        # Register in in-memory dict and persist to store
        PROBLEMS[prob_obj.id] = prob_obj
        question_store.save_problem(prob_obj)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to persist generated problem: {str(e)}")

    return _problem_obj_to_response(prob_obj, language)

@app.post("/api/problems/generate-batch", response_model=GenerateQuestionBatchResponse)
def generate_questions_batch(req: GenerateQuestionRequest):
    allowed, retry_after = rate_limiter.is_allowed("global")
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Generation rate limit exceeded. Please wait {retry_after} seconds before requesting more questions."
        )

    topic = normalize_topic(req.topic.strip())
    difficulty = req.difficulty.strip().capitalize()
    language = req.language.strip().lower()
    if language in ["c++"]:
        language = "cpp"
    if language not in ["python", "c", "cpp", "java"]:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'. Supported languages: Python, C, C++, Java.")

    count = max(1, min(5, req.count or 1))

    all_prev_titles = list(req.previous_titles or [])
    all_prev_titles.extend(question_store.get_recent_titles(topic=topic, limit=20))
    all_prev_ids = list(req.previous_ids or [])

    batch_dicts = mentor_ai.generate_coding_problems_batch(
        topic=topic,
        difficulty=difficulty,
        language=language,
        count=count,
        subtopic=req.subtopic,
        previous_titles=all_prev_titles,
        previous_ids=all_prev_ids
    )

    responses = []
    for problem_dict in batch_dicts:
        prob_obj = _problem_dict_to_problem_obj(problem_dict, language)
        PROBLEMS[prob_obj.id] = prob_obj
        question_store.save_problem(prob_obj)
        responses.append(_problem_obj_to_response(prob_obj, language))

    return GenerateQuestionBatchResponse(
        questions=responses,
        count=len(responses),
        topic=topic,
        difficulty=difficulty
    )

@app.get("/api/problems")
def list_problems(
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    subtopic: Optional[str] = None,
    source: Optional[str] = None
):
    result = []
    for pid, prob in PROBLEMS.items():
        if topic and prob.topic.lower() != topic.lower():
            continue
        if difficulty and prob.difficulty.lower() != difficulty.lower():
            continue
        if subtopic and getattr(prob, "subtopic", "").lower() != subtopic.lower():
            continue
        if source:
            s_clean = source.lower()
            is_gen = getattr(prob, "is_generated", False)
            if s_clean == "curated" and is_gen:
                continue
            if s_clean == "generated" and not is_gen:
                continue

        is_gen = getattr(prob, "is_generated", False)
        badge = "AI Generated" if is_gen else "Curated"
        result.append({
            "id": prob.id,
            "title": prob.title,
            "difficulty": prob.difficulty,
            "topic": prob.topic,
            "subtopic": getattr(prob, "subtopic", ""),
            "test_cases_count": len(prob.test_cases),
            "objectives": prob.learning_objectives,
            "is_generated": is_gen,
            "source": getattr(prob, "source", "curated"),
            "badge": badge
        })
    return result

@app.get("/api/topics")
def list_topics():
    topics_map = {}
    for p in PROBLEMS.values():
        if p.topic not in topics_map:
            subtopics_list = TOPIC_SUBTOPICS.get(p.topic, [])
            topics_map[p.topic] = {
                "name": p.topic,
                "counts": {"Easy": 0, "Medium": 0, "Hard": 0, "Total": 0},
                "curated_count": 0,
                "generated_count": 0,
                "subtopics": subtopics_list,
                "problems": []
            }
        topics_map[p.topic]["counts"][p.difficulty] = topics_map[p.topic]["counts"].get(p.difficulty, 0) + 1
        topics_map[p.topic]["counts"]["Total"] += 1

        is_gen = getattr(p, "is_generated", False)
        if is_gen:
            topics_map[p.topic]["generated_count"] += 1
        else:
            topics_map[p.topic]["curated_count"] += 1

        topics_map[p.topic]["problems"].append({
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "subtopic": getattr(p, "subtopic", ""),
            "is_generated": is_gen,
            "badge": "AI Generated" if is_gen else "Curated"
        })
    return list(topics_map.values())

@app.delete("/api/problems/generated")
@app.post("/api/problems/clear-generated")
def clear_generated_problems():
    removed_count = question_store.clear_all(PROBLEMS)
    return {
        "status": "success",
        "message": f"Successfully removed {removed_count} generated questions.",
        "remaining_total": len(PROBLEMS),
        "curated_total": sum(1 for p in PROBLEMS.values() if not getattr(p, "is_generated", False))
    }

@app.get("/api/problems/{problem_id}")
def get_problem(problem_id: str):
    if problem_id not in PROBLEMS:
        raise HTTPException(status_code=404, detail="Problem not found")
    return PROBLEMS[problem_id]

@app.post("/api/execute", response_model=ExecuteResponse)
def execute_code(req: ExecuteRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    if req.problem_id not in PROBLEMS:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Security check: verify session is not locked
    if req.is_locked:
        raise HTTPException(status_code=403, detail="Execution rejected: Coding session is locked. Full-screen mode is required to continue coding.")

    if req.attempt_id:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, is_locked, attempt_status FROM coding_attempts WHERE id = ?", (req.attempt_id,))
            att = cursor.fetchone()
            if att:
                if user and att["user_id"] != user["id"]:
                    raise HTTPException(status_code=403, detail="Forbidden: Attempt ownership mismatch.")
                if att["is_locked"] == 1:
                    raise HTTPException(status_code=403, detail="Execution rejected: Coding session is locked. Full-screen mode is required to continue coding.")
    elif user:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_locked FROM coding_attempts 
                WHERE user_id = ? AND question_id = ? AND attempt_status IN ('running', 'paused')
                ORDER BY created_at DESC LIMIT 1
            """, (user["id"], req.problem_id))
            active_att = cursor.fetchone()
            if active_att and active_att["is_locked"] == 1:
                raise HTTPException(status_code=403, detail="Execution rejected: Active coding attempt is locked.")
    
    problem = PROBLEMS[req.problem_id]
    
    if req.language == "python":
        res = run_python_code(req.code, req.problem_id, problem.test_cases)
    elif req.language in ["c"]:
        res = run_c_code(req.code, req.problem_id, problem.test_cases)
    elif req.language in ["cpp", "c++"]:
        res = run_cpp_code(req.code, req.problem_id, problem.test_cases)
    elif req.language in ["java"]:
        res = run_java_code(req.code, req.problem_id, problem.test_cases)
    else:
        raise HTTPException(status_code=400, detail=f"Language '{req.language}' not currently supported.")

    # Strict completion condition:
    # 1. res.status == "success" (compilation and execution succeeded, no runtime error/timeout)
    # 2. res.total_count > 0 (at least one executable testcase required; empty suites do not complete)
    # 3. res.passed_count == res.total_count (all testcases passed)
    passed = (res.status == "success" and res.total_count > 0 and res.passed_count == res.total_count)
    session_status = "completed" if passed else "running"
    time_spent = req.time_spent_seconds or 0

    res.time_spent_seconds = time_spent
    res.session_status = session_status
    res.is_completed = passed

    # Record analytics per-user if authenticated, otherwise fallback
    tab_switches = req.tab_switch_count or 0
    away_secs = req.total_time_away_seconds or 0
    last_sw = req.last_switch_timestamp
    tab_history = req.tab_switch_history or []

    res.tab_switch_count = tab_switches
    res.total_time_away_seconds = away_secs
    res.last_switch_timestamp = last_sw
    res.tab_switch_history = tab_history

    # Calculate transparent score out of 100 with configurable weights and renormalization
    unique_hints = req.unique_hints_used or 0
    score_result = scoring_engine.evaluate(
        problem=problem,
        code=req.code,
        language=req.language,
        execution_status=res.status,
        passed_count=res.passed_count,
        total_count=res.total_count,
        test_results=res.results,
        runtime_ms=res.runtime_ms,
        coding_time_seconds=time_spent,
        time_spent_away_seconds=away_secs,
        tab_switch_count=tab_switches,
        unique_hints_used=unique_hints,
        ast_feedback=res.ast_feedback,
        custom_weights=req.custom_weights
    )

    res.overall_score = score_result["overall_score"]
    res.unique_hints_used = unique_hints
    res.independent_score = score_result.get("independent_score", 10)
    res.score_data = score_result

    idempotency_key = req.idempotency_key or CodingScoringEngine.generate_idempotency_key(
        user["id"] if user else "guest",
        problem.id,
        req.code
    )

    tr_list = [
        {
            "test_id": r.test_id,
            "passed": r.passed,
            "execution_time_ms": r.execution_time_ms,
            "is_hidden": False,
            "error": r.error
        }
        for r in res.results
    ]

    if user:
        attempt_id = auth.record_user_attempt(
            user_id=user["id"], 
            problem_id=problem.id, 
            topic=problem.topic, 
            passed=passed, 
            hints_used=unique_hints,
            unique_hints_used=unique_hints,
            time_spent_seconds=time_spent,
            session_status=session_status,
            tab_switch_count=tab_switches,
            total_time_away_seconds=away_secs,
            last_switch_timestamp=last_sw,
            tab_switch_history=tab_history,
            code=req.code,
            test_results_list=tr_list,
            language=req.language,
            score_data=score_result,
            idempotency_key=idempotency_key,
            passed_count=res.passed_count,
            total_count=res.total_count,
            attempt_id=req.attempt_id,
            start_time=req.start_time,
            end_time=req.end_time,
            paused_seconds=req.paused_seconds
        )
        res.attempt_id = attempt_id
        if not passed and res.ast_feedback and res.ast_feedback.get("suspected_bugs"):
            for bug in res.ast_feedback["suspected_bugs"][:1]:
                auth.record_user_mistake(user["id"], problem.topic, bug)
    else:
        analytics_mgr.record_attempt(
            problem_id=problem.id, 
            topic=problem.topic, 
            passed=passed, 
            hints_used=0,
            time_spent_seconds=time_spent,
            session_status=session_status,
            tab_switch_count=tab_switches,
            total_time_away_seconds=away_secs,
            last_switch_timestamp=last_sw,
            tab_switch_history=tab_history
        )
        if not passed and res.ast_feedback and res.ast_feedback.get("suspected_bugs"):
            for bug in res.ast_feedback["suspected_bugs"][:1]:
                analytics_mgr.record_mistake(problem.topic, bug)

    return res

@app.get("/api/scores/history")
def get_user_scores_history(
    question_id: Optional[str] = None,
    limit: Optional[int] = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    return auth.get_user_scores_history(user["id"], question_id=question_id, limit=limit or 50)

@app.get("/api/scores/analytics", response_model=CodingScoreAnalyticsResponse)
def get_user_scores_analytics(user: Dict[str, Any] = Depends(get_current_user)):
    return auth.get_user_score_analytics(user["id"])

@app.get("/api/scores/{attempt_id}")
def get_attempt_score(attempt_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    score_record = auth.get_score_by_attempt_id(user["id"], attempt_id)
    if not score_record:
        raise HTTPException(status_code=404, detail="Score evaluation record not found or access denied.")
    return score_record

@app.post("/api/session/record")
def record_session_state(req: SessionRecordRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    problem = PROBLEMS.get(req.problem_id)
    topic = problem.topic if problem else "General"
    time_spent = req.time_spent_seconds or 0
    tab_switches = req.tab_switch_count or 0
    away_secs = req.total_time_away_seconds or 0
    last_sw = req.last_switch_timestamp
    tab_history = req.tab_switch_history or []

    status_val = req.session_status or req.status or "completed"
    p_cnt = req.passed_count if req.passed_count is not None else (req.passed_test_cases or 0)
    t_cnt = req.total_count if req.total_count is not None else (req.total_test_cases or 0)

    # Security check: do not allow completing an attempt while locked
    if user and req.attempt_id and status_val == "completed":
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_locked FROM coding_attempts WHERE id = ?", (req.attempt_id,))
            att_row = cursor.fetchone()
            if att_row and att_row["is_locked"] == 1:
                raise HTTPException(status_code=403, detail="Cannot complete session while locked. Restore full-screen mode first.")

    score_dict = None
    if req.overall_score is not None:
        score_dict = {"overall_score": float(req.overall_score)}

    saved_attempt_id = None
    if user:
        saved_attempt_id = auth.record_user_session(
            user_id=user["id"],
            problem_id=req.problem_id,
            topic=topic,
            status=status_val,
            time_spent_seconds=time_spent,
            passed_count=p_cnt,
            total_count=t_cnt,
            tab_switch_count=tab_switches,
            total_time_away_seconds=away_secs,
            last_switch_timestamp=last_sw,
            tab_switch_history=tab_history,
            attempt_id=req.attempt_id,
            start_time=req.start_time,
            end_time=req.end_time,
            paused_seconds=req.paused_seconds,
            code=req.code or "",
            score_data=score_dict,
            is_locked=req.is_locked,
            lock_reason=req.lock_reason
        )
    else:
        analytics_mgr.record_session(
            problem_id=req.problem_id,
            topic=topic,
            status=req.status,
            time_spent_seconds=time_spent,
            passed_count=req.passed_count or 0,
            total_count=req.total_count or 0,
            tab_switch_count=tab_switches,
            total_time_away_seconds=away_secs,
            last_switch_timestamp=last_sw,
            tab_switch_history=tab_history
        )

    return {
        "status": "success",
        "attempt_id": saved_attempt_id or req.attempt_id,
        "recorded_status": req.status,
        "problem_id": req.problem_id,
        "time_spent_seconds": time_spent,
        "tab_switch_count": tab_switches,
        "total_time_away_seconds": away_secs,
        "last_switch_timestamp": last_sw,
        "tab_switch_history": tab_history
    }

@app.post("/api/assessment/paste-attempt", response_model=PasteAttemptResponse)
def record_paste_attempt_endpoint(
    req: PasteAttemptRecordRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Records a blocked paste attempt during restricted assessment mode.
    Never collects or stores clipboard content.
    """
    res = auth.record_user_paste_attempt(
        user_id=user["id"],
        page_type=req.page_type,
        question_id=req.question_id,
        attempt_id=req.attempt_id,
        event_timestamp=req.event_timestamp
    )
    is_dup = res.get("is_deduplicated", False)
    return PasteAttemptResponse(
        status="success",
        recorded=True,
        duplicate=is_dup,
        message="Blocked paste attempt logged under assessment policy." if not is_dup else "Duplicate burst paste attempt suppressed.",
        record=res
    )

@app.get("/api/assessment/paste-attempts")
def get_user_paste_attempts_endpoint(
    page_type: Optional[str] = None,
    question_id: Optional[str] = None,
    attempt_id: Optional[str] = None,
    limit: Optional[int] = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Returns user's blocked paste attempt records formatted in IST (Asia/Kolkata).
    """
    events = auth.get_user_paste_attempts(
        user_id=user["id"],
        page_type=page_type,
        question_id=question_id,
        attempt_id=attempt_id,
        limit=limit or 50
    )
    return {
        "status": "success",
        "events": events
    }

@app.post("/api/session/lock", response_model=SessionLockResponse)
def lock_session(req: SessionLockRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    """
    Transitions an active coding session into locked state upon full-screen exit or page blur.
    Makes editor read-only, pauses timers, and records telemetry events.
    """
    user_id = user["id"] if user else "guest"
    reason = req.reason or "fullscreen_exit"
    now_utc = req.event_timestamp or utc_iso_now()
    now_ist = format_timestamp_ist(now_utc)

    try:
        res = auth.lock_coding_session(
            user_id=user_id,
            attempt_id=req.attempt_id,
            question_id=req.question_id,
            reason=reason,
            event_timestamp=now_utc,
            metadata=req.metadata
        )
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))

    return SessionLockResponse(
        status="locked",
        is_locked=True,
        attempt_id=req.attempt_id,
        question_id=req.question_id,
        reason=reason,
        message="Assessment session is locked. Full-screen mode is required to continue coding.",
        event_timestamp_ist=now_ist
    )

@app.post("/api/session/resume", response_model=SessionResumeResponse)
def resume_session(req: SessionResumeRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    """
    Restores an active coding session after verifying that browser full-screen mode has been restored.
    Rejects any resume attempt if fullscreen verification is false or rejected.
    """
    user_id = user["id"] if user else "guest"
    now_utc = req.event_timestamp or utc_iso_now()
    now_ist = format_timestamp_ist(now_utc)

    if not req.fullscreen_verified:
        auth.record_session_lock_event(
            user_id=user_id,
            event_type="resume_requested",
            attempt_id=req.attempt_id,
            question_id=req.question_id,
            event_timestamp=now_utc,
            metadata=req.metadata
        )
        auth.record_session_lock_event(
            user_id=user_id,
            event_type="resume_failed",
            attempt_id=req.attempt_id,
            question_id=req.question_id,
            event_timestamp=now_utc,
            metadata={"reason": "fullscreen_verification_failed"}
        )
        raise HTTPException(
            status_code=400,
            detail="Verification failed: Document is not in browser full-screen mode. Full-screen mode is required to resume coding."
        )

    try:
        res = auth.resume_coding_session(
            user_id=user_id,
            attempt_id=req.attempt_id,
            question_id=req.question_id,
            fullscreen_verified=req.fullscreen_verified,
            event_timestamp=now_utc,
            metadata=req.metadata
        )
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    return SessionResumeResponse(
        status="unlocked",
        is_locked=False,
        attempt_id=req.attempt_id,
        question_id=req.question_id,
        message="Full-screen mode verified. Editor unlocked and session resumed.",
        event_timestamp_ist=now_ist
    )

@app.post("/api/session/lock-event", response_model=SessionLockEventResponse)
def record_lock_event(req: SessionLockEventRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    """
    Logs structured full-screen proctoring and focus telemetry events.
    Enforces deduplication within 1.0s window.
    """
    user_id = user["id"] if user else "guest"
    valid_types = {
        "fullscreen_entered", "fullscreen_exited", 
        "page_hidden", "page_visible", 
        "editor_locked", "editor_unlocked", 
        "resume_requested", "resume_success", "resume_failed"
    }
    if req.event_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid event_type '{req.event_type}'. Valid types: {valid_types}")

    res = auth.record_session_lock_event(
        user_id=user_id,
        event_type=req.event_type,
        attempt_id=req.attempt_id,
        question_id=req.question_id,
        event_timestamp=req.event_timestamp,
        metadata=req.metadata
    )
    is_dup = res.get("duplicate", False)
    return SessionLockEventResponse(
        status="success",
        event_id=res["id"],
        event_type=req.event_type,
        recorded=not is_dup,
        duplicate=is_dup,
        message="Event recorded." if not is_dup else "Duplicate event throttled.",
        event_timestamp_ist=res.get("event_timestamp_ist")
    )

@app.get("/api/session/lock-events")
def get_lock_events_endpoint(
    attempt_id: Optional[str] = None,
    limit: Optional[int] = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieves the user's session lock and proctoring telemetry audit trail.
    """
    events = auth.get_user_lock_events(user["id"], attempt_id=attempt_id, limit=limit or 50)
    return {
        "status": "success",
        "events": events
    }


@app.post("/api/hints", response_model=HintResponse)
def get_hint(req: HintRequest):
    if req.problem_id not in PROBLEMS:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    problem = PROBLEMS[req.problem_id]
    hint = mentor_ai.get_progressive_hint(
        problem=problem,
        code=req.code,
        language=req.language,
        hint_level=req.hint_level,
        error_context=req.error_context
    )
    return hint

@app.post("/api/hints/independent-score")
def get_independent_score_endpoint(payload: Dict[str, Any]):
    from scoring_engine import calculate_independent_score
    unique_hints = int(payload.get("unique_hints_used", 0))
    score = calculate_independent_score(unique_hints)
    return {
        "unique_hints_used": unique_hints,
        "independent_score": score,
        "score": score,
        "max_score": 10,
        "points_deducted": 10 - score
    }


@app.post("/api/explain")
def explain_code(req: ExplainRequest):
    problem = PROBLEMS.get(req.problem_id)
    if not problem:
        if req.problem_statement or req.problem_title:
            problem = Problem(
                id=req.problem_id,
                title=req.problem_title or "Coding Problem",
                difficulty="Medium",
                topic="Algorithms",
                description=req.problem_statement or "",
                examples=[],
                constraints=[],
                starter_code={}
            )
        else:
            raise HTTPException(status_code=404, detail="Problem not found")
    return mentor_ai.explain_code(
        problem=problem,
        code=req.code,
        language=req.language,
        selected_code=req.selected_code,
        problem_title=req.problem_title,
        problem_statement=req.problem_statement
    )

@app.post("/api/debug")
def debug_guide(req: DebugGuideRequest):
    problem = PROBLEMS.get(req.problem_id)
    if not problem:
        if req.problem_statement or req.problem_title:
            problem = Problem(
                id=req.problem_id,
                title=req.problem_title or "Coding Problem",
                difficulty="Medium",
                topic="Algorithms",
                description=req.problem_statement or "",
                examples=[],
                constraints=[],
                starter_code={}
            )
        else:
            raise HTTPException(status_code=404, detail="Problem not found")
    return mentor_ai.generate_debugging_guide(
        problem=problem,
        code=req.code,
        language=req.language,
        error_message=req.error_message,
        failing_input=req.failing_input,
        expected_output=req.expected_output,
        actual_output=req.actual_output,
        has_run=req.has_run,
        problem_title=req.problem_title,
        problem_statement=req.problem_statement
    )

@app.post("/api/viva/start", response_model=List[VivaQuestion])
def start_viva(req: VivaStartRequest):
    if req.problem_id not in PROBLEMS:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem = PROBLEMS[req.problem_id]
    return mentor_ai.start_viva_session(problem, req.code, req.language)

@app.post("/api/viva/evaluate", response_model=VivaScoreResult)
def evaluate_viva(req: VivaEvaluateRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    if req.problem_id not in PROBLEMS:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem = PROBLEMS[req.problem_id]
    
    # Support deterministic AI provider failure simulation (Test G)
    if req.simulate_failure:
        raise HTTPException(
            status_code=502,
            detail="AI evaluation service timeout: Simulated provider failure. Please retry."
        )

    # Track and validate answer modality
    modality = req.answer_modality if req.answer_modality in ("typed", "voice_transcribed", "audio_recorded") else "typed"
    comm_label = "Verbal Response Clarity" if modality == "voice_transcribed" else "Communication & Clarity"

    # Empty answer validation
    if not req.student_answer or not req.student_answer.strip():
        applicable_dims, _ = mentor_ai._get_applicable_dimensions_and_weights(req.category, req.question, modality)
        return VivaScoreResult(
            conceptual_score=0 if "conceptual_score" in applicable_dims else None,
            code_understanding_score=0 if "code_understanding_score" in applicable_dims else None,
            complexity_score=0 if "complexity_score" in applicable_dims else None,
            communication_score=0 if "communication_score" in applicable_dims else None,
            overall_score=0,
            feedback="No substantive answer was provided. Please formulate a clear response addressing the question.",
            ideal_points_covered=[],
            missing_concepts=["An explanation addressing the question requirements"],
            suggested_improvement=req.hint_guidance or "State the main algorithmic intuition and relevant constraints.",
            answer_relevance="irrelevant",
            applicable_dimensions=applicable_dims,
            should_retry=True,
            question_id=req.question_id,
            category=req.category,
            status="Evaluated",
            answer_modality=modality,
            communication_label=comm_label
        )

    question_obj = VivaQuestion(
        id=req.question_id,
        category=req.category,
        question=req.question,
        hint_guidance=req.hint_guidance
    )

    try:
        result = mentor_ai.evaluate_viva_answer(
            problem=problem,
            code=req.code,
            question=question_obj,
            student_answer=req.student_answer,
            answer_modality=modality
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"AI evaluation service encountered an error: {str(e)}. Please retry."
        )

    # Populate matching schema aliases
    result.scores = {
        "conceptualUnderstanding": result.conceptual_score,
        "codeUnderstanding": result.code_understanding_score,
        "complexityAnalysis": result.complexity_score,
        "communication": result.communication_score
    }
    result.correctPoints = result.ideal_points_covered
    result.examinerRemarks = result.feedback
    result.followUpHint = result.suggested_improvement
    result.answer_modality = modality
    result.communication_label = comm_label

    if result.overall_score > 0:
        score_payload = {
            "overall": result.overall_score,
            "conceptual": result.conceptual_score if result.conceptual_score is not None else 0,
            "code_understanding": result.code_understanding_score if result.code_understanding_score is not None else 0,
            "complexity": result.complexity_score if result.complexity_score is not None else 0,
            "communication": result.communication_score if result.communication_score is not None else 0
        }
        if user:
            auth.record_user_viva(user["id"], problem.id, score_payload)
        else:
            analytics_mgr.record_viva(problem.id, score_payload)

    return result

@app.get("/api/profile")
def get_student_profile(user: Dict[str, Any] = Depends(get_current_user)):
    return auth.get_user_profile(user["id"])

@app.get("/api/attempts")
def get_user_attempts(
    question_id: Optional[str] = None,
    limit: Optional[int] = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    return auth.get_user_attempts(user["id"], question_id=question_id, limit=limit or 50)

@app.get("/api/tab-switches")
def get_user_tab_switches(
    attempt_id: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    return auth.get_user_tab_switches(user["id"], attempt_id=attempt_id)

@app.post("/api/tab-switch/record")
def record_tab_switch_event(
    req: TabSwitchRecordRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    from database import get_db, utc_iso_now, format_timestamp_ist, parse_utc_timestamp
    import secrets
    now_utc_dt = datetime.now(timezone.utc)
    now_utc = now_utc_dt.isoformat()

    ev_dt = parse_utc_timestamp(req.event_timestamp) if req.event_timestamp else None

    ret_dt = None
    if req.return_timestamp and str(req.return_timestamp).strip() not in (
        "Away...", "Active", "Pending Return", "Awaiting return", "Incomplete", "None", "null", ""
    ):
        ret_dt = parse_utc_timestamp(req.return_timestamp)
    ret_time = ret_dt.isoformat() if ret_dt else None

    raw_status = (req.event_status or "").lower().strip()
    if raw_status:
        status = raw_status
    else:
        status = "returned" if ret_dt else "away"

    if not ret_dt and status == "returned":
        status = "incomplete"

    ts_id = req.id or f"ts_{secrets.token_hex(8)}"
    with get_db() as conn:
        cursor = conn.cursor()
        valid_attempt_id = None
        if req.attempt_id:
            cursor.execute("SELECT id FROM coding_attempts WHERE id = ?", (req.attempt_id,))
            if cursor.fetchone():
                valid_attempt_id = req.attempt_id

        # Update last activity on coding_attempt
        if valid_attempt_id:
            cursor.execute("UPDATE coding_attempts SET last_activity_at = ? WHERE id = ?", (now_utc, valid_attempt_id))

        # Check if closing an existing open/away event
        if ret_dt:
            open_ts = None
            if req.id:
                cursor.execute("""
                    SELECT id, event_timestamp, attempt_id, question_id FROM tab_switch_events
                    WHERE id = ? AND user_id = ?
                """, (req.id, user["id"]))
                open_ts = cursor.fetchone()

            if not open_ts and valid_attempt_id:
                cursor.execute("""
                    SELECT id, event_timestamp, attempt_id, question_id FROM tab_switch_events
                    WHERE user_id = ? AND attempt_id = ?
                      AND (return_timestamp IS NULL OR event_status IN ('away', 'incomplete'))
                    ORDER BY event_timestamp DESC LIMIT 1
                """, (user["id"], valid_attempt_id))
                open_ts = cursor.fetchone()

            if not open_ts and req.question_id:
                cursor.execute("""
                    SELECT id, event_timestamp, attempt_id, question_id FROM tab_switch_events
                    WHERE user_id = ? AND question_id = ?
                      AND (return_timestamp IS NULL OR event_status IN ('away', 'incomplete'))
                    ORDER BY event_timestamp DESC LIMIT 1
                """, (user["id"], req.question_id))
                open_ts = cursor.fetchone()

            if not open_ts:
                cursor.execute("""
                    SELECT id, event_timestamp, attempt_id, question_id FROM tab_switch_events
                    WHERE user_id = ?
                      AND (return_timestamp IS NULL OR event_status IN ('away', 'incomplete'))
                    ORDER BY event_timestamp DESC LIMIT 1
                """, (user["id"],))
                open_ts = cursor.fetchone()

            if open_ts:
                target_id = open_ts["id"]
                open_ev_dt = parse_utc_timestamp(open_ts["event_timestamp"]) or ev_dt or now_utc_dt
                away_s = max(0, int(round((ret_dt - open_ev_dt).total_seconds())))
                if away_s == 0 and req.time_away_seconds and req.time_away_seconds > 0:
                    away_s = max(0, int(round(float(req.time_away_seconds))))

                cursor.execute("""
                    UPDATE tab_switch_events SET
                        attempt_id = COALESCE(?, attempt_id),
                        question_id = COALESCE(?, question_id),
                        return_timestamp = ?,
                        time_away_seconds = ?,
                        event_status = 'returned'
                    WHERE id = ?
                """, (valid_attempt_id, req.question_id, ret_time, away_s, target_id))
                conn.commit()
                return {
                    "id": target_id,
                    "status": "success",
                    "event_status": "returned",
                    "time_away_seconds": away_s,
                    "event_timestamp_ist": format_timestamp_ist(open_ts["event_timestamp"]),
                    "return_timestamp_ist": format_timestamp_ist(ret_time)
                }

            # No open event found, but return timestamp provided
            if ev_dt:
                away_s = max(0, int(round((ret_dt - ev_dt).total_seconds())))
                if away_s == 0 and req.time_away_seconds and req.time_away_seconds > 0:
                    away_s = max(0, int(round(float(req.time_away_seconds))))
                event_time = ev_dt.isoformat()
            elif req.time_away_seconds and req.time_away_seconds > 0:
                away_s = max(0, int(round(float(req.time_away_seconds))))
                ev_dt = ret_dt - timedelta(seconds=away_s)
                event_time = ev_dt.isoformat()
            else:
                # No event_timestamp, no open event, and 0 duration away:
                # Do NOT create a false 0s returned event with identical timestamps!
                away_s = 0
                status = "incomplete"
                ret_time = None
                ev_dt = now_utc_dt
                event_time = ev_dt.isoformat()

            cursor.execute("""
                INSERT INTO tab_switch_events (
                    id, user_id, attempt_id, question_id, event_timestamp, return_timestamp, time_away_seconds, event_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts_id,
                user["id"],
                valid_attempt_id,
                req.question_id,
                event_time,
                ret_time,
                away_s,
                status,
                now_utc
            ))
            conn.commit()
            return {
                "id": ts_id,
                "status": "success",
                "event_status": status,
                "time_away_seconds": away_s,
                "event_timestamp_ist": format_timestamp_ist(event_time),
                "return_timestamp_ist": format_timestamp_ist(ret_time) if ret_time else "Active / Pending Return"
            }

        # Handling an 'away' or incomplete event (ret_dt is None)
        ev_dt = ev_dt or now_utc_dt
        event_time = ev_dt.isoformat()
        away_s = 0
        if status not in ("away", "incomplete", "active"):
            status = "away"

        # Deduplication check for rapid consecutive away events
        cursor.execute("""
            SELECT id, event_timestamp FROM tab_switch_events
            WHERE user_id = ? AND (return_timestamp IS NULL OR event_status IN ('away', 'incomplete'))
            ORDER BY event_timestamp DESC LIMIT 1
        """, (user["id"],))
        recent_open = cursor.fetchone()
        if recent_open:
            rec_dt = parse_utc_timestamp(recent_open["event_timestamp"])
            if rec_dt and abs((ev_dt - rec_dt).total_seconds()) < 3:
                # Update attempt_id / question_id if now available
                cursor.execute("""
                    UPDATE tab_switch_events SET
                        attempt_id = COALESCE(?, attempt_id),
                        question_id = COALESCE(?, question_id)
                    WHERE id = ?
                """, (valid_attempt_id, req.question_id, recent_open["id"]))
                conn.commit()
                return {
                    "id": recent_open["id"],
                    "status": "success",
                    "event_status": status,
                    "time_away_seconds": 0,
                    "event_timestamp_ist": format_timestamp_ist(recent_open["event_timestamp"]),
                    "return_timestamp_ist": "Active / Pending Return"
                }

        cursor.execute("""
            INSERT INTO tab_switch_events (
                id, user_id, attempt_id, question_id, event_timestamp, return_timestamp, time_away_seconds, event_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ts_id,
            user["id"],
            valid_attempt_id,
            req.question_id,
            event_time,
            None,
            0,
            status,
            now_utc
        ))
        conn.commit()
    return {
        "id": ts_id,
        "status": "success",
        "event_status": status,
        "time_away_seconds": 0,
        "event_timestamp_ist": format_timestamp_ist(event_time),
        "return_timestamp_ist": "Active / Pending Return"
    }

@app.get("/api/viva/history")
def get_viva_history(
    limit: Optional[int] = 20,
    user: Dict[str, Any] = Depends(get_current_user)
):
    return auth.get_user_viva_history(user["id"], limit=limit or 20)

@app.get("/api/recommendations")
def get_recommendations(user: Dict[str, Any] = Depends(get_current_user)):
    all_prob_summaries = [
        {
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty,
            "topic": p.topic,
            "description": p.description[:120] + "..."
        }
        for p in PROBLEMS.values()
    ]
    return auth.get_user_recommendations(user["id"], all_prob_summaries)


@app.post("/api/settings")
def update_settings(req: UpdateSettingsRequest):
    api_key = req.bharatcode_api_key or req.gemini_api_key
    model = req.bharatcode_model or req.gemini_model
    mentor_ai.set_config(
        api_key=api_key,
        persona=req.mentor_persona,
        model=model,
        base_url=req.bharatcode_base_url
    )
    return {
        "message": "Settings updated successfully",
        "has_gemini_key": bool(mentor_ai.api_key),
        "has_bharatcode_key": bool(mentor_ai.api_key),
        "has_llm_key": bool(mentor_ai.api_key),
        "persona": mentor_ai.persona,
        "model": mentor_ai.model
    }

# ----------------- Student Performance Dashboard & PDF Reporting -----------------

@app.get("/api/performance/dashboard")
def get_performance_dashboard(
    date_filter: Optional[str] = "last_30_days",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Returns genuine, persisted performance statistics, question attempt history,
    tab switch events, and chart datasets for the authenticated student.
    Never uses mock or hardcoded statistics.
    """
    try:
        data = performance_service.get_student_performance_data(
            user_id=user["id"],
            date_filter=date_filter or "last_30_days",
            start_date_str=start_date,
            end_date_str=end_date
        )
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load performance analytics: {str(e)}")

@app.get("/api/reports/pdf")
def download_pdf_report_get(
    date_filter: Optional[str] = "last_30_days",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_tab_switches: Optional[bool] = True,
    include_viva: Optional[bool] = True,
    view_mode: Optional[str] = "detailed",
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generates and streams an authentic, professional multi-page PDF performance report
    strictly adhering to CodeAcharya design principles, IST Asia/Kolkata timezone,
    and actual persisted student attempts and test evaluations.
    """
    try:
        data = performance_service.get_student_performance_data(
            user_id=user["id"],
            date_filter=date_filter or "last_30_days",
            start_date_str=start_date,
            end_date_str=end_date
        )
        pdf_bytes = pdf_generator.generate_student_performance_pdf(
            data=data,
            include_tab_switches=include_tab_switches if include_tab_switches is not None else True,
            include_viva=include_viva if include_viva is not None else True,
            view_mode=view_mode or "detailed"
        )
        now_tag = datetime.now().strftime("%Y%m%d_%H%M")
        clean_name = "".join(c for c in user.get("full_name", "Student") if c.isalnum() or c in ("_", "-"))
        filename = f"CodeAcharya_Performance_Report_{clean_name}_{now_tag}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

@app.post("/api/reports/pdf")
def download_pdf_report_post(
    req: PDFReportRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    POST variant for generating and streaming downloadable PDF report
    with custom JSON configuration payload.
    """
    try:
        data = performance_service.get_student_performance_data(
            user_id=user["id"],
            date_filter=req.date_filter or "last_30_days",
            start_date_str=req.start_date,
            end_date_str=req.end_date
        )
        pdf_bytes = pdf_generator.generate_student_performance_pdf(
            data=data,
            include_tab_switches=req.include_tab_switches if req.include_tab_switches is not None else True,
            include_viva=req.include_viva if req.include_viva is not None else True,
            view_mode=req.view_mode or "detailed"
        )
        now_tag = datetime.now().strftime("%Y%m%d_%H%M")
        clean_name = "".join(c for c in user.get("full_name", "Student") if c.isalnum() or c in ("_", "-"))
        filename = f"CodeAcharya_Performance_Report_{clean_name}_{now_tag}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
