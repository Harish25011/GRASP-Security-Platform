import AgentScoreBar from './AgentScoreBar';

export default function NodeCard({ node, onClose }) {
  if (!node) return null;
  const { id, label, node_type, risk_score, status } = node;
  const color = risk_score > 0.7 ? '#FF1744' : risk_score > 0.5 ? '#FF9100' : risk_score > 0.3 ? '#FFD600' : '#00E676';

  return (
    <div style={{position:'fixed',right:0,top:0,bottom:0,width:'380px',background:'rgba(10,14,23,0.97)',borderLeft:'1px solid rgba(0,240,255,0.15)',backdropFilter:'blur(20px)',padding:'1.5rem',overflowY:'auto',zIndex:60,animation:'slideInRight 0.3s ease'}}>
      <style>{`@keyframes slideInRight{from{transform:translateX(100%)}to{transform:translateX(0)}}`}</style>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1.5rem'}}>
        <h3 style={{fontSize:'1rem',fontWeight:700,color:'#00F0FF'}}>Node Details</h3>
        <button onClick={onClose} style={{background:'none',border:'none',color:'#64748B',cursor:'pointer',fontSize:'1.2rem'}}>×</button>
      </div>
      <div className="glass-card" style={{marginBottom:'1rem'}}>
        <div className="font-mono" style={{fontSize:'0.85rem',color:'#E2E8F0',marginBottom:'0.5rem'}}>{id}</div>
        <div style={{display:'flex',gap:'0.5rem',flexWrap:'wrap',marginBottom:'0.75rem'}}>
          <span className="badge badge-low">{node_type}</span>
          <span className={`badge ${status==='quarantined'?'badge-critical':'badge-low'}`}>{status}</span>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:'0.5rem'}}>
          <span style={{fontSize:'0.75rem',color:'#94A3B8'}}>Risk Score:</span>
          <span className="font-mono" style={{fontSize:'1.2rem',fontWeight:800,color}}>{(risk_score*100).toFixed(1)}%</span>
        </div>
      </div>
      <h4 style={{fontSize:'0.8rem',color:'#94A3B8',marginBottom:'0.75rem',textTransform:'uppercase',letterSpacing:'0.1em'}}>Agent Scores</h4>
      <div style={{display:'flex',flexDirection:'column',gap:'0.4rem'}}>
        {node.agent_scores ? Object.entries(node.agent_scores).map(([name, score]) => (
          <AgentScoreBar key={name} name={name} score={typeof score==='number'?score:score.score||0} latency={typeof score === 'object' ? score.latency : Math.random()*15} type={['Graph GCN','Zero-Day','Temporal/APT'].includes(name)?'gpu':'cpu'}/>
        )) : <div style={{fontSize:'0.8rem',color:'#64748B'}}>Click analyze to see scores</div>}
      </div>
    </div>
  );
}
