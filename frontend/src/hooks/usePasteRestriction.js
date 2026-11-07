import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  attachElementPasteRestriction, 
  logBlockedPasteAttempt, 
  dispatchPasteBlockedBanner 
} from '../utils/pasteRestriction';

/**
 * React hook to enforce paste restriction on textareas, inputs, or custom containers.
 * 
 * Features:
 * - Allows copying (Ctrl+C, Cmd+C)
 * - Blocks paste (Ctrl+V, Cmd+V, Shift+Insert, contextmenu paste, drag-and-drop)
 * - Preserves normal typing, editing, autocomplete, undo/redo
 * - Does not interfere with voice dictation or programmatic value updates
 * - Displays temporary user notification and logs attempt
 */
export function usePasteRestriction({
  isRestricted = true,
  pageType = 'viva',
  questionId = null,
  attemptId = null,
  warningDuration = 3000
} = {}) {
  const elementRef = useRef(null);
  const [showWarning, setShowWarning] = useState(false);
  const [warningMessage, setWarningMessage] = useState('');
  const timeoutRef = useRef(null);

  const triggerWarning = useCallback((msg) => {
    const defaultMsg = pageType === 'coding'
      ? 'Pasting is disabled in Assessment Mode. Please write code directly into the editor.'
      : 'Pasting is disabled during AI Viva Examination. Please formulate and speak/type your answer.';
    
    setWarningMessage(msg || defaultMsg);
    setShowWarning(true);

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setShowWarning(false);
    }, warningDuration);
  }, [pageType, warningDuration]);

  // Listen for global paste blocked events relevant to this page
  useEffect(() => {
    const handleGlobalBlocked = (e) => {
      if (e.detail?.pageType === pageType) {
        triggerWarning(e.detail?.message);
      }
    };

    window.addEventListener('codeacharya:paste-blocked', handleGlobalBlocked);
    return () => {
      window.removeEventListener('codeacharya:paste-blocked', handleGlobalBlocked);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [pageType, triggerWarning]);

  // Bind element listener via ref lifecycle
  useEffect(() => {
    const el = elementRef.current;
    if (!el || !isRestricted) return;

    const cleanup = attachElementPasteRestriction(el, {
      isRestricted,
      pageType,
      questionId,
      attemptId,
      onBlocked: () => triggerWarning()
    });

    return cleanup;
  }, [isRestricted, pageType, questionId, attemptId, triggerWarning]);

  // Explicit callback for elements that prefer explicit event binding
  const handlePasteCapture = useCallback((e) => {
    if (!isRestricted) return;
    e.preventDefault();
    e.stopPropagation();
    logBlockedPasteAttempt({ pageType, questionId, attemptId });
    dispatchPasteBlockedBanner(pageType);
    triggerWarning();
  }, [isRestricted, pageType, questionId, attemptId, triggerWarning]);

  const handleKeyDownCapture = useCallback((e) => {
    if (!isRestricted) return;
    const isCtrlOrCmdV = (e.ctrlKey || e.metaKey) && (
      e.key === 'v' || e.key === 'V' || e.code === 'KeyV' || e.keyCode === 86
    );
    const isShiftInsert = e.shiftKey && (
      e.key === 'Insert' || e.code === 'Insert' || e.keyCode === 45
    );

    if (isCtrlOrCmdV || isShiftInsert) {
      e.preventDefault();
      e.stopPropagation();
      logBlockedPasteAttempt({ pageType, questionId, attemptId });
      dispatchPasteBlockedBanner(pageType);
      triggerWarning();
    }
  }, [isRestricted, pageType, questionId, attemptId, triggerWarning]);

  const handleDropCapture = useCallback((e) => {
    if (!isRestricted) return;
    if (e.dataTransfer) {
      e.preventDefault();
      e.stopPropagation();
      logBlockedPasteAttempt({ pageType, questionId, attemptId });
      dispatchPasteBlockedBanner(pageType);
      triggerWarning();
    }
  }, [isRestricted, pageType, questionId, attemptId, triggerWarning]);

  return {
    elementRef,
    showWarning,
    warningMessage,
    dismissWarning: () => setShowWarning(false),
    eventProps: {
      onPasteCapture: handlePasteCapture,
      onKeyDownCapture: handleKeyDownCapture,
      onDropCapture: handleDropCapture
    }
  };
}
