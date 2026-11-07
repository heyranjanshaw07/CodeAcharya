import React, { useState, useEffect } from 'react';
import { 
  BrainCircuit, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  AlertCircle, 
  CheckCircle2,
  UserCheck
} from 'lucide-react';
import GoogleSetupModal from './GoogleSetupModal';
import ForgotPasswordModal from './ForgotPasswordModal';

export default function LoginPage({ onLoginSuccess, onNavigate, redirectTarget = 'workspace' }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Modals
  const [isGoogleSetupOpen, setIsGoogleSetupOpen] = useState(false);
  const [isForgotOpen, setIsForgotOpen] = useState(false);

  // Google OAuth Client ID check
  const [googleClientId, setGoogleClientId] = useState(() => {
    return import.meta.env?.VITE_GOOGLE_CLIENT_ID || '';
  });

  useEffect(() => {
    // Check backend for configured Google Client ID if not found in frontend env
    if (!googleClientId) {
      fetch('/api/auth/google/config')
        .then(res => res.json())
        .then(data => {
          if (data?.client_id) {
            setGoogleClientId(data.client_id);
          }
        })
        .catch(() => {});
    }
  }, [googleClientId]);

  // Initialize Google Identity Services when script and Client ID are ready
  useEffect(() => {
    if (googleClientId && window.google?.accounts?.id) {
      try {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: handleGoogleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: true
        });
      } catch (err) {
        console.warn('Google Identity initialization warning:', err);
      }
    }
  }, [googleClientId]);

  const handleGoogleCredentialResponse = async (response) => {
    if (!response || !response.credential) {
      setServerError('No credentials returned from Google authentication.');
      return;
    }

    setIsGoogleLoading(true);
    setServerError('');

    try {
      const res = await fetch('/api/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          id_token: response.credential,
          remember_me: rememberMe
        })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Google sign-in verification failed.');
      }

      if (data.token) {
        localStorage.setItem('codeacharya_auth_token', data.token);
      }
      onLoginSuccess(data.user, data.token);
    } catch (err) {
      setServerError(err.message || 'Failed to authenticate with Google. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleGoogleButtonClick = () => {
    setServerError('');
    if (!googleClientId) {
      // Guide developer on how to configure Google OAuth in Google Cloud Console
      setIsGoogleSetupOpen(true);
      return;
    }

    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // If One Tap was dismissed or skipped, open setup guide or prompt
          console.log('Google One Tap status:', notification.getNotDisplayedReason?.());
        }
      });
    } else {
      setIsGoogleSetupOpen(true);
    }
  };

  const validate = () => {
    const newErrors = {};
    const trimmedEmail = email.trim();

    if (!trimmedEmail) {
      newErrors.email = 'Email address is required.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      newErrors.email = 'Please enter a valid email address (e.g. name@example.com).';
    }

    if (!password) {
      newErrors.password = 'Password is required.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');

    if (!validate()) {
      return;
    }

    setIsLoading(true);

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          email: email.trim(),
          password,
          remember_me: rememberMe
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Login failed. Please verify your credentials.');
      }

      // Successful login
      if (data.token) {
        localStorage.setItem('codeacharya_auth_token', data.token);
      }
      onLoginSuccess(data.user, data.token);
    } catch (err) {
      setServerError(err.message || 'Unable to connect to server. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFillDemo = () => {
    setEmail('student@codeacharya.ai');
    setPassword('Password123!');
    setErrors({});
    setServerError('');
  };

  return (
    <div style={{
      minHeight: 'calc(100vh - 80px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '32px 16px',
      position: 'relative'
    }}>
      {/* Ambient background glows */}
      <div style={{
        position: 'absolute',
        width: 450,
        height: 450,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)',
        top: '20%',
        left: '15%',
        filter: 'blur(50px)',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute',
        width: 400,
        height: 400,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(6, 182, 212, 0.12) 0%, transparent 70%)',
        bottom: '15%',
        right: '15%',
        filter: 'blur(50px)',
        pointerEvents: 'none'
      }} />

      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: 460,
        padding: '36px 32px',
        position: 'relative',
        zIndex: 10,
        boxShadow: '0 20px 45px -10px rgba(0, 0, 0, 0.7), 0 0 30px rgba(99, 102, 241, 0.15)',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        {/* Brand header */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{
            width: 54,
            height: 54,
            borderRadius: 16,
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 25px rgba(99, 102, 241, 0.5)',
            marginBottom: 14
          }}>
            <BrainCircuit size={30} color="#fff" />
          </div>
          <h1 style={{
            fontSize: '1.65rem',
            fontWeight: 700,
            fontFamily: 'var(--font-heading)',
            letterSpacing: '-0.02em',
            background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: 6
          }}>
            Welcome Back
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', margin: 0 }}>
            Sign in to continue your personalized algorithmic learning journey
          </p>
        </div>

        {/* Continue with Google button */}
        <div style={{ marginBottom: 20 }}>
          <button
            type="button"
            onClick={handleGoogleButtonClick}
            disabled={isGoogleLoading || isLoading}
            style={{
              width: '100%',
              padding: '11px 16px',
              borderRadius: 10,
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              color: 'var(--text-main)',
              fontSize: '0.9rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 12,
              cursor: (isGoogleLoading || isLoading) ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
            }}
          >
            {/* Official Google 'G' icon */}
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>{isGoogleLoading ? 'Connecting to Google...' : 'Continue with Google'}</span>
          </button>
        </div>

        {/* Divider */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          margin: '20px 0',
          color: 'var(--text-subtle)',
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          <div style={{ flex: 1, height: 1, background: 'var(--border-glass)' }} />
          <span>or sign in with email</span>
          <div style={{ flex: 1, height: 1, background: 'var(--border-glass)' }} />
        </div>

        {/* Server error alert banner */}
        {serverError && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.35)',
            borderRadius: 10,
            padding: '12px 14px',
            marginBottom: 20,
            display: 'flex',
            alignItems: 'flex-start',
            gap: 10,
            color: '#fca5a5',
            fontSize: '0.85rem'
          }} role="alert">
            <AlertCircle size={18} color="#f43f5e" style={{ flexShrink: 0, marginTop: 1 }} />
            <div>
              <strong style={{ display: 'block', color: '#fda4af', marginBottom: 2 }}>Authentication Failed</strong>
              <span>{serverError}</span>
            </div>
          </div>
        )}

        {/* Login form */}
        <form onSubmit={handleSubmit} noValidate>
          {/* Email input */}
          <div style={{ marginBottom: 18 }}>
            <label htmlFor="login-email" style={{
              display: 'block',
              fontSize: '0.825rem',
              fontWeight: 600,
              color: 'var(--text-main)',
              marginBottom: 6
            }}>
              Email Address
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <Mail size={17} color="var(--text-subtle)" style={{
                position: 'absolute',
                left: 14,
                pointerEvents: 'none'
              }} />
              <input
                id="login-email"
                type="email"
                autoComplete="email"
                placeholder="name@codeacharya.ai"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) setErrors(prev => ({ ...prev, email: null }));
                }}
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '11px 14px 11px 40px',
                  borderRadius: 10,
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: `1px solid ${errors.email ? '#f43f5e' : 'var(--border-glass)'}`,
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                  boxShadow: errors.email ? '0 0 10px rgba(244, 63, 94, 0.2)' : 'none'
                }}
                onFocus={(e) => {
                  if (!errors.email) e.target.style.borderColor = '#6366f1';
                }}
                onBlur={(e) => {
                  if (!errors.email) e.target.style.borderColor = 'var(--border-glass)';
                }}
              />
            </div>
            {errors.email && (
              <p style={{ fontSize: '0.75rem', color: '#f87171', marginTop: 4, marginLeft: 2 }}>
                {errors.email}
              </p>
            )}
          </div>

          {/* Password input */}
          <div style={{ marginBottom: 18 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <label htmlFor="login-password" style={{
                fontSize: '0.825rem',
                fontWeight: 600,
                color: 'var(--text-main)'
              }}>
                Password
              </label>
              <button
                type="button"
                onClick={() => setIsForgotOpen(true)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#818cf8',
                  fontSize: '0.775rem',
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                Forgot Password?
              </button>
            </div>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <Lock size={17} color="var(--text-subtle)" style={{
                position: 'absolute',
                left: 14,
                pointerEvents: 'none'
              }} />
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) setErrors(prev => ({ ...prev, password: null }));
                }}
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '11px 44px 11px 40px',
                  borderRadius: 10,
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: `1px solid ${errors.password ? '#f43f5e' : 'var(--border-glass)'}`,
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                  boxShadow: errors.password ? '0 0 10px rgba(244, 63, 94, 0.2)' : 'none'
                }}
                onFocus={(e) => {
                  if (!errors.password) e.target.style.borderColor = '#6366f1';
                }}
                onBlur={(e) => {
                  if (!errors.password) e.target.style.borderColor = 'var(--border-glass)';
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(prev => !prev)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                title={showPassword ? "Hide password" : "Show password"}
                style={{
                  position: 'absolute',
                  right: 12,
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: 4,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 4
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.password && (
              <p style={{ fontSize: '0.75rem', color: '#f87171', marginTop: 4, marginLeft: 2 }}>
                {errors.password}
              </p>
            )}
          </div>

          {/* Remember me checkbox */}
          <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              id="login-remember-me"
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              disabled={isLoading}
              style={{
                accentColor: '#6366f1',
                width: 16,
                height: 16,
                cursor: 'pointer'
              }}
            />
            <label htmlFor="login-remember-me" style={{
              fontSize: '0.825rem',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              userSelect: 'none'
            }}>
              Remember me on this browser (30 days)
            </label>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary glow-primary"
            style={{
              width: '100%',
              padding: '12px 18px',
              fontSize: '0.95rem',
              fontWeight: 600,
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.75 : 1,
              transition: 'all 0.2s ease'
            }}
          >
            {isLoading ? (
              <>
                <span style={{
                  width: 16,
                  height: 16,
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderTopColor: '#ffffff',
                  borderRadius: '50%',
                  display: 'inline-block',
                  animation: 'spin 0.8s linear infinite'
                }} />
                <span>Signing In...</span>
              </>
            ) : (
              <>
                <span>Sign In to Account</span>
                <ArrowRight size={17} />
              </>
            )}
          </button>
        </form>

        {/* Demo Account Quick-Fill Card */}
        <div style={{
          marginTop: 22,
          padding: '12px 14px',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px dashed rgba(99, 102, 241, 0.3)',
          borderRadius: 10,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 10
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.775rem', color: '#818cf8', fontWeight: 600 }}>
              <UserCheck size={14} /> Quick Demo Account
            </div>
            <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: 2 }}>
              student@codeacharya.ai / Password123!
            </div>
          </div>
          <button
            type="button"
            onClick={handleFillDemo}
            className="btn btn-secondary"
            style={{
              padding: '5px 10px',
              fontSize: '0.75rem',
              borderRadius: 6,
              background: 'rgba(99, 102, 241, 0.15)',
              color: '#a5b4fc',
              border: '1px solid rgba(99, 102, 241, 0.35)'
            }}
          >
            Auto Fill
          </button>
        </div>

        {/* Sign up prompt */}
        <div style={{
          textAlign: 'center',
          marginTop: 22,
          paddingTop: 16,
          borderTop: '1px solid var(--border-glass)',
          fontSize: '0.85rem',
          color: 'var(--text-muted)'
        }}>
          Don't have an account yet?{' '}
          <button
            type="button"
            onClick={() => onNavigate('signup')}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#818cf8',
              fontWeight: 600,
              cursor: 'pointer',
              textDecoration: 'underline',
              padding: 0,
              fontFamily: 'inherit',
              fontSize: 'inherit'
            }}
          >
            Create an Account
          </button>
        </div>
      </div>

      {/* Google Setup Guidance Modal */}
      <GoogleSetupModal
        isOpen={isGoogleSetupOpen}
        onClose={() => setIsGoogleSetupOpen(false)}
      />

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        isOpen={isForgotOpen}
        onClose={() => setIsForgotOpen(false)}
      />

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
