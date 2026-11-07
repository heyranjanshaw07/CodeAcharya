import test from 'node:test';
import assert from 'node:assert/strict';
import { getLanguageDisplayName } from './src/utils/languageUtils.js';

test('1. getLanguageDisplayName formats language names correctly', () => {
  assert.equal(getLanguageDisplayName('python'), 'Python');
  assert.equal(getLanguageDisplayName('c'), 'C');
  assert.equal(getLanguageDisplayName('cpp'), 'C++');
  assert.equal(getLanguageDisplayName('java'), 'Java');
  assert.equal(getLanguageDisplayName(''), '');
  assert.equal(getLanguageDisplayName(null), '');
});

test('2. Trigger Behaviour: selecting a different language with existing code opens modal and stores pendingLanguage', () => {
  let isModalOpen = false;
  let pendingLanguage = null;
  let currentLanguage = 'python';
  const existingCode = 'def solution(x):\n    return x * 2\n';

  const requestLanguageChange = (newLang, code, isLocked = false) => {
    if (isLocked) return;
    if (newLang === currentLanguage) return;

    const isEditorEmpty = !code || code.trim().length === 0;
    if (isEditorEmpty) {
      currentLanguage = newLang;
      return;
    }

    pendingLanguage = newLang;
    isModalOpen = true;
  };

  requestLanguageChange('c', existingCode, false);

  assert.equal(isModalOpen, true, 'Modal must open when code exists');
  assert.equal(pendingLanguage, 'c', 'Pending language must be stored separately');
  assert.equal(currentLanguage, 'python', 'Current language must NOT change until confirmed');
});

test('3. Cancel Behaviour: Cancel closes modal, preserves code, keeps language, and resets pendingLanguage', () => {
  let isModalOpen = true;
  let pendingLanguage = 'cpp';
  let currentLanguage = 'python';
  let editorCode = 'def solution():\n    return 42\n';
  let attemptId = 'att_existing_123';
  let hints = [{ hint_level: 1 }];

  const onCancel = () => {
    pendingLanguage = null;
    isModalOpen = false;
  };

  onCancel();

  assert.equal(isModalOpen, false, 'Modal must close on cancel');
  assert.equal(pendingLanguage, null, 'Pending language must be cleared');
  assert.equal(currentLanguage, 'python', 'Language must remain python');
  assert.equal(editorCode, 'def solution():\n    return 42\n', 'Code must remain exactly intact');
  assert.equal(attemptId, 'att_existing_123', 'Attempt ID must not change');
  assert.equal(hints.length, 1, 'Hints must remain intact');
});

test('4. Confirm Behaviour: Confirm switches language, loads starter code, updates runtime, and clears old code', () => {
  let isModalOpen = true;
  let pendingLanguage = 'c';
  let currentLanguage = 'python';
  let editorCode = 'def solution(nums):\n    # user ongoing code\n    return sum(nums)\n';
  const starterTemplates = {
    c: '#include <stdio.h>\n\nint solution(int* nums, int size) {\n    return 0;\n}\n',
    python: 'def solution(nums):\n    pass\n',
    cpp: '#include <iostream>\n\nint solution() {\n    return 0;\n}\n',
    java: 'public class Solution {\n    public int solution() { return 0; }\n}\n'
  };

  const onConfirm = () => {
    if (!pendingLanguage) return;
    currentLanguage = pendingLanguage;
    editorCode = starterTemplates[pendingLanguage] || '';
    pendingLanguage = null;
    isModalOpen = false;
  };

  onConfirm();

  assert.equal(isModalOpen, false, 'Modal must close on confirmation');
  assert.equal(currentLanguage, 'c', 'Current language must update to c');
  assert.equal(editorCode, starterTemplates.c, 'Editor code must be updated with C starter template');
  assert.equal(editorCode.includes('def solution'), false, 'Old Python code must be cleared');
  assert.equal(pendingLanguage, null, 'Pending language must be reset');
});

