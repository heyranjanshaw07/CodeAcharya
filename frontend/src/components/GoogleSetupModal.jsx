import React from 'react';
import { ShieldCheck, ExternalLink, X, Copy, Check, Terminal, KeyRound } from 'lucide-react';

export default function GoogleSetupModal({ isOpen, onClose }) {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const envSnippet = `GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com\nGOOGLE_CLIENT_SECRET=your-client-secret`;

  const handleCopy = () => {
    navigator.clipboard.writeText(envSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 16,
      backgroundColor: 'rgba(5, 8, 22, 0.78)',
      backdropFilter: 'blur(8px)'
    }} onClick={onClose}>
      <div 
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: 580,
          padding: 28,
          borderRadius: 16,
          border: '1px solid rgba(99, 102, 241, 0.3)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 30px rgba(99, 102, 241, 0.2)',
          position: 'relative'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 18,
            right: 18,
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: 4
          }}
          aria-label="Close"
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc05 75%, #ea4335 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(66, 133, 244, 0.35)'
          }}>
            <KeyRound size={22} color="#fff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, color: 'var(--text-main)' }}>
              Google OAuth 2.0 Setup Guide
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
              Connect your verified Google Cloud project credentials for real Google Sign-In
            </p>
          </div>
        </div>

        <div style={{
          background: 'rgba(15, 23, 42, 0.75)',
          borderRadius: 10,
          border: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '16px 18px',
          marginBottom: 18,
          fontSize: '0.85rem',
          lineHeight: 1.55,
          color: 'var(--text-muted)'
        }}>
          <p style={{ margin: '0 0 8px 0', color: 'var(--text-main)', fontWeight: 600 }}>
            Quick Setup Steps:
          </p>
          <ol style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
            <li>Open the <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer" style={{ color: '#818cf8', textDecoration: 'underline' }}>Google Cloud Console Credentials</a> page.</li>
            <li>Configure your <strong>OAuth Consent Screen</strong> (Scopes: <code>openid</code>, <code>email</code>, <code>profile</code>).</li>
            <li>Create an <strong>OAuth 2.0 Client ID</strong> (Application type: <em>Web application</em>).</li>
            <li>Add Authorized JavaScript origins: <code>http://localhost:5173</code> and <code>http://127.0.0.1:5173</code>.</li>
            <li>Save your <strong>Client ID</strong> and <strong>Client Secret</strong> into <code>backend/.env</code> and <code>frontend/.env</code>.</li>
          </ol>
        </div>

        <div style={{ marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <span style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              Environment Variables (.env):
            </span>
            <button
              onClick={handleCopy}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5,
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid rgba(99, 102, 241, 0.35)',
                color: '#a5b4fc',
                borderRadius: 6,
                padding: '4px 8px',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              {copied ? <Check size={13} color="#34d399" /> : <Copy size={13} />}
              {copied ? 'Copied!' : 'Copy Snippet'}
            </button>
          </div>
          <pre style={{
            background: 'rgba(10, 15, 29, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 8,
            padding: 12,
            fontFamily: 'var(--font-mono)',
            fontSize: '0.775rem',
            color: '#38bdf8',
            overflowX: 'auto',
            margin: 0
          }}>
            {envSnippet}
          </pre>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{ padding: '8px 16px', fontSize: '0.85rem' }}
          >
            Close
          </button>
          <a
            href="https://console.cloud.google.com/apis/credentials"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary glow-primary"
            style={{ padding: '8px 16px', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: 6 }}
          >
            <span>Open Google Cloud Console</span>
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
}
