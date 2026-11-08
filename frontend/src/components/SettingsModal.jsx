import React, { useState } from 'react';
import { 
  Settings, 
  Sparkles, 
  Brain, 
  X, 
  Check, 
  ShieldCheck,
  UserCheck
} from 'lucide-react';

export default function SettingsModal({ 
  isOpen, 
  onClose, 
  onSaveSettings, 
  currentPersona, 
  hasKey,
  isAssessmentMode = true,
  onToggleAssessmentMode
}) {
  const [selectedPersona, setSelectedPersona] = useState(currentPersona || 'socratic');
  const [isSaved, setIsSaved] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveSettings({
      mentor_persona: selectedPersona
    });
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 900);
  };

  const personas = [
    {
      id: 'socratic',
      title: 'Socratic Guide (Default)',
      desc: 'Never gives the direct answer. Asks progressive questions that lead you to discover the solution yourself.'
    },
    {
      id: 'strict',
      title: 'Rigorous Examiner',
      desc: 'Formal university viva style. Emphasizes formal Big-O proofs, memory stack frames, and boundary conditions.'
    },
    {
      id: 'friendly',
      title: 'Encouraging Peer',
      desc: 'Approachable, warm tone with intuitive real-world analogies and supportive debugging praise.'
    }
  ];

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      zIndex: 110,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 20
    }}>
      <div className="glass-panel-elevated animate-slide-down" style={{
        width: '100%',
        maxWidth: 580,
        padding: 28,
        position: 'relative'
      }}>
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

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Settings size={22} color="#fff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
              AI Mentor Settings
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Customize teaching persona and assessment environment
            </p>
          </div>
        </div>

        {/* Copy-Paste Assessment Mode Preference */}
        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', fontWeight: 600, marginBottom: 10 }}>
            <ShieldCheck size={16} color={isAssessmentMode ? '#ef4444' : '#10b981'} />
            Assessment Environment Policy:
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <div
              onClick={() => onToggleAssessmentMode && onToggleAssessmentMode(true)}
              style={{
                background: isAssessmentMode ? 'rgba(239, 68, 68, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${isAssessmentMode ? '#ef4444' : 'var(--border-glass)'}`,
                padding: '12px 14px',
                borderRadius: 10,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                <strong style={{ fontSize: '0.85rem', color: isAssessmentMode ? '#fca5a5' : '#f8fafc' }}>
                  🔒 Assessment Mode
                </strong>
                {isAssessmentMode && <Check size={14} color="#ef4444" />}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                Paste disabled in Coding & AI Viva. Copying is allowed.
              </div>
            </div>

            <div
              onClick={() => onToggleAssessmentMode && onToggleAssessmentMode(false)}
              style={{
                background: !isAssessmentMode ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${!isAssessmentMode ? '#10b981' : 'var(--border-glass)'}`,
                padding: '12px 14px',
                borderRadius: 10,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                <strong style={{ fontSize: '0.85rem', color: !isAssessmentMode ? '#6ee7b7' : '#f8fafc' }}>
                  🔓 Practice Mode
                </strong>
                {!isAssessmentMode && <Check size={14} color="#10b981" />}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                Paste allowed freely during unrestricted self-study.
              </div>
            </div>
          </div>
        </div>

        {/* Mentor Persona Selector */}
        <div style={{ marginBottom: 28 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.85rem', fontWeight: 600, marginBottom: 12 }}>
            <Brain size={16} color="#8b5cf6" />
            Mentor Teaching Persona:
          </label>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {personas.map(p => (
              <div 
                key={p.id}
                onClick={() => setSelectedPersona(p.id)}
                style={{
                  background: selectedPersona === p.id ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.02)',
                  border: `1px solid ${selectedPersona === p.id ? '#6366f1' : 'var(--border-glass)'}`,
                  padding: '12px 16px',
                  borderRadius: 10,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontWeight: 600, fontSize: '0.9rem', color: selectedPersona === p.id ? '#a5b4fc' : '#f8fafc' }}>
                    {p.title}
                  </span>
                  {selectedPersona === p.id && <UserCheck size={16} color="#6366f1" />}
                </div>
                <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {p.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            {isSaved ? (
              <>
                <Check size={16} /> Saved!
              </>
            ) : 'Save Preferences'}
          </button>
        </div>
      </div>
    </div>
  );
}
