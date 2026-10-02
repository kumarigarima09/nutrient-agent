import { useState } from 'react';
import { profileApi } from '../api/client';
import { useAuth } from '../context/AuthContext';

const STEPS = [
  { id: 'basics', label: 'Basic Info', icon: '👤' },
  { id: 'body', label: 'Body Stats', icon: '📏' },
  { id: 'goals', label: 'Goals', icon: '🎯' },
  { id: 'diet', label: 'Diet Prefs', icon: '🥗' },
];

const GOALS = [
  { value: 'weight_loss', label: 'Lose Weight', icon: '📉', desc: 'Healthy caloric deficit' },
  { value: 'muscle_gain', label: 'Build Muscle', icon: '💪', desc: 'Lean bulk with extra protein' },
  { value: 'maintenance', label: 'Maintain Weight', icon: '⚖️', desc: 'Sustain current body weight' },
  { value: 'endurance', label: 'Endurance', icon: '🏃', desc: 'Fuel for performance' },
  { value: 'general_health', label: 'General Health', icon: '❤️', desc: 'Balanced lifestyle nutrition' },
];

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary', desc: 'Little/no exercise' },
  { value: 'light', label: 'Lightly Active', desc: '1–3 days/week' },
  { value: 'moderate', label: 'Moderately Active', desc: '3–5 days/week' },
  { value: 'very_active', label: 'Very Active', desc: '6–7 days/week' },
  { value: 'athlete', label: 'Extremely Active', desc: 'Physical job + training' },
];

const DIET_TYPES = [
  { value: 'omnivore', label: 'Omnivore', icon: '🍗' },
  { value: 'vegetarian', label: 'Vegetarian', icon: '🥕' },
  { value: 'vegan', label: 'Vegan', icon: '🌱' },
  { value: 'keto', label: 'Keto', icon: '🥓' },
  { value: 'paleo', label: 'Paleo', icon: '🦴' },
];

const ALLERGIES = ['Gluten', 'Dairy', 'Nuts', 'Eggs', 'Soy', 'Shellfish', 'None'];

