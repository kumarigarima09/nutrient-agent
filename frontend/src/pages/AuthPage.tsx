import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

function LeafIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22v-7"/>
      <path d="M12 15c-3.5 0-6-2.5-6-6 4 0 6 2 6 6Z"/>
      <path d="M12 15c3.5 0 6-2.5 6-6-4 0-6 2-6 6Z"/>
    </svg>
  );
}

const features = [
  { icon: '🌱', title: 'Deterministic Targets', desc: 'Precision BMR & TDEE calculated with Mifflin-St Jeor formulas.' },
  { icon: '🍽️', title: '7-Day Meal Scheduling', desc: 'Varied weekly plans tailored to cultural tastes & macro splits.' },
  { icon: '🛒', title: 'Aggregated Grocery Hauls', desc: 'Automated supermarket checklists categorized by fresh aisles.' },
  { icon: '🤖', title: 'Grounded AI Coach', desc: 'Practical, pressure-free advice rooted in scientific nutrition.' },
];

export default function AuthPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password, name);
      }
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ minHeight: '100dvh', display: 'flex', fontFamily: 'var(--font-sans)', background: 'var(--bg-base)' }}>
      {/* Left panel - Warm editorial branding */}
      <div style={{
        flex: '0 0 52%',
        background: 'linear-gradient(145deg, #ede8df 0%, #ebe4d8 60%, #e3dcd0 100%)',
        borderRight: '1px solid var(--border)',
        padding: '60px 64px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Ambient subtle circles */}
        <div style={{
          position: 'absolute', top: '-15%', left: '-15%', width: 500, height: 500,
          borderRadius: '50%', background: 'radial-gradient(circle, rgba(209, 100, 77, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none'
        }} />

        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            color: '#ffffff',
            background: 'var(--accent-terracotta)',
            padding: 10,
            borderRadius: 14,
            display: 'flex',
            boxShadow: '0 2px 8px rgba(209, 100, 77, 0.25)'
          }}>
            <LeafIcon />
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700, fontFamily: 'var(--font-serif)', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
              Nutrient Agent
            </div>
            <div style={{ fontSize: 10.5, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
              Everyday Food Support
            </div>
          </div>
        </div>

        {/* Hero Copy */}
        <div style={{ margin: '40px 0' }}>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 11,
            letterSpacing: '0.12em',
            color: 'var(--accent-terracotta)',
            fontWeight: 600,
            textTransform: 'uppercase',
            marginBottom: 12
          }}>
            A softer start to food guidance
          </div>
          <h1 style={{
            fontSize: 46,
            fontWeight: 600,
            fontFamily: 'var(--font-serif)',
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            color: 'var(--text-primary)',
            marginBottom: 18
          }}>
            What would make eating feel <em style={{ fontStyle: 'italic', color: 'var(--accent-terracotta)' }}>easier?</em>
          </h1>
          <p style={{ fontSize: 16.5, color: 'var(--text-secondary)', lineHeight: 1.65, maxWidth: 460, marginBottom: 36 }}>
            Practical, personal, pressure-free food guidance built on deterministic science-backed calculations.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            {features.map(f => (
              <div key={f.title} style={{
                background: 'rgba(255, 255, 255, 0.65)',
                border: '1px solid var(--border)',
                borderRadius: 14,
                padding: '14px 16px',
                boxShadow: '0 1px 3px rgba(31, 41, 34, 0.03)'
              }}>
                <div style={{ fontSize: 20, marginBottom: 6 }}>{f.icon}</div>
                <div style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{f.title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          🔒 Evidence-grounded AI agent · Deterministic calculations
        </div>
      </div>

      {/* Right form panel */}
      <div style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px',
        background: 'var(--bg-base)',
      }}>
        <div style={{
          width: '100%',
          maxWidth: 420,
          background: '#ffffff',
          border: '1px solid var(--border)',
          borderRadius: 24,
          padding: '36px 32px',
          boxShadow: '0 8px 30px rgba(31, 41, 34, 0.05)'
        }}>
          <h2 style={{ fontSize: 28, fontWeight: 700, fontFamily: 'var(--font-serif)', color: 'var(--text-primary)', marginBottom: 6, letterSpacing: '-0.02em' }}>
            {mode === 'login' ? 'Welcome back' : 'Get started free'}
          </h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginBottom: 28 }}>
            {mode === 'login' ? 'Sign in to access your everyday nutrition companion.' : 'Create your personal nutrition profile.'}
          </p>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {mode === 'register' && (
              <div>
                <label style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)', display: 'block', marginBottom: 6 }}>Full Name</label>
                <input
                  id="auth-name"
                  type="text"
                  className="input-field"
                  placeholder="Priya Sharma"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  required
                />
              </div>
            )}
            <div>
              <label style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)', display: 'block', marginBottom: 6 }}>Email address</label>
              <input
                id="auth-email"
                type="email"
                className="input-field"
                placeholder="priya@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)', display: 'block', marginBottom: 6 }}>Password</label>
              <input
                id="auth-password"
                type="password"
                className="input-field"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            {error && (
              <div style={{ background: '#fdf0f0', border: '1px solid rgba(200, 83, 83, 0.3)', borderRadius: 10, padding: '10px 14px', fontSize: 12.5, color: 'var(--accent-rose)' }}>
                {error}
              </div>
            )}

            <button id="auth-submit" type="submit" className="btn-primary" disabled={busy} style={{ marginTop: 4, padding: '13px 24px', fontSize: 14.5 }}>
              {busy ? <span className="spinner" /> : (mode === 'login' ? 'Sign In' : 'Create Account')}
            </button>
          </form>

          <div style={{ textAlign: 'center', marginTop: 22, fontSize: 13.5, color: 'var(--text-muted)' }}>
            {mode === 'login' ? "Don't have an account? " : "Already have an account? "}
            <button
              id="auth-toggle"
              onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
              style={{ background: 'none', border: 'none', color: 'var(--accent-terracotta)', fontWeight: 600, cursor: 'pointer', fontSize: 13.5 }}
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </div>

          <div style={{
            marginTop: 32,
            padding: '14px 18px',
            background: 'var(--accent-sage-light)',
            border: '1px solid rgba(126, 146, 120, 0.25)',
            borderRadius: 14
          }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-sage-dark)', marginBottom: 4 }}>🧪 Demo Account</div>
            <div style={{ fontSize: 11.5, color: 'var(--text-secondary)' }}>Email: <code style={{ color: 'var(--text-primary)', fontWeight: 600 }}>demo@nutritionagent.ai</code></div>
            <div style={{ fontSize: 11.5, color: 'var(--text-secondary)' }}>Password: <code style={{ color: 'var(--text-primary)', fontWeight: 600 }}>demo1234</code></div>
          </div>
        </div>
      </div>
    </div>
  );
}
