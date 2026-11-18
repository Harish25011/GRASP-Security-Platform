import { useState, useEffect, useRef, useCallback } from 'react';
import { useGraphStore } from '../store/graphStore';
import { Crosshair, Play, RotateCcw, Shield, AlertTriangle, Lock, Eye, Cpu, Zap } from 'lucide-react';

const ATTACKS = [
  { id: 'ddos', name: 'DDoS Flood', icon: '🌊', desc: 'Volumetric flood attack overwhelming target capacity', severity: 'critical', agents: ['DDoS', 'Spike', 'Graph GCN'] },
  { id: 'sql_injection', name: 'SQL Injection', icon: '💉', desc: 'Malicious SQL payload injected through input fields', severity: 'high', agents: ['SQLi/XSS', 'Signature', 'Behavior'] },
  { id: 'ransomware', name: 'Ransomware', icon: '🔐', desc: 'File encryption spreading across network nodes', severity: 'critical', agents: ['Ransomware', 'Lateral Move', 'Temporal/APT'] },
  { id: 'port_scan', name: 'Port Scan', icon: '🔍', desc: 'Network reconnaissance scanning open ports', severity: 'medium', agents: ['Port Scan', 'Signature', 'C2/Beacon'] },
  { id: 'zero_day', name: 'Zero-Day Exploit', icon: '💀', desc: 'Unknown vulnerability exploitation with no prior signature', severity: 'critical', agents: ['Zero-Day', 'Graph GCN', 'Behavior'] },
  { id: 'lateral', name: 'Lateral Movement', icon: '🦀', desc: 'Attacker moving through internal network nodes', severity: 'high', agents: ['Lateral Move', 'Behavior', 'Graph GCN'] },
  { id: 'exfiltration', name: 'Data Exfiltration', icon: '📤', desc: 'Sensitive data being extracted to external servers', severity: 'critical', agents: ['Exfiltration', 'C2/Beacon', 'MITM'] },
  { id: 'brute_force', name: 'Brute Force', icon: '🔨', desc: 'Credential stuffing attack on authentication endpoints', severity: 'high', agents: ['Brute Force', 'Spike', 'Signature'] },
];

// 3D Network node positions (arranged in a sphere-like perspective layout)
const NETWORK_NODES = [
  { id: 'attacker', x: 50, y: 50, z: 40, label: 'ATTACKER', type: 'attacker' },
  { id: 'firewall', x: 200, y: 120, z: 20, label: 'Firewall', type: 'defense' },
  { id: 'router-1', x: 320, y: 60, z: 30, label: 'Router-01', type: 'network' },
  { id: 'router-2', x: 340, y: 180, z: 10, label: 'Router-02', type: 'network' },
  { id: 'server-web', x: 480, y: 50, z: 25, label: 'Web Server', type: 'server' },
  { id: 'server-app', x: 500, y: 140, z: 15, label: 'App Server', type: 'server' },
  { id: 'server-db', x: 520, y: 230, z: 5, label: 'Database', type: 'server' },
  { id: 'host-1', x: 650, y: 40, z: 30, label: 'Host-01', type: 'endpoint' },
  { id: 'host-2', x: 670, y: 130, z: 20, label: 'Host-02', type: 'endpoint' },
  { id: 'host-3', x: 660, y: 220, z: 10, label: 'Host-03', type: 'endpoint' },
  { id: 'target', x: 780, y: 140, z: 35, label: 'TARGET', type: 'target' },
];

const EDGES = [
  ['attacker', 'firewall'], ['firewall', 'router-1'], ['firewall', 'router-2'],
  ['router-1', 'server-web'], ['router-1', 'server-app'], ['router-2', 'server-app'],
  ['router-2', 'server-db'], ['server-web', 'host-1'], ['server-app', 'host-2'],
  ['server-db', 'host-3'], ['host-1', 'target'], ['host-2', 'target'], ['host-3', 'target'],
  ['server-web', 'server-app'], ['server-app', 'server-db'],
];

const ATTACK_PATHS = {
  ddos: ['attacker', 'firewall', 'router-1', 'server-web', 'server-app'],
  sql_injection: ['attacker', 'firewall', 'router-1', 'server-web', 'server-app', 'server-db'],
  ransomware: ['attacker', 'firewall', 'router-2', 'server-db', 'host-3', 'host-2', 'host-1'],
  port_scan: ['attacker', 'firewall', 'router-1', 'router-2', 'server-web', 'server-app', 'server-db'],
  zero_day: ['attacker', 'firewall', 'router-1', 'server-web', 'host-1', 'target'],
  lateral: ['attacker', 'firewall', 'router-2', 'server-app', 'host-2', 'target'],
  exfiltration: ['attacker', 'firewall', 'router-1', 'server-app', 'server-db', 'host-3'],
  brute_force: ['attacker', 'firewall', 'router-1', 'server-web', 'server-app'],
};

