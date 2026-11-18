import sys
import os
import networkx as nx

sys.path.insert(0, os.path.dirname(__file__))

from backend.data.dataset_loader import DatasetLoader
from backend.services.aggregator import Aggregator
from backend.services.decision_engine import DecisionEngine

def test_agents():
    print("Loading dataset...")
    loader = DatasetLoader('backend/data')
    df = loader.load(sample_size=20)
    
    print("Initializing agents...")
    aggregator = Aggregator()
    decision_engine = DecisionEngine()
    
    events = loader.to_events()
    attacks = [e for e in events if e['label'] != 'benign']
    
    print(f"\nEvaluating {len(attacks)} attack flows:")
    print("-" * 50)
    
    # Create an empty graph snapshot
    snapshot = nx.Graph()
    
    for i, e in enumerate(attacks[:10]):
        # Mock add edge for the snapshot
        snapshot.add_edge(e['source_ip'], e['dest_ip'], protocol=e['protocol'], bytes_sent=e.get('bytes_sent', 0))
        
        swarm_result = aggregator.run_swarm(snapshot, e['dest_ip'], e)
        decision = decision_engine.evaluate(e['dest_ip'], swarm_result)
        
        threat_score = decision['risk_score'] * 100
        
        print(f"[{i+1}] {e['label']:<15} | Risk: {threat_score:>5.1f}% | IP: {e['source_ip']:<14} -> {e['dest_ip']}")
        if threat_score > 40:
            top_agents = sorted(swarm_result['scores'].items(), key=lambda x: x[1]['score'], reverse=True)[:3]
            agents_str = ', '.join([f"{k} ({v['score']*100:.0f}%)" for k,v in top_agents])
            print(f"    Detected by: {agents_str}")

if __name__ == '__main__':
    test_agents()
