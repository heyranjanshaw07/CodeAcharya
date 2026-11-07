from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class TestCase(BaseModel):
    id: int
    input: Any
    expected_output: Any
    is_hidden: bool = False
    explanation: Optional[str] = None

class Problem(BaseModel):
    id: str
    title: str
    difficulty: str  # Easy, Medium, Hard
    topic: str       # Recursion, Arrays, Dynamic Programming, Stack, etc.
    subtopic: Optional[str] = ""
    description: str
    examples: List[Dict[str, Any]]
    constraints: List[str]
    starter_code: Dict[str, str]  # e.g. {"python": "...", "javascript": "...", "cpp": "...", "java": "..."}
    test_cases: List[TestCase] = []
    learning_objectives: List[str] = []
    common_misconceptions: List[str] = []
    input_format: Optional[str] = ""
    output_format: Optional[str] = ""
    hint: Optional[str] = ""
    progressive_hints: Optional[List[Dict[str, Any]]] = []
    explanation: Optional[str] = ""
    expected_solution: Optional[Dict[str, str]] = {}
    time_complexity: Optional[str] = ""
    space_complexity: Optional[str] = ""
    relevant_concepts: Optional[List[str]] = []
    is_generated: Optional[bool] = False
    source: Optional[str] = "curated"  # "curated", "ai_generated", "blueprint_fallback"

class GenerateQuestionRequest(BaseModel):
    topic: str
    subtopic: Optional[str] = None
    difficulty: str
    language: str = "python"
    count: Optional[int] = 1
    previous_titles: Optional[List[str]] = []
    previous_ids: Optional[List[str]] = []

class GenerateQuestionResponse(BaseModel):
    id: str
    title: str
    topic: str
    subtopic: Optional[str] = ""
    difficulty: str
    language: str
    description: str
    inputFormat: Optional[str] = ""
    outputFormat: Optional[str] = ""
    constraints: List[str] = []
    examples: List[Dict[str, Any]] = []
    hint: Optional[str] = ""
    progressive_hints: Optional[List[Dict[str, Any]]] = []
    explanation: Optional[str] = ""
    expected_solution: Optional[Dict[str, str]] = {}
    time_complexity: Optional[str] = ""
    space_complexity: Optional[str] = ""
    relevant_concepts: Optional[List[str]] = []
    starterCode: str
    starter_code: Optional[Dict[str, str]] = {}
    test_cases: Optional[List[Dict[str, Any]]] = []
    learning_objectives: Optional[List[str]] = []
    common_misconceptions: Optional[List[str]] = []
    is_generated: Optional[bool] = True
    source: Optional[str] = "ai_generated"
    badge: Optional[str] = "AI Generated"

class GenerateQuestionBatchResponse(BaseModel):
    questions: List[GenerateQuestionResponse]
    count: int
    topic: str
    difficulty: str

class ExecuteRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"
    custom_input: Optional[str] = None
    time_spent_seconds: Optional[int] = 0
    session_status: Optional[str] = "running"
    tab_switch_count: Optional[int] = 0
    total_time_away_seconds: Optional[int] = 0
    last_switch_timestamp: Optional[str] = None
    tab_switch_history: Optional[List[Dict[str, Any]]] = None
    idempotency_key: Optional[str] = None
    custom_weights: Optional[Dict[str, float]] = None
    unique_hints_used: Optional[int] = 0
    attempt_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    paused_seconds: Optional[int] = 0
    is_locked: Optional[bool] = False

class SessionRecordRequest(BaseModel):
    problem_id: str
    language: str = "python"
    time_spent_seconds: int = 0
    status: Optional[str] = None  # completed, abandoned, paused, running, failed
    session_status: Optional[str] = None
    passed_count: Optional[int] = None
    passed_test_cases: Optional[int] = None
    total_count: Optional[int] = None
    total_test_cases: Optional[int] = None
    tab_switch_count: Optional[int] = 0
    total_time_away_seconds: Optional[int] = 0
    last_switch_timestamp: Optional[str] = None
    tab_switch_history: Optional[List[Dict[str, Any]]] = None
    attempt_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    paused_seconds: Optional[int] = 0
    code: Optional[str] = ""
    overall_score: Optional[float] = None
    is_locked: Optional[bool] = None
    lock_reason: Optional[str] = None

