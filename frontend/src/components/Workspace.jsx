import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { 
  Play, 
  Lightbulb, 
  Bug, 
  HelpCircle, 
  GraduationCap, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Cpu, 
  RotateCcw, 
  Sparkles, 
  ChevronRight, 
  ChevronDown,
  ChevronUp,
  Code, 
  FileCode2,
  Terminal,
  Activity,
  Layers,
  AlertOctagon,
  Search,
  Filter,
  Check,
  FolderTree,
  BookOpen,
  Shuffle,
  ArrowRight,
  ArrowLeft,
  Compass,
  Target,
  RefreshCw,
  X,
  Pause,
  Lock,
  Unlock,
  Award,
  AlertTriangle,
  Timer,
  Flag,
  Square,
  EyeOff,
  History,
  Trash2,
  ShieldCheck
} from 'lucide-react';
import confetti from 'canvas-confetti';
import ProgressiveHintModal from './ProgressiveHintModal';
import ScoreBreakdownModal from './ScoreBreakdownModal';
import FullscreenLockOverlay from './FullscreenLockOverlay';
import LanguageChangeModal from './LanguageChangeModal';
import { useAutoScroll } from '../utils/scrollUtils';
import { configureMonacoPasteRestriction } from '../utils/pasteRestriction';
import {
  registerCodeAcharyaIntelliSense,
  disposeCodeAcharyaIntelliSense
} from '../utils/monacoIntelliSense';
import {
  isBrowserFullscreen,
  isFullscreenSupported,
  requestBrowserFullscreen,
  exitBrowserFullscreen,
  logSessionLockTelemetry,
  notifySessionLockedOnServer,
  notifySessionResumeOnServer
} from '../utils/fullscreenEnforcement';

export const calculateIndependentScore = (uniqueHintsUsed) => {
  if (!uniqueHintsUsed || uniqueHintsUsed <= 0) return 10;
  if (uniqueHintsUsed === 1) return 9;
  if (uniqueHintsUsed === 2) return 7;
  if (uniqueHintsUsed === 3) return 4;
  return 1;
};

