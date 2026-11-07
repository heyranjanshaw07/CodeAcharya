/**
 * Comprehensive Test Suite for CodeAcharya Monaco IntelliSense & Auto-Completion Engine
 *
 * Verifies:
 * 1. Built-in suggestions & snippets across all 4 languages (Python, C, C++, Java)
 * 2. Real-time extraction of user-declared functions with parameter placeholders
 * 3. Extraction of declared variables, constants, and function parameters
 * 4. Function signatures & parameter help parsing and lookup
 * 5. Member-access suggestions triggered on '.'
 * 6. Idempotent registration and disposal (zero duplicates on re-render)
 * 7. Strict lock-state enforcement (cannot bypass fullscreen/read-only restriction)
 */

import test from 'node:test';
import assert from 'node:assert/strict';

import {
  BUILTIN_COMPLETIONS,
  MEMBER_COMPLETIONS,
  BUILTIN_SIGNATURES,
  extractUserSymbols,
  parseCallBeforeCursor,
  getFunctionSignature,
  registerCodeAcharyaIntelliSense,
  disposeCodeAcharyaIntelliSense
} from './src/utils/monacoIntelliSense.js';

// =============================================================================
// TEST 1: Built-in suggestions and snippets across Python, C, C++, Java
// =============================================================================
test('1. Built-in IntelliSense catalog covers all 4 languages with snippets & docs', () => {
  // Python Built-ins
  const pyLabels = BUILTIN_COMPLETIONS.python.map(c => c.label);
  assert.ok(pyLabels.includes('print'), 'Python should have print()');
  assert.ok(pyLabels.includes('len'), 'Python should have len()');
  assert.ok(pyLabels.includes('range'), 'Python should have range()');
  assert.ok(pyLabels.includes('enumerate'), 'Python should have enumerate()');
  assert.ok(pyLabels.includes('def'), 'Python should have def snippet');
  assert.ok(pyLabels.includes('class'), 'Python should have class snippet');
  assert.ok(pyLabels.includes('if'), 'Python should have if snippet');

  const pyPrint = BUILTIN_COMPLETIONS.python.find(c => c.label === 'print');
  assert.equal(pyPrint.isSnippet, true);
  assert.ok(pyPrint.insertText.includes('${1:object}'));

  // C Built-ins
  const cLabels = BUILTIN_COMPLETIONS.c.map(c => c.label);
  assert.ok(cLabels.includes('printf'), 'C should have printf()');
  assert.ok(cLabels.includes('scanf'), 'C should have scanf()');
  assert.ok(cLabels.includes('malloc'), 'C should have malloc()');
  assert.ok(cLabels.includes('inc'), 'C should have #include snippet');
  assert.ok(cLabels.includes('main'), 'C should have main() snippet');
  assert.ok(cLabels.includes('for'), 'C should have for loop snippet');

  // C++ Built-ins
  const cppLabels = BUILTIN_COMPLETIONS.cpp.map(c => c.label);
  assert.ok(cppLabels.includes('cout'), 'C++ should have cout');
  assert.ok(cppLabels.includes('cin'), 'C++ should have cin');
  assert.ok(cppLabels.includes('vector'), 'C++ should have vector');
  assert.ok(cppLabels.includes('std::sort'), 'C++ should have std::sort');
  assert.ok(cppLabels.includes('vec'), 'C++ should have vec snippet');
  assert.ok(cppLabels.includes('cou'), 'C++ should have cou snippet');

  // Java Built-ins
  const javaLabels = BUILTIN_COMPLETIONS.java.map(c => c.label);
  assert.ok(javaLabels.includes('System.out.println'), 'Java should have System.out.println');
  assert.ok(javaLabels.includes('sout'), 'Java should have sout snippet');
  assert.ok(javaLabels.includes('main'), 'Java should have main method snippet');
  assert.ok(javaLabels.includes('pub'), 'Java should have pub snippet');
  assert.ok(javaLabels.includes('new'), 'Java should have new object snippet');
  assert.ok(javaLabels.includes('Math.max'), 'Java should have Math.max');
  assert.ok(javaLabels.includes('Arrays.sort'), 'Java should have Arrays.sort');
});

