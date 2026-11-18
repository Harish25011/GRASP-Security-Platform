"""
Behavior Agent — IsolationForest anomaly detection on sliding window features.
Replaces per-request IsolationForest fitting with a pre-trained persistent model.
"""
import os
import logging
import threading
import numpy as np
import joblib
from collections import defaultdict, deque
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("BehaviorAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "behavior_agent_iforest.pkl")


class BehaviorAgent(BaseAgent):
    def __init__(self, window_size=50):
        super().__init__("Behavior", "cpu")
        self._lock = threading.Lock()
        self.windows = defaultdict(lambda: deque(maxlen=window_size))
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[BehaviorAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[BehaviorAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[BehaviorAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 5-dimensional behavioral feature vector:
        [in_degree, out_degree, bytes_out, bytes_in, out_in_ratio]
        """
        in_d = graph_snapshot.in_degree(node_id) if graph_snapshot.has_node(node_id) else 0
        out_d = graph_snapshot.out_degree(node_id) if graph_snapshot.has_node(node_id) else 0

        out_b, in_b = 0, 0
        if graph_snapshot.has_node(node_id):
            out_b = sum(d.get("bytes_sent", 0) for _, _, d in graph_snapshot.out_edges(node_id, data=True))
            in_b = sum(d.get("bytes_recv", 0) for _, _, d in graph_snapshot.in_edges(node_id, data=True))

        # Enrich from event data
        if event_data:
            out_b = max(out_b, event_data.get("bytes_sent", 0))
            in_b = max(in_b, event_data.get("bytes_recv", 0))
            in_d = max(in_d, event_data.get("size", 0) // 100)

        ratio = out_b / max(in_b, 1)
        return np.array([in_d, out_d, out_b, in_b, ratio], dtype=np.float64)

    def score(self, graph_snapshot, node_id, event_data=None) -> tuple[float, float]:
        if self._model is None:
            return 0.0, 0.0

        try:
            features = self._extract_features(graph_snapshot, node_id, event_data)

            with self._lock:
                self.windows[node_id].append(features)
                if len(self.windows[node_id]) < 5:
                    return 0.0, 0.4

            X = features.reshape(1, -1)
            raw_score = self._model.decision_function(X)[0]
            risk = float(max(0.0, min(1.0, -raw_score * 2.0)))
            confidence = float(max(0.0, min(1.0, abs(raw_score) * 1.5)))
            return risk, confidence
        except Exception as e:
            logger.error(f"[BehaviorAgent] Inference error: {e}")
            return 0.0, 0.0