export default function OnboardingPage() {
  const { refreshProfile, logout } = useAuth();
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    name: '',
    age: 28,
    sex: 'female',
    height_cm: 162,
    current_weight_kg: 65,
    target_weight_kg: 60,
    activity_level: 'moderate',
    goal: 'weight_loss',
    diet_type: 'vegetarian',
    allergies: [] as string[],
    medical_conditions: '',
    weekly_weight_change_target_kg: 0.5,
  });

  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }));

  const toggleAllergy = (a: string) => {
    if (a === 'None') { set('allergies', []); return; }
    const cur = form.allergies;
    set('allergies', cur.includes(a) ? cur.filter(x => x !== a) : [...cur, a]);
  };

  async function submit() {
    if (!form.name.trim()) { setError('Please enter your name.'); return; }
    setBusy(true);
    setError('');
    try {
      await profileApi.create({
        name: form.name.trim(),
        age: Number(form.age),
        sex: form.sex,
        height_cm: Number(form.height_cm),
        current_weight_kg: Number(form.current_weight_kg),
        target_weight_kg: Number(form.target_weight_kg),
        activity_level: form.activity_level,
        goal: form.goal,
        diet_type: form.diet_type,
        allergies: form.allergies.join(', '),
        food_preferences: '',
        foods_disliked: '',
        budget: 'moderate',
        meal_count: 4,
        cooking_time: '30_mins',
        exercise_frequency: form.activity_level === 'sedentary' ? '0_days' : '3_4_days',
      });
      await refreshProfile();
    } catch (e: any) {
      setError(e.message);
      setBusy(false);
    }
  }

  const progress = ((step + 1) / STEPS.length) * 100;

  return (
    <div style={{ minHeight:'100dvh', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'40px 20px', fontFamily:'Inter,sans-serif', background:'var(--bg-base)' }}>
      {/* Header */}
      <div style={{ marginBottom:40, textAlign:'center' }}>
        <div style={{ fontSize:32, marginBottom:8 }}>🌱</div>
        <h1 style={{ fontSize:30, fontWeight:900, letterSpacing:'-0.02em', marginBottom:6 }}>
          <span className="gradient-text">Set Up Your Profile</span>
        </h1>
        <p style={{ color:'var(--text-secondary)', fontSize:15 }}>Let's personalise your nutrition journey in just a few steps.</p>
      </div>

      {/* Step indicators */}
      <div style={{ display:'flex', gap:8, marginBottom:36 }}>
        {STEPS.map((s, i) => (
          <div key={s.id} style={{ display:'flex', alignItems:'center', gap:8 }}>
            <div style={{
              width:32, height:32, borderRadius:'50%', display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:14, fontWeight:700,
              background: i <= step ? 'linear-gradient(135deg, var(--accent-teal), var(--accent-blue))' : 'rgba(255,255,255,0.06)',
              color: i <= step ? '#fff' : 'var(--text-muted)',
              border: i === step ? '2px solid var(--accent-teal)' : '2px solid transparent',
              transition:'all 0.3s',
            }}>
              {i < step ? '✓' : i + 1}
            </div>
            <span style={{ fontSize:13, color: i === step ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: i === step ? 600 : 400 }}>{s.label}</span>
            {i < STEPS.length - 1 && <div style={{ width:28, height:1, background: i < step ? 'var(--accent-teal)' : 'var(--border)', margin:'0 4px', transition:'background 0.3s' }} />}
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div style={{ width:'100%', maxWidth:560, marginBottom:28 }}>
        <div className="progress-track">
          <div className="progress-fill" style={{ width:`${progress}%`, background:'linear-gradient(90deg, var(--accent-teal), var(--accent-blue))' }} />
        </div>
      </div>

      {/* Card */}
      <div className="glass-card" style={{ width:'100%', maxWidth:560, padding:'36px 40px' }}>
        {/* Step 0: Basics */}
        {step === 0 && (
          <div className="fade-in" style={{ display:'flex', flexDirection:'column', gap:20 }}>
            <h2 style={{ fontSize:20, fontWeight:700, marginBottom:4 }}>Tell us about yourself</h2>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Your Name</label>
              <input id="ob-name" className="input-field" placeholder="e.g. Priya Sharma" value={form.name} onChange={e => set('name', e.target.value)} />
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
              <div>
                <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Age</label>
                <input id="ob-age" type="number" className="input-field" min={15} max={100} value={form.age} onChange={e => set('age', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Biological Sex</label>
                <select id="ob-sex" className="input-field" value={form.sex} onChange={e => set('sex', e.target.value)}>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Step 1: Body */}
        {step === 1 && (
          <div className="fade-in" style={{ display:'flex', flexDirection:'column', gap:20 }}>
            <h2 style={{ fontSize:20, fontWeight:700, marginBottom:4 }}>Your body measurements</h2>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
              <div>
                <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Height (cm)</label>
                <input id="ob-height" type="number" className="input-field" min={100} max={250} value={form.height_cm} onChange={e => set('height_cm', e.target.value)} />
              </div>
              <div>
                <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Current Weight (kg)</label>
                <input id="ob-weight" type="number" className="input-field" min={30} max={300} step={0.1} value={form.current_weight_kg} onChange={e => set('current_weight_kg', e.target.value)} />
              </div>
            </div>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:10, fontWeight:500 }}>Activity Level</label>
              <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                {ACTIVITY_LEVELS.map(a => (
                  <div key={a.value} id={`ob-activity-${a.value}`} onClick={() => set('activity_level', a.value)} style={{
                    display:'flex', justifyContent:'space-between', alignItems:'center',
                    padding:'12px 16px', borderRadius:12, cursor:'pointer', transition:'all 0.2s',
                    background: form.activity_level === a.value ? 'rgba(0,212,170,0.08)' : 'rgba(255,255,255,0.03)',
                    border:`1px solid ${form.activity_level === a.value ? 'var(--accent-teal)' : 'var(--border)'}`,
                  }}>
                    <span style={{ fontWeight:600, fontSize:14, color: form.activity_level === a.value ? 'var(--accent-teal)' : 'var(--text-primary)' }}>{a.label}</span>
                    <span style={{ fontSize:12, color:'var(--text-muted)' }}>{a.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Goals */}
        {step === 2 && (
          <div className="fade-in" style={{ display:'flex', flexDirection:'column', gap:20 }}>
            <h2 style={{ fontSize:20, fontWeight:700, marginBottom:4 }}>What's your primary goal?</h2>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
              {GOALS.map(g => (
                <div key={g.value} id={`ob-goal-${g.value}`} onClick={() => set('goal', g.value)} style={{
                  padding:'16px', borderRadius:14, cursor:'pointer', transition:'all 0.2s',
                  background: form.goal === g.value ? 'rgba(0,212,170,0.08)' : 'rgba(255,255,255,0.03)',
                  border:`1px solid ${form.goal === g.value ? 'var(--accent-teal)' : 'var(--border)'}`,
                  textAlign:'center',
                }}>
                  <div style={{ fontSize:28, marginBottom:6 }}>{g.icon}</div>
                  <div style={{ fontWeight:700, fontSize:14, color: form.goal === g.value ? 'var(--accent-teal)' : 'var(--text-primary)', marginBottom:3 }}>{g.label}</div>
                  <div style={{ fontSize:11, color:'var(--text-muted)' }}>{g.desc}</div>
                </div>
              ))}
            </div>
            {(form.goal === 'weight_loss' || form.goal === 'muscle_gain') && (
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
                <div>
                  <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Target Weight (kg)</label>
                  <input id="ob-target-weight" type="number" className="input-field" step={0.1} value={form.target_weight_kg} onChange={e => set('target_weight_kg', e.target.value)} />
                </div>
                <div>
                  <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Weekly Rate (kg/week)</label>
                  <input id="ob-rate" type="number" className="input-field" step={0.1} min={0.1} max={1} value={form.weekly_weight_change_target_kg} onChange={e => set('weekly_weight_change_target_kg', e.target.value)} />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Diet */}
        {step === 3 && (
          <div className="fade-in" style={{ display:'flex', flexDirection:'column', gap:20 }}>
            <h2 style={{ fontSize:20, fontWeight:700, marginBottom:4 }}>Dietary preferences</h2>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:10, fontWeight:500 }}>Diet Type</label>
              <div style={{ display:'flex', gap:10, flexWrap:'wrap' }}>
                {DIET_TYPES.map(d => (
                  <div key={d.value} id={`ob-diet-${d.value}`} onClick={() => set('diet_type', d.value)} style={{
                    display:'flex', alignItems:'center', gap:8, padding:'10px 16px', borderRadius:10, cursor:'pointer',
                    background: form.diet_type === d.value ? 'rgba(0,212,170,0.08)' : 'rgba(255,255,255,0.03)',
                    border:`1px solid ${form.diet_type === d.value ? 'var(--accent-teal)' : 'var(--border)'}`,
                    transition:'all 0.2s',
                  }}>
                    <span style={{ fontSize:18 }}>{d.icon}</span>
                    <span style={{ fontSize:13, fontWeight:600, color: form.diet_type === d.value ? 'var(--accent-teal)' : 'var(--text-primary)' }}>{d.label}</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:10, fontWeight:500 }}>Allergies / Intolerances</label>
              <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
                {ALLERGIES.map(a => (
                  <div key={a} id={`ob-allergy-${a}`} onClick={() => toggleAllergy(a)} style={{
                    padding:'7px 14px', borderRadius:8, cursor:'pointer', fontSize:13, fontWeight:500,
                    background: form.allergies.includes(a) ? 'rgba(244,63,94,0.1)' : 'rgba(255,255,255,0.03)',
                    border:`1px solid ${form.allergies.includes(a) ? 'var(--accent-rose)' : 'var(--border)'}`,
                    color: form.allergies.includes(a) ? 'var(--accent-rose)' : 'var(--text-secondary)',
                    transition:'all 0.2s',
                  }}>{a}</div>
                ))}
              </div>
            </div>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Medical Conditions <span style={{ color:'var(--text-muted)' }}>(optional)</span></label>
              <input id="ob-conditions" className="input-field" placeholder="e.g. Type 2 Diabetes, PCOS…" value={form.medical_conditions} onChange={e => set('medical_conditions', e.target.value)} />
            </div>
          </div>
        )}

        {error && (
          <div style={{ marginTop:16, background:'rgba(244,63,94,0.1)', border:'1px solid rgba(244,63,94,0.25)', borderRadius:10, padding:'10px 14px', fontSize:13, color:'var(--accent-rose)' }}>
            {error}
          </div>
        )}

        {/* Nav buttons */}
        <div style={{ display:'flex', justifyContent:'space-between', marginTop:32 }}>
          {step > 0 ? (
            <button id="ob-back" className="btn-secondary" onClick={() => setStep(s => s - 1)}>← Back</button>
          ) : (
            <button id="ob-skip-login" className="btn-ghost" onClick={logout}>Sign out</button>
          )}
          {step < STEPS.length - 1 ? (
            <button id="ob-next" className="btn-primary" onClick={() => setStep(s => s + 1)}>Continue →</button>
          ) : (
            <button id="ob-submit" className="btn-primary" onClick={submit} disabled={busy}>
              {busy ? <span className="spinner" /> : '🚀 Launch My Plan'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