// =============================================================================
// TEST 2: Python User-Defined Functions, Variables, and Parameters
// =============================================================================
test('2. Python user-defined functions, variables, and parameters extraction', () => {
  const pythonCode = `
student_name = "Ranjan"
student_age = 21
MAX_SCORE = 100

def calculate_sum(a, b):
    result = a + b
    return result

for item in items:
    print(item)
`;

  const symbols = extractUserSymbols(pythonCode, 'python', 7);

  // Functions
  const fnNames = symbols.functions.map(f => f.name);
  assert.ok(fnNames.includes('calculate_sum'), 'Should detect calculate_sum function');
  const calcSum = symbols.functions.find(f => f.name === 'calculate_sum');
  assert.deepEqual(calcSum.params, ['a', 'b']);
  assert.equal(calcSum.insertSnippet, 'calculate_sum(${1:a}, ${2:b})$0');

  // Variables
  const varNames = symbols.variables.map(v => v.name);
  assert.ok(varNames.includes('student_name'), 'Should detect student_name variable');
  assert.ok(varNames.includes('student_age'), 'Should detect student_age variable');
  assert.ok(varNames.includes('MAX_SCORE'), 'Should detect MAX_SCORE constant');
  const maxScore = symbols.variables.find(v => v.name === 'MAX_SCORE');
  assert.equal(maxScore.isConstant, true);

  // Parameters
  const paramNames = symbols.parameters.map(p => p.name);
  assert.ok(paramNames.includes('a'), 'Should detect parameter a');
  assert.ok(paramNames.includes('b'), 'Should detect parameter b');

  // In-scope parameter priority (cursor at line 7 is inside calculate_sum)
  const paramA = symbols.parameters.find(p => p.name === 'a');
  assert.equal(paramA.isCurrentScope, true, 'Parameter a should be in current scope at line 7');
});

// =============================================================================
// TEST 3: C and C++ User-Defined Functions, Structs, and Variables
// =============================================================================
test('3. C / C++ user-defined functions, structs, and variables extraction', () => {
  const cCode = `
#include <stdio.h>

struct Student {
    int id;
    int score;
};

int calculate_area(int length, int width) {
    int total = length * width;
    return total;
}

int main() {
    int student_age = 21;
    return 0;
}
`;

  const cSymbols = extractUserSymbols(cCode, 'c', 10);

  // Functions
  const fnNames = cSymbols.functions.map(f => f.name);
  assert.ok(fnNames.includes('calculate_area'), 'Should detect calculate_area function');
  assert.ok(fnNames.includes('main'), 'Should detect main function');

  const calcArea = cSymbols.functions.find(f => f.name === 'calculate_area');
  assert.deepEqual(calcArea.params, ['length', 'width']);
  assert.equal(calcArea.insertSnippet, 'calculate_area(${1:length}, ${2:width})$0');

  // Classes / Structs
  const classNames = cSymbols.classes.map(c => c.name);
  assert.ok(classNames.includes('Student'), 'Should detect Student struct');

  // Parameters
  const paramNames = cSymbols.parameters.map(p => p.name);
  assert.ok(paramNames.includes('length'));
  assert.ok(paramNames.includes('width'));

  // Variables
  const varNames = cSymbols.variables.map(v => v.name);
  assert.ok(varNames.includes('total'));
});

