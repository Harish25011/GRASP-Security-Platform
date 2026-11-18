"""Anomaly Autoencoder — reconstruction-error based zero-day detection."""
import torch
import torch.nn as nn


class AnomalyAutoencoder(nn.Module):
    """
    Encoder-Decoder architecture trained on BENIGN-only traffic.
    High reconstruction error → unseen attack pattern → potential zero-day.
    """
    def __init__(self, input_dim=34):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

    def anomaly_score(self, x: torch.Tensor) -> float:
        """Compute reconstruction error as anomaly score."""
        self.eval()
        with torch.no_grad():
            reconstruction = self.forward(x)
            mse = torch.mean((x - reconstruction) ** 2, dim=-1)
            return mse.item() if mse.dim() == 0 else mse.squeeze().item()
