"""Attack LSTM — sequential pattern detector for multi-stage attacks."""
import torch
import torch.nn as nn


class AttackLSTM(nn.Module):
    """
    LSTM-based temporal sequence classifier.
    Input: sliding window of 50 event feature vectors (34-dim each).
    Output: probability of ongoing multi-stage attack (APT).
    """
    def __init__(self, input_dim=34, hidden_dim=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2,
        )
        self.fc = nn.Linear(hidden_dim, 1)
        self.sig = nn.Sigmoid()

    def forward(self, x):
        """
        x: (batch, seq_len, input_dim) e.g. (N, 50, 34)
        returns: (batch, 1) risk probability
        """
        _, (hn, _) = self.lstm(x)
        # Use last layer hidden state
        return self.sig(self.fc(hn[-1]))

    def predict_risk(self, x: torch.Tensor) -> float:
        """Single inference: return risk probability."""
        self.eval()
        with torch.no_grad():
            output = self.forward(x.unsqueeze(0) if x.dim() == 2 else x)
            return output.squeeze().item()
