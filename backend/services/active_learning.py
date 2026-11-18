"""
Active Learning - identifies borderline cases for analyst review.
When the model is uncertain (score near 0.5), it flags cases for
human review, which feeds back into the nightly retraining pipeline.
"""
import os
import csv
import time
import logging

logger = logging.getLogger("active_learning")

FEEDBACK_PATH = os.path.join("backend", "data", "feedback_log.csv")


class ActiveLearner:
    """Identifies borderline cases for analyst review."""

    UNCERTAINTY_THRESHOLD = 0.15  # Score within 0.5 +/- 0.15

    def should_request_feedback(self, risk_score: float) -> bool:
        """True if score is near the decision boundary (0.5 +/- threshold)."""
        distance_from_boundary = abs(risk_score - 0.5)
        return distance_from_boundary < self.UNCERTAINTY_THRESHOLD

    def generate_feedback_request(self, node_id: str, risk_score: float,
                                   top_agents: list) -> dict:
        """Generate a feedback request for the analyst."""
        agent_str = ", ".join(
            f"{a['agent']}={a['score']:.2f}" for a in top_agents[:3]
        ) if top_agents else "none"

        return {
            "node_id": node_id,
            "risk_score": round(risk_score, 4),
            "question": "Is this node malicious or benign?",
            "context": f"Top agents: {agent_str}",
            "priority": "high" if risk_score > 0.4 else "medium",
            "timestamp": time.time(),
        }

    def submit_feedback(self, node_id: str, label: int,
                        risk_score: float, agent_scores: dict) -> bool:
        """
        Store analyst feedback for nightly retraining.
        label: 1 = malicious, 0 = benign
        """
        try:
            file_exists = os.path.exists(FEEDBACK_PATH)
            with open(FEEDBACK_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        "timestamp", "node_id", "label", "risk_score",
                        "agent_scores"
                    ])
                writer.writerow([
                    time.strftime("%Y-%m-%d %H:%M:%S"),
                    node_id,
                    label,
                    round(risk_score, 4),
                    str(agent_scores),
                ])
            logger.info(
                f"[ActiveLearning] Feedback stored: {node_id} -> "
                f"{'malicious' if label else 'benign'}"
            )
            return True
        except Exception as e:
            logger.error(f"[ActiveLearning] Failed to store feedback: {e}")
            return False

    def get_feedback_count(self) -> int:
        """Count total feedback entries."""
        if not os.path.exists(FEEDBACK_PATH):
            return 0
        try:
            with open(FEEDBACK_PATH) as f:
                return sum(1 for _ in f) - 1  # Subtract header
        except Exception:
            return 0


# Singleton
active_learner = ActiveLearner()
