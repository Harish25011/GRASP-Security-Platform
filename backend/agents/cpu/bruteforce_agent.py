"""
Brute Force Agent — RandomForest classifier on authentication failure patterns.
Replaces hardcoded exponential decay counters with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from collections import defaultdict, deque
import time
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("BruteForceAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "brute_force_agent_rf.pkl")


class BruteForceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Brute Force", "cpu")
        self._model = None
        # Sliding window for temporal feature extraction
        self._auth_history = defaultdict(lambda: deque(maxlen=200))
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[BruteForceAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[BruteForceAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[BruteForceAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional brute force feature vector:
        [auth_failures, auth_rate, unique_usernames, lockout_count,
         time_between_attempts, password_entropy_avg, geo_distance, success_ratio]
        """
        now = time.time()

        # Track auth events in sliding window
        if event_data and event_data.get("event_type", "") in (
            "auth_failure", "login_failed", "brute_force", "BRUTE_FORCE"
        ):
            self._auth_history[node_id].append(now)

        recent = [t for t in self._auth_history[node_id] if now - t < 60]
        auth_failures = len(recent)
        auth_rate = auth_failures / 60.0 if auth_failures > 0 else 0

        # Time between attempts
        if len(recent) >= 2:
            intervals = np.diff(sorted(recent))
            time_between = float(np.mean(intervals)) if len(intervals) > 0 else 60
        else:
            time_between = 60

        unique_usernames = 1
        lockout_count = 0
        password_entropy = 4.0
        geo_distance = 0
        success_ratio = 0.9

        if event_data:
            unique_usernames = event_data.get("unique_usernames", 1)
            lockout_count = event_data.get("lockouts", 0)
            password_entropy = event_data.get("password_entropy", 4.0)
            geo_distance = event_data.get("geo_distance", 0)
            success_ratio = event_data.get("success_ratio", 0.9)

            # Boost for known brute force event types
            if event_data.get("event_type", "") in ("brute_force", "BRUTE_FORCE"):
                auth_failures = max(auth_failures, 30)
                auth_rate = max(auth_rate, 5.0)
                time_between = min(time_between, 0.5)
                success_ratio = 0.02

        return np.array([auth_failures, auth_rate, unique_usernames, lockout_count,
                         time_between, password_entropy, geo_distance, success_ratio],
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
            logger.error(f"[BruteForceAgent] Inference error: {e}")
            return 0.0, 0.0
