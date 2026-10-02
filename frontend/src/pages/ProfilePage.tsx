import { useState } from 'react';
import { profileApi } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const { profile, refreshProfile, user, logout } = useAuth();
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState<any>(profile || {});

  const set = (k: string, v: any) => setForm((f: any) => ({ ...f, [k]: v }));

  async function save() {
    setBusy(true);
    setError('');
    try {
      await profileApi.update(form);
      await refreshProfile();
      setEditing(false);
    } catch (e: any) {
      setError(e.message);
    } finally { setBusy(false); }
  }

  const firstName = (profile?.name || profile?.full_name || 'User').split(' ')[0];

  const INFO_FIELDS = [
    { key:'age', label:'Age', unit:'years', type:'number' },
    { key:'height_cm', label:'Height', unit:'cm', type:'number' },
    { key:'current_weight_kg', label:'Current Weight', unit:'kg', type:'number', step:0.1 },
    { key:'target_weight_kg', label:'Target Weight', unit:'kg', type:'number', step:0.1 },
  ];

  const goalLabels: Record<string, string> = {
    weight_loss: '📉 Weight Loss',
    muscle_gain: '💪 Muscle Gain',
    maintenance: '⚖️ Maintenance',
    endurance: '🏃 Endurance',
    general_health: '❤️ General Health',
  };

  const activityLabels: Record<string, string> = {
    sedentary: 'Sedentary',
    light: 'Lightly Active',
    moderate: 'Moderately Active',
    very_active: 'Very Active',
    athlete: 'Extremely Active',
  };

  return (
    <div style={{ padding:'32px 36px', maxWidth:800, margin:'0 auto', fontFamily:'Inter,sans-serif' }}>
      <h1 style={{ fontSize:26, fontWeight:900, letterSpacing:'-0.02em', marginBottom:4 }}>👤 Profile</h1>
      <p style={{ color:'var(--text-muted)', fontSize:14, marginBottom:32 }}>Your personal nutrition profile and account settings.</p>

      {/* Avatar card */}
      <div className="glass-card" style={{ padding:28, display:'flex', alignItems:'center', gap:24, marginBottom:24 }}>
        <div style={{
          width:72, height:72, borderRadius:'50%',
          background:'linear-gradient(135deg, var(--accent-teal), var(--accent-blue))',
          display:'flex', alignItems:'center', justifyContent:'center',
          fontSize:28, fontWeight:900, color:'#fff', flexShrink:0,
        }}>
          {firstName[0]?.toUpperCase()}
        </div>
        <div>
          <div style={{ fontSize:22, fontWeight:800, color:'var(--text-primary)' }}>{profile?.name || profile?.full_name || 'User'}</div>
          <div style={{ fontSize:14, color:'var(--text-secondary)' }}>{user?.email}</div>
          <div style={{ display:'flex', gap:8, marginTop:8 }}>
            <span className="badge badge-teal">{goalLabels[profile?.goal] || profile?.goal}</span>
            <span className="badge badge-blue">{profile?.diet_type}</span>
            {profile?.sex && <span className="badge" style={{ background:'rgba(167,139,250,0.1)', color:'var(--accent-purple)' }}>{profile.sex}</span>}
          </div>
        </div>
        <button
          id="profile-edit-btn"
          className="btn-secondary"
          style={{ marginLeft:'auto' }}
          onClick={() => { setEditing(e => !e); setForm(profile); }}
        >
          {editing ? '✕ Cancel' : '✎ Edit Profile'}
        </button>
      </div>

      {editing ? (
        <div className="glass-card" style={{ padding:28 }}>
          <h3 style={{ fontSize:16, fontWeight:700, marginBottom:20 }}>Edit Profile</h3>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
            <div style={{ gridColumn:'1/-1' }}>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Full Name</label>
              <input id="profile-name" className="input-field" value={form.name || form.full_name || ''} onChange={e => set('name', e.target.value)} />
            </div>
            {INFO_FIELDS.map(f => (
              <div key={f.key}>
                <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>{f.label} ({f.unit})</label>
                <input id={`profile-${f.key}`} type={f.type} step={(f as any).step} className="input-field" value={form[f.key] || ''} onChange={e => set(f.key, e.target.value)} />
              </div>
            ))}
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Goal</label>
              <select id="profile-goal" className="input-field" value={form.goal || ''} onChange={e => set('goal', e.target.value)}>
                {Object.entries(goalLabels).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Activity Level</label>
              <select id="profile-activity" className="input-field" value={form.activity_level || ''} onChange={e => set('activity_level', e.target.value)}>
                {Object.entries(activityLabels).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Diet Type</label>
              <select id="profile-diet" className="input-field" value={form.diet_type || ''} onChange={e => set('diet_type', e.target.value)}>
                {['omnivore','vegetarian','vegan','keto','paleo'].map(d => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize:13, color:'var(--text-secondary)', display:'block', marginBottom:6, fontWeight:500 }}>Weekly Rate (kg/week)</label>
              <input id="profile-rate" type="number" step={0.1} min={0.1} max={1} className="input-field" value={form.weekly_weight_change_target_kg || ''} onChange={e => set('weekly_weight_change_target_kg', e.target.value)} />
            </div>
          </div>
          {error && <div style={{ marginTop:16, fontSize:13, color:'var(--accent-rose)', background:'rgba(244,63,94,0.08)', padding:'10px 14px', borderRadius:8 }}>{error}</div>}
          <div style={{ display:'flex', gap:12, marginTop:24 }}>
            <button id="profile-save" className="btn-primary" onClick={save} disabled={busy}>
              {busy ? <><span className="spinner" style={{ width:14, height:14 }} /> Saving…</> : '💾 Save Changes'}
            </button>
            <button className="btn-secondary" onClick={() => setEditing(false)}>Cancel</button>
          </div>
        </div>
      ) : (
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:20 }}>
          {/* Body stats */}
          <div className="glass-card" style={{ padding:24 }}>
            <h3 style={{ fontSize:15, fontWeight:700, marginBottom:16 }}>📏 Body Stats</h3>
            {[
              { label:'Age', val:`${profile?.age} years` },
              { label:'Height', val:`${profile?.height_cm} cm` },
              { label:'Current Weight', val:`${profile?.current_weight_kg} kg` },
              { label:'Target Weight', val:`${profile?.target_weight_kg} kg` },
              { label:'Sex', val:profile?.sex },
              { label:'BMI (approx)', val: profile?.height_cm && profile?.current_weight_kg ? `${(profile.current_weight_kg / Math.pow(profile.height_cm / 100, 2)).toFixed(1)}` : '—' },
            ].map(r => (
              <div key={r.label} style={{ display:'flex', justifyContent:'space-between', padding:'9px 0', borderBottom:'1px solid var(--border)' }}>
                <span style={{ fontSize:13, color:'var(--text-muted)' }}>{r.label}</span>
                <span style={{ fontSize:13, fontWeight:600, color:'var(--text-primary)', textTransform:'capitalize' }}>{r.val}</span>
              </div>
            ))}
          </div>

          {/* Goal & activity */}
          <div className="glass-card" style={{ padding:24 }}>
            <h3 style={{ fontSize:15, fontWeight:700, marginBottom:16 }}>🎯 Goals & Preferences</h3>
            {[
              { label:'Primary Goal', val:goalLabels[profile?.goal] || profile?.goal },
              { label:'Activity Level', val:activityLabels[profile?.activity_level] || profile?.activity_level },
              { label:'Diet Type', val:profile?.diet_type },
              { label:'Weekly Rate', val:`${profile?.weekly_weight_change_target_kg} kg/week` },
              { label:'Allergies', val:(profile?.allergies ? (typeof profile.allergies === 'string' ? profile.allergies || 'None' : (profile.allergies as string[]).join(', ') || 'None') : 'None') },
            ].map(r => (
              <div key={r.label} style={{ display:'flex', justifyContent:'space-between', padding:'9px 0', borderBottom:'1px solid var(--border)' }}>
                <span style={{ fontSize:13, color:'var(--text-muted)' }}>{r.label}</span>
                <span style={{ fontSize:13, fontWeight:600, color:'var(--text-primary)', textTransform:'capitalize', textAlign:'right', maxWidth:'55%' }}>{r.val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Danger zone */}
      <div style={{ marginTop:32, padding:'20px 24px', border:'1px solid rgba(244,63,94,0.2)', borderRadius:16, background:'rgba(244,63,94,0.03)' }}>
        <h3 style={{ fontSize:14, fontWeight:700, color:'var(--accent-rose)', marginBottom:8 }}>Account Actions</h3>
        <button id="profile-logout" className="btn-secondary" onClick={logout} style={{ borderColor:'rgba(244,63,94,0.3)', color:'var(--accent-rose)', fontSize:13 }}>
          ← Sign Out
        </button>
      </div>
    </div>
  );
}
