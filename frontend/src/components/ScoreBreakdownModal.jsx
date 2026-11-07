import React from 'react';
import { 
  X, 
  Award, 
  CheckCircle2, 
  Clock, 
  Zap, 
  Lightbulb, 
  Sparkles, 
  Cpu, 
  ShieldCheck, 
  Code2, 
  AlertCircle,
  HelpCircle,
  ArrowRight,
  HelpCircle as HintIcon,
  Layers
} from 'lucide-react';

export default function ScoreBreakdownModal({ scoreRecord, onClose }) {
  if (!scoreRecord) return null;

  const score = scoreRecord.overall_score != null ? Math.round(scoreRecord.overall_score * 10) / 10 : 0;
  const breakdown = scoreRecord.breakdown || {};
  const feedback = scoreRecord.feedback || {};
  const strengths = feedback.strengths || [];
  const suggestions = feedback.improvement_suggestions || [];
  const perf = scoreRecord.performance || {};
  const evaluator = scoreRecord.evaluator || {};
  const uniqueHintsUsed = scoreRecord.unique_hints_used ?? (breakdown.independent?.unique_hints_used ?? 0);
  const independentScore = breakdown.independent?.points_earned ?? (scoreRecord.independent_score ?? 10);
  const memoryUsage = perf.memory_usage_mb || scoreRecord.memory_usage_mb;

  const isPending = scoreRecord.is_empty_submission || scoreRecord.scoring_status === 'not_evaluated';
  const getScoreColor = (val) => {
    if (isPending) return '#94a3b8';
    if (val >= 85) return '#10b981'; // Emerald
    if (val >= 70) return '#38bdf8'; // Cyan
    if (val >= 50) return '#f59e0b'; // Amber
    return '#f43f5e'; // Rose
  };

  const scoreColor = getScoreColor(score);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(5, 10, 24, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: 16
    }}>
      <div 
        className="glass-panel-elevated animate-scale-up"
        style={{
          width: '100%',
          maxWidth: 820,
          maxHeight: '92vh',
          overflowY: 'auto',
          borderRadius: 16,
          border: '1px solid rgba(56, 189, 248, 0.25)',
          background: 'linear-gradient(145deg, #0f172a 0%, #0a0f1d 100%)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 30px rgba(56, 189, 248, 0.15)',
          padding: 24,
          position: 'relative'
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '50%',
            width: 34,
            height: 34,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#94a3b8',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = '#94a3b8'; e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'; }}
          aria-label="Close modal"
        >
          <X size={18} />
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, marginBottom: 20, paddingRight: 40 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 12,
            background: `linear-gradient(135deg, ${scoreColor}22, ${scoreColor}44)`,
            border: `1px solid ${scoreColor}66`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: scoreColor,
            flexShrink: 0
          }}>
            <Award size={26} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: '#f8fafc', fontFamily: 'var(--font-heading)' }}>
                {scoreRecord.question_title || scoreRecord.question_id || 'Coding Evaluation'}
              </h2>
              <span style={{
                fontSize: '0.75rem',
                textTransform: 'uppercase',
                padding: '2px 8px',
                borderRadius: 6,
                background: 'rgba(56, 189, 248, 0.12)',
                color: '#38bdf8',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                fontWeight: 600,
                fontFamily: 'var(--font-mono)'
              }}>
                {scoreRecord.language || 'python'}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>
              Attempt ID: <code style={{ color: '#cbd5e1' }}>{scoreRecord.attempt_id}</code> • {scoreRecord.created_at_ist || scoreRecord.created_at || 'Recent Evaluation'}
            </div>
          </div>
        </div>

        {/* Score Overview Banner */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: 14,
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 12,
          padding: 16,
          marginBottom: 20,
          alignItems: 'center'
        }}>
          {/* Main Score Metric */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              border: `3px solid ${scoreColor}`,
              boxShadow: `0 0 20px ${scoreColor}44`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(10, 15, 29, 0.8)',
              flexShrink: 0
            }}>
              <span style={{ fontSize: '1.4rem', fontWeight: 800, color: scoreColor, lineHeight: 1, fontFamily: 'var(--font-heading)' }}>
                {score}
              </span>
              <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                / 100
              </span>
            </div>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc' }}>
                Coding Score {isPending ? '(Not Evaluated)' : (scoreRecord.is_provisional ? '(Provisional)' : '')}
              </div>
              <div style={{ fontSize: '0.725rem', color: isPending ? '#cbd5e1' : 'var(--text-muted)' }}>
                {isPending ? 'Pending Code Submission' : (scoreRecord.is_renormalized ? '⚖️ Renormalized' : '5-Component Weighted')}
              </div>
            </div>
          </div>

          {/* Test Cases Counter */}
          <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)', paddingLeft: 12 }}>
            <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Test Cases</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', fontFamily: 'var(--font-mono)' }}>
              {scoreRecord.passed_count ?? 0} / {scoreRecord.total_count ?? 0}
            </div>
            <div style={{ fontSize: '0.7rem', color: scoreRecord.passed_count === scoreRecord.total_count ? '#34d399' : '#fb7185' }}>
              {scoreRecord.passed_count === scoreRecord.total_count ? '✓ 100% Passed' : 'Partial / Failing'}
            </div>
          </div>

          {/* Independent Solving (Hint Usage) */}
          <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)', paddingLeft: 12 }}>
            <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Independent Solving</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: independentScore >= 9 ? '#34d399' : independentScore >= 7 ? '#818cf8' : '#fbbf24', fontFamily: 'var(--font-mono)' }}>
              {independentScore} / 10 pts
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              💡 {uniqueHintsUsed} {uniqueHintsUsed === 1 ? 'hint' : 'hints'} used
            </div>
          </div>

          {/* Timing & Telemetry */}
          <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)', paddingLeft: 12 }}>
            <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Timing Telemetry</div>
            <div style={{ fontSize: '0.775rem', color: '#cbd5e1', marginTop: 2 }}>
              ⏱️ Coding: <strong style={{ color: '#38bdf8' }}>{perf.coding_time_formatted || `${scoreRecord.coding_time_seconds || 0}s`}</strong>
            </div>
            <div style={{ fontSize: '0.775rem', color: '#cbd5e1', marginTop: 2 }}>
              ⚡ Exec: <strong style={{ color: '#c084fc' }}>{perf.execution_time_ms || scoreRecord.execution_time_ms || 0} ms</strong>
              {memoryUsage ? <span style={{ marginLeft: 6, color: '#94a3b8' }}>({memoryUsage}MB)</span> : null}
            </div>
          </div>
        </div>

        {/* 5 Evaluation Dimensions Grid */}
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Cpu size={16} color="#38bdf8" />
          5 Evaluation Dimensions (Sum = 100 Points)
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 12, marginBottom: 20 }}>
          {/* 1. Correctness (40 pts) */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                1. Correctness
              </span>
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: (breakdown.correctness?.ratio || 0) >= 1.0 ? '#34d399' : (breakdown.correctness?.ratio || 0) > 0 ? '#fbbf24' : '#fb7185',
                fontFamily: 'var(--font-mono)'
              }}>
                {breakdown.correctness?.points_earned ?? scoreRecord.correctness_score ?? 0} / {breakdown.correctness?.max_points ?? 40} pts
              </span>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${((breakdown.correctness?.ratio ?? ((scoreRecord.passed_count || 0) / Math.max(1, scoreRecord.total_count || 1)))) * 100}%`,
                background: (breakdown.correctness?.ratio || 0) >= 1.0 ? '#10b981' : '#f59e0b',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
              {breakdown.correctness?.notes || `(Passed Tests / Total Evaluated Tests) × 40. ${scoreRecord.passed_count ?? 0}/${scoreRecord.total_count ?? 0} passed.`}
            </p>
          </div>

          {/* 2. Complexity Analysis (20 pts) */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(168, 85, 247, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                2. Complexity Analysis
              </span>
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: breakdown.complexity?.is_available !== false ? '#c084fc' : 'var(--text-muted)',
                fontFamily: 'var(--font-mono)'
              }}>
                {breakdown.complexity?.is_available !== false
                  ? `${breakdown.complexity?.points_earned ?? scoreRecord.complexity_score ?? 0} / ${breakdown.complexity?.max_points ?? 20} pts` 
                  : 'N/A (Renormalized)'}
              </span>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: breakdown.complexity?.is_available !== false ? `${(breakdown.complexity?.ratio || 0) * 100}%` : '0%',
                background: '#a855f7',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
              {breakdown.complexity?.notes || 'Static AST & Big-O algorithmic complexity evaluation.'}
            </p>
          </div>

          {/* 3. Code Quality (15 pts) */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(6, 182, 212, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                3. Code Quality
              </span>
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: '#22d3ee',
                fontFamily: 'var(--font-mono)'
              }}>
                {breakdown.quality?.is_available !== false
                  ? `${breakdown.quality?.points_earned ?? scoreRecord.quality_score ?? 0} / ${breakdown.quality?.max_points ?? 15} pts` 
                  : 'N/A (Renormalized)'}
              </span>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${(breakdown.quality?.ratio || 0) * 100}%`,
                background: '#06b6d4',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
              {breakdown.quality?.notes || 'Readability, function modularity, naming, and language idioms.'}
            </p>
          </div>

          {/* 4. Problem-Solving Approach (15 pts) */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                4. Problem-Solving Approach
              </span>
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: '#fbbf24',
                fontFamily: 'var(--font-mono)'
              }}>
                {breakdown.approach?.is_available !== false
                  ? `${breakdown.approach?.points_earned ?? scoreRecord.approach_score ?? 0} / ${breakdown.approach?.max_points ?? 15} pts` 
                  : 'N/A (Renormalized)'}
              </span>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${(breakdown.approach?.ratio || 0) * 100}%`,
                background: '#f59e0b',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
              {breakdown.approach?.notes || 'Algorithmic alignment with problem constraints (e.g. Backtracking, Recursion).'}
            </p>
          </div>

          {/* 5. Independent Problem-Solving (10 pts) */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.65)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                5. Independent Solving
              </span>
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: independentScore >= 9 ? '#34d399' : independentScore >= 7 ? '#818cf8' : '#fbbf24',
                fontFamily: 'var(--font-mono)'
              }}>
                {independentScore} / 10 pts
              </span>
            </div>
            <div style={{ height: 6, background: 'rgba(255, 255, 255, 0.08)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
              <div style={{
                height: '100%',
                width: `${(independentScore / 10) * 100}%`,
                background: 'linear-gradient(90deg, #6366f1 0%, #818cf8 100%)',
                borderRadius: 3
              }} />
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
              {uniqueHintsUsed === 0 && '0 hints used (10/10). Independent formulation without assistance.'}
              {uniqueHintsUsed === 1 && '1 unique hint used (9/10). Strong self-direction.'}
              {uniqueHintsUsed === 2 && '2 unique hints used (7/10). Good algorithmic progress.'}
              {uniqueHintsUsed === 3 && '3 unique hints used (4/10). Required multiple hints.'}
              {uniqueHintsUsed >= 4 && `${uniqueHintsUsed} unique hints used (1/10). High hint dependence.`}
            </p>
          </div>
        </div>

        {/* Strengths & Improvement Suggestions */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14, marginBottom: 20 }}>
          {/* Strengths */}
          <div style={{
            background: 'rgba(16, 185, 129, 0.06)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#34d399', fontWeight: 700, fontSize: '0.85rem', marginBottom: 8 }}>
              <CheckCircle2 size={16} /> Key Strengths
            </div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.8rem', color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {strengths.map((str, idx) => (
                <li key={idx}>{str}</li>
              ))}
            </ul>
          </div>

          {/* Suggestions */}
          <div style={{
            background: 'rgba(245, 158, 11, 0.06)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: 10,
            padding: 14
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#fbbf24', fontWeight: 700, fontSize: '0.85rem', marginBottom: 8 }}>
              <Lightbulb size={16} /> Actionable Improvement Guidance
            </div>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.8rem', color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {suggestions.map((sug, idx) => (
                <li key={idx}>{sug}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Evaluator Attribution & Limitations */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.5)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: 8,
          padding: '10px 14px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 10,
          fontSize: '0.75rem',
          color: 'var(--text-muted)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <ShieldCheck size={14} color="#38bdf8" />
            <span>Evaluator Engine: <strong style={{ color: '#cbd5e1' }}>{evaluator.evaluator_label || scoreRecord.evaluator_type || 'Automated Static Evaluation'}</strong></span>
          </div>
          <div style={{ maxWidth: 450, fontSize: '0.725rem', opacity: 0.85 }}>
            {evaluator.limitations || 'Score derived from deterministic AST structure, hint usage curves, and automated test executions.'}
          </div>
        </div>
      </div>
    </div>
  );
}
