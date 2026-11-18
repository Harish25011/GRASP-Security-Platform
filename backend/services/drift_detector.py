"""
Drift Detector - monitors model performance degradation over time.
Tracks predictions vs actual outcomes and alerts when F1 drops below threshold.
"""
import logging

logger = logging.getLogger("drift_detector")


class DriftDetector:
    """Monitors model performance over time and detects concept drift."""

    def __init__(self, window_size: int = 100, f1_threshold: float = 0.75):
        self.predictions = []
        self.actuals = []
        self.window = window_size
        self.f1_threshold = f1_threshold
        self.drift_events = []

    def add_sample(self, predicted: float, actual: int):
        """Record a prediction-actual pair."""
        self.predictions.append(predicted)
        self.actuals.append(actual)

    def check_drift(self) -> dict:
        """Check if model performance has degraded."""
        if len(self.predictions) < self.window:
            return {
                "drift": False,
                "reason": f"Insufficient data ({len(self.predictions)}/{self.window})",
                "samples": len(self.predictions),
            }

        recent_preds = self.predictions[-self.window:]
        recent_actual = self.actuals[-self.window:]

        # Calculate recent F1
        pred_labels = [1 if p > 0.5 else 0 for p in recent_preds]
        tp = sum(1 for p, a in zip(pred_labels, recent_actual) if p == 1 and a == 1)
        fp = sum(1 for p, a in zip(pred_labels, recent_actual) if p == 1 and a == 0)
        fn = sum(1 for p, a in zip(pred_labels, recent_actual) if p == 0 and a == 1)
        tn = sum(1 for p, a in zip(pred_labels, recent_actual) if p == 0 and a == 0)

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 0.001)
        accuracy = (tp + tn) / max(len(pred_labels), 1)
        fp_rate = fp / max(fp + tn, 1)

        is_drift = f1 < self.f1_threshold

        if is_drift:
            import time
            self.drift_events.append({
                "time": time.time(),
                "f1": f1,
                "fp_rate": fp_rate,
            })
            logger.warning(
                f"[DriftDetector] DRIFT DETECTED: F1={f1:.3f} "
                f"(threshold={self.f1_threshold})"
            )

        return {
            "drift": is_drift,
            "f1": round(f1, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "accuracy": round(accuracy, 4),
            "fp_rate": round(fp_rate, 4),
            "window_size": len(recent_preds),
            "total_samples": len(self.predictions),
            "drift_events": len(self.drift_events),
        }

    def get_performance_history(self, last_n: int = 10) -> list:
        """Get performance metrics over rolling windows."""
        if len(self.predictions) < self.window:
            return []

        history = []
        step = max(1, self.window // 5)
        for i in range(self.window, len(self.predictions) + 1, step):
            window_preds = self.predictions[i - self.window:i]
            window_actual = self.actuals[i - self.window:i]

            pred_labels = [1 if p > 0.5 else 0 for p in window_preds]
            tp = sum(1 for p, a in zip(pred_labels, window_actual) if p == 1 and a == 1)
            fp = sum(1 for p, a in zip(pred_labels, window_actual) if p == 1 and a == 0)
            fn = sum(1 for p, a in zip(pred_labels, window_actual) if p == 0 and a == 1)

            precision = tp / max(tp + fp, 1)
            recall = tp / max(tp + fn, 1)
            f1 = 2 * precision * recall / max(precision + recall, 0.001)

            history.append({
                "window_end": i,
                "f1": round(f1, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
            })

        return history[-last_n:]

    def reset(self):
        """Reset after model retraining."""
        self.predictions.clear()
        self.actuals.clear()
        self.drift_events.clear()
        logger.info("[DriftDetector] Reset after model retrain")


# Singleton
drift_detector = DriftDetector()
