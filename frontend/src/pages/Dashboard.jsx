import { useState, useCallback } from 'react';
import { useGraphStore } from '../store/graphStore';
import { NavLink } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area,
} from 'recharts';
import { ShieldAlert, Activity, Bell, Cpu, Zap, Target } from 'lucide-react';

const AGENT_NAMES = [
  'Signature','Spike','Behavior','Port Scan','DDoS','SQLi/XSS','Brute Force',
  'Lateral Move','Exfiltration','Ransomware','MITM','Supply Inject',
  'Priv Escalation','C2/Beacon','Graph GCN','Zero-Day','Temporal/APT',
];

const PIE_COLORS = ['#06B6D4','#3B82F6','#6366F1','#8B5CF6','#EC4899','#EF4444','#F59E0B'];

export default function Dashboard() {
  const { metrics, riskTimeline, anomalies, safeBoxCount, agentScores, modelHealth, addAnomaly, addAlert, addToSafeBox, updateAgentScores, addRiskPoint, addEvent } = useGraphStore();
  const [simulating, setSimulating] = useState(false);

  const handleSimulate = useCallback(() => {
    setSimulating(true);
    const nodeId = `192.168.1.${10 + Math.floor(Math.random() * 30)}`;
    const attackType = ['DDoS','SQL Injection','Port Scan','Ransomware','Zero-Day','Brute Force','APT'][Math.floor(Math.random() * 7)];
    const risk = 0.6 + Math.random() * 0.4;

    const scores = {};
    AGENT_NAMES.forEach(a => { scores[a] = Math.random() * 0.4; });
    const trigger = AGENT_NAMES[Math.floor(Math.random() * AGENT_NAMES.length)];
    scores[trigger] = 0.75 + Math.random() * 0.25;
    scores[AGENT_NAMES[Math.floor(Math.random() * AGENT_NAMES.length)]] = 0.5 + Math.random() * 0.4;
    updateAgentScores(scores);

    addAnomaly({ node_id: nodeId, risk_score: risk, severity: risk > 0.7 ? 'critical' : 'high', attack_type: attackType, scores });
    addAlert({ type: 'anomaly', message: `🚨 ${attackType} detected on ${nodeId}`, severity: 'critical', node_id: nodeId });
    addToSafeBox({ node_id: nodeId, risk_score: risk, reason: `Attack: ${attackType}`, agent_scores: scores });
    addRiskPoint({ time: new Date().toLocaleTimeString(), risk, events: 1 });
    addEvent({ source_ip: `10.0.0.${Math.floor(Math.random()*20)}`, dest_ip: nodeId, protocol: 'TCP', event_type: attackType, risk_score: risk, label: attackType });

    setTimeout(() => setSimulating(false), 800);
  }, []);

  // Attack distribution for pie
  const attackTypes = {};
  anomalies.forEach(a => { attackTypes[a.attack_type || 'Unknown'] = (attackTypes[a.attack_type || 'Unknown'] || 0) + 1; });
  const pieData = Object.entries(attackTypes).slice(0, 7).map(([name, value]) => ({ name, value }));
  if (pieData.length === 0) pieData.push({ name: 'No Data', value: 1 });

  // Risk score
  const avgRisk = metrics.avgRisk || 0;
  const riskPct = Math.round(avgRisk * 100);
  const riskColor = avgRisk > 0.6 ? '#EF4444' : avgRisk > 0.35 ? '#F59E0B' : '#10B981';

  const kpis = [
    { label: 'Threats Blocked', value: anomalies.length, icon: ShieldAlert, color: '#EF4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.15)' },
    { label: 'Live Traffic', value: `${metrics.eventsPerSec || 0}/s`, icon: Activity, color: '#10B981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.15)' },
    { label: 'Active Alerts', value: anomalies.filter(a => a.severity === 'critical').length, icon: Bell, color: '#F59E0B', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.15)' },
    { label: 'AI Agents Running', value: 17, icon: Cpu, color: '#06B6D4', bg: 'rgba(6,182,212,0.08)', border: 'rgba(6,182,212,0.15)' },
  ];

  return (
    <div className="fade-up">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: '1.7rem', fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>Dashboard</h1>
          <p style={{ fontSize: '0.85rem', color: '#64748B', marginTop: 4 }}>Real-time security monitoring & analytics</p>
        </div>
        <button className={`btn-primary ${simulating ? 'save-success' : ''}`} onClick={handleSimulate} disabled={simulating}
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Zap size={16} />
          {simulating ? 'Simulating...' : 'Simulate Attack'}
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {kpis.map(k => {
          const Icon = k.icon;
          return (
            <div key={k.label} className="kpi">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <p style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 500, marginBottom: 8 }}>{k.label}</p>
                  <p className="font-mono" style={{ fontSize: '2rem', fontWeight: 800, color: '#F1F5F9', lineHeight: 1 }}>{k.value}</p>
                </div>
                <div className="kpi-icon" style={{ background: k.bg, border: `1px solid ${k.border}` }}>
                  <Icon size={20} color={k.color} strokeWidth={2} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        {/* Line Chart */}
        <div className="glass" style={{ padding: 24 }}>
          <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94A3B8', marginBottom: 20 }}>Network Traffic — Live</h3>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={riskTimeline}>
              <defs>
                <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06B6D4" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.06)" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748B' }} axisLine={{ stroke: 'rgba(148,163,184,0.08)' }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 10, fill: '#64748B' }} axisLine={{ stroke: 'rgba(148,163,184,0.08)' }} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(6,182,212,0.2)', borderRadius: 10, fontSize: '0.78rem' }} />
              <Area type="monotone" dataKey="risk" stroke="#06B6D4" fill="url(#grad1)" strokeWidth={2} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart */}
        <div className="glass" style={{ padding: 24 }}>
          <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94A3B8', marginBottom: 20 }}>Attack Distribution</h3>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value" stroke="none">
                {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(6,182,212,0.2)', borderRadius: 10, fontSize: '0.78rem' }} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 14px', justifyContent: 'center', marginTop: 8 }}>
            {pieData.map((d, i) => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <div style={{ width: 8, height: 8, borderRadius: 2, background: PIE_COLORS[i % PIE_COLORS.length] }} />
                <span style={{ fontSize: '0.68rem', color: '#94A3B8' }}>{d.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row: Risk Score + Agent Network */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16 }}>
        {/* Risk Score Widget */}
        <div className="glass" style={{ padding: 32, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94A3B8', marginBottom: 24 }}>System Risk Score</h3>
          <div className="risk-ring" style={{
            width: 140, height: 140, borderRadius: '50%',
            background: `conic-gradient(${riskColor} ${riskPct * 3.6}deg, rgba(30,41,59,0.5) 0deg)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{
              width: 110, height: 110, borderRadius: '50%', background: '#0B0F19',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            }}>
              <span className="font-mono" style={{ fontSize: '2.2rem', fontWeight: 800, color: riskColor }}>{riskPct}</span>
              <span style={{ fontSize: '0.65rem', color: '#64748B', marginTop: 2 }}>RISK %</span>
            </div>
          </div>
          <div style={{ marginTop: 16, display: 'flex', gap: 20, fontSize: '0.72rem' }}>
            {[{ l: 'Low', c: '#10B981' }, { l: 'Medium', c: '#F59E0B' }, { l: 'High', c: '#EF4444' }].map(s => (
              <div key={s.l} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: s.c }} />
                <span style={{ color: '#94A3B8' }}>{s.l}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Phase 3: Live Model Health Card */}
        <NavLink to="/model-health" style={{ textDecoration: 'none' }}>
        <div className="glass" style={{ padding: 24, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', cursor: 'pointer', transition: 'border-color 0.2s' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94A3B8' }}>Model Health</h3>
            <span className="font-mono" style={{ fontSize: '0.6rem', padding: '2px 6px', background: 'rgba(0, 240, 255, 0.1)', color: '#00F0FF', borderRadius: 4, border: '1px solid rgba(0, 240, 255, 0.3)' }}>34-DIM MLP</span>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <span style={{ fontSize: '0.65rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em' }}>F1 Score</span>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: (modelHealth.currentF1 || modelHealth.f1_score) >= 0.9 ? '#10B981' : '#F59E0B', marginTop: 4 }}>{(modelHealth.currentF1 || modelHealth.f1_score || 0).toFixed(3)}</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <span style={{ fontSize: '0.65rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em' }}>AUC-ROC</span>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: '#00F0FF', marginTop: 4 }}>{(modelHealth.currentAUC || modelHealth.auc_roc || 0).toFixed(3)}</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <span style={{ fontSize: '0.65rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Feedback</span>
              <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: '#7C3AED', marginTop: 4 }}>{modelHealth.feedbackCount || modelHealth.feedbackSamplesUsed || 0}</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: 12, borderRadius: 8, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <span style={{ fontSize: '0.65rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</span>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: modelHealth.driftAlert ? '#F59E0B' : '#10B981', marginTop: 8 }}>{modelHealth.driftAlert ? '⚠ Drift' : '✓ Stable'}</div>
            </div>
          </div>
        </div>
        </NavLink>

        {/* AI Agent Network */}
        <div className="glass" style={{ padding: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 600, color: '#94A3B8' }}>AI Agent Network — Live</h3>
            <span className="font-mono" style={{ fontSize: '0.7rem', color: '#06B6D4' }}>17 nodes</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12 }}>
            {AGENT_NAMES.map(name => {
              const data = agentScores[name] || {};
              const score = data.score || 0;
              const firing = score > 0.45;
              const nodeColor = firing ? '#EF4444' : score > 0.2 ? '#F59E0B' : '#10B981';
              const isGpu = ['Graph GCN', 'Zero-Day', 'Temporal/APT'].includes(name);
              return (
                <div key={name} className={firing ? 'pulse-red' : 'pulse-green'} style={{
                  padding: '14px 8px', borderRadius: 12, textAlign: 'center',
                  background: firing ? 'rgba(239,68,68,0.06)' : 'rgba(16,185,129,0.04)',
                  border: `1px solid ${firing ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.1)'}`,
                  transition: 'all 0.3s ease',
                }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%', margin: '0 auto 8px',
                    background: `${nodeColor}18`, border: `2px solid ${nodeColor}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    {isGpu ? <Cpu size={12} color={nodeColor} /> : <Target size={12} color={nodeColor} />}
                  </div>
                  <div style={{ fontSize: '0.6rem', fontWeight: 600, color: '#CBD5E1', lineHeight: 1.2 }}>{name.length > 10 ? name.slice(0, 9) + '…' : name}</div>
                  <div className="font-mono" style={{ fontSize: '0.62rem', color: nodeColor, marginTop: 4, fontWeight: 700 }}>{Math.round(score * 100)}%</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
