/**
 * CodeAcharya Global Full-Screen Enforcement & Proctoring Utility
 * 
 * Provides robust cross-browser Fullscreen API and Page Visibility API integration:
 * - Checks fullscreen status across standard and vendor prefixes
 * - Manages user-gesture full-screen requests and graceful error handling
 * - Dispatches telemetry events to backend with client-side deduplication
 * - Guarantees that student code is never deleted or overwritten
 */

let lastEventTime = 0;
let lastEventType = '';

/**
 * Checks whether the browser document is currently in full-screen mode.
 * Supports standard and vendor-prefixed properties.
 */
export function isBrowserFullscreen() {
  if (typeof document === 'undefined') return false;
  return Boolean(
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  );
}

/**
 * Checks whether the browser supports Fullscreen API.
 */
export function isFullscreenSupported() {
  if (typeof document === 'undefined') return false;
  return Boolean(
    document.fullscreenEnabled ||
    document.webkitFullscreenEnabled ||
    document.mozFullScreenEnabled ||
    document.msFullscreenEnabled ||
    document.documentElement?.requestFullscreen ||
    document.documentElement?.webkitRequestFullscreen ||
    document.documentElement?.mozRequestFullScreen ||
    document.documentElement?.msRequestFullscreen
  );
}

/**
 * Requests browser full-screen on the specified element (defaults to document.documentElement).
 * Must be initiated by a user interaction gesture (click/keydown).
 * Returns { success: boolean, error?: string }
 */
export async function requestBrowserFullscreen(element = null) {
  if (typeof document === 'undefined') {
    return { success: false, error: 'Document is not available.' };
  }

  const target = element || document.documentElement;

  try {
    if (target.requestFullscreen) {
      await target.requestFullscreen();
    } else if (target.webkitRequestFullscreen) {
      await target.webkitRequestFullscreen();
    } else if (target.mozRequestFullScreen) {
      await target.mozRequestFullScreen();
    } else if (target.msRequestFullscreen) {
      await target.msRequestFullscreen();
    } else {
      return { success: false, error: 'Full-screen mode is not supported by your browser.' };
    }

    // Small delay to let browser update fullscreenElement property
    await new Promise(r => setTimeout(r, 60));

    const verified = isBrowserFullscreen();
    return {
      success: verified,
      error: verified ? null : 'Full-screen request was not confirmed by the browser.'
    };
  } catch (err) {
    const errorMsg = err?.message || 'Full-screen request was blocked or denied by the browser.';
    return { success: false, error: errorMsg };
  }
}

/**
 * Exits browser full-screen if active.
 */
export async function exitBrowserFullscreen() {
  if (typeof document === 'undefined' || !isBrowserFullscreen()) return;
  try {
    if (document.exitFullscreen) {
      await document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      await document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
      await document.mozCancelFullScreen();
    } else if (document.msExitFullscreen) {
      await document.msExitFullscreen();
    }
  } catch (err) {
    console.debug('[Fullscreen] Exit notice:', err);
  }
}

/**
 * Dispatches structured session lock / proctoring telemetry to the backend.
 * Enforces client deduplication within 1000ms.
 */
export async function logSessionLockTelemetry({
  eventType,
  attemptId = null,
  questionId = null,
  metadata = {}
}) {
  const now = Date.now();
  if (eventType === lastEventType && now - lastEventTime < 1000) {
    return { duplicate: true };
  }
  lastEventType = eventType;
  lastEventTime = now;

  try {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('codeacharya_auth_token') : null;
    const res = await fetch('/api/session/lock-event', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      credentials: 'include',
      body: JSON.stringify({
        event_type: eventType,
        attempt_id: attemptId,
        question_id: questionId,
        event_timestamp: new Date().toISOString(),
        metadata
      })
    });
    return await res.json().catch(() => ({}));
  } catch (err) {
    console.debug('[Fullscreen] Telemetry error:', err);
    return { error: err.message };
  }
}

/**
 * Notifies the backend that the session is locked.
 */
export async function notifySessionLockedOnServer({
  attemptId = null,
  questionId = null,
  reason = 'fullscreen_exit',
  metadata = {}
}) {
  try {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('codeacharya_auth_token') : null;
    const res = await fetch('/api/session/lock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      credentials: 'include',
      body: JSON.stringify({
        attempt_id: attemptId,
        question_id: questionId,
        reason,
        event_timestamp: new Date().toISOString(),
        metadata
      })
    });
    return await res.json().catch(() => ({}));
  } catch (err) {
    console.debug('[Fullscreen] Lock notification error:', err);
    return { error: err.message };
  }
}

/**
 * Requests server-side session resume after verified browser full-screen.
 */
export async function notifySessionResumeOnServer({
  attemptId = null,
  questionId = null,
  fullscreenVerified = true,
  metadata = {}
}) {
  try {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('codeacharya_auth_token') : null;
    const res = await fetch('/api/session/resume', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      credentials: 'include',
      body: JSON.stringify({
        attempt_id: attemptId,
        question_id: questionId,
        fullscreen_verified: Boolean(fullscreenVerified),
        event_timestamp: new Date().toISOString(),
        metadata
      })
    });
    return await res.json().catch(() => ({}));
  } catch (err) {
    console.debug('[Fullscreen] Resume notification error:', err);
    return { error: err.message };
  }
}

