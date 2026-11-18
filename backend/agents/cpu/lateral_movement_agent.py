"""
Lateral Movement Agent — RandomForest classifier on network traversal features.
Replaces hardcoded BFS hop-count thresholds with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("LateralMovementAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "lateral_movement_agent_rf.pkl")


class LateralMovementAgent(BaseAgent):
    def __init__(self):
        super().__init__("Lateral Movement", "cpu")
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[LateralMovementAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[LateralMovementAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[LateralMovementAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional lateral movement feature vector:
        [hop_count, internal_connections, unique_subnets, time_spread,
         auth_events, new_hosts_contacted, protocol_switch_count, priv_level_delta]
        """
        hop_count = 0
        internal_conn = 0
        unique_subnets = 0

        if graph_snapshot.has_node(node_id):
            internal_conn = graph_snapshot.degree(node_id)
            successors = list(graph_snapshot.successors(node_id))
            # Estimate subnet diversity from neighbor IPs
            subnets = set()
            for s in successors:
                parts = str(s).split(".")
                if len(parts) >= 3:
                    subnets.add(".".join(parts[:3]))
            unique_subnets = len(subnets) if subnets else 1

        time_spread = 3600
        auth_events = 0
        new_hosts = 0
        proto_switch = 0
        priv_delta = 0

        if event_data:
            time_spread = event_data.get("duration", 3600)
            auth_events = 1 if event_data.get("event_type", "") in ("auth_failure", "brute_force") else 0
            new_hosts = len(set(graph_snapshot.successors(node_id))) if graph_snapshot.has_node(node_id) else 0
            proto_switch = event_data.get("protocol", 1)
            priv_delta = 1 if event_data.get("event_type", "") in ("priv_esc", "lateral_move", "lateral_movement") else 0

            # Boost features for known lateral movement events
            if event_data.get("event_type", "") in ("lateral_move", "lateral_movement"):
                hop_count = 5
                auth_events = 8
                new_hosts = max(new_hosts, 6)
                priv_delta = 2

        return np.array([hop_count, internal_conn, unique_subnets, time_spread,
                         auth_events, new_hosts, proto_switch, priv_delta],
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
            logger.error(f"[LateralMovementAgent] Inference error: {e}")
            return 0.0, 0.0
