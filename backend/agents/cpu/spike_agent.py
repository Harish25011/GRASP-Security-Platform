"""
Spike Agent — IsolationForest anomaly detection on degree time-series features.
Replaces hardcoded Z-score threshold with pre-trained ML model.
"""
import os
import logging
import numpy as np
import joblib
from collections import defaultdict, deque
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("SpikeAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "spike_agent_iforest.pkl")


class SpikeAgent(BaseAgent):
    def __init__(self, window_size=50):
        super().__init__("Spike", "cpu")
        self.history = defaultdict(lambda: deque(maxlen=window_size))
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[SpikeAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[SpikeAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[SpikeAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 5-dimensional spike feature vector:
        [current_degree, rolling_mean, rolling_std, z_score, delta_from_prev]
        """
        degree = graph_snapshot.degree(node_id) if graph_snapshot.has_node(node_id) else 0
        self.history[node_id].append(degree)

        arr = np.array(self.history[node_id], dtype=np.float64)
        rolling_mean = arr.mean() if len(arr) > 0 else 0
        rolling_std = arr.std() if len(arr) > 1 else 0.1
        rolling_std = max(rolling_std, 0.1)  # Prevent division by zero

        z_score = (degree - rolling_mean) / rolling_std
        delta = degree - arr[-2] if len(arr) >= 2 else 0

        return np.array([degree, rolling_mean, rolling_std, z_score, delta],
                        dtype=np.float64).reshape(1, -1)

    def score(self, graph_snapshot, node_id, event_data=None) -> tuple[float, float]:
        if self._model is None:
            return 0.0, 0.0

        try:
            X = self._extract_features(graph_snapshot, node_id, event_data)

            if len(self.history[node_id]) < 5:
                return 0.0, 0.4

            raw_score = self._model.decision_function(X)[0]
            risk = float(max(0.0, min(1.0, -raw_score * 2.0)))
            confidence = float(max(0.0, min(1.0, abs(raw_score) * 1.5)))
            return risk, confidence
        except Exception as e:
            logger.error(f"[SpikeAgent] Inference error: {e}")
            return 0.0, 0.0
