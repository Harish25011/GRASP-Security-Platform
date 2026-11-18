import { create } from 'zustand';

const AGENT_NAMES = [
  'Signature', 'Spike', 'Behavior', 'Port Scan', 'DDoS', 'SQLi/XSS',
  'Brute Force', 'Lateral Movement', 'Exfiltration', 'Ransomware',
  'MITM', 'Supply Inject', 'Priv Escalation', 'C2/Beaconing',
  'Graph GCN', 'Zero-Day', 'Temporal/APT'
];

const initialAgentScores = Object.fromEntries(AGENT_NAMES.map(a => [a, { score: 0, latency: 0, history: [] }]));

const NODE_TYPES = ['Hospital', 'Supplier', 'Distributor', 'Manufacturer', 'Pharmacy', 'Warehouse', 'Lab'];

function generateMockGraph() {
  const nodes = [];
  const edges = [];
  for (let i = 0; i < 30; i++) {
    nodes.push({
      data: {
        id: `192.168.1.${10 + i}`,
        label: `${NODE_TYPES[i % NODE_TYPES.length]}-${String(i).padStart(2, '0')}`,
        node_type: NODE_TYPES[i % NODE_TYPES.length],
        risk_score: Math.random() * 0.4,
        status: 'active',
      }
    });
  }
  for (let i = 0; i < 50; i++) {
    const src = `192.168.1.${10 + Math.floor(Math.random() * 30)}`;
    const dst = `192.168.1.${10 + Math.floor(Math.random() * 30)}`;
    if (src !== dst) {
      edges.push({ data: { source: src, target: dst, protocol: ['TCP', 'UDP', 'HTTP'][Math.floor(Math.random() * 3)] } });
    }
  }
  return { elements: [...nodes, ...edges] };
}

