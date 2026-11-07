import React from 'react';
import { 
  Terminal, 
  BrainCircuit, 
  BarChart3, 
  Compass, 
  Settings, 
  Flame, 
  CheckCircle2, 
  GraduationCap, 
  ArrowLeft,
  LogOut,
  TrendingUp
} from 'lucide-react';

export default function Header({ 
  activeTab, 
  setActiveTab, 
  studentProfile, 
  persona, 
  setPersona,
  onOpenSettings,
  hasGeminiKey,
  language = 'python',
  setLanguage,
  onBack,
  canGoBack,
  onGoHome,
  user,
  onRequestLogout
}) {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-glass)',
      background: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '12px 24px'
    }}>
      <div style={{
        maxWidth: 1600,
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 16
      }}>
        {/* Brand & Optional Back Action */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          {/* Clickable Brand Logo navigating to Home */}
          <button
            type="button"
            onClick={user ? onGoHome : () => setActiveTab('login')}
            className="brand-home-btn"
            aria-label="Go to Home"
            title="Go to Home (Code IDE & Problem Catalog)"
          >
            <div style={{
              width: 42,
              height: 42,
              borderRadius: 12,
              background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(99, 102, 241, 0.45)',
              flexShrink: 0
            }}>
              <BrainCircuit size={24} color="#fff" />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <span style={{ 
                fontFamily: 'var(--font-heading)', 
                fontSize: '1.25rem', 
                fontWeight: 700, 
                letterSpacing: '-0.02em',
                lineHeight: 1.2,
                background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                CodeAcharya
              </span>
              <p style={{ 
                fontSize: '0.75rem', 
                color: 'var(--text-muted)', 
                margin: 0,
                marginTop: 2,
                fontWeight: 500,
                letterSpacing: '-0.01em'
              }}>
                Your AI Coding Mentor
              </p>
            </div>
          </button>

          {/* Header Back Button (shown on internal/subpages or when history exists) */}
          {(activeTab !== 'workspace' || canGoBack) && onBack && user && (
            <button
              type="button"
              onClick={onBack}
              className="nav-back-btn"
              aria-label="Back"
              title="Back to previous page"
              style={{ marginLeft: 4 }}
            >
              <ArrowLeft size={16} />
              <span>Back</span>
            </button>
          )}
        </div>

        {/* Navigation Tabs - only shown when authenticated */}
        {user && (
          <nav style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(15, 23, 42, 0.6)', padding: 4, borderRadius: 12, border: '1px solid var(--border-glass)' }}>
            <button 
              type="button"
              className={`btn ${activeTab === 'workspace' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '0.825rem' }}
              onClick={() => setActiveTab('workspace')}
            >
              <Terminal size={15} /> Code IDE & Hints
            </button>

            <button 
              type="button"
              className={`btn ${activeTab === 'viva' ? 'btn-purple' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '0.825rem' }}
              onClick={() => setActiveTab('viva')}
            >
              <GraduationCap size={15} /> AI Viva Mode
            </button>

            <button 
              type="button"
              className={`btn ${activeTab === 'performance' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ 
                padding: '6px 14px', 
                fontSize: '0.825rem',
                background: activeTab === 'performance' ? 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)' : undefined,
                color: activeTab === 'performance' ? '#fff' : undefined,
                boxShadow: activeTab === 'performance' ? '0 0 15px rgba(6, 182, 212, 0.4)' : undefined,
                borderColor: activeTab === 'performance' ? '#06b6d4' : undefined
              }}
              onClick={() => setActiveTab('performance')}
            >
              <TrendingUp size={15} /> My Performance
            </button>

            <button 
              type="button"
              className={`btn ${activeTab === 'analytics' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '0.825rem' }}
              onClick={() => setActiveTab('analytics')}
            >
              <BarChart3 size={15} /> Skill Profile
            </button>

            <button 
              type="button"
              className={`btn ${activeTab === 'recommendations' ? 'btn-emerald' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '0.825rem' }}
              onClick={() => setActiveTab('recommendations')}
            >
              <Compass size={15} /> Adaptive Paths
            </button>
          </nav>
        )}

        {/* Right Stats & Settings / Auth controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {user ? (
            <>
              {/* Language Selector */}
              {setLanguage && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: 'rgba(15, 23, 42, 0.75)',
                  borderRadius: 10,
                  padding: 3,
                  border: '1px solid var(--border-glass)',
                  boxShadow: '0 2px 10px rgba(0, 0, 0, 0.3)'
                }}>
                  <button
                    onClick={() => setLanguage('python')}
                    style={{
                      padding: '5px 9px',
                      borderRadius: 7,
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                      background: language === 'python' ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' : 'transparent',
                      color: language === 'python' ? '#fff' : 'var(--text-muted)',
                      transition: 'all 0.2s',
                      boxShadow: language === 'python' ? '0 0 10px rgba(59, 130, 246, 0.4)' : 'none'
                    }}
                    title="Code in Python 3"
                  >
                    <span>🐍 Python</span>
                  </button>

                  <button
                    onClick={() => setLanguage('c')}
                    style={{
                      padding: '5px 9px',
                      borderRadius: 7,
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                      background: language === 'c' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'transparent',
                      color: language === 'c' ? '#fff' : 'var(--text-muted)',
                      transition: 'all 0.2s',
                      boxShadow: language === 'c' ? '0 0 10px rgba(99, 102, 241, 0.4)' : 'none'
                    }}
                    title="Code in C (GCC)"
                  >
                    <span>🔷 C</span>
                  </button>

                  <button
                    onClick={() => setLanguage('cpp')}
                    style={{
                      padding: '5px 9px',
                      borderRadius: 7,
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                      background: language === 'cpp' ? 'linear-gradient(135deg, #06b6d4, #0891b2)' : 'transparent',
                      color: language === 'cpp' ? '#fff' : 'var(--text-muted)',
                      transition: 'all 0.2s',
                      boxShadow: language === 'cpp' ? '0 0 10px rgba(6, 182, 212, 0.4)' : 'none'
                    }}
                    title="Code in C++ (C++20)"
                  >
                    <span>⚙️ C++</span>
                  </button>

                  <button
                    onClick={() => setLanguage('java')}
                    style={{
                      padding: '5px 9px',
                      borderRadius: 7,
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      border: 'none',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                      background: language === 'java' ? 'linear-gradient(135deg, #ef4444, #b91c1c)' : 'transparent',
                      color: language === 'java' ? '#fff' : 'var(--text-muted)',
                      transition: 'all 0.2s',
                      boxShadow: language === 'java' ? '0 0 10px rgba(239, 68, 68, 0.4)' : 'none'
                    }}
                    title="Code in Java (Java 21)"
                  >
                    <span>☕ Java</span>
                  </button>
                </div>
              )}

              {/* Live Compiler Status Pill */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: 'rgba(16, 185, 129, 0.1)',
                padding: '5px 10px',
                borderRadius: 8,
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontSize: '0.75rem',
                color: '#34d399',
                fontWeight: 600,
                boxShadow: '0 0 12px rgba(16, 185, 129, 0.15)'
              }}>
                <span style={{
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: '#10b981',
                  boxShadow: '0 0 8px #10b981',
                  animation: 'pulse 1.8s infinite'
                }}></span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>IDE v2.4 Live</span>
              </div>

              {/* Streak indicator */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: 'rgba(245, 158, 11, 0.12)',
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid rgba(245, 158, 11, 0.35)',
                fontSize: '0.8rem',
                color: '#fbbf24',
                fontWeight: 600,
                boxShadow: '0 0 12px rgba(245, 158, 11, 0.2)'
              }}>
                <Flame size={15} color="#f59e0b" />
                <span>{studentProfile?.streak_days || 1} Day Streak</span>
              </div>

              {/* Solved Count */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                background: 'rgba(99, 102, 241, 0.12)',
                padding: '6px 12px',
                borderRadius: 8,
                border: '1px solid rgba(99, 102, 241, 0.35)',
                fontSize: '0.8rem',
                color: '#a5b4fc',
                fontWeight: 600,
                boxShadow: '0 0 12px rgba(99, 102, 241, 0.18)'
              }}>
                <CheckCircle2 size={15} color="#818cf8" />
                <span>{studentProfile?.total_solved || 0} Solved</span>
              </div>

              {/* Settings / API Key */}
              <button 
                onClick={onOpenSettings}
                className="btn btn-secondary"
                title="Configure AI & Persona"
                style={{ padding: 8, borderRadius: 8 }}
              >
                <Settings size={18} />
              </button>

              {/* Authenticated User info & Logout button */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                background: 'rgba(15, 23, 42, 0.85)',
                padding: '4px 6px 4px 10px',
                borderRadius: 10,
                border: '1px solid var(--border-glass)',
                boxShadow: '0 2px 10px rgba(0, 0, 0, 0.3)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '0.75rem',
                    color: '#ffffff',
                    boxShadow: '0 0 10px rgba(99, 102, 241, 0.4)',
                    flexShrink: 0
                  }} title={user.email}>
                    {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ 
                      fontSize: '0.775rem', 
                      fontWeight: 600, 
                      color: 'var(--text-main)', 
                      maxWidth: 110, 
                      whiteSpace: 'nowrap', 
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis' 
                    }}>
                      {user.full_name || 'Learner'}
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={onRequestLogout}
                  className="btn btn-secondary logout-action-btn"
                  title="Sign out of your account"
                  aria-label="Log Out"
                  style={{
                    padding: '5px 10px',
                    fontSize: '0.75rem',
                    borderRadius: 7,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 5,
                    color: '#fca5a5',
                    background: 'rgba(244, 63, 94, 0.1)',
                    borderColor: 'rgba(244, 63, 94, 0.3)',
                    cursor: 'pointer'
                  }}
                >
                  <LogOut size={13} color="#f43f5e" />
                  <span>Log Out</span>
                </button>
              </div>
            </>
          ) : (
            /* Unauthenticated user header actions */
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <button
                type="button"
                onClick={() => setActiveTab('login')}
                className={`btn ${activeTab === 'login' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '6px 14px', fontSize: '0.8rem', borderRadius: 8 }}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('signup')}
                className={`btn ${activeTab === 'signup' ? 'btn-purple' : 'btn-secondary'}`}
                style={{ padding: '6px 14px', fontSize: '0.8rem', borderRadius: 8 }}
              >
                Sign Up
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
