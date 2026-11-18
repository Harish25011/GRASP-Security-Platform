import { useState } from 'react';
import { useGraphStore } from '../store/graphStore';
import { useApi } from '../hooks/useApi';

const TIER_BADGE = {
  CRITICAL:   { bg: 'rgba(239,68,68,0.15)', color: '#EF4444', border: '1px solid rgba(239,68,68,0.4)', order: 0 },
  SUSPICIOUS: { bg: 'rgba(255,145,0,0.15)', color: '#FF9100', border: '1px solid rgba(255,145,0,0.4)', order: 1 },
  WATCH:      { bg: 'rgba(245,158,11,0.15)', color: '#F59E0B', border: '1px solid rgba(245,158,11,0.4)', order: 2 },
  NORMAL:     { bg: 'rgba(16,185,129,0.15)', color: '#10B981', border: '1px solid rgba(16,185,129,0.4)', order: 3 },
};

export default function SafeBox() {
  const { safeBox, removeFromSafeBox, riskTiers } = useGraphStore();
  const api = useApi();
  const [sortMode, setSortMode] = useState('tier'); // 'tier' or 'time'

  const handleRelease = async (nodeId) => {
    try { await api.releaseNode(nodeId); } catch {}
    removeFromSafeBox(nodeId);
  };

  const getTier = (node) => {
    if (riskTiers[node.node_id]) return riskTiers[node.node_id];
    if (node.risk_score >= 0.7) return 'CRITICAL';
    if (node.risk_score >= 0.5) return 'SUSPICIOUS';
    if (node.risk_score >= 0.3) return 'WATCH';
    return 'NORMAL';
  };

  const sortedBox = [...safeBox].sort((a, b) => {
    if (sortMode === 'tier') {
      const ta = TIER_BADGE[getTier(a)]?.order ?? 9;
      const tb = TIER_BADGE[getTier(b)]?.order ?? 9;
      if (ta !== tb) return ta - tb;
      return new Date(b.quarantined_at) - new Date(a.quarantined_at);
    }
    return new Date(b.quarantined_at) - new Date(a.quarantined_at);
  });

  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'1.25rem'}}>
        <h1 style={{fontSize:'1.4rem',fontWeight:800,color:'#E2E8F0'}}>
          <span style={{color:'#00F0FF'}}>Safe Box</span> — Quarantined Nodes ({safeBox.length})
        </h1>
        <div style={{display:'flex',gap:'0.5rem'}}>
          <button className={`btn ${sortMode==='tier'?'btn-cyan':'btn-red'}`} style={{fontSize:'0.7rem',padding:'0.3rem 0.7rem'}} onClick={()=>setSortMode('tier')}>Sort by Tier</button>
          <button className={`btn ${sortMode==='time'?'btn-cyan':'btn-red'}`} style={{fontSize:'0.7rem',padding:'0.3rem 0.7rem'}} onClick={()=>setSortMode('time')}>Sort by Time</button>
        </div>
      </div>

      {safeBox.length === 0 ? (
        <div className="glass-card" style={{textAlign:'center',padding:'3rem',color:'#64748B'}}>
          <div style={{fontSize:'3rem',marginBottom:'0.75rem'}}>🔒</div>
          <div style={{fontSize:'0.9rem'}}>No nodes currently quarantined</div>
          <div style={{fontSize:'0.75rem',marginTop:'0.3rem'}}>Nodes with risk score &gt; 70% are automatically quarantined</div>
        </div>
      ) : (
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:'1rem'}}>
          {sortedBox.map((node, i) => {
            const tier = getTier(node);
            const ts = TIER_BADGE[tier] || TIER_BADGE.NORMAL;
            return (
              <div key={node.node_id + i} className="glass-card pulse-red" style={{border:'1px solid rgba(255,23,68,0.2)'}}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:'0.75rem'}}>
                  <div>
                    <div className="font-mono" style={{fontSize:'0.85rem',color:'#E2E8F0',fontWeight:600}}>{node.node_id}</div>
                    <div style={{fontSize:'0.65rem',color:'#64748B',marginTop:'0.2rem'}}>
                      Quarantined: {new Date(node.quarantined_at).toLocaleString()}
                    </div>
                  </div>
                  <div style={{display:'flex',flexDirection:'column',alignItems:'flex-end',gap:6}}>
                    <div className="font-mono" style={{fontSize:'1.2rem',fontWeight:800,color:'#FF1744'}}>
                      {(node.risk_score * 100).toFixed(0)}%
                    </div>
                    {/* Tier Badge */}
                    <span style={{padding:'2px 10px',borderRadius:12,background:ts.bg,color:ts.color,border:ts.border,fontSize:'0.6rem',fontWeight:700}}>{tier}</span>
                  </div>
                </div>
                <div style={{fontSize:'0.75rem',color:'#94A3B8',marginBottom:'0.75rem'}}>{node.reason}</div>

                {/* Mini sparkline */}
                <div style={{display:'flex',alignItems:'end',gap:'2px',height:'30px',marginBottom:'0.75rem'}}>
                  {Array.from({length:14}).map((_,j) => {
                    const h = Math.random() * 25 + 5;
                    return <div key={j} style={{flex:1,height:`${h}px`,background:`rgba(255,23,68,${0.2+Math.random()*0.3})`,borderRadius:'2px 2px 0 0'}} />;
                  })}
                </div>

                <div style={{display:'flex',gap:'0.5rem'}}>
                  <button className="btn btn-green" style={{flex:1,fontSize:'0.7rem'}} onClick={()=>handleRelease(node.node_id)}>
                    ✓ Release
                  </button>
                  <button className="btn btn-cyan" style={{flex:1,fontSize:'0.7rem'}}>
                    🔍 Investigate
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
