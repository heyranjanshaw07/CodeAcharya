import React, { useEffect, useRef } from 'react';
import { LogOut, AlertTriangle, X, RefreshCw } from 'lucide-react';

export default function LogoutConfirmModal({ 
  isOpen, 
  onClose, 
  onConfirmLogout, 
  isLoggingOut,
  logoutError,
  onRetry
}) {
  const modalRef = useRef(null);
  const cancelBtnRef = useRef(null);

  // Keyboard navigation & accessibility: Escape key closes modal safely
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && !isLoggingOut) {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    
    // Auto focus the Cancel button for safety and fast keyboard dismiss
    if (cancelBtnRef.current) {
      cancelBtnRef.current.focus();
    }

    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isLoggingOut, onClose]);

  if (!isOpen) return null;

  // Safe backdrop click: clicking outside the dialog card safely closes the modal without logging out
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !isLoggingOut) {
      onClose();
    }
  };

  return (
    <div 
      onClick={handleBackdropClick}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(5, 8, 16, 0.75)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        padding: 16,
        animation: 'fadeIn 0.2s ease-out'
      }}
      aria-hidden={!isOpen}
    >
      <div 
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="logout-dialog-title"
        aria-describedby="logout-dialog-desc"
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: 440,
          padding: '28px 24px',
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 35px rgba(244, 63, 94, 0.2)',
          position: 'relative'
        }}
      >
        {/* Close "X" button (disabled during logout) */}
        <button
          type="button"
          onClick={onClose}
          disabled={isLoggingOut}
          aria-label="Close dialog"
          title="Close dialog"
          style={{
            position: 'absolute',
            top: 16,
            right: 16,
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: isLoggingOut ? 'not-allowed' : 'pointer',
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
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 18
        }}>
          <div style={{
            width: 58,
            height: 58,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, rgba(244, 63, 94, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)',
            border: '1px solid rgba(244, 63, 94, 0.35)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(244, 63, 94, 0.25)'
          }}>
            <LogOut size={28} color="#f43f5e" />
          </div>
        </div>

        {/* Modal Title & Description */}
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <h2 
            id="logout-dialog-title" 
            style={{
              fontSize: '1.25rem',
              fontWeight: 700,
              fontFamily: 'var(--font-heading)',
              color: '#ffffff',
              marginBottom: 8
            }}
          >
            Are you sure you want to log out?
          </h2>
          <p 
            id="logout-dialog-desc"
            style={{
              fontSize: '0.875rem',
              color: 'var(--text-muted)',
              lineHeight: 1.5,
              margin: 0
            }}
          >
            You will need to sign in again to access your account.
          </p>
        </div>

        {/* Optional Error / Retry Display */}
        {logoutError && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            borderRadius: 8,
            padding: '10px 14px',
            marginBottom: 20,
            fontSize: '0.8rem',
            color: '#fca5a5',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 8
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <AlertTriangle size={15} color="#f43f5e" />
              <span>{logoutError}</span>
            </div>
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                disabled={isLoggingOut}
                className="btn btn-secondary"
                style={{
                  padding: '3px 8px',
                  fontSize: '0.725rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4
                }}
              >
                <RefreshCw size={12} /> Retry
              </button>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          gap: 12,
          flexWrap: 'wrap'
        }}>
          {/* Cancel button: closes modal, preserves auth */}
          <button
            ref={cancelBtnRef}
            type="button"
            onClick={onClose}
            disabled={isLoggingOut}
            className="btn btn-secondary"
            style={{
              flex: 1,
              padding: '10px 16px',
              fontWeight: 600,
              fontSize: '0.875rem',
              borderRadius: 8,
              cursor: isLoggingOut ? 'not-allowed' : 'pointer'
            }}
          >
            Cancel
          </button>

          {/* Yes, Log Out button: executes logout */}
          <button
            type="button"
            onClick={onConfirmLogout}
            disabled={isLoggingOut}
            className="btn"
            style={{
              flex: 1,
              padding: '10px 16px',
              fontWeight: 600,
              fontSize: '0.875rem',
              borderRadius: 8,
              background: 'linear-gradient(135deg, #f43f5e 0%, #e11d48 100%)',
              color: '#ffffff',
              boxShadow: '0 4px 14px rgba(244, 63, 94, 0.35)',
              cursor: isLoggingOut ? 'not-allowed' : 'pointer',
              opacity: isLoggingOut ? 0.75 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6
            }}
          >
            {isLoggingOut ? (
              <>
                <span style={{
                  width: 14,
                  height: 14,
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderTopColor: '#ffffff',
                  borderRadius: '50%',
                  display: 'inline-block',
                  animation: 'spin 0.8s linear infinite'
                }} />
                <span>Logging out...</span>
              </>
            ) : (
              <>
                <LogOut size={16} />
                <span>Yes, Log Out</span>
              </>
            )}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: scale(0.96); }
          to { opacity: 1; transform: scale(1); }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