export default function Workspace({ 
  problems, 
  selectedProblemId, 
  onSelectProblem, 
  onLaunchViva, 
  onResetSelection,
  onProblemCreated,
  language, 
  setLanguage,
  code,
  setCode,
  studentProfile,
  onBack,
  onRefreshProfile,
  isAssessmentMode: propAssessmentMode,
  setIsAssessmentMode: propSetIsAssessmentMode,
  onRegisterLanguageHandler
}) {
  const [localAssessmentMode, setLocalAssessmentMode] = useState(() => {
    if (typeof localStorage !== 'undefined') {
      const saved = localStorage.getItem('codeacharya_assessment_mode');
      return saved !== 'false';
    }
    return true;
  });

  const isAssessmentMode = propAssessmentMode !== undefined ? propAssessmentMode : localAssessmentMode;
  const setIsAssessmentMode = (val) => {
    if (typeof propSetIsAssessmentMode === 'function') {
      propSetIsAssessmentMode(val);
    } else {
      setLocalAssessmentMode(val);
    }
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('codeacharya_assessment_mode', val ? 'true' : 'false');
    }
  };

  // Monaco Editor references & paste restriction state
  const monacoEditorRef = useRef(null);
  const monacoInstanceRef = useRef(null);
  const monacoCleanupRef = useRef(null);
  const monacoIntelliSenseCleanupRef = useRef(null);

  // Clean up Monaco IntelliSense providers on component unmount
  useEffect(() => {
    return () => {
      if (monacoIntelliSenseCleanupRef.current) {
        monacoIntelliSenseCleanupRef.current();
      }
      disposeCodeAcharyaIntelliSense();
    };
  }, []);
  const [showPasteWarning, setShowPasteWarning] = useState(false);
  const [pasteWarningMessage, setPasteWarningMessage] = useState('');
  const pasteWarningTimerRef = useRef(null);

  const triggerPasteWarning = useCallback((msg) => {
    setPasteWarningMessage(msg || 'Pasting is disabled in Assessment Mode. Please write code directly into the editor.');
    setShowPasteWarning(true);
    if (pasteWarningTimerRef.current) clearTimeout(pasteWarningTimerRef.current);
    pasteWarningTimerRef.current = setTimeout(() => {
      setShowPasteWarning(false);
    }, 3000);
  }, []);

  // Global Full-Screen Coding Lock & Telemetry state
  const [isLocked, setIsLocked] = useState(false);
  const [lockReason, setLockReason] = useState('fullscreen_exit');
  const [lockErrorMessage, setLockErrorMessage] = useState('');
  const [isResuming, setIsResuming] = useState(false);
  const isLockedRef = useRef(false);

  useEffect(() => {
    isLockedRef.current = isLocked;
    window.__codeAcharyaIsLocked = isLocked;
  }, [isLocked]);

  // Language Change Confirmation Modal state
  const [pendingLanguage, setPendingLanguage] = useState(null);
  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);
  const [isConfirmingLanguage, setIsConfirmingLanguage] = useState(false);
  const pendingLanguageRef = useRef(null);

  useEffect(() => {
    pendingLanguageRef.current = pendingLanguage;
    window.__codeAcharyaIsLanguageModalOpen = isLanguageModalOpen;
    window.__codeAcharyaPendingLanguage = pendingLanguage;
  }, [isLanguageModalOpen, pendingLanguage]);

  const [currentProblem, setCurrentProblem] = useState(null);
  const [activeBottomTab, setActiveBottomTab] = useState('tests'); // tests, ast, explanation, debugger

  // Re-configure Monaco paste restriction when assessment mode or problem changes
  useEffect(() => {
    if (monacoEditorRef.current && monacoInstanceRef.current) {
      if (monacoCleanupRef.current) monacoCleanupRef.current();
      monacoCleanupRef.current = configureMonacoPasteRestriction(
        monacoEditorRef.current,
        monacoInstanceRef.current,
        {
          isRestricted: isAssessmentMode,
          pageType: 'coding',
          questionId: currentProblem?.id,
          attemptId: null,
          onBlocked: () => triggerPasteWarning()
        }
      );
    }
  }, [isAssessmentMode, currentProblem, triggerPasteWarning]);
  
  // Execution state
  const [isExecuting, setIsExecuting] = useState(false);
  const [execResult, setExecResult] = useState(null);
  const [showScoreModal, setShowScoreModal] = useState(false);

  // Progressive Hint State
  const [isHintOpen, setIsHintOpen] = useState(false);
  const [hintLevel, setHintLevel] = useState(1);
  const [hintsHistory, setHintsHistory] = useState([]);
  const [isLoadingHint, setIsLoadingHint] = useState(false);

  // Explanation state
  const [explanationData, setExplanationData] = useState(null);
  const [isExplaining, setIsExplaining] = useState(false);
  const [explainError, setExplainError] = useState(null);

  // Debugger state
  const [debugGuide, setDebugGuide] = useState(null);
  const [isDebugging, setIsDebugging] = useState(false);
  const [debugError, setDebugError] = useState(null);

  // Request ID refs to prevent race conditions on rapid clicks or language switching
  const debugReqIdRef = useRef(0);
  const explainReqIdRef = useRef(0);

  // Auto-scroll ref for bottom results panel (Run & Test, Debug Guide, Explain Code)
  const [bottomPanelRef, scrollToBottomPanel] = useAutoScroll({ offset: 85 });

  // Guided Topic & Difficulty Selector State
  const [launcherTopic, setLauncherTopic] = useState('Recursion & Backtracking');
  const [launcherDifficulty, setLauncherDifficulty] = useState('Easy');
  const [launcherSubtopic, setLauncherSubtopic] = useState('All');
  const [generationCount, setGenerationCount] = useState(1);
  const [seenProblemIds, setSeenProblemIds] = useState([]);
  const [seenProblemTitles, setSeenProblemTitles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateSuccess, setGenerateSuccess] = useState(false);
  const [generateError, setGenerateError] = useState(null);

  // Topic & Difficulty Explorer State
  const [selectedTopic, setSelectedTopic] = useState('All');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All'); // 'All', 'Easy', 'Medium', 'Hard'
  const [selectedSource, setSelectedSource] = useState('All'); // 'All', 'curated', 'generated'
  const [searchQuery, setSearchQuery] = useState('');
  const [isExplorerExpanded, setIsExplorerExpanded] = useState(false);
  const [isCurriculumModalOpen, setIsCurriculumModalOpen] = useState(false);

  // Timed Coding Practice Mode State
  // Valid transitions:
  // 'not_started' -> 'running' (Start Coding)
  // 'running' -> 'paused' (Pause Coding)
  // 'running' -> 'completed' (All testcases pass)
  // 'running' -> 'abandoned' (Abandon Session)
  // 'paused' -> 'running' (Resume Coding)
  // 'paused' -> 'abandoned' (Abandon Session)
  // 'completed' -> 'not_started' (New Attempt)
  // 'abandoned' -> 'not_started' (Try Again)
  const [sessionState, setSessionState] = useState('not_started'); // not_started, running, paused, completed, abandoned
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [completedSummary, setCompletedSummary] = useState(null);
  const [isAbandonModalOpen, setIsAbandonModalOpen] = useState(false);
  const [pendingNavigationAction, setPendingNavigationAction] = useState(null);

  // Tab Switching Tracking State
  const [tabSwitches, setTabSwitches] = useState(0);
  const [totalTimeAwayMs, setTotalTimeAwayMs] = useState(0);
  const [lastSwitchTime, setLastSwitchTime] = useState(null);
  const [tabSwitchHistory, setTabSwitchHistory] = useState([]);
  const [isTabHistoryModalOpen, setIsTabHistoryModalOpen] = useState(false);

  const startTimeRef = useRef(null);
  const accumulatedMsRef = useRef(0);
  const timerIntervalRef = useRef(null);

  // Tab Switching Tracking Refs (ensures robust event handling without stale closures)
  const tabSwitchesRef = useRef(0);
  const totalTimeAwayMsRef = useRef(0);
  const lastSwitchTimeRef = useRef(null);
  const tabSwitchHistoryRef = useRef([]);
  const hiddenStartTimeRef = useRef(null);
  const isTabHiddenRef = useRef(false);
  const sessionStateRef = useRef('not_started');
  const currentProblemRef = useRef(null);
  const attemptIdRef = useRef(null);
  const currentAwayEventIdRef = useRef(null);
  const codeRef = useRef('');
  const languageRef = useRef('python');

  // Expose tab switch statistics for verification & automated diagnostics
  useEffect(() => {
    window.__codeAcharyaTabSwitches = tabSwitches;
    window.__codeAcharyaTabSwitchHistory = tabSwitchHistory;
  }, [tabSwitches, tabSwitchHistory]);

  // Synchronize ref values with current React state
  useEffect(() => {
    sessionStateRef.current = sessionState;
  }, [sessionState]);

  useEffect(() => {
    currentProblemRef.current = currentProblem;
  }, [currentProblem]);

  useEffect(() => {
    codeRef.current = code;
  }, [code]);

  useEffect(() => {
    languageRef.current = language;
  }, [language]);

  // Indian Standard Time (IST) formatting helpers (Asia/Kolkata timezone)
  const formatISTTimestamp = (dateOrMs) => {
    if (!dateOrMs) return '--';
    const d = new Date(dateOrMs);
    return d.toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    }) + ' IST';
  };

  const formatISTDate = (dateOrMs) => {
    if (!dateOrMs) return '--';
    const d = new Date(dateOrMs);
    return d.toLocaleDateString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: '2-digit'
    });
  };

  // Time formatter: MM:SS or HH:MM:SS
  const formatTime = (totalSeconds) => {
    const s = Math.max(0, totalSeconds || 0);
    const hrs = Math.floor(s / 3600);
    const mins = Math.floor((s % 3600) / 60);
    const secs = s % 60;
    if (hrs > 0) {
      return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  // Duration formatter: HH:MM:SS for Total Time Away display
  const formatDuration = (totalSeconds) => {
    const s = Math.max(0, totalSeconds || 0);
    const hrs = Math.floor(s / 3600);
    const mins = Math.floor((s % 3600) / 60);
    const secs = s % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  const startTimerInterval = () => {
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    timerIntervalRef.current = setInterval(() => {
      if (startTimeRef.current) {
        const ms = accumulatedMsRef.current + (Date.now() - startTimeRef.current);
        setElapsedSeconds(Math.floor(ms / 1000));
      }
    }, 1000);
  };

  const stopTimerInterval = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  };

  // Ref to track if session was actively running before editor was locked
  const wasRunningBeforeLockRef = useRef(false);

  // Global Full-Screen Lock Handler
  const handleLockEditor = useCallback((reason = 'fullscreen_exit') => {
    // Only lock active sessions (running or paused); do not lock if completed, abandoned, or not started
    if (sessionStateRef.current === 'completed' || sessionStateRef.current === 'abandoned' || sessionStateRef.current === 'not_started') {
      return;
    }

    if (isLockedRef.current && lockReason === reason) {
      return;
    }

    if (sessionStateRef.current === 'running') {
      wasRunningBeforeLockRef.current = true;
      if (startTimeRef.current) {
        accumulatedMsRef.current += (Date.now() - startTimeRef.current);
        startTimeRef.current = null;
        stopTimerInterval();
      }
    }

    setIsLocked(true);
    setLockReason(reason);
    isLockedRef.current = true;

    // Enforce official Monaco read-only APIs
    if (monacoEditorRef.current) {
      try {
        monacoEditorRef.current.updateOptions({
          readOnly: true,
          domReadOnly: true
        });
      } catch (e) {}
    }

    // Telemetry and server-side lock registration
    logSessionLockTelemetry({
      eventType: 'editor_locked',
      attemptId: attemptIdRef.current,
      questionId: currentProblemRef.current?.id,
      metadata: { lock_reason: reason, session_state: sessionStateRef.current }
    });

    notifySessionLockedOnServer({
      attemptId: attemptIdRef.current,
      questionId: currentProblemRef.current?.id,
      reason: reason,
      metadata: { session_state: sessionStateRef.current }
    });
  }, [lockReason]);

  // Full-Screen Recovery & Resume Handler
  const handleRestoreFullscreenAndResume = async () => {
    setIsResuming(true);
    setLockErrorMessage('');

    logSessionLockTelemetry({
      eventType: 'resume_requested',
      attemptId: attemptIdRef.current,
      questionId: currentProblemRef.current?.id,
      metadata: { previous_reason: lockReason }
    });

    try {
      const reqRes = await requestBrowserFullscreen();
      const verified = isBrowserFullscreen();

      if (!verified) {
        const errMsg = reqRes.error || 'Full-screen mode was not entered. Please click again and allow full-screen mode to resume coding.';
        setLockErrorMessage(errMsg);
        setIsResuming(false);
        logSessionLockTelemetry({
          eventType: 'resume_unsuccessful',
          attemptId: attemptIdRef.current,
          questionId: currentProblemRef.current?.id,
          metadata: { error: errMsg }
        });
        return;
      }

      // Notify server of successful resume with verified full-screen
      await notifySessionResumeOnServer({
        attemptId: attemptIdRef.current,
        questionId: currentProblemRef.current?.id,
        fullscreenVerified: true,
        metadata: { was_running: wasRunningBeforeLockRef.current }
      });

      logSessionLockTelemetry({
        eventType: 'editor_unlocked',
        attemptId: attemptIdRef.current,
        questionId: currentProblemRef.current?.id,
        metadata: { resume_successful: true }
      });

      setIsLocked(false);
      isLockedRef.current = false;
      setIsResuming(false);
      setLockErrorMessage('');

      // Restore timer if it was running before lock
      if (wasRunningBeforeLockRef.current && sessionStateRef.current === 'running') {
        startTimeRef.current = Date.now();
        startTimerInterval();
      }

      // Restore Monaco editor read-only status based on current session state
      if (monacoEditorRef.current) {
        try {
          const shouldBeReadOnly = sessionStateRef.current !== 'running';
          monacoEditorRef.current.updateOptions({
            readOnly: shouldBeReadOnly,
            domReadOnly: shouldBeReadOnly
          });
          monacoEditorRef.current.focus();
        } catch (e) {}
      }
    } catch (err) {
      console.error('Error during full-screen restore:', err);
      setLockErrorMessage('An unexpected error occurred while requesting full-screen: ' + (err.message || 'unknown error'));
      setIsResuming(false);
    }
  };

  // Re-sync timer, track Tab Visibility Changes and enforce Global Full-Screen restriction
  useEffect(() => {
    const handleVisibilityOrBlur = (isLeaving) => {
      if (isLeaving) {
        // Enforce lock on page hidden / tab switch during active coding session
        if (sessionStateRef.current === 'running' || sessionStateRef.current === 'paused') {
          handleLockEditor('page_hidden');
          logSessionLockTelemetry({
            eventType: 'page_hidden',
            attemptId: attemptIdRef.current,
            questionId: currentProblemRef.current?.id,
            metadata: { session_state: sessionStateRef.current }
          });
        }

        // Page/window transitioning to hidden or inactive
        if (!isTabHiddenRef.current) {
          isTabHiddenRef.current = true;
          // Track only during an active 'running' coding session
          if (sessionStateRef.current === 'running') {
            const now = Date.now();
            hiddenStartTimeRef.current = now;
            const eventId = 'ts_' + now.toString(36) + '_' + Math.random().toString(36).substring(2, 8);
            currentAwayEventIdRef.current = eventId;
            const newCount = tabSwitchesRef.current + 1;
            tabSwitchesRef.current = newCount;
            const nowIso = new Date(now).toISOString();
            const nowTimeStr = formatISTTimestamp(now);
            const nowDateStr = formatISTDate(now);
            lastSwitchTimeRef.current = nowTimeStr;
            setTabSwitches(newCount);
            setLastSwitchTime(nowTimeStr);

            const newEvent = {
              id: eventId,
              switch_number: newCount,
              date: nowDateStr,
              event_timestamp: nowIso,
              switch_timestamp_ist: nowTimeStr,
              switch_timestamp_ms: now,
              return_timestamp: null,
              return_timestamp_ist: 'Away...',
              return_timestamp_ms: null,
              duration_away_seconds: 0,
              duration_away_formatted: '--',
              status: 'away'
            };
            const updatedHistory = [...tabSwitchHistoryRef.current, newEvent];
            tabSwitchHistoryRef.current = updatedHistory;
            setTabSwitchHistory(updatedHistory);

            // Notify server immediately to record the away visibility event with actual timestamp
            const token = typeof localStorage !== 'undefined' ? localStorage.getItem('codeacharya_auth_token') : null;
            try {
              fetch('/api/tab-switch/record', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                },
                credentials: 'include',
                keepalive: true,
                body: JSON.stringify({
                  id: eventId,
                  attempt_id: attemptIdRef.current || null,
                  question_id: currentProblemRef.current?.id || null,
                  event_timestamp: nowIso,
                  event_status: 'away',
                  time_away_seconds: 0
                })
              }).then(r => r.json()).then(d => {
                if (d?.id) currentAwayEventIdRef.current = d.id;
              }).catch(e => console.warn('Tab away tracking error:', e));
            } catch (e) {}

            if (currentProblemRef.current) {
              try {
                localStorage.setItem(`codeacharya_tab_switch_history_${currentProblemRef.current.id}`, JSON.stringify(updatedHistory));
              } catch (e) {
                console.warn('Failed to save tab switch history:', e);
              }

              saveSessionToStorage(
                currentProblemRef.current.id,
                sessionStateRef.current,
                accumulatedMsRef.current,
                startTimeRef.current,
                codeRef.current,
                languageRef.current,
                completedSummary,
                newCount,
                totalTimeAwayMsRef.current,
                nowTimeStr,
                updatedHistory
              );
            }
          }
        }
      } else {
        // Page/window transitioning back to visible
        if (sessionStateRef.current === 'running' || sessionStateRef.current === 'paused') {
          logSessionLockTelemetry({
            eventType: 'page_visible',
            attemptId: attemptIdRef.current,
            questionId: currentProblemRef.current?.id,
            metadata: { session_state: sessionStateRef.current }
          });

          // CRITICAL: Returning to CodeAcharya MUST NOT automatically unlock the editor!
          // If the document is not in fullscreen mode, ensure editor remains locked.
          if (!isBrowserFullscreen()) {
            handleLockEditor('fullscreen_exit');
          }
        }

        if (isTabHiddenRef.current) {
          isTabHiddenRef.current = false;
          let newTotalAwayMs = totalTimeAwayMsRef.current;
          let updatedHistory = [...tabSwitchHistoryRef.current];

          if (hiddenStartTimeRef.current) {
            const hiddenStart = hiddenStartTimeRef.current;
            hiddenStartTimeRef.current = null;
            const now = Date.now();
            const awayDuration = Math.max(0, now - hiddenStart);
            const durationSec = Math.max(0, Math.round(awayDuration / 1000));
            const returnIso = new Date(now).toISOString();
            const returnIst = formatISTTimestamp(now);

            // Strictly track away duration only when session was actively running (excludes paused or completed)
            if (sessionStateRef.current === 'running') {
              newTotalAwayMs += awayDuration;
              totalTimeAwayMsRef.current = newTotalAwayMs;
              setTotalTimeAwayMs(newTotalAwayMs);

              // Notify server immediately to close the event and calculate duration from real timestamps
              const token = typeof localStorage !== 'undefined' ? localStorage.getItem('codeacharya_auth_token') : null;
              try {
                fetch('/api/tab-switch/record', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                  },
                  credentials: 'include',
                  keepalive: true,
                  body: JSON.stringify({
                    id: currentAwayEventIdRef.current || null,
                    attempt_id: attemptIdRef.current || null,
                    question_id: currentProblemRef.current?.id || null,
                    event_timestamp: new Date(hiddenStart).toISOString(),
                    return_timestamp: returnIso,
                    event_status: 'returned',
                    time_away_seconds: durationSec
                  })
                }).catch(e => console.warn('Tab return tracking error:', e));
              } catch (e) {}

              // Update latest unclosed history entry
              if (updatedHistory.length > 0) {
                const lastIdx = updatedHistory.length - 1;
                const lastEvt = updatedHistory[lastIdx];
                if (!lastEvt.return_timestamp_ms || lastEvt.return_timestamp_ist === 'Away...' || lastEvt.status === 'away') {
                  updatedHistory[lastIdx] = {
                    ...lastEvt,
                    return_timestamp: returnIso,
                    return_timestamp_ist: returnIst,
                    return_timestamp_ms: now,
                    duration_away_seconds: durationSec,
                    duration_away_formatted: formatDuration(durationSec),
                    status: 'returned'
                  };
                  tabSwitchHistoryRef.current = updatedHistory;
                  setTabSwitchHistory(updatedHistory);
                }
              }
            }
          }

          // Re-sync timer accuracy immediately when browser tab regains focus or visibility
          if (sessionStateRef.current === 'running' && startTimeRef.current) {
            const ms = accumulatedMsRef.current + (Date.now() - startTimeRef.current);
            setElapsedSeconds(Math.floor(ms / 1000));
          }

          if (currentProblemRef.current) {
            try {
              localStorage.setItem(`codeacharya_tab_switch_history_${currentProblemRef.current.id}`, JSON.stringify(updatedHistory));
            } catch (e) {
              console.warn('Failed to save tab switch history:', e);
            }

            saveSessionToStorage(
              currentProblemRef.current.id,
              sessionStateRef.current,
              accumulatedMsRef.current,
              startTimeRef.current,
              codeRef.current,
              languageRef.current,
              completedSummary,
              tabSwitchesRef.current,
              newTotalAwayMs,
              lastSwitchTimeRef.current,
              updatedHistory
            );
          }
        }
      }
    };

    const onVisibilityChange = () => {
      handleVisibilityOrBlur(document.visibilityState === 'hidden');
    };

    const onWindowBlur = () => {
      // Supplementary signal: check document visibility to avoid false positives on simple clicks
      if (document.visibilityState === 'hidden') {
        handleVisibilityOrBlur(true);
      }
    };

    const onWindowFocus = () => {
      if (document.visibilityState === 'visible') {
        handleVisibilityOrBlur(false);
      }
    };

    const handleFullscreenChange = () => {
      const isFs = isBrowserFullscreen();
      if (!isFs) {
        if (sessionStateRef.current === 'running' || sessionStateRef.current === 'paused') {
          handleLockEditor('fullscreen_exit');
          logSessionLockTelemetry({
            eventType: 'fullscreen_exited',
            attemptId: attemptIdRef.current,
            questionId: currentProblemRef.current?.id,
            metadata: { session_state: sessionStateRef.current }
          });
        }
      } else {
        logSessionLockTelemetry({
          eventType: 'fullscreen_entered',
          attemptId: attemptIdRef.current,
          questionId: currentProblemRef.current?.id,
          metadata: { session_state: sessionStateRef.current }
        });
      }
    };

    const handleWindowResize = () => {
      if (!isBrowserFullscreen() && (sessionStateRef.current === 'running' || sessionStateRef.current === 'paused')) {
        handleLockEditor('fullscreen_exit');
      }
    };

    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('blur', onWindowBlur);
    window.addEventListener('focus', onWindowFocus);
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
    window.addEventListener('resize', handleWindowResize);

    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange);
      window.removeEventListener('blur', onWindowBlur);
      window.removeEventListener('focus', onWindowFocus);
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
      window.removeEventListener('resize', handleWindowResize);
    };
  }, [handleLockEditor]);

  // Clean up timer on unmount
  useEffect(() => {
    return () => stopTimerInterval();
  }, []);

  const saveSessionToStorage = (
    pid, 
    state, 
    accumMs, 
    startTs, 
    customCode, 
    lang, 
    compSummary = null,
    switches = null,
    awayMs = null,
    lastSw = null,
    history = null,
    attId = null
  ) => {
    if (!pid) return;
    try {
      const swCount = switches !== null ? switches : tabSwitchesRef.current;
      const tAwayMs = awayMs !== null ? awayMs : totalTimeAwayMsRef.current;
      const lSwitch = lastSw !== null ? lastSw : lastSwitchTimeRef.current;
      const hist = history !== null ? history : tabSwitchHistoryRef.current;
      const currentAttId = attId !== null ? attId : attemptIdRef.current;
      const payload = {
        problemId: pid,
        attemptId: currentAttId,
        sessionState: state,
        accumulatedMs: accumMs,
        startTime: startTs,
        elapsedSeconds: Math.floor((accumMs + (state === 'running' && startTs ? Date.now() - startTs : 0)) / 1000),
        code: customCode,
        language: lang,
        completedSummary: compSummary,
        tabSwitches: swCount,
        totalTimeAwayMs: tAwayMs,
        lastSwitchTime: lSwitch,
        tabSwitchHistory: hist,
        updatedAt: Date.now()
      };
      localStorage.setItem(`codeacharya_timed_session_${pid}`, JSON.stringify(payload));
      if (hist && hist.length > 0) {
        localStorage.setItem(`codeacharya_tab_switch_history_${pid}`, JSON.stringify(hist));
      }
    } catch (e) {
      console.warn('Failed to save session:', e);
    }
  };

  const getProblemStarterCode = (prob, lang) => {
    if (prob?.starter_code?.[lang]) {
      return prob.starter_code[lang];
    }
    if (lang === 'c') {
      return '#include <stdio.h>\n\nint main(void) {\n    return 0;\n}\n';
    }
    if (lang === 'cpp') {
      return '#include <iostream>\nusing namespace std;\n\nint main() {\n    return 0;\n}\n';
    }
    if (lang === 'java') {
      return 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        \n    }\n}\n';
    }
    return prob?.starter_code?.['python'] || prob?.starterCode || '';
  };

  // Load problem details when selectedProblemId changes.
  // When selectedProblemId is null, currentProblem is null so user chooses Topic & Level first!
  useEffect(() => {
    if (selectedProblemId) {
      loadProblem(selectedProblemId);
    } else {
      setCurrentProblem(null);
    }
  }, [selectedProblemId]);

  // Synchronize state when language changes
  const isLanguageMountedRef = useRef(false);
  useEffect(() => {
    if (!isLanguageMountedRef.current) {
      isLanguageMountedRef.current = true;
      return;
    }
    // Invalidate pending requests and clear stale debug/explain state on language switch
    debugReqIdRef.current += 1;
    explainReqIdRef.current += 1;
    setIsDebugging(false);
    setIsExplaining(false);
    setDebugGuide(null);
    setExplanationData(null);
    setDebugError(null);
    setExplainError(null);
  }, [language]);

  const loadProblem = async (pid) => {
    try {
      const res = await fetch(`/api/problems/${pid}`);
      const data = await res.json();
      setCurrentProblem(data);

      // Check localStorage for existing session on this problem
      const savedRaw = localStorage.getItem(`codeacharya_timed_session_${pid}`);
      if (savedRaw) {
        try {
          const saved = JSON.parse(savedRaw);
          const isNotStarted = !saved.sessionState || saved.sessionState === 'not_started';
          const isKnownOldSolution = saved.code && (
            saved.code.includes('// TODO:') ||
            saved.code.includes('# TODO:') ||
            (data.expected_solution && Object.values(data.expected_solution).some(sol => sol && saved.code.trim() === sol.trim()))
          );
          if (!isNotStarted && saved.code && !isKnownOldSolution) {
            setCode(saved.code);
          } else {
            setCode(getProblemStarterCode(data, language));
          }

          // Restore tab switching tracking statistics & complete history per coding attempt
          let restoredHistory = [];
          try {
            const savedHistRaw = localStorage.getItem(`codeacharya_tab_switch_history_${pid}`);
            if (savedHistRaw) {
              restoredHistory = JSON.parse(savedHistRaw) || [];
            }
          } catch (e) {
            restoredHistory = [];
          }
          if ((!restoredHistory || restoredHistory.length === 0) && saved.tabSwitchHistory) {
            restoredHistory = saved.tabSwitchHistory;
          }

          let restoredSwitches = saved.tabSwitches !== undefined ? saved.tabSwitches : 0;
          if (restoredSwitches === 0 && restoredHistory.length > 0) {
            restoredSwitches = restoredHistory.length;
          }
          const restoredAwayMs = saved.totalTimeAwayMs || 0;
          const restoredLastSwitch = saved.lastSwitchTime || (restoredHistory.length > 0 ? restoredHistory[restoredHistory.length - 1].switch_timestamp_ist : null);

          // Mark unclosed history event if page reloaded during an away state without return
          if (restoredHistory.length > 0) {
            const lastEvt = restoredHistory[restoredHistory.length - 1];
            if (!lastEvt.return_timestamp_ms || lastEvt.return_timestamp_ist === 'Away...' || lastEvt.status === 'away') {
              restoredHistory[restoredHistory.length - 1] = {
                ...lastEvt,
                status: 'incomplete',
                return_timestamp: null,
                return_timestamp_ist: 'Awaiting return',
                duration_away_seconds: null,
                duration_away_formatted: 'Incomplete'
              };
            }
          }

          attemptIdRef.current = saved.attemptId || null;

          if (saved.sessionState === 'running') {
            const now = Date.now();
            if (!attemptIdRef.current) {
              attemptIdRef.current = 'att_' + now.toString(36) + '_' + Math.random().toString(36).substring(2, 8);
            }
            accumulatedMsRef.current = saved.accumulatedMs || 0;
            startTimeRef.current = saved.startTime || now;
            const currentSec = Math.floor((accumulatedMsRef.current + (now - startTimeRef.current)) / 1000);
            setElapsedSeconds(currentSec);
            setSessionState('running');
            tabSwitchesRef.current = restoredSwitches;
            totalTimeAwayMsRef.current = restoredAwayMs;
            lastSwitchTimeRef.current = restoredLastSwitch;
            tabSwitchHistoryRef.current = restoredHistory;
            setTabSwitches(restoredSwitches);
            setTotalTimeAwayMs(restoredAwayMs);
            setLastSwitchTime(restoredLastSwitch);
            setTabSwitchHistory(restoredHistory);
            
            // Global Full-Screen check on reload / session recovery
            if (!isBrowserFullscreen()) {
              setIsLocked(true);
              isLockedRef.current = true;
              setLockReason('fullscreen_exit');
              wasRunningBeforeLockRef.current = true;
              stopTimerInterval();
            } else {
              setIsLocked(false);
              isLockedRef.current = false;
              startTimerInterval();
            }
          } else if (saved.sessionState === 'paused' || saved.sessionState === 'stopped') {
            accumulatedMsRef.current = saved.accumulatedMs || 0;
            startTimeRef.current = null;
            setElapsedSeconds(saved.elapsedSeconds || Math.floor(accumulatedMsRef.current / 1000));
            setSessionState('paused');
            tabSwitchesRef.current = restoredSwitches;
            totalTimeAwayMsRef.current = restoredAwayMs;
            lastSwitchTimeRef.current = restoredLastSwitch;
            setTabSwitchHistory(restoredHistory);
            stopTimerInterval();

            if (!isBrowserFullscreen()) {
              setIsLocked(true);
              isLockedRef.current = true;
              setLockReason('fullscreen_exit');
            } else {
              setIsLocked(false);
              isLockedRef.current = false;
            }
          } else if (saved.sessionState === 'completed') {
            accumulatedMsRef.current = saved.accumulatedMs || 0;
            startTimeRef.current = null;
            setElapsedSeconds(saved.elapsedSeconds || Math.floor(accumulatedMsRef.current / 1000));
            setSessionState('completed');
            tabSwitchesRef.current = restoredSwitches;
            totalTimeAwayMsRef.current = restoredAwayMs;
            lastSwitchTimeRef.current = restoredLastSwitch;
            tabSwitchHistoryRef.current = restoredHistory;
            setTabSwitches(restoredSwitches);
            setTotalTimeAwayMs(restoredAwayMs);
            setLastSwitchTime(restoredLastSwitch);
            setTabSwitchHistory(restoredHistory);
            if (saved.completedSummary) setCompletedSummary(saved.completedSummary);
            stopTimerInterval();
          } else if (saved.sessionState === 'abandoned') {
            accumulatedMsRef.current = saved.accumulatedMs || 0;
            startTimeRef.current = null;
            setElapsedSeconds(saved.elapsedSeconds || Math.floor(accumulatedMsRef.current / 1000));
            setSessionState('abandoned');
            tabSwitchesRef.current = restoredSwitches;
            totalTimeAwayMsRef.current = restoredAwayMs;
            lastSwitchTimeRef.current = restoredLastSwitch;
            tabSwitchHistoryRef.current = restoredHistory;
            setTabSwitches(restoredSwitches);
            setTotalTimeAwayMs(restoredAwayMs);
            setLastSwitchTime(restoredLastSwitch);
            setTabSwitchHistory(restoredHistory);
            stopTimerInterval();
          } else {
            // not_started
            setSessionState('not_started');
            setElapsedSeconds(0);
            accumulatedMsRef.current = 0;
            startTimeRef.current = null;
            tabSwitchesRef.current = 0;
            totalTimeAwayMsRef.current = 0;
            lastSwitchTimeRef.current = null;
            hiddenStartTimeRef.current = null;
            tabSwitchHistoryRef.current = [];
            setTabSwitches(0);
            setTotalTimeAwayMs(0);
            setLastSwitchTime(null);
            setTabSwitchHistory([]);
            stopTimerInterval();
          }
        } catch (e) {
          setCode(getProblemStarterCode(data, language));
          setSessionState('not_started');
          setElapsedSeconds(0);
          accumulatedMsRef.current = 0;
          startTimeRef.current = null;
          tabSwitchesRef.current = 0;
          totalTimeAwayMsRef.current = 0;
          lastSwitchTimeRef.current = null;
          hiddenStartTimeRef.current = null;
          tabSwitchHistoryRef.current = [];
          setTabSwitches(0);
          setTotalTimeAwayMs(0);
          setLastSwitchTime(null);
          setTabSwitchHistory([]);
          stopTimerInterval();
        }
      } else {
        // Question-First mode: initially not started, timer at 0
        setCode(getProblemStarterCode(data, language));
        setSessionState('not_started');
        setElapsedSeconds(0);
        accumulatedMsRef.current = 0;
        startTimeRef.current = null;
        setCompletedSummary(null);
        tabSwitchesRef.current = 0;
        totalTimeAwayMsRef.current = 0;
        lastSwitchTimeRef.current = null;
        hiddenStartTimeRef.current = null;
        tabSwitchHistoryRef.current = [];
        setTabSwitches(0);
        setTotalTimeAwayMs(0);
        setLastSwitchTime(null);
        setTabSwitchHistory([]);
        stopTimerInterval();
      }

      setExecResult(null);
      setExplanationData(null);
      setDebugGuide(null);
      setDebugError(null);
      setExplainError(null);
      // Restore hint history from localStorage to survive page reloads & component re-renders
      let restoredHints = [];
      try {
        const savedHintsRaw = localStorage.getItem(`codeacharya_hints_history_${pid}`);
        if (savedHintsRaw) {
          restoredHints = JSON.parse(savedHintsRaw) || [];
        }
      } catch (e) {
        restoredHints = [];
      }
      setHintsHistory(restoredHints);
      setHintLevel(restoredHints.length > 0 ? Math.max(...restoredHints.map(h => h.hint_level || 1)) : 1);
    } catch (err) {
      console.error('Failed to load problem:', err);
    }
  };

  // Dynamic question generation flow connecting frontend to backend AI generator
  const handleLaunchFreshQuestion = async (
    topic = launcherTopic, 
    difficulty = launcherDifficulty, 
    subtopic = launcherSubtopic,
    count = generationCount
  ) => {
    if (isGenerating) return;
    setIsGenerating(true);
    setGenerateError(null);
    setGenerateSuccess(false);

    const effectiveSubtopic = subtopic && subtopic !== 'All' ? subtopic : undefined;

    try {
      if (count > 1) {
        // Batch Generation Endpoint
        const res = await fetch('/api/problems/generate-batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic: topic,
            difficulty: difficulty,
            language: language,
            subtopic: effectiveSubtopic,
            count: count,
            previous_titles: seenProblemTitles,
            previous_ids: seenProblemIds
          })
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Server returned ${res.status}`);
        }

        const batchData = await res.json();
        const batchQuestions = batchData.questions || [];
        if (batchQuestions.length === 0) {
          throw new Error('No problems were returned from the generator.');
        }

        batchQuestions.forEach(p => {
          setSeenProblemIds(prev => [...prev.filter(id => id !== p.id), p.id]);
          setSeenProblemTitles(prev => [...prev.filter(t => t !== p.title), p.title]);
          if (onProblemCreated) onProblemCreated(p);
        });

        const chosen = batchQuestions[0];
        if (onSelectProblem) onSelectProblem(chosen.id);

        setGenerateSuccess(true);
        setTimeout(() => {
          setCurrentProblem(chosen);
          const starterCode = getProblemStarterCode(chosen, language);
          setCode(starterCode);
          setExecResult(null);
          setExplanationData(null);
          setDebugGuide(null);
          setHintLevel(1);
          setHintsHistory([]);
          setIsGenerating(false);
          setGenerateSuccess(false);
        }, 400);

      } else {
        // Single Question Endpoint
        const res = await fetch('/api/generate-question', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            topic: topic,
            difficulty: difficulty,
            language: language,
            subtopic: effectiveSubtopic,
            count: 1,
            previous_titles: seenProblemTitles,
            previous_ids: seenProblemIds
          })
        });

        if (!res.ok) {
          const errorData = await res.json().catch(() => ({}));
          throw new Error(errorData.detail || `Server returned ${res.status}`);
        }

        const newProblem = await res.json();

        // Track history to prevent duplicates
        setSeenProblemIds(prev => [...prev.filter(id => id !== newProblem.id), newProblem.id]);
        setSeenProblemTitles(prev => [...prev.filter(t => t !== newProblem.title), newProblem.title]);

        // Inform parent app
        if (onProblemCreated) {
          onProblemCreated(newProblem);
        }
        if (onSelectProblem) {
          onSelectProblem(newProblem.id);
        }

        setGenerateSuccess(true);

        // Transition to code environment with starter code loaded
        setTimeout(() => {
          setCurrentProblem(newProblem);
          const starterCode = getProblemStarterCode(newProblem, language);
          setCode(starterCode);
          setExecResult(null);
          setExplanationData(null);
          setDebugGuide(null);
          setHintLevel(1);
          setHintsHistory([]);
          setIsGenerating(false);
          setGenerateSuccess(false);
        }, 400);
      }

    } catch (err) {
      console.error('Failed to generate question:', err);
      setGenerateError(err.message || 'Unable to generate a question right now. Please try again.');
      setIsGenerating(false);
      setGenerateSuccess(false);
    }
  };

  const performLanguageChange = useCallback((newLang) => {
    if (!newLang || newLang === language) return;

    // 1. Update language state in parent & localStorage
    setLanguage(newLang);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('codeacharya_preferred_lang', newLang);
    }

    // 2. Clear old editor code and load new language starter template
    const starter = getProblemStarterCode(currentProblem, newLang);
    setCode(starter);

    // 3. Clear stale execution, test output, and AI analysis results
    setExecResult(null);
    setExplanationData(null);
    setDebugGuide(null);
    setDebugError(null);
    setExplainError(null);

    // 4. Invalidate pending debug/explain requests
    debugReqIdRef.current += 1;
    explainReqIdRef.current += 1;
    setIsDebugging(false);
    setIsExplaining(false);

    // 5. Persist to storage, preserving attemptId, timers, sessionState, hints, and tabSwitches
    if (currentProblem) {
      saveSessionToStorage(
        currentProblem.id,
        sessionState,
        accumulatedMsRef.current,
        startTimeRef.current,
        starter,
        newLang,
        completedSummary,
        tabSwitchesRef.current,
        totalTimeAwayMsRef.current,
        lastSwitchTimeRef.current,
        tabSwitchHistoryRef.current,
        attemptIdRef.current
      );
    }

    // 6. Reset pending selection and close modal
    setPendingLanguage(null);
    setIsLanguageModalOpen(false);
  }, [language, setLanguage, currentProblem, setCode, sessionState, completedSummary]);

  const handleLanguageChange = useCallback((newLang) => {
    if (!newLang) return;

    // 1. Edge Case: If editor is locked by global Full-Screen Coding Restriction, prevent language changes
    if (isLockedRef.current) {
      return;
    }

    // 2. Edge Case: Selecting the currently active language does nothing
    if (newLang === language) {
      return;
    }

    // 3. Edge Case: If modal is already confirming, prevent duplicate submissions
    if (isConfirmingLanguage) {
      return;
    }

    // 4. Check whether editor contains existing / user-written code
    const isEditorEmpty = !code || code.trim().length === 0;

    if (isEditorEmpty) {
      // Allow language switch without unnecessary confirmation
      performLanguageChange(newLang);
      return;
    }

    // Editor contains code -> show confirmation modal
    setPendingLanguage(newLang);
    setIsLanguageModalOpen(true);
  }, [language, isConfirmingLanguage, code, performLanguageChange]);

  const handleCancelLanguageChange = () => {
    setPendingLanguage(null);
    setIsLanguageModalOpen(false);
  };

  const handleConfirmLanguageChange = () => {
    if (!pendingLanguage || isConfirmingLanguage) return;
    setIsConfirmingLanguage(true);
    try {
      performLanguageChange(pendingLanguage);
    } finally {
      setIsConfirmingLanguage(false);
    }
  };

  // Register language change handler with parent App component
  useEffect(() => {
    if (typeof onRegisterLanguageHandler === 'function') {
      onRegisterLanguageHandler(handleLanguageChange);
      return () => onRegisterLanguageHandler(null);
    }
  }, [onRegisterLanguageHandler, handleLanguageChange]);

  const handleCodeChange = (newVal) => {
    // Prevent typing, deleting, pasting, cutting or any modifications when not running or editor is locked
    if (sessionState !== 'running' || isLockedRef.current) {
      return;
    }
    const val = newVal || '';
    setCode(val);
    if (currentProblem && sessionState === 'running') {
      saveSessionToStorage(currentProblem.id, sessionState, accumulatedMsRef.current, startTimeRef.current, val, language, completedSummary);
    }
  };

  const resetCode = () => {
    if (!currentProblem || sessionState === 'paused' || sessionState === 'completed' || isLockedRef.current) return;
    const starter = getProblemStarterCode(currentProblem, language);
    setCode(starter);
    if (currentProblem) {
      saveSessionToStorage(
        currentProblem.id, 
        sessionState, 
        accumulatedMsRef.current, 
        startTimeRef.current, 
        starter, 
        language, 
        completedSummary,
        tabSwitchesRef.current,
        totalTimeAwayMsRef.current,
        lastSwitchTimeRef.current,
        tabSwitchHistoryRef.current
      );
    }
  };

  const handleStartCoding = async () => {
    if (!currentProblem) return;

    // Enforce Full-Screen requirement before starting coding
    const fsRes = await requestBrowserFullscreen();
    const verified = isBrowserFullscreen();

    if (!verified) {
      setIsLocked(true);
      isLockedRef.current = true;
      setLockReason('fullscreen_exit');
      setLockErrorMessage(fsRes.error || 'Full-screen mode is required to write code. Please allow full-screen mode when prompted.');
      return;
    }

    setIsLocked(false);
    isLockedRef.current = false;
    setLockErrorMessage('');

    logSessionLockTelemetry({
      eventType: 'fullscreen_entered',
      questionId: currentProblem.id,
      metadata: { initial_start: true }
    });

    const now = Date.now();
    startTimeRef.current = now;
    accumulatedMsRef.current = 0;
    setElapsedSeconds(0);
    setSessionState('running');
    setCompletedSummary(null);
    tabSwitchesRef.current = 0;
    totalTimeAwayMsRef.current = 0;
    lastSwitchTimeRef.current = null;
    hiddenStartTimeRef.current = null;
    tabSwitchHistoryRef.current = [];
    setTabSwitches(0);
    setTotalTimeAwayMs(0);
    setLastSwitchTime(null);
    setTabSwitchHistory([]);
    try {
      localStorage.removeItem(`codeacharya_tab_switch_history_${currentProblem.id}`);
    } catch (e) {}
    startTimerInterval();

    const newAttemptId = 'att_' + Date.now().toString(36) + '_' + Math.random().toString(36).substring(2, 8);
    attemptIdRef.current = newAttemptId;

    saveSessionToStorage(currentProblem.id, 'running', 0, now, code, language, null, 0, 0, null, [], newAttemptId);

    try {
      fetch('/api/session/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          language: language,
          time_spent_seconds: 0,
          session_status: 'running',
          attempt_id: newAttemptId,
          start_time: new Date(now).toISOString(),
          code: code,
          is_locked: false
        })
      }).catch(e => console.warn('Failed to record attempt start:', e));
    } catch (e) {}
  };

  const handlePauseCoding = () => {
    if (!currentProblem) return;
    if (sessionState === 'running') {
      const now = Date.now();
      const currentMs = accumulatedMsRef.current + (startTimeRef.current ? now - startTimeRef.current : 0);
      accumulatedMsRef.current = currentMs;
      startTimeRef.current = null;
      stopTimerInterval();

      // If page was hidden when paused, safely finalize active time away up to this moment
      if (hiddenStartTimeRef.current) {
        const awaySinceHidden = Math.max(0, now - hiddenStartTimeRef.current);
        totalTimeAwayMsRef.current += awaySinceHidden;
        setTotalTimeAwayMs(totalTimeAwayMsRef.current);
        hiddenStartTimeRef.current = null;
      }

      const finalSec = Math.floor(currentMs / 1000);
      setElapsedSeconds(finalSec);
      setSessionState('paused');
      saveSessionToStorage(
        currentProblem.id, 
        'paused', 
        currentMs, 
        null, 
        code, 
        language, 
        completedSummary,
        tabSwitchesRef.current,
        totalTimeAwayMsRef.current,
        lastSwitchTimeRef.current,
        tabSwitchHistoryRef.current,
        attemptIdRef.current
      );

      try {
        fetch('/api/session/record', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            problem_id: currentProblem.id,
            language: language,
            time_spent_seconds: finalSec,
            session_status: 'paused',
            attempt_id: attemptIdRef.current,
            code: code,
            tab_switch_count: tabSwitchesRef.current,
            total_time_away_seconds: Math.floor(totalTimeAwayMsRef.current / 1000)
          })
        }).catch(e => console.warn('Failed to record paused session:', e));
      } catch (e) {}
    } else if (sessionState === 'paused' || sessionState === 'stopped') {
      handleResumeCoding();
    }
  };

  const handleResumeCoding = () => {
    if (!currentProblem) return;
    const now = Date.now();
    startTimeRef.current = now;
    setSessionState('running');
    startTimerInterval();
    saveSessionToStorage(
      currentProblem.id, 
      'running', 
      accumulatedMsRef.current, 
      now, 
      code, 
      language, 
      completedSummary,
      tabSwitchesRef.current,
      totalTimeAwayMsRef.current,
      lastSwitchTimeRef.current,
      tabSwitchHistoryRef.current,
      attemptIdRef.current
    );

    try {
      fetch('/api/session/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          language: language,
          time_spent_seconds: Math.floor(accumulatedMsRef.current / 1000),
          session_status: 'running',
          attempt_id: attemptIdRef.current,
          code: code
        })
      }).catch(e => console.warn('Failed to record resume session:', e));
    } catch (e) {}
  };


  const handleConfirmAbandon = async () => {
    if (!currentProblem) return;
    const now = Date.now();
    const currentMs = accumulatedMsRef.current + (sessionState === 'running' && startTimeRef.current ? now - startTimeRef.current : 0);
    accumulatedMsRef.current = currentMs;
    startTimeRef.current = null;
    stopTimerInterval();

    // Finalize any active time away if abandoning while hidden
    if (hiddenStartTimeRef.current) {
      const awaySinceHidden = Math.max(0, now - hiddenStartTimeRef.current);
      totalTimeAwayMsRef.current += awaySinceHidden;
      setTotalTimeAwayMs(totalTimeAwayMsRef.current);
      hiddenStartTimeRef.current = null;
    }

    const finalSec = Math.floor(currentMs / 1000);
    setElapsedSeconds(finalSec);
    setSessionState('abandoned');
    setIsAbandonModalOpen(false);

    try {
      await fetch('/api/session/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          language: language,
          time_spent_seconds: finalSec,
          status: 'abandoned',
          session_status: 'abandoned',
          attempt_id: attemptIdRef.current,
          code: code,
          passed_count: execResult?.passed_count || 0,
          total_count: execResult?.total_count || currentProblem.test_cases?.length || 0,
          tab_switch_count: tabSwitchesRef.current,
          total_time_away_seconds: Math.floor(totalTimeAwayMsRef.current / 1000),
          last_switch_timestamp: lastSwitchTimeRef.current,
          tab_switch_history: tabSwitchHistoryRef.current
        })
      });
      if (onRefreshProfile) onRefreshProfile();
    } catch (e) {
      console.warn('Failed to record abandoned session:', e);
    }

    saveSessionToStorage(
      currentProblem.id, 
      'abandoned', 
      currentMs, 
      null, 
      code, 
      language,
      null,
      tabSwitchesRef.current,
      totalTimeAwayMsRef.current,
      lastSwitchTimeRef.current,
      tabSwitchHistoryRef.current,
      attemptIdRef.current
    );

    if (pendingNavigationAction) {
      const act = pendingNavigationAction;
      setPendingNavigationAction(null);
      act();
    }
  };

  const handleStartNewAttempt = () => {
    if (!currentProblem) return;
    accumulatedMsRef.current = 0;
    startTimeRef.current = null;
    setElapsedSeconds(0);
    setSessionState('not_started');
    setCompletedSummary(null);
    setExecResult(null);
    tabSwitchesRef.current = 0;
    totalTimeAwayMsRef.current = 0;
    lastSwitchTimeRef.current = null;
    hiddenStartTimeRef.current = null;
    tabSwitchHistoryRef.current = [];
    setTabSwitches(0);
    setTotalTimeAwayMs(0);
    setLastSwitchTime(null);
    setTabSwitchHistory([]);
    try {
      localStorage.removeItem(`codeacharya_tab_switch_history_${currentProblem.id}`);
    } catch (e) {}
    stopTimerInterval();
    attemptIdRef.current = null;
    const starter = getProblemStarterCode(currentProblem, language);
    setCode(starter);
    saveSessionToStorage(currentProblem.id, 'not_started', 0, null, starter, language, null, 0, 0, null, [], null);
  };

  const handleNavBack = () => {
    if (sessionState === 'running' || sessionState === 'paused') {
      setPendingNavigationAction(() => () => {
        if (onBack) onBack();
        else {
          if (onResetSelection) onResetSelection();
          setCurrentProblem(null);
        }
      });
      setIsAbandonModalOpen(true);
    } else {
      if (onBack) onBack();
      else {
        if (onResetSelection) onResetSelection();
        setCurrentProblem(null);
      }
    }
  };

  const handleProblemCardClick = (pid) => {
    if (pid === currentProblem?.id) return;
    if (sessionState === 'running' || sessionState === 'paused') {
      setPendingNavigationAction(() => () => {
        onSelectProblem(pid);
      });
      setIsAbandonModalOpen(true);
    } else {
      onSelectProblem(pid);
    }
  };

  const handleResetCode = () => {
    if (!currentProblem || sessionState === 'paused' || sessionState === 'completed') return;
    const starter = getProblemStarterCode(currentProblem, language);
    setCode(starter);
    setExecResult(null);
    setCompletedSummary(null);

    // Reset code only!
    // Tab-switch statistics and complete history are strictly preserved across code resets.
    saveSessionToStorage(
      currentProblem.id, 
      sessionState, 
      accumulatedMsRef.current, 
      startTimeRef.current, 
      starter, 
      language, 
      null, 
      tabSwitchesRef.current, 
      totalTimeAwayMsRef.current, 
      lastSwitchTimeRef.current,
      tabSwitchHistoryRef.current
    );
  };

  const executeCode = async () => {
    if (!currentProblem || sessionState !== 'running' || isLockedRef.current || !isBrowserFullscreen()) {
      if (isLockedRef.current || !isBrowserFullscreen()) {
        handleLockEditor('fullscreen_exit');
      }
      return;
    }

    // Calculate exact current elapsed seconds
    const now = Date.now();
    const currentMs = accumulatedMsRef.current + (sessionState === 'running' && startTimeRef.current ? now - startTimeRef.current : 0);
    const currentSec = Math.floor(currentMs / 1000);

    // If currently hidden during run, record up to now
    if (hiddenStartTimeRef.current) {
      const awaySinceHidden = Math.max(0, now - hiddenStartTimeRef.current);
      totalTimeAwayMsRef.current += awaySinceHidden;
      setTotalTimeAwayMs(totalTimeAwayMsRef.current);
      hiddenStartTimeRef.current = now;
    }

    setIsExecuting(true);
    setActiveBottomTab('tests');
    scrollToBottomPanel();

    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          code: code,
          language: language,
          time_spent_seconds: currentSec,
          session_status: sessionState,
          is_locked: isLockedRef.current,
          tab_switch_count: tabSwitchesRef.current,
          total_time_away_seconds: Math.floor(totalTimeAwayMsRef.current / 1000),
          last_switch_timestamp: lastSwitchTimeRef.current,
          tab_switch_history: tabSwitchHistoryRef.current,
          unique_hints_used: hintsHistory.length,
          attempt_id: attemptIdRef.current,
          start_time: startTimeRef.current ? new Date(startTimeRef.current).toISOString() : null
        })
      });

      if (res.status === 403) {
        const errData = await res.json().catch(() => ({}));
        setIsLocked(true);
        isLockedRef.current = true;
        setLockReason('fullscreen_exit');
        setLockErrorMessage(errData.detail || 'Execution blocked: Full-screen mode is required.');
        setIsExecuting(false);
        return;
      }

      const data = await res.json();
      if (data?.attempt_id) {
        attemptIdRef.current = data.attempt_id;
      }
      setExecResult(data);

      // Strict automatic completion verification:
      // 1. status is success
      // 2. total testcases > 0 (empty suites do NOT complete)
      // 3. passed_count === total_count (all required test cases pass)
      const isAllPassed = (data.status === 'success' && data.total_count > 0 && data.passed_count === data.total_count);

      if (isAllPassed) {
        // Stop timer automatically
        stopTimerInterval();
        accumulatedMsRef.current = currentMs;
        startTimeRef.current = null;
        setElapsedSeconds(currentSec);
        setSessionState('completed');

        const summary = {
          title: currentProblem.title,
          language: language,
          finalDurationSeconds: currentSec,
          finalDurationFormatted: formatTime(currentSec),
          tabSwitches: tabSwitchesRef.current,
          totalTimeAwayFormatted: formatDuration(Math.floor(totalTimeAwayMsRef.current / 1000)),
          passedCount: data.passed_count,
          totalCount: data.total_count,
          runtimeMs: data.runtime_ms,
          timestamp: new Date().toLocaleString(),
          status: 'Completed',
          tabSwitchHistory: tabSwitchHistoryRef.current,
          attemptId: attemptIdRef.current
        };
        setCompletedSummary(summary);
        saveSessionToStorage(
          currentProblem.id, 
          'completed', 
          currentMs, 
          null, 
          code, 
          language, 
          summary,
          tabSwitchesRef.current,
          totalTimeAwayMsRef.current,
          lastSwitchTimeRef.current,
          tabSwitchHistoryRef.current,
          attemptIdRef.current
        );

        confetti({
          particleCount: 100,
          spread: 75,
          origin: { y: 0.6 }
        });

        if (onRefreshProfile) {
          onRefreshProfile();
        }
      } else if (data.ast_feedback && data.ast_feedback.suspected_bugs?.length > 0) {
        // Automatically switch to AST view if critical syntax/base case bug detected
        setActiveBottomTab('ast');
      }
      scrollToBottomPanel();
    } catch (err) {
      console.error('Execution failed:', err);
    } finally {
      setIsExecuting(false);
      scrollToBottomPanel();
    }
  };

  const fetchHint = async (levelToFetch) => {
    if (!currentProblem) return;
    setIsLoadingHint(true);
    try {
      const res = await fetch('/api/hints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          code: code,
          language: language,
          hint_level: levelToFetch,
          error_context: execResult?.stderr || null
        })
      });
      const data = await res.json();
      
      setHintsHistory(prev => {
        const filtered = prev.filter(h => h.hint_level !== data.hint_level);
        const updated = [...filtered, data].sort((a, b) => a.hint_level - b.hint_level);
        try {
          localStorage.setItem(`codeacharya_hints_history_${currentProblem.id}`, JSON.stringify(updated));
        } catch (e) {}

        // Requirement 9: Recalculate displayed overall score when a new hint is revealed after evaluation
        if (execResult && execResult.score_data) {
          const isPending = execResult.score_data?.is_empty_submission || execResult.score_data?.scoring_status === 'not_evaluated';
          if (!isPending) {
            const newHintsCount = updated.length;
            const newIndepScore = calculateIndependentScore(newHintsCount);
            setExecResult(oldExec => {
              if (!oldExec || !oldExec.score_data) return oldExec;
              const oldBreakdown = oldExec.score_data.breakdown || {};
              const oldIndep = oldBreakdown.independent?.points_earned ?? 10;
              const scoreDiff = newIndepScore - oldIndep;
              const updatedOverall = Math.max(0, Math.min(100, Math.round(((oldExec.overall_score || 0) + scoreDiff) * 10) / 10));
              return {
                ...oldExec,
                overall_score: updatedOverall,
                unique_hints_used: newHintsCount,
                independent_score: newIndepScore,
                score_data: {
                  ...oldExec.score_data,
                  overall_score: updatedOverall,
                  unique_hints_used: newHintsCount,
                  independent_score: newIndepScore,
                  breakdown: {
                    ...oldBreakdown,
                    independent: {
                      ...(oldBreakdown.independent || {}),
                      points_earned: newIndepScore,
                      raw_score: newIndepScore,
                      unique_hints_used: newHintsCount,
                      notes: `Used ${newHintsCount} progressive hint${newHintsCount !== 1 ? 's' : ''} (${newIndepScore}/10 earned).`
                    }
                  }
                }
              };
            });
          }
        }

        return updated;
      });
      setHintLevel(levelToFetch);
    } catch (err) {
      console.error('Failed to get hint:', err);
    } finally {
      setIsLoadingHint(false);
    }
  };

  const openHintModal = () => {
    setIsHintOpen(true);
    if (hintsHistory.length === 0) {
      fetchHint(1);
    }
  };

  const unlockNextHint = () => {
    if (hintLevel < 4) {
      fetchHint(hintLevel + 1);
    }
  };

  const explainCode = async () => {
    if (!currentProblem || isExplaining) return;

    // Gracefully handle empty code
    if (!code || !code.trim()) {
      setActiveBottomTab('explanation');
      setExplanationData({
        summary: 'The code editor is currently empty. Please write or load code for this problem to view an algorithmic breakdown and complexity analysis.',
        purpose: 'No code provided to analyze.',
        algorithmic_approach: 'N/A',
        execution_flow: ['No code instructions to execute.'],
        key_components: {
          loops: 'None',
          conditions: 'None',
          data_structures: 'None'
        },
        time_complexity: 'N/A',
        time_rationale: 'Cannot determine time complexity without code.',
        space_complexity: 'N/A',
        space_rationale: 'Cannot determine space complexity without code.',
        edge_cases_and_limitations: ['Please write or paste code into the editor to run analysis.'],
        strengths: [],
        optimizations: []
      });
      setExplainError(null);
      scrollToBottomPanel();
      return;
    }

    const currentReqId = ++explainReqIdRef.current;
    const reqLang = language;
    setIsExplaining(true);
    setExplainError(null);
    setActiveBottomTab('explanation');
    scrollToBottomPanel();

    try {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          code: code,
          language: language,
          problem_title: currentProblem.title,
          problem_statement: currentProblem.description
        })
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned status ${res.status}`);
      }

      const data = await res.json();
      if (currentReqId === explainReqIdRef.current && reqLang === language) {
        setExplanationData(data);
        scrollToBottomPanel();
      }
    } catch (err) {
      if (currentReqId === explainReqIdRef.current) {
        console.error('Explain code failed:', err);
        setExplainError(err.message || 'Failed to generate code explanation. Please check your network or try again.');
        scrollToBottomPanel();
      }
    } finally {
      if (currentReqId === explainReqIdRef.current) {
        setIsExplaining(false);
        scrollToBottomPanel();
      }
    }
  };

  const launchDebugger = async () => {
    if (!currentProblem || isDebugging) return;

    // Gracefully handle empty code
    if (!code || !code.trim()) {
      setActiveBottomTab('debugger');
      setDebugGuide({
        status: 'empty_code',
        primary_symptom: 'Code Editor is Empty',
        bug_summary: 'No code statements were found in the active editor.',
        relevant_section: null,
        why_it_occurs: 'The editor does not contain any executable logic or function definitions.',
        investigation_steps: [
          'Step 1: Write or paste your solution code in the editor.',
          'Step 2: Ensure your function signature matches the problem parameters.',
          'Step 3: Click "Run & Test" to execute tests or "Debug Guide" for guided analysis.'
        ],
        suggested_correction: 'Provide a complete function implementation before requesting debugging guidance.',
        edge_cases_to_check: [],
        socratic_prompt: 'What initial approach or algorithm do you plan to implement?',
        detected_anomalies: []
      });
      setDebugError(null);
      scrollToBottomPanel();
      return;
    }

    const currentReqId = ++debugReqIdRef.current;
    const reqLang = language;
    setIsDebugging(true);
    setDebugError(null);
    setActiveBottomTab('debugger');
    scrollToBottomPanel();

    // Extract runtime or test failure context if code has been run
    let failingInput = null;
    let expectedOutput = null;
    let actualOutput = null;
    let errorMsg = null;

    if (execResult) {
      if (execResult.stderr && execResult.stderr.trim()) {
        errorMsg = execResult.stderr.trim();
      }
      if (execResult.results && execResult.results.length > 0) {
        const failedTest = execResult.results.find(t => !t.passed);
        if (failedTest) {
          failingInput = String(failedTest.input);
          expectedOutput = String(failedTest.expected);
          actualOutput = String(failedTest.actual);
          if (!errorMsg) {
            errorMsg = `Test case failure: input '${failedTest.input}' expected '${failedTest.expected}', got '${failedTest.actual}'`;
          }
        }
      }
    }

    try {
      const res = await fetch('/api/debug', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          code: code,
          language: language,
          error_message: errorMsg,
          failing_input: failingInput,
          expected_output: expectedOutput,
          actual_output: actualOutput,
          has_run: Boolean(execResult),
          problem_title: currentProblem.title,
          problem_statement: currentProblem.description
        })
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned status ${res.status}`);
      }

      const data = await res.json();
      if (currentReqId === debugReqIdRef.current && reqLang === language) {
        setDebugGuide(data);
        scrollToBottomPanel();
      }
    } catch (err) {
      if (currentReqId === debugReqIdRef.current) {
        console.error('Debugger failed:', err);
        setDebugError(err.message || 'Failed to retrieve debugging guide. Please check your network or try again.');
        scrollToBottomPanel();
      }
    } finally {
      if (currentReqId === debugReqIdRef.current) {
        setIsDebugging(false);
        scrollToBottomPanel();
      }
    }
  };

  const TOPIC_SUBTOPICS_MAP = {
    'Recursion & Backtracking': ['All', 'Basic Recursion', 'Backtracking', 'Divide & Conquer', 'Tree Recursion'],
    'Arrays & Hashing': ['All', 'Hash Maps & Sets', 'Prefix Sums', 'Frequency Counting', 'Array Manipulation'],
    'Strings': ['All', 'String Manipulation', 'Anagrams & Palindromes', 'Pattern Matching', 'Sliding Window'],
    'Stack & Queue': ['All', 'Monotonic Stack', 'Parentheses Matching', 'BFS Queue', 'Deque'],
    'Dynamic Programming': ['All', '1D DP', '2D Grid DP', 'Knapsack & Subsets', 'Memoization'],
    'Algorithms & Two Pointers': ['All', 'Two Pointers', 'Binary Search', 'Sorting & Partitioning', 'Sliding Window'],
    'Trees & Binary Search Trees': ['All', 'DFS Traversal', 'BFS Level Order', 'BST Properties', 'Path Sums'],
    'Graphs & Traversal': ['All', 'BFS / Shortest Path', 'DFS Traversal', 'Topological Sort', 'Cycle Detection']
  };

  const TOPICS = [
    { id: 'All', name: 'All Topics', icon: Layers },
    { id: 'Recursion & Backtracking', name: 'Recursion & Backtracking', icon: RotateCcw },
    { id: 'Arrays & Hashing', name: 'Arrays & Hashing', icon: Layers },
    { id: 'Strings', name: 'Strings', icon: FileCode2 },
    { id: 'Stack & Queue', name: 'Stack & Queue', icon: Terminal },
    { id: 'Dynamic Programming', name: 'Dynamic Programming', icon: Sparkles },
    { id: 'Algorithms & Two Pointers', name: 'Algorithms & Two Pointers', icon: Activity },
    { id: 'Trees & Binary Search Trees', name: 'Trees & BST', icon: FolderTree },
    { id: 'Graphs & Traversal', name: 'Graphs & Traversal', icon: Activity }
  ];

  const getDifficultyBadgeClass = (diff) => {
    if (diff === 'Easy') return 'badge-easy';
    if (diff === 'Medium') return 'badge-medium';
    if (diff === 'Hard') return 'badge-hard';
    return 'badge-topic';
  };

  const isProblemSolved = (pid) => {
    if (!studentProfile) return false;
    return (
      studentProfile.activity_log?.some(a => a.action === 'Solved' && (a.problem === pid || a.problem?.toLowerCase().includes(pid))) ||
      studentProfile.viva_history?.some(v => v.problem_id === pid && v.overall_score >= 70)
    );
  };

  const filteredProblems = problems.filter(p => {
    const matchesTopic = selectedTopic === 'All' || p.topic === selectedTopic;
    const matchesDiff = selectedDifficulty === 'All' || p.difficulty === selectedDifficulty;
    const isGen = Boolean(p.is_generated);
    const matchesSource = selectedSource === 'All' || 
      (selectedSource === 'curated' && !isGen) || 
      (selectedSource === 'generated' && isGen);
    const matchesSearch = !searchQuery.trim() || 
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      p.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.subtopic && p.subtopic.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTopic && matchesDiff && matchesSource && matchesSearch;
  });

  const easyProblems = filteredProblems.filter(p => p.difficulty === 'Easy');
  const mediumProblems = filteredProblems.filter(p => p.difficulty === 'Medium');
  const hardProblems = filteredProblems.filter(p => p.difficulty === 'Hard');

  const topicCount = problems.filter(p => selectedTopic === 'All' || p.topic === selectedTopic).length;
  const easyCount = problems.filter(p => (selectedTopic === 'All' || p.topic === selectedTopic) && p.difficulty === 'Easy').length;
  const mediumCount = problems.filter(p => (selectedTopic === 'All' || p.topic === selectedTopic) && p.difficulty === 'Medium').length;
  const hardCount = problems.filter(p => (selectedTopic === 'All' || p.topic === selectedTopic) && p.difficulty === 'Hard').length;
  const generatedCount = problems.filter(p => (selectedTopic === 'All' || p.topic === selectedTopic) && p.is_generated).length;
  const curatedCount = topicCount - generatedCount;

  return (
    <div style={{ padding: '16px 20px', maxWidth: 1680, margin: '0 auto' }}>
      {!currentProblem ? (
        /* =========================================================================
            GUIDED TOPIC & DIFFICULTY SELECTOR (Topic, Difficulty, and Question Generation)
           ========================================================================= */
        <div style={{ maxWidth: 1180, margin: '16px auto', display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Hero Banner */}
          <div className="glass-panel" style={{
            padding: '36px 32px',
            textAlign: 'center',
            borderRadius: 20,
            position: 'relative',
            overflow: 'hidden',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.4)'
          }}>
            {/* Background decorative glow */}
            <div style={{
              position: 'absolute',
              top: '-50%',
              left: '50%',
              transform: 'translateX(-50%)',
              width: 500,
              height: 300,
              background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)',
              pointerEvents: 'none'
            }} />

            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              padding: '6px 16px',
              borderRadius: 9999,
              background: 'rgba(99, 102, 241, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              color: '#a5b4fc',
              fontSize: '0.825rem',
              fontWeight: 600,
              marginBottom: 16
            }}>
              <Compass size={15} />
              <span>Step-by-Step Learning Flow</span>
            </div>

            <h1 style={{
              fontSize: '2.2rem',
              fontWeight: 800,
              margin: '0 0 10px 0',
              fontFamily: 'var(--font-heading)',
              letterSpacing: '-0.02em'
            }}>
              Choose a <span className="gradient-text">Topic</span>, select a <span className="gradient-text">Difficulty</span>, and start <span className="gradient-text">Coding</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: 680, margin: '0 auto 24px auto', lineHeight: 1.6 }}>
              Select a DSA topic and target difficulty level. Each time you request a question, the system will generate a new and different problem.
            </p>

            {/* Quick Actions: Language Switcher & Full Matrix */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, flexWrap: 'wrap' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(15, 23, 42, 0.8)',
                padding: '4px 6px',
                borderRadius: 10,
                border: '1px solid var(--border-glass)'
              }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginRight: 8, marginLeft: 4 }}>
                  Language:
                </span>
                {[
                  { id: 'python', label: '🐍 Python', gradient: 'linear-gradient(135deg, #3b82f6, #1d4ed8)' },
                  { id: 'c', label: '🔷 C', gradient: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
                  { id: 'cpp', label: '⚙️ C++', gradient: 'linear-gradient(135deg, #06b6d4, #0891b2)' },
                  { id: 'java', label: '☕ Java', gradient: 'linear-gradient(135deg, #ef4444, #b91c1c)' }
                ].map(l => (
                  <button
                    key={l.id}
                    onClick={() => handleLanguageChange(l.id)}
                    disabled={isLocked}
                    style={{
                      padding: '5px 12px',
                      borderRadius: 6,
                      fontSize: '0.775rem',
                      fontWeight: 600,
                      border: 'none',
                      cursor: isLocked ? 'not-allowed' : 'pointer',
                      opacity: isLocked ? 0.6 : 1,
                      background: language === l.id ? l.gradient : 'transparent',
                      color: language === l.id ? '#fff' : 'var(--text-muted)',
                      transition: 'all 0.2s'
                    }}
                    title={isLocked ? 'Editor locked: Full-screen mode required' : `Code in ${l.label}`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>

              <button
                onClick={() => setIsCurriculumModalOpen(true)}
                className="btn btn-secondary"
                style={{ padding: '8px 16px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: 6 }}
              >
                <BookOpen size={14} />
                <span>View Full Curriculum Matrix</span>
              </button>
            </div>
          </div>

          {/* STEP 1: TOPIC SELECTION */}
          <div className="glass-panel" style={{ padding: '24px 28px', borderRadius: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '0.9rem',
                  boxShadow: '0 0 12px rgba(99, 102, 241, 0.4)'
                }}>
                  1
                </div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>
                    Step 1: Select a DSA Topic
                  </h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                    Choose the DSA topic you want to solve problems in (8 core categories)
                  </p>
                </div>
              </div>

              <span style={{
                fontSize: '0.8rem',
                padding: '4px 12px',
                borderRadius: 9999,
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                color: '#a5b4fc',
                fontWeight: 600
              }}>
                Selected Topic: <strong>{launcherTopic}</strong>
              </span>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: 12
            }}>
              {TOPICS.filter(t => t.id !== 'All').map(topic => {
                const Icon = topic.icon;
                const isSelected = launcherTopic === topic.id;
                const count = problems.filter(p => p.topic === topic.id).length;
                return (
                  <div
                    key={topic.id}
                    onClick={() => {
                      setLauncherTopic(topic.id);
                      setSelectedTopic(topic.id);
                    }}
                    style={{
                      padding: '14px 16px',
                      borderRadius: 12,
                      background: isSelected 
                        ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.22), rgba(139, 92, 246, 0.12))' 
                        : 'rgba(15, 23, 42, 0.65)',
                      border: isSelected ? '2px solid #818cf8' : '1px solid var(--border-glass)',
                      boxShadow: isSelected ? '0 0 20px rgba(99, 102, 241, 0.35)' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12
                    }}
                  >
                    <div style={{
                      width: 36,
                      height: 36,
                      borderRadius: 10,
                      background: isSelected ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'rgba(255,255,255,0.06)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <Icon size={18} color={isSelected ? '#fff' : 'var(--text-muted)'} />
                    </div>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: isSelected ? '#fff' : '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {topic.name}
                      </div>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                        {count} Questions
                      </div>
                    </div>
                    {isSelected && <Check size={18} color="#818cf8" />}
                  </div>
                );
              })}
            </div>

            {/* Subtopic Filter Chips */}
            <div style={{ marginTop: 18, paddingTop: 16, borderTop: '1px solid var(--border-glass)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600 }}>
                Target Algorithmic Subtopic / Technique (Optional):
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {(TOPIC_SUBTOPICS_MAP[launcherTopic] || ['All']).map(sub => {
                  const isSubSelected = launcherSubtopic === sub;
                  return (
                    <button
                      key={sub}
                      onClick={() => setLauncherSubtopic(sub)}
                      style={{
                        padding: '4px 12px',
                        borderRadius: 8,
                        fontSize: '0.775rem',
                        fontWeight: 600,
                        border: isSubSelected ? '1px solid #818cf8' : '1px solid var(--border-glass)',
                        background: isSubSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(15, 23, 42, 0.6)',
                        color: isSubSelected ? '#a5b4fc' : 'var(--text-muted)',
                        cursor: 'pointer',
                        transition: 'all 0.15s'
                      }}
                    >
                      {sub === 'All' ? '⚡ Any / All Subtopics' : sub}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* STEP 2: DIFFICULTY LEVEL SELECTION */}
          <div className="glass-panel" style={{ padding: '24px 28px', borderRadius: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 800,
                  fontSize: '0.9rem',
                  boxShadow: '0 0 12px rgba(16, 185, 129, 0.4)'
                }}>
                  2
                </div>
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, margin: 0 }}>
                    Step 2: Select Difficulty Level
                  </h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                    Select Easy, Medium, or Hard difficulty
                  </p>
                </div>
              </div>

              <span style={{
                fontSize: '0.8rem',
                padding: '4px 12px',
                borderRadius: 9999,
                background: launcherDifficulty === 'Easy' ? 'rgba(16, 185, 129, 0.15)' : launcherDifficulty === 'Medium' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                border: `1px solid ${launcherDifficulty === 'Easy' ? '#10b981' : launcherDifficulty === 'Medium' ? '#f59e0b' : '#f43f5e'}`,
                color: launcherDifficulty === 'Easy' ? '#34d399' : launcherDifficulty === 'Medium' ? '#fbbf24' : '#fb7185',
                fontWeight: 600
              }}>
                Selected Level: <strong>{launcherDifficulty}</strong>
              </span>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: 16
            }}>
              {/* EASY CARD */}
              {(() => {
                const isSelected = launcherDifficulty === 'Easy';
                const count = problems.filter(p => p.topic === launcherTopic && p.difficulty === 'Easy').length;
                return (
                  <div
                    onClick={() => {
                      setLauncherDifficulty('Easy');
                      setSelectedDifficulty('Easy');
                    }}
                    style={{
                      padding: '20px',
                      borderRadius: 14,
                      background: isSelected ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.08))' : 'rgba(15, 23, 42, 0.65)',
                      border: isSelected ? '2px solid #10b981' : '1px solid var(--border-glass)',
                      boxShadow: isSelected ? '0 0 25px rgba(16, 185, 129, 0.3)' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 8
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></span>
                        <strong style={{ fontSize: '1.05rem', color: '#34d399' }}>🟢 Easy</strong>
                      </div>
                      <span className="badge badge-easy">{count} available</span>
                    </div>
                    <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                      Fundamental logic, base condition clarity, basic loops & recursion steps.
                    </p>
                  </div>
                );
              })()}

              {/* MEDIUM CARD */}
              {(() => {
                const isSelected = launcherDifficulty === 'Medium';
                const count = problems.filter(p => p.topic === launcherTopic && p.difficulty === 'Medium').length;
                return (
                  <div
                    onClick={() => {
                      setLauncherDifficulty('Medium');
                      setSelectedDifficulty('Medium');
                    }}
                    style={{
                      padding: '20px',
                      borderRadius: 14,
                      background: isSelected ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.08))' : 'rgba(15, 23, 42, 0.65)',
                      border: isSelected ? '2px solid #f59e0b' : '1px solid var(--border-glass)',
                      boxShadow: isSelected ? '0 0 25px rgba(245, 158, 11, 0.3)' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 8
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 8px #f59e0b' }}></span>
                        <strong style={{ fontSize: '1.05rem', color: '#fbbf24' }}>🟡 Medium</strong>
                      </div>
                      <span className="badge badge-medium">{count} available</span>
                    </div>
                    <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                      Top tech interview favorites, time-space optimizations, two pointers & branching.
                    </p>
                  </div>
                );
              })()}

              {/* HARD CARD */}
              {(() => {
                const isSelected = launcherDifficulty === 'Hard';
                const count = problems.filter(p => p.topic === launcherTopic && p.difficulty === 'Hard').length;
                return (
                  <div
                    onClick={() => {
                      setLauncherDifficulty('Hard');
                      setSelectedDifficulty('Hard');
                    }}
                    style={{
                      padding: '20px',
                      borderRadius: 14,
                      background: isSelected ? 'linear-gradient(135deg, rgba(244, 63, 94, 0.2), rgba(225, 29, 72, 0.08))' : 'rgba(15, 23, 42, 0.65)',
                      border: isSelected ? '2px solid #f43f5e' : '1px solid var(--border-glass)',
                      boxShadow: isSelected ? '0 0 25px rgba(244, 63, 94, 0.3)' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 8
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#f43f5e', boxShadow: '0 0 8px #f43f5e' }}></span>
                        <strong style={{ fontSize: '1.05rem', color: '#fb7185' }}>🔴 Hard</strong>
                      </div>
                      <span className="badge badge-hard">{count} available</span>
                    </div>
                    <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>
                      Complex edge cases, DP state transitions, backtracking pruning & advanced structures.
                    </p>
                  </div>
                );
              })()}
            </div>
          </div>

          {/* STEP 3: ACTION - GET DIFFERENT QUESTION & START CODING */}
          <div className="glass-panel" style={{
            padding: '24px 28px',
            borderRadius: 16,
            background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95))',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 16
          }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 4, fontWeight: 600 }}>
                Target Session Configuration:
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                <span style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff' }}>
                  {launcherTopic}
                </span>
                {launcherSubtopic !== 'All' && (
                  <>
                    <span style={{ color: 'var(--text-muted)' }}>•</span>
                    <span style={{
                      fontSize: '0.75rem',
                      padding: '2px 8px',
                      borderRadius: 6,
                      background: 'rgba(59, 130, 246, 0.15)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      color: '#93c5fd',
                      fontWeight: 600
                    }}>
                      {launcherSubtopic}
                    </span>
                  </>
                )}
                <span style={{ color: 'var(--text-muted)' }}>•</span>
                <span className={`badge ${launcherDifficulty === 'Easy' ? 'badge-easy' : launcherDifficulty === 'Medium' ? 'badge-medium' : 'badge-hard'}`}>
                  {launcherDifficulty} Category
                </span>
                <span style={{ color: 'var(--text-muted)' }}>•</span>
                <span style={{
                  fontSize: '0.75rem',
                  padding: '2px 8px',
                  borderRadius: 6,
                  background: 'rgba(99, 102, 241, 0.15)',
                  color: '#a5b4fc',
                  fontWeight: 600
                }}>
                  {language.toUpperCase()}
                </span>
              </div>
            </div>

            <button
              onClick={() => handleLaunchFreshQuestion(launcherTopic, launcherDifficulty, launcherSubtopic, 1)}
              disabled={isGenerating}
              className="btn btn-primary"
              style={{
                padding: '12px 28px',
                fontSize: '0.95rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                boxShadow: '0 0 25px rgba(99, 102, 241, 0.5)',
                opacity: isGenerating ? 0.75 : 1,
                cursor: isGenerating ? 'not-allowed' : 'pointer'
              }}
            >
              {isGenerating ? (
                <>
                  <RefreshCw size={18} className="animate-spin" />
                  <span>Generating {generationCount > 1 ? `${generationCount} Questions` : 'Question'}...</span>
                </>
              ) : generateSuccess ? (
                <>
                  <Check size={18} color="#10b981" />
                  <span>Question Ready ✓</span>
                </>
              ) : (
                <>
                  <Shuffle size={18} />
                  <span>Generate {generationCount > 1 ? `${generationCount} Questions` : 'Question'} & Start Coding 🎲</span>
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>

          {/* Generation Error Alert */}
          {generateError && (
            <div style={{
              padding: '12px 18px',
              borderRadius: 12,
              background: 'rgba(244, 63, 94, 0.15)',
              border: '1px solid rgba(244, 63, 94, 0.4)',
              color: '#fb7185',
              fontSize: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 10
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <AlertOctagon size={18} />
                <span>{generateError}</span>
              </div>
              <button
                onClick={() => handleLaunchFreshQuestion(launcherTopic, launcherDifficulty, launcherSubtopic, generationCount)}
                className="btn btn-secondary"
                style={{ padding: '4px 10px', fontSize: '0.75rem' }}
              >
                Retry
              </button>
            </div>
          )}

          {/* Direct Question Select Grid (Optional Quick Pick) */}
          {(() => {
            const availableProbs = problems.filter(p => p.topic === launcherTopic && p.difficulty === launcherDifficulty);
            if (availableProbs.length === 0) return null;
            const curCount = availableProbs.filter(p => !p.is_generated).length;
            const genCount = availableProbs.filter(p => p.is_generated).length;
            return (
              <div style={{ marginTop: 4 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                    Or choose directly from available questions ({availableProbs.length} available):
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', gap: 10, alignItems: 'center' }}>
                    <span style={{ color: '#6ee7b7' }}>📚 {curCount} Curated</span>
                    {genCount > 0 && <span style={{ color: '#c4b5fd' }}>🤖 {genCount} AI Generated</span>}
                    {genCount > 0 && (
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (window.confirm("Are you sure you want to completely remove all AI generated practice questions?")) {
                            try {
                              const res = await fetch('/api/problems/clear-generated', { method: 'POST' });
                              if (res.ok) {
                                if (onRefreshProfile) await onRefreshProfile();
                              }
                            } catch (err) {
                              console.error('Failed to clear generated problems:', err);
                            }
                          }
                        }}
                        style={{
                          background: 'rgba(239, 68, 68, 0.15)',
                          border: '1px solid rgba(239, 68, 68, 0.3)',
                          color: '#f87171',
                          borderRadius: 6,
                          padding: '2px 8px',
                          fontSize: '0.7rem',
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: 4
                        }}
                        title="Remove all AI-generated questions"
                      >
                        <Trash2 size={11} /> Clear AI Questions
                      </button>
                    )}
                  </div>
                </div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 10
                }}>
                  {availableProbs.map(p => {
                    const solved = isProblemSolved(p.id);
                    return (
                      <div
                        key={p.id}
                        onClick={() => {
                          setSeenProblemIds(prev => [...prev.filter(id => id !== p.id), p.id]);
                          handleProblemCardClick(p.id);
                        }}
                        className="problem-card"
                        style={{ padding: '12px 16px', borderRadius: 12, cursor: 'pointer' }}
                      >
                        <div style={{ minWidth: 0, flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4, flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f1f5f9' }}>{p.title}</span>
                            {solved && <Check size={14} color="#10b981" title="Solved" />}
                            {p.is_generated ? (
                              <span style={{
                                fontSize: '0.675rem',
                                padding: '1px 6px',
                                borderRadius: 4,
                                background: 'rgba(139, 92, 246, 0.18)',
                                border: '1px solid rgba(139, 92, 246, 0.35)',
                                color: '#c4b5fd',
                                fontWeight: 600
                              }}>
                                🤖 AI
                              </span>
                            ) : (
                              <span style={{
                                fontSize: '0.675rem',
                                padding: '1px 6px',
                                borderRadius: 4,
                                background: 'rgba(16, 185, 129, 0.12)',
                                border: '1px solid rgba(16, 185, 129, 0.3)',
                                color: '#6ee7b7',
                                fontWeight: 600
                              }}>
                                📚 Curated
                              </span>
                            )}
                            {p.subtopic && (
                              <span style={{
                                fontSize: '0.675rem',
                                padding: '1px 6px',
                                borderRadius: 4,
                                background: 'rgba(59, 130, 246, 0.12)',
                                border: '1px solid rgba(59, 130, 246, 0.25)',
                                color: '#93c5fd',
                                fontWeight: 500
                              }}>
                                {p.subtopic}
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                            {p.test_cases_count || 4} test cases • Starter Code in {language.toUpperCase()}
                          </div>
                        </div>
                        <ArrowRight size={15} color="var(--text-muted)" />
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}
        </div>
      ) : (
        /* =========================================================================
            ACTIVE PROBLEM WORKSPACE (Two-Panel IDE + Top Navigation Bar)
           ========================================================================= */
        <div>
          {/* Active Question Top Bar */}
          <div className="glass-panel" style={{
            padding: '12px 18px',
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12
          }}>
            {/* Left: Change Topic / Level & Problem Info */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={handleNavBack}
                className="nav-back-btn"
                style={{
                  padding: '6px 12px',
                  fontSize: '0.775rem'
                }}
                title="Back to Topic & Level selection"
                aria-label="Back"
              >
                <ArrowLeft size={14} />
                <span>Back</span>
              </button>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <span className="badge badge-topic">{currentProblem.topic}</span>
                <span className={`badge ${getDifficultyBadgeClass(currentProblem.difficulty)}`}>
                  {currentProblem.difficulty}
                </span>
                {currentProblem.is_generated ? (
                  <span style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: 'rgba(139, 92, 246, 0.2)',
                    border: '1px solid rgba(139, 92, 246, 0.45)',
                    color: '#c4b5fd',
                    fontWeight: 600,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4
                  }}>
                    <Sparkles size={11} /> AI Generated
                  </span>
                ) : (
                  <span style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: 'rgba(16, 185, 129, 0.15)',
                    border: '1px solid rgba(16, 185, 129, 0.35)',
                    color: '#6ee7b7',
                    fontWeight: 600
                  }}>
                    📚 Curated
                  </span>
                )}
                {currentProblem.subtopic && (
                  <span style={{
                    fontSize: '0.72rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: 'rgba(59, 130, 246, 0.15)',
                    border: '1px solid rgba(59, 130, 246, 0.3)',
                    color: '#93c5fd',
                    fontWeight: 500
                  }}>
                    {currentProblem.subtopic}
                  </span>
                )}
                <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                  {currentProblem.title}
                </span>
              </div>
            </div>

            {/* Right: Different Question button & Curriculum Matrix */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              <button
                onClick={() => handleLaunchFreshQuestion(currentProblem.topic, currentProblem.difficulty)}
                disabled={isGenerating}
                className="btn btn-purple"
                style={{
                  padding: '6px 14px',
                  fontSize: '0.775rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  boxShadow: '0 0 15px rgba(139, 92, 246, 0.4)',
                  opacity: isGenerating ? 0.75 : 1,
                  cursor: isGenerating ? 'not-allowed' : 'pointer'
                }}
                title="Generate another problem for this topic & difficulty"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw size={14} className="animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Shuffle size={14} />
                    <span>🎲 Generate New Question</span>
                  </>
                )}
              </button>

              <button
                onClick={() => setIsExplorerExpanded(!isExplorerExpanded)}
                className="btn btn-secondary"
                style={{ padding: '6px 12px', fontSize: '0.775rem' }}
              >
                {isExplorerExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                <span>{isExplorerExpanded ? "Hide Explorer" : "All Questions"}</span>
              </button>

              <button
                onClick={() => setIsCurriculumModalOpen(true)}
                className="btn btn-secondary"
                style={{ padding: '6px 12px', fontSize: '0.775rem' }}
                title="Open full Topics & Difficulty matrix"
              >
                <BookOpen size={14} />
                <span>Matrix</span>
              </button>
            </div>
          </div>

          {/* Collapsible Curriculum Explorer */}
          <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: 20 }}>
        {/* Explorer Header: Title + Language Indicator + Collapse Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 34,
              height: 34,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)'
            }}>
              <FolderTree size={18} color="#fff" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
                  Interactive Curriculum Explorer
                </h3>
                <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                  ({problems.length} Problems • 8 Core Topics)
                </span>
              </div>
              <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: 0 }}>
                Choose programming language, select topic, and explore Easy, Medium & Hard categories
              </p>
            </div>
          </div>

          {/* Quick Language Switcher & Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            {/* View All Categories Matrix Button */}
            <button
              onClick={() => setIsCurriculumModalOpen(true)}
              className="btn btn-purple"
              style={{
                padding: '5px 12px',
                fontSize: '0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: 6
              }}
              title="Open full Topics & Difficulty matrix"
            >
              <BookOpen size={14} />
              <span>Topics & Difficulty Matrix</span>
            </button>

            {/* Active Language Switcher */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              background: 'rgba(15, 23, 42, 0.85)',
              padding: '3px 4px',
              borderRadius: 8,
              border: '1px solid var(--border-glass)'
            }}>
              <button
                onClick={() => handleLanguageChange('python')}
                disabled={isLocked}
                style={{
                  padding: '4px 8px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: isLocked ? 'not-allowed' : 'pointer',
                  opacity: isLocked ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  background: language === 'python' ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' : 'transparent',
                  color: language === 'python' ? '#fff' : 'var(--text-muted)'
                }}
                title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in Python 3'}
              >
                <span>🐍 Python</span>
              </button>
              <button
                onClick={() => handleLanguageChange('c')}
                disabled={isLocked}
                style={{
                  padding: '4px 8px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: isLocked ? 'not-allowed' : 'pointer',
                  opacity: isLocked ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  background: language === 'c' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'transparent',
                  color: language === 'c' ? '#fff' : 'var(--text-muted)'
                }}
                title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in C (GCC)'}
              >
                <span>🔷 C</span>
              </button>
              <button
                onClick={() => handleLanguageChange('cpp')}
                disabled={isLocked}
                style={{
                  padding: '4px 8px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: isLocked ? 'not-allowed' : 'pointer',
                  opacity: isLocked ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  background: language === 'cpp' ? 'linear-gradient(135deg, #06b6d4, #0891b2)' : 'transparent',
                  color: language === 'cpp' ? '#fff' : 'var(--text-muted)'
                }}
                title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in C++ (C++20)'}
              >
                <span>⚙️ C++</span>
              </button>
              <button
                onClick={() => handleLanguageChange('java')}
                disabled={isLocked}
                style={{
                  padding: '4px 8px',
                  borderRadius: 6,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: isLocked ? 'not-allowed' : 'pointer',
                  opacity: isLocked ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  background: language === 'java' ? 'linear-gradient(135deg, #ef4444, #b91c1c)' : 'transparent',
                  color: language === 'java' ? '#fff' : 'var(--text-muted)'
                }}
                title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in Java (OpenJDK 21)'}
              >
                <span>☕ Java</span>
              </button>
            </div>

            {/* Toggle Explorer Expand/Collapse */}
            <button
              onClick={() => setIsExplorerExpanded(!isExplorerExpanded)}
              className="btn btn-secondary"
              style={{ padding: '6px 10px', fontSize: '0.75rem' }}
              title={isExplorerExpanded ? "Collapse Category Explorer" : "Expand Category Explorer"}
            >
              {isExplorerExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
              <span>{isExplorerExpanded ? "Collapse" : "Expand"}</span>
            </button>
          </div>
        </div>

        {/* Collapsible Content */}
        {isExplorerExpanded && (
          <div>
            {/* Topic Pills Bar */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              overflowX: 'auto',
              paddingBottom: 8,
              marginBottom: 12
            }}>
              {TOPICS.map(topic => {
                const Icon = topic.icon;
                const count = topic.id === 'All' 
                  ? problems.length 
                  : problems.filter(p => p.topic === topic.id).length;
                const mastery = studentProfile?.topic_mastery?.[topic.id];
                const isActive = selectedTopic === topic.id;

                return (
                  <button
                    key={topic.id}
                    onClick={() => setSelectedTopic(topic.id)}
                    className={`topic-pill ${isActive ? 'active' : ''}`}
                  >
                    <Icon size={14} />
                    <span>{topic.name}</span>
                    <span style={{
                      fontSize: '0.675rem',
                      padding: '1px 6px',
                      borderRadius: 10,
                      background: isActive ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                      color: isActive ? '#fff' : 'var(--text-muted)',
                      fontWeight: 700
                    }}>
                      {count}
                    </span>
                    {mastery && (
                      <span style={{
                        fontSize: '0.65rem',
                        color: mastery >= 80 ? '#34d399' : mastery >= 60 ? '#818cf8' : '#fbbf24',
                        fontWeight: 700
                      }}>
                        {mastery}%
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Difficulty Tabs & Search Filter Row */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 12,
              paddingTop: 10,
              borderTop: '1px solid rgba(255, 255, 255, 0.05)',
              marginBottom: 16
            }}>
              {/* Difficulty Category Tabs */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.775rem', color: 'var(--text-muted)', fontWeight: 600, marginRight: 4 }}>
                  Difficulty Categories:
                </span>
                
                <button
                  onClick={() => setSelectedDifficulty('All')}
                  className={`diff-filter-btn ${selectedDifficulty === 'All' ? 'active-all' : ''}`}
                >
                  <span>All ({topicCount})</span>
                </button>

                <button
                  onClick={() => setSelectedDifficulty('Easy')}
                  className={`diff-filter-btn ${selectedDifficulty === 'Easy' ? 'active-easy' : ''}`}
                >
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981' }}></span>
                  <span>Easy ({easyCount})</span>
                </button>

                <button
                  onClick={() => setSelectedDifficulty('Medium')}
                  className={`diff-filter-btn ${selectedDifficulty === 'Medium' ? 'active-medium' : ''}`}
                >
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }}></span>
                  <span>Medium ({mediumCount})</span>
                </button>

                <button
                  onClick={() => setSelectedDifficulty('Hard')}
                  className={`diff-filter-btn ${selectedDifficulty === 'Hard' ? 'active-hard' : ''}`}
                >
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f43f5e' }}></span>
                  <span>Hard ({hardCount})</span>
                </button>

                {/* Source Filter: Curated vs AI Generated */}
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: 4, marginLeft: 6, paddingLeft: 8, borderLeft: '1px solid var(--border-glass)' }}>
                  <button
                    onClick={() => setSelectedSource('All')}
                    className={`diff-filter-btn ${selectedSource === 'All' ? 'active-all' : ''}`}
                    style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                  >
                    <span>All ({topicCount})</span>
                  </button>
                  <button
                    onClick={() => setSelectedSource('curated')}
                    className={`diff-filter-btn ${selectedSource === 'curated' ? 'active-easy' : ''}`}
                    style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                  >
                    <span>📚 Curated ({curatedCount})</span>
                  </button>
                  <button
                    onClick={() => setSelectedSource('generated')}
                    className={`diff-filter-btn ${selectedSource === 'generated' ? 'active-medium' : ''}`}
                    style={{ fontSize: '0.72rem', padding: '3px 8px' }}
                  >
                    <span>🤖 AI ({generatedCount})</span>
                  </button>
                </div>
              </div>

              {/* Quick Search */}
              <div style={{ position: 'relative', minWidth: 220 }}>
                <Search size={14} style={{ position: 'absolute', left: 10, top: 9, color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search questions..."
                  style={{
                    width: '100%',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 8,
                    padding: '6px 10px 6px 30px',
                    fontSize: '0.775rem',
                    color: '#fff',
                    outline: 'none'
                  }}
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    style={{
                      position: 'absolute',
                      right: 8,
                      top: 6,
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      fontSize: '0.75rem'
                    }}
                  >
                    ×
                  </button>
                )}
              </div>
            </div>

            {/* Categorized Question Lists */}
            {selectedDifficulty === 'All' ? (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: 14
              }}>
                {/* 1. EASY CATEGORY */}
                <div className="category-lane" style={{ borderTop: '2px solid #10b981' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></span>
                        <strong style={{ fontSize: '0.85rem', color: '#34d399' }}>🟢 Easy Category</strong>
                      </div>
                      <div style={{ fontSize: '0.675rem', color: 'var(--text-muted)', marginTop: 2 }}>
                        Core Foundations & Base Logic
                      </div>
                    </div>
                    <span className="badge badge-easy">{easyProblems.length}</span>
                  </div>
                  {easyProblems.length === 0 ? (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontStyle: 'italic', padding: 8 }}>
                      No easy problems match filters.
                    </div>
                  ) : (
                    easyProblems.map(p => {
                      const isSelected = p.id === currentProblem?.id;
                      const solved = isProblemSolved(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => handleProblemCardClick(p.id)}
                          className={`problem-card ${isSelected ? 'active' : ''}`}
                        >
                          <div style={{ minWidth: 0, flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {p.title}
                              </span>
                              {solved && <Check size={13} color="#10b981" title="Solved" />}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              {p.topic}
                            </div>
                          </div>
                          <span className="badge badge-easy" style={{ fontSize: '0.625rem', padding: '1px 6px' }}>
                            Easy
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* 2. MEDIUM CATEGORY */}
                <div className="category-lane" style={{ borderTop: '2px solid #f59e0b' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 8px #f59e0b' }}></span>
                        <strong style={{ fontSize: '0.85rem', color: '#fbbf24' }}>🟡 Medium Category</strong>
                      </div>
                      <div style={{ fontSize: '0.675rem', color: 'var(--text-muted)', marginTop: 2 }}>
                        Interview Favorites & Optimization
                      </div>
                    </div>
                    <span className="badge badge-medium">{mediumProblems.length}</span>
                  </div>
                  {mediumProblems.length === 0 ? (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontStyle: 'italic', padding: 8 }}>
                      No medium problems match filters.
                    </div>
                  ) : (
                    mediumProblems.map(p => {
                      const isSelected = p.id === currentProblem?.id;
                      const solved = isProblemSolved(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => handleProblemCardClick(p.id)}
                          className={`problem-card ${isSelected ? 'active' : ''}`}
                        >
                          <div style={{ minWidth: 0, flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {p.title}
                              </span>
                              {solved && <Check size={13} color="#10b981" title="Solved" />}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              {p.topic}
                            </div>
                          </div>
                          <span className="badge badge-medium" style={{ fontSize: '0.625rem', padding: '1px 6px' }}>
                            Medium
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* 3. HARD CATEGORY */}
                <div className="category-lane" style={{ borderTop: '2px solid #f43f5e' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#f43f5e', boxShadow: '0 0 8px #f43f5e' }}></span>
                        <strong style={{ fontSize: '0.85rem', color: '#fb7185' }}>🔴 Hard Category</strong>
                      </div>
                      <div style={{ fontSize: '0.675rem', color: 'var(--text-muted)', marginTop: 2 }}>
                        Advanced Edge Cases & DP
                      </div>
                    </div>
                    <span className="badge badge-hard">{hardProblems.length}</span>
                  </div>
                  {hardProblems.length === 0 ? (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontStyle: 'italic', padding: 8 }}>
                      No hard problems match filters.
                    </div>
                  ) : (
                    hardProblems.map(p => {
                      const isSelected = p.id === currentProblem?.id;
                      const solved = isProblemSolved(p.id);
                      return (
                        <div
                          key={p.id}
                          onClick={() => handleProblemCardClick(p.id)}
                          className={`problem-card ${isSelected ? 'active' : ''}`}
                        >
                          <div style={{ minWidth: 0, flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {p.title}
                              </span>
                              {solved && <Check size={13} color="#10b981" title="Solved" />}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              {p.topic}
                            </div>
                          </div>
                          <span className="badge badge-hard" style={{ fontSize: '0.625rem', padding: '1px 6px' }}>
                            Hard
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            ) : (
              /* Specific Difficulty Grid */
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: 12
              }}>
                {filteredProblems.map(p => {
                  const isSelected = p.id === currentProblem?.id;
                  const solved = isProblemSolved(p.id);
                  return (
                    <div
                      key={p.id}
                      onClick={() => handleProblemCardClick(p.id)}
                      className={`problem-card ${isSelected ? 'active' : ''}`}
                    >
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
                          <span style={{ fontSize: '0.825rem', fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {p.title}
                          </span>
                          {solved && <Check size={13} color="#10b981" title="Solved" />}
                        </div>
                        <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                          {p.topic} • {p.test_cases_count || 4} test cases
                        </div>
                      </div>
                      <span className={`badge ${getDifficultyBadgeClass(p.difficulty)}`} style={{ fontSize: '0.65rem' }}>
                        {p.difficulty}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Two-Panel Layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(380px, 460px) minmax(0, 1fr)',
        gap: 16,
        alignItems: 'start'
      }}>
        {/* LEFT COLUMN: Problem Details */}
        <div className="glass-panel" style={{ padding: 22, maxHeight: 'calc(100vh - 150px)', overflowY: 'auto' }}>
          {currentProblem && (
            <div>
              {/* Badges */}
              {/* Badges & Status Strip */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                  <span className={`badge ${getDifficultyBadgeClass(currentProblem.difficulty)}`}>
                    {currentProblem.difficulty}
                  </span>
                  <span className="badge badge-topic">
                    {currentProblem.topic}
                  </span>
                  <span style={{
                    fontSize: '0.725rem',
                    padding: '3px 8px',
                    borderRadius: 9999,
                    fontWeight: 600,
                    background: language === 'python' ? 'rgba(59, 130, 246, 0.15)' : language === 'c' ? 'rgba(99, 102, 241, 0.15)' : language === 'cpp' ? 'rgba(6, 182, 212, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: language === 'python' ? '#60a5fa' : language === 'c' ? '#818cf8' : language === 'cpp' ? '#22d3ee' : '#f87171',
                    border: `1px solid ${language === 'python' ? 'rgba(59, 130, 246, 0.3)' : language === 'c' ? 'rgba(99, 102, 241, 0.3)' : language === 'cpp' ? 'rgba(6, 182, 212, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4
                  }}>
                    {language === 'python' ? '🐍 Python 3' : language === 'c' ? '🔷 C' : language === 'cpp' ? '⚙️ C++ 20' : '☕ Java 21'}
                  </span>
                </div>

                {isProblemSolved(currentProblem.id) ? (
                  <span style={{
                    fontSize: '0.725rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: 'rgba(16, 185, 129, 0.18)',
                    border: '1px solid rgba(16, 185, 129, 0.4)',
                    color: '#34d399',
                    fontWeight: 700,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4
                  }}>
                    <Check size={12} /> Solved
                  </span>
                ) : (
                  <span style={{
                    fontSize: '0.725rem',
                    padding: '3px 8px',
                    borderRadius: 6,
                    background: 'rgba(148, 163, 184, 0.1)',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    color: '#94a3b8',
                    fontWeight: 600
                  }}>
                    Unsolved
                  </span>
                )}
              </div>

              {/* Title */}
              <h1 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0 0 10px 0', fontFamily: 'var(--font-heading)', letterSpacing: '-0.02em', color: '#f8fafc' }}>
                {currentProblem.title}
              </h1>

              {/* Competitive Programming Meta Strip */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '6px 12px',
                background: 'rgba(15, 23, 42, 0.75)',
                borderRadius: 8,
                border: '1px solid var(--border-glass)',
                marginBottom: 18,
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                flexWrap: 'wrap'
              }}>
                <span>📈 Acceptance: <strong style={{ color: '#38bdf8' }}>74.8%</strong></span>
                <span>•</span>
                <span>⏱️ Limit: <strong style={{ color: '#cbd5e1' }}>2.0s</strong></span>
                <span>•</span>
                <span>💾 Memory: <strong style={{ color: '#cbd5e1' }}>256 MB</strong></span>
                <span>•</span>
                <span style={{ color: currentProblem.is_generated ? '#c4b5fd' : '#6ee7b7' }}>
                  {currentProblem.is_generated ? '🤖 AI Question' : '📚 Curated'}
                </span>
              </div>

              {/* Description */}
              <div style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.65, marginBottom: 22 }}>
                {currentProblem.description.split('\n\n').map((paragraph, idx) => (
                  <p key={idx} style={{ marginBottom: 12 }}>{paragraph}</p>
                ))}
              </div>

              {/* Input & Output Format */}
              {(currentProblem.inputFormat || currentProblem.input_format) && (
                <div style={{ marginBottom: 16 }}>
                  <h3 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6, fontWeight: 700 }}>
                    📥 Input Format
                  </h3>
                  <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5, background: 'rgba(15, 23, 42, 0.5)', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-glass)' }}>
                    {currentProblem.inputFormat || currentProblem.input_format}
                  </div>
                </div>
              )}
              {(currentProblem.outputFormat || currentProblem.output_format) && (
                <div style={{ marginBottom: 16 }}>
                  <h3 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6, fontWeight: 700 }}>
                    📤 Output Format
                  </h3>
                  <div style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5, background: 'rgba(15, 23, 42, 0.5)', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-glass)' }}>
                    {currentProblem.outputFormat || currentProblem.output_format}
                  </div>
                </div>
              )}

              {/* Examples - Terminal Style Cards */}
              <div style={{ marginBottom: 22 }}>
                <h3 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 10, fontWeight: 700 }}>
                  🧪 Test Examples
                </h3>
                {currentProblem.examples?.map((ex, i) => (
                  <div key={i} style={{
                    background: 'rgba(10, 15, 26, 0.85)',
                    borderRadius: 10,
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    overflow: 'hidden',
                    marginBottom: 10,
                    fontSize: '0.825rem',
                    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.4)'
                  }}>
                    <div style={{
                      padding: '6px 12px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--text-muted)'
                    }}>
                      <span>Example {i + 1}</span>
                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Standard I/O</span>
                    </div>
                    <div style={{ padding: '10px 14px' }}>
                      <div style={{ marginBottom: 6 }}>
                        <span style={{ color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600 }}>Input: </span>
                        <code style={{ color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 6px', borderRadius: 4 }}>
                          {typeof ex.input === 'object' ? JSON.stringify(ex.input) : ex.input}
                        </code>
                      </div>
                      <div style={{ marginBottom: ex.explanation ? 6 : 0 }}>
                        <span style={{ color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600 }}>Output: </span>
                        <code style={{ color: '#34d399', background: 'rgba(52, 211, 153, 0.1)', padding: '2px 6px', borderRadius: 4 }}>
                          {typeof ex.output === 'object' ? JSON.stringify(ex.output) : ex.output}
                        </code>
                      </div>
                      {ex.explanation && (
                        <div style={{ color: '#64748b', fontSize: '0.775rem', marginTop: 4, fontStyle: 'italic', borderTop: '1px dashed rgba(255,255,255,0.06)', paddingTop: 4 }}>
                          Explanation: {ex.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Constraints */}
              <div style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8, fontWeight: 700 }}>
                  📌 Constraints
                </h3>
                <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.825rem', color: '#94a3b8' }}>
                  {currentProblem.constraints?.map((c, i) => (
                    <li key={i} style={{ marginBottom: 4 }}><code>{c}</code></li>
                  ))}
                </ul>
              </div>

              {/* Learning Objectives */}
              {currentProblem.learning_objectives?.length > 0 && (
                <div style={{
                  background: 'rgba(99, 102, 241, 0.08)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  padding: 14,
                  borderRadius: 10
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#818cf8', fontSize: '0.825rem', fontWeight: 600, marginBottom: 8 }}>
                    <Sparkles size={15} />
                    <span>Learning Objectives:</span>
                  </div>
                  <ul style={{ margin: 0, paddingLeft: 16, fontSize: '0.8rem', color: '#cbd5e1' }}>
                    {currentProblem.learning_objectives.map((obj, i) => (
                      <li key={i} style={{ marginBottom: 4 }}>{obj}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Code Editor + Controls + Tabbed Inspection */}
        {/* RIGHT COLUMN: Code Editor + Controls + Tabbed Inspection */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {/* Editor Header Toolbar */}
          <div className="glass-panel" style={{ padding: '10px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
            {/* Left: Language & Reset */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              {/* Segmented Language Selector */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                background: 'rgba(15, 23, 42, 0.85)',
                padding: '2px 4px',
                borderRadius: 8,
                border: '1px solid var(--border-glass)'
              }}>
                <button
                  onClick={() => handleLanguageChange('python')}
                  disabled={isLocked}
                  style={{
                    padding: '5px 10px',
                    borderRadius: 6,
                    fontSize: '0.775rem',
                    fontWeight: 600,
                    border: 'none',
                    cursor: isLocked ? 'not-allowed' : 'pointer',
                    opacity: isLocked ? 0.6 : 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    background: language === 'python' ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' : 'transparent',
                    color: language === 'python' ? '#fff' : 'var(--text-muted)',
                    transition: 'all 0.2s'
                  }}
                  title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in Python 3'}
                >
                  <span>🐍 Python</span>
                </button>
                <button
                  onClick={() => handleLanguageChange('c')}
                  disabled={isLocked}
                  style={{
                    padding: '5px 10px',
                    borderRadius: 6,
                    fontSize: '0.775rem',
                    fontWeight: 600,
                    border: 'none',
                    cursor: isLocked ? 'not-allowed' : 'pointer',
                    opacity: isLocked ? 0.6 : 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    background: language === 'c' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'transparent',
                    color: language === 'c' ? '#fff' : 'var(--text-muted)',
                    transition: 'all 0.2s'
                  }}
                  title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in C (GCC)'}
                >
                  <span>🔷 C</span>
                </button>
                <button
                  onClick={() => handleLanguageChange('cpp')}
                  disabled={isLocked}
                  style={{
                    padding: '5px 10px',
                    borderRadius: 6,
                    fontSize: '0.775rem',
                    fontWeight: 600,
                    border: 'none',
                    cursor: isLocked ? 'not-allowed' : 'pointer',
                    opacity: isLocked ? 0.6 : 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    background: language === 'cpp' ? 'linear-gradient(135deg, #06b6d4, #0891b2)' : 'transparent',
                    color: language === 'cpp' ? '#fff' : 'var(--text-muted)',
                    transition: 'all 0.2s'
                  }}
                  title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in C++ (C++20)'}
                >
                  <span>⚙️ C++</span>
                </button>
                <button
                  onClick={() => handleLanguageChange('java')}
                  disabled={isLocked}
                  style={{
                    padding: '5px 10px',
                    borderRadius: 6,
                    fontSize: '0.775rem',
                    fontWeight: 600,
                    border: 'none',
                    cursor: isLocked ? 'not-allowed' : 'pointer',
                    opacity: isLocked ? 0.6 : 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    background: language === 'java' ? 'linear-gradient(135deg, #ef4444, #b91c1c)' : 'transparent',
                    color: language === 'java' ? '#fff' : 'var(--text-muted)',
                    transition: 'all 0.2s'
                  }}
                  title={isLocked ? 'Editor locked: Full-screen mode required' : 'Code in Java (OpenJDK 21)'}
                >
                  <span>☕ Java</span>
                </button>
              </div>

              {/* Assessment Mode Toggle & Status Indicator */}
              <button
                id="btn-assessment-mode-toggle"
                onClick={() => setIsAssessmentMode(!isAssessmentMode)}
                className="btn btn-secondary"
                style={{
                  padding: '5px 10px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 5,
                  background: isAssessmentMode ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.12)',
                  border: isAssessmentMode ? '1px solid rgba(239, 68, 68, 0.35)' : '1px solid rgba(16, 185, 129, 0.35)',
                  color: isAssessmentMode ? '#f87171' : '#34d399'
                }}
                title={isAssessmentMode ? "Assessment Mode: Pasting is disabled in coding editor and AI viva. Click to switch to Practice Mode." : "Practice Mode: Pasting is enabled. Click to enforce Assessment Mode."}
              >
                <ShieldCheck size={13} color={isAssessmentMode ? '#f87171' : '#34d399'} />
                <span>{isAssessmentMode ? 'Assessment: Paste Blocked' : 'Practice: Paste Allowed'}</span>
              </button>

              {sessionState !== 'not_started' && (
                <button 
                  id="btn-reset-code"
                  onClick={handleResetCode} 
                  disabled={sessionState === 'paused' || sessionState === 'completed'}
                  className="btn btn-secondary"
                  style={{
                    padding: '5px 12px',
                    fontSize: '0.775rem',
                    opacity: sessionState === 'paused' || sessionState === 'completed' ? 0.5 : 1,
                    cursor: sessionState === 'paused' || sessionState === 'completed' ? 'not-allowed' : 'pointer'
                  }}
                  title={sessionState === 'paused' ? 'Coding is paused. Resume the timer to edit your code.' : 'Reset editor content to clean starter code (tab-switch history is preserved)'}
                >
                  <RotateCcw size={13} /> Reset
                </button>
              )}

              {/* Live Timer & Session State Display */}
              <div 
                id="live-practice-timer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '5px 12px',
                  borderRadius: 8,
                  background: sessionState === 'running'
                    ? 'rgba(16, 185, 129, 0.15)'
                    : sessionState === 'paused'
                    ? 'rgba(245, 158, 11, 0.15)'
                    : sessionState === 'stopped'
                    ? 'rgba(244, 63, 94, 0.15)'
                    : sessionState === 'completed'
                    ? 'rgba(16, 185, 129, 0.25)'
                    : sessionState === 'abandoned'
                    ? 'rgba(244, 63, 94, 0.15)'
                    : 'rgba(15, 23, 42, 0.85)',
                  border: sessionState === 'running'
                    ? '1px solid rgba(16, 185, 129, 0.45)'
                    : sessionState === 'paused'
                    ? '1px solid rgba(245, 158, 11, 0.45)'
                    : sessionState === 'stopped'
                    ? '1px solid rgba(244, 63, 94, 0.45)'
                    : sessionState === 'completed'
                    ? '1px solid rgba(16, 185, 129, 0.65)'
                    : sessionState === 'abandoned'
                    ? '1px solid rgba(244, 63, 94, 0.45)'
                    : '1px solid var(--border-glass)',
                  transition: 'all 0.25s ease'
                }}
              >
                {sessionState === 'running' && (
                  <span style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: '#10b981',
                    boxShadow: '0 0 10px #10b981',
                    animation: 'pulse 1.5s infinite'
                  }} />
                )}
                {sessionState === 'paused' && (
                  <span style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: '#f59e0b',
                    boxShadow: '0 0 8px #f59e0b'
                  }} />
                )}
                {sessionState === 'stopped' && <Square size={13} fill="#fb7185" color="#fb7185" />}
                {sessionState === 'completed' && <Award size={14} color="#10b981" />}
                {sessionState === 'abandoned' && <Flag size={14} color="#f43f5e" />}
                {sessionState === 'not_started' && <Clock size={14} color="var(--text-muted)" />}

                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  fontSize: '0.825rem',
                  color: sessionState === 'running'
                    ? '#34d399'
                    : sessionState === 'paused'
                    ? '#fbbf24'
                    : sessionState === 'stopped'
                    ? '#fb7185'
                    : sessionState === 'completed'
                    ? '#10b981'
                    : sessionState === 'abandoned'
                    ? '#fb7185'
                    : 'var(--text-muted)'
                }}>
                  {sessionState === 'not_started' 
                    ? '00:00 (Not Started)' 
                    : sessionState === 'paused'
                    ? `Paused (${formatTime(elapsedSeconds)})`
                    : sessionState === 'completed'
                    ? `Solved in ${formatTime(elapsedSeconds)}`
                    : sessionState === 'abandoned'
                    ? `Abandoned (${formatTime(elapsedSeconds)})`
                    : formatTime(elapsedSeconds)}
                </span>
              </div>

              {/* Tab Switching Statistics Panel */}
              <div 
                id="tab-switch-stats-panel"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '5px 12px',
                  borderRadius: 8,
                  background: 'rgba(15, 23, 42, 0.85)',
                  border: '1px solid var(--border-glass)',
                  fontSize: '0.775rem',
                  color: 'var(--text-muted)',
                  userSelect: 'none'
                }}
                title="Activity signal: tracks tab visibility transitions during active coding practice (Preserved across Reset Code)"
              >
                <div 
                  onClick={() => setIsTabHistoryModalOpen(true)}
                  style={{ display: 'flex', alignItems: 'center', gap: 5, cursor: 'pointer' }}
                  title="Click to view tab switch history"
                >
                  <EyeOff size={13} style={{ color: tabSwitches > 0 ? '#f59e0b' : '#64748b' }} />
                  <span>Tab Switches:</span>
                  <strong style={{ 
                    color: tabSwitches > 0 ? '#f59e0b' : '#f8fafc', 
                    fontFamily: 'var(--font-mono)' 
                  }}>
                    {tabSwitches}
                  </strong>
                </div>

                <div style={{ width: 1, height: 14, background: 'rgba(148, 163, 184, 0.2)' }} />

                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Clock size={13} style={{ color: totalTimeAwayMs > 0 ? '#38bdf8' : '#64748b' }} />
                  <span>Total Time Away:</span>
                  <strong style={{ color: '#f8fafc', fontFamily: 'var(--font-mono)' }}>
                    {formatDuration(Math.floor(totalTimeAwayMs / 1000))}
                  </strong>
                </div>

                <div style={{ width: 1, height: 14, background: 'rgba(148, 163, 184, 0.2)' }} />

                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <span>Last Switch:</span>
                  <strong style={{ color: '#f8fafc', fontFamily: 'var(--font-mono)' }}>
                    {lastSwitchTime || '--'}
                  </strong>
                </div>

                <div style={{ width: 1, height: 14, background: 'rgba(148, 163, 184, 0.2)' }} />

                <button
                  id="btn-tab-history"
                  onClick={() => setIsTabHistoryModalOpen(true)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4,
                    padding: '2px 8px',
                    borderRadius: 6,
                    background: tabSwitchHistory.length > 0 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                    border: `1px solid ${tabSwitchHistory.length > 0 ? 'rgba(245, 158, 11, 0.35)' : 'rgba(255, 255, 255, 0.1)'}`,
                    color: tabSwitchHistory.length > 0 ? '#f59e0b' : 'var(--text-muted)',
                    fontSize: '0.725rem',
                    cursor: 'pointer',
                    fontWeight: 500,
                    transition: 'all 0.15s ease'
                  }}
                  title="View detailed Tab Switch History (IST timestamps)"
                >
                  <History size={12} />
                  <span>History</span>
                  {tabSwitchHistory.length > 0 && (
                    <span style={{
                      background: 'rgba(245, 158, 11, 0.3)',
                      color: '#f59e0b',
                      borderRadius: '50%',
                      width: 16,
                      height: 16,
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.65rem',
                      fontWeight: 700
                    }}>
                      {tabSwitchHistory.length}
                    </span>
                  )}
                </button>

                <div 
                  style={{ 
                    cursor: 'help', 
                    display: 'inline-flex', 
                    alignItems: 'center', 
                    marginLeft: 2, 
                    color: '#64748b' 
                  }}
                  title="Privacy & Limitations Notice: Detects when the coding tab becomes hidden or minimized using the browser Page Visibility API. It does not monitor browsing history, other applications, or keystrokes outside this page. Activity is recorded neutrally as practice engagement. Reset Code preserves this history."
                >
                  <HelpCircle size={12} />
                </div>
              </div>

              {/* Only Pause / Resume Button */}
              {sessionState === 'running' && (
                <button 
                  onClick={handlePauseCoding}
                  className="btn btn-secondary"
                  style={{ padding: '5px 12px', fontSize: '0.775rem', borderColor: 'rgba(245, 158, 11, 0.45)' }}
                  title="Pause timer"
                  aria-label="Pause Coding"
                >
                  <Pause size={13} color="#f59e0b" />
                  <span>Pause</span>
                </button>
              )}

              {sessionState === 'paused' && (
                <button 
                  onClick={handleResumeCoding}
                  className="btn btn-emerald glow-emerald"
                  style={{ padding: '5px 14px', fontSize: '0.775rem' }}
                  title="Resume timer"
                  aria-label="Resume Coding"
                >
                  <Play size={13} fill="#fff" />
                  <span>Resume</span>
                </button>
              )}
            </div>

            {/* Right: Controls & AI Actions */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              {sessionState === 'running' && (
                <button 
                  onClick={() => setIsAbandonModalOpen(true)}
                  className="btn btn-secondary"
                  style={{ padding: '6px 10px', fontSize: '0.75rem', color: '#fb7185', borderColor: 'rgba(244, 63, 94, 0.3)' }}
                  title="Abandon practice session"
                  aria-label="Abandon Session"
                >
                  <X size={13} />
                  <span>Abandon</span>
                </button>
              )}

              {sessionState === 'completed' && (
                <button 
                  onClick={handleStartNewAttempt}
                  className="btn btn-purple"
                  style={{ padding: '6px 12px', fontSize: '0.775rem' }}
                  title="Start a fresh practice attempt with a reset timer"
                >
                  <RotateCcw size={13} />
                  <span>New Attempt</span>
                </button>
              )}

              {sessionState === 'abandoned' && (
                <button 
                  onClick={handleStartNewAttempt}
                  className="btn btn-primary"
                  style={{ padding: '6px 14px', fontSize: '0.775rem' }}
                  title="Start a fresh practice session"
                >
                  <Play size={13} fill="#fff" />
                  <span>Try Again</span>
                </button>
              )}

              {/* Progressive Hint Button */}
              <button 
                onClick={openHintModal}
                className="btn btn-amber"
                style={{ padding: '6px 14px', fontSize: '0.825rem' }}
                disabled={sessionState === 'not_started'}
                title="Get progressive socratic hint (0: 10pts, 1: 9pts, 2: 7pts, 3: 4pts, ≥4: 1pt)"
              >
                <Lightbulb size={15} />
                <span>Get Hint {hintsHistory.length > 0 ? `(${hintsHistory.length} used • ${calculateIndependentScore(hintsHistory.length)}/10 pts)` : '(10/10 pts)'}</span>
              </button>

              {/* Debug Guide */}
              <button 
                onClick={launchDebugger}
                className="btn btn-secondary"
                disabled={isDebugging || sessionState === 'not_started'}
                style={{ padding: '6px 12px', fontSize: '0.825rem' }}
              >
                <Bug size={15} />
                <span>{isDebugging ? 'Analyzing...' : 'Debug Guide'}</span>
              </button>

              {/* AI Explain */}
              <button 
                onClick={explainCode}
                className="btn btn-secondary"
                disabled={isExplaining || sessionState === 'not_started'}
                style={{ padding: '6px 12px', fontSize: '0.825rem' }}
              >
                <HelpCircle size={15} />
                <span>{isExplaining ? 'Explaining...' : 'Explain Code'}</span>
              </button>

              {/* Run Code Button */}
              <button 
                onClick={executeCode}
                className="btn btn-emerald glow-emerald"
                disabled={isExecuting || sessionState !== 'running' || isLocked}
                style={{
                  padding: '7px 18px',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  opacity: (sessionState !== 'running' || isLocked) ? 0.6 : 1,
                  cursor: (sessionState !== 'running' || isLocked) ? 'not-allowed' : 'pointer',
                  boxShadow: (sessionState === 'running' && !isLocked) ? '0 0 20px rgba(16, 185, 129, 0.45)' : 'none'
                }}
                title={isLocked ? 'Full-screen mode is required to run code' : sessionState === 'not_started' ? 'Click Start Coding to begin session' : sessionState === 'paused' ? 'Resume session to run code' : 'Execute code and evaluate test cases (Ctrl + Enter)'}
              >
                <Play size={15} fill="#fff" />
                <span>{isExecuting ? 'Running...' : 'Run & Test'}</span>
                <kbd style={{
                  marginLeft: 4,
                  fontSize: '0.675rem',
                  padding: '1px 5px',
                  borderRadius: 4,
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid rgba(255, 255, 255, 0.25)',
                  color: '#e2e8f0'
                }}>
                  Ctrl ↵
                </kbd>
              </button>
            </div>
          </div>

          {/* QUESTION-FIRST EXPERIENCE: Initial Locked Welcome Screen */}
          {sessionState === 'not_started' && (
            <div className="glass-panel-elevated animate-fade-in" style={{
              padding: '32px 28px',
              borderRadius: 14,
              border: '1px solid rgba(99, 102, 241, 0.35)',
              background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 27, 75, 0.6))',
              boxShadow: '0 12px 30px rgba(0, 0, 0, 0.5)',
              textAlign: 'center'
            }}>
              <div style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px auto',
                boxShadow: '0 0 20px rgba(99, 102, 241, 0.3)'
              }}>
                <Timer size={28} color="#818cf8" />
              </div>

              <span className="badge badge-topic" style={{ marginBottom: 12, display: 'inline-block' }}>
                Timed Practice Mode • Question-First Experience
              </span>

              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '8px 0 10px 0', color: '#f8fafc', fontFamily: 'var(--font-heading)' }}>
                {currentProblem?.title}
              </h2>

              <p style={{ maxWidth: 620, margin: '0 auto 24px auto', fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.6 }}>
                Carefully review the problem statement, constraints, and sample input/output on the left. When you are ready to implement your algorithm, click <strong>Start Coding</strong> to unlock the editor and initiate the session timer.
              </p>

              {/* Target Problem Meta Highlights */}
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 16,
                flexWrap: 'wrap',
                marginBottom: 28
              }}>
                <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border-glass)', fontSize: '0.825rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Difficulty: </span>
                  <strong style={{ color: currentProblem?.difficulty === 'Easy' ? '#34d399' : currentProblem?.difficulty === 'Medium' ? '#fbbf24' : '#fb7185' }}>
                    {currentProblem?.difficulty}
                  </strong>
                </div>

                <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border-glass)', fontSize: '0.825rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Test Cases: </span>
                  <strong style={{ color: '#60a5fa' }}>{currentProblem?.test_cases?.length || 4} Required Cases</strong>
                </div>

                <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border-glass)', fontSize: '0.825rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Active Language: </span>
                  <strong style={{ color: '#c084fc' }}>{language.toUpperCase()}</strong>
                </div>
              </div>

              {/* Start Coding Button */}
              <button
                id="btn-start-coding"
                onClick={handleStartCoding}
                className="btn btn-emerald glow-emerald"
                style={{
                  padding: '14px 38px',
                  fontSize: '1.05rem',
                  fontWeight: 700,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 10,
                  borderRadius: 10,
                  boxShadow: '0 0 30px rgba(16, 185, 129, 0.5)'
                }}
                aria-label="Start Coding and begin practice timer"
              >
                <Play size={20} fill="#fff" />
                <span>Start Coding (Begin Timer)</span>
              </button>

              {/* Locked Editor Preview */}
              <div style={{ marginTop: 28, textAlign: 'left' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.775rem', color: 'var(--text-muted)' }}>
                    <Lock size={13} color="#f59e0b" />
                    <span>Editor Preview (Locked until session starts)</span>
                  </div>
                  <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                    {language.toUpperCase()} starter template
                  </span>
                </div>
                <pre style={{
                  background: 'rgba(9, 13, 22, 0.75)',
                  border: '1px dashed rgba(245, 158, 11, 0.3)',
                  borderRadius: 8,
                  padding: '12px 16px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.775rem',
                  color: '#64748b',
                  overflowX: 'auto',
                  maxHeight: 120,
                  margin: 0
                }}>
                  {code}
                </pre>
              </div>
            </div>
          )}

          {/* ACTIVE CODING WORKSPACE: Monaco Editor Container (Running, Paused, Completed, Abandoned) */}
          {sessionState !== 'not_started' && (
            <div style={{ position: 'relative' }}>
              {/* Paused State Banner */}
              {sessionState === 'paused' && (
                <div className="animate-slide-down" style={{
                  padding: '10px 16px',
                  marginBottom: 10,
                  background: 'rgba(245, 158, 11, 0.15)',
                  border: '1px solid rgba(245, 158, 11, 0.45)',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 12
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: '0.85rem', color: '#fbbf24' }}>
                    <Lock size={16} />
                    <span><strong>Coding is paused. Resume the timer to edit your code.</strong> <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginLeft: 6 }}>(Timer frozen at <strong>{formatTime(elapsedSeconds)}</strong>)</span></span>
                  </div>
                  <button
                    onClick={handleResumeCoding}
                    className="btn btn-emerald"
                    style={{ padding: '6px 14px', fontSize: '0.775rem' }}
                    aria-label="Resume Coding"
                  >
                    <Play size={13} fill="#fff" /> Resume
                  </button>
                </div>
              )}

              {/* Abandoned State Banner */}
              {sessionState === 'abandoned' && (
                <div className="animate-slide-down" style={{
                  padding: '10px 16px',
                  marginBottom: 10,
                  background: 'rgba(244, 63, 94, 0.12)',
                  border: '1px solid rgba(244, 63, 94, 0.4)',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 12
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: '0.85rem', color: '#fb7185' }}>
                    <Flag size={16} />
                    <span><strong>Session Abandoned:</strong> Final elapsed duration recorded: <strong>{formatTime(elapsedSeconds)}</strong>. Your code is preserved. Ready for another shot?</span>
                  </div>
                  <button
                    onClick={handleStartNewAttempt}
                    className="btn btn-primary"
                    style={{ padding: '6px 14px', fontSize: '0.775rem' }}
                  >
                    <Play size={13} fill="#fff" /> Start Fresh
                  </button>
                </div>
              )}

              {/* Monaco Editor Container with Real IDE Window Chrome */}
              <div className="ide-panel" style={{
                borderRadius: 12,
                overflow: 'hidden',
                border: sessionState === 'paused'
                  ? '1px solid rgba(245, 158, 11, 0.55)'
                  : sessionState === 'completed'
                  ? '1px solid rgba(16, 185, 129, 0.55)'
                  : sessionState === 'running'
                  ? '1px solid rgba(99, 102, 241, 0.45)'
                  : '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: sessionState === 'running' 
                  ? '0 12px 35px rgba(0,0,0,0.65), 0 0 25px rgba(99, 102, 241, 0.18)' 
                  : '0 12px 35px rgba(0,0,0,0.65)',
                transition: 'all 0.25s ease'
              }}>
                {/* IDE Window Title Bar & Active File Tab */}
                <div className="editor-window-chrome">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div className="window-dots">
                      <span className="dot-red" title="Close"></span>
                      <span className="dot-yellow" title="Minimize"></span>
                      <span className="dot-green" title="Maximize"></span>
                    </div>
                    {/* Active File Tab */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      background: 'rgba(255, 255, 255, 0.07)',
                      padding: '4px 12px',
                      borderRadius: '6px 6px 0 0',
                      borderBottom: '2px solid #6366f1',
                      fontSize: '0.75rem',
                      fontFamily: 'var(--font-mono)',
                      color: '#f8fafc',
                      fontWeight: 600,
                      boxShadow: '0 0 10px rgba(99, 102, 241, 0.25)'
                    }}>
                      <span>{language === 'python' ? '🐍 solution.py' : language === 'c' ? '🔷 solution.c' : language === 'cpp' ? '⚙️ solution.cpp' : '☕ Solution.java'}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {isLocked ? (
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 5,
                        background: 'rgba(239, 68, 68, 0.2)',
                        border: '1px solid rgba(239, 68, 68, 0.5)',
                        padding: '2px 8px',
                        borderRadius: 6,
                        color: '#fca5a5',
                        fontWeight: 700
                      }}>
                        <Lock size={12} color="#ef4444" />
                        <span>LOCKED • FULL-SCREEN REQUIRED</span>
                      </span>
                    ) : (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                        <span style={{
                          width: 7,
                          height: 7,
                          borderRadius: '50%',
                          background: sessionState === 'running' ? '#10b981' : sessionState === 'paused' ? '#f59e0b' : '#64748b',
                          boxShadow: sessionState === 'running' ? '0 0 8px #10b981' : 'none'
                        }}></span>
                        <span style={{ fontFamily: 'var(--font-mono)', color: sessionState === 'running' ? '#34d399' : 'var(--text-muted)' }}>
                          {sessionState === 'running' ? 'LIVE RUNTIME' : sessionState === 'paused' ? 'PAUSED' : 'READY'}
                        </span>
                      </span>
                    )}
                    <span>•</span>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>UTF-8</span>
                    <span>•</span>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>Spaces: 4</span>
                  </div>
                </div>

                {/* Blocked Paste Warning Toast */}
                {showPasteWarning && (
                  <div className="animate-slide-down" style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 14px',
                    margin: '8px 12px',
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.45)',
                    borderRadius: 8,
                    fontSize: '0.8rem',
                    color: '#fca5a5'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <AlertTriangle size={15} color="#ef4444" style={{ flexShrink: 0 }} />
                      <span><strong>Action Blocked:</strong> {pasteWarningMessage}</span>
                    </div>
                    <button
                      onClick={() => setShowPasteWarning(false)}
                      style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer', fontSize: '0.8rem' }}
                    >
                      ✕
                    </button>
                  </div>
                )}

                <div style={{ height: 420, position: 'relative' }}>
                  <Editor
                    height="100%"
                    language={language === 'c' ? 'c' : language === 'cpp' ? 'cpp' : language === 'java' ? 'java' : 'python'}
                    theme="vs-dark"
                    value={code}
                    onChange={handleCodeChange}
                    onMount={(editor, monaco) => {
                      monacoEditorRef.current = editor;
                      monacoInstanceRef.current = monaco;

                      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
                        executeCode();
                      });

                      // Keyboard shortcut for manual IntelliSense triggering
                      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, () => {
                        editor.trigger('keyboard', 'editor.action.triggerSuggest', {});
                      });

                      if (monacoCleanupRef.current) monacoCleanupRef.current();
                      monacoCleanupRef.current = configureMonacoPasteRestriction(editor, monaco, {
                        isRestricted: isAssessmentMode,
                        pageType: 'coding',
                        questionId: currentProblem?.id,
                        attemptId: null,
                        onBlocked: () => triggerPasteWarning()
                      });

                      // Register VS Code-like Monaco IntelliSense & Auto-Completion
                      if (monacoIntelliSenseCleanupRef.current) monacoIntelliSenseCleanupRef.current();
                      monacoIntelliSenseCleanupRef.current = registerCodeAcharyaIntelliSense(monaco);
                    }}
                    options={{
                      fontSize: 14,
                      fontFamily: 'var(--font-mono)',
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                      padding: { top: 12, bottom: 12 },
                      lineNumbers: 'on',
                      bracketPairColorization: { enabled: true },
                      automaticLayout: true,
                      readOnly: isLocked || sessionState !== 'running',
                      domReadOnly: isLocked || sessionState !== 'running',
                      dropIntoEditor: { enabled: !isAssessmentMode && !isLocked },
                      quickSuggestions: { other: true, comments: false, strings: false },
                      suggestOnTriggerCharacters: true,
                      acceptSuggestionOnEnter: 'on',
                      tabCompletion: 'on',
                      parameterHints: { enabled: true, cycle: true },
                      suggest: {
                        localityBonus: true,
                        shareSuggestSelections: true,
                        showIcons: true,
                        filterGraceful: true,
                        snippetsPreventQuickSuggestions: false
                      },
                      wordBasedSuggestions: 'matchingDocuments'
                    }}
                  />

                  {/* Global Full-Screen Locked Overlay */}
                  <FullscreenLockOverlay
                    isOpen={isLocked && sessionState !== 'not_started'}
                    onRestoreResume={handleRestoreFullscreenAndResume}
                    lockReason={lockReason}
                    errorMessage={lockErrorMessage}
                    isResuming={isResuming}
                    savedCode={code}
                  />
                </div>
              </div>
            </div>
          )}

          {/* COMPLETED RESULTS SUMMARY CARD & MODAL (Section 6 Requirements) */}
          {sessionState === 'completed' && completedSummary && (
            <div className="glass-panel-elevated animate-slide-down" style={{
              padding: '20px 24px',
              border: '1px solid rgba(16, 185, 129, 0.6)',
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(15, 23, 42, 0.85))',
              borderRadius: 12,
              boxShadow: '0 15px 35px rgba(16, 185, 129, 0.2)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14, marginBottom: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 44,
                    height: 44,
                    borderRadius: 10,
                    background: 'rgba(16, 185, 129, 0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 0 15px rgba(16, 185, 129, 0.4)'
                  }}>
                    <Award size={24} color="#10b981" />
                  </div>
                  <div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-heading)' }}>
                      Problem Solved! 100% Test Cases Passed
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {completedSummary.title} • {completedSummary.timestamp}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <button 
                    onClick={onLaunchViva}
                    className="btn btn-purple glow-primary"
                    style={{ padding: '8px 20px', fontSize: '0.875rem' }}
                  >
                    <GraduationCap size={16} />
                    <span>Launch AI Viva Exam</span>
                  </button>

                  <button
                    onClick={handleStartNewAttempt}
                    className="btn btn-secondary"
                    style={{ padding: '8px 14px', fontSize: '0.825rem' }}
                  >
                    <RotateCcw size={14} /> Practice Again
                  </button>
                </div>
              </div>

              {/* Performance Result Metrics Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                gap: 12,
                padding: '12px 14px',
                background: 'rgba(15, 23, 42, 0.75)',
                borderRadius: 8,
                border: '1px solid var(--border-glass)'
              }}>
                <div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Solving Duration</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                    ⏱️ {completedSummary.finalDurationFormatted}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Test Results</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
                    {completedSummary.passedCount} / {completedSummary.totalCount} Passed (100%)
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Execution Runtime</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#60a5fa' }}>
                    {completedSummary.runtimeMs} ms
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Language</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#c084fc' }}>
                    {completedSummary.language.toUpperCase()}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Tab Switches</div>
                  <div style={{ 
                    fontSize: '1.05rem', 
                    fontWeight: 700, 
                    color: (completedSummary.tabSwitches || 0) > 0 ? '#f59e0b' : '#34d399', 
                    fontFamily: 'var(--font-mono)' 
                  }}>
                    {completedSummary.tabSwitches || 0}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Time Away</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                    {completedSummary.totalTimeAwayFormatted || '00:00:00'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Bottom Inspection & Results Panel */}
          <div 
            ref={bottomPanelRef} 
            id="workspace-results-panel" 
            className="glass-panel" 
            style={{ padding: 18, scrollMarginTop: 85 }}
          >
            {/* Tabs Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-glass)', marginBottom: 14 }}>
              <div style={{ display: 'flex', gap: 4 }}>
                <button 
                  className={`tab-btn ${activeBottomTab === 'tests' ? 'active' : ''}`}
                  onClick={() => setActiveBottomTab('tests')}
                >
                  <Terminal size={15} />
                  <span>Test Cases {execResult ? `(${execResult.passed_count}/${execResult.total_count})` : ''}</span>
                </button>

                <button 
                  className={`tab-btn ${activeBottomTab === 'ast' ? 'active' : ''}`}
                  onClick={() => setActiveBottomTab('ast')}
                >
                  <Cpu size={15} />
                  <span>AST & Code Analyzer</span>
                  {execResult?.ast_feedback?.suspected_bugs?.length > 0 && (
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f43f5e' }} />
                  )}
                </button>

                <button 
                  className={`tab-btn ${activeBottomTab === 'debugger' ? 'active' : ''}`}
                  onClick={() => setActiveBottomTab('debugger')}
                >
                  <Bug size={15} />
                  <span>Guided Debugger</span>
                  {isDebugging && (
                    <span className="pulse-indicator" style={{ width: 7, height: 7, borderRadius: '50%', background: '#f59e0b', display: 'inline-block' }} />
                  )}
                </button>

                <button 
                  className={`tab-btn ${activeBottomTab === 'explanation' ? 'active' : ''}`}
                  onClick={() => setActiveBottomTab('explanation')}
                >
                  <HelpCircle size={15} />
                  <span>Execution Flow & Big-O</span>
                  {isExplaining && (
                    <span className="pulse-indicator" style={{ width: 7, height: 7, borderRadius: '50%', background: '#818cf8', display: 'inline-block' }} />
                  )}
                </button>
              </div>

              {activeBottomTab !== 'tests' && (
                <button
                  onClick={() => setActiveBottomTab('tests')}
                  className="btn btn-secondary"
                  style={{ padding: '4px 10px', fontSize: '0.75rem', gap: 4, height: 28 }}
                  title="Close view and return to Test Cases"
                >
                  <X size={13} />
                  <span>Back to Tests</span>
                </button>
              )}
            </div>

            {/* TAB CONTENT: 1. Test Cases */}
            {activeBottomTab === 'tests' && (
              <div>
                {!execResult && !isExecuting && (
                  <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    Click <strong>Run & Test</strong> to execute your code against automated test cases.
                  </div>
                )}

                {isExecuting && (
                  <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>
                    <Sparkles size={24} color="#10b981" className="pulse-indicator" style={{ marginBottom: 8 }} />
                    <p style={{ fontSize: '0.85rem' }}>Executing test cases in secure sandbox...</p>
                  </div>
                )}

                {execResult && (
                  <div>
                    {/* Execution Telemetry Status Bar & Coding Score */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px 18px',
                      background: execResult.passed_count === execResult.total_count 
                        ? 'linear-gradient(90deg, rgba(16, 185, 129, 0.18), rgba(15, 23, 42, 0.85))'
                        : 'linear-gradient(90deg, rgba(244, 63, 94, 0.18), rgba(15, 23, 42, 0.85))',
                      borderRadius: 12,
                      border: `1px solid ${execResult.passed_count === execResult.total_count ? 'rgba(16, 185, 129, 0.45)' : 'rgba(244, 63, 94, 0.45)'}`,
                      marginBottom: 14,
                      flexWrap: 'wrap',
                      gap: 12
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                        {execResult.passed_count === execResult.total_count ? (
                          <>
                            <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 10px #10b981' }}></div>
                            <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-heading)' }}>
                              Accepted
                            </span>
                          </>
                        ) : (
                          <>
                            <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f43f5e', boxShadow: '0 0 10px #f43f5e' }}></div>
                            <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#fb7185', fontFamily: 'var(--font-heading)' }}>
                              {execResult.status === 'timeout' ? 'Time Limit Exceeded' : execResult.status === 'error' ? 'Runtime / Syntax Error' : 'Tests Failed'}
                            </span>
                          </>
                        )}
                        <span style={{
                          fontSize: '0.75rem',
                          padding: '3px 10px',
                          borderRadius: 6,
                          background: 'rgba(255, 255, 255, 0.08)',
                          color: '#f8fafc',
                          fontWeight: 600,
                          fontFamily: 'var(--font-mono)'
                        }}>
                          {execResult.passed_count} / {execResult.total_count} Passed
                        </span>

                        {execResult.score_data?.is_empty_submission || execResult.score_data?.scoring_status === 'not_evaluated' ? (
                          <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6,
                            background: 'rgba(148, 163, 184, 0.15)',
                            border: '1px solid rgba(148, 163, 184, 0.35)',
                            padding: '3px 10px',
                            borderRadius: 8
                          }}>
                            <Award size={14} color="#94a3b8" />
                            <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#cbd5e1', fontFamily: 'var(--font-mono)' }}>
                              Score: Pending / Not Evaluated
                            </span>
                          </div>
                        ) : execResult.overall_score !== undefined ? (
                          <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6,
                            background: execResult.is_completed ? 'rgba(6, 182, 212, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                            border: `1px solid ${execResult.is_completed ? 'rgba(6, 182, 212, 0.35)' : 'rgba(245, 158, 11, 0.35)'}`,
                            padding: '3px 10px',
                            borderRadius: 8
                          }}>
                            <Award size={14} color={execResult.is_completed ? "#06b6d4" : "#f59e0b"} />
                            <span style={{ fontSize: '0.8rem', fontWeight: 800, color: execResult.is_completed ? '#38bdf8' : '#fbbf24', fontFamily: 'var(--font-mono)' }}>
                              Score: {execResult.overall_score} / 100 {execResult.is_completed ? '' : '(Provisional)'}
                            </span>
                          </div>
                        ) : (
                          <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 6,
                            background: 'rgba(99, 102, 241, 0.15)',
                            border: '1px solid rgba(99, 102, 241, 0.35)',
                            padding: '3px 10px',
                            borderRadius: 8
                          }}>
                            <Lightbulb size={14} color="#818cf8" />
                            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#a5b4fc' }}>
                              Independent: {calculateIndependentScore(hintsHistory.length)}/10 • Final Score: Pending Evaluation
                            </span>
                          </div>
                        )}
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: '0.75rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                          ⚡ Runtime: <strong style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{execResult.runtime_ms || 0} ms</strong> ({language})
                        </span>
                        <span>•</span>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                          ⏱️ Coding Time: <strong style={{ color: '#c084fc', fontFamily: 'var(--font-mono)' }}>{formatTime(execResult.time_spent_seconds || 0)}</strong>
                        </span>
                        {execResult.score_data && (
                          <button
                            onClick={() => setShowScoreModal(true)}
                            className="btn btn-secondary"
                            style={{ padding: '4px 10px', fontSize: '0.75rem', gap: 5, borderRadius: 6 }}
                          >
                            <Award size={13} color="#38bdf8" />
                            <span>Score Breakdown</span>
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Coding Score Breakdown Summary Strip (5 Dimensions) */}
                    {execResult.score_data && (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.7)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: 10,
                        padding: '12px 16px',
                        marginBottom: 14,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: 12
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', fontSize: '0.785rem' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Dimensions:</span>
                          <span style={{ color: '#34d399', fontWeight: 600 }}>
                            Correctness: {execResult.score_data.breakdown?.correctness?.points_earned || 0}/{execResult.score_data.breakdown?.correctness?.max_points || 40}
                          </span>
                          <span>•</span>
                          <span style={{ color: '#38bdf8', fontWeight: 600 }}>
                            Complexity: {execResult.score_data.breakdown?.complexity?.is_available ? `${execResult.score_data.breakdown.complexity.points_earned}/${execResult.score_data.breakdown.complexity.max_points}` : 'N/A'}
                          </span>
                          <span>•</span>
                          <span style={{ color: '#818cf8', fontWeight: 600 }}>
                            Quality: {execResult.score_data.breakdown?.quality?.is_available ? `${execResult.score_data.breakdown.quality.points_earned || 0}/${execResult.score_data.breakdown.quality.max_points || 15}` : '0/15'}
                          </span>
                          <span>•</span>
                          <span style={{ color: '#c084fc', fontWeight: 600 }}>
                            Approach: {execResult.score_data.breakdown?.approach?.is_available ? `${execResult.score_data.breakdown.approach.points_earned || 0}/${execResult.score_data.breakdown.approach.max_points || 15}` : '0/15'}
                          </span>
                          <span>•</span>
                          <span style={{ color: '#fbbf24', fontWeight: 600 }}>
                            Independent (Hints): {execResult.score_data?.is_empty_submission ? '0/10 (Pending Code)' : `${execResult.score_data.breakdown?.independent?.points_earned ?? calculateIndependentScore(hintsHistory.length)}/10`}
                          </span>
                        </div>

                        {execResult.score_data.complexity_analysis && (
                          <div style={{
                            fontSize: '0.75rem',
                            color: '#94a3b8',
                            fontFamily: 'var(--font-mono)',
                            background: 'rgba(255, 255, 255, 0.04)',
                            padding: '3px 8px',
                            borderRadius: 6
                          }}>
                            Big-O: {execResult.score_data.complexity_analysis?.complexity_status === 'N/A' || !execResult.score_data.breakdown?.complexity?.is_available ? 'N/A' : (execResult.score_data.complexity_analysis?.estimated_time_complexity || 'O(N)')} (Expected: {execResult.score_data.complexity_analysis?.expected_time_complexity || 'O(N)'})
                          </div>
                        )}
                      </div>
                    )}

                    {execResult.stderr && (
                      <div style={{
                        background: 'rgba(244, 63, 94, 0.1)',
                        border: '1px solid rgba(244, 63, 94, 0.3)',
                        borderRadius: 8,
                        padding: 12,
                        marginBottom: 14,
                        fontSize: '0.825rem',
                        color: '#fb7185',
                        fontFamily: 'var(--font-mono)',
                        whiteSpace: 'pre-wrap'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600, marginBottom: 4 }}>
                          <AlertOctagon size={16} /> Error Output:
                        </div>
                        {execResult.stderr}
                      </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 10 }}>
                      {execResult.results.map(r => (
                        <div 
                          key={r.test_id}
                          style={{
                            background: r.passed ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)',
                            border: `1px solid ${r.passed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
                            borderRadius: 8,
                            padding: 12,
                            fontSize: '0.8rem'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ fontWeight: 600, color: r.passed ? '#34d399' : '#fb7185', display: 'flex', alignItems: 'center', gap: 6 }}>
                              {r.passed ? <CheckCircle2 size={15} /> : <XCircle size={15} />}
                              Test Case #{r.test_id}
                            </span>
                            <span style={{ fontSize: '0.725rem', color: 'var(--text-subtle)' }}>
                              {r.execution_time_ms}ms
                            </span>
                          </div>

                          <div style={{ marginBottom: 4 }}>
                            <span style={{ color: 'var(--text-muted)' }}>Input: </span>
                            <code>{r.input}</code>
                          </div>
                          <div style={{ marginBottom: 4 }}>
                            <span style={{ color: 'var(--text-muted)' }}>Expected: </span>
                            <code style={{ color: '#34d399' }}>{r.expected}</code>
                          </div>
                          <div>
                            <span style={{ color: 'var(--text-muted)' }}>Actual: </span>
                            <code style={{ color: r.passed ? '#34d399' : '#fb7185' }}>{r.actual}</code>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB CONTENT: 2. AST & Static Analysis */}
            {activeBottomTab === 'ast' && (
              <div>
                {execResult?.ast_feedback ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {/* Suspected Bugs / Base Case warnings */}
                    {execResult.ast_feedback.suspected_bugs?.length > 0 && (
                      <div style={{
                        background: 'rgba(244, 63, 94, 0.12)',
                        border: '1px solid rgba(244, 63, 94, 0.4)',
                        padding: 14,
                        borderRadius: 8
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#fb7185', fontWeight: 600, fontSize: '0.85rem', marginBottom: 6 }}>
                          <AlertOctagon size={16} /> AST Detected Structural Bug:
                        </div>
                        <ul style={{ margin: 0, paddingLeft: 18, color: '#fecdd3', fontSize: '0.825rem' }}>
                          {execResult.ast_feedback.suspected_bugs.map((b, i) => (
                            <li key={i}>{b}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Metadata Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Recursion Detected</div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: execResult.ast_feedback.has_recursion ? '#818cf8' : '#94a3b8' }}>
                          {execResult.ast_feedback.has_recursion ? 'Yes (Recursive Call Active)' : 'No (Iterative)'}
                        </div>
                      </div>

                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Base Case Present</div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: execResult.ast_feedback.has_base_case ? '#34d399' : '#f59e0b' }}>
                          {execResult.ast_feedback.has_base_case ? 'Verified (Conditional Found)' : 'Missing Base Case'}
                        </div>
                      </div>

                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Loop Nesting Depth</div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#06b6d4' }}>
                          Depth: {execResult.ast_feedback.loop_depth} ({execResult.ast_feedback.estimated_complexity})
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Run Python code to inspect real-time AST syntax structure, recursion base cases, and loop nesting bounds.
                  </div>
                )}
              </div>
            )}

            {/* TAB CONTENT: 3. Guided Debugger */}
            {activeBottomTab === 'debugger' && (
              <div>
                {/* 1. Loading State */}
                {isDebugging && (
                  <div style={{ padding: 32, textAlign: 'center', color: '#cbd5e1' }}>
                    <Sparkles size={26} color="#f59e0b" className="pulse-indicator" style={{ marginBottom: 12 }} />
                    <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f59e0b', marginBottom: 4 }}>
                      AI Debugger Analyzing Solution...
                    </div>
                    <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: 0 }}>
                      Evaluating runtime traces, base conditions, recursion bounds, and edge constraints...
                    </p>
                  </div>
                )}

                {/* 2. Error State */}
                {!isDebugging && debugError && (
                  <div style={{
                    background: 'rgba(244, 63, 94, 0.1)',
                    border: '1px solid rgba(244, 63, 94, 0.3)',
                    borderRadius: 8,
                    padding: 16
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#fb7185', fontWeight: 600, fontSize: '0.875rem', marginBottom: 6 }}>
                      <AlertOctagon size={16} /> Debugger Request Failed
                    </div>
                    <p style={{ fontSize: '0.825rem', color: '#fecdd3', marginBottom: 14 }}>{debugError}</p>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button onClick={launchDebugger} className="btn btn-secondary" style={{ padding: '5px 14px', fontSize: '0.8rem', gap: 4 }}>
                        <RefreshCw size={13} /> Retry Analysis
                      </button>
                      <button onClick={() => setActiveBottomTab('tests')} className="btn btn-secondary" style={{ padding: '5px 14px', fontSize: '0.8rem' }}>
                        Back to Test Cases
                      </button>
                    </div>
                  </div>
                )}

                {/* 3. Debug Guide Content */}
                {!isDebugging && !debugError && debugGuide && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {/* Status Badge & Primary Symptom */}
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Bug size={18} color={debugGuide.status === 'clean' ? '#10b981' : debugGuide.status === 'verified_runtime_error' ? '#f43f5e' : '#f59e0b'} />
                        <span style={{ fontSize: '0.95rem', fontWeight: 700, color: debugGuide.status === 'clean' ? '#34d399' : debugGuide.status === 'verified_runtime_error' ? '#fb7185' : '#fbbf24' }}>
                          {debugGuide.primary_symptom}
                        </span>
                      </div>

                      <div>
                        {debugGuide.status === 'verified_runtime_error' && (
                          <span style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.4)', color: '#fb7185', fontSize: '0.725rem', fontWeight: 700, padding: '3px 8px', borderRadius: 12 }}>
                            Verified Runtime Error
                          </span>
                        )}
                        {debugGuide.status === 'suspected_static_issue' && (
                          <span style={{ background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.4)', color: '#fbbf24', fontSize: '0.725rem', fontWeight: 700, padding: '3px 8px', borderRadius: 12 }}>
                            Static Code Analysis
                          </span>
                        )}
                        {debugGuide.status === 'clean' && (
                          <span style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#34d399', fontSize: '0.725rem', fontWeight: 700, padding: '3px 8px', borderRadius: 12 }}>
                            Clean Solution — No Issues Found
                          </span>
                        )}
                        {debugGuide.status === 'empty_code' && (
                          <span style={{ background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#93c5fd', fontSize: '0.725rem', fontWeight: 700, padding: '3px 8px', borderRadius: 12 }}>
                            Editor Empty
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Bug Summary */}
                    {debugGuide.bug_summary && debugGuide.bug_summary !== debugGuide.primary_symptom && (
                      <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5, margin: 0 }}>
                        {debugGuide.bug_summary}
                      </p>
                    )}

                    {/* Relevant Code Section */}
                    {debugGuide.relevant_section && (
                      <div style={{
                        background: 'rgba(2, 6, 23, 0.75)',
                        border: '1px solid rgba(244, 63, 94, 0.3)',
                        borderRadius: 6,
                        padding: '8px 12px',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.8rem',
                        color: '#fecdd3'
                      }}>
                        <span style={{ color: '#fb7185', fontWeight: 600, marginRight: 8 }}>Problematic Section:</span>
                        <code>{debugGuide.relevant_section}</code>
                      </div>
                    )}

                    {/* Socratic Prompt */}
                    {debugGuide.socratic_prompt && (
                      <div style={{
                        fontStyle: 'italic',
                        fontSize: '0.85rem',
                        color: '#93c5fd',
                        background: 'rgba(59, 130, 246, 0.08)',
                        border: '1px solid rgba(59, 130, 246, 0.25)',
                        padding: '10px 14px',
                        borderRadius: 6
                      }}>
                        "{debugGuide.socratic_prompt}"
                      </div>
                    )}

                    {/* Why This Occurs */}
                    {debugGuide.why_it_occurs && (
                      <div style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        borderLeft: '3px solid #f59e0b',
                        padding: '10px 14px',
                        borderRadius: '0 6px 6px 0'
                      }}>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#f59e0b', fontWeight: 700, marginBottom: 4 }}>
                          Why This Issue Occurs
                        </div>
                        <div style={{ fontSize: '0.825rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                          {debugGuide.why_it_occurs}
                        </div>
                      </div>
                    )}

                    {/* Step-by-Step Debugging Steps */}
                    {debugGuide.investigation_steps?.length > 0 && (
                      <div>
                        <h4 style={{ fontSize: '0.775rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                          Step-by-Step Investigation Approach
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          {debugGuide.investigation_steps.map((step, idx) => (
                            <div key={idx} style={{
                              background: 'rgba(15, 23, 42, 0.6)',
                              borderLeft: '3px solid #6366f1',
                              padding: '8px 12px',
                              borderRadius: 6,
                              fontSize: '0.825rem',
                              color: '#e2e8f0'
                            }}>
                              {step}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Suggested Correction */}
                    {debugGuide.suggested_correction && (
                      <div style={{
                        background: 'rgba(16, 185, 129, 0.08)',
                        border: '1px solid rgba(16, 185, 129, 0.25)',
                        padding: '10px 14px',
                        borderRadius: 6
                      }}>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#34d399', fontWeight: 700, marginBottom: 4 }}>
                          Suggested Correction
                        </div>
                        <div style={{ fontSize: '0.825rem', color: '#d1fae5', lineHeight: 1.5 }}>
                          {debugGuide.suggested_correction}
                        </div>
                      </div>
                    )}

                    {/* Edge Cases to Check */}
                    {debugGuide.edge_cases_to_check?.length > 0 && (
                      <div>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 6 }}>
                          Edge Cases to Verify
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                          {debugGuide.edge_cases_to_check.map((ec, idx) => (
                            <span key={idx} style={{
                              background: 'rgba(255, 255, 255, 0.04)',
                              border: '1px solid var(--border-glass)',
                              borderRadius: 12,
                              padding: '3px 10px',
                              fontSize: '0.75rem',
                              color: '#cbd5e1'
                            }}>
                              {ec}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Action Bar */}
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 6, paddingTop: 10, borderTop: '1px solid var(--border-glass)' }}>
                      <button
                        onClick={launchDebugger}
                        className="btn btn-secondary"
                        style={{ padding: '5px 12px', fontSize: '0.8rem', gap: 4 }}
                      >
                        <RefreshCw size={13} /> Re-analyze
                      </button>
                      <button
                        onClick={() => setActiveBottomTab('tests')}
                        className="btn btn-secondary"
                        style={{ padding: '5px 14px', fontSize: '0.8rem' }}
                      >
                        Back to Test Cases
                      </button>
                    </div>
                  </div>
                )}

                {/* 4. Default Empty Prompt */}
                {!isDebugging && !debugError && !debugGuide && (
                  <div style={{ padding: 28, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Click <strong>Debug Guide</strong> on the toolbar above for guided troubleshooting steps that teach you how to spot and fix issues.
                  </div>
                )}
              </div>
            )}

            {/* TAB CONTENT: 4. Code Explanation */}
            {activeBottomTab === 'explanation' && (
              <div>
                {/* 1. Loading State */}
                {isExplaining && (
                  <div style={{ padding: 32, textAlign: 'center', color: '#cbd5e1' }}>
                    <Sparkles size={26} color="#818cf8" className="pulse-indicator" style={{ marginBottom: 12 }} />
                    <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#818cf8', marginBottom: 4 }}>
                      Analyzing Code Logic & Asymptotics...
                    </div>
                    <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', margin: 0 }}>
                      Evaluating step-by-step execution flow, loops, data structures, and Big-O complexity...
                    </p>
                  </div>
                )}

                {/* 2. Error State */}
                {!isExplaining && explainError && (
                  <div style={{
                    background: 'rgba(244, 63, 94, 0.1)',
                    border: '1px solid rgba(244, 63, 94, 0.3)',
                    borderRadius: 8,
                    padding: 16
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#fb7185', fontWeight: 600, fontSize: '0.875rem', marginBottom: 6 }}>
                      <AlertOctagon size={16} /> Explanation Request Failed
                    </div>
                    <p style={{ fontSize: '0.825rem', color: '#fecdd3', marginBottom: 14 }}>{explainError}</p>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button onClick={explainCode} className="btn btn-secondary" style={{ padding: '5px 14px', fontSize: '0.8rem', gap: 4 }}>
                        <RefreshCw size={13} /> Retry Explanation
                      </button>
                      <button onClick={() => setActiveBottomTab('tests')} className="btn btn-secondary" style={{ padding: '5px 14px', fontSize: '0.8rem' }}>
                        Back to Test Cases
                      </button>
                    </div>
                  </div>
                )}

                {/* 3. Explanation Content */}
                {!isExplaining && !explainError && explanationData && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                    {/* Summary & Algorithmic Approach Badge */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap' }}>
                      <div style={{ fontSize: '0.9rem', color: '#f1f5f9', lineHeight: 1.5, flex: 1 }}>
                        {explanationData.summary}
                      </div>
                      {explanationData.algorithmic_approach && explanationData.algorithmic_approach !== 'N/A' && (
                        <span style={{
                          background: 'rgba(99, 102, 241, 0.15)',
                          border: '1px solid rgba(99, 102, 241, 0.4)',
                          color: '#a5b4fc',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          padding: '3px 10px',
                          borderRadius: 12
                        }}>
                          {explanationData.algorithmic_approach}
                        </span>
                      )}
                    </div>

                    {/* Complexity Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 2 }}>Time Complexity</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#818cf8', marginBottom: 4 }}>
                          {explanationData.time_complexity}
                        </div>
                        <div style={{ fontSize: '0.775rem', color: '#94a3b8', lineHeight: 1.4 }}>
                          {explanationData.time_rationale}
                        </div>
                      </div>

                      <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 2 }}>Space Complexity</div>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#06b6d4', marginBottom: 4 }}>
                          {explanationData.space_complexity}
                        </div>
                        <div style={{ fontSize: '0.775rem', color: '#94a3b8', lineHeight: 1.4 }}>
                          {explanationData.space_rationale}
                        </div>
                      </div>
                    </div>

                    {/* Key Components (Loops, Conditions, Data Structures) */}
                    {explanationData.key_components && (
                      <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border-glass)', borderRadius: 8, padding: 12 }}>
                        <h4 style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', margin: '0 0 8px 0' }}>
                          Core Components & Control Flow
                        </h4>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 8, fontSize: '0.8rem' }}>
                          {explanationData.key_components.loops && (
                            <div>
                              <span style={{ color: '#818cf8', fontWeight: 600 }}>Loops: </span>
                              <span style={{ color: '#cbd5e1' }}>{explanationData.key_components.loops}</span>
                            </div>
                          )}
                          {explanationData.key_components.conditions && (
                            <div>
                              <span style={{ color: '#34d399', fontWeight: 600 }}>Conditions: </span>
                              <span style={{ color: '#cbd5e1' }}>{explanationData.key_components.conditions}</span>
                            </div>
                          )}
                          {explanationData.key_components.data_structures && (
                            <div>
                              <span style={{ color: '#06b6d4', fontWeight: 600 }}>Data Structures: </span>
                              <span style={{ color: '#cbd5e1' }}>{explanationData.key_components.data_structures}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Step-by-Step Execution Flow */}
                    {explanationData.execution_flow?.length > 0 && (
                      <div>
                        <h4 style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>
                          Step-by-Step Logic Walkthrough
                        </h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          {explanationData.execution_flow.map((f, i) => (
                            <div key={i} style={{
                              background: 'rgba(255, 255, 255, 0.02)',
                              borderLeft: '3px solid #818cf8',
                              padding: '8px 12px',
                              borderRadius: '0 6px 6px 0',
                              fontSize: '0.825rem',
                              color: '#cbd5e1'
                            }}>
                              {f}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Potential Edge Cases & Limitations */}
                    {explanationData.edge_cases_and_limitations?.length > 0 && (
                      <div>
                        <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: 6 }}>
                          Potential Edge Cases & Limitations
                        </div>
                        <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.8rem', color: '#cbd5e1' }}>
                          {explanationData.edge_cases_and_limitations.map((lim, i) => (
                            <li key={i} style={{ marginBottom: 4 }}>{lim}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action Bar */}
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 6, paddingTop: 10, borderTop: '1px solid var(--border-glass)' }}>
                      <button
                        onClick={explainCode}
                        className="btn btn-secondary"
                        style={{ padding: '5px 12px', fontSize: '0.8rem', gap: 4 }}
                      >
                        <RefreshCw size={13} /> Refresh Explanation
                      </button>
                      <button
                        onClick={() => setActiveBottomTab('tests')}
                        className="btn btn-secondary"
                        style={{ padding: '5px 14px', fontSize: '0.8rem' }}
                      >
                        Back to Test Cases
                      </button>
                    </div>
                  </div>
                )}

                {/* 4. Default Empty Prompt */}
                {!isExplaining && !explainError && !explanationData && (
                  <div style={{ padding: 28, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Click <strong>Explain Code</strong> on the toolbar above for beginner-friendly execution flow, Big-O proofs, and algorithmic breakdowns.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      </div>
      )}

      {/* Progressive Hint Modal */}
      <ProgressiveHintModal 
        isOpen={isHintOpen}
        onClose={() => setIsHintOpen(false)}
        hintsHistory={hintsHistory}
        currentLevel={hintLevel}
        onUnlockNextLevel={unlockNextHint}
        isLoading={isLoadingHint}
        problemTitle={currentProblem?.title}
      />

      {/* Topics & Difficulty Matrix Modal */}
      {isCurriculumModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.78)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: 20
        }}>
          <div className="glass-panel-elevated animate-slide-down" style={{
            maxWidth: 1200,
            width: '100%',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 16,
            border: '1px solid var(--border-glass)',
            boxShadow: '0 25px 60px rgba(0,0,0,0.7)',
            overflow: 'hidden'
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '18px 24px',
              borderBottom: '1px solid var(--border-glass)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'rgba(15, 23, 42, 0.9)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{
                  width: 38,
                  height: 38,
                  borderRadius: 10,
                  background: 'linear-gradient(135deg, #8b5cf6, #ec4899)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 15px rgba(139, 92, 246, 0.4)'
                }}>
                  <BookOpen size={20} color="#fff" />
                </div>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
                    Complete Curriculum & Categories Matrix
                  </h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                    Browse all 8 core DSA topics with Easy, Medium & Hard problem categories • Active Language: {language.toUpperCase()}
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                {/* Modal Language Selector */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: 'rgba(15, 23, 42, 0.7)',
                  borderRadius: 8,
                  padding: 2,
                  border: '1px solid var(--border-glass)'
                }}>
                  {['python', 'c', 'cpp', 'java'].map(langKey => (
                    <button
                      key={langKey}
                      onClick={() => handleLanguageChange(langKey)}
                      disabled={isLocked}
                      style={{
                        padding: '4px 8px',
                        borderRadius: 6,
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        border: 'none',
                        cursor: isLocked ? 'not-allowed' : 'pointer',
                        opacity: isLocked ? 0.6 : 1,
                        background: language === langKey ? 'linear-gradient(135deg, #6366f1, #8b5cf6)' : 'transparent',
                        color: language === langKey ? '#fff' : 'var(--text-muted)',
                        transition: 'all 0.2s'
                      }}
                      title={isLocked ? 'Editor locked: Full-screen mode required' : `Code in ${langKey}`}
                    >
                      {langKey === 'python' ? '🐍 Python' : langKey === 'c' ? '🔷 C' : langKey === 'cpp' ? '⚙️ C++' : '☕ Java'}
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => setIsCurriculumModalOpen(false)}
                  className="btn btn-secondary"
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  ✕ Close
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div style={{ padding: 24, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 20 }}>
              {TOPICS.filter(t => t.id !== 'All').map(topic => {
                const Icon = topic.icon;
                const topicProbs = problems.filter(p => p.topic === topic.id);
                const easyP = topicProbs.filter(p => p.difficulty === 'Easy');
                const medP = topicProbs.filter(p => p.difficulty === 'Medium');
                const hardP = topicProbs.filter(p => p.difficulty === 'Hard');

                return (
                  <div key={topic.id} className="glass-panel" style={{ padding: 18, borderRadius: 12 }}>
                    {/* Topic Row Title */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <Icon size={18} color="#818cf8" />
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0 }}>{topic.name}</h4>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          ({topicProbs.length} problems)
                        </span>
                      </div>

                      <button
                        onClick={() => {
                          setSelectedTopic(topic.id);
                          setIsCurriculumModalOpen(false);
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '3px 10px', fontSize: '0.7rem' }}
                      >
                        Filter to This Topic →
                      </button>
                    </div>

                    {/* 3 Categories: Easy, Medium, Hard */}
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                      gap: 12
                    }}>
                      {/* Easy Column */}
                      <div style={{ background: 'rgba(16, 185, 129, 0.05)', borderRadius: 8, padding: 10, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#34d399' }}>🟢 Easy ({easyP.length})</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          {easyP.map(p => {
                            const isSelected = p.id === currentProblem?.id;
                            const solved = isProblemSolved(p.id);
                            return (
                              <div
                                key={p.id}
                                onClick={() => {
                                  handleProblemCardClick(p.id);
                                  setSelectedTopic(topic.id);
                                  setIsCurriculumModalOpen(false);
                                }}
                                style={{
                                  padding: '6px 10px',
                                  borderRadius: 6,
                                  background: isSelected ? 'rgba(99, 102, 241, 0.3)' : 'rgba(15, 23, 42, 0.8)',
                                  border: isSelected ? '1px solid #6366f1' : '1px solid var(--border-glass)',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  fontSize: '0.775rem'
                                }}
                              >
                                <span style={{ fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9' }}>{p.title}</span>
                                {solved && <Check size={13} color="#10b981" />}
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Medium Column */}
                      <div style={{ background: 'rgba(245, 158, 11, 0.05)', borderRadius: 8, padding: 10, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fbbf24' }}>🟡 Medium ({medP.length})</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          {medP.map(p => {
                            const isSelected = p.id === currentProblem?.id;
                            const solved = isProblemSolved(p.id);
                            return (
                              <div
                                key={p.id}
                                onClick={() => {
                                  handleProblemCardClick(p.id);
                                  setSelectedTopic(topic.id);
                                  setIsCurriculumModalOpen(false);
                                }}
                                style={{
                                  padding: '6px 10px',
                                  borderRadius: 6,
                                  background: isSelected ? 'rgba(99, 102, 241, 0.3)' : 'rgba(15, 23, 42, 0.8)',
                                  border: isSelected ? '1px solid #6366f1' : '1px solid var(--border-glass)',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  fontSize: '0.775rem'
                                }}
                              >
                                <span style={{ fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9' }}>{p.title}</span>
                                {solved && <Check size={13} color="#10b981" />}
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Hard Column */}
                      <div style={{ background: 'rgba(244, 63, 94, 0.05)', borderRadius: 8, padding: 10, border: '1px solid rgba(244, 63, 94, 0.2)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fb7185' }}>🔴 Hard ({hardP.length})</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          {hardP.map(p => {
                            const isSelected = p.id === currentProblem?.id;
                            const solved = isProblemSolved(p.id);
                            return (
                              <div
                                key={p.id}
                                onClick={() => {
                                  handleProblemCardClick(p.id);
                                  setSelectedTopic(topic.id);
                                  setIsCurriculumModalOpen(false);
                                }}
                                style={{
                                  padding: '6px 10px',
                                  borderRadius: 6,
                                  background: isSelected ? 'rgba(99, 102, 241, 0.3)' : 'rgba(15, 23, 42, 0.8)',
                                  border: isSelected ? '1px solid #6366f1' : '1px solid var(--border-glass)',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  fontSize: '0.775rem'
                                }}
                              >
                                <span style={{ fontWeight: 600, color: isSelected ? '#a5b4fc' : '#f1f5f9' }}>{p.title}</span>
                                {solved && <Check size={13} color="#10b981" />}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Abandon Practice Session Confirmation Modal (Section 5 Requirements) */}
      {isAbandonModalOpen && (
        <div 
          role="dialog"
          aria-modal="true"
          aria-labelledby="abandon-modal-title"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.78)',
            backdropFilter: 'blur(6px)',
            zIndex: 10000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 20
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setIsAbandonModalOpen(false);
              setPendingNavigationAction(null);
            }
          }}
        >
          <div 
            className="glass-panel-elevated animate-scale-up"
            style={{
              maxWidth: 480,
              width: '100%',
              borderRadius: 14,
              border: '1px solid rgba(244, 63, 94, 0.45)',
              background: 'linear-gradient(145deg, rgba(15, 23, 42, 0.98), rgba(30, 20, 35, 0.95))',
              boxShadow: '0 20px 45px rgba(0, 0, 0, 0.75)',
              padding: '24px 28px',
              position: 'relative'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <div style={{
                width: 44,
                height: 44,
                borderRadius: '50%',
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <AlertTriangle size={22} color="#fb7185" />
              </div>
              <div>
                <h3 id="abandon-modal-title" style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', fontFamily: 'var(--font-heading)' }}>
                  Abandon Practice Session?
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Current elapsed time: <strong style={{ color: '#fb7185' }}>{formatTime(elapsedSeconds)}</strong>
                </span>
              </div>
            </div>

            <p style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: 22 }}>
              Are you sure you want to abandon this practice session? Abandoning will stop your timer and record this attempt as <strong>Abandoned</strong> with your elapsed duration. Your code remains saved so you can resume or start a new attempt anytime.
            </p>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
              <button
                type="button"
                onClick={() => {
                  setIsAbandonModalOpen(false);
                  setPendingNavigationAction(null);
                }}
                className="btn btn-secondary"
                style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              >
                Keep Coding
              </button>

              <button
                type="button"
                id="btn-confirm-abandon"
                onClick={handleConfirmAbandon}
                className="btn"
                style={{
                  padding: '8px 18px',
                  fontSize: '0.85rem',
                  background: 'linear-gradient(135deg, #e11d48, #be123c)',
                  color: '#ffffff',
                  fontWeight: 600,
                  border: '1px solid rgba(244, 63, 94, 0.5)',
                  boxShadow: '0 4px 15px rgba(225, 29, 72, 0.35)',
                  cursor: 'pointer'
                }}
              >
                Confirm Abandon
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab Switch Activity History Modal */}
      {isTabHistoryModalOpen && (
        <div 
          id="tab-history-modal-backdrop"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(3, 7, 18, 0.78)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1050,
            padding: 16
          }}
          onClick={() => setIsTabHistoryModalOpen(false)}
        >
          <div 
            id="tab-history-modal"
            className="glass-panel"
            style={{
              width: '100%',
              maxWidth: 680,
              maxHeight: '85vh',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 14,
              background: 'rgba(15, 23, 42, 0.96)',
              border: '1px solid var(--border-glass)',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.55)',
              overflow: 'hidden'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{
              padding: '16px 20px',
              borderBottom: '1px solid var(--border-glass)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 34,
                  height: 34,
                  borderRadius: 8,
                  background: 'rgba(245, 158, 11, 0.15)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#f59e0b'
                }}>
                  <EyeOff size={18} />
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: '#f8fafc' }}>
                    Tab Switch Activity History
                  </h3>
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Indian Standard Time (Asia/Kolkata) • Preserved across code resets
                  </p>
                </div>
              </div>
              <button 
                id="btn-close-tab-history"
                onClick={() => setIsTabHistoryModalOpen(false)}
                className="btn btn-secondary"
                style={{ padding: 6, borderRadius: 6, height: 28, width: 28, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                title="Close"
              >
                <X size={15} />
              </button>
            </div>

            {/* Modal Stats Bar */}
            <div style={{
              padding: '12px 20px',
              background: 'rgba(30, 41, 59, 0.4)',
              borderBottom: '1px solid var(--border-glass)',
              display: 'flex',
              gap: 24
            }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Total Switches</div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: tabSwitches > 0 ? '#f59e0b' : '#34d399', fontFamily: 'var(--font-mono)' }}>
                  {tabSwitches}
                </div>
              </div>
              <div style={{ width: 1, background: 'rgba(148, 163, 184, 0.2)' }} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Total Time Away</div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                  {formatDuration(Math.floor(totalTimeAwayMs / 1000))}
                </div>
              </div>
              <div style={{ width: 1, background: 'rgba(148, 163, 184, 0.2)' }} />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Last Switch</div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#f8fafc', fontFamily: 'var(--font-mono)' }}>
                  {lastSwitchTime || '--'}
                </div>
              </div>
            </div>

            {/* Events Table */}
            <div style={{ padding: '16px 20px', overflowY: 'auto', flex: 1 }}>
              {tabSwitchHistory.length === 0 ? (
                <div style={{
                  padding: '36px 20px',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                  fontSize: '0.85rem'
                }}>
                  <EyeOff size={32} style={{ opacity: 0.35, marginBottom: 8 }} />
                  <div style={{ fontWeight: 600, color: '#cbd5e1' }}>No tab switches recorded in this attempt.</div>
                  <div style={{ fontSize: '0.75rem', marginTop: 4 }}>
                    When you switch away from the assessment tab during active practice, each event is logged with sequential numbers, IST timestamps, and durations.
                  </div>
                </div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    fontSize: '0.8rem',
                    color: '#f8fafc'
                  }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-glass)', color: 'var(--text-muted)', textAlign: 'left' }}>
                        <th style={{ padding: '8px 10px' }}>#</th>
                        <th style={{ padding: '8px 10px' }}>Date</th>
                        <th style={{ padding: '8px 10px' }}>Switched Away (IST)</th>
                        <th style={{ padding: '8px 10px' }}>Returned (IST)</th>
                        <th style={{ padding: '8px 10px', textAlign: 'right' }}>Duration Away</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tabSwitchHistory.map((item, idx) => (
                        <tr 
                          key={idx}
                          style={{
                            borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                            background: idx % 2 === 0 ? 'transparent' : 'rgba(255, 255, 255, 0.02)'
                          }}
                        >
                          <td style={{ padding: '8px 10px', fontWeight: 700, color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>
                            #{item.switch_number || (idx + 1)}
                          </td>
                          <td style={{ padding: '8px 10px', color: 'var(--text-muted)' }}>
                            {item.date || '--'}
                          </td>
                          <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)' }}>
                            {item.switch_timestamp_ist || '--'}
                          </td>
                          <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)' }}>
                            {item.return_timestamp_ist || '--'}
                          </td>
                          <td style={{ padding: '8px 10px', textAlign: 'right', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                            {item.duration_away_formatted || `${item.duration_away_seconds || 0}s`}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '12px 20px',
              borderTop: '1px solid var(--border-glass)',
              background: 'rgba(15, 23, 42, 0.8)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '0.75rem',
              color: 'var(--text-muted)'
            }}>
              <span>💡 <strong>Reset Code</strong> preserves this history. Only starting a new attempt will reset it.</span>
              <button
                onClick={() => setIsTabHistoryModalOpen(false)}
                className="btn btn-secondary"
                style={{ padding: '4px 14px', fontSize: '0.75rem' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Score Breakdown & Analytics Modal */}
      {showScoreModal && execResult && execResult.score_data && (
        <ScoreBreakdownModal
          scoreRecord={{
            ...execResult.score_data,
            attempt_id: execResult.attempt_id || 'recent_attempt',
            question_id: currentProblem?.id,
            question_title: currentProblem?.title,
            language: language,
            passed_count: execResult.passed_count,
            total_count: execResult.total_count,
            unique_hints_used: hintsHistory.length,
            independent_score: calculateIndependentScore(hintsHistory.length),
            execution_time_ms: execResult.runtime_ms,
            coding_time_seconds: execResult.time_spent_seconds || 0
          }}
          onClose={() => setShowScoreModal(false)}
        />
      )}

      {/* Programming Language Change Confirmation Modal */}
      <LanguageChangeModal
        isOpen={isLanguageModalOpen}
        currentLanguage={language}
        newLanguage={pendingLanguage || language}
        onCancel={handleCancelLanguageChange}
        onConfirm={handleConfirmLanguageChange}
        isConfirming={isConfirmingLanguage}
      />
    </div>
  );
}