// =============================================================================
// TEST 4: Java User-Defined Methods, Classes, and Variables
// =============================================================================
test('4. Java user-defined methods, classes, and variables extraction', () => {
  const javaCode = `
public class Solution {
    private int globalCount = 0;

    public int calculateSum(int a, int b) {
        int total = a + b;
        return total;
    }

    public static void main(String[] args) {
        String studentName = "Ranjan";
    }
}
`;

  const javaSymbols = extractUserSymbols(javaCode, 'java', 6);

  // Methods
  const fnNames = javaSymbols.functions.map(f => f.name);
  assert.ok(fnNames.includes('calculateSum'), 'Should detect calculateSum method');
  assert.ok(fnNames.includes('main'), 'Should detect main method');

  const calcSum = javaSymbols.functions.find(f => f.name === 'calculateSum');
  assert.deepEqual(calcSum.params, ['a', 'b']);
  assert.equal(calcSum.insertSnippet, 'calculateSum(${1:a}, ${2:b})$0');

  // Classes
  const classNames = javaSymbols.classes.map(c => c.name);
  assert.ok(classNames.includes('Solution'), 'Should detect Solution class');

  // Variables
  const varNames = javaSymbols.variables.map(v => v.name);
  assert.ok(varNames.includes('total'), 'Should detect total variable');
});

// =============================================================================
// TEST 5: Signature Help Parser and Active Parameter Resolution
// =============================================================================
test('5. Signature help parses function call and determines active parameter correctly', () => {
  // Python user function call at first parameter
  const call1 = parseCallBeforeCursor('val = calculate_area(');
  assert.deepEqual(call1, { funcName: 'calculate_area', paramIndex: 0 });

  // Python user function call at second parameter
  const call2 = parseCallBeforeCursor('val = calculate_area(length, ');
  assert.deepEqual(call2, { funcName: 'calculate_area', paramIndex: 1 });

  // Nested expression before comma
  const call3 = parseCallBeforeCursor('val = calculate_sum((a + b) * 2, ');
  assert.deepEqual(call3, { funcName: 'calculate_sum', paramIndex: 1 });

  // Built-in Python print
  const callPrint = parseCallBeforeCursor('print("score: ", ');
  assert.deepEqual(callPrint, { funcName: 'print', paramIndex: 1 });

  // Java Math.max
  const callMath = parseCallBeforeCursor('int m = Math.max(x, ');
  assert.deepEqual(callMath, { funcName: 'Math.max', paramIndex: 1 });

  // Signature lookup for user function
  const mockSymbols = {
    functions: [
      {
        name: 'calculate_area',
        params: ['length', 'width'],
        line: 5
      }
    ]
  };
  const sigUser = getFunctionSignature('calculate_area', 'python', mockSymbols);
  assert.ok(sigUser, 'Signature should be found for user function');
  assert.equal(sigUser.label, 'calculate_area(length, width)');
  assert.equal(sigUser.parameters.length, 2);
  assert.equal(sigUser.parameters[0].label, 'length');
  assert.equal(sigUser.parameters[1].label, 'width');

  // Signature lookup for built-in
  const sigBuiltin = getFunctionSignature('print', 'python');
  assert.ok(sigBuiltin, 'Signature should be found for built-in print');
  assert.ok(sigBuiltin.label.startsWith('print('));
});

// =============================================================================
// TEST 6: Member Access Completions on '.'
// =============================================================================
test('6. Member-access completions provide relevant methods for each language', () => {
  const pyMembers = MEMBER_COMPLETIONS.python.map(m => m.label);
  assert.ok(pyMembers.includes('append'));
  assert.ok(pyMembers.includes('pop'));
  assert.ok(pyMembers.includes('split'));
  assert.ok(pyMembers.includes('keys'));

  const cppMembers = MEMBER_COMPLETIONS.cpp.map(m => m.label);
  assert.ok(cppMembers.includes('push_back'));
  assert.ok(cppMembers.includes('size'));
  assert.ok(cppMembers.includes('empty'));

  const javaMembers = MEMBER_COMPLETIONS.java.map(m => m.label);
  assert.ok(javaMembers.includes('length'));
  assert.ok(javaMembers.includes('charAt'));
  assert.ok(javaMembers.includes('substring'));
  assert.ok(javaMembers.includes('add'));
});

