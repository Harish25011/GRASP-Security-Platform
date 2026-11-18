"""
Port Scan Agent — RandomForest classifier on network reconnaissance features.
Replaces hardcoded successor-count thresholds with pre-trained supervised model.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("PortScanAgent")
CHECKPOINT = os.path.join("backend", "checkpoints", "port_scan_agent_rf.pkl")


class PortScanAgent(BaseAgent):
    def __init__(self):
        super().__init__("Port Scan", "cpu")
        self._model = None
        try:
            if os.path.exists(CHECKPOINT):
                self._model = joblib.load(CHECKPOINT)
                logger.info(f"[PortScanAgent] Loaded model from {CHECKPOINT}")
            else:
                logger.warning(f"[PortScanAgent] Checkpoint not found: {CHECKPOINT}")
        except Exception as e:
            logger.error(f"[PortScanAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> np.ndarray:
        """
        Extract 8-dimensional port scan feature vector:
        [unique_targets, unique_ports, scan_rate, syn_only_ratio,
         avg_pkt_size, rst_ratio, total_connections, connection_failures]
        """
        unique_targets = 0
        total_conn = 0
        if graph_snapshot.has_node(node_id):
            unique_targets = len(set(graph_snapshot.successors(node_id)))
            total_conn = graph_snapshot.out_degree(node_id)

        unique_ports = 0
        scan_rate = 0
        syn_ratio = 0.1
        avg_pkt_size = 512
        rst_ratio = 0.05
        conn_failures = 0

        if event_data:
            unique_ports = event_data.get("unique_ports", unique_targets * 5)
            scan_rate = event_data.get("flood_rate", total_conn)
            flags = str(event_data.get("flags", ""))
            syn_ratio = 0.9 if flags == "S" else 0.1
            avg_pkt_size = event_data.get("size", 512)
            rst_ratio = 0.7 if event_data.get("event_type", "").upper() in ("PORT_SCAN",) else 0.05
            conn_failures = int(total_conn * rst_ratio)

            # Boost for known port scan event types
            if event_data.get("event_type", "").upper() in ("PORT_SCAN",):
                unique_ports = max(unique_ports, 50)
                scan_rate = max(scan_rate, 80)

        return np.array([unique_targets, unique_ports, scan_rate, syn_ratio,
                         avg_pkt_size, rst_ratio, total_conn, conn_failures],
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
            logger.error(f"[PortScanAgent] Inference error: {e}")
            return 0.0, 0.0
