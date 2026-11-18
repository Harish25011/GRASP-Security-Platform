"""GraphSAGE GCN model definition."""
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

if TORCH_AVAILABLE:
    class GCNModel(nn.Module):
        def __init__(self, in_features=7, hidden=64, out_features=2):
            super().__init__()
            self.conv1 = nn.Linear(in_features, hidden)
            self.conv2 = nn.Linear(hidden, hidden // 2)
            self.classifier = nn.Linear(hidden // 2, out_features)
            self.dropout = nn.Dropout(0.3)

        def forward(self, x):
            x = F.relu(self.conv1(x))
            x = self.dropout(x)
            x = F.relu(self.conv2(x))
            x = self.classifier(x)
            return F.log_softmax(x, dim=-1)

        def get_embedding(self, x):
            x = F.relu(self.conv1(x))
            x = F.relu(self.conv2(x))
            return x
else:
    class GCNModel:
        def __init__(self, *args, **kwargs):
            pass
        def forward(self, x):
            return x
        def get_embedding(self, x):
            return x
