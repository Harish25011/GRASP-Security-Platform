"""Temporal/APT Agent — 7-day graph similarity for APT detection."""
import time
import numpy as np
from collections import defaultdict, deque
from backend.agents.base_agent import BaseAgent

class TemporalAPTAgent(BaseAgent):
    def __init__(self, window_days=7):
        super().__init__("Temporal/APT", "gpu")
        self.snapshots = deque(maxlen=100)
        self.window_sec = window_days * 86400

    def score(self, graph_snapshot, node_id, event_data=None):
        if not graph_snapshot.has_node(node_id):
            return 0.0, 0.5
        current_sig = self._compute_signature(graph_snapshot, node_id)
        self.snapshots.append({"time": time.time(), "sig": current_sig, "node": node_id})
        past = [s for s in self.snapshots if s["node"] == node_id and time.time() - s["time"] < self.window_sec]
        if len(past) < 3:
            return 0.0, 0.4
        sigs = [s["sig"] for s in past]
        changes = []
        for i in range(1, len(sigs)):
            diff = np.linalg.norm(np.array(sigs[i]) - np.array(sigs[i-1]))
            changes.append(diff)
        if not changes:
            return 0.0, 0.5
        trend = np.mean(changes[-5:]) if len(changes) >= 5 else np.mean(changes)
        risk = min(1.0, max(0.0, trend / 3.0))
        # confidence equals normalized graph similarity trend as implied
        return risk, risk

    def _compute_signature(self, graph, node_id):
        in_d = graph.in_degree(node_id)
        out_d = graph.out_degree(node_id)
        neighbors = len(set(graph.predecessors(node_id)) | set(graph.successors(node_id)))
        features = graph.nodes[node_id].get("features", [0, 0, 0])
        return [in_d, out_d, neighbors] + list(features[:4])
