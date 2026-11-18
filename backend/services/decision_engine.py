import os
import torch
from backend.models.meta_classifier import MetaClassifier
from backend.services.bayesian_fusion import compute_ensemble_risk

class DecisionEngine:
    """Routes nodes based on strictly defined risk score tiers and invokes the ML Classifier."""
    
    THRESHOLDS = {
        'critical':    0.70,   # quarantine immediately
        'suspicious':  0.50,   # flag and monitor
        'watch':       0.30,   # log only
    }
    
    def __init__(self):
        self.classifier = MetaClassifier()
        ckpt_path = 'backend/checkpoints/grasp_classifier.pt'
        if os.path.exists(ckpt_path):
            try:
                if torch.cuda.is_available():
                    self.classifier.load_state_dict(torch.load(ckpt_path))
                else:
                    self.classifier.load_state_dict(torch.load(ckpt_path, map_location=torch.device('cpu')))
            except Exception as e:
                print(f"[DecisionEngine] Model checkpoint load failed: {e}")
        self.classifier.eval()

    def evaluate(self, node_id: str, agent_results: dict) -> dict:
        """Evaluate risk using the 30-dimensional Attention-MLP + Bayesian fusion."""
        feature_vector = agent_results.get("feature_vector", [0.0] * 34)
        
        # ML Inference (Attention-MLP Meta-Classifier)
        risk_score, attention_weights = self.classifier.predict(feature_vector)
        
        # Phase 4: Bayesian Fusion — ensemble of multiple scoring methods
        ensemble = compute_ensemble_risk(agent_results)
        bayesian_score = ensemble.get("bayesian_score", risk_score)
        
        # Final risk: blend ML prediction (60%) with Bayesian fusion (40%)
        final_risk = risk_score * 0.6 + bayesian_score * 0.4
        
        if final_risk >= self.THRESHOLDS['critical']:
            action = "quarantine"
            severity = "critical"
            tier = "CRITICAL"
        elif final_risk >= self.THRESHOLDS['suspicious']:
            action = "alert"
            severity = "high"
            tier = "SUSPICIOUS"
        elif final_risk >= self.THRESHOLDS['watch']:
            action = "watch"
            severity = "medium"
            tier = "WATCH"
        else:
            action = "normal"
            severity = "low"
            tier = "NORMAL"
        
        # Determine the top contributing features
        scores = agent_results.get("scores", {})
        top_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "node_id": node_id,
            "risk_score": round(final_risk, 4),
            "ml_risk_score": round(risk_score, 4),
            "bayesian_score": round(bayesian_score, 4),
            "ensemble": ensemble,
            "action": action,
            "severity": severity,
            "tier": tier,
            "attention_weights": attention_weights,
            "top_agents": [{"agent": a, "score": round(s, 4)} for a, s in top_agents],
            "agent_count_fired": agent_results.get("agents_fired", 0),
            "correlation_score": agent_results.get("correlation_score", 0.0),
        }

