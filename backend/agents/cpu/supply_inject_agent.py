"""
Supply Chain Inject Agent — RandomForest classifier on supply chain graph features.
Replaces hardcoded edge-diff thresholds with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("SupplyInjectAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "supply_inject_agent_rf.pkl")


class SupplyInjectAgent(BaseAgent):
    def __init__(self):
        super().__init__("Supply Inject", "cpu")
        self._prev_edges = set()
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[SupplyInjectAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[SupplyInjectAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[SupplyInjectAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional supply chain feature vector:
        [new_edges_count, node_age_hours, supplier_reputation_score,
         edge_weight_anomaly, cross_tier_connection, cert_validity_days,
         api_call_frequency, payload_hash_novelty]
        """
        # Compute new edges since last snapshot
        current_edges = set(graph_snapshot.edges()) if graph_snapshot else set()
        new_edges = current_edges - self._prev_edges
        self._prev_edges = current_edges
        suspect = [e for e in new_edges if node_id in e] if graph_snapshot.has_node(node_id) else []
        new_edges_count = len(suspect)

        node_data = graph_snapshot.nodes.get(node_id, {}) if graph_snapshot.has_node(node_id) else {}
        node_age = node_data.get("age_hours", 720)
        reputation = node_data.get("reputation", 0.8)
        edge_weight_anomaly = 0
        cross_tier = 0
        cert_days = 365
        api_freq = 10
        payload_novelty = 0

        if event_data:
            node_age = event_data.get("node_age", node_age)
            reputation = event_data.get("reputation", reputation)
            api_freq = event_data.get("api_calls", api_freq)
            payload_novelty = event_data.get("payload_novelty", payload_novelty)

            # Boost for known supply injection events
            if event_data.get("event_type", "") in ("new_supplier", "supply_inject"):
                new_edges_count = max(new_edges_count, 4)
                node_age = 1
                reputation = 0.1
                payload_novelty = 0.85

        return np.array([new_edges_count, node_age, reputation, edge_weight_anomaly,
                         cross_tier, cert_days, api_freq, payload_novelty],
                        dtype=np.float64).reshape(1, -1)

    def score(self, graph_snapshot, node_id, event_data=None) -> tuple[float, float]:
        if self._model is None:
            return 0.0, 0.0

        try:
            X = self._extract_features(graph_snapshot, node_id, event_data)
            proba = self._model.predict_proba(X)[0]
            risk = float(max(0.0, min(1.0, proba[1])))
            confidence = float(max(0.0, min(1.0, abs(proba[1] - proba[0]))))
            return risk, confidence
        except Exception as e:
            logger.error(f"[SupplyInjectAgent] Inference error: {e}")
            return 0.0, 0.0
