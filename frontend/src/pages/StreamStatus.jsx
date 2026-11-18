import { useGraphStore } from '../store/graphStore';

export default function StreamStatus() {
  const { streamStatus, metrics } = useGraphStore();
  const { queueDepth, eventsPerSec, workers, gpuUtil, gpuMemory } = streamStatus;

  return (
    <div>
      <h1 style={{fontSize:'1.4rem',fontWeight:800,marginBottom:'1.25rem',color:'#E2E8F0'}}>
        <span style={{color:'#00F0FF'}}>Stream Status</span> — System Health
      </h1>

      {/* Top metrics */}
      <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'1rem',marginBottom:'1.25rem'}}>
        {[
          {l:'Queue Depth',v:queueDepth,max:100,c:'#00F0FF',icon:'📊'},
          {l:'Events/sec',v:eventsPerSec,max:20,c:'#00E676',icon:'⚡'},
          {l:'GPU Utilization',v:`${gpuUtil?.toFixed?gpuUtil.toFixed(1):gpuUtil}%`,max:100,c:'#FFD600',icon:'🎮'},
          {l:'GPU Memory',v:`${gpuMemory?.toFixed?gpuMemory.toFixed(1):gpuMemory} GB`,max:8,c:'#00F0FF',icon:'💾'},
        ].map(m=>(
          <div key={m.l} className="kpi-card">
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:'0.75rem'}}>
              <div>
                <div style={{fontSize:'0.65rem',color:'#64748B',textTransform:'uppercase',letterSpacing:'0.1em'}}>{m.l}</div>
                <div className="font-mono" style={{fontSize:'1.6rem',fontWeight:800,color:m.c,marginTop:'0.3rem'}}>{m.v}</div>
              </div>
              <span style={{fontSize:'1.3rem'}}>{m.icon}</span>
            </div>
            <div style={{height:4,background:'rgba(0,240,255,0.05)',borderRadius:2}}>
              <div style={{height:'100%',width:`${Math.min(100,(typeof m.v==='number'?m.v:parseFloat(m.v))/m.max*100)}%`,background:m.c,borderRadius:2,transition:'width 0.5s'}}/>
            </div>
          </div>
        ))}
      </div>

      {/* Worker health */}
      <div className="glass-card" style={{marginBottom:'1rem'}}>
        <h3 style={{fontSize:'0.75rem',color:'#94A3B8',textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:'1rem'}}>Worker Health — 8 Workers</h3>
        <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:'0.75rem'}}>
          {(workers || []).map((w,i) => (
            <div key={i} style={{padding:'0.75rem',background:'rgba(17,24,39,0.6)',borderRadius:'8px',border:`1px solid ${w.status==='active'?'rgba(0,230,118,0.2)':'rgba(0,240,255,0.05)'}`,transition:'all 0.3s'}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:'0.5rem'}}>
                <span style={{fontSize:'0.75rem',fontWeight:600,color:'#E2E8F0'}}>Worker {w.id}</span>
                <div style={{display:'flex',alignItems:'center',gap:'0.3rem'}}>
                  <div style={{width:8,height:8,borderRadius:'50%',background:w.status==='active'?'#00E676':'#64748B',boxShadow:w.status==='active'?'0 0 8px #00E676':''}}/>
                  <span style={{fontSize:'0.65rem',color:w.status==='active'?'#00E676':'#64748B'}}>{w.status}</span>
                </div>
              </div>
              <div className="font-mono" style={{fontSize:'0.7rem',color:'#94A3B8'}}>
                Processed: <span style={{color:'#00F0FF'}}>{w.processed}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* GPU gauge */}
      <div className="glass-card">
        <h3 style={{fontSize:'0.75rem',color:'#94A3B8',textTransform:'uppercase',letterSpacing:'0.1em',marginBottom:'1rem'}}>GPU Status — RTX 4060</h3>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'1.5rem'}}>
          <div>
            <div style={{fontSize:'0.7rem',color:'#64748B',marginBottom:'0.5rem'}}>Compute Utilization</div>
            <div style={{height:20,background:'rgba(0,240,255,0.05)',borderRadius:10,overflow:'hidden'}}>
              <div style={{height:'100%',width:`${gpuUtil||22}%`,background:'linear-gradient(90deg,#00F0FF44,#00F0FF)',borderRadius:10,transition:'width 0.5s',boxShadow:'0 0 10px rgba(0,240,255,0.3)'}}/>
            </div>
            <div className="font-mono" style={{fontSize:'0.75rem',color:'#00F0FF',marginTop:'0.3rem'}}>{gpuUtil?.toFixed?gpuUtil.toFixed(1):22}%</div>
          </div>
          <div>
            <div style={{fontSize:'0.7rem',color:'#64748B',marginBottom:'0.5rem'}}>VRAM Usage ({gpuMemory?.toFixed?gpuMemory.toFixed(1):1.2}GB / 8GB)</div>
            <div style={{height:20,background:'rgba(0,240,255,0.05)',borderRadius:10,overflow:'hidden'}}>
              <div style={{height:'100%',width:`${((gpuMemory||1.2)/8)*100}%`,background:'linear-gradient(90deg,#00E67644,#00E676)',borderRadius:10,transition:'width 0.5s',boxShadow:'0 0 10px rgba(0,230,118,0.3)'}}/>
            </div>
            <div className="font-mono" style={{fontSize:'0.75rem',color:'#00E676',marginTop:'0.3rem'}}>{((gpuMemory||1.2)/8*100).toFixed(1)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}
