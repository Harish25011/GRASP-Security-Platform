import { useEffect, useState } from 'react';
import { useGraphStore } from '../store/graphStore';

export default function AgentScoreBar({ name, score, latency, type }) {
  const { agentConfidence } = useGraphStore();
  const [animated, setAnimated] = useState(false);
  const [prevScore, setPrevScore] = useState(0);
  const pct = Math.round(score * 100);
  const color = score > 0.7 ? '#FF1744' : score > 0.5 ? '#FF9100' : score > 0.3 ? '#FFD600' : '#00E676';

  // Get confidence from Zustand store
  const confidence = agentConfidence[name] ?? 1.0;
  const confPct = Math.round(confidence * 100);

  // Confidence ring style
  let ringBorder;
  if (confidence >= 0.8) ringBorder = '2px solid rgba(0,240,255,0.6)';
  else if (confidence >= 0.2) ringBorder = `2px solid rgba(0,240,255,${confidence * 0.6})`;
  else ringBorder = '2px dotted rgba(100,116,139,0.4)';

  useEffect(() => {
    if (Math.abs(score - prevScore) > 0.15) {
      setAnimated(true);
      setTimeout(() => setAnimated(false), 500);
    }
    setPrevScore(score);
  }, [score]);

  return (
    <div className={animated ? 'flash-score' : ''} style={{padding:'0.5rem 0.7rem',background:'rgba(17,24,39,0.6)',borderRadius:'8px',border: ringBorder,transition:'all 0.3s'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'0.3rem'}}>
        <div style={{display:'flex',alignItems:'center',gap:'0.4rem'}}>
          <span style={{width:'6px',height:'6px',borderRadius:'50%',background:type==='gpu'?'#00F0FF':'#94A3B8'}}/>
          <span style={{fontSize:'0.72rem',fontWeight:600,color:'#E2E8F0'}}>{name}</span>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:'0.5rem'}}>
          <span className="font-mono" style={{fontSize:'0.72rem',color,fontWeight:700}}>{pct}%</span>
          <span className="font-mono" style={{fontSize:'0.6rem',color:'#64748B'}}>{latency?.toFixed?latency.toFixed(1):latency}ms</span>
        </div>
      </div>
      <div style={{height:'4px',background:'rgba(0,240,255,0.05)',borderRadius:'2px',overflow:'hidden'}}>
        <div className="bar-animate" style={{height:'100%',width:`${pct}%`,background:`linear-gradient(90deg, ${color}88, ${color})`,borderRadius:'2px',transition:'width 0.4s ease',boxShadow:score>0.5?`0 0 8px ${color}44`:''}}/>
      </div>
      <div className="font-mono" style={{fontSize:'0.58rem',color:'rgba(0,240,255,0.5)',marginTop:'0.25rem',textAlign:'right'}}>{confPct}% conf</div>
    </div>
  );
}
