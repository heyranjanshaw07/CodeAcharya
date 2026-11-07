import React from 'react';
import { 
  Lightbulb, 
  HelpCircle, 
  CheckCircle, 
  ArrowRight, 
  X, 
  Sparkles, 
  AlertCircle,
  Brain,
  ShieldAlert
} from 'lucide-react';

export default function ProgressiveHintModal({ 
  isOpen, 
  onClose, 
  hintsHistory, 
  currentLevel, 
  onUnlockNextLevel, 
  isLoading,
  problemTitle
}) {
  if (!isOpen) return null;

  const currentHint = hintsHistory[currentLevel - 1];

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      zIndex: 100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 20
    }}>
      <div 
        className="glass-panel-elevated animate-slide-down" 
        style={{
          width: '100%',
          maxWidth: 720,
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: 28,
          position: 'relative',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 35px rgba(99, 102, 241, 0.25)'
        }}
      >
        {/* Close Button */}
        <button 
          onClick={onClose}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(245, 158, 11, 0.4)'
          }}>
            <Lightbulb size={24} color="#fff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
              Socratic Progressive Hint System
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Guided problem-solving instead of giving the answer right away
            </p>
          </div>
        </div>

        {/* Level Indicator Stepper */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: 8,
          marginBottom: 24,
          background: 'rgba(15, 23, 42, 0.5)',
          padding: 8,
          borderRadius: 10,
          border: '1px solid var(--border-glass)'
        }}>
          {[
            { lvl: 1, label: '1. Conceptual' },
            { lvl: 2, label: '2. Algorithmic' },
            { lvl: 3, label: '3. Structural' },
            { lvl: 4, label: '4. Resolution' }
          ].map(step => {
            const isUnlocked = currentLevel >= step.lvl;
            const isCurrent = currentLevel === step.lvl;
            return (
              <div 
                key={step.lvl}
                style={{
                  padding: '8px 10px',
                  borderRadius: 8,
                  textAlign: 'center',
                  background: isCurrent 
                    ? 'rgba(99, 102, 241, 0.25)' 
                    : isUnlocked 
                      ? 'rgba(16, 185, 129, 0.15)' 
                      : 'rgba(255, 255, 255, 0.03)',
                  border: `1px solid ${
                    isCurrent 
                      ? '#6366f1' 
                      : isUnlocked 
                        ? 'rgba(16, 185, 129, 0.3)' 
                        : 'transparent'
                  }`,
                  color: isCurrent 
                    ? '#a5b4fc' 
                    : isUnlocked 
                      ? '#34d399' 
                      : 'var(--text-subtle)',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  transition: 'all 0.2s'
                }}
              >
                {step.label}
              </div>
            );
          })}
        </div>

        {/* Current Active Hint */}
        {currentHint && (
          <div 
            style={{
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: 12,
              padding: 20,
              marginBottom: 20,
              position: 'relative'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <span className="badge badge-medium">
                {currentHint.hint_title}
              </span>
              <span style={{ fontSize: '0.75rem', color: '#f59e0b', fontWeight: 600 }}>
                Level {currentLevel} of 4
              </span>
            </div>

            <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: '#f8fafc', marginBottom: 16 }}>
              {currentHint.hint_content}
            </p>

            {/* Thought Questions */}
            {currentHint.thought_questions && currentHint.thought_questions.length > 0 && (
              <div style={{
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px dashed rgba(99, 102, 241, 0.35)',
                borderRadius: 8,
                padding: '12px 16px',
                marginTop: 12
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#818cf8', fontSize: '0.8rem', fontWeight: 600, marginBottom: 8 }}>
                  <Brain size={15} />
                  <span>Reflective Questions to Ask Yourself:</span>
                </div>
                <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.85rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {currentHint.thought_questions.map((q, idx) => (
                    <li key={idx} style={{ marginBottom: 4 }}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Previous Unlocked Hints Accordion */}
        {hintsHistory.length > 1 && (
          <div style={{ marginBottom: 20 }}>
            <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
              Previously Unlocked Clues
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {hintsHistory.slice(0, currentLevel - 1).map((h, i) => (
                <div key={i} style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-glass)',
                  padding: '10px 14px',
                  borderRadius: 8,
                  fontSize: '0.825rem'
                }}>
                  <strong style={{ color: '#94a3b8' }}>{h.hint_title}: </strong>
                  <span style={{ color: '#cbd5e1' }}>{h.hint_content}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 16, borderTop: '1px solid var(--border-glass)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <ShieldAlert size={14} color="#f59e0b" />
            <span>Encourages cognitive reflection for deep retention</span>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-secondary" onClick={onClose}>
              Try Coding With This Hint
            </button>

            {currentLevel < 4 && (
              <button 
                className="btn btn-amber"
                onClick={onUnlockNextLevel}
                disabled={isLoading}
              >
                {isLoading ? 'Consulting Mentor...' : (
                  <>
                    <span>Unlock Level {currentLevel + 1} Hint</span>
                    <ArrowRight size={15} />
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
