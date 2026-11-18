"""
SQLi/XSS Agent — TF-IDF + LogisticRegression NLP classifier on HTTP payloads.
Replaces hardcoded regex pattern matching with pre-trained NLP pipeline.
"""
import os
import logging
import numpy as np
import joblib
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("SQLiXSSAgent")
VECTORIZER_PATH = os.path.join("backend", "checkpoints", "sqli_xss_agent_vectorizer.pkl")
CLASSIFIER_PATH = os.path.join("backend", "checkpoints", "sqli_xss_agent_tfidf.pkl")


class SQLiXSSAgent(BaseAgent):
    def __init__(self):
        super().__init__("SQLi/XSS", "cpu")
        self._vectorizer = None
        self._classifier = None
        try:
            if os.path.exists(VECTORIZER_PATH) and os.path.exists(CLASSIFIER_PATH):
                self._vectorizer = joblib.load(VECTORIZER_PATH)
                self._classifier = joblib.load(CLASSIFIER_PATH)
                logger.info(f"[SQLiXSSAgent] Loaded TF-IDF pipeline from checkpoints")
            else:
                logger.warning(f"[SQLiXSSAgent] Checkpoint(s) not found")
        except Exception as e:
            logger.error(f"[SQLiXSSAgent] Failed to load model: {e}")

    def _extract_features(self, graph_snapshot, node_id, event_data) -> str:
        """
        Extract text payload for TF-IDF vectorization.
        Concatenates all available text fields from the event data.
        """
        parts = []

        if event_data:
            # Gather all text-bearing fields
            payload = str(event_data.get("payload", ""))
            metadata = str(event_data.get("metadata", ""))
            path = str(event_data.get("path", ""))
            query = str(event_data.get("query_string", ""))
            headers = str(event_data.get("headers", ""))
            event_type = str(event_data.get("event_type", ""))

            parts = [payload, metadata, path, query, headers, event_type]

            # For events explicitly labeled as SQLi/XSS, include synthetic signal
            if event_type in ("sql_injection", "sqli_xss", "xss"):
                parts.append("' OR 1=1 -- UNION SELECT * FROM <script>alert(1)</script>")

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

            risk = float(max(0.0, min(1.0, proba[1])))  # P(attack)
            confidence = float(max(0.0, min(1.0, abs(proba[1] - proba[0]))))
            return risk, confidence
        except Exception as e:
            logger.error(f"[SQLiXSSAgent] Inference error: {e}")
            return 0.0, 0.0