class TestResult(BaseModel):
    test_id: int
    passed: bool
    input: str = ""
    expected: str = ""
    actual: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class ExecuteResponse(BaseModel):
    status: str  # success, error, timeout
    passed_count: int
    total_count: int
    results: List[TestResult]
    runtime_ms: float
    stdout: str = ""
    stderr: str = ""
    error_type: Optional[str] = None
    ast_feedback: Optional[Dict[str, Any]] = None
    time_spent_seconds: Optional[int] = None
    session_status: Optional[str] = None
    is_completed: Optional[bool] = False
    tab_switch_count: Optional[int] = 0
    total_time_away_seconds: Optional[int] = 0
    last_switch_timestamp: Optional[str] = None
    tab_switch_history: Optional[List[Dict[str, Any]]] = None
    attempt_id: Optional[str] = None
    overall_score: Optional[float] = None
    unique_hints_used: Optional[int] = 0
    independent_score: Optional[float] = None
    score_data: Optional[Dict[str, Any]] = None

class CodingScoreRecord(BaseModel):
    id: str
    attempt_id: str
    question_id: str
    question_title: Optional[str] = ""
    question_topic: Optional[str] = ""
    language: str
    overall_score: float
    correctness_score: float
    correctness_max: float
    complexity_score: Optional[float] = None
    complexity_max: Optional[float] = None
    quality_score: Optional[float] = None
    quality_max: Optional[float] = None
    approach_score: Optional[float] = None
    approach_max: Optional[float] = None
    independent_score: Optional[float] = None
    independent_max: Optional[float] = 10.0
    unique_hints_used: Optional[int] = 0
    code_snapshot: Optional[str] = ""
    memory_usage_mb: Optional[float] = None
    is_renormalized: bool = False
    evaluator_type: str
    breakdown: Dict[str, Any]
    feedback: Dict[str, Any]
    execution_time_ms: float
    coding_time_seconds: int
    tab_away_seconds: int
    passed_count: int
    total_count: int
    status: str
    created_at: str
    created_at_ist: Optional[str] = None

class CodingScoreAnalyticsResponse(BaseModel):
    average_score: float
    best_score: float
    total_evaluated_attempts: int
    total_solved: int
    accuracy_percentage: float
    topic_accuracy: Dict[str, Any]
    score_improvement_trend: List[Dict[str, Any]]
    dimension_averages: Dict[str, float]
    recent_evaluations: List[Dict[str, Any]]
    hint_usage_trend: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = {}
    average_hints_per_problem: Optional[float] = 0.0

class HintRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"
    hint_level: int = 1  # 1: conceptual, 2: algorithmic, 3: concrete, 4: final explanation
    error_context: Optional[str] = None

class HintResponse(BaseModel):
    hint_level: int
    hint_title: str
    hint_content: str
    thought_questions: List[str] = []
    penalty_points: int = 0
    next_hint_available: bool = True

class ExplainRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"
    selected_code: Optional[str] = None
    problem_title: Optional[str] = None
    problem_statement: Optional[str] = None

class DebugGuideRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"
    error_message: Optional[str] = None
    failing_input: Optional[str] = None
    expected_output: Optional[str] = None
    actual_output: Optional[str] = None
    has_run: Optional[bool] = False
    problem_title: Optional[str] = None
    problem_statement: Optional[str] = None

class VivaStartRequest(BaseModel):
    problem_id: str
    code: str
    language: str = "python"

class VivaQuestion(BaseModel):
    id: int
    category: str # conceptual, code_choice, complexity, edge_case, optimization
    question: str
    hint_guidance: Optional[str] = None

class VivaEvaluateRequest(BaseModel):
    problem_id: str
    code: str
    question_id: int
    question: str
    category: str
    student_answer: str
    answer_modality: Optional[str] = "typed" # typed, voice_transcribed, audio_recorded
    hint_guidance: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    expected_concepts: Optional[List[str]] = None
    rubric: Optional[Dict[str, Any]] = None
    simulate_failure: Optional[bool] = False

