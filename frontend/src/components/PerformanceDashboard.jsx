import React, { useState, useEffect, useMemo } from 'react';
import { 
  TrendingUp, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Lightbulb, 
  EyeOff, 
  BarChart2, 
  Calendar, 
  Filter, 
  Search, 
  Download, 
  FileText, 
  ChevronRight, 
  Sparkles, 
  GraduationCap, 
  ShieldAlert, 
  ArrowLeft, 
  RefreshCw, 
  Terminal, 
  Award, 
  Cpu, 
  Layers, 
  Code2, 
  HelpCircle,
  ExternalLink,
  ChevronDown,
  X
} from 'lucide-react';

const PRESET_DATE_FILTERS = [
  { id: 'today', label: 'Today' },
  { id: 'last_7_days', label: 'Last 7 Days' },
  { id: 'last_30_days', label: 'Last 30 Days' },
  { id: 'this_month', label: 'This Month' },
  { id: 'previous_month', label: 'Previous Month' },
  { id: 'custom', label: 'Custom Range' },
  { id: 'all', label: 'All Time' }
];

export default function PerformanceDashboard({ user, onSelectProblem, onBack }) {
  // Date filter states
  const [dateFilter, setDateFilter] = useState('last_30_days');
  const [customStartDate, setCustomStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 29);
    return d.toISOString().split('T')[0];
  });
  const [customEndDate, setCustomEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0];
  });

  // Data fetching states
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  
  // Table search & filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [topicFilter, setTopicFilter] = useState('all');
  const [sortField, setSortField] = useState('date_desc');

  // Modal states
  const [selectedAttempt, setSelectedAttempt] = useState(null);
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [pdfError, setPdfError] = useState('');

  // PDF report configuration
  const [pdfDateFilter, setPdfDateFilter] = useState('last_30_days');
  const [pdfStartDate, setPdfStartDate] = useState(() => customStartDate);
  const [pdfEndDate, setPdfEndDate] = useState(() => customEndDate);
  const [pdfIncludeTabs, setPdfIncludeTabs] = useState(true);
  const [pdfIncludeViva, setPdfIncludeViva] = useState(true);
  const [pdfViewMode, setPdfViewMode] = useState('detailed');

  // Fetch dashboard data whenever date filter changes
  useEffect(() => {
    fetchDashboardData(dateFilter, customStartDate, customEndDate);
  }, [dateFilter]);

  const fetchDashboardData = async (filter, start = null, end = null) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      let url = `/api/performance/dashboard?date_filter=${encodeURIComponent(filter)}`;
      if (filter === 'custom' && start && end) {
        url += `&start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`;
      }

      const res = await fetch(url);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to fetch performance dashboard.');
      }
      const data = await res.json();
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard:', err);
      setErrorMessage(err.message || 'Error loading performance records. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyCustomDateFilter = () => {
    if (!customStartDate || !customEndDate) {
      setErrorMessage('Please select both start date and end date.');
      return;
    }
    if (customStartDate > customEndDate) {
      setErrorMessage('Start date cannot be after end date.');
      return;
    }
    fetchDashboardData('custom', customStartDate, customEndDate);
  };

  // PDF Download Handler (Strictly PDF-Only)
  const handleDownloadPdf = async () => {
    setIsGeneratingPdf(true);
    setPdfError('');
    try {
      if (pdfDateFilter === 'custom') {
        if (!pdfStartDate || !pdfEndDate) {
          throw new Error('Please select both start and end dates for the custom report period.');
        }
        if (pdfStartDate > pdfEndDate) {
          throw new Error('Start date cannot be later than end date.');
        }
      }

      const payload = {
        date_filter: pdfDateFilter,
        start_date: pdfDateFilter === 'custom' ? pdfStartDate : null,
        end_date: pdfDateFilter === 'custom' ? pdfEndDate : null,
        include_tab_switches: pdfIncludeTabs,
        include_viva: pdfIncludeViva,
        view_mode: pdfViewMode
      };

      const res = await fetch('/api/reports/pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Server encountered an issue generating the PDF.');
      }

      // Receive binary blob and initiate direct file download
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      const dateTag = new Date().toISOString().split('T')[0];
      link.download = `CodeAcharya_Performance_Report_${user?.full_name?.replace(/\s+/g, '_') || 'Student'}_${dateTag}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);

      setIsPdfModalOpen(false);
    } catch (err) {
      console.error('PDF generation error:', err);
      setPdfError(err.message || 'PDF report generation failed. Please verify dates and retry.');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const summary = dashboardData?.summary || {};
  const attempts = dashboardData?.questions_performance || [];
  const charts = dashboardData?.charts || {};
  const reportingPeriod = dashboardData?.reporting_period_label || 'Selected Period';

  // Topics list for filtering
  const availableTopics = useMemo(() => {
    const set = new Set();
    attempts.forEach(a => { if (a.topic) set.add(a.topic); });
    return Array.from(set).sort();
  }, [attempts]);

  // Filtered & sorted question attempts table
  const filteredAttempts = useMemo(() => {
    return attempts
      .filter(a => {
        if (statusFilter !== 'all') {
          if (statusFilter === 'completed' && !a.is_completed) return false;
          if (statusFilter === 'failed' && a.attempt_status !== 'failed') return false;
          if (statusFilter === 'abandoned' && a.attempt_status !== 'abandoned') return false;
        }
        if (topicFilter !== 'all' && a.topic !== topicFilter) return false;
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchTitle = (a.question_title || '').toLowerCase().includes(q);
          const matchId = (a.question_id || '').toLowerCase().includes(q);
          const matchTopic = (a.topic || '').toLowerCase().includes(q);
          const matchLang = (a.language || '').toLowerCase().includes(q);
          if (!matchTitle && !matchId && !matchTopic && !matchLang) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortField === 'date_desc') return (b.start_time || '').localeCompare(a.start_time || '');
        if (sortField === 'date_asc') return (a.start_time || '').localeCompare(b.start_time || '');
        if (sortField === 'score_desc') return (b.overall_score || 0) - (a.overall_score || 0);
        if (sortField === 'score_asc') return (a.overall_score || 0) - (b.overall_score || 0);
        if (sortField === 'duration_desc') return (b.coding_duration_seconds || 0) - (a.coding_duration_seconds || 0);
        if (sortField === 'duration_asc') return (a.coding_duration_seconds || 0) - (b.coding_duration_seconds || 0);
        if (sortField === 'switches_desc') return (b.tab_switch_count || 0) - (a.tab_switch_count || 0);
        return 0;
      });
  }, [attempts, statusFilter, topicFilter, searchQuery, sortField]);

  return (
    <div style={{ maxWidth: 1600, margin: '0 auto', padding: '24px 24px 60px' }}>
      
      {/* Top Header & Report Download Trigger */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between', 
        flexWrap: 'wrap', 
        gap: 16,
        marginBottom: 20
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {onBack && (
            <button
              onClick={onBack}
              className="btn btn-secondary"
              style={{ padding: '8px 12px' }}
              title="Return to previous screen"
            >
              <ArrowLeft size={16} />
            </button>
          )}
          <div style={{
            width: 46,
            height: 46,
            borderRadius: 14,
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 25px rgba(6, 182, 212, 0.4)'
          }}>
            <TrendingUp size={24} color="#fff" />
          </div>
          <div>
            <h1 style={{ 
              fontFamily: 'var(--font-heading)',
              fontSize: '1.6rem', 
              fontWeight: 800, 
              margin: 0,
              letterSpacing: '-0.02em',
              background: 'linear-gradient(90deg, #ffffff 0%, #93c5fd 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              My Performance Dashboard
            </h1>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Detailed question analytics, Coding Scores, time tracking, hints, and PDF reporting in IST (Asia/Kolkata)
            </p>
          </div>
        </div>

        {/* Prominent PDF Report Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={() => {
              setPdfDateFilter(dateFilter);
              setPdfStartDate(customStartDate);
              setPdfEndDate(customEndDate);
              setIsPdfModalOpen(true);
            }}
            className="btn btn-primary"
            style={{
              padding: '10px 22px',
              fontSize: '0.9rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
              boxShadow: '0 0 20px rgba(79, 70, 229, 0.4)',
              border: 'none',
              borderRadius: 10
            }}
            title="Configure and download a multi-page PDF performance report"
          >
            <Download size={18} />
            <span>Download PDF Report</span>
          </button>
        </div>
      </div>

      {/* Date Filtering Panel */}
      <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14 }}>
          {/* Preset Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginRight: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
              <Calendar size={14} /> Timeframe:
            </span>
            {PRESET_DATE_FILTERS.map(f => (
              <button
                key={f.id}
                onClick={() => setDateFilter(f.id)}
                style={{
                  padding: '6px 12px',
                  borderRadius: 8,
                  fontSize: '0.8rem',
                  fontWeight: dateFilter === f.id ? 700 : 500,
                  border: '1px solid',
                  borderColor: dateFilter === f.id ? '#06b6d4' : 'var(--border-glass)',
                  background: dateFilter === f.id ? 'rgba(6, 182, 212, 0.2)' : 'rgba(15, 23, 42, 0.5)',
                  color: dateFilter === f.id ? '#38bdf8' : 'var(--text-muted)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Current Period Badge */}
          <div style={{
            fontSize: '0.8rem',
            padding: '5px 12px',
            borderRadius: 6,
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            color: '#a5b4fc',
            fontWeight: 600
          }}>
            Active Period: <strong>{reportingPeriod}</strong>
          </div>
        </div>

        {/* Custom Date Range Picker Fields */}
        {dateFilter === 'custom' && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 12, 
            marginTop: 14, 
            paddingTop: 12, 
            borderTop: '1px solid var(--border-glass)',
            flexWrap: 'wrap' 
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>From (IST):</label>
              <input
                type="date"
                value={customStartDate}
                onChange={(e) => setCustomStartDate(e.target.value)}
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 6,
                  padding: '5px 10px',
                  color: '#fff',
                  fontSize: '0.8rem'
                }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>To (IST):</label>
              <input
                type="date"
                value={customEndDate}
                onChange={(e) => setCustomEndDate(e.target.value)}
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 6,
                  padding: '5px 10px',
                  color: '#fff',
                  fontSize: '0.8rem'
                }}
              />
            </div>

            <button
              onClick={handleApplyCustomDateFilter}
              className="btn btn-primary"
              style={{ padding: '6px 14px', fontSize: '0.8rem' }}
            >
              Apply Filter
            </button>
          </div>
        )}
      </div>

      {/* Error Message Banner */}
      {errorMessage && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          borderRadius: 8,
          padding: '12px 16px',
          color: '#fca5a5',
          fontSize: '0.85rem',
          marginBottom: 20,
          display: 'flex',
          alignItems: 'center',
          gap: 10
        }}>
          <AlertTriangle size={18} color="#ef4444" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Loading Skeleton / Spinner */}
      {isLoading ? (
        <div style={{ padding: '80px 20px', textAlign: 'center' }}>
          <RefreshCw size={36} color="#6366f1" style={{ animation: 'spin 1s linear infinite', marginBottom: 12 }} />
          <div style={{ fontSize: '0.95rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            Loading genuine performance statistics...
          </div>
        </div>
      ) : (
        <>
          {/* Summary Cards Grid (11 Required Metrics) */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
            gap: 14,
            marginBottom: 24
          }}>
            {/* Card 1: Unique Questions Solved */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #10b981' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Unique Solved
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981', display: 'flex', alignItems: 'baseline', gap: 6 }}>
                {summary.total_unique_solved || 0}
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>problems</span>
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Fully verified test pass
              </div>
            </div>

            {/* Card 2: Total Coding Attempts */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #6366f1' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Coding Attempts
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#818cf8', display: 'flex', alignItems: 'baseline', gap: 6 }}>
                {summary.total_attempts || 0}
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                  ({summary.completed_attempts || 0} completed)
                </span>
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                {summary.failed_attempts || 0} failed / {summary.abandoned_attempts || 0} abandoned
              </div>
            </div>

            {/* Card 3: Average Coding Score */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #06b6d4' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Average Score
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#38bdf8' }}>
                {summary.average_coding_score != null ? `${summary.average_coding_score}` : 'N/A'}
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}> / 100</span>
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                5-component evaluation
              </div>
            </div>

            {/* Card 4: Best Coding Score */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #a855f7' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Best Score
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#c084fc' }}>
                {summary.best_coding_score != null ? `${summary.best_coding_score}` : 'N/A'}
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}> / 100</span>
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Peak attempt performance
              </div>
            </div>

            {/* Card 5: Total Active Coding Time */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #f59e0b' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Active Coding Time
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fbbf24' }}>
                {summary.total_active_coding_time_formatted || '0s'}
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Timer pauses excluded
              </div>
            </div>

            {/* Card 6: Average Time per Completed Attempt */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #eab308' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Avg Time / Solve
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fde047' }}>
                {summary.avg_coding_time_completed_formatted || '0s'}
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Completed solves duration
              </div>
            </div>

            {/* Card 7: Total Unique Hints Used */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #ec4899' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Unique Hints Used
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#f472b6' }}>
                {summary.total_unique_hints_used || 0}
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Penalty: 10, 9, 7, 4, 1 curve
              </div>
            </div>

            {/* Card 8: Total Tab Switches */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #f97316' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Tab Switches
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fb923c' }}>
                {summary.total_tab_switches || 0}
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Visibility loss telemetry
              </div>
            </div>

            {/* Card 9: Total Time Away from IDE */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #f43f5e' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Time Spent Away
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fb7185' }}>
                {summary.total_time_away_formatted || '0s'}
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Non-coding background time
              </div>
            </div>

            {/* Card 10: Overall Test Pass Rate */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #22c55e' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                Test Pass Rate
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#4ade80' }}>
                {summary.overall_pass_rate_percentage || 0}%
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                {summary.total_test_cases_passed || 0} of {summary.total_test_cases_evaluated || 0} passed
              </div>
            </div>

            {/* Card 11: AI Viva Performance */}
            <div className="glass-panel" style={{ padding: '16px 18px', borderLeft: '4px solid #8b5cf6' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6, textTransform: 'uppercase' }}>
                AI Viva Score
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#a78bfa' }}>
                {summary.viva?.average_score != null ? `${summary.viva.average_score}` : 'N/A'}
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                  {summary.viva?.sessions_count ? ` (${summary.viva.sessions_count} viva)` : ''}
                </span>
              </div>
              <div style={{ fontSize: '0.725rem', color: '#94a3b8', marginTop: 4 }}>
                Oral defense evaluation
              </div>
            </div>
          </div>

          {/* Visualizations Section */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: 20, marginBottom: 28 }}>
            
            {/* Chart 1: Coding Score Over Time */}
            <div className="glass-panel" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <TrendingUp size={16} color="#06b6d4" />
                  Coding Score Over Time
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Chronological attempt scores (out of 100)
                </span>
              </div>

              {(!charts.score_over_time || charts.score_over_time.length === 0) ? (
                <div style={{ padding: '40px 10px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No evaluated scores in this date period.
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 160, padding: '10px 0', borderBottom: '1px solid var(--border-glass)' }}>
                  {charts.score_over_time.map((pt, idx) => {
                    const hPct = Math.max(8, Math.min(100, pt.score));
                    const barColor = pt.score >= 85 ? '#10b981' : (pt.score >= 70 ? '#06b6d4' : (pt.score >= 50 ? '#f59e0b' : '#ef4444'));
                    return (
                      <div 
                        key={idx} 
                        style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}
                        title={`${pt.question_title} (Att #${pt.attempt_number}): ${pt.score}/100\nDate: ${pt.timestamp_ist}`}
                      >
                        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: barColor, marginBottom: 4 }}>
                          {pt.score}
                        </span>
                        <div style={{
                          width: '100%',
                          maxWidth: 24,
                          height: `${hPct}%`,
                          background: `linear-gradient(180deg, ${barColor} 0%, rgba(15, 23, 42, 0.4) 100%)`,
                          borderRadius: '4px 4px 0 0',
                          boxShadow: `0 0 10px ${barColor}33`,
                          transition: 'height 0.3s ease'
                        }} />
                        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 45 }}>
                          #{idx + 1}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Chart 2: Topic Accuracy & Pass Rate */}
            <div className="glass-panel" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BarChart2 size={16} color="#8b5cf6" />
                  Topic Accuracy &amp; Pass Rate
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Pass rate % by problem category
                </span>
              </div>

              {(!charts.topic_accuracy || charts.topic_accuracy.length === 0) ? (
                <div style={{ padding: '40px 10px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No topic activity recorded in this period.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {charts.topic_accuracy.map((top, idx) => (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 4 }}>
                        <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{top.topic}</span>
                        <span style={{ color: '#a5b4fc', fontWeight: 700 }}>
                          {top.pass_rate_percentage}% ({top.unique_solved} solved / {top.attempts_count} att)
                        </span>
                      </div>
                      <div style={{ height: 8, background: 'rgba(15, 23, 42, 0.8)', borderRadius: 4, overflow: 'hidden', border: '1px solid var(--border-glass)' }}>
                        <div style={{
                          height: '100%',
                          width: `${Math.min(100, Math.max(2, top.pass_rate_percentage))}%`,
                          background: top.pass_rate_percentage >= 80 ? 'linear-gradient(90deg, #10b981, #34d399)' : 'linear-gradient(90deg, #6366f1, #a855f7)',
                          borderRadius: 4,
                          transition: 'width 0.4s ease'
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Chart 3: Active Coding Time per Question */}
            <div className="glass-panel" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Clock size={16} color="#f59e0b" />
                  Coding Time per Question Attempt
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Active duration excluding pauses
                </span>
              </div>

              {(!charts.coding_time_per_question || charts.coding_time_per_question.length === 0) ? (
                <div style={{ padding: '40px 10px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No duration records in this period.
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 160, padding: '10px 0', borderBottom: '1px solid var(--border-glass)' }}>
                  {charts.coding_time_per_question.slice(0, 15).map((q, idx) => {
                    const maxSecs = Math.max(...charts.coding_time_per_question.map(x => x.seconds), 60);
                    const hPct = Math.max(10, Math.min(100, (q.seconds / maxSecs) * 100));
                    return (
                      <div 
                        key={idx} 
                        style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}
                        title={`${q.question_title} (Att #${q.attempt_number}): ${q.formatted}\nStatus: ${q.status}`}
                      >
                        <span style={{ fontSize: '0.65rem', fontWeight: 600, color: '#fbbf24', marginBottom: 4 }}>
                          {q.formatted}
                        </span>
                        <div style={{
                          width: '100%',
                          maxWidth: 24,
                          height: `${hPct}%`,
                          background: 'linear-gradient(180deg, #f59e0b 0%, rgba(245, 158, 11, 0.2) 100%)',
                          borderRadius: '4px 4px 0 0',
                          boxShadow: '0 0 10px rgba(245, 158, 11, 0.2)'
                        }} />
                        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 45 }}>
                          #{idx + 1}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Chart 4: Tab Switches & Activity Telemetry */}
            <div className="glass-panel" style={{ padding: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <EyeOff size={16} color="#f97316" />
                  Tab Switches &amp; Time Away per Attempt
                </h3>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Page visibility loss count
                </span>
              </div>

              {(!charts.tab_switches_per_attempt || charts.tab_switches_per_attempt.length === 0) ? (
                <div style={{ padding: '40px 10px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No visibility change events recorded.
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, height: 160, padding: '10px 0', borderBottom: '1px solid var(--border-glass)' }}>
                  {charts.tab_switches_per_attempt.slice(0, 15).map((ts, idx) => {
                    const maxSw = Math.max(...charts.tab_switches_per_attempt.map(x => x.tab_switch_count), 5);
                    const hPct = Math.max(8, Math.min(100, (ts.tab_switch_count / maxSw) * 100));
                    return (
                      <div 
                        key={idx} 
                        style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}
                        title={`${ts.question_title} (Att #${ts.attempt_number}): ${ts.tab_switch_count} switches, ${ts.time_away_seconds}s away`}
                      >
                        <span style={{ fontSize: '0.65rem', fontWeight: 600, color: ts.tab_switch_count > 0 ? '#fb923c' : '#10b981', marginBottom: 4 }}>
                          {ts.tab_switch_count}
                        </span>
                        <div style={{
                          width: '100%',
                          maxWidth: 24,
                          height: `${hPct}%`,
                          background: ts.tab_switch_count > 0 
                            ? 'linear-gradient(180deg, #f97316 0%, rgba(249, 115, 22, 0.2) 100%)'
                            : 'linear-gradient(180deg, #10b981 0%, rgba(16, 185, 129, 0.2) 100%)',
                          borderRadius: '4px 4px 0 0',
                          boxShadow: '0 0 10px rgba(249, 115, 22, 0.2)'
                        }} />
                        <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)', marginTop: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 45 }}>
                          #{idx + 1}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

          </div>

          {/* Question-Wise Coding Performance Table */}
          <div className="glass-panel" style={{ padding: '24px 20px', marginBottom: 32 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14, marginBottom: 18 }}>
              <div>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Terminal size={18} color="#06b6d4" />
                  Question-Wise Coding Performance ({filteredAttempts.length} of {attempts.length} attempts)
                </h2>
                <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>
                  Searchable and sortable log of all persisted coding attempts with full score breakdown and time metrics
                </p>
              </div>

              {/* Filters & Search Toolbar */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                {/* Search input */}
                <div style={{ position: 'relative' }}>
                  <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
                  <input
                    type="text"
                    placeholder="Search question, topic, lang..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      background: 'rgba(15, 23, 42, 0.7)',
                      border: '1px solid var(--border-glass)',
                      borderRadius: 8,
                      padding: '6px 12px 6px 30px',
                      color: '#fff',
                      fontSize: '0.8rem',
                      width: 220
                    }}
                  />
                  {searchQuery && (
                    <button 
                      onClick={() => setSearchQuery('')}
                      style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                    >
                      <X size={12} />
                    </button>
                  )}
                </div>

                {/* Status Filter */}
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.7)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 8,
                    padding: '6px 10px',
                    color: '#e2e8f0',
                    fontSize: '0.8rem'
                  }}
                >
                  <option value="all">All Statuses</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                  <option value="abandoned">Abandoned</option>
                </select>

                {/* Topic Filter */}
                {availableTopics.length > 0 && (
                  <select
                    value={topicFilter}
                    onChange={(e) => setTopicFilter(e.target.value)}
                    style={{
                      background: 'rgba(15, 23, 42, 0.7)',
                      border: '1px solid var(--border-glass)',
                      borderRadius: 8,
                      padding: '6px 10px',
                      color: '#e2e8f0',
                      fontSize: '0.8rem'
                    }}
                  >
                    <option value="all">All Topics</option>
                    {availableTopics.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                )}

                {/* Sort Order */}
                <select
                  value={sortField}
                  onChange={(e) => setSortField(e.target.value)}
                  style={{
                    background: 'rgba(15, 23, 42, 0.7)',
                    border: '1px solid var(--border-glass)',
                    borderRadius: 8,
                    padding: '6px 10px',
                    color: '#e2e8f0',
                    fontSize: '0.8rem'
                  }}
                >
                  <option value="date_desc">Newest First</option>
                  <option value="date_asc">Oldest First</option>
                  <option value="score_desc">Highest Score</option>
                  <option value="score_asc">Lowest Score</option>
                  <option value="duration_desc">Longest Duration</option>
                  <option value="duration_asc">Shortest Duration</option>
                  <option value="switches_desc">Most Tab Switches</option>
                </select>
              </div>
            </div>

            {/* Table Display or Empty State */}
            {filteredAttempts.length === 0 ? (
              <div style={{
                padding: '60px 20px',
                textAlign: 'center',
                background: 'rgba(15, 23, 42, 0.4)',
                borderRadius: 12,
                border: '1px dashed var(--border-glass)'
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
                  <Terminal size={24} color="#818cf8" />
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, margin: '0 0 6px 0', color: '#f1f5f9' }}>
                  {attempts.length === 0 ? 'No coding attempts yet' : 'No matching attempts found'}
                </h3>
                <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: 450, marginInline: 'auto' }}>
                  {attempts.length === 0 
                    ? 'Start working on algorithmic problems in the Code IDE to record your coding duration, test results, hints, and 5-dimension scores.'
                    : 'Try clearing your search term or setting filter options back to "All".'}
                </p>
                {attempts.length === 0 && onSelectProblem && (
                  <button
                    onClick={() => onSelectProblem('two-sum')}
                    className="btn btn-primary"
                    style={{ padding: '8px 20px', fontSize: '0.85rem' }}
                  >
                    Solve First Coding Challenge
                  </button>
                )}
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-glass)', background: 'rgba(15, 23, 42, 0.6)' }}>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Question &amp; ID</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Topic / Diff</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Language / Att</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Status</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Start / End (IST)</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Duration</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Score / Tests</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Hints / Indep</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600 }}>Tabs / Away</th>
                      <th style={{ padding: '12px 14px', color: '#94a3b8', fontWeight: 600, textAlign: 'center' }}>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAttempts.map((att, idx) => {
                      const isComplete = att.is_completed;
                      const statusColor = isComplete ? '#10b981' : (att.attempt_status === 'failed' ? '#ef4444' : '#f59e0b');
                      const scoreColor = (att.overall_score || 0) >= 80 ? '#10b981' : ((att.overall_score || 0) >= 60 ? '#06b6d4' : '#f59e0b');

                      return (
                        <tr 
                          key={att.attempt_id || idx}
                          style={{ 
                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                            transition: 'background 0.15s ease'
                          }}
                          className="table-row-hover"
                        >
                          {/* Question Title & ID */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: 2 }}>
                              {att.question_title}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace' }}>
                              {att.question_id}
                            </div>
                          </td>

                          {/* Topic & Difficulty */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ color: '#cbd5e1' }}>{att.topic}</div>
                            <span style={{
                              display: 'inline-block',
                              fontSize: '0.68rem',
                              padding: '2px 6px',
                              borderRadius: 4,
                              marginTop: 2,
                              fontWeight: 600,
                              background: att.difficulty === 'Easy' ? 'rgba(16, 185, 129, 0.15)' : (att.difficulty === 'Hard' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)'),
                              color: att.difficulty === 'Easy' ? '#34d399' : (att.difficulty === 'Hard' ? '#f87171' : '#fbbf24')
                            }}>
                              {att.difficulty}
                            </span>
                          </td>

                          {/* Language & Attempt # */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ fontWeight: 600, textTransform: 'uppercase', color: '#93c5fd' }}>
                              {att.language}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                              Attempt #{att.attempt_number}
                            </div>
                          </td>

                          {/* Status */}
                          <td style={{ padding: '12px 14px' }}>
                            <span style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 4,
                              fontSize: '0.725rem',
                              fontWeight: 700,
                              padding: '3px 8px',
                              borderRadius: 6,
                              background: `${statusColor}18`,
                              color: statusColor,
                              border: `1px solid ${statusColor}44`
                            }}>
                              {isComplete ? <CheckCircle2 size={12} /> : (att.attempt_status === 'failed' ? <XCircle size={12} /> : <AlertTriangle size={12} />)}
                              {att.attempt_status?.toUpperCase()}
                            </span>
                          </td>

                          {/* Timestamps (IST) */}
                          <td style={{ padding: '12px 14px', fontSize: '0.725rem' }}>
                            <div style={{ color: '#e2e8f0' }}>{att.start_time_ist || 'N/A'}</div>
                            <div style={{ color: '#64748b', marginTop: 2 }}>
                              {att.end_time_ist ? `Done: ${att.end_time_ist}` : 'Incomplete'}
                            </div>
                          </td>

                          {/* Duration (Coding / Exec) */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ fontWeight: 700, color: '#f8fafc' }}>
                              {att.coding_duration_formatted}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                              {att.execution_time_ms ? `${att.execution_time_ms} ms` : 'N/A'}
                            </div>
                          </td>

                          {/* Score / Tests */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ fontWeight: 800, fontSize: '0.875rem', color: scoreColor }}>
                              {att.overall_score != null ? `${att.overall_score} / 100` : 'Not evaluated'}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                              {att.passed_count}/{att.total_count} tests ({att.pass_rate_percentage}%)
                            </div>
                          </td>

                          {/* Hints / Independent Score */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ color: '#cbd5e1' }}>
                              {att.unique_hints_used} hint{att.unique_hints_used !== 1 ? 's' : ''}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#a5b4fc', fontWeight: 600 }}>
                              Indep: {att.independent_score}/10
                            </div>
                          </td>

                          {/* Tab Switches / Away */}
                          <td style={{ padding: '12px 14px' }}>
                            <div style={{ color: att.tab_switch_count > 0 ? '#fb923c' : '#10b981', fontWeight: 600 }}>
                              {att.tab_switch_count} switch{att.tab_switch_count !== 1 ? 'es' : ''}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                              Away: {att.time_away_formatted}
                            </div>
                          </td>

                          {/* Action Details */}
                          <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                            <button
                              onClick={() => setSelectedAttempt(att)}
                              className="btn btn-secondary"
                              style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                              title="View full evaluation breakdown and tab-switch log"
                            >
                              Details
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {/* Attempt Details & Score Breakdown Modal */}
      {selectedAttempt && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(8px)',
          zIndex: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 20
        }}>
          <div className="glass-panel-elevated animate-slide-down" style={{
            width: '100%',
            maxWidth: 820,
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: 28,
            position: 'relative'
          }}>
            {/* Close Button */}
            <button
              onClick={() => setSelectedAttempt(null)}
              style={{
                position: 'absolute',
                top: 20,
                right: 20,
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              <X size={20} />
            </button>

            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <div style={{
                width: 44,
                height: 44,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Award size={24} color="#fff" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
                  {selectedAttempt.question_title}
                </h3>
                <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Question ID: <code>{selectedAttempt.question_id}</code> • Attempt #{selectedAttempt.attempt_number} • {selectedAttempt.language.toUpperCase()}
                </p>
              </div>
            </div>

            {/* Overall Score Banner */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: 12,
              padding: '16px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 20,
              flexWrap: 'wrap',
              gap: 12
            }}>
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#38bdf8', textTransform: 'uppercase' }}>
                  Coding Score Evaluation
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fff' }}>
                  {selectedAttempt.overall_score != null ? `${selectedAttempt.overall_score}` : 'N/A'}
                  <span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 500 }}> / 100</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: 16, fontSize: '0.8rem' }}>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Status</div>
                  <div style={{ fontWeight: 700, color: selectedAttempt.is_completed ? '#10b981' : '#f59e0b' }}>
                    {selectedAttempt.attempt_status?.toUpperCase()}
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Tests Passed</div>
                  <div style={{ fontWeight: 700, color: '#e2e8f0' }}>
                    {selectedAttempt.passed_count} / {selectedAttempt.total_count} ({selectedAttempt.pass_rate_percentage}%)
                  </div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)' }}>Active Time</div>
                  <div style={{ fontWeight: 700, color: '#fde047' }}>
                    {selectedAttempt.coding_duration_formatted}
                  </div>
                </div>
              </div>
            </div>

            {/* 5-Dimension Score Breakdown */}
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 10, color: '#93c5fd' }}>
              Configured Score Components
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 10, marginBottom: 20 }}>
              {/* Correctness */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Correctness</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34d399' }}>
                  {selectedAttempt.score_breakdown?.correctness?.points_earned ?? (selectedAttempt.passed_count ? Math.round((selectedAttempt.passed_count / Math.max(1, selectedAttempt.total_count)) * 40) : 0)}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 40</span>
                </div>
              </div>

              {/* Complexity */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Complexity</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#38bdf8' }}>
                  {selectedAttempt.score_breakdown?.complexity?.points_earned ?? (selectedAttempt.score_breakdown?.complexity?.is_available === false ? 'N/A' : '15')}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 20</span>
                </div>
              </div>

              {/* Code Quality */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Code Quality</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#c084fc' }}>
                  {selectedAttempt.score_breakdown?.quality?.points_earned ?? (selectedAttempt.score_breakdown?.quality?.is_available === false ? 'N/A' : '12')}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 15</span>
                </div>
              </div>

              {/* Approach */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Approach</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fcd34d' }}>
                  {selectedAttempt.score_breakdown?.approach?.points_earned ?? (selectedAttempt.score_breakdown?.approach?.is_available === false ? 'N/A' : '12')}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 15</span>
                </div>
              </div>

              {/* Independent Problem-Solving */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Independent (Hints)</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f472b6' }}>
                  {selectedAttempt.independent_score ?? 10}
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}> / 10</span>
                </div>
                <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                  {selectedAttempt.unique_hints_used} hint{selectedAttempt.unique_hints_used !== 1 ? 's' : ''} used
                </div>
              </div>
            </div>

            {/* Tab Switches & Away Telemetry for this attempt */}
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 8, color: '#93c5fd', display: 'flex', alignItems: 'center', gap: 6 }}>
              <EyeOff size={16} /> Tab Switches &amp; Browser Focus Activity
            </h4>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', borderRadius: 8, padding: 14, marginBottom: 20, border: '1px solid var(--border-glass)' }}>
              <div style={{ display: 'flex', gap: 20, marginBottom: 10, fontSize: '0.8rem' }}>
                <div>Total Switches: <strong>{selectedAttempt.tab_switch_count}</strong></div>
                <div>Time Away: <strong>{selectedAttempt.time_away_formatted}</strong></div>
                <div>Start (IST): <strong>{selectedAttempt.start_time_ist || 'N/A'}</strong></div>
                <div>End (IST): <strong>{selectedAttempt.end_time_ist || 'Incomplete'}</strong></div>
              </div>

              {selectedAttempt.tab_switch_history && selectedAttempt.tab_switch_history.length > 0 ? (
                <div style={{ maxHeight: 180, overflowY: 'auto' }}>
                  <table style={{ width: '100%', fontSize: '0.75rem', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ color: '#94a3b8', borderBottom: '1px solid var(--border-glass)' }}>
                        <th style={{ padding: '4px 6px', textAlign: 'left' }}>#</th>
                        <th style={{ padding: '4px 6px', textAlign: 'left' }}>Page Hidden (IST)</th>
                        <th style={{ padding: '4px 6px', textAlign: 'left' }}>Returned (IST)</th>
                        <th style={{ padding: '4px 6px', textAlign: 'left' }}>Duration Away</th>
                        <th style={{ padding: '4px 6px', textAlign: 'left' }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedAttempt.tab_switch_history.map((ev, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                          <td style={{ padding: '4px 6px' }}>{i + 1}</td>
                          <td style={{ padding: '4px 6px' }}>{ev.hidden_time_ist || 'N/A'}</td>
                          <td style={{ padding: '4px 6px' }}>{ev.return_time_ist || 'Active Away'}</td>
                          <td style={{ padding: '4px 6px' }}>{ev.duration_away_formatted || `${ev.time_away_seconds}s`}</td>
                          <td style={{ padding: '4px 6px', color: ev.status === 'returned' ? '#10b981' : '#f59e0b' }}>
                            {ev.status || 'returned'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  No tab switches occurred during this attempt. Full IDE focus maintained.
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              {onSelectProblem && (
                <button
                  onClick={() => {
                    const qid = selectedAttempt.question_id;
                    setSelectedAttempt(null);
                    onSelectProblem(qid);
                  }}
                  className="btn btn-primary"
                  style={{ padding: '8px 18px', fontSize: '0.85rem' }}
                >
                  <Terminal size={15} style={{ marginRight: 6 }} /> Open in Code IDE
                </button>
              )}
              <button
                onClick={() => setSelectedAttempt(null)}
                className="btn btn-secondary"
                style={{ padding: '8px 18px', fontSize: '0.85rem' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PDF Report Generation Modal */}
      {isPdfModalOpen && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(8px)',
          zIndex: 100,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 20
        }}>
          <div className="glass-panel-elevated animate-slide-down" style={{
            width: '100%',
            maxWidth: 580,
            padding: 28,
            position: 'relative',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 35px rgba(6, 182, 212, 0.25)'
          }}>
            {/* Close Button */}
            <button
              onClick={() => {
                if (!isGeneratingPdf) {
                  setIsPdfModalOpen(false);
                  setPdfError('');
                }
              }}
              style={{
                position: 'absolute',
                top: 20,
                right: 20,
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              <X size={20} />
            </button>

            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <div style={{
                width: 44,
                height: 44,
                borderRadius: 12,
                background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 20px rgba(79, 70, 229, 0.4)'
              }}>
                <FileText size={24} color="#fff" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
                  Generate PDF Performance Report
                </h3>
                <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Download genuine multi-page PDF performance records in IST (Asia/Kolkata)
                </p>
              </div>
            </div>

            {/* Note: PDF only */}
            <div style={{
              background: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.2)',
              borderRadius: 8,
              padding: '8px 12px',
              fontSize: '0.78rem',
              color: '#38bdf8',
              marginBottom: 16
            }}>
              <strong>Format Notice:</strong> PDF is the exclusive official download format for CodeAcharya student audit reports.
            </div>

            {pdfError && (
              <div style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                borderRadius: 8,
                padding: '8px 12px',
                color: '#fca5a5',
                fontSize: '0.8rem',
                marginBottom: 14
              }}>
                {pdfError}
              </div>
            )}

            {/* Configuration 1: Date Range */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '0.825rem', fontWeight: 700, color: '#e2e8f0', display: 'block', marginBottom: 8 }}>
                1. Select Reporting Period
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6, marginBottom: 8 }}>
                {PRESET_DATE_FILTERS.map(f => (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => setPdfDateFilter(f.id)}
                    style={{
                      padding: '6px 8px',
                      borderRadius: 6,
                      fontSize: '0.75rem',
                      fontWeight: pdfDateFilter === f.id ? 700 : 500,
                      border: '1px solid',
                      borderColor: pdfDateFilter === f.id ? '#06b6d4' : 'var(--border-glass)',
                      background: pdfDateFilter === f.id ? 'rgba(6, 182, 212, 0.2)' : 'rgba(15, 23, 42, 0.6)',
                      color: pdfDateFilter === f.id ? '#38bdf8' : 'var(--text-muted)',
                      cursor: 'pointer'
                    }}
                  >
                    {f.label}
                  </button>
                ))}
              </div>

              {pdfDateFilter === 'custom' && (
                <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: '0.725rem', color: 'var(--text-muted)', display: 'block', marginBottom: 3 }}>Start Date (IST):</label>
                    <input
                      type="date"
                      value={pdfStartDate}
                      onChange={(e) => setPdfStartDate(e.target.value)}
                      style={{
                        width: '100%',
                        background: 'rgba(15, 23, 42, 0.8)',
                        border: '1px solid var(--border-glass)',
                        borderRadius: 6,
                        padding: '6px 10px',
                        color: '#fff',
                        fontSize: '0.78rem'
                      }}
                    />
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: '0.725rem', color: 'var(--text-muted)', display: 'block', marginBottom: 3 }}>End Date (IST):</label>
                    <input
                      type="date"
                      value={pdfEndDate}
                      onChange={(e) => setPdfEndDate(e.target.value)}
                      style={{
                        width: '100%',
                        background: 'rgba(15, 23, 42, 0.8)',
                        border: '1px solid var(--border-glass)',
                        borderRadius: 6,
                        padding: '6px 10px',
                        color: '#fff',
                        fontSize: '0.78rem'
                      }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Configuration 2: Optional Sections */}
            <div style={{ marginBottom: 20 }}>
              <label style={{ fontSize: '0.825rem', fontWeight: 700, color: '#e2e8f0', display: 'block', marginBottom: 8 }}>
                2. Optional Report Sections
              </label>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, background: 'rgba(15, 23, 42, 0.5)', padding: 12, borderRadius: 8, border: '1px solid var(--border-glass)' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8rem', color: '#cbd5e1', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={pdfIncludeTabs}
                    onChange={(e) => setPdfIncludeTabs(e.target.checked)}
                    style={{ accentColor: '#06b6d4' }}
                  />
                  <span>Include detailed tab-switch &amp; visibility history</span>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8rem', color: '#cbd5e1', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={pdfIncludeViva}
                    onChange={(e) => setPdfIncludeViva(e.target.checked)}
                    style={{ accentColor: '#06b6d4' }}
                  />
                  <span>Include AI Viva oral defense evaluation records</span>
                </label>

                <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.8rem', color: '#cbd5e1', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={pdfViewMode === 'detailed'}
                    onChange={(e) => setPdfViewMode(e.target.checked ? 'detailed' : 'summary')}
                    style={{ accentColor: '#06b6d4' }}
                  />
                  <span>Include question-level attempt details (unchecked: summary only)</span>
                </label>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                type="button"
                disabled={isGeneratingPdf}
                onClick={() => setIsPdfModalOpen(false)}
                className="btn btn-secondary"
                style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              >
                Cancel
              </button>
              
              <button
                type="button"
                disabled={isGeneratingPdf}
                onClick={handleDownloadPdf}
                className="btn btn-primary"
                style={{
                  padding: '8px 22px',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)'
                }}
              >
                {isGeneratingPdf ? (
                  <>
                    <RefreshCw size={15} style={{ animation: 'spin 1s linear infinite' }} />
                    <span>Preparing PDF...</span>
                  </>
                ) : (
                  <>
                    <Download size={15} />
                    <span>Download PDF Report</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