export const useGraphStore = create((set, get) => ({
  // Graph data
  graph: generateMockGraph(),
  setGraph: (graph) => set({ graph }),

  // Agent scores
  agentScores: initialAgentScores,
  updateAgentScores: (scores) => set(state => {
    const updated = { ...state.agentScores };
    Object.entries(scores).forEach(([agent, score]) => {
      const prev = updated[agent] || { score: 0, latency: 0, history: [] };
      updated[agent] = {
        score: typeof score === 'object' ? score.score : score,
        latency: typeof score === 'object' ? score.latency_ms || 0 : Math.random() * 15,
        history: [...prev.history.slice(-19), typeof score === 'object' ? score.score : score],
      };
    });
    return { agentScores: updated };
  }),

  // Anomalies
  anomalies: [],
  addAnomaly: (anomaly) => set(state => ({
    anomalies: [{ ...anomaly, id: Date.now(), timestamp: new Date().toISOString() }, ...state.anomalies].slice(0, 100)
  })),

  // Safe Box
  safeBox: [],
  safeBoxCount: 0,
  addToSafeBox: (node) => set(state => ({
    safeBox: [{ ...node, quarantined_at: new Date().toISOString() }, ...state.safeBox],
    safeBoxCount: state.safeBoxCount + 1,
  })),
  removeFromSafeBox: (nodeId) => set(state => ({
    safeBox: state.safeBox.filter(n => n.node_id !== nodeId),
    safeBoxCount: Math.max(0, state.safeBoxCount - 1),
  })),

  // Event log
  eventLog: [],
  addEvent: (event) => set(state => ({
    eventLog: [{ ...event, id: Date.now(), timestamp: new Date().toISOString() }, ...state.eventLog].slice(0, 200)
  })),

  // Alerts
  alerts: [],
  addAlert: (alert) => set(state => ({
    alerts: [{ ...alert, id: Date.now(), timestamp: new Date().toISOString() }, ...state.alerts].slice(0, 50)
  })),
  dismissAlert: (id) => set(state => ({ alerts: state.alerts.filter(a => a.id !== id) })),

  // Metrics
  metrics: {
    totalNodes: 30,
    activeAlerts: 0,
    avgRisk: 0.12,
    eventsPerSec: 0,
    gpuUtilization: 22,
  },
  updateMetrics: (m) => set(state => ({ metrics: { ...state.metrics, ...m } })),

  // Risk timeline data
  riskTimeline: Array.from({ length: 20 }, (_, i) => ({
    time: new Date(Date.now() - (20 - i) * 3000).toLocaleTimeString(),
    risk: Math.random() * 0.3,
    events: Math.floor(Math.random() * 5),
  })),
  addRiskPoint: (point) => set(state => ({
    riskTimeline: [...state.riskTimeline.slice(-29), point]
  })),

  // Connection status
  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),

  // Mock Traffic Toggle
  mockEnabled: false,
  toggleMock: () => set(state => ({ mockEnabled: !state.mockEnabled })),

  // ─── Phase 3: Agent Confidence ───
  agentConfidence: {},
  setAgentConfidence: (v) => set({ agentConfidence: v }),

  // ─── Phase 3: SHAP Values per node ───
  shapValues: {},
  setShapValues: (nodeId, vals) => set(s => ({
    shapValues: { ...s.shapValues, [nodeId]: vals }
  })),

  // ─── Phase 3: Attention Weights per node ───
  attentionWeights: {},
  setAttentionWeights: (nodeId, w) => set(s => ({
    attentionWeights: { ...s.attentionWeights, [nodeId]: w }
  })),

  // ─── Phase 3: Risk Tier per node ───
  riskTiers: {},
  setRiskTier: (nodeId, tier) => set(s => ({
    riskTiers: { ...s.riskTiers, [nodeId]: tier }
  })),

  // ─── Phase 3: Stream Processor Status ───
  streamStatus: {
    active: false,
    queueDepth: 0,
    eventsPerSec: 0,
    dropCount: 0,
    workerCount: 8,
    activeSources: [],
    dedupCacheSize: 0,
    isCaptureRunning: false,
    captureTarget: null,
    workers: Array.from({ length: 8 }, (_, i) => ({ id: i, status: 'idle', processed: 0 })),
  },
  updateStreamStatus: (s) => set(state => ({ streamStatus: { ...state.streamStatus, ...s } })),
  setStreamStatus: (v) => set({ streamStatus: v }),

  // ─── Phase 3: Model Health ───
  modelHealth: {
    f1_score: 0.934,
    auc_roc: 0.967,
    feedbackSamplesUsed: 0,
    llmOnline: false,
    lastRetrained: null,
    feedbackCount: 0,
    currentF1: 0.934,
    currentAUC: 0.967,
    driftAlert: false,
  },
  updateModelHealth: (h) => set(state => ({ modelHealth: { ...state.modelHealth, ...h } })),
  setModelHealth: (v) => set(state => ({ modelHealth: { ...state.modelHealth, ...v } })),

  // ─── Phase 3: Feedback Log ───
  feedbackLog: [],
  addFeedback: (entry) => set(s => ({
    feedbackLog: [...s.feedbackLog, entry]
  })),

  // ─── Phase 3: Live Capture ───
  captureActive: false,
  captureTargetIp: '',
  packetsPerSec: 0,
  setCaptureStatus: (v) => set(v),

  // ─── Phase 3: Live Threat Events ───
  threatEvents: [],
  addThreatEvent: (e) => set(s => ({
    threatEvents: [e, ...s.threatEvents].slice(0, 200)
  })),
  clearThreatEvents: () => set({ threatEvents: [] }),

  // ─── Phase 3: Ollama Status ───
  ollamaOnline: false,
  setOllamaOnline: (v) => set({ ollamaOnline: v }),

  // Legacy alias
  currentRiskTier: 'NORMAL',
  setCurrentRiskTier: (tier) => set({ currentRiskTier: tier }),
}));