class VivaScoreResult(BaseModel):
    conceptual_score: Optional[int] = None
    code_understanding_score: Optional[int] = None
    complexity_score: Optional[int] = None
    communication_score: Optional[int] = None
    overall_score: int
    feedback: str
    ideal_points_covered: List[str] = []
    missing_concepts: List[str] = []
    suggested_improvement: Optional[str] = None
    answer_relevance: str = "relevant" # relevant, partially_relevant, irrelevant, uncertain
    applicable_dimensions: List[str] = []
    should_retry: bool = False
    question_id: Optional[int] = None
    category: Optional[str] = None
    status: Optional[str] = "Evaluated"
    scores: Optional[Dict[str, Optional[int]]] = None
    correctPoints: Optional[List[str]] = None
    examinerRemarks: Optional[str] = None
    followUpHint: Optional[str] = None
    answer_modality: Optional[str] = "typed"
    communication_label: Optional[str] = None

class UpdateSettingsRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    mentor_persona: Optional[str] = "socratic" # socratic, strict, friendly
    gemini_model: Optional[str] = None
    bharatcode_api_key: Optional[str] = None
    bharatcode_base_url: Optional[str] = None
    bharatcode_model: Optional[str] = None

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: Optional[bool] = False

class GoogleAuthRequest(BaseModel):
    id_token: str
    remember_me: Optional[bool] = False

class ForgotPasswordRequest(BaseModel):
    email: str

class ForgotPasswordResponse(BaseModel):
    status: str = "success"
    message: str

class TabSwitchRecordRequest(BaseModel):
    id: Optional[str] = None
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    event_timestamp: Optional[str] = None
    return_timestamp: Optional[str] = None
    time_away_seconds: Optional[int] = 0
    event_status: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    auth_provider: Optional[str] = "local"

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    message: str

class PasteAttemptRecordRequest(BaseModel):
    page_type: str  # 'coding' or 'viva'
    question_id: Optional[str] = None
    attempt_id: Optional[str] = None
    event_timestamp: Optional[str] = None

class PasteAttemptResponse(BaseModel):
    status: str = "success"
    recorded: bool = True
    duplicate: bool = False
    message: str = "Paste attempt recorded."
    record: Optional[Dict[str, Any]] = None

class PasteAttemptEvent(BaseModel):
    id: str
    user_id: str
    page_type: str
    question_id: Optional[str] = None
    attempt_id: Optional[str] = None
    event_timestamp: str
    event_timestamp_ist: str
    created_at: str

class PDFReportRequest(BaseModel):
    date_filter: Optional[str] = "last_30_days"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    include_tab_switches: Optional[bool] = True
    include_viva: Optional[bool] = True
    view_mode: Optional[str] = "detailed"

class SessionLockEventRequest(BaseModel):
    event_type: str  # fullscreen_entered, fullscreen_exited, page_hidden, page_visible, editor_locked, editor_unlocked, resume_requested, resume_success, resume_failed
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    event_timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionLockEventResponse(BaseModel):
    status: str = "success"
    event_id: str
    event_type: str
    recorded: bool = True
    duplicate: bool = False
    message: str = "Session lock event recorded."
    event_timestamp_ist: Optional[str] = None

class SessionLockRequest(BaseModel):
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    reason: Optional[str] = "fullscreen_exit"
    event_timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionLockResponse(BaseModel):
    status: str = "locked"
    is_locked: bool = True
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    reason: Optional[str] = "fullscreen_exit"
    message: str = "Assessment session is locked. Full-screen mode is required to continue coding."
    event_timestamp_ist: Optional[str] = None

class SessionResumeRequest(BaseModel):
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    fullscreen_verified: bool = False
    event_timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SessionResumeResponse(BaseModel):
    status: str = "unlocked"
    is_locked: bool = False
    attempt_id: Optional[str] = None
    question_id: Optional[str] = None
    message: str = "Full-screen mode verified. Editor unlocked and session resumed."
    event_timestamp_ist: Optional[str] = None



