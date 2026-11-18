import { useEffect } from 'react';
import { useGraphStore } from '../store/graphStore';

export default function Navbar() {
  const { alerts, dismissAlert, metrics, modelHealth, updateModelHealth, ollamaOnline, setOllamaOnline, mockEnabled, toggleMock } = useGraphStore();
  const latestAlert = alerts[0];

  // Addition B: 30-second Ollama status polling
  useEffect(() => {
    const checkOllama = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/ollama/status');
        const data = await res.json();
        const isOnline = data.status === 'online' || data.available === true;
        updateModelHealth({ llmOnline: isOnline });
        setOllamaOnline(isOnline);
      } catch (e) {
        updateModelHealth({ llmOnline: false });
        setOllamaOnline(false);
      }
    };
    checkOllama();
    const intv = setInterval(checkOllama, 30000);
    return () => clearInterval(intv);
  }, []);

  return (
    <>
      {latestAlert && (
        <div className="alert-slide-in" style={{position:'fixed',top:0,left:'240px',right:0,zIndex:100,background:latestAlert.severity==='critical'?'rgba(255,23,68,0.15)':'rgba(255,145,0,0.12)',borderBottom:`1px solid ${latestAlert.severity==='critical'?'rgba(255,23,68,0.4)':'rgba(255,145,0,0.3)'}`,padding:'0.5rem 1.5rem',display:'flex',alignItems:'center',gap:'0.75rem',backdropFilter:'blur(10px)'}}>
          <span style={{fontSize:'1rem'}}>{latestAlert.severity==='critical'?'🚨':'⚠️'}</span>
          <span className="font-mono" style={{fontSize:'0.8rem',color:latestAlert.severity==='critical'?'#FF1744':'#FF9100',flex:1}}>{latestAlert.message}</span>
          <span className="font-mono" style={{fontSize:'0.65rem',color:'#64748B'}}>{new Date(latestAlert.timestamp).toLocaleTimeString()}</span>
          <button onClick={()=>dismissAlert(latestAlert.id)} style={{background:'none',border:'none',color:'#64748B',cursor:'pointer',fontSize:'1rem'}}>×</button>
        </div>
      )}
      <header style={{height:'48px',background:'rgba(13,17,23,0.9)',borderBottom:'1px solid rgba(0,240,255,0.08)',display:'flex',alignItems:'center',justifyContent:'flex-end',padding:'0 1.5rem',backdropFilter:'blur(10px)',gap:'1.5rem',position:'sticky',top:0,zIndex:40}}>
        <div className="font-mono" style={{display:'flex',gap:'1.5rem',fontSize:'0.72rem',color:'#94A3B8',alignItems:'center'}}>
          {/* Mock Toggle Button */}
          <button onClick={toggleMock} style={{padding: '3px 10px', borderRadius: 20, background: mockEnabled ? 'rgba(239,68,68,0.15)' : '#1E293B', border: `1px solid ${mockEnabled ? 'rgba(239,68,68,0.4)' : 'rgba(255,255,255,0.1)'}`, color: mockEnabled ? '#EF4444' : '#94A3B8', cursor: 'pointer', fontWeight: 600, fontSize: '0.68rem', display: 'flex', alignItems: 'center', gap: '5px'}}>
            <div style={{width: 6, height: 6, borderRadius: '50%', background: mockEnabled ? '#EF4444' : '#64748B'}} />
            MOCK DATA {mockEnabled ? 'ON' : 'OFF'}
          </button>
          
          {/* Ollama LLM Status Pill (Addition B) */}
          <div
            title="Local Ollama — llama3 — localhost:11434"
            style={{display:'flex',alignItems:'center',gap:'0.4rem',cursor:'default',padding:'3px 10px',borderRadius:20,background: ollamaOnline ? 'rgba(0,230,118,0.08)' : 'rgba(239,68,68,0.08)',border: `1px solid ${ollamaOnline ? 'rgba(0,230,118,0.25)' : 'rgba(239,68,68,0.25)'}`}}
          >
            <div className={ollamaOnline ? 'pulse-green' : ''} style={{width:7,height:7,borderRadius:'50%',background: ollamaOnline ? '#00E676' : '#F59E0B',boxShadow: ollamaOnline ? '0 0 8px #00E676' : '0 0 6px #F59E0B'}} />
            <span style={{letterSpacing:'0.8px',color: ollamaOnline ? '#00E676' : '#F59E0B',fontWeight:600,fontSize:'0.68rem'}}>LLM {ollamaOnline ? 'Online' : 'Offline'}</span>
          </div>
          <span>NODES: <b style={{color:'#00F0FF'}}>{metrics.totalNodes}</b></span>
          <span>EVENTS/s: <b style={{color:'#00E676'}}>{metrics.eventsPerSec}</b></span>
          <span>AVG RISK: <b style={{color:metrics.avgRisk>0.5?'#FF1744':metrics.avgRisk>0.3?'#FFD600':'#00E676'}}>{(metrics.avgRisk*100).toFixed(1)}%</b></span>
          <span>GPU: <b style={{color:'#00F0FF'}}>{metrics.gpuUtilization?.toFixed?metrics.gpuUtilization.toFixed(0):metrics.gpuUtilization}%</b></span>
        </div>
      </header>
    </>
  );
}
