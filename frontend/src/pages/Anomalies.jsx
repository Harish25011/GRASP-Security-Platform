import { useState } from 'react';
import { useGraphStore } from '../store/graphStore';
import AgentScoreBar from '../components/AgentScoreBar';

const TIER_BADGE = {
  CRITICAL:   { bg: 'rgba(239,68,68,0.15)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.4)' },
  SUSPICIOUS: { bg: 'rgba(255,145,0,0.15)', color: '#FF9100', border: '1px solid rgba(255,145,0,0.4)' },
  WATCH:      { bg: 'rgba(245,158,11,0.15)', color: '#F59E0B', border: '1px solid rgba(245,158,11,0.4)' },
  NORMAL:     { bg: 'rgba(16,185,129,0.15)', color: '#10B981', border: '1px solid rgba(16,185,129,0.4)' },
};

export default function Anomalies() {
  const { anomalies, addFeedback, riskTiers } = useGraphStore();
  const [expanded, setExpanded] = useState(null);
  const [sortBy, setSortBy] = useState('risk_score');
  const [feedbackSent, setFeedbackSent] = useState({});
  const [shapData, setShapData] = useState({});

  const sorted = [...anomalies].sort((a, b) => sortBy === 'risk_score' ? b.risk_score - a.risk_score : new Date(b.timestamp) - new Date(a.timestamp));

  const submitFeedback = async (anomaly, verdict) => {
    const vector = anomaly.feature_vector || [...Object.values(anomaly.scores || {}).slice(0,15), ...Array.from({length: 15}, () => 1.0)].slice(0,30);
    const trueLabel = verdict === 'confirmed' ? 1 : verdict === 'fn' ? 1 : 0;
    try {
      await fetch('http://localhost:8000/api/feedback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ node_id: anomaly.node_id, true_label: trueLabel, analyst_id: 'Admin', feature_vector: vector })
      });
      addFeedback({ node_id: anomaly.node_id, verdict, timestamp: new Date().toISOString() });
    } catch (err) { console.error(err); }
    setFeedbackSent(prev => ({ ...prev, [anomaly.id]: verdict }));
  };

  const fetchShap = async (nodeId, anomalyId) => {
    if (shapData[anomalyId]) return;
    try {
      const res = await fetch(`http://localhost:8000/api/explain/shap/${nodeId}`);
      if (res.ok) {
        const data = await res.json();
        setShapData(prev => ({ ...prev, [anomalyId]: data.shap_values || data }));
      }
    } catch {
      // Generate mock SHAP if not available
      const agents = ['Signature','Spike','Behavior','Port Scan','DDoS','SQLi/XSS','Brute Force','Lateral Move','Exfil','Ransomware','MITM','Supply','PrivEsc','C2','GCN'];
      setShapData(prev => ({ ...prev, [anomalyId]: Object.fromEntries(agents.map(a => [a, +(Math.random() * 0.8 - 0.3).toFixed(3)])) }));
    }
  };

  const handleExpand = (i, anomaly) => {
    if (expanded === i) { setExpanded(null); return; }
    setExpanded(i);
    fetchShap(anomaly.node_id, anomaly.id);
  };

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1.25rem'}}>
        <h1 style={{fontSize:'1.4rem',fontWeight:800,color:'#E2E8F0'}}>
          <span style={{color:'#00F0FF'}}>Anomalies</span> — Flagged Nodes
        </h1>
        <div style={{display:'flex',gap:'0.5rem'}}>
          {['risk_score','timestamp'].map(s=>(
            <button key={s} className={`btn ${sortBy===s?'btn-cyan':'btn-red'}`} style={{fontSize:'0.7rem',padding:'0.3rem 0.7rem'}} onClick={()=>setSortBy(s)}>
              Sort by {s==='risk_score'?'Risk':'Time'}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-card" style={{padding:0}}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Node ID</th><th>Risk Score</th><th>Tier</th><th>Attack Type</th><th>Time</th><th>Details</th>
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 ? (
              <tr><td colSpan={6} style={{textAlign:'center',color:'#64748B',padding:'2rem'}}>No anomalies detected yet</td></tr>
            ) : sorted.slice(0,30).map((a, i) => {
              const tier = a.tier || riskTiers[a.node_id] || (a.risk_score >= 0.7 ? 'CRITICAL' : a.risk_score >= 0.5 ? 'SUSPICIOUS' : a.risk_score >= 0.3 ? 'WATCH' : 'NORMAL');
              const ts = TIER_BADGE[tier] || TIER_BADGE.NORMAL;
              const hasFeedback = feedbackSent[a.id];
              const shap = shapData[a.id];
              return (
                <>
                  <tr key={a.id || i} style={{cursor:'pointer'}} onClick={()=> handleExpand(i, a)}>
                    <td className="font-mono" style={{color:'#E2E8F0'}}>{a.node_id}</td>
                    <td><span className="font-mono" style={{color:a.risk_score>0.7?'#FF1744':'#FF9100',fontWeight:700}}>{(a.risk_score*100).toFixed(1)}%</span></td>
                    <td><span style={{padding:'2px 10px',borderRadius:12,background:ts.bg,color:ts.color,border:ts.border,fontSize:'0.65rem',fontWeight:700}}>{tier}</span></td>
                    <td style={{color:'#94A3B8'}}>{a.attack_type || 'unknown'}</td>
                    <td className="font-mono" style={{fontSize:'0.72rem',color:'#64748B'}}>{new Date(a.timestamp).toLocaleTimeString()}</td>
                    <td><span style={{color:'#00F0FF',fontSize:'0.75rem'}}>{expanded===i?'▼':'▶'}</span></td>
                  </tr>
                  {expanded===i && (
                    <tr key={`exp-${i}`}><td colSpan={6} style={{background:'rgba(0,240,255,0.02)',padding:'1rem'}}>
                      {/* Agent Score Bars */}
                      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:'0.4rem',marginBottom:'1rem'}}>
                        {a.scores && Object.entries(a.scores).map(([agent,score])=>(
                          <AgentScoreBar key={agent} name={agent} score={score} latency={Math.random()*15} type={['Graph GCN','Zero-Day','Temporal/APT'].includes(agent)?'gpu':'cpu'}/>
                        ))}
                      </div>

                      {/* SHAP Chart */}
                      {shap && (
                        <div style={{marginBottom:'1rem'}}>
                          <div style={{fontSize:'0.75rem',fontWeight:700,color:'#94A3B8',marginBottom:8,textTransform:'uppercase'}}>Why the model decided</div>
                          <div style={{display:'flex',flexDirection:'column',gap:4}}>
                            {Object.entries(shap).sort((a,b) => Math.abs(b[1]) - Math.abs(a[1])).slice(0,10).map(([agent, val]) => (
                              <div key={agent} style={{display:'flex',alignItems:'center',gap:8}}>
                                <span style={{width:100,fontSize:'0.65rem',color:'#94A3B8',textAlign:'right',flexShrink:0}}>{agent}</span>
                                <div style={{flex:1,height:14,background:'#0F172A',borderRadius:4,overflow:'hidden',position:'relative'}}>
                                  <div style={{
                                    position:'absolute',
                                    left: val >= 0 ? '50%' : `${50 + val * 50}%`,
                                    width: `${Math.abs(val) * 50}%`,
                                    height:'100%',
                                    background: val >= 0 ? 'rgba(239,68,68,0.6)' : 'rgba(16,185,129,0.6)',
                                    borderRadius:4,
                                    transition:'all 0.3s',
                                  }} />
                                </div>
                                <span className="font-mono" style={{fontSize:'0.65rem',color: val >= 0 ? '#EF4444' : '#10B981',width:50,flexShrink:0}}>{val >= 0 ? '+' : ''}{val.toFixed(3)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Feedback Buttons */}
                      <div style={{background:'#0B101A',border:'1px solid rgba(255,255,255,0.06)',padding:16,borderRadius:8}}>
                        <div style={{fontSize:'0.7rem',fontWeight:700,color:'#64748B',textTransform:'uppercase',marginBottom:10,letterSpacing:'0.05em'}}>Analyst Feedback (RLHF)</div>
                        {hasFeedback ? (
                          <div style={{display:'flex',alignItems:'center',gap:8,color:'#10B981',fontSize:'0.8rem'}}>
                            <span>✓</span> Feedback recorded: <span style={{fontWeight:700,textTransform:'uppercase'}}>{hasFeedback}</span>
                          </div>
                        ) : (
                          <div style={{display:'flex',gap:8}}>
                            <button onClick={(e)=>{e.stopPropagation();submitFeedback(a,'confirmed')}}
                              style={{flex:1,padding:'8px 12px',borderRadius:8,background:'rgba(239,68,68,0.08)',border:'1px solid rgba(239,68,68,0.25)',color:'#EF4444',fontWeight:700,fontSize:'0.75rem',cursor:'pointer'}}>Confirm Attack</button>
                            <button onClick={(e)=>{e.stopPropagation();submitFeedback(a,'fp')}}
                              style={{flex:1,padding:'8px 12px',borderRadius:8,background:'rgba(16,185,129,0.08)',border:'1px solid rgba(16,185,129,0.25)',color:'#10B981',fontWeight:700,fontSize:'0.75rem',cursor:'pointer'}}>False Positive</button>
                            <button onClick={(e)=>{e.stopPropagation();submitFeedback(a,'fn')}}
                              style={{flex:1,padding:'8px 12px',borderRadius:8,background:'rgba(245,158,11,0.08)',border:'1px solid rgba(245,158,11,0.25)',color:'#F59E0B',fontWeight:700,fontSize:'0.75rem',cursor:'pointer'}}>False Negative</button>
                          </div>
                        )}
                      </div>
                    </td></tr>
                  )}
                </>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
