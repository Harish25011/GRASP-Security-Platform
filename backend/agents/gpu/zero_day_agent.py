"""Zero-Day Agent — cosine distance in GCN embedding space."""
import numpy as np
from backend.agents.base_agent import BaseAgent

class ZeroDayAgent(BaseAgent):
    def __init__(self):
        super().__init__("Zero-Day", "gpu")
        self._centroid = None
        self._embeddings = []

    def score(self, graph_snapshot, node_id, event_data=None):
        # Event-based detection
        if event_data and event_data.get("event_type") in ("zero_day", "unknown_exploit"):
            return 0.89, 0.85

        if not graph_snapshot.has_node(node_id):
            return 0.0, 0.5
        features = graph_snapshot.nodes[node_id].get("features", [])
        if not features:
            return 0.0, 0.5
        embedding = np.array(features, dtype=np.float32)
        self._embeddings.append(embedding)
        if len(self._embeddings) < 5:
            return 0.0, 0.4
        self._centroid = np.mean(self._embeddings[-100:], axis=0)
        norm_e = np.linalg.norm(embedding)
        norm_c = np.linalg.norm(self._centroid)
        if norm_e == 0 or norm_c == 0:
            return 0.0, 0.5
        cos_sim = np.dot(embedding, self._centroid) / (norm_e * norm_c)
        distance = 1.0 - cos_sim
        risk = min(1.0, max(0.0, distance * 2))
        confidence = 1.0 - min(1.0, distance)
        return risk, confidence
