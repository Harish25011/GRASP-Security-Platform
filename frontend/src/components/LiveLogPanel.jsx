import { useGraphStore } from '../store/graphStore';

const TIER_STYLES = {
  CRITICAL:   { bg: 'rgba(127,29,29,0.4)', color: '#FCA5A5', border: '1px solid rgba(239,68,68,0.5)' },
  SUSPICIOUS: { bg: 'rgba(124,45,18,0.4)', color: '#FDBA74', border: '1px solid rgba(255,145,0,0.5)' },
  WATCH:      { bg: 'rgba(113,63,18,0.4)', color: '#FDE68A', border: '1px solid rgba(245,158,11,0.5)' },
  NORMAL:     { bg: 'rgba(6,78,59,0.4)',   color: '#A7F3D0', border: '1px solid rgba(16,185,129,0.5)' },
};

export default function LiveLogPanel({ maxItems = 30 }) {
  const { eventLog } = useGraphStore();
  const events = eventLog.slice(0, maxItems);

  return (
    <div style={{fontFamily:'"JetBrains Mono",monospace',fontSize:'0.7rem',maxHeight:'400px',overflowY:'auto',padding:'0.5rem'}}>
      {events.length === 0 ? (
        <div style={{color:'#64748B',textAlign:'center',padding:'2rem'}}>Waiting for events...</div>
      ) : events.map((e, i) => {
        const tier = e.tier || (e.label && e.label !== 'benign' ? 'SUSPICIOUS' : 'NORMAL');
        const style = TIER_STYLES[tier] || TIER_STYLES.NORMAL;
        return (
          <div key={e.id || i} style={{padding:'0.35rem 0.5rem',borderBottom:'1px solid rgba(0,240,255,0.04)',display:'flex',gap:'0.75rem',alignItems:'center',background: tier !== 'NORMAL' ? 'rgba(255,23,68,0.04)':'transparent',animation:i===0?'fadeIn 0.3s ease':''}}>
            <span style={{color:'#64748B',minWidth:'70px'}}>{new Date(e.timestamp).toLocaleTimeString()}</span>
            {/* 4-Tier Badge */}
            <span style={{padding:'1px 8px',borderRadius:10,background:style.bg,color:style.color,border:style.border,fontSize:'0.55rem',fontWeight:700,minWidth:60,textAlign:'center'}}>{tier}</span>
            <span style={{color:'#94A3B8',minWidth:'100px'}}>{e.source_ip}</span>
            <span style={{color:'#64748B'}}>→</span>
            <span style={{color:'#94A3B8',minWidth:'100px'}}>{e.dest_ip}</span>
            <span style={{color:'#64748B',minWidth:'40px'}}>{e.protocol}</span>
            <span style={{color: tier !== 'NORMAL' ? '#FF9100':'#64748B',flex:1}}>{e.event_type}</span>
          </div>
        );
      })}
      <style>{`@keyframes fadeIn{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}`}</style>
    </div>
  );
}
