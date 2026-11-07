import React, { useEffect, useRef } from 'react';
import { Lock, Maximize2, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

/**
 * FullscreenLockOverlay
 * 
 * Displayed when full-screen mode is exited or page is hidden during any coding mode.
 * Enforces browser full-screen verification before unlocking the editor.
 * Reassures the student that their existing code remains 100% preserved.
 */
export default function FullscreenLockOverlay({
  isOpen = false,
  onRestoreResume,
  lockReason = 'fullscreen_exit',
  errorMessage = '',
  isResuming = false,
  savedCode = ''
}) {
  const buttonRef = useRef(null);

  // Auto-focus the restore button when modal appears for accessible keyboard flow
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      buttonRef.current.focus();
    }
  }, [isOpen]);

  // Trap keyboard events inside the overlay so keyboard shortcuts don't reach the editor
  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      // Keep focus on the interactive button
      if (buttonRef.current) {
        buttonRef.current.focus();
      }
      e.preventDefault();
    }
    // Prevent Enter or Space if focused elsewhere, but allow default on button
    if (e.target !== buttonRef.current && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      if (typeof onRestoreResume === 'function' && !isResuming) {
        onRestoreResume();
      }
    }
  };

  if (!isOpen) return null;

  const reasonDescription = lockReason === 'page_hidden'
    ? 'The application window lost focus or switched tabs.'
    : lockReason === 'unsupported'
    ? 'Browser full-screen API is unsupported in this environment.'
    : 'Full-screen mode was exited.';

  return (
    <div 
      className="fullscreen-lock-overlay animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="lock-overlay-title"
      aria-describedby="lock-overlay-desc"
      onKeyDown={handleKeyDown}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1000,
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        background: 'rgba(10, 15, 29, 0.94)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
        borderRadius: 12,
        boxShadow: 'inset 0 0 40px rgba(0, 0, 0, 0.8)'
      }}
    >
      <div 
        className="glass-panel-elevated animate-scale-up"
        style={{
          maxWidth: 520,
          width: '100%',
          padding: '36px 32px',
          borderRadius: 16,
          background: 'linear-gradient(135deg, rgba(20, 26, 47, 0.98), rgba(15, 23, 42, 0.99))',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(239, 68, 68, 0.2)',
          textAlign: 'center'
        }}
      >
        {/* Pulsing Lock Icon */}
        <div style={{
          width: 64,
          height: 64,
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.45)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 18px auto',
          boxShadow: '0 0 25px rgba(239, 68, 68, 0.35)',
          animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
        }}>
          <Lock size={32} color="#f87171" />
        </div>

        {/* Security Badge */}
        <span 
          className="badge" 
          style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            color: '#fca5a5',
            fontSize: '0.75rem',
            fontWeight: 700,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            padding: '4px 12px',
            borderRadius: 20,
            marginBottom: 12,
            display: 'inline-block'
          }}
        >
          Proctoring Enforcement Active
        </span>

        {/* Headline & Subtitle */}
        <h2 
          id="lock-overlay-title"
          style={{
            fontSize: '1.5rem',
            fontWeight: 800,
            color: '#f8fafc',
            margin: '8px 0 8px 0',
            fontFamily: 'var(--font-heading)'
          }}
        >
          Assessment Locked
        </h2>

        <p 
          id="lock-overlay-desc"
          style={{
            fontSize: '0.975rem',
            color: '#cbd5e1',
            lineHeight: 1.5,
            margin: '0 auto 16px auto',
            maxWidth: 420
          }}
        >
          Full-screen mode is required to continue coding.
        </p>

        {/* Reason Context Box */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.75)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 10,
          padding: '10px 16px',
          marginBottom: 20,
          fontSize: '0.825rem',
          color: '#94a3b8',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 8
        }}>
          <AlertTriangle size={15} color="#f59e0b" style={{ flexShrink: 0 }} />
          <span><strong>Event detected:</strong> {reasonDescription}</span>
        </div>

        {/* Error message banner if browser rejected fullscreen request */}
        {errorMessage && (
          <div 
            className="animate-slide-down"
            style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.5)',
              borderRadius: 8,
              padding: '10px 14px',
              marginBottom: 20,
              fontSize: '0.825rem',
              color: '#fca5a5',
              textAlign: 'left'
            }}
          >
            <strong>Full-Screen Error:</strong> {errorMessage}
          </div>
        )}

        {/* Restore Full Screen & Resume Button */}
        <button
          ref={buttonRef}
          id="btn-restore-fullscreen"
          onClick={onRestoreResume}
          disabled={isResuming}
          className="btn btn-emerald glow-emerald"
          style={{
            padding: '14px 34px',
            fontSize: '1rem',
            fontWeight: 700,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 10,
            borderRadius: 10,
            boxShadow: '0 0 30px rgba(16, 185, 129, 0.45)',
            width: '100%',
            cursor: isResuming ? 'wait' : 'pointer'
          }}
          aria-label="Restore Full Screen and Resume Coding"
        >
          {isResuming ? (
            <>
              <RefreshCw size={18} className="animate-spin" />
              <span>Verifying Full-Screen...</span>
            </>
          ) : (
            <>
              <Maximize2 size={18} />
              <span>Restore Full Screen &amp; Resume</span>
            </>
          )}
        </button>

        {/* Code Preservation Reassurance */}
        <div style={{
          marginTop: 18,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 6,
          fontSize: '0.775rem',
          color: '#34d399'
        }}>
          <ShieldCheck size={14} color="#34d399" />
          <span>Your code and progress are securely preserved.</span>
        </div>
      </div>
    </div>
  );
}

