import { useEffect, useRef } from 'react';
import { useGraphStore } from '../store/graphStore';

const AGENT_NAMES = [
  'Signature', 'Spike', 'Behavior', 'Port Scan', 'DDoS', 'SQLi/XSS',
  'Brute Force', 'Lateral Movement', 'Exfiltration', 'Ransomware',
  'MITM', 'Supply Inject', 'Priv Escalation', 'C2/Beaconing',
  'Graph GCN', 'Zero-Day', 'Temporal/APT'
];

const ATTACK_TYPES = ['ddos', 'port_scan', 'sql_injection', 'xss', 'brute_force', 'lateral_movement', 'exfiltration', 'ransomware', 'mitm', 'supply_inject', 'priv_escalation', 'c2_beacon', 'zero_day', 'apt', 'command_injection'];

export function useWebSocket() {
  const wsRef = useRef(null);
  const mockIntervalRef = useRef(null);
  const { addEvent, updateAgentScores, addAnomaly, addToSafeBox, addAlert, addRiskPoint, updateMetrics, setWsConnected, updateStreamStatus, mockEnabled } = useGraphStore();

  useEffect(() => {
    if (mockEnabled) {
      startMockSimulation();
    } else {
      if (mockIntervalRef.current) clearInterval(mockIntervalRef.current);
    }
    return () => {
      if (mockIntervalRef.current) clearInterval(mockIntervalRef.current);
    };
  }, [mockEnabled]);

  useEffect(() => {
    let reconnectTimer = null;

    function connectWebSocket() {
      try {
        const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws/events`);
        ws.onopen = () => {
          setWsConnected(true);
          console.log("[WS] Connected to backend");
        };
        ws.onmessage = (e) => {
          const msg = JSON.parse(e.data);
          handleMessage(msg);
        };
        ws.onclose = () => {
          setWsConnected(false);
          console.log("[WS] Disconnected — reconnecting in 3s...");
          reconnectTimer = setTimeout(connectWebSocket, 3000);
        };
        ws.onerror = () => {
          ws.close(); // triggers onclose -> reconnect
        };
        wsRef.current = ws;
      } catch {
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      }
    }

    connectWebSocket();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (wsRef.current) wsRef.current.close();
      if (mockIntervalRef.current) clearInterval(mockIntervalRef.current);
    };
  }, []);

  function handleMessage(msg) {
    const store = useGraphStore.getState();
    switch (msg.type) {
      case 'event':
        addEvent(msg.payload);
        if (msg.payload.result?.scores) updateAgentScores(msg.payload.result.scores);
        break;
      case 'anomaly':
        addAnomaly(msg.payload);
        addAlert({ type: 'anomaly', message: `Anomaly detected on ${msg.payload.node_id}`, severity: msg.payload.severity });
        break;
      case 'agent_update':
        updateAgentScores(msg.payload);
        if (msg.payload.confidence) store.setAgentConfidence(msg.payload.confidence);
        break;
      case 'safebox':
        if (msg.payload.action === 'quarantine') addToSafeBox(msg.payload);
        break;
      // ─── Phase 3 WebSocket handlers ───
      case 'model_updated':
        store.setModelHealth(msg.payload);
        break;
      case 'stream_status':
        store.setStreamStatus(msg.payload);
        break;
      case 'threat_detected':
        store.addThreatEvent(msg.payload);
        break;
      case 'risk_tier':
        store.setRiskTier(msg.payload.node_id, msg.payload.tier);
        break;
    }
  }

  function startMockSimulation() {
    setWsConnected(true);
    let eventCounter = 0;

    mockIntervalRef.current = setInterval(() => {
      eventCounter++;
      const isAnomaly = Math.random() < 0.12;
      const nodeIdx = Math.floor(Math.random() * 30);
      const nodeId = `192.168.1.${10 + nodeIdx}`;
      const srcIdx = Math.floor(Math.random() * 30);
      const srcId = `192.168.1.${10 + srcIdx}`;

      const scores = {};
      AGENT_NAMES.forEach(agent => {
        scores[agent] = isAnomaly ? Math.random() * 0.6 + 0.2 : Math.random() * 0.3;
      });
      if (isAnomaly) {
        const triggerAgent = AGENT_NAMES[Math.floor(Math.random() * AGENT_NAMES.length)];
        scores[triggerAgent] = 0.7 + Math.random() * 0.3;
        const secondAgent = AGENT_NAMES[Math.floor(Math.random() * AGENT_NAMES.length)];
        scores[secondAgent] = 0.5 + Math.random() * 0.4;
      }

      updateAgentScores(scores);

      const attackType = isAnomaly ? ATTACK_TYPES[Math.floor(Math.random() * ATTACK_TYPES.length)] : null;
      const riskScore = isAnomaly ? 0.5 + Math.random() * 0.5 : Math.random() * 0.35;

      // Determine tier
      let tier = 'NORMAL';
      if (riskScore >= 0.7) tier = 'CRITICAL';
      else if (riskScore >= 0.5) tier = 'SUSPICIOUS';
      else if (riskScore >= 0.3) tier = 'WATCH';

      addEvent({
        source_ip: srcId,
        dest_ip: nodeId,
        protocol: ['TCP', 'UDP', 'HTTP', 'HTTPS'][Math.floor(Math.random() * 4)],
        event_type: attackType || 'network_flow',
        risk_score: riskScore,
        label: isAnomaly ? attackType : 'benign',
        tier,
      });

      // Set risk tier in store
      useGraphStore.getState().setRiskTier(nodeId, tier);

      if (isAnomaly) {
        const topAgents = Object.entries(scores).sort((a, b) => b[1] - a[1]).slice(0, 3);
        addAnomaly({
          node_id: nodeId,
          risk_score: riskScore,
          severity: riskScore > 0.7 ? 'critical' : 'high',
          attack_type: attackType,
          tier,
          top_agents: topAgents.map(([a, s]) => ({ agent: a, score: s })),
          scores,
        });

        addAlert({
          type: 'anomaly',
          message: `🚨 ${attackType?.replace('_', ' ').toUpperCase()} detected on ${nodeId}`,
          severity: riskScore > 0.7 ? 'critical' : 'high',
          node_id: nodeId,
        });

        if (riskScore > 0.7) {
          addToSafeBox({
            node_id: nodeId,
            risk_score: riskScore,
            reason: `Attack: ${attackType}`,
            agent_scores: scores,
          });
        }

        // Mock threat event for LiveThreatMonitor
        useGraphStore.getState().addThreatEvent({
          timestamp: new Date().toISOString(),
          source_ip: srcId,
          dest_ip: nodeId,
          attack_type: attackType,
          risk_score: riskScore,
          tier,
          fired_agents: topAgents.map(([a]) => a),
        });
      }

      addRiskPoint({
        time: new Date().toLocaleTimeString(),
        risk: riskScore,
        events: 1,
      });

      updateMetrics({
        activeAlerts: useGraphStore.getState().anomalies.length,
        avgRisk: parseFloat((useGraphStore.getState().riskTimeline.slice(-10).reduce((s, p) => s + p.risk, 0) / 10).toFixed(3)),
        eventsPerSec: Math.floor(Math.random() * 5) + 1,
      });

      updateStreamStatus({
        queueDepth: Math.floor(Math.random() * 20),
        eventsPerSec: Math.floor(Math.random() * 5) + 1,
        gpuUtil: 18 + Math.random() * 15,
        workers: Array.from({ length: 8 }, (_, i) => ({
          id: i,
          status: Math.random() > 0.3 ? 'active' : 'idle',
          processed: eventCounter + Math.floor(Math.random() * 100),
        })),
      });
    }, 2000 + Math.random() * 1000);
  }

  return wsRef;
}