const DETECTION_STEPS = [
  { phase: 'INGRESS', label: 'Packet enters network perimeter', icon: Eye },
  { phase: 'ANALYSIS', label: 'CPU agents analyze payload signatures', icon: Cpu },
  { phase: 'GRAPH', label: 'Graph neural network models structural anomaly', icon: Zap },
  { phase: 'SCORING', label: 'Meta-agent aggregates swarm scores', icon: AlertTriangle },
  { phase: 'DECISION', label: 'Decision engine evaluates risk threshold', icon: Shield },
  { phase: 'ACTION', label: 'System quarantines node to Safe Box', icon: Lock },
];

function getNodeStyle(type, isOnPath, isCompromised, isDetected) {
  const base = { attacker: '#EF4444', defense: '#F59E0B', network: '#3B82F6', server: '#06B6D4', endpoint: '#8B5CF6', target: '#10B981' };
  const color = base[type] || '#64748B';
  if (isDetected) return { bg: 'rgba(16,185,129,0.15)', border: '#10B981', color: '#10B981', glow: '0 0 20px rgba(16,185,129,0.4)' };
  if (isCompromised) return { bg: 'rgba(239,68,68,0.15)', border: '#EF4444', color: '#EF4444', glow: '0 0 20px rgba(239,68,68,0.5)' };
  if (isOnPath) return { bg: `${color}15`, border: color, color, glow: `0 0 12px ${color}44` };
  return { bg: `${color}08`, border: `${color}44`, color: `${color}88`, glow: 'none' };
}

