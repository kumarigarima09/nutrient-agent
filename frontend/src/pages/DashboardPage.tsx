import { useEffect, useState, useCallback } from 'react';
import { dashboardApi, weightApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import MacroRing from '../components/dashboard/MacroRing';
import WeightChart from '../components/dashboard/WeightChart';
import QuickLog from '../components/dashboard/QuickLog';

function StatCard({ label, value, unit, icon, color, sub }: any) {
  return (
    <div className="metric-card" style={{ position: 'relative', overflow: 'hidden', background: '#ffffff', borderRadius: 'var(--radius-lg)' }}>
      <div style={{ position: 'absolute', top: 14, right: 16, fontSize: 22, opacity: 0.2 }}>{icon}</div>
      <div style={{
        fontSize: 11,
        color: 'var(--text-muted)',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        fontFamily: 'var(--font-mono)',
        marginBottom: 8
      }}>
        {label}
      </div>
      <div style={{
        fontSize: 28,
        fontWeight: 700,
        fontFamily: 'var(--font-serif)',
        color: color || 'var(--text-primary)',
        letterSpacing: '-0.02em',
        lineHeight: 1
      }}>
        {value}
        <span style={{ fontSize: 13, fontWeight: 500, fontFamily: 'var(--font-sans)', color: 'var(--text-muted)', marginLeft: 4 }}>
          {unit}
        </span>
      </div>
      {sub && <div style={{ fontSize: 11.5, color: 'var(--text-secondary)', marginTop: 8 }}>{sub}</div>}
    </div>
  );
}

function MacroBar({ label, consumed, target, color }: any) {
  const pct = target > 0 ? Math.min(100, (consumed / target) * 100) : 0;
  const over = consumed > target;
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{label}</span>
        <span style={{ fontSize: 12, color: over ? 'var(--accent-rose)' : 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {Math.round(consumed)}g / {Math.round(target)}g
        </span>
      </div>
      <div className="progress-track" style={{ background: 'var(--bg-subtle)' }}>
        <div className="progress-fill" style={{ width: `${pct}%`, background: over ? 'var(--accent-rose)' : color }} />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { profile } = useAuth();
  const [dash, setDash] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [weightInput, setWeightInput] = useState('');
  const [loggingWeight, setLoggingWeight] = useState(false);

  const load = useCallback(async () => {
    try {
      const d = await dashboardApi.get();
      setDash(d);
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function logWeight() {
    if (!weightInput) return;
    setLoggingWeight(true);
    try {
      await weightApi.log(parseFloat(weightInput));
      setWeightInput('');
      await load();
    } finally { setLoggingWeight(false); }
  }

  const firstName = (profile?.name || profile?.full_name || 'there').split(' ')[0];
  const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' });

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 14 }}>
        <div className="spinner" style={{ width: 28, height: 28 }} />
        <span style={{ color: 'var(--text-secondary)' }}>Loading your dashboard…</span>
      </div>
    );
  }

  const metrics = dash?.metrics || {};
  const cal = metrics.calories || {};
  const prot = metrics.protein || {};
  const carbs = metrics.carbs || {};
  const fat = metrics.fat || {};
  const water = metrics.water || {};
  const weightData = dash?.weight || {};
  const todayMeals: any[] = dash?.today_meals || [];
  const recommendation = dash?.active_recommendation || {};

  const calCurrent = cal.current || 0;
  const calTarget = cal.target || 0;
  const calPct = calTarget > 0 ? Math.min(100, (calCurrent / calTarget) * 100) : 0;

  return (
    <div style={{ padding: '32px 36px', maxWidth: 1160, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
        <div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 11,
            letterSpacing: '0.12em',
            color: 'var(--accent-terracotta)',
            textTransform: 'uppercase',
            fontWeight: 600,
            marginBottom: 4
          }}>
            Daily Overview
          </div>
          <h1 style={{ fontSize: 32, fontWeight: 700, fontFamily: 'var(--font-serif)', color: 'var(--text-primary)', marginBottom: 4, letterSpacing: '-0.02em' }}>
            Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 17 ? 'afternoon' : 'evening'}, {firstName}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13.5 }}>{today}</p>
        </div>

        {/* Quick weight log */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', background: '#ffffff', padding: '6px 8px', borderRadius: 'var(--radius-full)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-card)' }}>
          <input
            id="dash-weight-input"
            type="number"
            step="0.1"
            placeholder="Log weight (kg)"
            value={weightInput}
            onChange={e => setWeightInput(e.target.value)}
            style={{
              width: 140,
              padding: '6px 14px',
              border: 'none',
              outline: 'none',
              fontSize: 13,
              fontFamily: 'var(--font-sans)',
              color: 'var(--text-primary)',
              background: 'transparent'
            }}
            onKeyDown={e => e.key === 'Enter' && logWeight()}
          />
          <button
            id="dash-log-weight"
            className="btn-primary"
            onClick={logWeight}
            disabled={loggingWeight}
            style={{ padding: '7px 16px', fontSize: 12.5 }}
          >
            {loggingWeight ? <span className="spinner" style={{ width: 13, height: 13 }} /> : 'Log'}
          </button>
        </div>
      </div>

      {/* Calorie Hero Card */}
      <div className="glass-card" style={{
        marginBottom: 24,
        padding: '28px 32px',
        background: '#ffffff',
        display: 'flex',
        alignItems: 'center',
        gap: 36,
        borderRadius: 'var(--radius-xl)'
      }}>
        <div style={{ textAlign: 'center', minWidth: 120 }}>
          <MacroRing percentage={calPct} calories={calCurrent} target={calTarget} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: 11,
            color: 'var(--accent-terracotta)',
            fontFamily: 'var(--font-mono)',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontWeight: 600,
            marginBottom: 4
          }}>
            Energy Intake
          </div>
          <div style={{
            fontSize: 40,
            fontWeight: 700,
            fontFamily: 'var(--font-serif)',
            letterSpacing: '-0.03em',
            marginBottom: 2,
            color: 'var(--text-primary)'
          }}>
            <span>{Math.round(calCurrent)}</span>
            <span style={{ fontSize: 18, color: 'var(--text-muted)', fontFamily: 'var(--font-sans)', fontWeight: 400, marginLeft: 8 }}>
              / {Math.round(calTarget)} kcal
            </span>
          </div>
          <div style={{ fontSize: 13.5, color: 'var(--text-secondary)' }}>
            <span style={{ fontWeight: 600, color: 'var(--accent-terracotta)' }}>
              {Math.round(cal.remaining ?? Math.max(0, calTarget - calCurrent))} kcal
            </span> remaining for your goal
          </div>

          {/* Macro Bars */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20, marginTop: 22 }}>
            <MacroBar label="Protein" consumed={prot.current || 0} target={prot.target || 0} color="var(--accent-sage-dark)" />
            <MacroBar label="Carbs" consumed={carbs.current || 0} target={carbs.target || 0} color="var(--accent-ochre)" />
            <MacroBar label="Fats" consumed={fat.current || 0} target={fat.target || 0} color="var(--accent-terracotta)" />
          </div>
        </div>
      </div>

      {/* Stat Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard
          label="Current Weight"
          value={weightData.current_kg ? Number(weightData.current_kg).toFixed(1) : '—'}
          unit="kg" icon="⚖️" color="var(--accent-terracotta)"
          sub={`Target: ${weightData.target_kg || '—'} kg`}
        />
        <StatCard
          label="Calorie Goal"
          value={Math.round(calTarget)}
          unit="kcal" icon="🎯" color="var(--accent-sage-dark)"
          sub="Daily target"
        />
        <StatCard
          label="Hydration"
          value={Math.round(water.current_ml || 0)}
          unit="ml" icon="💧" color="var(--accent-blue)"
          sub={`Goal: ${Math.round(water.target_ml || 2500)} ml`}
        />
        <StatCard
          label="Meals Logged"
          value={todayMeals.length}
          unit="meals" icon="🍽️" color="var(--accent-ochre)"
          sub="Today's intake"
        />
      </div>

      {/* Bottom Grid: Trend & Quick Log */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
        <div className="glass-card" style={{ padding: 24, background: '#ffffff' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
            <span style={{ fontSize: 18 }}>📈</span>
            <h3 style={{ fontSize: 16, fontWeight: 700, fontFamily: 'var(--font-serif)', color: 'var(--text-primary)' }}>
              Weight Trend
            </h3>
          </div>
          <WeightChart />
        </div>
        <div className="glass-card" style={{ padding: 24, background: '#ffffff' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
            <span style={{ fontSize: 18 }}>⚡</span>
            <h3 style={{ fontSize: 16, fontWeight: 700, fontFamily: 'var(--font-serif)', color: 'var(--text-primary)' }}>
              Quick Food Log
            </h3>
          </div>
          <QuickLog onLogged={load} />
        </div>
      </div>

      {/* Today's Meals */}
      {todayMeals.length > 0 && (
        <div className="glass-card" style={{ padding: 24, marginBottom: 24, background: '#ffffff' }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, fontFamily: 'var(--font-serif)', color: 'var(--text-primary)', marginBottom: 16 }}>
            🍽️ Today's Meals
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {todayMeals.map((meal: any) => (
              <div key={meal.id} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 18px',
                background: 'var(--bg-card-2)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)'
              }}>
                <div>
                  <div style={{ fontSize: 13.5, fontWeight: 600, textTransform: 'capitalize', color: 'var(--text-primary)' }}>
                    {meal.meal_type}
                  </div>
                  <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 2 }}>
                    {meal.items?.map((it: any) => it.food_name).join(', ') || 'No items'}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--accent-terracotta)', fontFamily: 'var(--font-mono)' }}>
                    {Math.round(meal.total_calories)} kcal
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    P: {Math.round(meal.total_protein_g)}g
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Recommendation Banner */}
      {recommendation.text && (
        <div className="glass-card" style={{
          padding: '20px 24px',
          background: 'var(--accent-sage-light)',
          border: '1px solid rgba(126, 146, 120, 0.3)',
          borderRadius: 'var(--radius-lg)'
        }}>
          <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
            <span style={{ fontSize: 22 }}>🌱</span>
            <div>
              <div style={{
                fontSize: 11,
                fontWeight: 700,
                color: 'var(--accent-sage-dark)',
                marginBottom: 4,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                fontFamily: 'var(--font-mono)'
              }}>
                Food Companion Insight
              </div>
              <p style={{ fontSize: 13.5, color: 'var(--text-primary)', margin: 0, lineHeight: 1.6 }}>
                {recommendation.text}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
