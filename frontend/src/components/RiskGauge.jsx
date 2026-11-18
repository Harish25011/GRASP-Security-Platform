import { useGraphStore } from '../store/graphStore';

export default function RiskGauge({ score, size = 120, nodeId }) {
  const { riskTiers } = useGraphStore();
  const pct = Math.round(score * 100);

  // 4-tier color zones
  let color, tierLabel;
  if (score >= 0.7) { color = '#FF1744'; tierLabel = 'CRITICAL'; }
  else if (score >= 0.5) { color = '#FF9100'; tierLabel = 'SUSPICIOUS'; }
  else if (score >= 0.3) { color = '#FFD600'; tierLabel = 'WATCH'; }
  else { color = '#00E676'; tierLabel = 'NORMAL'; }

  // Override with Zustand tier if available
  const storedTier = nodeId ? riskTiers[nodeId] : null;
  if (storedTier) tierLabel = storedTier;

  const radius = (size - 10) / 2;
  const circumference = Math.PI * radius;
  const offset = circumference * (1 - score);

  return (
    <div style={{position:'relative',width:size,height:size/2+30,display:'flex',flexDirection:'column',alignItems:'center'}}>
      <svg width={size} height={size/2+5} viewBox={`0 0 ${size} ${size/2+5}`}>
        {/* Background zones */}
        <path d={`M 5,${size/2} A ${radius},${radius} 0 0,1 ${size-5},${size/2}`}
          fill="none" stroke="rgba(0,240,255,0.08)" strokeWidth="6" strokeLinecap="round"/>
        {/* Active arc */}
        <path d={`M 5,${size/2} A ${radius},${radius} 0 0,1 ${size-5},${size/2}`}
          fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          style={{transition:'stroke-dashoffset 0.6s ease, stroke 0.3s',filter:`drop-shadow(0 0 6px ${color}66)`}}/>
      </svg>
      <div style={{position:'absolute',bottom:'12px',textAlign:'center'}}>
        <div className="font-mono" style={{fontSize:size/5,fontWeight:800,color,lineHeight:1}}>{pct}%</div>
        <div style={{fontSize:'0.6rem',color,fontWeight:700,marginTop:'3px',letterSpacing:'0.08em'}}>{tierLabel}</div>
      </div>
    </div>
  );
}