// =============================================================================
// TEST 7: Idempotent Registration & Clean Disposal Lifecycle
// =============================================================================
test('7. registerCodeAcharyaIntelliSense is idempotent and disposes cleanly without memory leaks', () => {
  let completionRegisteredCount = 0;
  let signatureRegisteredCount = 0;
  let disposedCount = 0;

  const mockMonaco = {
    languages: {
      CompletionItemKind: {
        Function: 1,
        Method: 0,
        Variable: 4,
        Constant: 19,
        Class: 5,
        Snippet: 13,
        Keyword: 12,
        Field: 3,
        Module: 7,
        Text: 18
      },
      CompletionItemInsertTextRule: {
        InsertAsSnippet: 4
      },
      registerCompletionItemProvider: (lang, provider) => {
        completionRegisteredCount++;
        return {
          dispose: () => {
            disposedCount++;
          }
        };
      },
      registerSignatureHelpProvider: (lang, provider) => {
        signatureRegisteredCount++;
        return {
          dispose: () => {
            disposedCount++;
          }
        };
      }
    }
  };

  // First registration: 4 languages * 2 providers = 8 registrations
  const cleanup1 = registerCodeAcharyaIntelliSense(mockMonaco);
  assert.equal(completionRegisteredCount, 4);
  assert.equal(signatureRegisteredCount, 4);
  assert.equal(disposedCount, 0);

  // Second registration (simulating React re-render or re-mount):
  // Must automatically dispose all 8 previous providers first, keeping total active providers at 8!
  const cleanup2 = registerCodeAcharyaIntelliSense(mockMonaco);
  assert.equal(disposedCount, 8, 'Should have disposed all 8 prior providers');
  assert.equal(completionRegisteredCount, 8);
  assert.equal(signatureRegisteredCount, 8);

  // Cleanup:
  cleanup2();
  assert.equal(disposedCount, 16, 'Should have disposed the remaining 8 providers');
});

// =============================================================================
// TEST 8: Full-Screen / Read-Only Lock State Enforcement
// =============================================================================
test('8. Locked state strictly disables completion suggestions and signature help', () => {
  let registeredCompletionProvider = null;
  let registeredSignatureProvider = null;

  const mockMonaco = {
    languages: {
      CompletionItemKind: { Function: 1 },
      CompletionItemInsertTextRule: { InsertAsSnippet: 4 },
      registerCompletionItemProvider: (lang, provider) => {
        if (lang === 'python') registeredCompletionProvider = provider;
        return { dispose: () => {} };
      },
      registerSignatureHelpProvider: (lang, provider) => {
        if (lang === 'python') registeredSignatureProvider = provider;
        return { dispose: () => {} };
      }
    }
  };

  registerCodeAcharyaIntelliSense(mockMonaco);

  const mockModel = {
    getValue: () => 'def test(): pass\n',
    getWordUntilPosition: () => ({ startColumn: 1, endColumn: 2 }),
    getLineContent: () => 'te'
  };
  const mockPosition = { lineNumber: 1, column: 3 };

  // When UNLOCKED:
  globalThis.window = { __codeAcharyaIsLocked: false };
  const unlockedCompletions = registeredCompletionProvider.provideCompletionItems(mockModel, mockPosition);
  assert.ok(unlockedCompletions.suggestions.length > 0, 'Completions should be available when unlocked');

  // When LOCKED:
  globalThis.window = { __codeAcharyaIsLocked: true };
  const lockedCompletions = registeredCompletionProvider.provideCompletionItems(mockModel, mockPosition);
  assert.deepEqual(lockedCompletions.suggestions, [], 'Completions must be empty when editor is locked');

  const lockedSignature = registeredSignatureProvider.provideSignatureHelp(mockModel, mockPosition);
  assert.equal(lockedSignature, null, 'Signature help must be null when editor is locked');

  // Clean up global mock
  delete globalThis.window;
  disposeCodeAcharyaIntelliSense();
});

