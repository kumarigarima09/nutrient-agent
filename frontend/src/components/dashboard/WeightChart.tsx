import { useEffect, useState } from 'react';
import { weightApi } from '../../api/client';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  Tooltip, CartesianGrid, ReferenceLine
} from 'recharts';

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div style={{ background:'var(--bg-card)', border:'1px solid var(--border)', borderRadius:10, padding:'10px 14px', fontSize:13 }}>
        <div style={{ color:'var(--text-muted)', marginBottom:4 }}>{label}</div>
        <div style={{ color:'var(--accent-teal)', fontWeight:700 }}>{payload[0].value} kg</div>
      </div>
    );
  }
  return null;
};

export default function WeightChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    weightApi.history(30).then(raw => {
      const points = (raw || []).map((r: any) => ({
        date: new Date(r.logged_at || r.date).toLocaleDateString('en-IN', { day:'numeric', month:'short' }),
        weight: r.weight_kg,
      })).reverse();
      setData(points);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ height:180, display:'flex', alignItems:'center', justifyContent:'center' }}><div className="spinner" /></div>;

  if (data.length === 0) {
    return (
      <div style={{ height:180, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', color:'var(--text-muted)', gap:10 }}>
        <span style={{ fontSize:32 }}>⚖️</span>
        <span style={{ fontSize:13 }}>No weight entries yet. Log your weight from the dashboard.</span>
      </div>
    );
  }

  const avg = data.reduce((s, d) => s + d.weight, 0) / data.length;

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top:4, right:8, bottom:0, left:-20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis dataKey="date" tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill:'var(--text-muted)', fontSize:10 }} tickLine={false} axisLine={false} domain={['auto','auto']} />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine y={avg} stroke="rgba(255,255,255,0.1)" strokeDasharray="4 4" label={{ value:'avg', fill:'var(--text-muted)', fontSize:10 }} />
        <Line
          type="monotone"
          dataKey="weight"
          stroke="var(--accent-teal)"
          strokeWidth={2.5}
          dot={{ fill:'var(--accent-teal)', r:3, strokeWidth:0 }}
          activeDot={{ r:5, fill:'var(--accent-teal)', filter:'drop-shadow(0 0 6px var(--accent-teal))' }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
