"""
Parallel agent aggregator with ThreadPoolExecutor.
Freezes graph snapshot then dispatches all 15 agents simultaneously.
"""
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.services.graph_builder import GraphBuilder

# Lazy imports to avoid circular deps
_agents = None

def _get_agents():
    global _agents
    if _agents is None:
        from backend.agents.cpu.signature_agent import SignatureAgent
        from backend.agents.cpu.spike_agent import SpikeAgent
        from backend.agents.cpu.behavior_agent import BehaviorAgent
        from backend.agents.cpu.port_scan_agent import PortScanAgent
        from backend.agents.cpu.ddos_agent import DDoSAgent
        from backend.agents.cpu.sqli_xss_agent import SQLiXSSAgent
        from backend.agents.cpu.bruteforce_agent import BruteForceAgent
        from backend.agents.cpu.lateral_movement_agent import LateralMovementAgent
        from backend.agents.cpu.exfiltration_agent import ExfiltrationAgent
        from backend.agents.cpu.ransomware_agent import RansomwareAgent
        from backend.agents.cpu.mitm_agent import MITMAgent
        from backend.agents.cpu.supply_inject_agent import SupplyInjectAgent
        from backend.agents.cpu.priv_escalation_agent import PrivEscalationAgent
        from backend.agents.cpu.c2_beacon_agent import C2BeaconAgent
        from backend.agents.gpu.graph_gcn_agent import GraphGCNAgent
        from backend.agents.gpu.zero_day_agent import ZeroDayAgent
        from backend.agents.gpu.temporal_apt_agent import TemporalAPTAgent

        _agents = [
            SignatureAgent(),
            SpikeAgent(),
            BehaviorAgent(),
            PortScanAgent(),
            DDoSAgent(),
            SQLiXSSAgent(),
            BruteForceAgent(),
            LateralMovementAgent(),
            ExfiltrationAgent(),
            RansomwareAgent(),
            MITMAgent(),
            SupplyInjectAgent(),
            PrivEscalationAgent(),
            C2BeaconAgent(),
            GraphGCNAgent(),
            ZeroDayAgent(),
            TemporalAPTAgent(),
        ]
    return _agents


class Aggregator:
    """Dispatches all 15 agents in parallel and collects scores."""
    
    def __init__(self, max_workers: int = 15, timeout_ms: int = 100):
        self.max_workers = max_workers
        self.timeout_s = timeout_ms / 1000.0
        self.graph_builder = GraphBuilder()
    
    def run_swarm(self, graph_snapshot, node_id: str, event_data: dict = None) -> dict:
        """Run all 15 agents on a frozen graph snapshot."""
        agents = _get_agents()
        results = []
        start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(agent.run, graph_snapshot, node_id, event_data): agent
                for agent in agents
            }
            
            for future in as_completed(futures, timeout=2.0):
                try:
                    result = future.result(timeout=self.timeout_s)
                    results.append(result)
                except Exception as e:
                    agent = futures[future]
                    results.append({
                        "agent": agent.name,
                        "type": agent.agent_type,
                        "score": 0.0,
                        "latency_ms": 0.0,
                        "error": str(e),
                    })
        
        total_ms = (time.perf_counter() - start) * 1000
        
        # Ensure consistent order (e.g., sort by agent name)
        results.sort(key=lambda x: x["agent"])
        
        scores = {r["agent"]: r["score"] for r in results}
        confidences = {r["agent"]: r.get("confidence", 0.5) for r in results}
        
        # Phase 3: Publish results to Agent Communication Bus
        from backend.services.agent_bus import agent_bus
        agent_bus.clear()
        for r in results:
            if r["score"] > 0.3:
                agent_bus.publish(r["agent"], {
                    "score": r["score"],
                    "confidence": r.get("confidence", 0.5),
                    "node_id": node_id,
                    "alert": f"{r['agent']} detected anomaly (score={r['score']:.2f})",
                })
        
        correlation_score = agent_bus.get_correlation_score()
        fired_agents = agent_bus.get_fired_agents(threshold=0.5)
        
        avg_score = sum(scores.values()) / max(len(scores), 1)
        max_score = max(scores.values()) if scores else 0.0
        
        # Build feature vector: N scores + N confidences
        feature_vector = [r["score"] for r in results] + [r.get("confidence", 0.5) for r in results]
        agent_names = [r["agent"] for r in results]
        
        return {
            "node_id": node_id,
            "agent_results": results,
            "scores": scores,
            "confidences": confidences,
            "feature_vector": feature_vector,
            "agent_names": agent_names,
            "avg_score": round(avg_score, 4),
            "max_score": round(max_score, 4),
            "total_latency_ms": round(total_ms, 2),
            "agents_fired": sum(1 for r in results if r["score"] > 0.5),
            "total_agents": len(results),
            "correlation_score": round(correlation_score, 4),
            "fired_agents_detail": fired_agents,
        }
    
    def analyze_all_nodes(self, graph_snapshot) -> list:
        """Run swarm analysis on all nodes in the graph."""
        results = []
        for node in graph_snapshot.nodes():
            result = self.run_swarm(graph_snapshot, node)
            results.append(result)
        return results
    
    def get_all_agent_status(self) -> list:
        """Get status of all 15 agents."""
        agents = _get_agents()
        return [agent.get_status() for agent in agents]
