// MacroRing — animated SVG donut ring with Nutrient Agent palette
export default function MacroRing({ percentage, calories: _calories, target: _target }: { percentage: number; calories?: number; target?: number }) {
  const r = 52;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(100, percentage);
  const dash = (pct / 100) * circ;
  // Natural terracotta, sage, and warm ochre
  const color = pct > 90 ? 'var(--accent-terracotta)' : pct > 60 ? 'var(--accent-sage-dark)' : 'var(--accent-ochre)';

  return (
    <svg width="130" height="130" viewBox="0 0 130 130" style={{ transform:'rotate(-90deg)' }}>
      {/* Track */}
      <circle cx="65" cy="65" r={r} fill="none" stroke="var(--bg-subtle)" strokeWidth="12" />
      {/* Fill */}
      <circle
        cx="65" cy="65" r={r}
        fill="none"
        stroke={color}
        strokeWidth="12"
        strokeLinecap="round"
        strokeDasharray={`${dash} ${circ}`}
        style={{ transition:'stroke-dasharray 0.8s cubic-bezier(0.4,0,0.2,1), stroke 0.4s' }}
      />
      {/* Centre text */}
      <text
        x="65" y="58"
        textAnchor="middle"
        dominantBaseline="middle"
        style={{ transform:'rotate(90deg)', transformOrigin:'65px 65px' }}
        fill="var(--text-primary)"
        fontSize="22"
        fontWeight="700"
        fontFamily="var(--font-serif)"
      >
        {Math.round(pct)}%
      </text>
      <text
        x="65" y="78"
        textAnchor="middle"
        dominantBaseline="middle"
        style={{ transform:'rotate(90deg)', transformOrigin:'65px 65px' }}
        fill="var(--text-muted)"
        fontSize="10"
        fontFamily="var(--font-mono)"
        letterSpacing="0.05em"
      >
        OF GOAL
      </text>
    </svg>
  );
}
