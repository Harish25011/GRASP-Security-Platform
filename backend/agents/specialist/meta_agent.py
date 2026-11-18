"""Meta Agent — monitors all 15 agent scores, escalates multi-agent spikes."""
from backend.agents.base_agent import BaseAgent

class MetaAgent(BaseAgent):
    def __init__(self, spike_threshold=3):
        super().__init__("Meta Agent", "cpu")
        self.spike_threshold = spike_threshold

    def score(self, graph_snapshot, node_id, event_data=None):
        return 0.0  # Meta agent doesn't score independently

    def evaluate(self, all_scores: dict) -> dict:
        high_scores = {k: v for k, v in all_scores.items() if v > 0.5}
        if len(high_scores) >= self.spike_threshold:
            categories = self._categorize(high_scores)
            max_category = max(categories.items(), key=lambda x: len(x[1])) if categories else ("unknown", [])
            return {
                "escalated": True,
                "trigger_count": len(high_scores),
                "primary_category": max_category[0],
                "triggered_agents": list(high_scores.keys()),
                "severity": "critical" if len(high_scores) >= 5 else "high",
            }
        return {"escalated": False, "trigger_count": len(high_scores)}

    def _categorize(self, scores):
        categories = {
            "network": ["Port Scan", "DDoS", "MITM", "C2/Beaconing"],
            "injection": ["Signature", "SQLi/XSS", "Supply Inject"],
            "access": ["Brute Force", "Priv Escalation", "Lateral Movement"],
            "data": ["Exfiltration", "Ransomware"],
            "advanced": ["Graph GCN", "Zero-Day", "Temporal/APT"],
        }
        result = {}
        for cat, agents in categories.items():
            matched = [a for a in agents if a in scores]
            if matched:
                result[cat] = matched
        return result
