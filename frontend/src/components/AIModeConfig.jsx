import React, { useState } from 'react';
import { 
  Sparkles, 
  Brain, 
  Cpu, 
  Layers, 
  Clock, 
  ShieldCheck, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle,
  Code2,
  Zap,
  BookOpen
} from 'lucide-react';

const PROGRAMMING_LANGUAGES = [
  { id: 'python', name: 'Python', icon: '🐍', desc: 'Python 3.10+ with clean syntax' },
  { id: 'c', name: 'C', icon: '🔷', desc: 'Standard C (GCC) optimized execution' },
  { id: 'cpp', name: 'C++', icon: '⚡', desc: 'Modern C++20 with STL algorithms' },
  { id: 'java', name: 'Java', icon: '☕', desc: 'Java 17+ with OOP structure' }
];

const DIFFICULTY_LEVELS = [
  { id: 'Easy', name: 'Easy', badgeColor: '#10b981', desc: 'Fundamental concepts & basic logic' },
  { id: 'Medium', name: 'Medium', badgeColor: '#f59e0b', desc: 'Complex problem-solving & optimizations' },
  { id: 'Hard', name: 'Hard', badgeColor: '#ef4444', desc: 'Advanced algorithmic patterns & edge cases' }
];

const TOPICS = [
  { id: 'Arrays', name: 'Arrays', desc: 'Prefix sums, two-pointers, hash maps' },
  { id: 'Strings', name: 'Strings', desc: 'Palindromes, anagrams, sliding window' },
  { id: 'Linked Lists', name: 'Linked Lists', desc: 'Pointers, cycles, reversal, merge' },
  { id: 'Stacks and Queues', name: 'Stacks and Queues', desc: 'Monotonic stacks, parentheses, BFS' },
  { id: 'Trees and Binary Trees', name: 'Trees and Binary Trees', desc: 'DFS/BFS traversals, BST, path sums' },
  { id: 'Graphs', name: 'Graphs', desc: 'Topological sort, cycle detection, paths' },
  { id: 'Dynamic Programming', name: 'Dynamic Programming', desc: 'Memoization, 1D/2D tabular DP, knapsack' },
  { id: 'Searching and Sorting', name: 'Searching and Sorting', desc: 'Binary search, custom comparators' },
  { id: 'Recursion and Backtracking', name: 'Recursion and Backtracking', desc: 'Divide & conquer, subsets, permutations' },
  { id: 'Object-Oriented Programming', name: 'Object-Oriented Programming', desc: 'Classes, encapsulation, inheritance' },
  { id: 'Mixed DSA Problems', name: 'Mixed DSA Problems', desc: 'Comprehensive multi-pattern challenges' }
];

const QUESTION_COUNTS = [
  { count: 3, label: '3 Questions', timeEstimate: '~30-45 mins', recommended: true },
  { count: 5, label: '5 Questions', timeEstimate: '~60-75 mins' },
  { count: 10, label: '10 Questions', timeEstimate: '~120-150 mins' }
];

