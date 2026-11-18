"""LLM Reasoning Agent — prompt-based threat classification via Gemini."""
from backend.agents.base_agent import BaseAgent

class LLMReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__("LLM Reasoning", "cpu")

    def score(self, graph_snapshot, node_id, event_data=None):
        return 0.0  # Reasoning agent is called post-aggregation, not in scoring loop

        threat_indicators = {k: v for k, v in agent_scores.items() if v > 0.3}
        if not threat_indicators:
            return {"classification": "benign", "confidence": 0.9, "reasoning": "No significant agent triggers."}

        top_agent = max(threat_indicators, key=threat_indicators.get)
        top_score = threat_indicators[top_agent]
        
        # Invoke local Phi-3 (high speed)
        import asyncio
        import logging
        from backend.services.ollama_client import generate
        
        prompt = f"Network agents triggered these anomaly scores: {threat_indicators}. The top agent is {top_agent}. Output exactly one word specifying the attack category (e.g., 'ddos', 'ransomware', 'xss', 'unknown')."
        
        try:
            try:
                loop = asyncio.get_event_loop()
                classification = loop.run_until_complete(
                    generate(prompt, model="phi3:mini", system="You classify cyber threats into single word categories. Output only the category word.")
                )
            except RuntimeError:
                classification = asyncio.run(
                    generate(prompt, model="phi3:mini", system="You classify cyber threats into single word categories. Output only the category word.")
                )
        except Exception as e:
            logging.error(f"[LLMReasoning] Phi-3 error: {e}")
            classification = "unknown"

        return {
            "classification": classification.strip().lower(),
            "confidence": round(top_score, 4),
            "primary_agent": top_agent,
            "supporting_agents": list(threat_indicators.keys()),
            "reasoning": f"Phi-3 categorized this as {classification}. Primary indicator: {top_agent}.",
        }
