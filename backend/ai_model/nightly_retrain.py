"""
APScheduler job script executed automatically at 2:00 AM.
Ingests analyst feedback and intelligently overlays it with training logs to retrain the core MLP classifier.
"""
import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime

from backend.ai_model.train import train
from backend.models.meta_classifier import MetaClassifier
from backend.api.websocket import manager

logger = logging.getLogger("nightly_retrain")

FEEDBACK_LOG_PATH = "backend/data/feedback_log.csv"
VECTORS_PATH = "backend/data/vectors.npz"
HISTORY_PATH = "backend/checkpoints/training_history.json"
CKPT_PATH = "backend/checkpoints/grasp_classifier.pt"

async def run_nightly_retrain():
    logger.info("[ Nightly Retrain ] Beginning scheduled job...")
    
    # 1. Load Feedback Data
    if not os.path.exists(FEEDBACK_LOG_PATH):
        logger.info("[ Nightly Retrain ] Skipped: No feedback log exists.")
        return

    try:
        feedback_df = pd.read_csv(FEEDBACK_LOG_PATH)
        if len(feedback_df) < 50:
            logger.info(f"[ Nightly Retrain ] Skipped: Insufficient feedback samples ({len(feedback_df)} < 50).")
            return
            
        # Assumes feedback_log.csv columns: 
        # event_id, timestamp, f1, f2 ... f34, true_label, analyst_id
        feature_cols = [c for c in feedback_df.columns if c.startswith('f')] 
        if len(feature_cols) != 34:
            logger.error("[ Nightly Retrain ] Error: Feedback features do not match the 34-dim expectation.")
            return
            
        X_feedback = feedback_df[feature_cols].values
        y_feedback = feedback_df['true_label'].values
        
    except Exception as e:
        logger.error(f"[ Nightly Retrain ] Failed to load feedback logs: {e}")
        return

    # 2. Combine with historical vectors limit 70% original / 30% feedback 
    # For now, if vectors.npz doesn't exist, we fall back to just feedback.
    X_train = X_feedback
    y_train = y_feedback
    
    if os.path.exists(VECTORS_PATH):
        try:
            data = np.load(VECTORS_PATH)
            X_orig, y_orig = data['X'], data['y']
            
            # Simple blending: take up to 70% original 
            max_orig = int((len(X_feedback) / 0.3) * 0.7)
            idx = np.random.choice(len(X_orig), min(len(X_orig), max_orig), replace=False)
            
            X_train = np.vstack([X_orig[idx], X_feedback])
            y_train = np.concatenate([y_orig[idx], y_feedback])
        except Exception as e:
            logger.warning(f"[ Nightly Retrain ] Could not blend original vectors: {e}")
    
    logger.info(f"[ Nightly Retrain ] Training on {len(X_train)} assembled samples.")
    
    # 3. Retrain using existing logic
    model = MetaClassifier()
    # It auto-binds to SMOTE and Stratified K-Fold inside
    results = train(X_train, y_train, model, device="cpu", n_splits=5, epochs=50, retrain=True, save_path=CKPT_PATH)
    
    new_f1 = results["f1"]
    new_auc = results["auc"]
    
    # 4. Compare vs History
    improved = False
    hist_f1 = 0.0
    
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                history = json.load(f)
            hist_f1 = history.get("best_f1", 0.0)
        except:
            pass

    if new_f1 > hist_f1:
        improved = True
        logger.info(f"[ Nightly Retrain ] Model improved! F1: {hist_f1:.3f} -> {new_f1:.3f}. Updating Checkpoint.")
        with open(HISTORY_PATH, "w") as f:
            json.dump({"best_f1": new_f1, "best_auc": new_auc, "last_retrain": datetime.now().isoformat()}, f)
    else:
        logger.info(f"[ Nightly Retrain ] Model did not improve past F1 {hist_f1:.3f}. Keeping previous model.")
    
    # 5. Broadcast payload to UI
    payload = {
        "type": "model_updated",
        "improved": improved,
        "new_f1": round(new_f1, 4),
        "new_auc": round(new_auc, 4),
        "feedback_samples_used": len(X_feedback),
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        await manager.broadcast(json.dumps(payload))
    except Exception as e:
        logger.error(f"[ Nightly Retrain ] Missing websocket manager active connection for broadcast: {e}")
