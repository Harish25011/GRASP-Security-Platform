import os
import torch
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, roc_auc_score, matthews_corrcoef
from torch.utils.data import TensorDataset, DataLoader

def _train_fold(model, X_train, y_train, X_val, y_val, device, epochs, batch_size=64):
    """Trains the model on a single fold and returns validation metrics."""
    # Move model to device
    model = model.to(device)
    
    # Create DataLoaders
    train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    val_ds = TensorDataset(torch.FloatTensor(X_val), torch.FloatTensor(y_val))
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size)
    
    criterion = torch.nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs, _ = model(batch_x)
            loss = criterion(outputs.squeeze(), batch_y)
            loss.backward()
            optimizer.step()
            
    # Validation Phase
    model.eval()
    val_preds = []
    val_true = []
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            batch_x = batch_x.to(device)
            outputs, _ = model(batch_x)
            outputs = outputs.squeeze().cpu().numpy()
            if outputs.ndim == 0:
                outputs = [outputs.item()]
            val_preds.extend(outputs)
            val_true.extend(batch_y.numpy())
            
    val_preds = np.array(val_preds)
    val_true = np.array(val_true)
    
    # Calculate metrics
    pred_labels = (val_preds >= 0.5).astype(int)
    val_f1 = f1_score(val_true, pred_labels, zero_division=0)
    
    # Handle AUC when only one class is present in split (edge case)
    try:
        val_auc = roc_auc_score(val_true, val_preds)
    except ValueError:
        val_auc = 0.5
        
    val_mcc = matthews_corrcoef(val_true, pred_labels)
    
    return {"f1": val_f1, "auc": val_auc, "mcc": val_mcc}

def train(X, y, model, device='cuda', n_splits=5, epochs=50, retrain=False, save_path='backend/checkpoints/grasp_classifier.pt'):
    """
    Complete training pipeline using SMOTE for class imbalance and 5-fold CV.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    print(f"Starting Training Pipeline on {device.upper()}...")
    
    # 1. Handle class imbalance
    print(f"Original dataset shape: {X.shape}. Class distribution: {np.bincount(y.astype(int))}")
    sm = SMOTE(random_state=42)
    # SMOTE expects 2D array, we must ensure X is flat (Samples, Features)
    X_res, y_res = sm.fit_resample(X, y)
    print(f"Resampled dataset shape: {X_res.shape}. Class distribution: {np.bincount(y_res.astype(int))}")
    
    # 2. 5-Fold Cross Validation
    kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    fold_metrics = []
    
    best_f1 = 0.0
    best_state = None
    
    for fold, (tr_idx, val_idx) in enumerate(kf.split(X_res, y_res)):
        print(f"\n--- Fold {fold+1}/{n_splits} ---")
        X_tr, X_val = X_res[tr_idx], X_res[val_idx]
        y_tr, y_val = y_res[tr_idx], y_res[val_idx]
        
        # Train fold
        metrics = _train_fold(model, X_tr, y_tr, X_val, y_val, device, epochs)
        fold_metrics.append(metrics)
        print(f"Fold {fold+1} Metrics: F1={metrics['f1']:.3f} | AUC={metrics['auc']:.3f} | MCC={metrics['mcc']:.3f}")
        
        # Keep track of best model weights
        if metrics["f1"] > best_f1:
            best_f1 = metrics["f1"]
            best_state = model.state_dict()
            
    # 3. Save the best model
    if not retrain or (retrain and best_f1 > 0): # Simplistic checkpointing
        if best_state is not None:
            torch.save(best_state, save_path)
            print(f"\n[+] Model saved to {save_path} with val_f1: {best_f1:.3f}")
    
    avg_f1 = np.mean([m['f1'] for m in fold_metrics])
    avg_auc = np.mean([m['auc'] for m in fold_metrics])
    avg_mcc = np.mean([m['mcc'] for m in fold_metrics])
    
    print(f"\n--- Cross-Validation Summary ({n_splits} folds) ---")
    print(f"Average F1:  {avg_f1:.3f}")
    print(f"Average AUC: {avg_auc:.3f}")
    print(f"Average MCC: {avg_mcc:.3f}")
    
    return {
        "f1": avg_f1,
        "auc": avg_auc,
        "mcc": avg_mcc,
        "fold_metrics": fold_metrics
    }

if __name__ == '__main__':
    # Very simple stub to test syntax and execution
    # Replace with the newly built MultiheadAttention GRASPClassifier in reality
    import torch.nn as nn
    class DummyModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(nn.Linear(34, 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())
        def forward(self, x):
            return self.net(x)
            
    # Create fake data matching the 34-dim new format
    X_dummy = np.random.rand(2000, 34)
    y_dummy = np.random.randint(0, 2, 2000)
    train(X_dummy, y_dummy, DummyModel(), device='cpu', epochs=5)
