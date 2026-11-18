import React, { useState, useEffect, useRef } from 'react';
import { useGraphStore } from '../store/graphStore';

const TIER_STYLES = {
  CRITICAL:   { bg: 'rgba(239,68,68,0.15)', color: '#EF4444', border: 'rgba(239,68,68,0.4)' },
  SUSPICIOUS: { bg: 'rgba(255,145,0,0.15)', color: '#FF9100', border: 'rgba(255,145,0,0.4)' },
  WATCH:      { bg: 'rgba(245,158,11,0.15)', color: '#F59E0B', border: 'rgba(245,158,11,0.4)' },
  NORMAL:     { bg: 'rgba(16,185,129,0.15)', color: '#10B981', border: 'rgba(16,185,129,0.4)' },
};

const DEMO_ATTACKS = [
  { id: 'port_scan',     label: 'Nmap Port Scan',      color: '#F59E0B' },
  { id: 'brute_force',   label: 'SSH Brute Force',     color: '#F59E0B' },
  { id: 'ddos',          label: 'SYN Flood DDoS',      color: '#F59E0B' },
  { id: 'lateral_move',  label: 'Lateral Movement',    color: '#FF9100' },
  { id: 'c2_beacon',     label: 'C2 Beaconing',        color: '#EF4444' },
  { id: 'sql_injection', label: 'SQLi / XSS',          color: '#06B6D4' },
  { id: 'ransomware',    label: 'WannaCry Simulate',   color: '#EF4444' },
  { id: 'priv_esc',      label: 'Priv. Escalation',    color: '#06B6D4' },
  { id: 'mitm',          label: 'ARP Spoof MITM',      color: '#FF9100' },
];

