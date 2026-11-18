"""
LLM Explainer — uses Gemini API for plain-English anomaly reports.
Supports API key rotation for rate limit resilience.
"""
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

API_KEYS = [
    os.getenv("GEMINI_API_KEY_1", ""),
    os.getenv("GEMINI_API_KEY_2", ""),
]
API_KEYS = [k for k in API_KEYS if k]  # Filter empty

_current_key_idx = 0


def _get_api_key():
    global _current_key_idx
    if not API_KEYS:
        return None
    key = API_KEYS[_current_key_idx % len(API_KEYS)]
    _current_key_idx += 1
    return key


class LLMExplainer:
    """Generates human-readable anomaly reports using Gemini API."""
    
    def explain(self, node_id: str, agent_scores: dict, risk_score: float, graph_context: dict = None) -> dict:
        """Generate a plain-English explanation for an anomalous node."""
        
        # Build prompt
        top_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        agent_summary = "\n".join([f"  - {name}: {score:.2f}" for name, score in top_agents])
        
        prompt = f"""You are a cybersecurity analyst for a medical supply chain security platform called GRASP.

A node '{node_id}' has been flagged as anomalous with a risk score of {risk_score:.2f} (scale 0-1).

Top triggering agents and their scores:
{agent_summary}

Context: This is a medical supply chain network where nodes represent hospitals, suppliers, distributors, and pharmacies. Edges represent transactions and data flows.

Write exactly 3 sentences:
1. What type of threat this most likely represents
2. Which specific indicators triggered the detection
3. Recommended immediate action

Be specific, technical, and concise. No markdown formatting."""

        import logging
        logger = logging.getLogger("llm_explainer")
        
        # Try Local Ollama First
        import asyncio
        from backend.services.ollama_client import generate
        try:
            # We use an existing loop or run ad-hoc synchronous wrappers 
            try:
                loop = asyncio.get_event_loop()
                explanation = loop.run_until_complete(
                    generate(prompt, model="llama3", system="You are a strict technical incident responder. Output 3 sentences max.")
                )
            except RuntimeError:
                explanation = asyncio.run(
                    generate(prompt, model="llama3", system="You are a strict technical incident responder. Output 3 sentences max.")
                )
        except Exception as e:
            logger.error(f"[LLMExplainer] Ollama generation failed: {e}")
            explanation = self._fallback_explanation(node_id, top_agents, risk_score)
        
        return {
            "node_id": node_id,
            "risk_score": risk_score,
            "explanation": explanation,
            "top_agents": [{"agent": a, "score": round(s, 4)} for a, s in top_agents],
        }
    
    def _fallback_explanation(self, node_id: str, top_agents: list, risk_score: float) -> str:
        """Generate explanation without LLM API."""
        if not top_agents:
            return f"Node {node_id} has an elevated risk score of {risk_score:.2f} but no specific agent triggers were identified."
        
        top_agent, top_score = top_agents[0]
        threat_map = {
            "Signature": "known attack pattern match",
            "Spike": "anomalous traffic spike",
            "Behavior": "behavioral deviation from baseline",
            "Port Scan": "network reconnaissance activity",
            "DDoS": "distributed denial-of-service indicators",
            "SQLi/XSS": "injection attack attempt",
            "Brute Force": "credential stuffing or brute force",
            "Lateral Movement": "lateral movement across the network",
            "Exfiltration": "data exfiltration pattern",
            "Ransomware": "ransomware propagation pattern",
            "MITM": "man-in-the-middle interception",
            "Supply Inject": "supply chain injection attempt",
            "Priv Escalation": "privilege escalation attempt",
            "C2/Beaconing": "command-and-control beaconing",
            "Graph GCN": "structural graph anomaly via GNN",
            "Zero-Day": "unknown threat pattern in embedding space",
            "Temporal/APT": "advanced persistent threat sequence",
        }
        
        threat = threat_map.get(top_agent, "anomalous activity")
        agents_fired = len([a for a, s in top_agents if s > 0.5])
        
        return (
            f"Node {node_id} shows strong indicators of {threat} with a risk score of {risk_score:.2f}. "
            f"The primary trigger was the {top_agent} agent (score: {top_score:.2f}), with {agents_fired} agents reporting elevated scores. "
            f"Immediate investigation is recommended; the node has been flagged for quarantine review."
        )
