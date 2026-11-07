import React, { useEffect, useRef } from 'react';
import { AlertTriangle, X, Code2, ArrowRight } from 'lucide-react';
import { getLanguageDisplayName } from '../utils/languageUtils';

/**
 * LanguageChangeModal
 * 
 * Confirmation modal displayed whenever a student attempts to change the
 * programming language in the coding workspace while code exists in the editor.
 */
export default function LanguageChangeModal({
  isOpen = false,
  currentLanguage = 'python',
  newLanguage = 'c',
  onCancel,
  onConfirm,
  isConfirming = false
}) {
  const cancelBtnRef = useRef(null);
  const confirmBtnRef = useRef(null);

  // Focus Cancel button by default when modal opens (safe default for destructive actions)
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        if (cancelBtnRef.current) {
          cancelBtnRef.current.focus();
        }
      }, 50);
    }
  }, [isOpen]);

  // Handle Escape key and keyboard focus trapping
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        if (typeof onCancel === 'function' && !isConfirming) {
          onCancel();
        }
      } else if (e.key === 'Tab') {
        // Trap focus between Cancel and Confirm buttons
        const focusable = [cancelBtnRef.current, confirmBtnRef.current].filter(Boolean);
        if (focusable.length < 2) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onCancel, isConfirming]);

  if (!isOpen) return null;

  const currentLabel = getLanguageDisplayName(currentLanguage);
  const newLabel = getLanguageDisplayName(newLanguage);

  return (
    <div
      className="language-change-modal-backdrop animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="language-modal-title"
      aria-describedby="language-modal-desc"
      onClick={(e) => {
        // Close if student clicks outside the modal dialog box
        if (e.target === e.currentTarget && typeof onCancel === 'function' && !isConfirming) {
          onCancel();
        }
      }}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1100,
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        background: 'rgba(10, 15, 29, 0.88)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20
      }}
    >
      <div
        className="glass-panel-elevated animate-scale-up"
        style={{
          maxWidth: 480,
          width: '100%',
          padding: '28px 24px',
          borderRadius: 16,
          background: 'linear-gradient(135deg, rgba(20, 26, 47, 0.98), rgba(15, 23, 42, 0.99))',
          border: '1px solid rgba(245, 158, 11, 0.45)',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.85), 0 0 30px rgba(245, 158, 11, 0.2)',
          position: 'relative'
        }}
      >
        {/* Close Button top-right */}
        <button
          onClick={onCancel}
          disabled={isConfirming}
          aria-label="Close modal"
          style={{
            position: 'absolute',
            top: 14,
            right: 14,
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: isConfirming ? 'not-allowed' : 'pointer',
            padding: 4,
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <X size={18} />
        </button>

        {/* Warning Icon Badge */}
        <div style={{
          width: 56,
          height: 56,
          borderRadius: '50%',
          background: 'rgba(245, 158, 11, 0.15)',
          border: '1px solid rgba(245, 158, 11, 0.45)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px auto',
          boxShadow: '0 0 20px rgba(245, 158, 11, 0.3)'
        }}>
          <AlertTriangle size={28} color="#f59e0b" />
        </div>

        {/* Modal Title */}
        <h3
          id="language-modal-title"
          style={{
            fontSize: '1.35rem',
            fontWeight: 800,
            color: '#f8fafc',
            textAlign: 'center',
            margin: '0 0 10px 0',
            fontFamily: 'var(--font-heading)'
          }}
        >
          Change Programming Language?
        </h3>

        {/* Message */}
        <p
          id="language-modal-desc"
          style={{
            fontSize: '0.925rem',
            color: '#cbd5e1',
            textAlign: 'center',
            margin: '0 0 18px 0',
            lineHeight: 1.5
          }}
        >
          You are about to switch from <strong>{currentLabel}</strong> to <strong>{newLabel}</strong>.
        </p>

        {/* Language Transition Indicator Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 12,
          padding: '10px 16px',
          background: 'rgba(15, 23, 42, 0.75)',
          border: '1px solid var(--border-glass)',
          borderRadius: 10,
          marginBottom: 18,
          fontSize: '0.85rem'
        }}>
          <span style={{ fontWeight: 700, color: '#93c5fd' }}>{currentLabel}</span>
          <ArrowRight size={14} color="#94a3b8" />
          <span style={{ fontWeight: 700, color: '#f59e0b' }}>{newLabel}</span>
        </div>

        {/* Warning Callout Box */}
        <div
          className="warning-box"
          style={{
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            borderRadius: 10,
            padding: '12px 14px',
            color: '#fca5a5',
            fontSize: '0.825rem',
            lineHeight: 1.45,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 10,
            textAlign: 'left',
            marginBottom: 24
          }}
        >
          <AlertTriangle size={16} color="#ef4444" style={{ flexShrink: 0, marginTop: 2 }} />
          <span>Your current code will be deleted when you switch languages. This action cannot be undone.</span>
        </div>

        {/* Buttons */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          gap: 12
        }}>
          <button
            ref={cancelBtnRef}
            id="btn-cancel-language-change"
            onClick={onCancel}
            disabled={isConfirming}
            className="btn btn-secondary"
            style={{
              padding: '8px 18px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: isConfirming ? 'not-allowed' : 'pointer'
            }}
          >
            Cancel
          </button>

          <button
            ref={confirmBtnRef}
            id="btn-confirm-language-change"
            onClick={onConfirm}
            disabled={isConfirming}
            className="btn btn-amber glow-amber"
            style={{
              padding: '8px 20px',
              fontSize: '0.875rem',
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              cursor: isConfirming ? 'wait' : 'pointer'
            }}
          >
            <Code2 size={15} />
            <span>{isConfirming ? 'Switching...' : 'Yes, Change Language'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
