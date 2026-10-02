import { useState, useEffect, useCallback } from 'react';
import { foodLogApi, foodsApi, foodImageApi } from '../api/client';

export default function FoodLogPage() {
  const [summary, setSummary] = useState<any>(null);
  const [nlText, setNlText] = useState('');
  const [logBusy, setLogBusy] = useState(false);
  const [logResult, setLogResult] = useState<any>(null);
  const [searchQ, setSearchQ] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [waterMl, setWaterMl] = useState(250);
  const [waterBusy, setWaterBusy] = useState(false);
  const [imgBusy, setImgBusy] = useState(false);
  const [imgResult, setImgResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'nl' | 'search' | 'photo'>('nl');

  const loadSummary = useCallback(async () => {
    try {
      const s = await foodLogApi.today();
      setSummary(s);
    } catch { }
  }, []);

  useEffect(() => { loadSummary(); }, [loadSummary]);

  async function logNL() {
    if (!nlText.trim()) return;
    setLogBusy(true);
    setLogResult(null);
    try {
      const r = await foodLogApi.logNL(nlText);
      setLogResult(r);
      setNlText('');
      await loadSummary();
    } catch (e: any) { setLogResult({ error: e.message }); }
    finally { setLogBusy(false); }
  }

  async function search() {
    if (!searchQ.trim()) return;
    setSearching(true);
    try {
      const r = await foodsApi.search(searchQ);
      setSearchResults(r);
    } catch { } finally { setSearching(false); }
  }

  async function logWater() {
    setWaterBusy(true);
    try {
      await foodLogApi.logWater(waterMl);
      await loadSummary();
    } catch { } finally { setWaterBusy(false); }
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImgBusy(true);
    setImgResult(null);
    try {
      const r = await foodImageApi.analyze(file);
      setImgResult(r);
      await loadSummary();
    } catch (err: any) { setImgResult({ error: err.message }); }
    finally { setImgBusy(false); }
  }

  const WATER_PRESETS = [150, 200, 250, 350, 500];

  return (
    <div style={{ padding:'32px 36px', maxWidth:1000, margin:'0 auto', fontFamily:'Inter,sans-serif' }}>
      <h1 style={{ fontSize:26, fontWeight:900, letterSpacing:'-0.02em', marginBottom:4 }}>📝 Food Log</h1>
      <p style={{ color:'var(--text-muted)', fontSize:14, marginBottom:28 }}>Track everything you eat and drink today.</p>

      {/* Today summary */}
      {summary && (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap:14, marginBottom:28 }}>
          {[
            { label:'Calories', val:`${Math.round(summary.metrics?.calories?.current || 0)}`, unit:'kcal', color:'var(--accent-teal)' },
            { label:'Protein', val:`${Math.round(summary.metrics?.protein?.current || 0)}`, unit:'g', color:'var(--accent-blue)' },
            { label:'Carbs', val:`${Math.round(summary.metrics?.carbs?.current || 0)}`, unit:'g', color:'var(--accent-orange)' },
            { label:'Fats', val:`${Math.round(summary.metrics?.fat?.current || 0)}`, unit:'g', color:'var(--accent-purple)' },
            { label:'Water', val:`${Math.round(summary.metrics?.water?.current_ml || 0)}`, unit:'ml', color:'var(--accent-blue)' },
          ].map(m => (
            <div key={m.label} className="metric-card" style={{ textAlign:'center' }}>
              <div style={{ fontSize:11, color:'var(--text-muted)', marginBottom:4, textTransform:'uppercase', letterSpacing:'0.05em' }}>{m.label}</div>
              <div style={{ fontSize:24, fontWeight:900, color:m.color }}>{m.val}<span style={{ fontSize:12, fontWeight:400, color:'var(--text-muted)' }}> {m.unit}</span></div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24 }}>
        {/* Log panel */}
        <div className="glass-card" style={{ padding:24 }}>
          {/* Tab switcher */}
          <div style={{ display:'flex', gap:4, background:'rgba(255,255,255,0.04)', borderRadius:10, padding:4, marginBottom:20 }}>
            {(['nl','search','photo'] as const).map(t => (
              <button key={t} id={`foodlog-tab-${t}`} onClick={() => setActiveTab(t)} style={{
                flex:1, padding:'8px 0', borderRadius:8, border:'none', cursor:'pointer', fontSize:13, fontWeight:600, transition:'all 0.2s',
                background: activeTab === t ? 'var(--bg-card-2)' : 'transparent',
                color: activeTab === t ? 'var(--text-primary)' : 'var(--text-muted)',
              }}>
                {t === 'nl' ? '📝 Text' : t === 'search' ? '🔍 Search' : '📷 Photo'}
              </button>
            ))}
          </div>

          {activeTab === 'nl' && (
            <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
              <textarea
                id="foodlog-nl-input"
                className="input-field"
                rows={3}
                placeholder="Describe what you ate, e.g. '2 chapati with dal and raita for lunch'"
                value={nlText}
                onChange={e => setNlText(e.target.value)}
                style={{ resize:'vertical' }}
              />
              <button id="foodlog-nl-submit" className="btn-primary" onClick={logNL} disabled={logBusy || !nlText.trim()}>
                {logBusy ? <><span className="spinner" style={{ width:14, height:14 }} /> Parsing…</> : 'Log Meal'}
              </button>
              {logResult && !logResult.error && (
                <div className="fade-in" style={{ background:'rgba(0,212,170,0.06)', border:'1px solid rgba(0,212,170,0.2)', borderRadius:12, padding:14 }}>
                  <div style={{ fontSize:12, fontWeight:700, color:'var(--accent-teal)', marginBottom:8 }}>✓ Logged</div>
                  {logResult.entries?.map((e: any, i: number) => (
                    <div key={i} style={{ display:'flex', justifyContent:'space-between', fontSize:13, color:'var(--text-secondary)', marginBottom:4 }}>
                      <span>{e.food_name} ({e.quantity}g)</span>
                      <span style={{ fontWeight:600, color:'var(--text-primary)' }}>{Math.round(e.calories)} kcal</span>
                    </div>
                  ))}
                </div>
              )}
              {logResult?.error && <div style={{ fontSize:12, color:'var(--accent-rose)', background:'rgba(244,63,94,0.08)', padding:'8px 12px', borderRadius:8 }}>{logResult.error}</div>}
            </div>
          )}

          {activeTab === 'search' && (
            <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
              <div style={{ display:'flex', gap:8 }}>
                <input id="foodlog-search-input" className="input-field" placeholder="Search Indian foods…" value={searchQ} onChange={e => setSearchQ(e.target.value)} onKeyDown={e => e.key === 'Enter' && search()} />
                <button id="foodlog-search-btn" className="btn-secondary" onClick={search} disabled={searching}>
                  {searching ? <span className="spinner" style={{ width:14, height:14 }} /> : '🔍'}
                </button>
              </div>
              <div style={{ maxHeight:300, overflowY:'auto', display:'flex', flexDirection:'column', gap:8 }}>
                {searchResults.map(food => (
                  <div key={food.id} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 14px', background:'rgba(255,255,255,0.03)', border:'1px solid var(--border)', borderRadius:10 }}>
                    <div>
                      <div style={{ fontSize:13, fontWeight:600, color:'var(--text-primary)' }}>{food.name}</div>
                      <div style={{ fontSize:11, color:'var(--text-muted)' }}>{food.category} · per 100g</div>
                    </div>
                    <div style={{ textAlign:'right', fontSize:13 }}>
                      <div style={{ fontWeight:700, color:'var(--accent-teal)' }}>{food.calories_per_100g} kcal</div>
                      <div style={{ fontSize:11, color:'var(--text-muted)' }}>P:{food.protein_per_100g}g C:{food.carbs_per_100g}g</div>
                    </div>
                  </div>
                ))}
                {searchResults.length === 0 && searchQ && !searching && (
                  <div style={{ textAlign:'center', color:'var(--text-muted)', fontSize:13, paddingTop:20 }}>No results. Try different keywords.</div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'photo' && (
            <div style={{ display:'flex', flexDirection:'column', gap:16, alignItems:'center', textAlign:'center', paddingTop:10 }}>
              <div style={{ fontSize:48 }}>📷</div>
              <p style={{ fontSize:14, color:'var(--text-secondary)' }}>Take a photo of your meal and our Vision AI will identify the food and estimate macros.</p>
              <label id="foodlog-photo-label" style={{
                display:'inline-flex', alignItems:'center', gap:8,
                padding:'12px 24px', background:'linear-gradient(135deg, var(--accent-teal), var(--accent-blue))',
                borderRadius:12, color:'#fff', fontWeight:600, cursor:'pointer', fontSize:14,
              }}>
                {imgBusy ? <><span className="spinner" style={{ width:14, height:14 }} /> Analyzing…</> : '📷 Upload Food Photo'}
                <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display:'none' }} disabled={imgBusy} />
              </label>
              {imgResult && !imgResult.error && (
                <div className="fade-in" style={{ background:'rgba(0,212,170,0.06)', border:'1px solid rgba(0,212,170,0.2)', borderRadius:12, padding:16, width:'100%', textAlign:'left' }}>
                  <div style={{ fontSize:12, fontWeight:700, color:'var(--accent-teal)', marginBottom:8 }}>✓ Vision Analysis</div>
                  <div style={{ fontSize:14, color:'var(--text-primary)', fontWeight:600, marginBottom:8 }}>{imgResult.detected_foods?.join(', ')}</div>
                  <div style={{ fontSize:13, color:'var(--text-secondary)' }}>Est. {Math.round(imgResult.estimated_calories || 0)} kcal · {Math.round(imgResult.estimated_protein || 0)}g protein</div>
                </div>
              )}
              {imgResult?.error && <div style={{ fontSize:12, color:'var(--accent-rose)' }}>{imgResult.error}</div>}
            </div>
          )}
        </div>

        {/* Right side: Water tracker + recent log */}
        <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
          {/* Water tracker */}
          <div className="glass-card" style={{ padding:24 }}>
            <h3 style={{ fontSize:15, fontWeight:700, marginBottom:16, display:'flex', alignItems:'center', gap:8 }}>💧 Water Tracker</h3>
            <div style={{ display:'flex', gap:6, flexWrap:'wrap', marginBottom:14 }}>
              {WATER_PRESETS.map(ml => (
                <button key={ml} id={`water-preset-${ml}`} onClick={() => setWaterMl(ml)} style={{
                  padding:'6px 12px', borderRadius:8, border:'1px solid', fontSize:13, cursor:'pointer', transition:'all 0.2s',
                  borderColor: waterMl === ml ? 'var(--accent-teal)' : 'var(--border)',
                  background: waterMl === ml ? 'rgba(0,212,170,0.1)' : 'rgba(255,255,255,0.03)',
                  color: waterMl === ml ? 'var(--accent-teal)' : 'var(--text-secondary)',
                  fontWeight: waterMl === ml ? 700 : 400,
                }}>
                  {ml} ml
                </button>
              ))}
            </div>
            <div style={{ display:'flex', gap:8, alignItems:'center' }}>
              <input id="water-custom-input" type="number" className="input-field" min={50} max={2000} value={waterMl} onChange={e => setWaterMl(parseInt(e.target.value))} style={{ flex:1 }} />
              <button id="water-log-btn" className="btn-primary" onClick={logWater} disabled={waterBusy} style={{ flexShrink:0 }}>
                {waterBusy ? <span className="spinner" style={{ width:14, height:14 }} /> : '+ Log'}
              </button>
            </div>
            {summary?.metrics?.water?.current_ml > 0 && (
              <div style={{ marginTop:14 }}>
                <div style={{ fontSize:12, color:'var(--text-muted)', marginBottom:6 }}>
                  Today: {Math.round(summary.metrics?.water?.current_ml)} / {Math.round(summary.metrics?.water?.target_ml || 2500)} ml
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width:`${Math.min(100, ((summary.metrics?.water?.current_ml || 0) / (summary.metrics?.water?.target_ml || 2500)) * 100)}%`, background:'var(--accent-blue)' }} />
                </div>
              </div>
            )}
          </div>

          {/* Recent log entries */}
          <div className="glass-card" style={{ padding:24, flex:1 }}>
            <h3 style={{ fontSize:15, fontWeight:700, marginBottom:16 }}>📋 Today's Log</h3>
            {(() => {
              // today_meals is an array of meal objects, each with items[]
              const allItems: any[] = (summary?.today_meals || []).flatMap((m: any) => m.items || []);
              return allItems.length > 0 ? (
                <div style={{ display:'flex', flexDirection:'column', gap:8, maxHeight:280, overflowY:'auto' }}>
                  {allItems.map((e: any, i: number) => (
                    <div key={i} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 12px', background:'rgba(255,255,255,0.03)', borderRadius:10 }}>
                      <div>
                        <div style={{ fontSize:13, fontWeight:600, color:'var(--text-primary)' }}>{e.food_name}</div>
                        <div style={{ fontSize:11, color:'var(--text-muted)' }}>{e.quantity}{e.unit || 'g'}</div>
                      </div>
                      <div style={{ textAlign:'right', fontSize:12 }}>
                        <div style={{ fontWeight:700, color:'var(--accent-teal)' }}>{Math.round(e.calories)} kcal</div>
                        <div style={{ color:'var(--text-muted)' }}>P:{Math.round(e.protein_g || 0)}g</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign:'center', color:'var(--text-muted)', fontSize:13, paddingTop:20 }}>
                  <div style={{ fontSize:28, marginBottom:8 }}>📭</div>
                  Nothing logged yet today
                </div>
              );
            })()}
          </div>
        </div>
      </div>
    </div>
  );
}
