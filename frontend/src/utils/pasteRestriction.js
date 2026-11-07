/**
 * CodeAcharya Unified Paste Restriction System
 * 
 * Enforces strict "allow copy, prevent paste" policy across Coding Practice and AI Viva:
 * - Allows Ctrl+C, Cmd+C (copying code or text)
 * - Blocks Ctrl+V, Cmd+V, Shift+Insert
 * - Blocks context-menu paste
 * - Blocks drag-and-drop text insertion
 * - Blocks Monaco Editor clipboard paste actions
 * - Preserves normal typing, navigation, indentation, autocomplete, undo/redo
 * - Preserves Web Speech API voice dictation
 * - Never reads, stores, or transmits clipboard contents
 */

let lastLoggedAttemptTime = 0;

/**
 * Checks whether a keyboard event is a paste shortcut
 */
export function isPasteKeyboardShortcut(e) {
  if (!e) return false;
  
  // Ctrl+V or Cmd+V
  const isCtrlOrCmdV = (e.ctrlKey || e.metaKey) && (
    e.key === 'v' || e.key === 'V' || e.code === 'KeyV' || e.keyCode === 86
  );

  // Shift+Insert
  const isShiftInsert = e.shiftKey && (
    e.key === 'Insert' || e.code === 'Insert' || e.keyCode === 45
  );

  return isCtrlOrCmdV || isShiftInsert;
}

/**
 * Dispatches an API event log for blocked paste attempt.
 * Throttled to prevent flooding on rapid key repeats.
 * Never collects clipboard data.
 */
export async function logBlockedPasteAttempt({ pageType = 'coding', questionId = null, attemptId = null }) {
  const now = Date.now();
  if (now - lastLoggedAttemptTime < 1500) {
    return; // Throttled duplicate attempt
  }
  lastLoggedAttemptTime = now;

  try {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('codeacharya_auth_token') : null;
    await fetch('/api/assessment/paste-attempt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        page_type: pageType,
        question_id: questionId,
        attempt_id: attemptId,
        event_timestamp: new Date().toISOString()
      })
    });
  } catch (err) {
    // Non-blocking telemetry
    console.debug('[PasteRestriction] Telemetry notice:', err);
  }
}

/**
 * Triggers a custom browser event for UI feedback toast/banner
 */
export function dispatchPasteBlockedBanner(pageType = 'coding') {
  if (typeof window !== 'undefined') {
    const event = new CustomEvent('codeacharya:paste-blocked', {
      detail: {
        pageType,
        message: 'Pasting is disabled in restricted assessment mode. Please write your answer directly.',
        timestamp: Date.now()
      }
    });
    window.dispatchEvent(event);
  }
}

/**
 * Unified DOM element restriction handler (for textareas, inputs, and custom containers)
 */
export function attachElementPasteRestriction(element, {
  isRestricted = true,
  pageType = 'viva',
  questionId = null,
  attemptId = null,
  onBlocked = null
} = {}) {
  if (!element || !isRestricted) return () => {};

  const handleBlockedAction = (e, reason = 'paste') => {
    e.preventDefault();
    e.stopPropagation();

    logBlockedPasteAttempt({ pageType, questionId, attemptId });
    dispatchPasteBlockedBanner(pageType);
    if (typeof onBlocked === 'function') {
      onBlocked({ reason, pageType });
    }
  };

  // 1. Standard paste event
  const onPaste = (e) => {
    handleBlockedAction(e, 'paste_event');
  };

  // 2. Keyboard shortcut event (Ctrl+V, Cmd+V, Shift+Insert)
  const onKeyDown = (e) => {
    if (isPasteKeyboardShortcut(e)) {
      handleBlockedAction(e, 'keyboard_shortcut');
    }
  };

  // 3. Modern input event interception (insertFromPaste, insertFromDrop)
  const onBeforeInput = (e) => {
    if (e.inputType && (e.inputType.startsWith('insertFromPaste') || e.inputType.startsWith('insertFromDrop'))) {
      handleBlockedAction(e, 'before_input_paste');
    }
  };

  // 4. Drag & Drop text insertion prevention
  const onDrop = (e) => {
    // If dropping text or data transfer contains text/plain, block it
    if (e.dataTransfer && (e.dataTransfer.types.includes('text/plain') || e.dataTransfer.types.includes('Text') || e.dataTransfer.getData('text'))) {
      handleBlockedAction(e, 'drag_and_drop');
    }
  };

  const onDragOver = (e) => {
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'none';
    }
    e.preventDefault();
  };

  // Attach using capture phase so no sub-handlers can bypass
  element.addEventListener('paste', onPaste, true);
  element.addEventListener('keydown', onKeyDown, true);
  element.addEventListener('beforeinput', onBeforeInput, true);
  element.addEventListener('drop', onDrop, true);
  element.addEventListener('dragover', onDragOver, true);

  return () => {
    element.removeEventListener('paste', onPaste, true);
    element.removeEventListener('keydown', onKeyDown, true);
    element.removeEventListener('beforeinput', onBeforeInput, true);
    element.removeEventListener('drop', onDrop, true);
    element.removeEventListener('dragover', onDragOver, true);
  };
}

/**
 * Configures a Monaco Editor instance to enforce paste restriction:
 * - Overrides Monaco KeyCode.KeyV & Shift+Insert commands
 * - Overrides clipboard paste action
 * - Attaches capture DOM listeners to the editor root element
 * - Preserves copy (Ctrl+C / Cmd+C), indentation, typing, autocomplete
 */
export function configureMonacoPasteRestriction(editor, monaco, {
  isRestricted = true,
  pageType = 'coding',
  questionId = null,
  attemptId = null,
  onBlocked = null
} = {}) {
  if (!editor || !monaco) return () => {};

  if (!isRestricted) return () => {};

  const handleBlockedAction = (reason = 'monaco_paste') => {
    logBlockedPasteAttempt({ pageType, questionId, attemptId });
    dispatchPasteBlockedBanner(pageType);
    if (typeof onBlocked === 'function') {
      onBlocked({ reason, pageType });
    }
  };

  // 1. Monaco KeyCommand overrides
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyV, () => {
    handleBlockedAction('monaco_ctrl_v');
  });

  editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Insert, () => {
    handleBlockedAction('monaco_shift_insert');
  });

  // 2. Override Monaco clipboard paste action if registered
  try {
    const pasteAction = editor.getAction('editor.action.clipboardPasteAction');
    if (pasteAction && typeof pasteAction.run === 'function') {
      // Re-route execution to blocked handler
      const origRun = pasteAction.run;
      pasteAction.run = () => {
        handleBlockedAction('monaco_context_menu_paste');
        return Promise.resolve();
      };
    }
  } catch (err) {
    console.debug('[MonacoPasteRestriction] Action override notice:', err);
  }

  // 3. Attach DOM capture listeners to Monaco container
  const domNode = editor.getDomNode();
  let cleanupDom = () => {};
  if (domNode) {
    cleanupDom = attachElementPasteRestriction(domNode, {
      isRestricted,
      pageType,
      questionId,
      attemptId,
      onBlocked
    });
  }

  return () => {
    cleanupDom();
  };
}
