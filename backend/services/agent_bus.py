"""
Agent Communication Bus — enables inter-agent collaborative detection.

When one agent detects an anomaly, it publishes findings to the bus.
Other agents can subscribe to receive context from peers, enabling
correlated multi-stage attack detection.
"""
from collections import defaultdict
import threading
import logging

logger = logging.getLogger("agent_bus")


class AgentBus:
    """Thread-safe inter-agent communication bus for collaborative detection."""

    def __init__(self):
        self._lock = threading.Lock()
        self.messages = defaultdict(list)
        self.subscribers = defaultdict(list)

    def publish(self, agent_name: str, message: dict):
        """Agent publishes a finding to the bus."""
        with self._lock:
            self.messages[agent_name].append(message)
            # Notify all subscribers
            for callback in self.subscribers.get(agent_name, []):
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"[AgentBus] Subscriber error: {e}")

    def subscribe(self, source_agent: str, callback):
        """Subscribe to messages from a specific agent."""
        with self._lock:
            self.subscribers[source_agent].append(callback)

    def get_context(self, requesting_agent: str) -> dict:
        """Get all current findings from other agents."""
        with self._lock:
            context = {}
            for agent, msgs in self.messages.items():
                if agent != requesting_agent and msgs:
                    context[agent] = msgs[-1]  # Latest message only
            return context

    def get_fired_agents(self, threshold: float = 0.5) -> list:
        """Get list of agents that fired above threshold."""
        with self._lock:
            fired = []
            for agent, msgs in self.messages.items():
                if msgs and msgs[-1].get("score", 0) > threshold:
                    fired.append({
                        "agent": agent,
                        "score": msgs[-1]["score"],
                        "confidence": msgs[-1].get("confidence", 0.5),
                    })
            return sorted(fired, key=lambda x: x["score"], reverse=True)

    def get_correlation_score(self) -> float:
        """
        Compute inter-agent correlation.
        High correlation = many agents agree = higher confidence.
        """
        with self._lock:
            scores = []
            for agent, msgs in self.messages.items():
                if msgs:
                    scores.append(msgs[-1].get("score", 0))
            if not scores or len(scores) < 2:
                return 0.0
            # Correlation = how many agents agree on anomaly
            above_threshold = sum(1 for s in scores if s > 0.5)
            return above_threshold / len(scores)

    def clear(self):
        """Clear all messages after each analysis cycle."""
        with self._lock:
            self.messages.clear()

    def get_summary(self) -> dict:
        """Get a summary of all published messages for logging."""
        with self._lock:
            summary = {}
            for agent, msgs in self.messages.items():
                if msgs:
                    latest = msgs[-1]
                    summary[agent] = {
                        "score": latest.get("score", 0),
                        "confidence": latest.get("confidence", 0),
                        "message_count": len(msgs),
                    }
            return summary


# Singleton instance for the application
agent_bus = AgentBus()
