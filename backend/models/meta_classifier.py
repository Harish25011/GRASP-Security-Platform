"""GRASPClassifier — 30-dim Attention-MLP."""
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:
    class GRASPClassifier(nn.Module):
        def __init__(self, input_dim=34):
            super().__init__()
            # As explicitly defined by the architectural specs
            self.attn = nn.MultiheadAttention(input_dim, num_heads=2, batch_first=True)
            self.fc1  = nn.Linear(input_dim, 64)
            self.fc2  = nn.Linear(64, 32)
            self.out  = nn.Linear(32, 1)
            self.relu = nn.ReLU()
            self.sig  = nn.Sigmoid()

        def forward(self, x):
            x = x.unsqueeze(1)                   # add seq dim (N, 1, 30)
            attn_out, attn_weights = self.attn(x, x, x)            # self-attention
            x = attn_out.squeeze(1) + x.squeeze(1)   # residual (N, 30)
            
            # Extract the actual contextualized attention dimensions per feature instead of the 1x1 seq weight
            feature_attention = attn_out.squeeze(1) 
            
            x = self.relu(self.fc1(x))
            x = self.relu(self.fc2(x))
            risk = self.sig(self.out(x))
            return risk, feature_attention

        def predict(self, feature_vector: list) -> tuple[float, list]:
            """
            Returns:
                risk_score (float): Final risk classification probability
                attention_weights (list): 34-dimensional list of floats representing attention focus
            """
            x = torch.tensor(feature_vector, dtype=torch.float32).unsqueeze(0)
            if torch.cuda.is_available():
                x = x.cuda()
                self.cuda()
            with torch.no_grad():
                self.eval()
                risk, attn_weights = self(x)
                
                # Normalize attention weights for the heatmap [0, 1] across the 34 features
                attn_list = attn_weights.cpu().numpy()[0]
                # Min-max scaling so we get visible heatmap colors
                rng = (attn_list.max() - attn_list.min())
                if rng > 0:
                    attn_list = (attn_list - attn_list.min()) / rng
                
                return float(risk.item()), attn_list.tolist()
else:
    class GRASPClassifier:
        def __init__(self, *args, **kwargs):
            pass
        def predict(self, feature_vector):
            return 0.5, [0.0] * 34

MetaClassifier = GRASPClassifier