export default function LiveThreatMonitor() {
  const { threatEvents, addThreatEvent, clearThreatEvents, captureActive, captureTargetIp, packetsPerSec, setCaptureStatus } = useGraphStore();
  const [targetIp, setTargetIp] = useState(captureTargetIp || '');
  const [iface, setIface] = useState('eth0');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [report, setReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [loadingAttack, setLoadingAttack] = useState(null);
  const [filter, setFilter] = useState('all');
  const feedRef = useRef(null);

  // Poll capture status
  useEffect(() => {
    if (!captureActive) return;
    const intv = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/api/capture/status');
        const data = await res.json();
        setCaptureStatus({ packetsPerSec: data.stream_stats?.eventsPerSec || 0 });
      } catch {}
    }, 1000);
    return () => clearInterval(intv);
  }, [captureActive]);

  const startCapture = async () => {
    if (!targetIp) return alert('Enter a Target IP');
    // Clear old events so the feed starts fresh for the demo
    clearThreatEvents();
    try {
      await fetch('http://localhost:8000/api/capture/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interface: iface, target_ip: targetIp }),
      });
      setCaptureStatus({ captureActive: true, captureTargetIp: targetIp });
    } catch (e) { console.error(e); }
  };

  const stopCapture = async () => {
    try {
      await fetch('http://localhost:8000/api/capture/stop', { method: 'POST' });
      setCaptureStatus({ captureActive: false, packetsPerSec: 0 });
    } catch (e) { console.error(e); }
  };

  const fireDemo = async (attackType) => {
    setLoadingAttack(attackType);
    try {
      const res = await fetch(`http://localhost:8000/api/demo/attack/${attackType}`, { method: 'POST' });
      const data = await res.json();
      const d = data.decision || {};
      addThreatEvent({
        timestamp: new Date().toISOString(),
        source_ip: data.swarm_result?.node_id || '10.0.0.99',
        dest_ip: d.node_id || '192.168.1.10',
        attack_type: attackType,
        risk_score: d.risk_score || 0.85,
        tier: d.tier || 'CRITICAL',
        fired_agents: (d.top_agents || []).map(a => a.agent),
      });
    } catch (e) { console.error(e); }
    setLoadingAttack(null);
  };

  const openDrawer = async (event) => {
    setSelectedEvent(event);
    setDrawerOpen(true);
    setLoadingReport(true);
    setReport(null);
    try {
      const res = await fetch(`http://localhost:8000/api/remediation/${event.attack_type}?attacker_ip=${event.source_ip}`);
      const data = await res.json();
      setReport(data);
    } catch { setReport({ explanation: 'Failed to fetch remediation report.', immediate: [], hardening: [], attack_type: event.attack_type, risk_score: event.risk_score }); }
    setLoadingReport(false);
  };

  const filteredEvents = filter === 'all' ? threatEvents : threatEvents.filter(e => e.attack_type === filter);

  const cardStyle = { background: '#111827', border: '1px solid rgba(0,240,255,0.08)', borderRadius: 12, padding: 20 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 1400, margin: '0 auto', position: 'relative' }}>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#F1F5F9', margin: 0 }}>Live Threat Monitor</h1>

      {/* Section 1: IP Setup (Addition C1) */}
      <div style={{ ...cardStyle, display: 'flex', alignItems: 'flex-end', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 200 }}>
          <label style={{ display: 'block', fontSize: '0.7rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>Network Interface</label>
          <select value={iface} onChange={e => setIface(e.target.value)} disabled={captureActive}
            style={{ width: '100%', padding: '8px 12px', borderRadius: 8, background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', color: '#E2E8F0', fontSize: '0.85rem', outline: 'none' }}>
            <option value="eth0">eth0</option>
            <option value="wlan0">wlan0</option>
            <option value="lo">lo (Loopback)</option>
            <option value="Ethernet">Ethernet (Win)</option>
          </select>
        </div>
        <div style={{ flex: 2, minWidth: 250 }}>
          <label style={{ display: 'block', fontSize: '0.7rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>Target IPv4 Address</label>
          <input type="text" value={targetIp} onChange={e => setTargetIp(e.target.value)} disabled={captureActive} placeholder="e.g. 192.168.1.100"
            style={{ width: '100%', padding: '8px 12px', borderRadius: 8, background: '#0F172A', border: '1px solid rgba(255,255,255,0.1)', color: '#E2E8F0', fontSize: '0.85rem', fontFamily: 'monospace', outline: 'none' }} />
        </div>
        {!captureActive ? (
          <button onClick={startCapture} style={{ padding: '8px 24px', borderRadius: 8, background: '#06B6D4', color: '#fff', fontWeight: 700, fontSize: '0.85rem', border: 'none', cursor: 'pointer' }}>▶ Start Monitoring</button>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 20, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)' }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#10B981', animation: 'pulse 2s infinite' }} />
              <span className="font-mono" style={{ color: '#10B981', fontSize: '0.75rem', fontWeight: 600 }}>Watching {captureTargetIp}</span>
              <span className="font-mono" style={{ color: '#64748B', fontSize: '0.7rem' }}>| {packetsPerSec} pkt/s</span>
            </div>
            <button onClick={stopCapture} style={{ padding: '8px 16px', borderRadius: 8, background: '#EF4444', color: '#fff', fontWeight: 700, fontSize: '0.8rem', border: 'none', cursor: 'pointer' }}>■ Stop</button>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: 24, flex: 1 }}>
        {/* Left: Feed + Demo */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Section 2: Live Feed */}
          <div style={{ ...cardStyle, flex: 1, maxHeight: 420, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <span style={{ color: '#94A3B8', fontWeight: 700, fontSize: '0.8rem' }}>LIVE ATTACK FEED</span>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <button onClick={() => setFilter('all')} style={{ padding: '2px 8px', borderRadius: 10, background: filter === 'all' ? '#00F0FF20' : '#1E293B', color: filter === 'all' ? '#00F0FF' : '#64748B', border: '1px solid transparent', fontSize: '0.65rem', cursor: 'pointer', fontWeight: 600 }}>All</button>
                {['ddos', 'port_scan', 'brute_force', 'ransomware', 'sql_injection'].map(t => (
                  <button key={t} onClick={() => setFilter(t)} style={{ padding: '2px 8px', borderRadius: 10, background: filter === t ? '#00F0FF20' : '#1E293B', color: filter === t ? '#00F0FF' : '#64748B', border: '1px solid transparent', fontSize: '0.65rem', cursor: 'pointer', fontWeight: 600 }}>{t.replace('_', ' ')}</button>
                ))}
              </div>
            </div>
            <div ref={feedRef} style={{ flex: 1, overflow: 'auto' }}>
              {filteredEvents.length === 0 && (
                <div style={{ textAlign: 'center', padding: 40, color: '#475569', fontSize: '0.8rem' }}>Awaiting threat telemetry...</div>
              )}
              {filteredEvents.map((ev, i) => {
                const tier = TIER_STYLES[ev.tier] || TIER_STYLES.NORMAL;
                return (
                  <div key={i} onClick={() => openDrawer(ev)}
                    style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 12px', borderRadius: 8, marginBottom: 4, cursor: 'pointer', background: i === 0 ? 'rgba(255,215,0,0.04)' : 'transparent', transition: 'background 0.2s' }}
                    onMouseEnter={e => e.currentTarget.style.background = '#1E293B'}
                    onMouseLeave={e => e.currentTarget.style.background = i === 0 ? 'rgba(255,215,0,0.04)' : 'transparent'}>
                    <span className="font-mono" style={{ color: '#475569', fontSize: '0.65rem', width: 70, flexShrink: 0 }}>{new Date(ev.timestamp).toLocaleTimeString()}</span>
                    <span className="font-mono" style={{ color: '#94A3B8', fontSize: '0.75rem', width: 110 }}>{ev.source_ip}</span>
                    <span style={{ padding: '1px 8px', borderRadius: 10, background: tier.bg, color: tier.color, border: `1px solid ${tier.border}`, fontSize: '0.6rem', fontWeight: 700, flexShrink: 0 }}>{ev.tier}</span>
                    <span style={{ color: '#CBD5E1', fontSize: '0.75rem', flex: 1 }}>{(ev.attack_type || '').replace(/_/g, ' ')}</span>
                    <span className="font-mono" style={{ color: (ev.risk_score || 0) > 0.7 ? '#EF4444' : '#F59E0B', fontSize: '0.75rem', fontWeight: 700 }}>{(ev.risk_score || 0).toFixed(2)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 4: Demo Attack Buttons (Addition C3) */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
              <span style={{ color: '#94A3B8', fontWeight: 700, fontSize: '0.8rem' }}>THESIS DEMO — INJECT ATTACKS</span>
              <span style={{ color: '#475569', fontSize: '0.65rem' }}>No secondary machine required</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              {DEMO_ATTACKS.map(atk => (
                <button key={atk.id} onClick={() => fireDemo(atk.id)} disabled={loadingAttack !== null}
                  style={{ padding: '10px 14px', borderRadius: 8, background: loadingAttack === atk.id ? '#1E293B' : '#0F172A', border: `1px solid ${atk.color}30`, color: atk.color, fontWeight: 700, fontSize: '0.78rem', cursor: loadingAttack ? 'not-allowed' : 'pointer', textAlign: 'left', transition: 'all 0.2s', opacity: loadingAttack && loadingAttack !== atk.id ? 0.5 : 1 }}>
                  {loadingAttack === atk.id ? '⏳ Processing...' : atk.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Stats placeholder when drawer closed */}
        {!drawerOpen && (
          <div style={{ width: 350, ...cardStyle, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#475569' }}>
            <div style={{ fontSize: '3rem', marginBottom: 12, opacity: 0.3 }}>🛡️</div>
            <div style={{ fontSize: '0.85rem', textAlign: 'center' }}>Click any event in the feed to view the Ollama remediation report</div>
          </div>
        )}
      </div>

      {/* Section 3: Remediation Drawer (Addition C2) */}
      {drawerOpen && (
        <div style={{ position: 'fixed', top: 0, right: 0, width: 500, height: '100vh', background: '#1E1E2E', borderLeft: '1px solid rgba(0,240,255,0.1)', zIndex: 200, overflowY: 'auto', boxShadow: '-4px 0 30px rgba(0,0,0,0.5)', padding: 28, display: 'flex', flexDirection: 'column' }}>
          <button onClick={() => { setDrawerOpen(false); setSelectedEvent(null); setReport(null); }}
            style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', color: '#64748B', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>

          {selectedEvent && (
            <>
              <div style={{ marginBottom: 20 }}>
                <div style={{ ...(() => { const t = TIER_STYLES[selectedEvent.tier] || TIER_STYLES.NORMAL; return { display: 'inline-block', padding: '3px 12px', borderRadius: 16, background: t.bg, color: t.color, border: `1px solid ${t.border}`, fontSize: '0.7rem', fontWeight: 700, marginBottom: 10 }; })() }}>{selectedEvent.tier}</div>
                <h2 style={{ color: '#F1F5F9', fontSize: '1.4rem', fontWeight: 800, margin: '4px 0', textTransform: 'uppercase' }}>{(selectedEvent.attack_type || '').replace(/_/g, ' ')}</h2>
                <p className="font-mono" style={{ color: '#94A3B8', fontSize: '0.8rem' }}>Source: <span style={{ color: '#00F0FF' }}>{selectedEvent.source_ip}</span></p>
                <p className="font-mono" style={{ color: '#94A3B8', fontSize: '0.8rem', marginTop: 4 }}>Risk: <span style={{ color: '#EF4444', fontWeight: 700 }}>{(selectedEvent.risk_score || 0).toFixed(3)}</span></p>
              </div>

              {loadingReport ? (
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 28, height: 28, border: '3px solid #00F0FF', borderTop: '3px solid transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                    <span style={{ color: '#64748B', fontSize: '0.8rem' }}>Querying Ollama llama3...</span>
                  </div>
                </div>
              ) : report && (
                <>
                  {/* Ollama Explanation */}
                  <div style={{ background: 'rgba(59,130,246,0.06)', borderLeft: '3px solid #3B82F6', padding: 16, borderRadius: '0 8px 8px 0', marginBottom: 20 }}>
                    <div style={{ color: '#60A5FA', fontWeight: 700, fontSize: '0.8rem', marginBottom: 8 }}>Llama 3 Analysis</div>
                    <p style={{ color: '#CBD5E1', fontSize: '0.82rem', lineHeight: 1.6, margin: 0 }}>{report.explanation}</p>
                    {report.shap_summary && (
                      <div className="font-mono" style={{ color: '#475569', fontSize: '0.65rem', marginTop: 10 }}>SHAP: {report.shap_summary}</div>
                    )}
                  </div>

                  {/* Fired Agents */}
                  {selectedEvent.fired_agents && selectedEvent.fired_agents.length > 0 && (
                    <div style={{ marginBottom: 20 }}>
                      <div style={{ color: '#94A3B8', fontWeight: 700, fontSize: '0.75rem', marginBottom: 8, textTransform: 'uppercase' }}>Agents Fired</div>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {selectedEvent.fired_agents.map((a, i) => (
                          <span key={i} style={{ padding: '3px 10px', borderRadius: 12, background: 'rgba(239,68,68,0.12)', color: '#EF4444', fontSize: '0.7rem', fontWeight: 600, border: '1px solid rgba(239,68,68,0.25)' }}>{a}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Immediate Commands */}
                  <div style={{ color: '#94A3B8', fontWeight: 700, fontSize: '0.75rem', marginBottom: 8, textTransform: 'uppercase' }}>🔧 Immediate Remediation</div>
                  {(report.immediate || []).map((cmd, i) => {
                    const filled = cmd.replace(/\{attacker_ip\}/g, selectedEvent.source_ip || '10.0.0.99');
                    return (
                      <div key={i} style={{ background: '#0F172A', borderRadius: 8, padding: 12, marginBottom: 8, position: 'relative', fontFamily: 'monospace', fontSize: '0.78rem', color: '#10B981' }}>
                        <span>{filled}</span>
                        <button onClick={() => navigator.clipboard.writeText(filled)}
                          style={{ position: 'absolute', top: 8, right: 8, padding: '2px 8px', borderRadius: 4, background: '#1E293B', border: '1px solid rgba(255,255,255,0.1)', color: '#94A3B8', fontSize: '0.65rem', cursor: 'pointer' }}>Copy</button>
                      </div>
                    );
                  })}

                  {/* Hardening */}
                  {report.hardening && report.hardening.length > 0 && (
                    <div style={{ marginTop: 16 }}>
                      <div style={{ color: '#94A3B8', fontWeight: 700, fontSize: '0.75rem', marginBottom: 8, textTransform: 'uppercase' }}>🛡️ Post-Incident Hardening</div>
                      {report.hardening.map((h, i) => (
                        <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', padding: '8px 12px', borderRadius: 8, background: '#0F172A', marginBottom: 6 }}>
                          <span style={{ width: 20, height: 20, borderRadius: '50%', background: 'rgba(16,185,129,0.1)', color: '#10B981', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 700, flexShrink: 0 }}>{i + 1}</span>
                          <span style={{ color: '#CBD5E1', fontSize: '0.8rem' }}>{h}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      )}

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
