"""
DDoS Agent — IsolationForest anomaly detection on network traffic features.
Replaces hardcoded Z-score thresholds with a pre-trained ML model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("DDoSAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "ddos_agent_iforest.pkl")


class DDoSAgent(BaseAgent):
    def __init__(self):
        super().__init__("DDoS", "cpu")
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[DDoSAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[DDoSAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[DDoSAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional feature vector:
        [in_degree, out_degree, bytes_recv, pkt_rate, syn_ratio,
         unique_src_ips, avg_pkt_size, connection_duration]
        """
        in_deg = graph_snapshot.in_degree(node_id) if graph_snapshot.has_node(node_id) else 0
        out_deg = graph_snapshot.out_degree(node_id) if graph_snapshot.has_node(node_id) else 0

        bytes_recv = 0
        if graph_snapshot.has_node(node_id):
            bytes_recv = sum(d.get("bytes_recv", 0) for _, _, d in graph_snapshot.in_edges(node_id, data=True))

        # Extract from event_data if available
        pkt_rate = 0
        syn_ratio = 0.1
        avg_pkt_size = 512
        conn_duration = 30
        unique_src = 1

        if event_data:
            pkt_rate = event_data.get("flood_rate", event_data.get("pkt_rate", 0))
            size = event_data.get("size", 512)
            avg_pkt_size = size
            flags = str(event_data.get("flags", ""))
            syn_ratio = 0.9 if "S" in flags and len(flags) <= 2 else 0.1
            conn_duration = event_data.get("duration", 30)
            unique_src = event_data.get("unique_src", 1)

            # Boost features for known DDoS event types
            if event_data.get("event_type", "").lower() in ("ddos", "ddos_flood"):
                pkt_rate = max(pkt_rate, 200)
                syn_ratio = max(syn_ratio, 0.8)
                bytes_recv = max(bytes_recv, 200000)

        return np.array([in_deg, out_deg, bytes_recv, pkt_rate, syn_ratio,
                         unique_src, avg_pkt_size, conn_duration], dtype=np.float64).reshape(1, -1)

    def score(self, graph_snapshot, node_id, event_data=None) -> tuple[float, float]:
        # Graceful fallback if model not loaded
        if self._model is None:
            return 0.0, 0.0

        try:
            X = self._extract_features(graph_snapshot, node_id, event_data)

            # IsolationForest: decision_function returns negative for anomalies
            raw_score = self._model.decision_function(X)[0]
            # Convert: more negative = more anomalous = higher risk
            risk = float(max(0.0, min(1.0, -raw_score * 2.0)))
            # Confidence based on how far from decision boundary
            confidence = float(max(0.0, min(1.0, abs(raw_score) * 1.5)))

            return risk, confidence
        except Exception as e:
            logger.error(f"[DDoSAgent] Inference error: {e}")
            return 0.0, 0.0