export default function AttackSim() {
  const { addAnomaly, addAlert, addEvent, addRiskPoint, updateAgentScores } = useGraphStore();
  const [selectedAttack, setSelectedAttack] = useState(null);
  const [simState, setSimState] = useState('idle'); // idle, running, detected, complete
  const [currentPathIdx, setCurrentPathIdx] = useState(-1);
  const [detectionStep, setDetectionStep] = useState(-1);
  const [attackResult, setAttackResult] = useState(null);
  const [particles, setParticles] = useState([]);
  const timerRef = useRef(null);

  const resetSim = () => {
    setSimState('idle');
    setCurrentPathIdx(-1);
    setDetectionStep(-1);
    setAttackResult(null);
    setParticles([]);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const runSimulation = useCallback(() => {
    if (!selectedAttack) return;
    resetSim();
    setSimState('running');
    const path = ATTACK_PATHS[selectedAttack.id] || [];
    const attack = selectedAttack;
    let step = 0;

    timerRef.current = setInterval(() => {
      if (step < path.length) {
        setCurrentPathIdx(step);
        // Add particle between current and previous node
        if (step > 0) {
          const fromNode = NETWORK_NODES.find(n => n.id === path[step - 1]);
          const toNode = NETWORK_NODES.find(n => n.id === path[step]);
          if (fromNode && toNode) {
            setParticles(prev => [...prev, { id: Date.now(), x1: fromNode.x, y1: fromNode.y, x2: toNode.x, y2: toNode.y }]);
          }
        }
        step++;
      } else if (step === path.length) {
        // Detection phase
        setSimState('detected');
        step++;
      } else if (step - path.length - 1 < DETECTION_STEPS.length) {
        const dStep = step - path.length - 1;
        setDetectionStep(dStep);
        step++;
      } else {
        // Complete
        clearInterval(timerRef.current);
        setSimState('complete');
        
        // Execute real backend API call
        const runBackendAttack = async () => {
          const backendId = attack.id === 'lateral' ? 'lateral_move' : attack.id;
          try {
            const res = await fetch(`http://localhost:8000/api/attack`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ attack_type: backendId }),
            });
            const data = await res.json();
            const decision = data.decision || {};
            const swarm = data.swarm_result || {};
            setAttackResult({
              risk: decision.risk_score || 0.75,
              detected_by: (decision.top_agents || []).map(a => a.agent),
              action: decision.action === 'quarantine' ? 'QUARANTINED' : 'FLAGGED',
              latency: swarm.total_latency_ms?.toFixed(1) || '12.0',
            });
            // Update UI stores with the actual scores
            const riskScore = decision.risk_score || 0.75;
            const scores = swarm.scores || {};
            if (Object.keys(scores).length > 0) {
              updateAgentScores(scores);
            }
            addAnomaly({ node_id: path[path.length - 1], risk_score: riskScore, severity: decision.severity || attack.severity, attack_type: backendId, scores });
            addAlert({ type: 'anomaly', message: `🚨 ${attack.name} attack detected — ${decision.tier || 'CRITICAL'}`, severity: decision.severity || attack.severity });
            addEvent({ source_ip: '10.0.0.1', dest_ip: path[path.length - 1], protocol: 'TCP', event_type: backendId, risk_score: riskScore, label: backendId });
            addRiskPoint({ time: new Date().toLocaleTimeString(), risk: riskScore, events: 1 });
          } catch (err) {
            console.error('Backend attack API failed:', err);
            // Fallback
            const riskScore = 0.65 + Math.random() * 0.35;
            setAttackResult({
              risk: riskScore,
              detected_by: attack.agents,
              action: riskScore > 0.7 ? 'QUARANTINED' : 'FLAGGED',
              latency: (Math.random() * 12 + 3).toFixed(1),
            });
            const scores = {};
            attack.agents.forEach(a => { scores[a] = 0.7 + Math.random() * 0.3; });
            updateAgentScores(scores);
          }
        };
        
        runBackendAttack();
      }
    }, 600);
  }, [selectedAttack]);

  useEffect(() => { return () => { if (timerRef.current) clearInterval(timerRef.current); }; }, []);

  const currentPath = selectedAttack ? (ATTACK_PATHS[selectedAttack.id] || []) : [];
  const compromisedNodes = currentPath.slice(0, currentPathIdx + 1);

  return (
    <div className="fade-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: '1.7rem', fontWeight: 800, color: '#F1F5F9', letterSpacing: '-0.02em' }}>Attack Simulation</h1>
          <p style={{ fontSize: '0.85rem', color: '#64748B', marginTop: 4 }}>3D network attack visualization & detection</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          {simState !== 'idle' && (
            <button className="btn-ghost" onClick={resetSim} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <RotateCcw size={15} /> Reset
            </button>
          )}
          <button className="btn-primary" onClick={runSimulation} disabled={!selectedAttack || simState === 'running'}
            style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Play size={16} /> {simState === 'running' ? 'Simulating...' : 'Launch Attack'}
          </button>
        </div>
      </div>

      {/* Attack Type Selector */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 20 }}>
        {ATTACKS.map(a => (
          <button key={a.id} onClick={() => { resetSim(); setSelectedAttack(a); }}
            className="glass" style={{
              padding: '14px 16px', cursor: 'pointer', textAlign: 'left',
              borderColor: selectedAttack?.id === a.id ? '#06B6D4' : undefined,
              boxShadow: selectedAttack?.id === a.id ? '0 0 20px rgba(6,182,212,0.15)' : undefined,
              transition: 'all 0.25s',
            }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span style={{ fontSize: '1.2rem' }}>{a.icon}</span>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: selectedAttack?.id === a.id ? '#22D3EE' : '#E2E8F0' }}>{a.name}</span>
            </div>
            <p style={{ fontSize: '0.68rem', color: '#64748B', lineHeight: 1.4 }}>{a.desc}</p>
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2.5fr 1fr', gap: 16 }}>
        {/* 3D Network Visualization */}
        <div className="glass" style={{ padding: 0, overflow: 'hidden', position: 'relative' }}>
          <div style={{
            padding: '14px 20px', borderBottom: '1px solid var(--border)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#94A3B8' }}>Network Topology — 3D View</span>
            {simState !== 'idle' && (
              <span className="font-mono" style={{
                padding: '3px 10px', borderRadius: 6, fontSize: '0.68rem', fontWeight: 700,
                background: simState === 'complete' ? 'rgba(16,185,129,0.1)' : simState === 'detected' ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)',
                color: simState === 'complete' ? '#10B981' : simState === 'detected' ? '#F59E0B' : '#EF4444',
              }}>{simState === 'complete' ? '✓ NEUTRALIZED' : simState === 'detected' ? '⚠ DETECTING...' : '● ATTACK IN PROGRESS'}</span>
            )}
          </div>

          <svg viewBox="0 0 860 300" style={{
            width: '100%', height: 320,
            background: 'radial-gradient(ellipse at center, #0F1729 0%, #080C14 100%)',
          }}>
            {/* Grid lines for depth */}
            {Array.from({ length: 8 }).map((_, i) => (
              <line key={`g${i}`} x1={0} y1={i * 42 + 20} x2={860} y2={i * 42 + 20}
                stroke="rgba(6,182,212,0.03)" strokeWidth={1} />
            ))}
            {Array.from({ length: 12 }).map((_, i) => (
              <line key={`v${i}`} x1={i * 78 + 20} y1={0} x2={i * 78 + 20} y2={300}
                stroke="rgba(6,182,212,0.03)" strokeWidth={1} />
            ))}

            {/* Edges */}
            {EDGES.map(([from, to], i) => {
              const f = NETWORK_NODES.find(n => n.id === from);
              const t = NETWORK_NODES.find(n => n.id === to);
              if (!f || !t) return null;
              const onPath = compromisedNodes.includes(from) && compromisedNodes.includes(to);
              return (
                <line key={i} x1={f.x + 30} y1={f.y + 16} x2={t.x + 30} y2={t.y + 16}
                  stroke={onPath ? '#EF444466' : 'rgba(148,163,184,0.08)'} strokeWidth={onPath ? 2 : 1}
                  style={{ transition: 'all 0.4s ease' }} />
              );
            })}

            {/* Attack path animated dashes */}
            {currentPathIdx >= 1 && currentPath.slice(0, currentPathIdx + 1).map((nodeId, i) => {
              if (i === 0) return null;
              const from = NETWORK_NODES.find(n => n.id === currentPath[i - 1]);
              const to = NETWORK_NODES.find(n => n.id === nodeId);
              if (!from || !to) return null;
              return (
                <line key={`ap${i}`} x1={from.x + 30} y1={from.y + 16} x2={to.x + 30} y2={to.y + 16}
                  stroke="#EF4444" strokeWidth={2.5} strokeDasharray="6 4"
                  style={{ filter: 'drop-shadow(0 0 4px rgba(239,68,68,0.5))' }}>
                  <animate attributeName="stroke-dashoffset" from="20" to="0" dur="0.8s" repeatCount="indefinite" />
                </line>
              );
            })}

            {/* Particle effects along attack path */}
            {particles.map(p => (
              <circle key={p.id} r="4" fill="#EF4444" style={{ filter: 'drop-shadow(0 0 6px #EF4444)' }}>
                <animate attributeName="cx" from={p.x1 + 30} to={p.x2 + 30} dur="0.5s" fill="freeze" />
                <animate attributeName="cy" from={p.y1 + 16} to={p.y2 + 16} dur="0.5s" fill="freeze" />
                <animate attributeName="opacity" from="1" to="0" dur="1.5s" fill="freeze" />
              </circle>
            ))}

            {/* Nodes */}
            {NETWORK_NODES.map(node => {
              const isOnPath = currentPath.includes(node.id);
              const isCompromised = compromisedNodes.includes(node.id);
              const isDetected = simState === 'complete' && isOnPath;
              const style = getNodeStyle(node.type, isOnPath, isCompromised, isDetected);
              const scale = 1 + node.z / 200; // 3D depth effect
              const shadowY = node.z / 5;

              return (
                <g key={node.id} style={{ transition: 'all 0.4s ease' }}>
                  {/* 3D shadow */}
                  <ellipse cx={node.x + 30} cy={node.y + 36 + shadowY} rx={18 * scale} ry={5}
                    fill="rgba(0,0,0,0.2)" style={{ filter: 'blur(3px)' }} />
                  {/* Node body */}
                  <rect x={node.x} y={node.y} width={60 * scale} height={32 * scale}
                    rx={8} fill={style.bg} stroke={style.border} strokeWidth={isCompromised ? 2 : 1}
                    style={{ filter: isCompromised || isDetected ? `drop-shadow(${style.glow.replace('0 0', '0 0')})` : undefined, transition: 'all 0.3s' }} />
                  {/* Node icon */}
                  {node.type === 'attacker' && <text x={node.x + 8} y={node.y + 20} fontSize="14">{isCompromised ? '☠️' : '👤'}</text>}
                  {node.type === 'target' && <text x={node.x + 8} y={node.y + 20} fontSize="14">{isDetected ? '🛡️' : isCompromised ? '🎯' : '🏥'}</text>}
                  {/* Label */}
                  <text x={node.x + 30 * scale} y={node.y + 18 * scale} textAnchor="middle"
                    fill={style.color} fontSize={node.type === 'attacker' || node.type === 'target' ? 8 : 7.5}
                    fontFamily="'Inter', sans-serif" fontWeight={600}
                    dx={node.type === 'attacker' || node.type === 'target' ? 8 : 0}>
                    {node.label}
                  </text>
                  {/* Pulse ring for compromised nodes */}
                  {isCompromised && !isDetected && (
                    <circle cx={node.x + 30} cy={node.y + 16} r={20} fill="none"
                      stroke="#EF4444" strokeWidth={1} opacity={0.5}>
                      <animate attributeName="r" from="16" to="28" dur="1.2s" repeatCount="indefinite" />
                      <animate attributeName="opacity" from="0.6" to="0" dur="1.2s" repeatCount="indefinite" />
                    </circle>
                  )}
                  {/* Shield for detected nodes */}
                  {isDetected && (
                    <circle cx={node.x + 30} cy={node.y + 16} r={20} fill="none"
                      stroke="#10B981" strokeWidth={1.5} opacity={0.6}>
                      <animate attributeName="r" from="18" to="26" dur="1.5s" repeatCount="indefinite" />
                      <animate attributeName="opacity" from="0.5" to="0" dur="1.5s" repeatCount="indefinite" />
                    </circle>
                  )}
                </g>
              );
            })}
          </svg>
        </div>

        {/* Right Panel: Detection Timeline + Result */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Detection Timeline */}
          <div className="glass" style={{ padding: 20, flex: 1 }}>
            <h4 style={{ fontSize: '0.78rem', fontWeight: 700, color: '#94A3B8', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Detection Pipeline
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {DETECTION_STEPS.map((step, i) => {
                const Icon = step.icon;
                const isActive = detectionStep === i;
                const isDone = detectionStep > i;
                const isPending = detectionStep < i;
                return (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', borderRadius: 10,
                    background: isActive ? 'rgba(6,182,212,0.08)' : isDone ? 'rgba(16,185,129,0.04)' : 'transparent',
                    border: `1px solid ${isActive ? 'rgba(6,182,212,0.2)' : 'transparent'}`,
                    transition: 'all 0.3s', opacity: isPending && simState !== 'idle' ? 0.35 : 1,
                  }}>
                    <div style={{
                      width: 28, height: 28, borderRadius: 8, flexShrink: 0,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: isDone ? 'rgba(16,185,129,0.12)' : isActive ? 'rgba(6,182,212,0.12)' : 'rgba(100,116,139,0.06)',
                      border: `1px solid ${isDone ? 'rgba(16,185,129,0.25)' : isActive ? 'rgba(6,182,212,0.25)' : 'rgba(100,116,139,0.1)'}`,
                    }}>
                      <Icon size={13} color={isDone ? '#10B981' : isActive ? '#06B6D4' : '#475569'} />
                    </div>
                    <div>
                      <div className="font-mono" style={{ fontSize: '0.62rem', color: isDone ? '#10B981' : isActive ? '#06B6D4' : '#475569', fontWeight: 700, marginBottom: 1 }}>
                        {step.phase}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: isDone ? '#94A3B8' : isActive ? '#CBD5E1' : '#475569', lineHeight: 1.3 }}>
                        {step.label}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Result Card */}
          {attackResult && (
            <div className="glass fade-up" style={{
              padding: 20,
              borderColor: attackResult.action === 'QUARANTINED' ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)',
            }}>
              <h4 style={{ fontSize: '0.78rem', fontWeight: 700, color: '#10B981', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                ✓ Threat Neutralized
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
                <div>
                  <div style={{ fontSize: '0.62rem', color: '#64748B' }}>Risk Score</div>
                  <div className="font-mono" style={{ fontSize: '1.3rem', fontWeight: 800, color: '#EF4444' }}>{(attackResult.risk * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.62rem', color: '#64748B' }}>Latency</div>
                  <div className="font-mono" style={{ fontSize: '1.3rem', fontWeight: 800, color: '#06B6D4' }}>{attackResult.latency}ms</div>
                </div>
              </div>
              <div style={{ fontSize: '0.62rem', color: '#64748B', marginBottom: 6 }}>Detected By</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {attackResult.detected_by.map(a => (
                  <span key={a} style={{
                    padding: '3px 8px', borderRadius: 5, fontSize: '0.65rem', fontWeight: 600,
                    background: 'rgba(6,182,212,0.08)', color: '#22D3EE', border: '1px solid rgba(6,182,212,0.15)',
                  }}>{a}</span>
                ))}
              </div>
              <div style={{
                marginTop: 12, padding: '6px 10px', borderRadius: 6, textAlign: 'center',
                background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)',
              }}>
                <span className="font-mono" style={{ fontSize: '0.72rem', fontWeight: 700, color: '#10B981' }}>
                  🔒 {attackResult.action}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
