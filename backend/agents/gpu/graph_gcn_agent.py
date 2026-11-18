"""Graph GCN Agent — Uses trained GCNModel for node-level classification."""
import os
import numpy as np
from backend.agents.base_agent import BaseAgent


class GraphGCNAgent(BaseAgent):
    def __init__(self):
        super().__init__("Graph GCN", "gpu")
        self._model = None
        self._device = "cpu"
        self._load_model()

    def _load_model(self):
        try:
            import torch
            from backend.models.gcn_model import GCNModel

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = GCNModel(in_features=7, hidden=64, out_features=2)

            ckpt_path = os.path.join('backend', 'checkpoints', 'gcn_model.pt')
            if os.path.exists(ckpt_path):
                state = torch.load(ckpt_path, map_location=self._device,
                                   weights_only=True)
                self._model.load_state_dict(state)
                self._model.eval()
                self._model.to(self._device)
                print("[GraphGCNAgent] Loaded gcn_model.pt successfully")
            else:
                print("[GraphGCNAgent] No checkpoint found, using random weights")

        except ImportError:
            print("[GraphGCNAgent] PyTorch not available, using numpy fallback")

    def score(self, graph_snapshot, node_id, event_data=None):
        if not graph_snapshot.has_node(node_id):
            return 0.0, 0.0

        features = graph_snapshot.nodes[node_id].get("features", [])
        if not features or len(features) < 7:
            features = [0.0] * 7

        # Attempt inference with the trained GCN model
        if self._model is not None:
            try:
                import torch
                x = torch.tensor(features[:7], dtype=torch.float32) \
                         .unsqueeze(0).to(self._device)
                with torch.no_grad():
                    output = self._model(x)
                    # output is log_softmax: [log_prob_benign, log_prob_malicious]
                    probs = torch.exp(output)
                    malicious_prob = probs[0, 1].item()
                    confidence = abs(malicious_prob - 0.5) * 2.0
                    return min(1.0, max(0.0, malicious_prob)), confidence
            except Exception:
                pass

        # Fallback: numpy-based sigmoid anomaly detection
        arr = np.array(features[:7], dtype=np.float32)
        mean, std = arr.mean(), arr.std()
        if std == 0:
            return 0.0, 0.5
        z = (arr.max() - mean) / std
        anomaly = 1 / (1 + np.exp(-z + 1))
        confidence = abs(anomaly - 0.5) * 2.0
        return min(1.0, max(0.0, anomaly)), confidence
