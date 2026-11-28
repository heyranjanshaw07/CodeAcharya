import React, { useState, useEffect, useRef, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { 
  Play, 
  Send, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  ChevronRight, 
  ChevronLeft,
  Sparkles,
  Maximize2,
  FileCode2,
  Terminal,
  ShieldAlert,
  ArrowRight,
  RotateCcw,
  Flag
} from 'lucide-react';
import { configureMonacoPasteRestriction } from '../utils/pasteRestriction';
import { registerCodeAcharyaIntelliSense, disposeCodeAcharyaIntelliSense } from '../utils/monacoIntelliSense';
import {
  isBrowserFullscreen,
  isFullscreenSupported,
  requestBrowserFullscreen,
  logSessionLockTelemetry
} from '../utils/fullscreenEnforcement';
import FullscreenLockOverlay from './FullscreenLockOverlay';

export default function AIAssessmentView({
  assessment,
  onFinishAssessment,
  isFinishing
}) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [codes, setCodes] = useState(() => {
    const initial = {};
    (assessment?.questions || []).forEach(q => {
      initial[q.id] = q.starter_code || '';
    });
    return initial;
  });

  const [questionStatuses, setQuestionStatuses] = useState(() => {
    const initial = {};
    (assessment?.questions || []).forEach(q => {
      initial[q.id] = {
        status: 'unattempted', // 'unattempted', 'attempted', 'accepted'
        passedCount: 0,
        totalCount: q.sample_test_cases?.length || 0,
        score: 0
      };
    });
    return initial;
  });

  // Active console / test output per question
  const [consoleOutputs, setConsoleOutputs] = useState({});
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Assessment timer (seconds elapsed)
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Tab switch & anti-cheating tracking
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [isFullscreenLocked, setIsFullscreenLocked] = useState(false);
  const [showFinishConfirm, setShowFinishConfirm] = useState(false);

  const editorRef = useRef(null);

  const currentQuestion = assessment?.questions?.[currentQuestionIndex] || null;
  const currentCode = currentQuestion ? (codes[currentQuestion.id] || '') : '';
  const currentConsole = currentQuestion ? (consoleOutputs[currentQuestion.id] || null) : null;
  const currentStatus = currentQuestion ? (questionStatuses[currentQuestion.id] || {}) : {};

  // Timer interval
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Format seconds to mm:ss or hh:mm:ss
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    if (m >= 60) {
      const h = Math.floor(m / 60);
      const remM = m % 60;
      return `${h}:${remM < 10 ? '0' : ''}${remM}:${s < 10 ? '0' : ''}${s}`;
    }
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  // Tab switch listener for anti-cheating audit
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setTabSwitchCount(prev => prev + 1);
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Full-screen change listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (isFullscreenSupported() && !isBrowserFullscreen()) {
        setIsFullscreenLocked(true);
      } else {
        setIsFullscreenLocked(false);
      }
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Monaco Editor Mount
  const handleEditorMount = (editor, monaco) => {
    editorRef.current = editor;
    if (editor && monaco) {
      try {
        configureMonacoPasteRestriction(editor, monaco, {
          isRestricted: true,
          pageType: 'assessment',
          questionId: currentQuestion?.id,
          attemptId: assessment?.assessment_id
        });
        registerCodeAcharyaIntelliSense(monaco);
      } catch (err) {
        console.warn('[Monaco Mount Notice]:', err);
      }
    }
  };

  const handleCodeChange = (newCode) => {
    if (!currentQuestion) return;
    setCodes(prev => ({
      ...prev,
      [currentQuestion.id]: newCode || ''
    }));
  };

  // Run Code against Sample / Public Test Cases
  const handleRunCode = async () => {
    if (!currentQuestion || isRunning || isSubmitting) return;
    setIsRunning(true);
    setErrorMessage('');

    try {
      const res = await fetch('/api/ai-mode/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assessment_id: assessment.assessment_id,
          question_id: currentQuestion.id,
          code: currentCode,
          language: assessment.language
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Execution failed');
      }

      const data = await res.json();
      setConsoleOutputs(prev => ({
        ...prev,
        [currentQuestion.id]: {
          type: 'run',
          data
        }
      }));
    } catch (err) {
      setErrorMessage(err.message || 'Execution error');
    } finally {
      setIsRunning(false);
    }
  };

  // Submit Solution against ALL test cases (Hidden Test Cases in Backend Sandbox)
  const handleSubmitQuestion = async () => {
    if (!currentQuestion || isRunning || isSubmitting) return;
    setIsSubmitting(true);
    setErrorMessage('');

    try {
      const res = await fetch('/api/ai-mode/submit-question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assessment_id: assessment.assessment_id,
          question_id: currentQuestion.id,
          code: currentCode,
          language: assessment.language,
          time_spent_seconds: elapsedSeconds,
          tab_switch_count: tabSwitchCount
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Submission failed');
      }

      const data = await res.json();
      setConsoleOutputs(prev => ({
        ...prev,
        [currentQuestion.id]: {
          type: 'submit',
          data
        }
      }));

      // Update Question Status Pill
      const isAccepted = data.status === 'Accepted';
      setQuestionStatuses(prev => ({
        ...prev,
        [currentQuestion.id]: {
          status: isAccepted ? 'accepted' : 'attempted',
          passedCount: data.passed_count,
          totalCount: data.total_count,
          score: data.score
        }
      }));
    } catch (err) {
      setErrorMessage(err.message || 'Submission error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFinishConfirm = () => {
    setShowFinishConfirm(false);
    onFinishAssessment({
      assessment_id: assessment.assessment_id,
      total_time_seconds: elapsedSeconds,
      tab_switch_count: tabSwitchCount
    });
  };

  // Monaco Language Mapping
  const monacoLang = assessment?.language === 'python' ? 'python' :
                     assessment?.language === 'c' ? 'c' :
                     assessment?.language === 'cpp' ? 'cpp' : 'java';

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 72px)',
      background: 'var(--bg-primary)',
      color: '#f8fafc',
      overflow: 'hidden'
    }}>
      {/* Top Assessment Control Bar */}
      <div style={{
        padding: '10px 20px',
        background: 'rgba(15, 23, 42, 0.95)',
        borderBottom: '1px solid var(--border-glass)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 12,
        zIndex: 20
      }}>
        {/* Left: Mode Title & Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            borderRadius: 8,
            padding: '4px 10px',
            fontSize: '0.8rem',
            fontWeight: 700,
            color: '#a5b4fc'
          }}>
            <Sparkles size={14} />
            <span>AI Assessment Mode</span>
          </div>

          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#e2e8f0' }}>
            {assessment.topic}
          </span>

          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            padding: '2px 8px',
            borderRadius: 6,
            background: assessment.difficulty === 'Easy' ? 'rgba(16, 185, 129, 0.2)' :
                        assessment.difficulty === 'Medium' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
            color: assessment.difficulty === 'Easy' ? '#34d399' :
                   assessment.difficulty === 'Medium' ? '#fbbf24' : '#f87171'
          }}>
            {assessment.difficulty}
          </span>

          <span style={{
            fontSize: '0.72rem',
            fontWeight: 600,
            padding: '2px 8px',
            borderRadius: 6,
            background: 'rgba(59, 130, 246, 0.2)',
            color: '#60a5fa'
          }}>
            {assessment.language.toUpperCase()}
          </span>
        </div>

        {/* Center: Question Navigation Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {(assessment?.questions || []).map((q, idx) => {
            const isCurrent = idx === currentQuestionIndex;
            const qStat = questionStatuses[q.id]?.status || 'unattempted';
            const isAccepted = qStat === 'accepted';
            const isAttempted = qStat === 'attempted';

            return (
              <button
                type="button"
                key={q.id}
                onClick={() => setCurrentQuestionIndex(idx)}
                style={{
                  padding: '6px 14px',
                  borderRadius: 8,
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  border: isCurrent ? '2px solid #6366f1' : '1px solid var(--border-glass)',
                  background: isCurrent 
                    ? 'rgba(99, 102, 241, 0.25)' 
                    : isAccepted 
                    ? 'rgba(16, 185, 129, 0.15)' 
                    : isAttempted 
                    ? 'rgba(245, 158, 11, 0.15)' 
                    : 'rgba(30, 41, 59, 0.5)',
                  color: isAccepted ? '#34d399' : isAttempted ? '#fbbf24' : isCurrent ? '#fff' : 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  transition: 'all 0.15s'
                }}
              >
                {isAccepted && <CheckCircle2 size={13} color="#10b981" />}
                {isAttempted && <AlertCircle size={13} color="#f59e0b" />}
                {!isAccepted && !isAttempted && <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#64748b' }} />}
                <span>Q{idx + 1}</span>
              </button>
            );
          })}
        </div>

        {/* Right: Timer, Proctoring Telemetry & Finish Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {/* Proctoring telemetry indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.78rem',
            color: tabSwitchCount > 0 ? '#fbbf24' : '#94a3b8',
            background: 'rgba(30, 41, 59, 0.6)',
            padding: '5px 10px',
            borderRadius: 7,
            border: '1px solid var(--border-glass)'
          }}>
            <ShieldAlert size={14} color={tabSwitchCount > 0 ? '#f59e0b' : '#38bdf8'} />
            <span>Switches: {tabSwitchCount}</span>
          </div>

          {/* Timer */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.85rem',
            fontWeight: 700,
            color: '#f8fafc',
            background: 'rgba(15, 23, 42, 0.8)',
            padding: '5px 12px',
            borderRadius: 7,
            border: '1px solid rgba(99, 102, 241, 0.3)'
          }}>
            <Clock size={14} color="#818cf8" />
            <span style={{ fontFamily: 'monospace' }}>{formatTime(elapsedSeconds)}</span>
          </div>

          {/* Finish Assessment Button */}
          <button
            type="button"
            onClick={() => setShowFinishConfirm(true)}
            disabled={isFinishing}
            style={{
              padding: '6px 14px',
              borderRadius: 8,
              fontSize: '0.82rem',
              fontWeight: 700,
              border: 'none',
              cursor: isFinishing ? 'not-allowed' : 'pointer',
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              boxShadow: '0 0 15px rgba(239, 68, 68, 0.35)'
            }}
          >
            <Flag size={14} />
            <span>{isFinishing ? 'Finalizing...' : 'Finish Assessment'}</span>
          </button>
        </div>
      </div>

      {/* Main Split Body: Left Problem Details, Right Monaco & Console */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left: Problem Details Pane */}
        <div style={{
          flex: '0 0 45%',
          borderRight: '1px solid var(--border-glass)',
          background: 'rgba(15, 23, 42, 0.5)',
          overflowY: 'auto',
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          gap: 20
        }}>
          {currentQuestion ? (
            <>
              {/* Question Header */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#818cf8' }}>
                    Question {currentQuestionIndex + 1} of {assessment.questions.length}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>•</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {currentQuestion.subtopic || currentQuestion.topic}
                  </span>
                </div>
                <h2 style={{
                  margin: 0,
                  fontSize: '1.4rem',
                  fontWeight: 800,
                  fontFamily: 'var(--font-heading)',
                  color: '#ffffff'
                }}>
                  {currentQuestion.title}
                </h2>
              </div>

              {/* Problem Description */}
              <div style={{
                fontSize: '0.92rem',
                lineHeight: 1.6,
                color: '#cbd5e1',
                whiteSpace: 'pre-wrap',
                fontFamily: 'inherit'
              }}>
                {currentQuestion.description}
              </div>

              {/* Input & Output Format */}
              {(currentQuestion.input_format || currentQuestion.output_format) && (
                <div style={{
                  background: 'rgba(30, 41, 59, 0.4)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 10,
                  padding: '14px 16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 10
                }}>
                  {currentQuestion.input_format && (
                    <div>
                      <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#a5b4fc', marginBottom: 2 }}>
                        Input Format:
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                        {currentQuestion.input_format}
                      </div>
                    </div>
                  )}
                  {currentQuestion.output_format && (
                    <div>
                      <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#a5b4fc', marginBottom: 2 }}>
                        Output Format:
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
                        {currentQuestion.output_format}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Constraints */}
              {currentQuestion.constraints && currentQuestion.constraints.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: 8 }}>
                    Constraints
                  </h3>
                  <ul style={{ margin: 0, paddingLeft: 20, fontSize: '0.82rem', color: '#94a3b8', lineHeight: 1.5 }}>
                    {currentQuestion.constraints.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Sample Test Cases with Explanations */}
              {currentQuestion.sample_test_cases && currentQuestion.sample_test_cases.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: 10 }}>
                    Sample Test Cases
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {currentQuestion.sample_test_cases.map((tc, i) => (
                      <div
                        key={i}
                        style={{
                          background: 'rgba(30, 41, 59, 0.55)',
                          border: '1px solid var(--border-glass)',
                          borderRadius: 10,
                          padding: '12px 14px',
                          fontSize: '0.82rem'
                        }}
                      >
                        <div style={{ fontWeight: 700, color: '#a5b4fc', marginBottom: 6 }}>
                          Example {i + 1}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: 6, marginBottom: 4 }}>
                          <span style={{ color: 'var(--text-muted)' }}>Input:</span>
                          <code style={{ color: '#38bdf8', fontFamily: 'monospace' }}>
                            {typeof tc.input === 'object' ? JSON.stringify(tc.input) : String(tc.input)}
                          </code>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: 6, marginBottom: 4 }}>
                          <span style={{ color: 'var(--text-muted)' }}>Output:</span>
                          <code style={{ color: '#34d399', fontFamily: 'monospace' }}>
                            {typeof tc.expected_output === 'object' ? JSON.stringify(tc.expected_output) : String(tc.expected_output)}
                          </code>
                        </div>
                        {tc.explanation && (
                          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 4 }}>
                            <i>{tc.explanation}</i>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div>Loading problem details...</div>
          )}
        </div>

        {/* Right: Monaco Editor & Interactive Console */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Action Bar */}
          <div style={{
            padding: '8px 16px',
            background: 'rgba(15, 23, 42, 0.85)',
            borderBottom: '1px solid var(--border-glass)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <FileCode2 size={16} color="#60a5fa" />
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#cbd5e1' }}>
                Solution Editor ({assessment.language})
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              {/* Reset to starter code */}
              <button
                type="button"
                onClick={() => {
                  if (currentQuestion && window.confirm('Reset code to original starter template?')) {
                    handleCodeChange(currentQuestion.starter_code || '');
                  }
                }}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
                title="Reset to starter code"
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </button>

              {/* Run Code */}
              <button
                type="button"
                onClick={handleRunCode}
                disabled={isRunning || isSubmitting}
                style={{
                  padding: '6px 14px',
                  borderRadius: 7,
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: (isRunning || isSubmitting) ? 'not-allowed' : 'pointer',
                  background: 'rgba(30, 41, 59, 0.8)',
                  border: '1px solid rgba(148, 163, 184, 0.3)',
                  color: '#f8fafc',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6
                }}
              >
                <Play size={13} color="#38bdf8" />
                <span>{isRunning ? 'Running...' : 'Run Code'}</span>
              </button>

              {/* Submit Solution */}
              <button
                type="button"
                onClick={handleSubmitQuestion}
                disabled={isRunning || isSubmitting}
                style={{
                  padding: '6px 16px',
                  borderRadius: 7,
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  cursor: (isRunning || isSubmitting) ? 'not-allowed' : 'pointer',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  border: 'none',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  boxShadow: '0 0 15px rgba(16, 185, 129, 0.35)'
                }}
              >
                <Send size={13} />
                <span>{isSubmitting ? 'Evaluating...' : 'Submit Solution'}</span>
              </button>
            </div>
          </div>

          {/* Monaco Editor Component */}
          <div style={{ flex: '1 1 60%', position: 'relative' }}>
            <Editor
              height="100%"
              language={monacoLang}
              value={currentCode}
              onChange={handleCodeChange}
              onMount={handleEditorMount}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "'Fira Code', 'JetBrains Mono', Consolas, monospace",
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                readOnly: false,
                automaticLayout: true,
                tabSize: 4,
                wordWrap: 'on'
              }}
            />
          </div>

          {/* Bottom Console / Test Results Output */}
          <div style={{
            flex: '0 0 38%',
            borderTop: '1px solid var(--border-glass)',
            background: 'rgba(10, 15, 29, 0.95)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '6px 16px',
              background: 'rgba(15, 23, 42, 0.9)',
              borderBottom: '1px solid var(--border-glass)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.78rem',
              fontWeight: 600,
              color: 'var(--text-muted)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Terminal size={14} color="#a5b4fc" />
                <span>Execution &amp; Test Results</span>
              </div>
              {currentConsole?.data && (
                <span style={{
                  color: currentConsole.data.status === 'Accepted' || (currentConsole.data.passed_count === currentConsole.data.total_count && currentConsole.data.total_count > 0)
                    ? '#34d399'
                    : '#f87171',
                  fontWeight: 700
                }}>
                  {currentConsole.data.status || (currentConsole.data.passed_count === currentConsole.data.total_count ? 'Accepted' : 'Failed')}
                </span>
              )}
            </div>

            <div style={{ flex: 1, padding: '12px 16px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '0.82rem' }}>
              {errorMessage && (
                <div style={{ color: '#f87171', marginBottom: 10 }}>
                  Error: {errorMessage}
                </div>
              )}

              {currentConsole ? (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: 4,
                      background: currentConsole.type === 'submit' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                      color: currentConsole.type === 'submit' ? '#818cf8' : '#60a5fa',
                      fontSize: '0.72rem',
                      fontWeight: 700
                    }}>
                      {currentConsole.type === 'submit' ? 'Full Validation (Hidden Tests)' : 'Sample Test Run'}
                    </span>
                    <span style={{ color: '#cbd5e1' }}>
                      Passed: {currentConsole.data.passed_count} / {currentConsole.data.total_count}
                    </span>
                    {currentConsole.data.execution_time_ms !== undefined && (
                      <span style={{ color: 'var(--text-muted)' }}>
                        ({currentConsole.data.execution_time_ms.toFixed(1)} ms)
                      </span>
                    )}
                  </div>

                  {/* Standard Output if present */}
                  {currentConsole.data.stdout && (
                    <div style={{ marginBottom: 10 }}>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: 4 }}>Standard Output:</div>
                      <pre style={{ margin: 0, padding: 8, background: 'rgba(30, 41, 59, 0.5)', borderRadius: 6, color: '#e2e8f0', whiteSpace: 'pre-wrap' }}>
                        {currentConsole.data.stdout}
                      </pre>
                    </div>
                  )}

                  {/* Test case breakdown */}
                  {currentConsole.data.results && currentConsole.data.results.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {currentConsole.data.results.map((r, i) => (
                        <div
                          key={i}
                          style={{
                            padding: '6px 10px',
                            borderRadius: 6,
                            background: r.passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            border: `1px solid ${r.passed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between'
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            {r.passed ? (
                              <CheckCircle2 size={14} color="#10b981" />
                            ) : (
                              <XCircle size={14} color="#ef4444" />
                            )}
                            <span style={{ color: r.passed ? '#34d399' : '#f87171' }}>
                              Test Case {i + 1} {r.is_hidden ? '(Hidden)' : ''}: {r.passed ? 'Passed' : 'Failed'}
                            </span>
                          </div>
                          {r.safe_error_info && (
                            <span style={{ fontSize: '0.75rem', color: '#f87171' }}>
                              {r.safe_error_info}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div style={{ color: 'var(--text-muted)', textAlign: 'center', paddingTop: 20 }}>
                  Click <b>"Run Code"</b> to test against sample test cases, or <b>"Submit Solution"</b> to validate against hidden evaluation test cases.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal to Finish Assessment */}
      {showFinishConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100
        }}>
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-glass)',
            borderRadius: 16,
            padding: 28,
            maxWidth: 480,
            width: '90%',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)'
          }}>
            <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: 12 }}>
              Finish Assessment?
            </h3>
            <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 20 }}>
              Are you sure you want to end your assessment? Your latest submitted solutions will be graded and compiled into an official performance report.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
              <button
                type="button"
                onClick={() => setShowFinishConfirm(false)}
                style={{
                  padding: '8px 18px',
                  borderRadius: 8,
                  border: '1px solid var(--border-glass)',
                  background: 'transparent',
                  color: '#cbd5e1',
                  cursor: 'pointer'
                }}
              >
                Continue Assessment
              </button>
              <button
                type="button"
                onClick={handleFinishConfirm}
                style={{
                  padding: '8px 20px',
                  borderRadius: 8,
                  border: 'none',
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  color: '#fff',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                Yes, Finish &amp; Submit
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Full-screen Lock Overlay */}
      {isFullscreenLocked && (
        <FullscreenLockOverlay 
          onReenterFullscreen={async () => {
            try {
              await requestBrowserFullscreen();
              setIsFullscreenLocked(false);
            } catch (err) {
              console.error(err);
            }
          }}
        />
      )}
    </div>
  );
}
