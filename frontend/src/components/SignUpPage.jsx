import React, { useState, useEffect } from 'react';
import { 
  BrainCircuit, 
  User, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  AlertCircle, 
  CheckCircle2, 
  ShieldCheck 
} from 'lucide-react';
import GoogleSetupModal from './GoogleSetupModal';

export default function SignUpPage({ onSignUpSuccess, onNavigate }) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Google Setup Modal
  const [isGoogleSetupOpen, setIsGoogleSetupOpen] = useState(false);

  // Google OAuth Client ID check
  const [googleClientId, setGoogleClientId] = useState(() => {
    return import.meta.env?.VITE_GOOGLE_CLIENT_ID || '';
  });

  useEffect(() => {
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

  // Initialize Google Identity Services
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
          remember_me: true
        })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Google sign-up verification failed.');
      }

      setSuccessMessage('Google account connected! Initializing your learning dashboard...');
      if (data.token) {
        localStorage.setItem('codeacharya_auth_token', data.token);
      }

      setTimeout(() => {
        onSignUpSuccess(data.user, data.token);
      }, 700);
    } catch (err) {
      setServerError(err.message || 'Failed to authenticate with Google. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleGoogleButtonClick = () => {
    setServerError('');
    if (!googleClientId) {
      setIsGoogleSetupOpen(true);
      return;
    }

    if (window.google?.accounts?.id) {
      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          console.log('Google One Tap status:', notification.getNotDisplayedReason?.());
        }
      });
    } else {
      setIsGoogleSetupOpen(true);
    }
  };

  const validate = () => {
    const newErrors = {};
    const trimmedName = fullName.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName) {
      newErrors.fullName = 'Full name is required.';
    } else if (trimmedName.length < 2) {
      newErrors.fullName = 'Full name must be at least 2 characters long.';
    }

    if (!trimmedEmail) {
      newErrors.email = 'Email address is required.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      newErrors.email = 'Please enter a valid email address (e.g. name@example.com).';
    }

    if (!password) {
      newErrors.password = 'Password is required.';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long.';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password.';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match.';
    }

    if (!agreeTerms) {
      newErrors.agreeTerms = 'You must accept the terms of service to create an account.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError('');
    setSuccessMessage('');

    if (!validate()) {
      return;
    }

    setIsLoading(true);

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          full_name: fullName.trim(),
          email: email.trim(),
          password
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed. Please check the entered data.');
      }

      setSuccessMessage('Account created successfully! Preparing your learning environment...');
      if (data.token) {
        localStorage.setItem('codeacharya_auth_token', data.token);
      }

      // Smooth transition to allow the success state to be visible
      setTimeout(() => {
        onSignUpSuccess(data.user, data.token);
      }, 700);
    } catch (err) {
      setServerError(err.message || 'Unable to complete registration. Please try again.');
    } finally {
      setIsLoading(false);
    }
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
      {/* Background radial glows */}
      <div style={{
        position: 'absolute',
        width: 480,
        height: 480,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(139, 92, 246, 0.14) 0%, transparent 70%)',
        top: '15%',
        right: '18%',
        filter: 'blur(55px)',
        pointerEvents: 'none'
      }} />
      <div style={{
        position: 'absolute',
        width: 420,
        height: 420,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(6, 182, 212, 0.12) 0%, transparent 70%)',
        bottom: '12%',
        left: '15%',
        filter: 'blur(50px)',
        pointerEvents: 'none'
      }} />

      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: 480,
        padding: '36px 32px',
        position: 'relative',
        zIndex: 10,
        boxShadow: '0 20px 45px -10px rgba(0, 0, 0, 0.7), 0 0 30px rgba(139, 92, 246, 0.15)',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        {/* Brand header */}
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{
            width: 54,
            height: 54,
            borderRadius: 16,
            background: 'linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 25px rgba(139, 92, 246, 0.5)',
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
            Create Your Account
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', margin: 0 }}>
            Join CodeAcharya to unlock adaptive hints, AI Viva, and personal progress analytics
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
              e.currentTarget.style.borderColor = 'rgba(139, 92, 246, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.15)';
            }}
          >
            {/* Google G icon */}
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
          margin: '18px 0',
          color: 'var(--text-subtle)',
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          <div style={{ flex: 1, height: 1, background: 'var(--border-glass)' }} />
          <span>or sign up with email</span>
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
              <strong style={{ display: 'block', color: '#fda4af', marginBottom: 2 }}>Registration Error</strong>
              <span>{serverError}</span>
            </div>
          </div>
        )}

        {/* Success message banner */}
        {successMessage && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            borderRadius: 10,
            padding: '12px 14px',
            marginBottom: 20,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            color: '#34d399',
            fontSize: '0.85rem'
          }} role="status">
            <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0 }} />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Sign up form */}
        <form onSubmit={handleSubmit} noValidate>
          {/* Full name input */}
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="signup-name" style={{
              display: 'block',
              fontSize: '0.825rem',
              fontWeight: 600,
              color: 'var(--text-main)',
              marginBottom: 6
            }}>
              Full Name
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <User size={17} color="var(--text-subtle)" style={{
                position: 'absolute',
                left: 14,
                pointerEvents: 'none'
              }} />
              <input
                id="signup-name"
                type="text"
                autoComplete="name"
                placeholder="Ada Lovelace"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  if (errors.fullName) setErrors(prev => ({ ...prev, fullName: null }));
                }}
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '11px 14px 11px 40px',
                  borderRadius: 10,
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: `1px solid ${errors.fullName ? '#f43f5e' : 'var(--border-glass)'}`,
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                  boxShadow: errors.fullName ? '0 0 10px rgba(244, 63, 94, 0.2)' : 'none'
                }}
                onFocus={(e) => {
                  if (!errors.fullName) e.target.style.borderColor = '#8b5cf6';
                }}
                onBlur={(e) => {
                  if (!errors.fullName) e.target.style.borderColor = 'var(--border-glass)';
                }}
              />
            </div>
            {errors.fullName && (
              <p style={{ fontSize: '0.75rem', color: '#f87171', marginTop: 4, marginLeft: 2 }}>
                {errors.fullName}
              </p>
            )}
          </div>

          {/* Email input */}
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="signup-email" style={{
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
                id="signup-email"
                type="email"
                autoComplete="email"
                placeholder="ada@example.com"
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
                  if (!errors.email) e.target.style.borderColor = '#8b5cf6';
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
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="signup-password" style={{
              display: 'block',
              fontSize: '0.825rem',
              fontWeight: 600,
              color: 'var(--text-main)',
              marginBottom: 6
            }}>
              Password
            </label>
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
                id="signup-password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                placeholder="At least 8 characters"
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
                  if (!errors.password) e.target.style.borderColor = '#8b5cf6';
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

          {/* Confirm Password input */}
          <div style={{ marginBottom: 18 }}>
            <label htmlFor="signup-confirm-password" style={{
              display: 'block',
              fontSize: '0.825rem',
              fontWeight: 600,
              color: 'var(--text-main)',
              marginBottom: 6
            }}>
              Confirm Password
            </label>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            }}>
              <ShieldCheck size={17} color="var(--text-subtle)" style={{
                position: 'absolute',
                left: 14,
                pointerEvents: 'none'
              }} />
              <input
                id="signup-confirm-password"
                type={showConfirmPassword ? 'text' : 'password'}
                autoComplete="new-password"
                placeholder="Re-type your password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (errors.confirmPassword) setErrors(prev => ({ ...prev, confirmPassword: null }));
                }}
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '11px 44px 11px 40px',
                  borderRadius: 10,
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: `1px solid ${errors.confirmPassword ? '#f43f5e' : 'var(--border-glass)'}`,
                  color: 'var(--text-main)',
                  fontSize: '0.9rem',
                  outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                  boxShadow: errors.confirmPassword ? '0 0 10px rgba(244, 63, 94, 0.2)' : 'none'
                }}
                onFocus={(e) => {
                  if (!errors.confirmPassword) e.target.style.borderColor = '#8b5cf6';
                }}
                onBlur={(e) => {
                  if (!errors.confirmPassword) e.target.style.borderColor = 'var(--border-glass)';
                }}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(prev => !prev)}
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                title={showConfirmPassword ? "Hide password" : "Show password"}
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
                {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p style={{ fontSize: '0.75rem', color: '#f87171', marginTop: 4, marginLeft: 2 }}>
                {errors.confirmPassword}
              </p>
            )}
          </div>

          {/* Terms & Conditions Acceptance Checkbox */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
              <input
                id="signup-agree-terms"
                type="checkbox"
                checked={agreeTerms}
                onChange={(e) => {
                  setAgreeTerms(e.target.checked);
                  if (errors.agreeTerms) setErrors(prev => ({ ...prev, agreeTerms: null }));
                }}
                disabled={isLoading}
                style={{
                  accentColor: '#8b5cf6',
                  width: 17,
                  height: 17,
                  marginTop: 2,
                  cursor: 'pointer'
                }}
              />
              <label htmlFor="signup-agree-terms" style={{
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                lineHeight: 1.45,
                cursor: 'pointer',
                userSelect: 'none'
              }}>
                I agree to the <span style={{ color: '#a5b4fc', textDecoration: 'underline' }}>Terms of Service</span> and <span style={{ color: '#a5b4fc', textDecoration: 'underline' }}>Privacy Policy</span> for CodeAcharya.
              </label>
            </div>
            {errors.agreeTerms && (
              <p style={{ fontSize: '0.75rem', color: '#f87171', marginTop: 4, marginLeft: 27 }}>
                {errors.agreeTerms}
              </p>
            )}
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
              background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
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
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <span>Create CodeAcharya Account</span>
                <ArrowRight size={17} />
              </>
            )}
          </button>
        </form>

        {/* Sign in prompt */}
        <div style={{
          textAlign: 'center',
          marginTop: 22,
          paddingTop: 16,
          borderTop: '1px solid var(--border-glass)',
          fontSize: '0.85rem',
          color: 'var(--text-muted)'
        }}>
          Already have an account?{' '}
          <button
            type="button"
            onClick={() => onNavigate('login')}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#a5b4fc',
              fontWeight: 600,
              cursor: 'pointer',
              textDecoration: 'underline',
              padding: 0,
              fontFamily: 'inherit',
              fontSize: 'inherit'
            }}
          >
            Sign In
          </button>
        </div>
      </div>

      {/* Google Setup Guidance Modal */}
      <GoogleSetupModal
        isOpen={isGoogleSetupOpen}
        onClose={() => setIsGoogleSetupOpen(false)}
      />

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
