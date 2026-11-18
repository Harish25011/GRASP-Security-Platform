"""
Exfiltration Agent — RandomForest classifier on outbound data patterns.
Replaces hardcoded byte-ratio thresholds with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("ExfiltrationAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "exfiltration_agent_rf.pkl")


class ExfiltrationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Exfiltration", "cpu")
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[ExfiltrationAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[ExfiltrationAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[ExfiltrationAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional exfiltration feature vector:
        [bytes_out, bytes_in, out_in_ratio, unique_dst_ips, avg_payload_size,
         session_duration, out_degree, protocol_diversity]
        """
        bytes_out, bytes_in = 0, 0
        out_degree = 0
        unique_dst = 0

        if graph_snapshot.has_node(node_id):
            bytes_out = sum(d.get("bytes_sent", 0) for _, _, d in graph_snapshot.out_edges(node_id, data=True))
            bytes_in = sum(d.get("bytes_recv", 0) for _, _, d in graph_snapshot.in_edges(node_id, data=True))
            out_degree = graph_snapshot.out_degree(node_id)
            unique_dst = len(set(graph_snapshot.successors(node_id)))

        if event_data:
            bytes_out = max(bytes_out, event_data.get("bytes_sent", event_data.get("size", 0)))
            bytes_in = max(bytes_in, event_data.get("bytes_recv", 0))

        ratio = bytes_out / max(bytes_in, 1)
        avg_payload = bytes_out / max(out_degree, 1)
        session_dur = event_data.get("duration", 30) if event_data else 30
        proto_div = event_data.get("protocol", 1) if event_data else 1

        return np.array([bytes_out, bytes_in, ratio, unique_dst, avg_payload,
                         session_dur, out_degree, proto_div],
                        dtype=np.float64).reshape(1, -1)

    def score(self, graph_snapshot, node_id, event_data=None) -> tuple[float, float]:
        if self._model is None:
            return 0.0, 0.0

        try:
            X = self._extract_features(graph_snapshot, node_id, event_data)
            proba = self._model.predict_proba(X)[0]
            risk = float(max(0.0, min(1.0, proba[1])))  # P(attack)
            confidence = float(max(0.0, min(1.0, abs(proba[1] - proba[0]))))
            return risk, confidence
        except Exception as e:
            logger.error(f"[ExfiltrationAgent] Inference error: {e}")
            return 0.0, 0.0
