import { useState } from 'react';
import { useGraphStore } from '../store/graphStore';
import LiveLogPanel from '../components/LiveLogPanel';
import { useApi } from '../hooks/useApi';

const AGENT_NAMES = [
  'Signature','Spike','Behavior','Port Scan','DDoS','SQLi/XSS',
  'Brute Force','Lateral Movement','Exfiltration','Ransomware',
  'MITM','Supply Inject','Priv Escalation','C2/Beaconing',
  'Graph GCN','Zero-Day','Temporal/APT'
];

export default function RealTime() {
  const { agentScores, addEvent } = useGraphStore();
  const api = useApi();
  const [simulating, setSimulating] = useState(false);

  const handleSimulate = async () => {
    setSimulating(true);
    try { await api.simulate({}); } catch {}
    setTimeout(() => setSimulating(false), 500);
  };

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1rem'}}>
        <h1 style={{fontSize:'1.4rem',fontWeight:800,color:'#E2E8F0'}}>
          <span style={{color:'#00F0FF'}}>Real-Time</span> — Live Event Feed
        </h1>
        <button className="btn btn-cyan" onClick={handleSimulate} disabled={simulating}>
          {simulating ? '⏳ Simulating...' : '⚡ Simulate Event'}
        </button>
      </div>

      {/* Agent firing indicators */}
      <div className="glass-card" style={{marginBottom:'1rem'}}>
        <h3 style={{fontSize:'0.7rem',color:'#64748B',textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:'0.7rem'}}>Agent Firing Indicators</h3>
        <div style={{display:'flex',flexWrap:'wrap',gap:'0.4rem'}}>
          {AGENT_NAMES.map(name => {
            const data = agentScores[name] || {};
            const score = data.score || 0;
            const firing = score > 0.4;
            return (
              <div key={name} style={{padding:'0.3rem 0.6rem',borderRadius:'6px',background:firing?'rgba(255,23,68,0.1)':'rgba(0,240,255,0.03)',border:`1px solid ${firing?'rgba(255,23,68,0.3)':'rgba(0,240,255,0.05)'}`,display:'flex',alignItems:'center',gap:'0.4rem',transition:'all 0.3s',animation:firing?'flash-score 0.5s':''}}>
                <div style={{width:6,height:6,borderRadius:'50%',background:firing?'#FF1744':'#1E293B',boxShadow:firing?'0 0 6px #FF1744':''}}/>
                <span style={{fontSize:'0.65rem',color:firing?'#FF1744':'#64748B',fontWeight:firing?600:400}}>{name}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Event Log */}
      <div className="glass-card" style={{padding:0}}>
        <div style={{padding:'0.75rem 1rem',borderBottom:'1px solid rgba(0,240,255,0.08)'}}>
          <h3 style={{fontSize:'0.7rem',color:'#64748B',textTransform:'uppercase',letterSpacing:'0.1em'}}>Event Stream</h3>
        </div>
        <LiveLogPanel maxItems={50} />
      </div>
    </div>
  );
}
