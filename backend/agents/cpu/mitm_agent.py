"""
MITM Agent — RandomForest classifier on path interception features.
Replaces hardcoded shortest-path comparison with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("MITMAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "mitm_agent_rf.pkl")


class MITMAgent(BaseAgent):
    def __init__(self):
        super().__init__("MITM", "cpu")
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[MITMAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[MITMAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[MITMAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional MITM feature vector:
        [path_deviation, direct_edge_exists, betweenness_centrality,
         arp_mismatch_count, cert_chain_length, tls_downgrade_flag,
         duplicate_mac_count, packet_delay_variance]
        """
        path_deviation = 0
        direct_edge = 0
        betweenness = 0
        preds_count = 0
        succs_count = 0

        if graph_snapshot.has_node(node_id):
            preds = list(graph_snapshot.predecessors(node_id))
            succs = list(graph_snapshot.successors(node_id))
            preds_count = len(preds)
            succs_count = len(succs)

            # If node sits between many preds and succs, it's suspicious
            if preds_count > 0 and succs_count > 0:
                # Check if direct edges exist between preds and succs
                for p in preds[:3]:
                    for s in succs[:3]:
                        if graph_snapshot.has_edge(p, s):
                            direct_edge += 1
                            path_deviation += 1

            total_nodes = graph_snapshot.number_of_nodes()
            betweenness = (preds_count * succs_count) / max(total_nodes, 1)

        arp_mismatch = 0
        cert_chain = 3
        tls_downgrade = 0
        dup_mac = 0
        delay_var = 1

        if event_data:
            arp_mismatch = event_data.get("arp_mismatches", 0)
            cert_chain = event_data.get("cert_chain_len", 3)
            tls_downgrade = 1 if event_data.get("tls_downgrade", False) else 0
            dup_mac = event_data.get("duplicate_macs", 0)
            delay_var = event_data.get("delay_variance", 1)

            # Boost for known MITM events
            if event_data.get("event_type", "") in ("route_hijack", "arp_spoof", "mitm"):
                path_deviation = max(path_deviation, 3)
                arp_mismatch = max(arp_mismatch, 5)
                tls_downgrade = 1
                dup_mac = max(dup_mac, 3)
                delay_var = 10

        return np.array([path_deviation, direct_edge, betweenness, arp_mismatch,
                         cert_chain, tls_downgrade, dup_mac, delay_var],
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
            logger.error(f"[MITMAgent] Inference error: {e}")
            return 0.0, 0.0
