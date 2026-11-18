"""
Privilege Escalation Agent — RandomForest classifier on RBAC violation features.
Replaces hardcoded RBAC baseline lookup with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("PrivEscalationAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "priv_escalation_agent_rf.pkl")


class PrivEscalationAgent(BaseAgent):
    def __init__(self):
        super().__init__("Priv Escalation", "cpu")
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[PrivEscalationAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[PrivEscalationAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[PrivEscalationAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional privilege escalation feature vector:
        [rbac_violations, out_degree, target_criticality, role_change_count,
         admin_api_calls, sudo_events, new_permissions_granted, time_since_last_role_change]
        """
        rbac_violations = 0
        out_degree = 0
        target_criticality = 2

        if graph_snapshot.has_node(node_id):
            out_degree = graph_snapshot.out_degree(node_id)
            # Estimate RBAC violations from cross-type edges
            node_type = graph_snapshot.nodes[node_id].get("node_type", "Unknown")
            for _, target in graph_snapshot.out_edges(node_id):
                t_type = graph_snapshot.nodes.get(target, {}).get("node_type", "Unknown")
                if t_type != "Unknown" and node_type != "Unknown":
                    rbac_violations += 1  # Simplified: treat each edge as potential
            target_criticality = 9 if node_type in ("Hospital", "Pharmacy") else 3

        role_changes = 0
        admin_calls = 0
        sudo_events = 0
        new_perms = 0
        time_since_role = 720

        if event_data:
            role_changes = event_data.get("role_changes", 0)
            admin_calls = event_data.get("admin_calls", 0)
            sudo_events = event_data.get("sudo_events", 0)
            new_perms = event_data.get("new_permissions", 0)

            # Boost for known priv escalation events
            if event_data.get("event_type", "") in ("role_change", "priv_esc"):
                rbac_violations = max(rbac_violations, 4)
                role_changes = max(role_changes, 3)
                admin_calls = max(admin_calls, 15)
                sudo_events = max(sudo_events, 4)
                time_since_role = 1

        return np.array([rbac_violations, out_degree, target_criticality, role_changes,
                         admin_calls, sudo_events, new_perms, time_since_role],
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
            logger.error(f"[PrivEscalationAgent] Inference error: {e}")
            return 0.0, 0.0
