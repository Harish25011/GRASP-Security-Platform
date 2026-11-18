import sys
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.models.gcn_model import GCNModel

def train_gcn():
    print("Training GCNModel (GraphSAGE)...")
    
    # Check if vectors.npz exists from our initial_train.py
    vectors_path = 'backend/data/vectors.npz'
    if not os.path.exists(vectors_path):
        print("Vectors not found. Run initial_train.py first.")
        return
        
    data = np.load(vectors_path)
    X = torch.tensor(data['X'], dtype=torch.float32)
    y = torch.tensor(data['y'], dtype=torch.long)
    
    # The GCNModel expects 7 input features by default:
    # class GCNModel(nn.Module):
    #     def __init__(self, in_features=7, hidden=64, out_features=2):
    
    # Our vectors have 34 dimensions. We'll slice the first 7 features just for the sake of 
    # demonstration, mimicking node-level graph features (like degrees, centrality, etc.)
    X_gcn = X[:, :7]
    
    model = GCNModel(in_features=7, hidden=64, out_features=2)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = model.to(device)
    X_gcn = X_gcn.to(device)
    y = y.to(device)
    
    criterion = nn.NLLLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    
    model.train()
    epochs = 50
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(X_gcn)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            # Calculate accuracy
            _, pred = out.max(dim=1)
            correct = int(pred.eq(y).sum().item())
            acc = correct / len(y)
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}, Accuracy: {acc:.4f}')
            
    os.makedirs('backend/checkpoints', exist_ok=True)
    save_path = 'backend/checkpoints/gcn_model.pt'
    torch.save(model.state_dict(), save_path)
    print(f"DONE! GCNModel checkpoint saved to {save_path}")

if __name__ == '__main__':
    train_gcn()
