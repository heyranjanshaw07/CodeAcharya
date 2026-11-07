import React, { useState, useEffect, useRef } from 'react';
import { 
  GraduationCap, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Send, 
  Award, 
  CheckCircle2, 
  HelpCircle, 
  Sparkles, 
  RotateCcw,
  BarChart2,
  TrendingUp,
  BrainCircuit,
  MessageSquare,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  ArrowLeft
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { usePasteRestriction } from '../hooks/usePasteRestriction';

export default function VivaRoom({ 
  currentProblem, 
  currentCode, 
  language,
  onBack,
  isAssessmentMode = true
}) {
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [studentAnswer, setStudentAnswer] = useState('');
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [evaluationError, setEvaluationError] = useState(null);
  const [sessionCompleted, setSessionCompleted] = useState(false);
  const [answersHistory, setAnswersHistory] = useState([]);
  const [answerModality, setAnswerModality] = useState('typed');

  // Audio / Speech states
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const [voices, setVoices] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Refs for audio instances & state management
  const recognitionRef = useRef(null);
  const baseAnswerRef = useRef('');
  const evalRequestIdRef = useRef(0);
  const utteranceRef = useRef(null);
  const hasVoiceTranscriptRef = useRef(false);

  // Unified Copy-Paste Restriction Hook for Viva
  const currentQId = questions[currentIdx]?.id ? `viva_q_${questions[currentIdx].id}` : (currentProblem?.id || 'viva_exam');
  const { 
    elementRef: answerTextareaRef, 
    showWarning: showPasteWarning, 
    warningMessage: pasteWarningMessage, 
    eventProps: pasteEventProps 
  } = usePasteRestriction({
    isRestricted: isAssessmentMode,
    pageType: 'viva',
    questionId: currentQId,
    attemptId: null
  });

  // Initialize Speech capabilities & voice catalogue
  useEffect(() => {
    // 1. Text-to-Speech detection
    const hasTTS = typeof window !== 'undefined' && 'speechSynthesis' in window;
    setTtsSupported(hasTTS);
    if (hasTTS) {
      const loadVoices = () => {
        try {
          const avail = window.speechSynthesis.getVoices();
          if (avail && avail.length > 0) {
            setVoices(avail);
          }
        } catch (e) {
          console.warn('Could not load speech voices:', e);
        }
      };
      loadVoices();
      window.speechSynthesis.addEventListener('voiceschanged', loadVoices);

      return () => {
        try {
          window.speechSynthesis.removeEventListener('voiceschanged', loadVoices);
        } catch (e) {}
      };
    }
  }, []);

  // 2. Speech-to-Text capability detection
  useEffect(() => {
    const hasSTT = typeof window !== 'undefined' && 
      Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
    setSpeechSupported(hasSTT);

    // Teardown any audio on component unmount
    return () => {
      stopSpeaking();
      stopVoiceInput();
    };
  }, []);

  // Stop any ongoing Text-To-Speech
  const stopSpeaking = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {
        // ignore
      }
    }
    if (typeof window !== 'undefined') {
      window._currentVivaUtterance = null;
    }
    utteranceRef.current = null;
    setIsSpeaking(false);
  };

  // Speak Current Question aloud with browser SpeechSynthesis
  const speakCurrentQuestion = (questionObj) => {
    if (!questionObj || typeof window === 'undefined') return;

    if (!('speechSynthesis' in window)) {
      setVoiceError('Text-to-speech is not supported in this browser.');
      return;
    }

    // Toggle off if already speaking
    if (isSpeaking || window.speechSynthesis.speaking) {
      stopSpeaking();
      return;
    }

    // Stop voice dictation to prevent microphone capturing TTS audio
    stopVoiceInput();
    setVoiceError(null);

    // Cancel any previous speech
    stopSpeaking();

    // Chromium synthesis bug workaround: ensure resume if paused
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }

    const fullText = `${questionObj.question}${
      questionObj.hint_guidance ? `. Key focus area: ${questionObj.hint_guidance}` : ''
    }`;

    // A brief tick allows synthesis cancel to settle in Chromium
    setTimeout(() => {
      try {
        const utterance = new SpeechSynthesisUtterance(fullText);
        utteranceRef.current = utterance;
        window._currentVivaUtterance = utterance;
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        utterance.lang = 'en-US';

        // Select an appropriate English voice if available
        const availVoices = window.speechSynthesis.getVoices() || [];
        const englishVoice = 
          availVoices.find(v => v.lang === 'en-US' || v.lang === 'en_US') ||
          availVoices.find(v => v.lang && v.lang.startsWith('en')) ||
          availVoices[0] ||
          null;

        if (englishVoice) {
          utterance.voice = englishVoice;
        }

        utterance.onstart = () => {
          setIsSpeaking(true);
        };

        utterance.onend = () => {
          setIsSpeaking(false);
          utteranceRef.current = null;
          if (typeof window !== 'undefined') {
            window._currentVivaUtterance = null;
          }
        };

        utterance.onerror = (e) => {
          if (e.error !== 'canceled' && e.error !== 'interrupted') {
            console.warn('Speech synthesis playback error:', e);
            setVoiceError(`Audio playback error: ${e.error || 'Playback failed'}`);
          }
          setIsSpeaking(false);
          utteranceRef.current = null;
          if (typeof window !== 'undefined') {
            window._currentVivaUtterance = null;
          }
        };

        setIsSpeaking(true);
        window.speechSynthesis.speak(utterance);
      } catch (err) {
        console.warn('Speech synthesis playback failed:', err);
        setVoiceError('Failed to initialize speech playback. Please check your browser audio settings.');
        setIsSpeaking(false);
        utteranceRef.current = null;
        if (typeof window !== 'undefined') {
          window._currentVivaUtterance = null;
        }
      }
    }, 50);
  };

  // Stop Voice Dictation and detach listeners to prevent duplicate instances
  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      try {
        const rec = recognitionRef.current;
        recognitionRef.current = null;
        rec.onstart = null;
        rec.onresult = null;
        rec.onerror = null;
        rec.onend = null;
        if (typeof rec.stop === 'function') {
          rec.stop();
        } else if (typeof rec.abort === 'function') {
          rec.abort();
        }
      } catch (e) {
        // ignore
      }
    }
    setIsListening(false);
  };

  // Toggle Voice Dictation (STT) with microphone permission check & real-time transcript streaming
  const toggleVoiceInput = async () => {
    setVoiceError(null);

    const SpeechRec = typeof window !== 'undefined' && 
      (window.SpeechRecognition || window.webkitSpeechRecognition);

    if (!SpeechRec) {
      setVoiceError('Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge, or type your answer directly.');
      setIsListening(false);
      return;
    }

    if (isListening) {
      stopVoiceInput();
      return;
    }

    // Stop TTS so examiner audio does not loop into the microphone
    stopSpeaking();

    // Clean up any stale recognition session to avoid duplicate listeners
    stopVoiceInput();

    // Check microphone permission via permissions API if available
    if (typeof navigator !== 'undefined' && navigator.permissions && navigator.permissions.query) {
      try {
        const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
        if (permissionStatus.state === 'denied') {
          setVoiceError('Microphone permission was denied. Please allow microphone access in your browser settings or type your answer.');
          setIsListening(false);
          return;
        }
      } catch (e) {
        // navigator.permissions.query for microphone not supported in all browsers; continue
      }
    }

    try {
      const recognition = new SpeechRec();
      recognitionRef.current = recognition;

      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      // Cache existing typed text so dictation cleanly appends without duplicates
      baseAnswerRef.current = studentAnswer;

      recognition.onstart = () => {
        setIsListening(true);
        setVoiceError(null);
      };

      recognition.onresult = (e) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = 0; i < e.results.length; ++i) {
          const item = e.results[i];
          if (item && item[0]) {
            if (item.isFinal) {
              finalTranscript += item[0].transcript;
            } else {
              interimTranscript += item[0].transcript;
            }
          }
        }

        const spoken = [finalTranscript.trim(), interimTranscript.trim()].filter(Boolean).join(' ');
        if (spoken.length > 0) {
          hasVoiceTranscriptRef.current = true;
          setAnswerModality('voice_transcribed');
          const base = baseAnswerRef.current ? baseAnswerRef.current.trim() : '';
          const combined = base ? `${base} ${spoken}` : spoken;
          setStudentAnswer(combined);
        }
      };

      recognition.onerror = (e) => {
        console.warn('Speech recognition event error:', e.error);
        if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {
          setVoiceError('Microphone permission was denied. Please allow microphone access in your browser settings or type your answer.');
        } else if (e.error === 'no-speech') {
          setVoiceError('No speech was detected. Please check your microphone volume and speak clearly, or type your answer.');
        } else if (e.error === 'audio-capture') {
          setVoiceError('No audio capture device found. Please verify your microphone connection or type your answer.');
        } else if (e.error === 'network') {
          setVoiceError('Speech recognition network error. Please check your connection or type your answer.');
        } else if (e.error !== 'aborted') {
          setVoiceError(`Voice recognition encountered an issue (${e.error}). You can continue by typing.`);
        }
        stopVoiceInput();
      };

      recognition.onend = () => {
        setIsListening(false);
        recognitionRef.current = null;
      };

      recognition.start();
    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      setVoiceError('Could not initialize speech recognition. Please type your answer directly.');
      stopVoiceInput();
    }
  };

  const startNewViva = async () => {
    if (!currentProblem) return;
    evalRequestIdRef.current++;
    stopSpeaking();
    stopVoiceInput();
    hasVoiceTranscriptRef.current = false;
    setAnswerModality('typed');

    setIsLoadingQuestions(true);
    setEvaluationResult(null);
    setEvaluationError(null);
    setSessionCompleted(false);
    setAnswersHistory([]);
    setCurrentIdx(0);
    setStudentAnswer('');
    setVoiceError(null);

    try {
      const res = await fetch('/api/viva/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          code: currentCode,
          language: language
        })
      });
      const data = await res.json();
      setQuestions(data);
    } catch (err) {
      console.error('Failed to start viva session:', err);
      setEvaluationError('Failed to initialize viva questions from the server. Please check connection and retry.');
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  const handleAnswerChange = (val) => {
    setStudentAnswer(val);
    if (!val.trim()) {
      hasVoiceTranscriptRef.current = false;
      setAnswerModality('typed');
    }
  };

  const submitAnswer = async () => {
    const trimmed = studentAnswer.trim();
    if (!trimmed) {
      setVoiceError('Please enter or record a substantive response before submitting.');
      return;
    }
    if (!questions[currentIdx] || isEvaluating) return;

    stopSpeaking();
    stopVoiceInput();

    // Clear previous scorecard immediately so stale scores are never visible while evaluating
    setEvaluationResult(null);
    setIsEvaluating(true);
    setEvaluationError(null);
    const currQ = questions[currentIdx];
    const thisReqId = ++evalRequestIdRef.current;
    const finalModality = hasVoiceTranscriptRef.current ? 'voice_transcribed' : 'typed';

    try {
      const res = await fetch('/api/viva/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: currentProblem.id,
          code: currentCode,
          language: language,
          question_id: currQ.id,
          question: currQ.question,
          category: currQ.category,
          student_answer: trimmed,
          answer_modality: finalModality,
          hint_guidance: currQ.hint_guidance || null,
          topic: currentProblem.topic || null,
          difficulty: currentProblem.difficulty || null,
          expected_concepts: currQ.hint_guidance ? [currQ.hint_guidance] : []
        })
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server returned evaluation error status ${res.status}`);
      }

      const scoreData = await res.json();

      // Guard against stale asynchronous requests
      if (thisReqId !== evalRequestIdRef.current) return;

      setEvaluationResult(scoreData);

      // Assign each question its own latest evaluation while preserving history order
      setAnswersHistory(prev => {
        const newEntry = {
          questionId: currQ.id,
          question: currQ.question,
          category: currQ.category,
          studentAnswer: trimmed,
          modality: finalModality,
          score: scoreData,
          timestamp: new Date().toLocaleTimeString()
        };
        const existingIdx = prev.findIndex(item => item.questionId === currQ.id);
        if (existingIdx >= 0) {
          const updated = [...prev];
          updated[existingIdx] = newEntry;
          return updated;
        }
        return [...prev, newEntry];
      });

      if (scoreData.overall_score >= 80) {
        confetti({ particleCount: 60, spread: 60, origin: { y: 0.7 } });
      }
    } catch (err) {
      console.error('Failed to evaluate answer:', err);
      if (thisReqId === evalRequestIdRef.current) {
        setEvaluationError(err.message || 'Evaluation failed due to a network or server issue. Your answer is preserved. Please retry.');
      }
    } finally {
      if (thisReqId === evalRequestIdRef.current) {
        setIsEvaluating(false);
      }
    }
  };

  const nextQuestion = () => {
    // Invalidate pending requests and clean up all recording resources
    evalRequestIdRef.current++;
    stopSpeaking();
    stopVoiceInput();
    hasVoiceTranscriptRef.current = false;
    setAnswerModality('typed');
    setEvaluationResult(null);
    setEvaluationError(null);
    setStudentAnswer('');
    setVoiceError(null);

    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(currentIdx + 1);
    } else {
      setSessionCompleted(true);
      confetti({ particleCount: 120, spread: 90, origin: { y: 0.6 } });
    }
  };

  const currentQ = questions[currentIdx];

  // Helper to calculate session average for a metric excluding non-applicable questions
  const getDimensionAverage = (key) => {
    const applicable = answersHistory.filter(h => h.score && h.score[key] !== null && h.score[key] !== undefined);
    if (applicable.length === 0) return 'N/A';
    const total = applicable.reduce((acc, h) => acc + h.score[key], 0);
    return `${Math.round(total / applicable.length)}%`;
  };

  const getSessionOverallAverage = () => {
    if (answersHistory.length === 0) return 0;
    const total = answersHistory.reduce((acc, h) => acc + (h.score?.overall_score || 0), 0);
    return Math.round(total / answersHistory.length);
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 16px' }}>
      {/* Title Banner */}
      <div className="glass-panel" style={{ padding: '24px 32px', marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          {onBack && (
            <button 
              type="button"
              onClick={onBack}
              className="nav-back-btn"
              aria-label="Back"
              title="Back to previous page"
            >
              <ArrowLeft size={16} />
              <span>Back</span>
            </button>
          )}

          <div style={{
            width: 52,
            height: 52,
            borderRadius: 14,
            background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 25px rgba(139, 92, 246, 0.45)',
            flexShrink: 0
          }}>
            <GraduationCap size={30} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
              AI Viva Voce Examination Room
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
              Simulates a formal computer science oral defense: testing conceptual depth, time/space rigor, and architectural choices.
            </p>
          </div>
        </div>

        <button 
          onClick={startNewViva}
          className="btn btn-purple"
          disabled={isLoadingQuestions}
          style={{ padding: '10px 20px' }}
        >
          <RotateCcw size={16} />
          {isLoadingQuestions ? 'Preparing Questions...' : 'Start Viva Defense'}
        </button>
      </div>

      {/* Main Content Area */}
      {questions.length === 0 && !isLoadingQuestions && (
        <div className="glass-panel" style={{ padding: 48, textAlign: 'center' }}>
          <div style={{ maxWidth: 500, margin: '0 auto' }}>
            <Award size={48} color="#8b5cf6" style={{ marginBottom: 16, opacity: 0.8 }} />
            <h3 style={{ fontSize: '1.25rem', marginBottom: 8 }}>Ready for your Technical Defense?</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 24 }}>
              The AI Viva Examiner will review your implementation for <strong>{currentProblem?.title}</strong>, asking 4 rigorous questions on design rationale, algorithmic complexity, and failure modes.
            </p>
            <button className="btn btn-purple" onClick={startNewViva} style={{ padding: '12px 28px', fontSize: '1rem' }}>
              <GraduationCap size={18} /> Begin Examination
            </button>
          </div>
        </div>
      )}

      {isLoadingQuestions && (
        <div className="glass-panel" style={{ padding: 48, textAlign: 'center' }}>
          <Sparkles size={36} color="#8b5cf6" className="pulse-indicator" style={{ marginBottom: 16 }} />
          <h3 style={{ fontSize: '1.1rem' }}>The Examiner is reviewing your source code...</h3>
          <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>Synthesizing technical questions across Big-O complexity, base cases, and data structure choices.</p>
        </div>
      )}

      {/* Live Question Chamber */}
      {questions.length > 0 && !sessionCompleted && (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr)', gap: 24 }}>
          {/* Left Column: Current Question and Input */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Question Card */}
            <div className="glass-panel-elevated" style={{ padding: 24, border: '1px solid rgba(139, 92, 246, 0.3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <span className="badge badge-topic" style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#c084fc' }}>
                  Question {currentIdx + 1} of {questions.length} • {currentQ?.category?.toUpperCase()}
                </span>

                <button 
                  onClick={() => speakCurrentQuestion(currentQ)}
                  className={`btn ${isSpeaking ? 'btn-amber pulse-indicator' : 'btn-secondary'}`}
                  style={{ padding: '6px 12px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6 }}
                  title={isSpeaking ? "Click to stop speaking" : (ttsSupported ? "Read complete question and key focus area aloud" : "Speech synthesis is unsupported in this browser")}
                >
                  {isSpeaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
                  {isSpeaking ? 'Stop Audio' : 'Listen'}
                </button>
              </div>

              <h2 style={{ fontSize: '1.15rem', fontWeight: 600, lineHeight: 1.5, marginBottom: 16 }}>
                {currentQ?.question}
              </h2>

              {currentQ?.hint_guidance && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderLeft: '3px solid #8b5cf6',
                  padding: '8px 12px',
                  borderRadius: 4,
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)'
                }}>
                  <strong style={{ color: '#a78bfa' }}>Key Focus Area:</strong> {currentQ.hint_guidance}
                </div>
              )}
            </div>

            {/* Answer Input Area */}
            <div className="glass-panel" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: 6 }}>
                    <MessageSquare size={16} color="#8b5cf6" />
                    Your Viva Response:
                  </label>
                  {answerModality === 'voice_transcribed' ? (
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      border: '1px solid rgba(16, 185, 129, 0.4)',
                      padding: '2px 8px',
                      borderRadius: 10,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4
                    }}>
                      <Mic size={11} /> Voice Transcribed
                    </span>
                  ) : (
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 500,
                      background: 'rgba(148, 163, 184, 0.12)',
                      color: '#94a3b8',
                      border: '1px solid rgba(148, 163, 184, 0.25)',
                      padding: '2px 8px',
                      borderRadius: 10,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4
                    }}>
                      ⌨️ Typed
                    </span>
                  )}

                  {isAssessmentMode && (
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      background: 'rgba(239, 68, 68, 0.12)',
                      color: '#f87171',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      padding: '2px 8px',
                      borderRadius: 10,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4
                    }} title="Assessment Mode: Paste is disabled, but copying is allowed.">
                      <ShieldCheck size={11} /> Paste Disabled
                    </span>
                  )}
                </div>

                {isListening ? (
                  <button 
                    onClick={stopVoiceInput}
                    className="btn btn-amber pulse-indicator"
                    style={{ padding: '6px 14px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6 }}
                    title="Stop recording"
                  >
                    <MicOff size={14} /> Stop Recording
                  </button>
                ) : speechSupported ? (
                  <button 
                    onClick={toggleVoiceInput}
                    className="btn btn-secondary"
                    style={{ padding: '6px 14px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6 }}
                    title="Start voice dictation (speech-to-text)"
                  >
                    <Mic size={14} /> Voice Dictation
                  </button>
                ) : (
                  <button 
                    onClick={() => setVoiceError('Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge, or type your answer directly.')}
                    className="btn btn-secondary"
                    style={{ padding: '6px 14px', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: 6, opacity: 0.65, cursor: 'not-allowed' }}
                    title="Speech recognition unsupported in this browser"
                  >
                    <Mic size={14} /> Voice Dictation (Unsupported)
                  </button>
                )}
              </div>

              {/* Blocked Paste Attempt Warning Banner */}
              {showPasteWarning && (
                <div className="animate-slide-down" style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 14px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.45)',
                  borderRadius: 8,
                  marginBottom: 12,
                  fontSize: '0.8rem',
                  color: '#fca5a5'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <AlertCircle size={15} color="#ef4444" style={{ flexShrink: 0 }} />
                    <span><strong>Action Blocked:</strong> {pasteWarningMessage}</span>
                  </div>
                </div>
              )}

              {/* Active Recording Status Banner */}
              {isListening && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 14px',
                  background: 'rgba(239, 68, 68, 0.12)',
                  border: '1px solid rgba(239, 68, 68, 0.35)',
                  borderRadius: 8,
                  marginBottom: 12,
                  fontSize: '0.8rem',
                  color: '#fca5a5'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      background: '#ef4444',
                      display: 'inline-block',
                      boxShadow: '0 0 10px #ef4444'
                    }} className="pulse-indicator" />
                    <span><strong>Recording active:</strong> Speak your answer. Live transcript appears below.</span>
                  </div>
                  <button
                    onClick={stopVoiceInput}
                    className="btn btn-amber"
                    style={{ padding: '3px 10px', fontSize: '0.72rem' }}
                  >
                    Stop Recording
                  </button>
                </div>
              )}

              {/* Informative voice error banner */}
              {voiceError && (
                <div style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: '#fca5a5',
                  padding: '8px 12px',
                  borderRadius: 8,
                  fontSize: '0.78rem',
                  marginBottom: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 8
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <AlertCircle size={14} style={{ flexShrink: 0 }} />
                    <span>{voiceError}</span>
                  </div>
                  <button
                    onClick={() => setVoiceError(null)}
                    style={{ background: 'none', border: 'none', color: '#fca5a5', cursor: 'pointer', fontSize: '0.8rem' }}
                  >
                    ✕
                  </button>
                </div>
              )}

              <textarea
                ref={answerTextareaRef}
                {...pasteEventProps}
                value={studentAnswer}
                onChange={(e) => handleAnswerChange(e.target.value)}
                placeholder="Formulate your technical answer here by speaking or typing (e.g. explain time complexity O(N), stack frames, reason for choosing hash maps, edge cases)..."
                rows={6}
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.9)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 10,
                  color: '#fff',
                  padding: 14,
                  fontSize: '0.9rem',
                  fontFamily: 'var(--font-body)',
                  lineHeight: 1.5,
                  resize: 'vertical',
                  marginBottom: 16
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                  Word count: {studentAnswer.trim() ? studentAnswer.trim().split(/\s+/).length : 0}
                </span>

                <button 
                  className="btn btn-purple"
                  onClick={submitAnswer}
                  disabled={isEvaluating || !studentAnswer.trim()}
                  style={{ padding: '8px 20px', display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  {isEvaluating ? <RefreshCw size={15} className="spin-indicator" /> : <Send size={15} />}
                  {isEvaluating ? 'Evaluating with Examiner...' : 'Submit Viva Answer'}
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Live Scorecard & Feedback */}
          <div>
            {isEvaluating ? (
              <div className="glass-panel" style={{ padding: 48, textAlign: 'center' }}>
                <div style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: '#c084fc',
                  marginBottom: 16,
                  letterSpacing: '0.05em'
                }}>
                  Status: Evaluating...
                </div>
                <Sparkles size={36} color="#8b5cf6" className="pulse-indicator" style={{ margin: '0 auto 16px' }} />
                <h3 style={{ fontSize: '1.1rem', marginBottom: 6 }}>Evaluating your answer...</h3>
                <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
                  Analyzing technical depth, Big-O proof, and algorithmic invariants against the question rubric.
                </p>
              </div>
            ) : evaluationError ? (
              <div className="glass-panel" style={{ padding: 32, textAlign: 'center', border: '1px solid rgba(239, 68, 68, 0.4)' }}>
                <div style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: '#f87171',
                  marginBottom: 12,
                  letterSpacing: '0.05em'
                }}>
                  Status: Evaluation failed
                </div>
                <AlertCircle size={40} color="#ef4444" style={{ margin: '0 auto 12px' }} />
                <h3 style={{ fontSize: '1.05rem', color: '#fca5a5', marginBottom: 8 }}>Evaluation Encountered an Error</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: 20 }}>
                  {evaluationError}
                </p>
                <button 
                  onClick={submitAnswer}
                  className="btn btn-purple"
                  style={{ padding: '8px 20px' }}
                >
                  <RotateCcw size={14} /> Retry Evaluation
                </button>
              </div>
            ) : evaluationResult ? (
              <div className="glass-panel-elevated animate-slide-down" style={{ 
                padding: 24, 
                border: `1px solid ${
                  evaluationResult.overall_score >= 80 
                    ? 'rgba(16, 185, 129, 0.3)' 
                    : evaluationResult.overall_score >= 50 
                      ? 'rgba(245, 158, 11, 0.3)' 
                      : 'rgba(239, 68, 68, 0.3)'
                }` 
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                  <div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Evaluation Scorecard
                    </span>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-subtle)' }}>
                      Status: {evaluationResult.answer_relevance === 'irrelevant' ? 'Unintelligible / Off-Topic' : (evaluationResult.answer_relevance === 'uncertain' ? 'Uncertainty Acknowledged' : 'Evaluated')} • Question {currentIdx + 1} • {evaluationResult.answer_modality === 'voice_transcribed' ? '🎤 Voice' : '⌨️ Typed'}
                    </div>
                  </div>

                  <div style={{
                    fontSize: '1.25rem',
                    fontWeight: 800,
                    color: evaluationResult.overall_score >= 80 
                      ? '#34d399' 
                      : evaluationResult.overall_score >= 50 
                        ? '#fbbf24' 
                        : '#ef4444',
                    background: evaluationResult.overall_score >= 80 
                      ? 'rgba(16, 185, 129, 0.15)' 
                      : evaluationResult.overall_score >= 50 
                        ? 'rgba(245, 158, 11, 0.15)' 
                        : 'rgba(239, 68, 68, 0.15)',
                    padding: '4px 14px',
                    borderRadius: 20,
                    border: `1px solid ${
                      evaluationResult.overall_score >= 80 
                        ? 'rgba(16, 185, 129, 0.4)' 
                        : evaluationResult.overall_score >= 50 
                          ? 'rgba(245, 158, 11, 0.4)' 
                          : 'rgba(239, 68, 68, 0.4)'
                    }`
                  }}>
                    {evaluationResult.overall_score}% Overall
                  </div>
                </div>

                {/* 4 Core Dimensions: Shows N/A when non-applicable */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginBottom: 24 }}>
                  {[
                    { label: 'Conceptual Understanding', score: evaluationResult.conceptual_score, color: '#8b5cf6' },
                    { label: 'Code Understanding', score: evaluationResult.code_understanding_score, color: '#06b6d4' },
                    { label: 'Complexity Analysis', score: evaluationResult.complexity_score, color: '#f59e0b' },
                    { 
                      label: evaluationResult.answer_modality === 'voice_transcribed' 
                        ? (evaluationResult.communication_label || 'Verbal Response Clarity') 
                        : 'Communication & Clarity', 
                      score: evaluationResult.communication_score, 
                      color: '#10b981',
                      note: evaluationResult.answer_modality === 'voice_transcribed' 
                        ? 'Assessed on transcript organization & clarity' 
                        : 'N/A for typed answers'
                    }
                  ].map(m => {
                    const isApplicable = m.score !== null && m.score !== undefined;
                    return (
                      <div key={m.label}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                          <span style={{ color: isApplicable ? 'var(--text-main)' : 'var(--text-muted)', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6 }}>
                            {m.label}
                            {m.note && (
                              <span style={{ fontSize: '0.7rem', color: 'var(--text-subtle)', fontWeight: 400 }}>
                                ({m.note})
                              </span>
                            )}
                          </span>
                          <span style={{ fontWeight: 700, color: isApplicable ? m.color : 'var(--text-muted)' }}>
                            {isApplicable ? `${m.score}%` : 'N/A'}
                          </span>
                        </div>
                        <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden' }}>
                          <div style={{
                            height: '100%',
                            width: isApplicable ? `${m.score}%` : '0%',
                            background: m.color,
                            borderRadius: 3,
                            transition: 'width 0.8s ease'
                          }} />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Examiner Feedback */}
                <div style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  borderRadius: 10,
                  padding: 16,
                  border: '1px solid var(--border-glass)',
                  marginBottom: 16
                }}>
                  <h4 style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: 6 }}>
                    Examiner Remarks
                  </h4>
                  <p style={{ fontSize: '0.875rem', lineHeight: 1.5, color: '#e2e8f0', margin: 0 }}>
                    {evaluationResult.feedback}
                  </p>
                </div>

                {/* Points Recognized */}
                {evaluationResult.ideal_points_covered && evaluationResult.ideal_points_covered.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <h5 style={{ fontSize: '0.75rem', color: '#34d399', textTransform: 'uppercase', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <CheckCircle2 size={14} /> Points Recognized
                    </h5>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.8rem', color: '#cbd5e1' }}>
                      {evaluationResult.ideal_points_covered.map((pt, i) => (
                        <li key={i}>{pt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Missing Concepts */}
                {evaluationResult.missing_concepts && evaluationResult.missing_concepts.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <h5 style={{ fontSize: '0.75rem', color: '#f59e0b', textTransform: 'uppercase', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <HelpCircle size={14} /> Concepts Missing / To Clarify
                    </h5>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.8rem', color: '#cbd5e1' }}>
                      {evaluationResult.missing_concepts.map((mc, i) => (
                        <li key={i}>{mc}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Suggested Improvement or Retry Hint */}
                {evaluationResult.suggested_improvement && (
                  <div style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderLeft: '3px solid #f59e0b',
                    padding: '8px 12px',
                    borderRadius: 4,
                    fontSize: '0.78rem',
                    color: 'var(--text-muted)',
                    marginBottom: 20
                  }}>
                    <strong style={{ color: '#fbbf24' }}>Improvement Guidance:</strong> {evaluationResult.suggested_improvement}
                  </div>
                )}

                {/* Next Step Button */}
                <button 
                  onClick={nextQuestion}
                  className="btn btn-emerald"
                  style={{ width: '100%', padding: '10px 0', fontSize: '0.9rem' }}
                >
                  {currentIdx + 1 < questions.length ? 'Next Viva Question' : 'Complete Oral Defense'}
                </button>
              </div>
            ) : (
              <div className="glass-panel" style={{ padding: 36, textAlign: 'center', color: 'var(--text-muted)' }}>
                <div style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  color: 'var(--text-subtle)',
                  marginBottom: 12,
                  letterSpacing: '0.05em'
                }}>
                  Status: Not evaluated
                </div>
                <BrainCircuit size={40} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
                <p style={{ fontSize: '0.875rem' }}>
                  Answer the question on the left to receive your live multi-metric viva scorecard.
                </p>
              </div>
            )}
          </div>

          {/* Collapsible Session Defense History */}
          {answersHistory.length > 0 && (
            <div style={{ gridColumn: '1 / -1', marginTop: 12 }}>
              <div className="glass-panel" style={{ padding: '14px 20px' }}>
                <div 
                  onClick={() => setShowHistory(!showHistory)}
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', userSelect: 'none' }}
                >
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <ShieldCheck size={16} color="#10b981" />
                    Viva Session Defense History ({answersHistory.length} answered)
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#a78bfa', fontWeight: 500 }}>
                    {showHistory ? 'Hide Previous Answers ▲' : 'View Previous Answers ▼'}
                  </span>
                </div>

                {showHistory && (
                  <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {answersHistory.map((item, idx) => (
                      <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, flexWrap: 'wrap', gap: 8 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#c084fc' }}>
                              Question {item.questionId || (idx + 1)} • {item.category?.toUpperCase()}: {item.question}
                            </span>
                            <span style={{
                              fontSize: '0.68rem',
                              padding: '2px 6px',
                              borderRadius: 6,
                              background: item.modality === 'voice_transcribed' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                              color: item.modality === 'voice_transcribed' ? '#34d399' : '#94a3b8',
                              border: `1px solid ${item.modality === 'voice_transcribed' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(148, 163, 184, 0.2)'}`
                            }}>
                              {item.modality === 'voice_transcribed' ? '🎤 Voice' : '⌨️ Typed'}
                            </span>
                          </div>
                          <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            color: item.score?.overall_score >= 80 ? '#34d399' : (item.score?.overall_score >= 50 ? '#fbbf24' : '#ef4444')
                          }}>
                            {item.score?.overall_score}% Overall
                          </span>
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>
                          <strong>Your Answer:</strong> "{item.studentAnswer}"
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          <strong>Examiner:</strong> {item.score?.feedback || item.score?.examinerRemarks}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Session Completed Final Score Summary */}
      {sessionCompleted && (
        <div className="glass-panel-elevated animate-slide-down" style={{ padding: 40, textAlign: 'center', maxWidth: 800, margin: '0 auto' }}>
          <div style={{
            width: 72,
            height: 72,
            borderRadius: 20,
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            boxShadow: '0 0 30px rgba(16, 185, 129, 0.4)'
          }}>
            <ShieldCheck size={40} color="#fff" />
          </div>

          <h2 style={{ fontSize: '1.6rem', fontWeight: 700, marginBottom: 8 }}>
            Viva Voce Defense Completed!
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 20 }}>
            Your technical oral defense on <strong>{currentProblem?.title}</strong> has been logged to your learning profile.
          </p>

          <div style={{
            display: 'inline-block',
            fontSize: '1.3rem',
            fontWeight: 800,
            color: '#34d399',
            background: 'rgba(16, 185, 129, 0.15)',
            padding: '6px 20px',
            borderRadius: 20,
            border: '1px solid rgba(16, 185, 129, 0.4)',
            marginBottom: 28
          }}>
            Overall Defense Average: {getSessionOverallAverage()}%
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 32 }}>
            {[
              {
                label: 'Conceptual Depth',
                score: getDimensionAverage('conceptual_score'),
                color: '#8b5cf6'
              },
              {
                label: 'Code Mechanics',
                score: getDimensionAverage('code_understanding_score'),
                color: '#06b6d4'
              },
              {
                label: 'Complexity Rigor',
                score: getDimensionAverage('complexity_score'),
                color: '#f59e0b'
              },
              {
                label: 'Verbal Clarity',
                score: getDimensionAverage('communication_score'),
                color: '#10b981'
              }
            ].map(m => (
              <div key={m.label} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 16, borderRadius: 12, border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: m.color, marginBottom: 4 }}>
                  {m.score}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{m.label}</div>
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, flexWrap: 'wrap' }}>
            {onBack && (
              <button 
                type="button" 
                className="nav-back-btn" 
                onClick={onBack} 
                style={{ padding: '10px 22px', fontSize: '0.9rem' }}
                aria-label="Back"
                title="Back to previous page"
              >
                <ArrowLeft size={16} />
                <span>Back</span>
              </button>
            )}
            <button type="button" className="btn btn-primary" onClick={startNewViva} style={{ padding: '10px 24px' }}>
              <RotateCcw size={16} /> Retake Viva Defense
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
