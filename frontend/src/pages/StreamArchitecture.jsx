import React, { useState, useEffect, useRef } from 'react';
import { useGraphStore } from '../store/graphStore';

const SOURCES = [
  { name: 'Kafka Stream', sub: 'Real-time event bus', active: true },
  { name: 'Syslog/SIEM', sub: 'System log aggregator', active: true },
  { name: 'ERP/API Feed', sub: 'Supply chain data', active: true },
  { name: 'Packet Capture', sub: 'Scapy network tap', active: true },
];

export default function StreamArchitecture() {
  const { streamStatus } = useGraphStore();
  const [mockMode, setMockMode] = useState(true);

  // Local mock state
  const [localEps, setLocalEps] = useState(10);
  const [localQueue, setLocalQueue] = useState(450);
  const [workerEvents, setWorkerEvents] = useState([142, 137, 128]);
  const [anomalyFlash, setAnomalyFlash] = useState(null);
  const [riskScore, setRiskScore] = useState(0.34);
  const [outputCounters, setOutputCounters] = useState({ graphUpdates: 48, safeBoxAlerts: 3, lastEvents: [] });

  useEffect(() => {
    if (!mockMode) return;
    const interval = setInterval(() => {
      setLocalEps(Math.floor(Math.random() * 4) + 8);
      setLocalQueue(prev => Math.max(0, prev + Math.floor(Math.random() * 200) - 80));
      setWorkerEvents(prev => prev.map(n => n + Math.floor(Math.random() * 3) + 1));
      setRiskScore(+(Math.random() * 0.8 + 0.1).toFixed(3));
      setOutputCounters(prev => ({
        graphUpdates: prev.graphUpdates + 1,
        safeBoxAlerts: prev.safeBoxAlerts + (Math.random() < 0.08 ? 1 : 0),
        lastEvents: [`Event ${Date.now().toString(36)}`, ...prev.lastEvents].slice(0, 5),
      }));
      if (Math.random() < 0.05) {
        const idx = Math.floor(Math.random() * 3);
        setAnomalyFlash(idx);
        setTimeout(() => setAnomalyFlash(null), 800);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [mockMode]);

  const eps = mockMode ? localEps : (streamStatus.eventsPerSec || 0);
  const queueDepth = mockMode ? localQueue : (streamStatus.queueDepth || 0);
  const queuePct = Math.min((queueDepth / 10000) * 100, 100);
  const queueColor = queuePct > 70 ? '#EF4444' : queuePct > 30 ? '#F59E0B' : '#10B981';
  const riskColor = riskScore >= 0.7 ? '#FF1744' : riskScore >= 0.5 ? '#FF9100' : riskScore >= 0.3 ? '#FFD600' : '#10B981';

  const cardStyle = { background: '#111827', border: '1px solid rgba(0,240,255,0.08)', borderRadius: 12, padding: 20 };
  const headingStyle = { color: '#94A3B8', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#F1F5F9', margin: 0 }}>Stream Architecture</h1>
          <p style={{ fontSize: '0.85rem', color: '#64748B', margin: '4px 0 0' }}>Deduplication, Backpressure, and ML Resilience Pipeline</p>
        </div>
        {/* Addition D: Mock/Live Toggle */}
        <button
          onClick={() => setMockMode(!mockMode)}
          style={{ padding: '6px 16px', borderRadius: 20, border: `1px solid ${mockMode ? '#F59E0B' : '#00F0FF'}`, background: mockMode ? 'rgba(245,158,11,0.1)' : 'rgba(0,240,255,0.1)', color: mockMode ? '#F59E0B' : '#00F0FF', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer', letterSpacing: '0.05em' }}
        >
          {mockMode ? '● MOCK' : '◉ LIVE'}
        </button>
      </div>

      {/* Row 1: Source Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        {SOURCES.map((src, i) => (
          <div key={i} style={{ ...cardStyle, display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: src.active ? '#00F0FF' : '#475569', boxShadow: src.active ? '0 0 10px #00F0FF' : 'none', animation: src.active ? 'pulse 2s infinite' : 'none' }} />
            <div>
              <div style={{ color: '#E2E8F0', fontWeight: 700, fontSize: '0.85rem' }}>{src.name}</div>
              <div style={{ color: '#64748B', fontSize: '0.7rem' }}>{src.sub}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Row 2: Ingestion Layer */}
      <div style={{ ...cardStyle, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={headingStyle}>Stream Ingestion Layer</div>
          <div style={{ color: '#94A3B8', fontSize: '0.8rem' }}>asyncio.Queue → Dedup LRU → Backpressure Gate</div>
        </div>
        <div className="font-mono" style={{ fontSize: '2rem', fontWeight: 800, color: '#00F0FF' }}>{eps} <span style={{ fontSize: '0.7rem', color: '#64748B' }}>events/sec</span></div>
      </div>

      {/* Row 3: Queue Tube */}
      <div style={{ ...cardStyle }}>
        <div style={headingStyle}>asyncio.Queue Buffer</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ flex: 1, height: 28, background: '#0F172A', borderRadius: 14, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)', position: 'relative' }}>
            <div style={{ height: '100%', width: `${queuePct}%`, background: `linear-gradient(90deg, ${queueColor}80, ${queueColor})`, borderRadius: 14, transition: 'width 0.5s ease', position: 'relative' }}>
              {/* Animated blocks */}
              {Array.from({ length: Math.min(Math.floor(queuePct / 5), 15) }).map((_, i) => (
                <div key={i} style={{ position: 'absolute', width: 8, height: 8, background: queueColor, borderRadius: 2, top: 10, left: `${(i / 15) * 90 + 2}%`, opacity: 0.7 + Math.random() * 0.3 }} />
              ))}
            </div>
          </div>
          <div className="font-mono" style={{ fontSize: '0.8rem', color: queueColor, whiteSpace: 'nowrap', fontWeight: 700 }}>
            {queueDepth.toLocaleString()} / 10,000
          </div>
        </div>
      </div>

      {/* Row 4: Workers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {['Worker A', 'Worker B', 'Worker C'].map((name, i) => (
          <div key={i} style={{ ...cardStyle, transition: 'background 0.3s', background: anomalyFlash === i ? 'rgba(255,23,68,0.15)' : '#111827', borderColor: anomalyFlash === i ? 'rgba(255,23,68,0.4)' : 'rgba(0,240,255,0.08)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <span style={{ color: '#E2E8F0', fontWeight: 700, fontSize: '0.85rem' }}>{name}</span>
              <div style={{ width: 16, height: 16, border: '2px solid #00F0FF', borderTop: '2px solid transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
            </div>
            <div className="font-mono" style={{ fontSize: '1.4rem', fontWeight: 800, color: '#00F0FF', marginBottom: 8 }}>Event #{workerEvents[i]}</div>
            <div style={{ color: '#64748B', fontSize: '0.7rem', marginBottom: 8 }}>15 agents firing</div>
            <div style={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
              {Array.from({ length: 15 }).map((_, j) => (
                <div key={j} style={{ width: 6, height: 6, borderRadius: '50%', background: Math.random() > 0.3 ? '#10B981' : '#EF4444' }} />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Row 5: Decision Engine */}
      <div style={{ ...cardStyle, textAlign: 'center', padding: 32 }}>
        <div style={headingStyle}>Decision Engine — Attention MLP</div>
        <div className="font-mono" style={{ fontSize: '3.5rem', fontWeight: 900, color: riskColor, transition: 'color 0.3s' }}>
          {riskScore.toFixed(3)}
        </div>
        <div style={{ fontSize: '0.75rem', color: riskColor, fontWeight: 700, marginTop: 4 }}>
          {riskScore >= 0.7 ? 'CRITICAL' : riskScore >= 0.5 ? 'SUSPICIOUS' : riskScore >= 0.3 ? 'WATCH' : 'NORMAL'}
        </div>
      </div>

      {/* Row 6: Outputs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        <div style={cardStyle}>
          <div style={headingStyle}>Live Graph Updates</div>
          <div className="font-mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: '#00F0FF' }}>{outputCounters.graphUpdates}</div>
          <div style={{ color: '#64748B', fontSize: '0.7rem', marginTop: 4 }}>nodes recolored</div>
        </div>
        <div style={cardStyle}>
          <div style={headingStyle}>Safe Box Alerts</div>
          <div className="font-mono" style={{ fontSize: '1.8rem', fontWeight: 800, color: '#EF4444' }}>{outputCounters.safeBoxAlerts}</div>
          <div style={{ color: '#64748B', fontSize: '0.7rem', marginTop: 4 }}>quarantined</div>
        </div>
        <div style={{ ...cardStyle, overflow: 'hidden' }}>
          <div style={headingStyle}>Live Event Log</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {(outputCounters.lastEvents.length > 0 ? outputCounters.lastEvents : ['Awaiting events...']).map((ev, i) => (
              <div key={i} className="font-mono" style={{ fontSize: '0.7rem', color: i === 0 ? '#00F0FF' : '#475569', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{ev}</div>
            ))}
          </div>
        </div>
      </div>

      {/* CSS Keyframes */}
      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
