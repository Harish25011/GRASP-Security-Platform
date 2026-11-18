import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.data.dataset_loader import DatasetLoader
from backend.services.aggregator import Aggregator
from backend.services.graph_builder import GraphBuilder
from backend.ai_model.train import train
from backend.models.meta_classifier import MetaClassifier
from backend.api.routes import ATTACK_TYPES

def main():
    print("Loading dataset...")
    loader = DatasetLoader('backend/data')
    df = loader.load(sample_size=1500)
    events = loader.to_events()
    
    aggregator = Aggregator(max_workers=15)
    graph_builder = GraphBuilder()
    
    graph = graph_builder.build_from_events(events[:1000])
    print(f"Graph built with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    
    snapshot = graph_builder.freeze()
    
    X = []
    y = []
    
    print(f"Processing {len(events)} events to generate 34-dim agent vectors...")
    
    count = 0
    for e in events:
        target_ip = e['dest_ip']
        try:
            swarm_res = aggregator.run_swarm(snapshot, target_ip, e)
            vec = swarm_res['feature_vector']
            if len(vec) == 34:
                X.append(vec)
                label = 0 if e['label'] == 'benign' else 1
                y.append(label)
                
                count += 1
                if count % 100 == 0:
                    print(f" Processed {count} vectors...")
        except Exception as err:
            pass

        if count >= 800:
            break

    X = np.array(X)
    y = np.array(y)
    
    print(f"Saving vectors shape {X.shape}")
    os.makedirs('backend/data', exist_ok=True)
    np.savez('backend/data/vectors.npz', X=X, y=y)
    
    print("Training GRASPClassifier...")
    model = MetaClassifier()
    res = train(X, y, model, device='cpu', epochs=15, n_splits=3, retrain=True, save_path='backend/checkpoints/grasp_classifier.pt')
    
    import json
    history_path = "backend/checkpoints/training_history.json"
    print(f"Saving history to {history_path}")
    from datetime import datetime
    with open(history_path, "w") as f:
        json.dump({
            "best_f1": res["f1"],
            "best_auc": res["auc"],
            "last_retrain": datetime.now().isoformat()
        }, f)
        
    print("DONE! Initial model checkpoint saved.")

if __name__ == '__main__':
    main()
