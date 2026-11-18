"""
Signature Agent — TF-IDF + LogisticRegression NLP classifier on payload signatures.
Replaces hardcoded regex pattern dictionaries with pre-trained NLP pipeline.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("SignatureAgent")
VECTORIZER_PATH = os.path.join("backend", "checkpoints", "signature_agent_vectorizer.pkl")
CLASSIFIER_PATH = os.path.join("backend", "checkpoints", "signature_agent_tfidf.pkl")


class SignatureAgent(BaseAgent):
    def __init__(self):
        super().__init__("Signature", "cpu")
        self._vectorizer = None
        self._classifier = None
        try:
            if os.path.exists(VECTORIZER_PATH) and os.path.exists(CLASSIFIER_PATH):
                self._vectorizer = joblib.load(VECTORIZER_PATH)
                self._classifier = joblib.load(CLASSIFIER_PATH)
                logger.info(f"[SignatureAgent] Loaded TF-IDF pipeline from checkpoints")
            else:
                logger.warning(f"[SignatureAgent] Checkpoint(s) not found")
        except Exception as e:
            logger.error(f"[SignatureAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> str:
        """
        Extract text payload for TF-IDF vectorization.
        Concatenates all available text fields from the event for signature analysis.
        """
        parts = []

        if event_data:
            payload = str(event_data.get("payload", ""))
            metadata = str(event_data.get("metadata", ""))
            event_type = str(event_data.get("event_type", ""))
            path = str(event_data.get("path", ""))
            user_agent = str(event_data.get("user_agent", ""))

            parts = [payload, metadata, event_type, path, user_agent]

        text = " ".join(p for p in parts if p and p != "None")
        return text if text.strip() else "normal http request benign traffic"

    def score(self, graph_snapshot, node_id, event_data=None) -> tuple[float, float]:
        if self._vectorizer is None or self._classifier is None:
            return 0.0, 0.0

        try:
            text = self._extract_features(graph_snapshot, node_id, event_data)

            # Transform text to TF-IDF vector and classify
            X = self._vectorizer.transform([text])
            proba = self._classifier.predict_proba(X)[0]

            risk = float(max(0.0, min(1.0, proba[1])))  # P(malicious signature)
            confidence = float(max(0.0, min(1.0, abs(proba[1] - proba[0]))))
            return risk, confidence
        except Exception as e:
            logger.error(f"[SignatureAgent] Inference error: {e}")
            return 0.0, 0.0
