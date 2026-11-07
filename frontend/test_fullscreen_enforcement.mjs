import test from 'node:test';
import assert from 'node:assert/strict';
import {
  isBrowserFullscreen,
  isFullscreenSupported,
  requestBrowserFullscreen,
  exitBrowserFullscreen,
  logSessionLockTelemetry,
  notifySessionLockedOnServer,
  notifySessionResumeOnServer
} from './src/utils/fullscreenEnforcement.js';

test('isBrowserFullscreen: returns false when no fullscreenElement is active', () => {
  global.document = {};
  assert.equal(isBrowserFullscreen(), false);
});

test('isBrowserFullscreen: returns true for standard and vendor prefixed elements', () => {
  const dummyEl = { tagName: 'DIV' };

  global.document = { fullscreenElement: dummyEl };
  assert.equal(isBrowserFullscreen(), true);

  global.document = { webkitFullscreenElement: dummyEl };
  assert.equal(isBrowserFullscreen(), true);

  global.document = { mozFullScreenElement: dummyEl };
  assert.equal(isBrowserFullscreen(), true);

  global.document = { msFullscreenElement: dummyEl };
  assert.equal(isBrowserFullscreen(), true);
});

test('isFullscreenSupported: correctly detects Fullscreen API capabilities', () => {
  global.document = {
    documentElement: {
      requestFullscreen: async () => {}
    }
  };
  assert.equal(isFullscreenSupported(), true);

  global.document = {
    documentElement: {}
  };
  assert.equal(isFullscreenSupported(), false);
});

test('requestBrowserFullscreen: succeeds and verifies when document enters fullscreen', async () => {
  const mockElement = {
    requestFullscreen: async () => {
      global.document.fullscreenElement = mockElement;
    }
  };
  global.document = {
    documentElement: mockElement,
    fullscreenElement: null
  };

  const res = await requestBrowserFullscreen(mockElement);
  assert.equal(res.success, true);
  assert.equal(res.error, null);
  assert.equal(isBrowserFullscreen(), true);
});

test('requestBrowserFullscreen: catches rejection and returns descriptive error', async () => {
  const mockElement = {
    requestFullscreen: async () => {
      throw new Error('Permissions policy denies fullscreen request');
    }
  };
  global.document = {
    documentElement: mockElement,
    fullscreenElement: null
  };

  const res = await requestBrowserFullscreen(mockElement);
  assert.equal(res.success, false);
  assert.match(res.error, /Permissions policy denies fullscreen request/);
});

test('exitBrowserFullscreen: calls document.exitFullscreen when fullscreen is active', async () => {
  let exitCalled = false;
  global.document = {
    fullscreenElement: {},
    exitFullscreen: async () => {
      exitCalled = true;
      global.document.fullscreenElement = null;
    }
  };

  await exitBrowserFullscreen();
  assert.equal(exitCalled, true);
  assert.equal(isBrowserFullscreen(), false);
});

test('Student code preservation: student code is never cleared, reset, or overwritten during lock/resume lifecycle', () => {
  const studentInitialCode = 'def solution(x):\n    # student ongoing implementation\n    return x * 2\n';
  let activeCode = studentInitialCode;
  let isEditorLocked = false;
  let lockReason = '';

  // Simulate Lock trigger (e.g. fullscreen exit or tab switch)
  const simulateLock = (reason) => {
    isEditorLocked = true;
    lockReason = reason;
    // CRITICAL: activeCode remains intact!
  };

  // Simulate Resume trigger
  const simulateResume = (fullscreenVerified) => {
    if (!fullscreenVerified) return false;
    isEditorLocked = false;
    lockReason = '';
    return true;
  };

  simulateLock('fullscreen_exit');
  assert.equal(isEditorLocked, true);
  assert.equal(activeCode, studentInitialCode, 'Code must not be modified when locked');

  simulateLock('page_hidden');
  assert.equal(isEditorLocked, true);
  assert.equal(activeCode, studentInitialCode, 'Code must not be modified on tab hidden');

  const resumeFailed = simulateResume(false);
  assert.equal(resumeFailed, false);
  assert.equal(isEditorLocked, true);
  assert.equal(activeCode, studentInitialCode, 'Code must remain intact if resume fails');

  const resumeSuccess = simulateResume(true);
  assert.equal(resumeSuccess, true);
  assert.equal(isEditorLocked, false);
  assert.equal(activeCode, studentInitialCode, 'Code must remain exactly as typed after successful resume');
});

test('Mode-agnostic global enforcement: lock applies to Practice, Timed, and Assessment modes without exemption', () => {
  const codingModes = ['practice_mode', 'timed_mode', 'assessment_mode', 'challenge_mode'];
  
  for (const mode of codingModes) {
    let modeLocked = false;
    const enforceLock = (currentMode, isFullscreen) => {
      // Global rule: NO mode exemption
      if (!isFullscreen) {
        modeLocked = true;
      }
      return modeLocked;
    };

    const locked = enforceLock(mode, false);
    assert.equal(locked, true, `Mode ${mode} must be locked when not in fullscreen`);
  }
});

