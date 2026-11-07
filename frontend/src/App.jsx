import React, { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import Workspace from './components/Workspace';
import VivaRoom from './components/VivaRoom';
import SkillDashboard from './components/SkillDashboard';
import RecommendationsView from './components/RecommendationsView';
import PerformanceDashboard from './components/PerformanceDashboard';
import SettingsModal from './components/SettingsModal';
import LoginPage from './components/LoginPage';
import SignUpPage from './components/SignUpPage';
import LogoutConfirmModal from './components/LogoutConfirmModal';
import { BrainCircuit } from 'lucide-react';

const VALID_TABS = ['workspace', 'viva', 'performance', 'analytics', 'recommendations', 'login', 'signup'];
const PROTECTED_TABS = ['workspace', 'viva', 'performance', 'analytics', 'recommendations'];

export default function App() {
  // Authentication state
  const [user, setUser] = useState(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState('');

  // Destination to return to after logging in
  const [redirectTarget, setRedirectTarget] = useState(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const redir = params.get('redirect');
      if (redir && PROTECTED_TABS.includes(redir)) return redir;
    }
    return null;
  });

  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tabParam = params.get('tab');
      if (VALID_TABS.includes(tabParam)) return tabParam;

      const hashParam = window.location.hash.replace('#', '');
      if (VALID_TABS.includes(hashParam)) return hashParam;
    }
    return 'workspace';
  });

  const [navHistory, setNavHistory] = useState([]);
  const [problems, setProblems] = useState([]);
  const [selectedProblemId, setSelectedProblemId] = useState(null);
  const [studentProfile, setStudentProfile] = useState(null);
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('codeacharya_preferred_lang');
    if (saved === 'javascript' || saved === 'js') return 'c';
    return saved || 'python';
  });
  const [code, setCode] = useState('');
  const workspaceLangHandlerRef = useRef(null);

  const applyLanguage = (newLang) => {
    setLanguage(newLang);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('codeacharya_preferred_lang', newLang);
    }
  };

  const handleHeaderSetLanguage = (newLang) => {
    if (activeTab === 'workspace' && typeof workspaceLangHandlerRef.current === 'function') {
      workspaceLangHandlerRef.current(newLang);
      return;
    }
    applyLanguage(newLang);
  };
  
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [persona, setPersona] = useState('socratic');
  const [hasGeminiKey, setHasGeminiKey] = useState(false);

  // Global Assessment Mode policy: enforces paste restrictions across Coding & Viva
  const [isAssessmentMode, setIsAssessmentMode] = useState(() => {
    if (typeof localStorage !== 'undefined') {
      const saved = localStorage.getItem('codeacharya_assessment_mode');
      return saved !== 'false'; // Default to true (Restricted Assessment Mode)
    }
    return true;
  });

  const handleSetAssessmentMode = (val) => {
    setIsAssessmentMode(val);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('codeacharya_assessment_mode', val ? 'true' : 'false');
    }
  };

  // Install transparent global fetch interceptor to attach Bearer token and credentials
  useEffect(() => {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      let [resource, config] = args;
      const token = localStorage.getItem('codeacharya_auth_token');
      
      const url = typeof resource === 'string' ? resource : resource?.url;
      if (url && (url.startsWith('/api') || url.includes('/api/'))) {
        config = config ? { ...config } : {};
        const headers = new Headers(config.headers || {});
        if (token && !headers.has('Authorization')) {
          headers.set('Authorization', `Bearer ${token}`);
        }
        config.headers = headers;
        config.credentials = config.credentials || 'include';
      }

      const response = await originalFetch(resource, config);

      // Handle 401 unauthorized on protected application endpoints
      if (response.status === 401 && url) {
        const isAuthApi = url.includes('/api/auth/login') || url.includes('/api/auth/register');
        if (!isAuthApi) {
          window.dispatchEvent(new CustomEvent('codeacharya:unauthorized'));
        }
      }

      return response;
    };

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  // Listen for unauthorized session expiration
  useEffect(() => {
    const handleUnauthorized = () => {
      localStorage.removeItem('codeacharya_auth_token');
      setUser(null);
      setStudentProfile(null);
      
      const current = activeTab;
      if (PROTECTED_TABS.includes(current)) {
        setRedirectTarget(current);
        setActiveTab('login');
        if (typeof window !== 'undefined') {
          window.history.pushState({ tab: 'login' }, '', `?tab=login&redirect=${current}`);
        }
      }
    };

    window.addEventListener('codeacharya:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('codeacharya:unauthorized', handleUnauthorized);
  }, [activeTab]);

  // Initial Auth Verification & Data Loading
  useEffect(() => {
    checkInitialAuth();
  }, []);

  const checkInitialAuth = async () => {
    setIsCheckingAuth(true);
    const token = localStorage.getItem('codeacharya_auth_token');

    try {
      const res = await fetch('/api/auth/me', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        credentials: 'include'
      });

      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
        await loadAuthenticatedData();

        // If user is authenticated but landed on login/signup, redirect to target
        if (activeTab === 'login' || activeTab === 'signup') {
          const destination = redirectTarget || 'workspace';
          setActiveTab(destination);
          setRedirectTarget(null);
          if (typeof window !== 'undefined') {
            window.history.replaceState({ tab: destination }, '', `?tab=${destination}`);
          }
        }
      } else {
        // Not authenticated
        localStorage.removeItem('codeacharya_auth_token');
        setUser(null);
        setStudentProfile(null);

        // If user attempted to visit a protected route, redirect to login
        if (PROTECTED_TABS.includes(activeTab)) {
          setRedirectTarget(activeTab);
          setActiveTab('login');
          if (typeof window !== 'undefined') {
            window.history.replaceState({ tab: 'login' }, '', `?tab=login&redirect=${activeTab}`);
          }
        }
      }
    } catch (err) {
      console.warn('Initial auth check warning:', err);
      setUser(null);
      if (PROTECTED_TABS.includes(activeTab)) {
        setActiveTab('login');
      }
    } finally {
      setIsCheckingAuth(false);
    }
  };

  const loadAuthenticatedData = async () => {
    // 1. Health check & settings
    try {
      const healthRes = await fetch('/api/health');
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHasGeminiKey(Boolean(healthData.has_gemini_key));
        if (healthData.persona) setPersona(healthData.persona);
      }
    } catch (err) {
      console.warn('Health check notice:', err);
    }

    // 2. Problems list
    try {
      const probRes = await fetch('/api/problems');
      if (probRes.ok) {
        const probData = await probRes.json();
        setProblems(probData);
      }
    } catch (err) {
      console.error('Failed to load problems:', err);
    }

    // 3. User-specific student profile
    try {
      const profRes = await fetch('/api/profile');
      if (profRes.ok) {
        const profData = await profRes.json();
        setStudentProfile(profData);
      }
    } catch (err) {
      console.error('Failed to load student profile:', err);
    }
  };

  // Browser Back/Forward navigation listener
  useEffect(() => {
    const handlePopState = (e) => {
      const targetTab = e.state?.tab;
      const params = new URLSearchParams(window.location.search);
      const tabParam = targetTab || params.get('tab') || 'workspace';

      // Route guard: Prevent unauthenticated users from seeing protected pages via browser Back
      if (!user && PROTECTED_TABS.includes(tabParam)) {
        setActiveTab('login');
        if (typeof window !== 'undefined') {
          window.history.replaceState({ tab: 'login' }, '', `?tab=login`);
        }
        return;
      }

      // Route guard: Prevent authenticated users from going back to login/signup
      if (user && (tabParam === 'login' || tabParam === 'signup')) {
        setActiveTab('workspace');
        if (typeof window !== 'undefined') {
          window.history.replaceState({ tab: 'workspace' }, '', `?tab=workspace`);
        }
        return;
      }

      if (VALID_TABS.includes(tabParam)) {
        setActiveTab(tabParam);
      } else {
        setActiveTab(user ? 'workspace' : 'login');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [user]);

  // Navigate between primary application tabs with history & URL synchronization
  const handleNavigate = useCallback((nextTab) => {
    if (nextTab === activeTab) return;

    // Protection check
    if (!user && PROTECTED_TABS.includes(nextTab)) {
      setRedirectTarget(nextTab);
      setActiveTab('login');
      if (typeof window !== 'undefined') {
        window.history.pushState({ tab: 'login' }, '', `?tab=login&redirect=${nextTab}`);
      }
      return;
    }

    if (user && (nextTab === 'login' || nextTab === 'signup')) {
      return;
    }

    setNavHistory(prev => [...prev, activeTab]);
    setActiveTab(nextTab);
    if (typeof window !== 'undefined') {
      window.history.pushState({ tab: nextTab }, '', `?tab=${nextTab}`);
    }
  }, [activeTab, user]);

  // Back button navigation: uses history stack or falls back cleanly
  const handleBack = () => {
    if (navHistory.length > 0) {
      const historyCopy = [...navHistory];
      let prevTab = historyCopy.pop();
      while (historyCopy.length > 0 && prevTab === activeTab) {
        prevTab = historyCopy.pop();
      }
      setNavHistory(historyCopy);

      if (prevTab && prevTab !== activeTab) {
        // Guard check on history back
        if (!user && PROTECTED_TABS.includes(prevTab)) {
          setActiveTab('login');
          return;
        }
        setActiveTab(prevTab);
        if (typeof window !== 'undefined') {
          window.history.pushState({ tab: prevTab }, '', `?tab=${prevTab}`);
        }
        return;
      }
    }

    // Fallback: If on an internal tab, return to Home
    if (activeTab !== 'workspace' && user) {
      setActiveTab('workspace');
      if (typeof window !== 'undefined') {
        window.history.pushState({ tab: 'workspace' }, '', `?tab=workspace`);
      }
    } else if (selectedProblemId !== null) {
      setSelectedProblemId(null);
    }
  };

  // Logo click handler: directly navigates to Home ('workspace') or 'login'
  const handleGoHome = () => {
    if (!user) {
      handleNavigate('login');
      return;
    }
    if (activeTab === 'workspace') {
      if (selectedProblemId !== null) {
        setSelectedProblemId(null);
      }
      return;
    }
    setNavHistory(prev => [...prev, activeTab]);
    setActiveTab('workspace');
    if (typeof window !== 'undefined') {
      window.history.pushState({ tab: 'workspace' }, '', `?tab=workspace`);
    }
  };

  // Authentication Handlers
  const handleLoginSuccess = async (userData, token) => {
    setUser(userData);
    await loadAuthenticatedData();

    const destination = redirectTarget || 'workspace';
    setRedirectTarget(null);
    setActiveTab(destination);
    if (typeof window !== 'undefined') {
      window.history.pushState({ tab: destination }, '', `?tab=${destination}`);
    }
  };

  const handleSignUpSuccess = async (userData, token) => {
    setUser(userData);
    await loadAuthenticatedData();

    setActiveTab('workspace');
    setRedirectTarget(null);
    if (typeof window !== 'undefined') {
      window.history.pushState({ tab: 'workspace' }, '', `?tab=workspace`);
    }
  };

  // Logout Confirmation Flow
  const handleRequestLogout = () => {
    setLogoutError('');
    setIsLogoutModalOpen(true);
  };

  const handleCloseLogoutModal = () => {
    if (!isLoggingOut) {
      setIsLogoutModalOpen(false);
      setLogoutError('');
    }
  };

  const handleConfirmLogout = async () => {
    setIsLoggingOut(true);
    setLogoutError('');

    try {
      const res = await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Logout failed on server.');
      }

      // Clear all local auth state and sensitive memory
      localStorage.removeItem('codeacharya_auth_token');
      setUser(null);
      setStudentProfile(null);
      setIsLogoutModalOpen(false);
      setNavHistory([]);
      setSelectedProblemId(null);

      // Navigate to Login page and overwrite history to avoid back access
      setActiveTab('login');
      if (typeof window !== 'undefined') {
        window.history.pushState({ tab: 'login' }, '', `?tab=login`);
      }
    } catch (err) {
      setLogoutError(err.message || 'Logout request encountered an issue. Click Retry to try again.');
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleSaveSettings = async (settings) => {
    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      const data = await res.json();
      setHasGeminiKey(data.has_gemini_key);
      setPersona(data.persona);
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  const handleSelectProblem = (pid) => {
    if (activeTab !== 'workspace') {
      setNavHistory(prev => [...prev, activeTab]);
    }
    setSelectedProblemId(pid);
    setActiveTab('workspace');
    if (typeof window !== 'undefined') {
      window.history.pushState({ tab: 'workspace', problemId: pid }, '', `?tab=workspace`);
    }
  };

  const handleProblemCreated = (newProb) => {
    setProblems(prev => {
      const exists = prev.some(p => p.id === newProb.id);
      if (exists) return prev.map(p => p.id === newProb.id ? newProb : p);
      return [newProb, ...prev];
    });
    setSelectedProblemId(newProb.id);
  };

  const handleLaunchViva = () => {
    handleNavigate('viva');
  };

  const currentProbObj = problems.find(p => p.id === selectedProblemId) || problems[0];
  const canGoBack = activeTab !== 'workspace' || selectedProblemId !== null || navHistory.length > 0;

  // Initial auth checking splash screen
  if (isCheckingAuth) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'var(--bg-dark)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16
      }}>
        <div style={{
          width: 56,
          height: 56,
          borderRadius: 16,
          background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 30px rgba(99, 102, 241, 0.5)',
          animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
        }}>
          <BrainCircuit size={32} color="#fff" />
        </div>
        <div style={{
          fontSize: '0.9rem',
          color: 'var(--text-muted)',
          fontWeight: 500,
          fontFamily: 'var(--font-heading)',
          letterSpacing: '0.05em'
        }}>
          INITIALIZING CODEACHARYA...
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Header 
        activeTab={activeTab}
        setActiveTab={handleNavigate}
        studentProfile={studentProfile}
        persona={persona}
        setPersona={setPersona}
        onOpenSettings={() => setIsSettingsOpen(true)}
        hasGeminiKey={hasGeminiKey}
        language={language}
        setLanguage={handleHeaderSetLanguage}
        onBack={handleBack}
        canGoBack={canGoBack}
        onGoHome={handleGoHome}
        user={user}
        onRequestLogout={handleRequestLogout}
      />

      <main style={{ flex: 1, paddingBottom: 40 }}>
        {/* Unauthenticated Routes */}
        {activeTab === 'login' && (
          <LoginPage 
            onLoginSuccess={handleLoginSuccess}
            onNavigate={handleNavigate}
            redirectTarget={redirectTarget}
          />
        )}

        {activeTab === 'signup' && (
          <SignUpPage 
            onSignUpSuccess={handleSignUpSuccess}
            onNavigate={handleNavigate}
          />
        )}

        {/* Protected Routes (rendered only when user is authenticated) */}
        {user && activeTab === 'workspace' && (
          <Workspace 
            problems={problems}
            selectedProblemId={selectedProblemId}
            onSelectProblem={handleSelectProblem}
            onLaunchViva={handleLaunchViva}
            onResetSelection={() => setSelectedProblemId(null)}
            onProblemCreated={handleProblemCreated}
            language={language}
            setLanguage={applyLanguage}
            onRegisterLanguageHandler={(handler) => { workspaceLangHandlerRef.current = handler; }}
            code={code}
            setCode={setCode}
            studentProfile={studentProfile}
            onBack={handleBack}
            onRefreshProfile={loadAuthenticatedData}
            isAssessmentMode={isAssessmentMode}
            setIsAssessmentMode={handleSetAssessmentMode}
          />
        )}

        {user && activeTab === 'viva' && (
          <VivaRoom 
            currentProblem={currentProbObj}
            currentCode={code}
            language={language}
            onBack={handleBack}
            isAssessmentMode={isAssessmentMode}
          />
        )}

        {user && activeTab === 'performance' && (
          <PerformanceDashboard 
            user={user}
            onSelectProblem={handleSelectProblem}
            onBack={handleBack}
          />
        )}

        {user && activeTab === 'analytics' && (
          <SkillDashboard 
            studentProfile={studentProfile}
            onSelectTopic={(topic) => {
              const matched = problems.find(p => p.topic === topic);
              if (matched) handleSelectProblem(matched.id);
            }}
            onBack={handleBack}
          />
        )}

        {user && activeTab === 'recommendations' && (
          <RecommendationsView 
            onSelectProblem={handleSelectProblem}
            onBack={handleBack}
          />
        )}
      </main>

      {/* Global Modals */}
      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSaveSettings={handleSaveSettings}
        currentPersona={persona}
        hasKey={hasGeminiKey}
        isAssessmentMode={isAssessmentMode}
        onToggleAssessmentMode={handleSetAssessmentMode}
      />

      <LogoutConfirmModal 
        isOpen={isLogoutModalOpen}
        onClose={handleCloseLogoutModal}
        onConfirmLogout={handleConfirmLogout}
        isLoggingOut={isLoggingOut}
        logoutError={logoutError}
        onRetry={handleConfirmLogout}
      />
    </div>
  );
}
