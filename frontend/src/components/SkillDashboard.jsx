import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Flame, 
  CheckCircle2, 
  Clock, 
  Lightbulb, 
  AlertTriangle, 
  GraduationCap, 
  TrendingUp, 
  FileText,
  Sparkles,
  ArrowLeft,
  Timer,
  Zap,
  Flag,
  Play,
  Code2,
  Award,
  ShieldCheck,
  Cpu,
  Layers,
  ChevronRight,
  RefreshCw,
  ExternalLink,
  Download
} from 'lucide-react';
import ScoreBreakdownModal from './ScoreBreakdownModal';

export default function SkillDashboard({ studentProfile, onSelectTopic, onBack }) {
  const [reportGenerated, setReportGenerated] = useState(false);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [isLoadingScores, setIsLoadingScores] = useState(true);
  const [selectedScoreRecord, setSelectedScoreRecord] = useState(null);
  const [showScoreModal, setShowScoreModal] = useState(false);
  const [scoreFilter, setScoreFilter] = useState('all');
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  const handleDownloadPdfReport = async () => {
    setIsDownloadingPdf(true);
    try {
      const res = await fetch('/api/reports/pdf?date_filter=last_30_days');
      if (!res.ok) throw new Error('Failed to generate PDF report');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CodeAcharya_Performance_Report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF download error:', err);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  // Fetch real scoring analytics and history from backend
  useEffect(() => {
    let isMounted = true;

    async function loadScoreAnalytics() {
      setIsLoadingScores(true);
      try {
        const [analyticsRes, historyRes] = await Promise.all([
          fetch('/api/scores/analytics'),
          fetch('/api/scores/history?limit=30')
        ]);

        if (analyticsRes.ok) {
          const data = await analyticsRes.json();
          if (isMounted) setAnalyticsData(data);
        }

        if (historyRes.ok) {
          const data = await historyRes.json();
          if (isMounted) setScoreHistory(data.scores || []);
        }
      } catch (err) {
        console.warn('Could not fetch score analytics:', err);
      } finally {
        if (isMounted) setIsLoadingScores(false);
      }
    }

    loadScoreAnalytics();

    return () => {
      isMounted = false;
    };
  }, []);

  const topicMastery = studentProfile?.topic_mastery || {
    "Recursion & Backtracking": 0,
    "Arrays & Hashing": 0,
    "Strings": 0,
    "Stack & Queue": 0,
    "Dynamic Programming": 0,
    "Algorithms & Two Pointers": 0
  };

  const getTopicColor = (percentage) => {
    if (percentage >= 80) return '#10b981'; // Emerald
    if (percentage >= 65) return '#6366f1'; // Indigo
    if (percentage >= 50) return '#f59e0b'; // Amber
    if (percentage > 0) return '#06b6d4'; // Cyan
    return 'var(--text-subtle)'; // Subdued for unattempted
  };

  const formatSecs = (totalSecs) => {
    if (!totalSecs || totalSecs <= 0) return '0s';
    const hrs = Math.floor(totalSecs / 3600);
    const mins = Math.floor((totalSecs % 3600) / 60);
    const secs = totalSecs % 60;
    if (hrs > 0) {
      return `${hrs}h ${mins}m`;
    }
    if (mins > 0) {
      return `${mins}m ${secs > 0 ? `${secs}s` : ''}`.trim();
    }
    return `${secs}s`;
  };

  // Solving duration stats
  const solvingTimesMap = studentProfile?.problem_solving_times || {};
  const solvingEntries = Object.entries(solvingTimesMap);

  const avgSeconds = solvingEntries.length > 0
    ? Math.round(solvingEntries.reduce((acc, [_, item]) => acc + (item.time_spent_seconds || 0), 0) / solvingEntries.length)
    : 0;

  const avgSpeedFormatted = avgSeconds > 0 
    ? formatSecs(avgSeconds) 
    : (studentProfile?.average_solving_time_formatted || '--');

  const totalPracticeSeconds = studentProfile?.total_coding_time_seconds 
    || ((studentProfile?.total_debug_time_mins || 0) * 60);
  const totalPracticeFormatted = formatSecs(totalPracticeSeconds);

  const totalSolved = studentProfile?.total_solved || 0;
  const totalAttempts = studentProfile?.total_attempts || 0;
  const hintsUnlocked = studentProfile?.hints_unlocked || 0;
  const hasAnyData = totalAttempts > 0 || totalSolved > 0 || (scoreHistory && scoreHistory.length > 0);

  // Computed coding score metrics (grounded in real database records)
  const averageCodingScore = analyticsData?.average_score 
    ?? (studentProfile?.average_coding_score != null ? Math.round(studentProfile.average_coding_score * 10) / 10 : null);
  const bestCodingScore = analyticsData?.best_score 
    ?? (studentProfile?.best_coding_score != null ? Math.round(studentProfile.best_coding_score * 10) / 10 : null);
  const totalScoredAttempts = analyticsData?.total_scored_evaluations 
    ?? (studentProfile?.total_scored_evaluations || scoreHistory.length);

  const dimensionAvgs = analyticsData?.dimension_averages || {
    correctness: 0,
    complexity: 0,
    code_quality: 0,
    approach: 0,
    independent: 0
  };

  // Filter score history based on filter chip
  const filteredScores = scoreHistory.filter(item => {
    const s = item.overall_score ?? 0;
    if (scoreFilter === '100') return s >= 99.5;
    if (scoreFilter === 'partial') return s > 0 && s < 99.5;
    if (scoreFilter === '0') return s === 0;
    return true;
  });

  const handleOpenBreakdown = (record) => {
    // If the record has score_data inside, pass that; otherwise construct a compatible object
    const scoreDataObj = record.score_data || {
      overall_score: record.overall_score,
      dimensions: record.dimensions || {
        correctness: { score: record.correctness_score, max_score: 40, status: 'evaluated', description: 'Test execution verification (Passed/Total * 40)' },
        complexity: { score: record.complexity_score, max_score: 20, status: 'evaluated', description: 'Static Big-O complexity analysis' },
        code_quality: { score: record.quality_score, max_score: 15, status: 'evaluated', description: 'AST code quality and style' },
        approach: { score: record.approach_score, max_score: 15, status: 'evaluated', description: 'Problem-solving approach alignment' },
        independent: { score: record.independent_score != null ? record.independent_score : 10, max_score: 10, status: 'evaluated', description: 'Independent problem-solving based on hint usage' }
      },
      evaluation_status: record.evaluation_status || 'evaluated',
      tests_passed: record.tests_passed,
      tests_total: record.tests_total,
      unique_hints_used: record.unique_hints_used ?? 0,
      memory_usage_mb: record.memory_usage_mb ?? null,
      coding_time_seconds: record.coding_time_seconds,
      execution_time_seconds: record.execution_time_seconds,
      evaluator_type: record.evaluator_type || 'static_analysis',
      evaluator_notes: record.evaluator_notes || 'Score recorded from actual test execution, static AST analysis, and hint usage.',
      strengths: record.strengths || ['Syntactically valid solution verified against test suite.'],
      suggestions: record.suggestions || []
    };

    setSelectedScoreRecord(scoreDataObj);
    setShowScoreModal(true);
  };

  return (
    <div style={{ maxWidth: 1300, margin: '0 auto', padding: '24px 16px' }}>
      {/* Header Banner */}
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
          <div>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
              Student Skill Profile & Coding Analytics
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
              Transparent, multi-dimensional coding scores (Correctness 50, Complexity 20, Quality 15, Approach 15) backed by real test execution.
            </p>
          </div>
        </div>

        {hasAnyData && (
          <button 
            className="btn btn-emerald"
            disabled={isDownloadingPdf}
            onClick={handleDownloadPdfReport}
            style={{ padding: '8px 18px', display: 'flex', alignItems: 'center', gap: 8 }}
            title="Download genuine multi-page PDF performance report"
          >
            <Download size={16} />
            {isDownloadingPdf ? 'Generating PDF...' : 'Download PDF Report'}
          </button>
        )}
      </div>

      {/* Empty State Banner if no attempts yet */}
      {!hasAnyData && (
        <div className="glass-panel" style={{
          padding: '32px 24px',
          marginBottom: 24,
          textAlign: 'center',
          background: 'rgba(99, 102, 241, 0.05)',
          border: '1px dashed rgba(99, 102, 241, 0.3)'
        }}>
          <div style={{
            width: 50,
            height: 50,
            borderRadius: '50%',
            background: 'rgba(99, 102, 241, 0.15)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 12
          }}>
            <Code2 size={26} color="#818cf8" />
          </div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: '0 0 6px 0', color: '#f8fafc' }}>
            No Coding Attempts Yet
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', maxWidth: 540, margin: '0 auto 16px auto', lineHeight: 1.5 }}>
            You haven't run any code submissions yet. Select a problem in the <strong>Workspace</strong> to begin your algorithmic practice, track your coding score out of 100, and build your mastery profile!
          </p>
          {onBack && (
            <button
              onClick={onBack}
              className="btn btn-primary glow-primary"
              style={{ padding: '8px 20px', fontSize: '0.85rem' }}
            >
              Go to Coding Workspace
            </button>
          )}
        </div>
      )}

      {/* KPI Cards Row (Includes Real Coding Score Card) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: 16, marginBottom: 24 }}>
        {/* Coding Score Primary Card */}
        <div className="glass-panel" style={{ padding: 20, border: '1px solid rgba(99, 102, 241, 0.35)', position: 'relative', overflow: 'hidden' }}>
          <div style={{
            position: 'absolute',
            top: 0,
            right: 0,
            width: 80,
            height: 80,
            background: 'radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%)',
            pointerEvents: 'none'
          }} />
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Average Coding Score</span>
            <Award size={18} color="#818cf8" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: averageCodingScore != null ? '#a5b4fc' : 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {averageCodingScore != null ? `${averageCodingScore}` : '--'}
            <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500, marginLeft: 4 }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: bestCodingScore != null ? '#34d399' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
            <Sparkles size={12} />
            <span>Best: <strong>{bestCodingScore != null ? `${bestCodingScore}/100` : '--'}</strong> ({totalScoredAttempts} evaluated)</span>
          </div>
        </div>

        {/* Problems Solved Card */}
        <div className="glass-panel" style={{ padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Problems Solved</span>
            <CheckCircle2 size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f8fafc' }}>
            {totalSolved}
          </div>
          <div style={{ fontSize: '0.75rem', color: totalSolved > 0 ? '#10b981' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
            {totalSolved > 0 ? <><TrendingUp size={12} /> Verified solutions</> : 'Awaiting first completion'}
          </div>
        </div>

        {/* Problem-Solving Speed Metric Card */}
        <div className="glass-panel" style={{ padding: 20, border: '1px solid rgba(168, 85, 247, 0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg Solving Speed</span>
            <Timer size={18} color="#a855f7" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: avgSeconds > 0 ? '#c084fc' : 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {avgSeconds > 0 ? `⏱️ ${avgSpeedFormatted}` : '--'}
          </div>
          <div style={{ fontSize: '0.75rem', color: avgSeconds > 0 ? '#a855f7' : 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
            <Zap size={12} /> Total Practice: {totalPracticeFormatted}
          </div>
        </div>

        {/* Total Submissions Card */}
        <div className="glass-panel" style={{ padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Submissions</span>
            <Flame size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f8fafc' }}>
            {totalAttempts}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Execution cycles recorded
          </div>
        </div>

        {/* Practice Time */}
        <div className="glass-panel" style={{ padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Coding Practice Time</span>
            <Clock size={18} color="#06b6d4" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f8fafc' }}>
            {totalPracticeFormatted}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Pure editor engagement time
          </div>
        </div>
      </div>

      {/* MULTI-DIMENSIONAL PERFORMANCE BREAKDOWN (Section 1 & Section 6 Requirements) */}
      <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Cpu size={20} color="#818cf8" />
              Multi-Dimensional Coding Evaluation (100 Pts Total)
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '4px 0 0 0' }}>
              Evaluation weights: Correctness (40%), Complexity (20%), Code Quality (15%), Approach (15%), Independent Problem-Solving (10%).
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: '0.75rem', color: '#a5b4fc', background: 'rgba(99, 102, 241, 0.15)', padding: '4px 10px', borderRadius: 6, border: '1px solid rgba(99, 102, 241, 0.3)' }}>
              Avg Hints / Problem: {analyticsData?.average_hints_per_problem != null ? analyticsData.average_hints_per_problem : '0.0'}
            </span>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', background: 'rgba(255, 255, 255, 0.05)', padding: '4px 10px', borderRadius: 6 }}>
              Reliable AST Static Evaluation
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
          {/* Dimension 1: Correctness */}
          <div style={{ background: 'rgba(15, 23, 42, 0.65)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: 10, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
              <div>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#10b981', fontWeight: 700, letterSpacing: '0.05em' }}>Dimension 1</span>
                <h3 style={{ margin: '2px 0 0 0', fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9' }}>Correctness</h3>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                  {dimensionAvgs.correctness != null ? dimensionAvgs.correctness : 0}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 40 pts</span>
              </div>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, Math.max(0, ((dimensionAvgs.correctness || 0) / 40) * 100))}%`,
                background: 'linear-gradient(90deg, #10b981 0%, #34d399 100%)',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
              (Passed/Total) × 40. 0 pts for compilation, syntax errors, or timeouts.
            </p>
          </div>

          {/* Dimension 2: Complexity */}
          <div style={{ background: 'rgba(15, 23, 42, 0.65)', border: '1px solid rgba(168, 85, 247, 0.25)', borderRadius: 10, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
              <div>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#a855f7', fontWeight: 700, letterSpacing: '0.05em' }}>Dimension 2</span>
                <h3 style={{ margin: '2px 0 0 0', fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9' }}>Time & Space</h3>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#c084fc', fontFamily: 'var(--font-mono)' }}>
                  {dimensionAvgs.complexity != null ? dimensionAvgs.complexity : 0}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 20 pts</span>
              </div>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, Math.max(0, ((dimensionAvgs.complexity || 0) / 20) * 100))}%`,
                background: 'linear-gradient(90deg, #9333ea 0%, #c084fc 100%)',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
              Static AST loop nesting, recursive calls, and auxiliary memory checks.
            </p>
          </div>

          {/* Dimension 3: Code Quality */}
          <div style={{ background: 'rgba(15, 23, 42, 0.65)', border: '1px solid rgba(6, 182, 212, 0.25)', borderRadius: 10, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
              <div>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#06b6d4', fontWeight: 700, letterSpacing: '0.05em' }}>Dimension 3</span>
                <h3 style={{ margin: '2px 0 0 0', fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9' }}>Code Quality</h3>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#22d3ee', fontFamily: 'var(--font-mono)' }}>
                  {dimensionAvgs.code_quality != null ? dimensionAvgs.code_quality : 0}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 15 pts</span>
              </div>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, Math.max(0, ((dimensionAvgs.code_quality || 0) / 15) * 100))}%`,
                background: 'linear-gradient(90deg, #0891b2 0%, #22d3ee 100%)',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
              Evaluates naming, modularity, clean error handling, and maintainability.
            </p>
          </div>

          {/* Dimension 4: Approach */}
          <div style={{ background: 'rgba(15, 23, 42, 0.65)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: 10, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
              <div>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#f59e0b', fontWeight: 700, letterSpacing: '0.05em' }}>Dimension 4</span>
                <h3 style={{ margin: '2px 0 0 0', fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9' }}>Approach</h3>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>
                  {dimensionAvgs.approach != null ? dimensionAvgs.approach : 0}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 15 pts</span>
              </div>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, Math.max(0, ((dimensionAvgs.approach || 0) / 15) * 100))}%`,
                background: 'linear-gradient(90deg, #d97706 0%, #fbbf24 100%)',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
              Problem requirements alignment (e.g. strict backtracking check).
            </p>
          </div>

          {/* Dimension 5: Independent Problem-Solving (Hint Usage) */}
          <div style={{ background: 'rgba(15, 23, 42, 0.65)', border: '1px solid rgba(236, 72, 153, 0.25)', borderRadius: 10, padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
              <div>
                <span style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#ec4899', fontWeight: 700, letterSpacing: '0.05em' }}>Dimension 5</span>
                <h3 style={{ margin: '2px 0 0 0', fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9' }}>Independence</h3>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f472b6', fontFamily: 'var(--font-mono)' }}>
                  {dimensionAvgs.independent != null ? dimensionAvgs.independent : 10}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 10 pts</span>
              </div>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, Math.max(0, ((dimensionAvgs.independent || 10) / 10) * 100))}%`,
                background: 'linear-gradient(90deg, #db2777 0%, #f472b6 100%)',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.7rem', color: '#94a3b8', margin: 0, lineHeight: 1.4 }}>
              Hint penalty: 0→10, 1→9, 2→7, 3→4, 4+→1. Deductions do not affect other scores.
            </p>
          </div>
        </div>

        {/* Hint Distribution Breakdown */}
        {analyticsData?.hint_usage_trend && (
          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid rgba(255, 255, 255, 0.07)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Lightbulb size={14} color="#f59e0b" />
              <strong>Hint Usage Distribution:</strong>
            </span>
            <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
              <span>0 Hints (10/10 pts): <strong style={{ color: '#34d399' }}>{analyticsData.hint_usage_trend['0_hints'] || 0}</strong></span>
              <span>1 Hint (9/10 pts): <strong style={{ color: '#a5b4fc' }}>{analyticsData.hint_usage_trend['1_hint'] || 0}</strong></span>
              <span>2 Hints (7/10 pts): <strong style={{ color: '#fbbf24' }}>{analyticsData.hint_usage_trend['2_hints'] || 0}</strong></span>
              <span>3+ Hints (≤4/10 pts): <strong style={{ color: '#f87171' }}>{analyticsData.hint_usage_trend['3_plus_hints'] || 0}</strong></span>
            </div>
          </div>
        )}
      </div>

      {/* AI Learning Report Dropdown */}
      {reportGenerated && (
        <div className="glass-panel-elevated animate-slide-down" style={{ padding: 24, marginBottom: 24, border: '1px solid rgba(16, 185, 129, 0.4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <Sparkles size={20} color="#34d399" />
            <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#34d399' }}>
              AI-Generated Weekly Pedagogical Assessment
            </h3>
          </div>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: '#e2e8f0', marginBottom: 14 }}>
            <strong>Executive Summary:</strong> The student has completed {totalSolved} verified solutions across {totalAttempts} submissions with an average coding score of {averageCodingScore != null ? `${averageCodingScore}/100` : '--'}. Focused practice time: {totalPracticeFormatted}.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: 14, borderRadius: 8 }}>
              <div style={{ color: '#10b981', fontWeight: 600, fontSize: '0.825rem', marginBottom: 4 }}>Recommended Next Focus</div>
              <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>Practice core data structures: Two Pointers, Sliding Window, and Backtracking.</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: 14, borderRadius: 8 }}>
              <div style={{ color: '#8b5cf6', fontWeight: 600, fontSize: '0.825rem', marginBottom: 4 }}>Viva Oral Readiness</div>
              <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>Head to the AI Viva Room after each solve to practice oral defense of space and time complexities.</div>
            </div>
          </div>
        </div>
      )}

      {/* Two Columns: Topic Accuracy & Historical Progression */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 1fr)', gap: 24, marginBottom: 24 }}>
        {/* Topic Mastery & Accuracy Matrix */}
        <div className="glass-panel" style={{ padding: 24 }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BarChart3 size={18} color="#6366f1" />
            Topic-Wise Accuracy & Mastery Matrix
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {Object.entries(topicMastery).map(([topic, score]) => {
              const color = getTopicColor(score);
              const topicStat = analyticsData?.topic_accuracy?.[topic];
              return (
                <div key={topic} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 14, borderRadius: 10, border: '1px solid var(--border-glass)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f1f5f9' }}>{topic}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      {topicStat && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Acc: <strong style={{ color: '#34d399' }}>{topicStat.accuracy_rate}%</strong> ({topicStat.passed_tests}/{topicStat.total_tests})
                        </span>
                      )}
                      <span style={{ fontWeight: 700, fontSize: '0.9rem', color: color }}>
                        {score}% {score >= 80 ? 'Proficient' : score >= 60 ? 'Developing' : score > 0 ? 'Started' : 'Unattempted'}
                      </span>
                    </div>
                  </div>

                  <div style={{ height: 8, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${Math.max(score, 0)}%`,
                      background: score > 0 ? `linear-gradient(90deg, ${color} 0%, #818cf8 100%)` : 'transparent',
                      borderRadius: 4,
                      transition: 'width 0.8s ease'
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Score Progression Trend Bar Chart */}
        <div className="glass-panel" style={{ padding: 24, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
              <TrendingUp size={18} color="#10b981" />
              Score Improvement Over Time
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '0 0 16px 0' }}>
              Chronological trajectory of scored attempts from the relational database ledger.
            </p>

            {scoreHistory.length > 0 ? (
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 160, padding: '10px 0', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', overflowX: 'auto' }}>
                {scoreHistory.slice(0, 15).reverse().map((rec, idx) => {
                  const s = rec.overall_score != null ? Math.round(rec.overall_score) : 0;
                  const barColor = s >= 85 ? '#10b981' : s >= 65 ? '#6366f1' : s > 0 ? '#f59e0b' : '#ef4444';
                  const heightPercent = Math.max(8, s);

                  return (
                    <div 
                      key={idx}
                      title={`${rec.question_id || 'Problem'} - Score: ${s}/100 on ${rec.created_at || 'Recent'}`}
                      onClick={() => handleOpenBreakdown(rec)}
                      style={{
                        flex: '1 0 24px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 4,
                        cursor: 'pointer'
                      }}
                    >
                      <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {s}
                      </span>
                      <div style={{
                        width: '100%',
                        height: `${heightPercent}%`,
                        background: `linear-gradient(180deg, ${barColor} 0%, rgba(15, 23, 42, 0.8) 100%)`,
                        borderRadius: '4px 4px 0 0',
                        border: `1px solid ${barColor}`,
                        transition: 'height 0.5s ease',
                      }} />
                      <span style={{ fontSize: '0.6rem', color: '#64748b', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', width: 28, textAlign: 'center' }}>
                        #{idx + 1}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ padding: '36px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No score history available yet. Run code submissions in the Workspace to track your improvement curve.
              </div>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 12 }}>
            <span>Recent {Math.min(15, scoreHistory.length)} Evaluated Attempts</span>
            <div style={{ display: 'flex', gap: 10 }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: '#10b981' }} /> ≥85
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: '#6366f1' }} /> 65-84
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: 2, background: '#f59e0b' }} /> &lt;65
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* EVALUATED SUBMISSIONS HISTORY LEDGER (Section 6 Requirements) */}
      <div className="glass-panel" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Award size={20} color="#818cf8" />
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
                Evaluated Coding Attempts Ledger
              </h2>
              <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', margin: 0 }}>
                Every completed evaluation saved against user, question, and attempt ID. Click any row to inspect transparent breakdown.
              </p>
            </div>
          </div>

          {/* Filter Chips */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <button
              onClick={() => setScoreFilter('all')}
              style={{
                background: scoreFilter === 'all' ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                color: scoreFilter === 'all' ? '#a5b4fc' : 'var(--text-muted)',
                border: scoreFilter === 'all' ? '1px solid #6366f1' : '1px solid var(--border-glass)',
                padding: '4px 10px',
                borderRadius: 6,
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              All ({scoreHistory.length})
            </button>
            <button
              onClick={() => setScoreFilter('100')}
              style={{
                background: scoreFilter === '100' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                color: scoreFilter === '100' ? '#34d399' : 'var(--text-muted)',
                border: scoreFilter === '100' ? '1px solid #10b981' : '1px solid var(--border-glass)',
                padding: '4px 10px',
                borderRadius: 6,
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Perfect 100
            </button>
            <button
              onClick={() => setScoreFilter('partial')}
              style={{
                background: scoreFilter === 'partial' ? 'rgba(245, 158, 11, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                color: scoreFilter === 'partial' ? '#fbbf24' : 'var(--text-muted)',
                border: scoreFilter === 'partial' ? '1px solid #f59e0b' : '1px solid var(--border-glass)',
                padding: '4px 10px',
                borderRadius: 6,
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Partial
            </button>
            <button
              onClick={() => setScoreFilter('0')}
              style={{
                background: scoreFilter === '0' ? 'rgba(239, 68, 68, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                color: scoreFilter === '0' ? '#f87171' : 'var(--text-muted)',
                border: scoreFilter === '0' ? '1px solid #ef4444' : '1px solid var(--border-glass)',
                padding: '4px 10px',
                borderRadius: 6,
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              0 Pts / Error
            </button>
          </div>
        </div>

        {filteredScores.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filteredScores.map((record, i) => {
              const score = record.overall_score != null ? Math.round(record.overall_score * 10) / 10 : 0;
              const isPerfect = score >= 99.5;
              const isZero = score === 0;
              const badgeColor = isPerfect ? '#10b981' : isZero ? '#ef4444' : '#6366f1';

              return (
                <div
                  key={record.id || record.attempt_id || i}
                  style={{
                    background: 'rgba(15, 23, 42, 0.65)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 10,
                    padding: '12px 16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: 12,
                    transition: 'border-color 0.2s ease, transform 0.2s ease'
                  }}
                  className="hover-card"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    {/* Score Circle Badge */}
                    <div style={{
                      width: 44,
                      height: 44,
                      borderRadius: '50%',
                      background: `rgba(${isPerfect ? '16, 185, 129' : isZero ? '239, 68, 68' : '99, 102, 241'}, 0.15)`,
                      border: `2px solid ${badgeColor}`,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 800, color: badgeColor, fontFamily: 'var(--font-mono)' }}>
                        {score}
                      </span>
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#f8fafc' }}>
                          {record.question_id || 'Problem Submission'}
                        </span>
                        <span style={{
                          fontSize: '0.7rem',
                          padding: '1px 7px',
                          borderRadius: 4,
                          background: 'rgba(255, 255, 255, 0.06)',
                          color: '#94a3b8',
                          fontFamily: 'var(--font-mono)'
                        }}>
                          {record.language || 'python'}
                        </span>
                        <span style={{
                          fontSize: '0.7rem',
                          padding: '1px 7px',
                          borderRadius: 4,
                          background: 'rgba(16, 185, 129, 0.12)',
                          color: '#34d399',
                          fontFamily: 'var(--font-mono)'
                        }}>
                          {record.tests_passed ?? 0} / {record.tests_total ?? 0} tests
                        </span>
                      </div>

                      {/* Dimension mini chips */}
                      <div style={{ display: 'flex', gap: 10, marginTop: 4, fontSize: '0.725rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
                        <span>Correctness: <strong style={{ color: '#34d399' }}>{record.correctness_score ?? '--'}</strong>/40</span>
                        <span>•</span>
                        <span>Complexity: <strong style={{ color: '#c084fc' }}>{record.complexity_score ?? '--'}</strong>/20</span>
                        <span>•</span>
                        <span>Quality: <strong style={{ color: '#22d3ee' }}>{record.quality_score ?? '--'}</strong>/15</span>
                        <span>•</span>
                        <span>Approach: <strong style={{ color: '#fbbf24' }}>{record.approach_score ?? '--'}</strong>/15</span>
                        <span>•</span>
                        <span>Independence: <strong style={{ color: '#f472b6' }}>{record.independent_score != null ? record.independent_score : 10}</strong>/10 ({record.unique_hints_used ?? 0} {record.unique_hints_used === 1 ? 'hint' : 'hints'})</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{ textAlign: 'right', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {record.coding_time_seconds != null && record.coding_time_seconds > 0 && (
                        <div>⏱️ {formatSecs(record.coding_time_seconds)} coding</div>
                      )}
                      {record.execution_time_seconds != null && (
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>
                          ⚡ {record.execution_time_seconds}s exec
                        </div>
                      )}
                      <div style={{ fontSize: '0.675rem', opacity: 0.75 }}>
                        {record.created_at || 'Recent'}
                      </div>
                    </div>

                    <button
                      onClick={() => handleOpenBreakdown(record)}
                      className="btn"
                      style={{
                        padding: '6px 12px',
                        fontSize: '0.775rem',
                        background: 'rgba(99, 102, 241, 0.18)',
                        color: '#c7d2fe',
                        border: '1px solid rgba(99, 102, 241, 0.35)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4
                      }}
                    >
                      <span>Breakdown</span>
                      <ChevronRight size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{
            padding: 32,
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.85rem',
            background: 'rgba(15, 23, 42, 0.4)',
            borderRadius: 8
          }}>
            {isLoadingScores ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <RefreshCw size={16} className="animate-spin" />
                <span>Loading relational score records...</span>
              </div>
            ) : (
              <div>No evaluated attempts matching current filter. Complete a problem run in the Workspace to generate scores.</div>
            )}
          </div>
        )}
      </div>

      {/* QUESTION-LEVEL SOLVING TIME & PRACTICE HISTORY (Section 7 Requirements) */}
      <div className="glass-panel" style={{ padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18, flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Timer size={20} color="#a855f7" />
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
              Individual Question Solving Times & Practice History
            </h2>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Average solving duration: <strong style={{ color: avgSeconds > 0 ? '#c084fc' : 'var(--text-muted)' }}>{avgSpeedFormatted}</strong>
          </div>
        </div>

        {/* Individual Solved Problems Table / List */}
        {solvingEntries.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14, marginBottom: 20 }}>
            {solvingEntries.map(([pid, record]) => {
              const secs = record.time_spent_seconds || 0;
              const formattedTime = record.time_spent_formatted || formatSecs(secs);
              const speedTag = secs < 180 ? '⚡ Rapid' : secs < 600 ? 'Optimal Pace' : 'Deep Exploration';
              const speedColor = secs < 180 ? '#34d399' : secs < 600 ? '#60a5fa' : '#fbbf24';

              return (
                <div 
                  key={pid}
                  style={{
                    background: 'rgba(15, 23, 42, 0.75)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 10,
                    padding: '14px 16px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: 10
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#f1f5f9' }}>
                      {pid}
                    </span>
                    <span style={{
                      fontSize: '0.7rem',
                      padding: '2px 8px',
                      borderRadius: 12,
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      border: '1px solid rgba(16, 185, 129, 0.3)'
                    }}>
                      Completed
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Solving Time</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
                        ⏱️ {formattedTime}
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Pace</div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: speedColor }}>
                        {speedTag}
                      </span>
                    </div>
                  </div>

                  {record.tab_switch_count !== undefined && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                      <span>Tab Switches:</span>
                      <strong style={{ color: record.tab_switch_count > 0 ? '#f59e0b' : '#34d399', fontFamily: 'var(--font-mono)' }}>
                        {record.tab_switch_count}
                      </strong>
                    </div>
                  )}

                  <div style={{ fontSize: '0.725rem', color: '#94a3b8', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: 8 }}>
                    Completed on {record.completed_at || 'Recent session'}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{
            background: 'rgba(15, 23, 42, 0.5)',
            border: '1px dashed var(--border-glass)',
            borderRadius: 10,
            padding: 24,
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.875rem',
            marginBottom: 20
          }}>
            <Timer size={24} style={{ margin: '0 auto 8px auto', opacity: 0.6 }} />
            No question-level solving records yet. Start a timed practice session in the Workspace to log your solving speed!
          </div>
        )}

        {/* Recent Session Logs Feed */}
        {(studentProfile?.activity_log || []).length > 0 ? (
          <div>
            <h3 style={{ fontSize: '0.925rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 10 }}>
              Recent Practice Sessions & Submission Stream
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {studentProfile.activity_log.slice(0, 8).map((act, i) => {
                const isSolved = act.action === 'Solved';
                const isAbandoned = act.action === 'Abandoned Attempt';
                return (
                  <div 
                    key={i}
                    style={{
                      background: 'rgba(15, 23, 42, 0.5)',
                      border: '1px solid var(--border-glass)',
                      borderRadius: 8,
                      padding: '10px 14px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: 8,
                      fontSize: '0.825rem'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      {isSolved ? (
                        <CheckCircle2 size={16} color="#10b981" />
                      ) : isAbandoned ? (
                        <Flag size={16} color="#fb7185" />
                      ) : (
                        <Play size={16} color="#f59e0b" />
                      )}
                      <div>
                        <strong style={{ color: isSolved ? '#34d399' : isAbandoned ? '#fb7185' : '#f8fafc' }}>
                          {act.action}:
                        </strong>{' '}
                        <span style={{ color: '#cbd5e1' }}>{act.problem}</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                      {(act.time_spent || act.time_spent_seconds) && (
                        <span style={{
                          fontFamily: 'var(--font-mono)',
                          fontSize: '0.775rem',
                          color: '#c084fc',
                          background: 'rgba(192, 132, 252, 0.12)',
                          padding: '2px 8px',
                          borderRadius: 6,
                          border: '1px solid rgba(192, 132, 252, 0.25)'
                        }}>
                          ⏱️ {act.time_spent || formatSecs(act.time_spent_seconds)}
                        </span>
                      )}
                      {act.tab_switch_count !== undefined && act.tab_switch_count > 0 && (
                        <span style={{
                          fontFamily: 'var(--font-mono)',
                          fontSize: '0.75rem',
                          color: '#f59e0b',
                          background: 'rgba(245, 158, 11, 0.12)',
                          padding: '2px 8px',
                          borderRadius: 6,
                          border: '1px solid rgba(245, 158, 11, 0.25)'
                        }}>
                          🔄 {act.tab_switch_count} tab {act.tab_switch_count === 1 ? 'switch' : 'switches'}
                        </span>
                      )}
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {act.timestamp}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div style={{
            padding: 16,
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.825rem',
            background: 'rgba(15, 23, 42, 0.4)',
            borderRadius: 8
          }}>
            No practice sessions recorded yet.
          </div>
        )}
      </div>

      {/* Score Breakdown Modal */}
      {showScoreModal && selectedScoreRecord && (
        <ScoreBreakdownModal 
          scoreData={selectedScoreRecord}
          onClose={() => {
            setShowScoreModal(false);
            setSelectedScoreRecord(null);
          }}
        />
      )}
    </div>
  );
}
