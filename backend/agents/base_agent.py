"""
Abstract base class for all 15 GRASP agents.
Every agent inherits from BaseAgent and implements score().
"""
from abc import ABC, abstractmethod
import time


class BaseAgent(ABC):
    """Base class for all detection agents in GRASP."""
    
    def __init__(self, name: str, agent_type: str = "cpu"):
        self.name = name
        self.agent_type = agent_type  # "cpu" or "gpu"
        self.last_score = 0.0
        self.last_latency_ms = 0.0
        self.total_runs = 0
        self.total_detections = 0
    
    @abstractmethod
    def score(self, graph_snapshot, node_id: str, event_data: dict = None) -> tuple[float, float]:
        """
        Score a node for anomaly.
        Returns tuple (risk_score, confidence) in [0, 1].
        """
        pass
    
    def run(self, graph_snapshot, node_id: str, event_data: dict = None) -> dict:
        """Execute agent with timing wrapper."""
        start = time.perf_counter()
        try:
            score_res = self.score(graph_snapshot, node_id, event_data)
            # Support transition phase where some agents might still return just a float
            if isinstance(score_res, tuple):
                score, confidence = score_res
            else:
                score = score_res
                confidence = 1.0 if score > 0 else 0.5
                
            score = float(max(0.0, min(1.0, score)))  # clamp + native type
            confidence = float(max(0.0, min(1.0, float(confidence))))
        except Exception as e:
            print(f"[Agent:{self.name}] Error: {e}")
            score = 0.0
            confidence = 0.0
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.last_score = score
        self.last_latency_ms = elapsed_ms
        self.total_runs += 1
        if score > 0.5:
            self.total_detections += 1
        
        return {
            "agent": self.name,
            "type": self.agent_type,
            "score": round(score, 4),
            "confidence": round(confidence, 4),
            "latency_ms": round(elapsed_ms, 2),
        }
    
    def get_status(self) -> dict:
        return {
            "name": self.name,
            "type": self.agent_type,
            "last_score": float(self.last_score),
            "last_latency_ms": float(self.last_latency_ms),
            "total_runs": int(self.total_runs),
            "total_detections": int(self.total_detections),
        }
