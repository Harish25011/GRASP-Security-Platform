import { useGraphStore } from '../store/graphStore';
import AgentScoreBar from '../components/AgentScoreBar';

const AGENT_META = [
  {name:'Signature',type:'cpu'},{name:'Spike',type:'cpu'},{name:'Behavior',type:'cpu'},
  {name:'Port Scan',type:'cpu'},{name:'DDoS',type:'cpu'},{name:'SQLi/XSS',type:'cpu'},
  {name:'Brute Force',type:'cpu'},{name:'Lateral Movement',type:'cpu'},{name:'Exfiltration',type:'cpu'},
  {name:'Ransomware',type:'cpu'},{name:'MITM',type:'cpu'},{name:'Supply Inject',type:'cpu'},
  {name:'Priv Escalation',type:'cpu'},{name:'C2/Beaconing',type:'cpu'},
  {name:'Graph GCN',type:'gpu'},{name:'Zero-Day',type:'gpu'},{name:'Temporal/APT',type:'gpu'},
];

export default function AgentStatus() {
  const { agentScores } = useGraphStore();

  return (
    <div>
      <h1 style={{fontSize:'1.4rem',fontWeight:800,marginBottom:'1.25rem',color:'#E2E8F0'}}>
        <span style={{color:'#00F0FF'}}>Agent Status</span> — 15-Agent Swarm
      </h1>
      <div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:'0.5rem'}}>
        {AGENT_META.map(a => {
          const data = agentScores[a.name] || {};
          return (
            <AgentScoreBar key={a.name} name={a.name} score={data.score || 0}
              latency={data.latency || 0} type={a.type} />
          );
        })}
      </div>
      <div className="glass-card" style={{marginTop:'1rem'}}>
        <h3 style={{fontSize:'0.75rem',color:'#64748B',textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:'0.75rem'}}>Agent Performance Summary</h3>
        <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'1rem'}}>
          {[
            {l:'CPU Agents',v:'14',c:'#94A3B8'},{l:'GPU Agents',v:'3',c:'#00F0FF'},
            {l:'Avg Latency',v:`${(Object.values(agentScores).reduce((s,a)=>s+(a.latency||0),0)/17).toFixed(1)}ms`,c:'#00E676'},
            {l:'Active Detections',v:Object.values(agentScores).filter(a=>(a.score||0)>0.5).length,c:'#FF1744'},
          ].map(s=>(
            <div key={s.l} style={{textAlign:'center'}}>
              <div className="font-mono" style={{fontSize:'1.4rem',fontWeight:800,color:s.c}}>{s.v}</div>
              <div style={{fontSize:'0.65rem',color:'#64748B',marginTop:'0.2rem'}}>{s.l}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
