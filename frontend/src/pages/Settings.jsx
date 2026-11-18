import { useState } from 'react';
import { Save, Check, Key, Server, Globe } from 'lucide-react';

const AGENTS = [
  { name: 'Signature Agent', type: 'CPU', desc: 'Regex pattern matching for known attack signatures' },
  { name: 'Spike Agent', type: 'CPU', desc: 'Z-score anomaly detection on traffic spikes' },
  { name: 'Behavior Agent', type: 'CPU', desc: 'IsolationForest behavioral deviation detection' },
  { name: 'Port Scan Agent', type: 'CPU', desc: 'Network reconnaissance detection' },
  { name: 'DDoS Agent', type: 'CPU', desc: 'Flood detection via in-degree analysis' },
  { name: 'SQLi/XSS Agent', type: 'CPU', desc: 'Injection attack detection with entropy scoring' },
  { name: 'Brute Force Agent', type: 'CPU', desc: 'Credential stuffing with exponential decay' },
  { name: 'Lateral Movement', type: 'CPU', desc: 'BFS from flagged nodes for spread detection' },
  { name: 'Exfiltration Agent', type: 'CPU', desc: 'Outbound/inbound byte ratio analysis' },
  { name: 'Ransomware Agent', type: 'CPU', desc: 'Cascading file_lock event detection' },
  { name: 'MITM Agent', type: 'CPU', desc: 'Path comparison vs shortest path routing' },
  { name: 'Supply Inject', type: 'CPU', desc: 'Supply chain edge injection detection' },
  { name: 'Priv Escalation', type: 'CPU', desc: 'RBAC baseline privilege violation' },
  { name: 'C2/Beacon Agent', type: 'CPU', desc: 'FFT periodicity on event timestamps' },
  { name: 'Graph GCN Agent', type: 'GPU', desc: 'GraphSAGE structural anomaly detection' },
  { name: 'Zero-Day Agent', type: 'GPU', desc: 'Cosine distance in embedding space' },
  { name: 'Temporal/APT', type: 'GPU', desc: '7-day graph signature similarity for APT' },
];

export default function Settings() {
  const [agentStates, setAgentStates] = useState(Object.fromEntries(AGENTS.map(a => [a.name, true])));
  const [apiKey1, setApiKey1] = useState('AIzaSy***********UWUDc');
  const [apiKey2, setApiKey2] = useState('AIzaSy***********A98KU');
  const [saved, setSaved] = useState(false);

  const toggleAgent = (name) => {
    setAgentStates(prev => ({ ...prev, [name]: !prev[name] }));
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const enabledCount = Object.values(agentStates).filter(Boolean).length;

  return (
    <div className="fade-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: '1.7rem', fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>Settings</h1>
          <p style={{ fontSize: '0.85rem', color: '#64748B', marginTop: 4 }}>Configure agents & API keys</p>
        </div>
        <button className={`btn-primary ${saved ? 'save-success' : ''}`} onClick={handleSave}
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {saved ? <><Check size={16} /> Saved!</> : <><Save size={16} /> Save Changes</>}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20 }}>
        {/* Agent Toggles */}
        <div className="glass" style={{ padding: 28 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#E2E8F0' }}>AI Agent Configuration</h3>
            <span className="font-mono" style={{ fontSize: '0.72rem', color: '#06B6D4' }}>{enabledCount}/17 active</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {AGENTS.map(a => (
              <div key={a.name} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 16px', borderRadius: 10,
                background: agentStates[a.name] ? 'rgba(6,182,212,0.03)' : 'transparent',
                transition: 'background 0.2s',
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: agentStates[a.name] ? '#E2E8F0' : '#64748B' }}>{a.name}</span>
                    <span style={{
                      padding: '1px 6px', borderRadius: 4, fontSize: '0.58rem', fontWeight: 700,
                      background: a.type === 'GPU' ? 'rgba(6,182,212,0.1)' : 'rgba(148,163,184,0.08)',
                      color: a.type === 'GPU' ? '#06B6D4' : '#94A3B8',
                      border: `1px solid ${a.type === 'GPU' ? 'rgba(6,182,212,0.2)' : 'rgba(148,163,184,0.1)'}`,
                    }}>{a.type}</span>
                  </div>
                  <span style={{ fontSize: '0.72rem', color: '#64748B' }}>{a.desc}</span>
                </div>
                <button className={`toggle ${agentStates[a.name] ? 'active' : ''}`} onClick={() => toggleAgent(a.name)} />
              </div>
            ))}
          </div>
        </div>

        {/* API Configuration */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="glass" style={{ padding: 28 }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#E2E8F0', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Key size={16} color="#06B6D4" /> API Keys
            </h3>
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 500, display: 'block', marginBottom: 6 }}>Gemini API Key 1</label>
              <input type="password" value={apiKey1} onChange={e => setApiKey1(e.target.value)} style={{
                width: '100%', padding: '10px 14px', borderRadius: 10,
                background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border)',
                color: '#E2E8F0', fontSize: '0.82rem', fontFamily: '"JetBrains Mono", monospace',
                outline: 'none', transition: 'border-color 0.2s',
              }} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 500, display: 'block', marginBottom: 6 }}>Gemini API Key 2 (Rotation)</label>
              <input type="password" value={apiKey2} onChange={e => setApiKey2(e.target.value)} style={{
                width: '100%', padding: '10px 14px', borderRadius: 10,
                background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border)',
                color: '#E2E8F0', fontSize: '0.82rem', fontFamily: '"JetBrains Mono", monospace',
                outline: 'none', transition: 'border-color 0.2s',
              }} />
            </div>
          </div>

          <div className="glass" style={{ padding: 28 }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#E2E8F0', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Server size={16} color="#06B6D4" /> Server
            </h3>
            {[
              { l: 'Backend', v: 'http://localhost:8000', s: true },
              { l: 'Frontend', v: 'http://localhost:5173', s: true },
              { l: 'Database', v: 'SQLite (WAL mode)', s: true },
              { l: 'WebSocket', v: 'ws://localhost:8000/ws', s: true },
            ].map(item => (
              <div key={item.l} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontSize: '0.82rem', color: '#94A3B8' }}>{item.l}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: item.s ? '#10B981' : '#EF4444' }} />
                  <span className="font-mono" style={{ fontSize: '0.72rem', color: '#64748B' }}>{item.v}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="glass" style={{ padding: 28 }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#E2E8F0', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Globe size={16} color="#06B6D4" /> Model Config
            </h3>
            {[
              { l: 'LLM Model', v: 'gemini-2.0-flash' },
              { l: 'GCN Layers', v: '2 (64 → 32)' },
              { l: 'Meta Classifier', v: 'MLP [64 → 32 → 1]' },
              { l: 'Quarantine Threshold', v: '70%' },
            ].map(item => (
              <div key={item.l} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontSize: '0.82rem', color: '#94A3B8' }}>{item.l}</span>
                <span className="font-mono" style={{ fontSize: '0.72rem', color: '#06B6D4' }}>{item.v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
