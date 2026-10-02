import { useEffect, useState, useCallback } from 'react';
import { progressApi, weightApi } from '../api/client';
import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div style={{ background:'var(--bg-card)', border:'1px solid var(--border)', borderRadius:10, padding:'10px 14px', fontSize:12 }}>
        <div style={{ color:'var(--text-muted)', marginBottom:6, fontWeight:600 }}>{label}</div>
        {payload.map((p: any) => (
          <div key={p.name} style={{ color:p.color, marginBottom:2 }}>{p.name}: {Math.round(p.value)}</div>
        ))}
      </div>
    );
  }
  return null;
};

export default function ProgressPage() {
  const [progress, setProgress] = useState<any>(null);
  const [weightHistory, setWeightHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [p, w] = await Promise.all([progressApi.weekly(), weightApi.history(30)]);
      setProgress(p);
      setWeightHistory((w || []).map((r: any) => ({
        date: new Date(r.logged_at || r.date).toLocaleDateString('en-IN', { day:'numeric', month:'short' }),
        weight: r.weight_kg,
      })).reverse());
    } catch { }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return <div style={{ display:'flex', alignItems:'center', justifyContent:'center', height:'100%', gap:14 }}>
      <div className="spinner" style={{ width:28, height:28 }} />
      <span style={{ color:'var(--text-secondary)', fontFamily:'Inter,sans-serif' }}>Loading progress…</span>
    </div>;
  }

  const macroData = progress?.daily_summaries?.map((d: any) => ({
    date: new Date(d.date).toLocaleDateString('en-IN', { day:'numeric', month:'short' }),
    Calories: Math.round(d.calories || 0),
    Protein: Math.round(d.protein || 0),
    Carbs: Math.round(d.carbs || 0),
    Fats: Math.round(d.fat || 0),
  })) || [];

  // Backend returns: averages.daily_calories, adherence.calorie_adherence_pct, weight_analysis
  const averages = progress?.averages || {};
  const adherence = progress?.adherence || {};
  const weightAnalysis = progress?.weight_analysis || {};
  const recommendation = progress?.recommendation || {};

  const stats = [
    { label:'7-Day Avg Calories', val: Math.round(averages.daily_calories || 0), unit:'kcal', color:'var(--accent-teal)' },
    { label:'7-Day Avg Protein', val: Math.round(averages.daily_protein_g || 0), unit:'g', color:'var(--accent-blue)' },
    { label:'Days Logged', val: progress?.days_logged || 0, unit:'days', color:'var(--accent-orange)' },
    { label:'Adherence Score', val: Math.round(adherence.calorie_adherence_pct || 0), unit:'%', color:'var(--accent-green)' },
  ];

  return (
    <div style={{ padding:'32px 36px', maxWidth:1100, margin:'0 auto', fontFamily:'Inter,sans-serif' }}>
      <h1 style={{ fontSize:26, fontWeight:900, letterSpacing:'-0.02em', marginBottom:4 }}>📈 Progress Tracking</h1>
      <p style={{ color:'var(--text-muted)', fontSize:14, marginBottom:28 }}>Your 7-day and 30-day nutrition & weight analytics.</p>

      {/* Stat summary */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:16, marginBottom:28 }}>
        {stats.map(s => (
          <div key={s.label} className="metric-card" style={{ textAlign:'center' }}>
            <div style={{ fontSize:11, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:6 }}>{s.label}</div>
            <div style={{ fontSize:32, fontWeight:900, color:s.color }}>{s.val}<span style={{ fontSize:13, fontWeight:400, color:'var(--text-muted)', marginLeft:3 }}>{s.unit}</span></div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24, marginBottom:24 }}>
        <div className="glass-card" style={{ padding:24 }}>
          <h3 style={{ fontSize:15, fontWeight:700, marginBottom:20 }}>📊 Daily Calories (7 days)</h3>
          {macroData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={macroData} margin={{ top:4, right:8, bottom:0, left:-20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="date" tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="Calories" fill="var(--accent-teal)" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </div>

        <div className="glass-card" style={{ padding:24 }}>
          <h3 style={{ fontSize:15, fontWeight:700, marginBottom:20 }}>📉 Weight Trend (30 days)</h3>
          {weightHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={weightHistory} margin={{ top:4, right:8, bottom:0, left:-20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="date" tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} domain={['auto','auto']} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="weight" stroke="var(--accent-blue)" strokeWidth={2.5} dot={{ fill:'var(--accent-blue)', r:3, strokeWidth:0 }} activeDot={{ r:5 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : <EmptyChart />}
        </div>
      </div>

      {/* Macro breakdown */}
      {macroData.length > 0 && (
        <div className="glass-card" style={{ padding:24 }}>
          <h3 style={{ fontSize:15, fontWeight:700, marginBottom:20 }}>🥗 Macro Breakdown (7 days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={macroData} margin={{ top:4, right:8, bottom:0, left:-20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize:12, color:'var(--text-secondary)' }} />
              <Bar dataKey="Protein" fill="var(--accent-blue)" radius={[2,2,0,0]} stackId="a" />
              <Bar dataKey="Carbs" fill="var(--accent-orange)" radius={[0,0,0,0]} stackId="a" />
              <Bar dataKey="Fats" fill="#a78bfa" radius={[2,2,0,0]} stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* AI Recommendation */}
      {recommendation.text && (
        <div className="glass-card" style={{ padding:24, marginTop:24, background:'rgba(0,212,170,0.04)', border:'1px solid rgba(0,212,170,0.15)' }}>
          <h3 style={{ fontSize:15, fontWeight:700, marginBottom:16 }}>🤖 AI Coaching Recommendation</h3>
          <div style={{ display:'flex', gap:12, padding:'12px 16px', borderRadius:10 }}>
            <span style={{ fontSize:16, flexShrink:0 }}>💡</span>
            <p style={{ fontSize:13, color:'var(--text-secondary)', margin:0, lineHeight:1.6 }}>{recommendation.text}</p>
          </div>
          {recommendation.suggested_calorie_delta !== 0 && (
            <div style={{ marginTop:12, padding:'8px 14px', background:'rgba(0,212,170,0.08)', borderRadius:8, fontSize:12, color:'var(--accent-teal)', fontWeight:600 }}>
              Suggested calorie adjustment: {recommendation.suggested_calorie_delta > 0 ? '+' : ''}{recommendation.suggested_calorie_delta} kcal → New target: {Math.round(recommendation.new_calorie_target || 0)} kcal
            </div>
          )}
        </div>
      )}

      {/* Weight analysis */}
      {weightAnalysis.trend && weightAnalysis.trend !== 'insufficient_data' && (
        <div className="glass-card" style={{ padding:24, marginTop:24 }}>
          <h3 style={{ fontSize:15, fontWeight:700, marginBottom:16 }}>⚖️ Weight Analysis</h3>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:16 }}>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:11, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:4 }}>Trend</div>
              <div style={{ fontSize:18, fontWeight:700, color: weightAnalysis.trend === 'losing' ? 'var(--accent-teal)' : weightAnalysis.trend === 'gaining' ? 'var(--accent-orange)' : 'var(--accent-blue)' }}>
                {weightAnalysis.trend === 'losing' ? '📉 Losing' : weightAnalysis.trend === 'gaining' ? '📈 Gaining' : '⚖️ Stable'}
              </div>
            </div>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:11, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:4 }}>Net Change</div>
              <div style={{ fontSize:18, fontWeight:700, color:'var(--text-primary)' }}>{weightAnalysis.net_change_kg > 0 ? '+' : ''}{weightAnalysis.net_change_kg} kg</div>
            </div>
            <div style={{ textAlign:'center' }}>
              <div style={{ fontSize:11, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:4 }}>Weekly Rate</div>
              <div style={{ fontSize:18, fontWeight:700, color:'var(--text-primary)' }}>{weightAnalysis.weekly_rate_kg > 0 ? '+' : ''}{weightAnalysis.weekly_rate_kg} kg/wk</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function EmptyChart() {
  return (
    <div style={{ height:220, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', color:'var(--text-muted)', gap:8 }}>
      <span style={{ fontSize:32 }}>📭</span>
      <span style={{ fontSize:13 }}>Not enough data yet. Keep logging!</span>
    </div>
  );
}
