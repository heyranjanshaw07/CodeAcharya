import React, { useState } from 'react';
import { 
  Award, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Download, 
  RotateCcw, 
  ArrowLeft, 
  ShieldAlert, 
  Sparkles,
  FileText,
  ChevronRight,
  Code
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function AIAssessmentResults({
  summary,
  assessment,
  onStartNewAssessment,
  onGoHome
}) {
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [downloadError, setDownloadError] = useState('');

  // Fire celebratory confetti on high scores
  React.useEffect(() => {
    if (summary && summary.overall_score >= 60) {
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (err) {
        // ignore if canvas-confetti unsupported
      }
    }
  }, [summary]);

  const formatTime = (secs) => {
    const m = Math.floor((secs || 0) / 60);
    const s = (secs || 0) % 60;
    if (m >= 60) {
      const h = Math.floor(m / 60);
      const remM = m % 60;
      return `${h}h ${remM}m ${s}s`;
    }
    return `${m}m ${s}s`;
  };

  const handleDownloadPdf = async () => {
    if (!summary?.assessment_id) return;
    setIsDownloadingPdf(true);
    setDownloadError('');

    try {
      const token = localStorage.getItem('codeacharya_auth_token');
      const res = await fetch(`/api/ai-mode/report/pdf/${summary.assessment_id}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });

      if (!res.ok) {
        throw new Error('Failed to generate PDF performance report');
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CodeAcharya_AI_Assessment_${summary.assessment_id.slice(-6)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setDownloadError(err.message || 'PDF Download failed');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const score = summary?.overall_score || 0;
  const scoreColor = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '36px 20px' }}>
      {/* Top Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        borderRadius: 20,
        padding: '32px 36px',
        marginBottom: 28,
        textAlign: 'center',
        position: 'relative'
      }}>
        <div style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px auto',
          boxShadow: '0 0 25px rgba(99, 102, 241, 0.5)'
        }}>
          <Award size={32} color="#fff" />
        </div>

        <h1 style={{
          margin: 0,
          fontSize: '2rem',
          fontWeight: 800,
          fontFamily: 'var(--font-heading)',
          color: '#ffffff',
          marginBottom: 6
        }}>
          Assessment Completed
        </h1>
        <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Official Evaluation for {assessment?.topic} ({assessment?.difficulty} • {assessment?.language?.toUpperCase()})
        </p>
      </div>

      {/* Main Scorecard Metrics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: 16,
        marginBottom: 32
      }}>
        {/* Overall Score */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 22,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Overall Score
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: scoreColor, fontFamily: 'var(--font-heading)' }}>
            {score.toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Graded out of 100
          </div>
        </div>

        {/* Problems Solved */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 22,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Problems Solved
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#818cf8', fontFamily: 'var(--font-heading)' }}>
            {summary?.passed_count || 0} / {summary?.total_count || 0}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            All test cases passed
          </div>
        </div>

        {/* Time Taken */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 22,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Time Taken
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-heading)' }}>
            {formatTime(summary?.time_taken_seconds)}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Total active assessment time
          </div>
        </div>

        {/* Proctoring Focus */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 22,
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>
            Tab Switches
          </div>
          <div style={{
            fontSize: '2.4rem',
            fontWeight: 800,
            color: (summary?.tab_switch_count || 0) > 2 ? '#ef4444' : '#10b981',
            fontFamily: 'var(--font-heading)'
          }}>
            {summary?.tab_switch_count || 0}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
            {(summary?.tab_switch_count || 0) === 0 ? 'High Focus Maintained' : 'Focus switch events recorded'}
          </div>
        </div>
      </div>

      {/* Question Breakdown Table */}
      <div style={{
        background: 'rgba(15, 23, 42, 0.65)',
        border: '1px solid var(--border-glass)',
        borderRadius: 16,
        padding: 24,
        marginBottom: 32
      }}>
        <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', marginBottom: 16 }}>
          Problem Breakdown &amp; Performance
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {(assessment?.questions || []).map((q, idx) => {
            return (
              <div
                key={q.id}
                style={{
                  background: 'rgba(30, 41, 59, 0.45)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 12,
                  padding: '14px 18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 12
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: 'rgba(99, 102, 241, 0.2)',
                    color: '#818cf8',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '0.85rem'
                  }}>
                    Q{idx + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.95rem' }}>
                      {q.title}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {q.subtopic || q.topic} • {q.difficulty}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <span style={{
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    padding: '3px 10px',
                    borderRadius: 6,
                    background: 'rgba(99, 102, 241, 0.15)',
                    color: '#a5b4fc'
                  }}>
                    {assessment.language.toUpperCase()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {downloadError && (
        <div style={{ color: '#f87171', textAlign: 'center', marginBottom: 16, fontSize: '0.85rem' }}>
          {downloadError}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
        flexWrap: 'wrap'
      }}>
        {/* PDF Download Button */}
        <button
          type="button"
          onClick={handleDownloadPdf}
          disabled={isDownloadingPdf}
          style={{
            padding: '12px 28px',
            borderRadius: 12,
            border: 'none',
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            color: '#fff',
            fontWeight: 700,
            fontSize: '0.92rem',
            cursor: isDownloadingPdf ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
          }}
        >
          <Download size={16} />
          <span>{isDownloadingPdf ? 'Generating PDF Report...' : 'Download Official PDF Report'}</span>
        </button>

        {/* Start New Assessment */}
        <button
          type="button"
          onClick={onStartNewAssessment}
          style={{
            padding: '12px 24px',
            borderRadius: 12,
            border: '1px solid var(--border-glass)',
            background: 'rgba(30, 41, 59, 0.8)',
            color: '#cbd5e1',
            fontWeight: 600,
            fontSize: '0.92rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}
        >
          <RotateCcw size={16} />
          <span>New Assessment</span>
        </button>

        {/* Return to Workspace */}
        <button
          type="button"
          onClick={onGoHome}
          style={{
            padding: '12px 24px',
            borderRadius: 12,
            border: '1px solid var(--border-glass)',
            background: 'transparent',
            color: '#94a3b8',
            fontWeight: 600,
            fontSize: '0.92rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}
        >
          <ArrowLeft size={16} />
          <span>Return to Workspace</span>
        </button>
      </div>
    </div>
  );
}
