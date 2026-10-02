import { useState } from 'react';
import { foodLogApi } from '../../api/client';

export default function QuickLog({ onLogged }: { onLogged?: () => void }) {
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const SUGGESTIONS = [
    '2 idli with sambar',
    '1 cup chai with biscuits',
    'Dal tadka with 2 chapati',
    '200ml skimmed milk',
  ];

  async function log() {
    if (!text.trim()) return;
    setBusy(true);
    setError('');
    setResult(null);
    try {
      const res = await foodLogApi.logNL(text);
      setResult(res);
      setText('');
      onLogged?.();
    } catch (e: any) {
      setError(e.message);
    } finally { setBusy(false); }
  }

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ display:'flex', gap:8 }}>
        <input
          id="quicklog-input"
          className="input-field"
          placeholder="e.g. 2 rotis with paneer sabzi…"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && log()}
          style={{ flex:1 }}
        />
        <button id="quicklog-btn" className="btn-primary" onClick={log} disabled={busy || !text.trim()} style={{ flexShrink:0 }}>
          {busy ? <span className="spinner" style={{ width:14, height:14 }} /> : 'Log'}
        </button>
      </div>

      {/* Suggestions */}
      <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
        {SUGGESTIONS.map(s => (
          <button key={s} onClick={() => setText(s)} style={{
            background:'rgba(255,255,255,0.03)', border:'1px solid var(--border)', borderRadius:8,
            padding:'5px 10px', fontSize:11, color:'var(--text-muted)', cursor:'pointer', transition:'all 0.2s',
          }}
          onMouseEnter={e => { (e.target as HTMLElement).style.color = 'var(--accent-teal)'; (e.target as HTMLElement).style.borderColor = 'rgba(0,212,170,0.4)'; }}
          onMouseLeave={e => { (e.target as HTMLElement).style.color = 'var(--text-muted)'; (e.target as HTMLElement).style.borderColor = 'var(--border)'; }}
          >
            {s}
          </button>
        ))}
      </div>

      {error && <div style={{ fontSize:12, color:'var(--accent-rose)', background:'rgba(244,63,94,0.08)', padding:'8px 12px', borderRadius:8 }}>{error}</div>}

      {result && (
        <div className="fade-in" style={{ background:'rgba(0,212,170,0.06)', border:'1px solid rgba(0,212,170,0.2)', borderRadius:12, padding:'12px 16px' }}>
          <div style={{ fontSize:12, color:'var(--accent-teal)', fontWeight:700, marginBottom:8 }}>✓ Logged successfully</div>
          {result.entries?.map((e: any, i: number) => (
            <div key={i} style={{ display:'flex', justifyContent:'space-between', fontSize:13, color:'var(--text-secondary)', paddingBottom:4 }}>
              <span>{e.food_name}</span>
              <span style={{ color:'var(--text-primary)', fontWeight:600 }}>{Math.round(e.calories)} kcal · {Math.round(e.protein)}g P</span>
            </div>
          ))}
          {result.total && (
            <div style={{ borderTop:'1px solid rgba(0,212,170,0.15)', marginTop:8, paddingTop:8, display:'flex', justifyContent:'space-between', fontSize:13, fontWeight:700 }}>
              <span style={{ color:'var(--text-primary)' }}>Total</span>
              <span style={{ color:'var(--accent-teal)' }}>{Math.round(result.total.calories)} kcal</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