export default function AIModeConfig({ onStartAssessment, isLoading, error }) {
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [selectedDifficulty, setSelectedDifficulty] = useState('Easy');
  const [selectedTopic, setSelectedTopic] = useState('Arrays');
  const [selectedCount, setSelectedCount] = useState(3);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLoading) return;
    onStartAssessment({
      language: selectedLanguage,
      difficulty: selectedDifficulty,
      topic: selectedTopic,
      num_questions: selectedCount
    });
  };

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '32px 20px' }}>
      {/* Header Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%)',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        borderRadius: 20,
        padding: '28px 32px',
        marginBottom: 28,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: -20,
          right: -20,
          width: 140,
          height: 140,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, transparent 70%)',
          pointerEvents: 'none'
        }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 8 }}>
          <div style={{
            width: 44,
            height: 44,
            borderRadius: 12,
            background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)'
          }}>
            <Sparkles size={24} color="#fff" />
          </div>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '1.75rem',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              background: 'linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              AI Mode — Dynamic Coding Assessment
            </h1>
            <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Attempt dynamically generated, original coding problems powered by Gemini 3.8 Flash with sandboxed evaluation.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 20, marginTop: 16, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', color: '#a5b4fc' }}>
            <Zap size={14} /> Zero Duplicates Guaranteed
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', color: '#a5b4fc' }}>
            <ShieldCheck size={14} /> Sandboxed Multi-Language Evaluation
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', color: '#a5b4fc' }}>
            <Brain size={14} /> Hidden Test Case Validation
          </div>
        </div>
      </div>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 12,
          padding: '14px 18px',
          marginBottom: 24,
          color: '#fca5a5',
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          fontSize: '0.9rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Main Configuration Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>
        {/* Step 1: Programming Language */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 24
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <div style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: 'rgba(99, 102, 241, 0.2)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              1
            </div>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Select Programming Language
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 14
          }}>
            {PROGRAMMING_LANGUAGES.map((lang) => {
              const isSelected = selectedLanguage === lang.id;
              return (
                <button
                  type="button"
                  key={lang.id}
                  onClick={() => setSelectedLanguage(lang.id)}
                  style={{
                    background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(30, 41, 59, 0.45)',
                    border: isSelected ? '2px solid #6366f1' : '1px solid var(--border-glass)',
                    borderRadius: 12,
                    padding: '16px 18px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
                      <span>{lang.icon}</span>
                      <span>{lang.name}</span>
                    </div>
                    {isSelected && <CheckCircle2 size={18} color="#6366f1" />}
                  </div>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {lang.desc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 2: Difficulty Level */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 24
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <div style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: 'rgba(99, 102, 241, 0.2)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              2
            </div>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Select Difficulty Level
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 14
          }}>
            {DIFFICULTY_LEVELS.map((diff) => {
              const isSelected = selectedDifficulty === diff.id;
              return (
                <button
                  type="button"
                  key={diff.id}
                  onClick={() => setSelectedDifficulty(diff.id)}
                  style={{
                    background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(30, 41, 59, 0.45)',
                    border: isSelected ? `2px solid ${diff.badgeColor}` : '1px solid var(--border-glass)',
                    borderRadius: 12,
                    padding: '16px 18px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{
                      background: diff.badgeColor,
                      color: '#fff',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '3px 10px',
                      borderRadius: 6
                    }}>
                      {diff.name}
                    </span>
                    {isSelected && <CheckCircle2 size={18} color={diff.badgeColor} />}
                  </div>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {diff.desc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 3: Topic Selection */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 24
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <div style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: 'rgba(99, 102, 241, 0.2)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              3
            </div>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Choose Topic
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 12
          }}>
            {TOPICS.map((top) => {
              const isSelected = selectedTopic === top.id;
              return (
                <button
                  type="button"
                  key={top.id}
                  onClick={() => setSelectedTopic(top.id)}
                  style={{
                    background: isSelected ? 'rgba(99, 102, 241, 0.18)' : 'rgba(30, 41, 59, 0.45)',
                    border: isSelected ? '2px solid #818cf8' : '1px solid var(--border-glass)',
                    borderRadius: 10,
                    padding: '14px 16px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, color: isSelected ? '#fff' : '#e2e8f0', fontSize: '0.92rem' }}>
                      {top.name}
                    </span>
                    {isSelected && <CheckCircle2 size={16} color="#818cf8" />}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {top.desc}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 4: Number of Questions */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.65)',
          border: '1px solid var(--border-glass)',
          borderRadius: 16,
          padding: 24
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <div style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: 'rgba(99, 102, 241, 0.2)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              4
            </div>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Number of Questions
            </h2>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 14
          }}>
            {QUESTION_COUNTS.map((opt) => {
              const isSelected = selectedCount === opt.count;
              return (
                <button
                  type="button"
                  key={opt.count}
                  onClick={() => setSelectedCount(opt.count)}
                  style={{
                    background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(30, 41, 59, 0.45)',
                    border: isSelected ? '2px solid #6366f1' : '1px solid var(--border-glass)',
                    borderRadius: 12,
                    padding: '16px 18px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    position: 'relative'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc' }}>
                      {opt.label}
                    </div>
                    {isSelected && <CheckCircle2 size={18} color="#6366f1" />}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <Clock size={12} />
                    <span>{opt.timeEstimate}</span>
                  </div>
                  {opt.recommended && (
                    <div style={{
                      marginTop: 8,
                      display: 'inline-block',
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: '#34d399',
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 4
                    }}>
                      Recommended
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Start Assessment Action */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 12,
          paddingTop: 8
        }}>
          <button
            type="submit"
            disabled={isLoading}
            style={{
              background: isLoading 
                ? 'rgba(99, 102, 241, 0.5)' 
                : 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: 14,
              padding: '16px 48px',
              fontSize: '1.05rem',
              fontWeight: 700,
              fontFamily: 'var(--font-heading)',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              boxShadow: '0 0 25px rgba(99, 102, 241, 0.45)',
              transition: 'all 0.2s'
            }}
          >
            {isLoading ? (
              <>
                <div style={{
                  width: 20,
                  height: 20,
                  border: '3px solid rgba(255, 255, 255, 0.3)',
                  borderTopColor: '#ffffff',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                <span>Generating Original Questions with Gemini 3.8 Flash...</span>
              </>
            ) : (
              <>
                <Sparkles size={20} />
                <span>Start Assessment</span>
                <ArrowRight size={20} />
              </>
            )}
          </button>

          {isLoading && (
            <p style={{ margin: 0, fontSize: '0.82rem', color: '#a5b4fc', textAlign: 'center' }}>
              Gemini is crafting {selectedCount} unique {selectedDifficulty.toLowerCase()} {selectedTopic} problems with verified starter code &amp; test cases...
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
