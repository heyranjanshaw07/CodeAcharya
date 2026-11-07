import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  ArrowRight, 
  ArrowLeft,
  Sparkles, 
  Target, 
  TrendingUp, 
  AlertCircle,
  Code2,
  CheckCircle2
} from 'lucide-react';

export default function RecommendationsView({ onSelectProblem, onBack }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const res = await fetch('/api/recommendations');
      const data = await res.json();
      setRecommendations(data);
    } catch (err) {
      console.error('Failed to load recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 16px' }}>
      {/* Banner */}
      <div className="glass-panel" style={{ padding: '24px 32px', marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          {onBack && (
            <button 
              type="button"
              onClick={onBack}
              className="nav-back-btn"
              aria-label="Back"
              title="Back to previous page"
            >
              <ArrowLeft size={16} />
              <span>Back</span>
            </button>
          )}

          <div style={{
            width: 52,
            height: 52,
            borderRadius: 14,
            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 25px rgba(16, 185, 129, 0.4)',
            flexShrink: 0
          }}>
            <Compass size={28} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.45rem', fontWeight: 700, margin: 0, fontFamily: 'var(--font-heading)' }}>
              Personalized Learning Pathway
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
              Dynamic problem recommendations targeted specifically at your weakest topics and identified misconceptions.
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: 48, textAlign: 'center' }}>
          <Sparkles size={32} color="#10b981" className="pulse-indicator" style={{ marginBottom: 16 }} />
          <p style={{ color: 'var(--text-muted)' }}>Synthesizing personalized curriculum recommendations...</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20 }}>
          {recommendations.map((rec, i) => {
            const prob = rec.problem;
            return (
              <div 
                key={prob.id} 
                className="glass-panel-elevated" 
                style={{
                  padding: 24,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  border: rec.priority === 'High' ? '1px solid rgba(244, 63, 94, 0.4)' : '1px solid var(--border-glass)',
                  position: 'relative'
                }}
              >
                {/* Priority ribbon */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <span className={`badge ${prob.difficulty === 'Easy' ? 'badge-easy' : prob.difficulty === 'Medium' ? 'badge-medium' : 'badge-hard'}`}>
                    {prob.difficulty}
                  </span>

                  <span style={{
                    fontSize: '0.725rem',
                    fontWeight: 700,
                    padding: '2px 8px',
                    borderRadius: 12,
                    background: rec.priority === 'High' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                    color: rec.priority === 'High' ? '#fb7185' : '#a5b4fc',
                    border: `1px solid ${rec.priority === 'High' ? 'rgba(244, 63, 94, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`
                  }}>
                    {rec.priority} Priority Focus
                  </span>
                </div>

                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 8, color: '#f8fafc' }}>
                    {prob.title}
                  </h3>
                  
                  <span className="badge badge-topic" style={{ marginBottom: 12 }}>
                    {prob.topic}
                  </span>

                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: 16 }}>
                    {prob.description}
                  </p>

                  <div style={{
                    background: 'rgba(15, 23, 42, 0.7)',
                    padding: '10px 12px',
                    borderRadius: 8,
                    border: '1px solid var(--border-glass)',
                    fontSize: '0.8rem',
                    color: '#cbd5e1',
                    marginBottom: 20,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8
                  }}>
                    <Target size={16} color="#06b6d4" />
                    <span>{rec.reason}</span>
                  </div>
                </div>

                <button 
                  className="btn btn-emerald"
                  onClick={() => onSelectProblem(prob.id)}
                  style={{ width: '100%', padding: '10px 0' }}
                >
                  <Code2 size={16} />
                  <span>Start Practice in IDE</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