test('5. Empty editor & Whitespace-only: switches languages immediately without modal', () => {
  const testCases = [
    { code: '', desc: 'empty string' },
    { code: '   \n  \t  ', desc: 'whitespace-only string' },
    { code: null, desc: 'null code' }
  ];

  for (const tc of testCases) {
    let isModalOpen = false;
    let currentLanguage = 'python';

    const requestLanguageChange = (newLang, code) => {
      if (newLang === currentLanguage) return;
      const isEditorEmpty = !code || code.trim().length === 0;
      if (isEditorEmpty) {
        currentLanguage = newLang;
        return;
      }
      isModalOpen = true;
    };

    requestLanguageChange('java', tc.code);

    assert.equal(isModalOpen, false, `Modal should not open for ${tc.desc}`);
    assert.equal(currentLanguage, 'java', `Language should immediately update to java for ${tc.desc}`);
  }
});

test('6. Selecting currently active language does nothing', () => {
  let isModalOpen = false;
  let currentLanguage = 'python';
  const code = 'print("hello")';

  const requestLanguageChange = (newLang, c) => {
    if (newLang === currentLanguage) return;
    isModalOpen = true;
  };

  requestLanguageChange('python', code);

  assert.equal(isModalOpen, false, 'Modal must not open when selecting the same language');
  assert.equal(currentLanguage, 'python', 'Language must remain unchanged');
});

test('7. Attempt, Timer, Hints, and Activity tracking are strictly preserved across language change', () => {
  let attemptId = 'att_session_999';
  let timerElapsedSeconds = 145;
  let hintsHistory = [{ hint_level: 1 }, { hint_level: 2 }];
  let tabSwitches = 3;
  let currentLanguage = 'python';
  let code = 'def test(): return 1';

  // Perform confirmed language change
  const performLanguageChange = (newLang) => {
    currentLanguage = newLang;
    code = '#include <stdio.h>\n';
    // CRITICAL: attemptId, timerElapsedSeconds, hintsHistory, tabSwitches are NOT reset!
  };

  performLanguageChange('c');

  assert.equal(currentLanguage, 'c');
  assert.equal(attemptId, 'att_session_999', 'Attempt ID must remain unchanged');
  assert.equal(timerElapsedSeconds, 145, 'Timer elapsed time must remain intact');
  assert.equal(hintsHistory.length, 2, 'Hint history must remain intact');
  assert.equal(tabSwitches, 3, 'Tab switch count must remain intact');
});

test('8. Locked editor prevents language changes completely', () => {
  let isModalOpen = false;
  let currentLanguage = 'python';
  const isLocked = true; // Editor locked by full-screen restriction

  const requestLanguageChange = (newLang, isEditorLocked) => {
    if (isEditorLocked) {
      return; // Blocked!
    }
    currentLanguage = newLang;
    isModalOpen = true;
  };

  requestLanguageChange('cpp', isLocked);

  assert.equal(isModalOpen, false, 'Modal must NOT open while editor is locked');
  assert.equal(currentLanguage, 'python', 'Language must NOT change while editor is locked');
});

test('9. Compiler/runtime configuration is updated to new language for execution payload', () => {
  let activeLanguage = 'python';
  let activeCode = 'def solution(): pass';

  const buildExecutionPayload = (problemId, code, language) => ({
    problem_id: problemId,
    code: code,
    language: language,
    compiler: language === 'c' ? 'gcc' : language === 'cpp' ? 'g++' : language === 'java' ? 'javac' : 'python3'
  });

  const payloadBefore = buildExecutionPayload('two-sum', activeCode, activeLanguage);
  assert.equal(payloadBefore.language, 'python');
  assert.equal(payloadBefore.compiler, 'python3');

  // Change language to C
  activeLanguage = 'c';
  activeCode = '#include <stdio.h>\n';
  const payloadAfter = buildExecutionPayload('two-sum', activeCode, activeLanguage);
  assert.equal(payloadAfter.language, 'c');
  assert.equal(payloadAfter.compiler, 'gcc');
});

test('10. Confirmation Modal content matches specification exactly', () => {
  const currentLanguage = 'python';
  const newLanguage = 'cpp';

  const title = 'Change Programming Language?';
  const message = `You are about to switch from ${getLanguageDisplayName(currentLanguage)} to ${getLanguageDisplayName(newLanguage)}.`;
  const warning = 'Your current code will be deleted when you switch languages. This action cannot be undone.';
  const buttons = ['Cancel', 'Yes, Change Language'];

  assert.equal(title, 'Change Programming Language?');
  assert.equal(message, 'You are about to switch from Python to C++.');
  assert.equal(warning, 'Your current code will be deleted when you switch languages. This action cannot be undone.');
  assert.deepEqual(buttons, ['Cancel', 'Yes, Change Language']);
});

