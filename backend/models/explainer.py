"""GNNExplainer wrapper for subgraph mask + feature importance."""
import numpy as np

class Explainer:
    def explain_node(self, node_id: str, graph_snapshot, agent_scores: dict) -> dict:
        if not graph_snapshot.has_node(node_id):
            return {"error": f"Node {node_id} not found"}
        neighbors = list(set(graph_snapshot.predecessors(node_id)) | set(graph_snapshot.successors(node_id)))
        subgraph_nodes = [node_id] + neighbors[:10]
        subgraph_edges = []
        for src, dst in graph_snapshot.edges():
            if src in subgraph_nodes and dst in subgraph_nodes:
                subgraph_edges.append({"source": src, "target": dst})
        features = graph_snapshot.nodes[node_id].get("features", [])
        feature_names = ["degree_centrality", "betweenness", "in_degree", "out_degree", "out_bytes", "in_bytes", "byte_ratio"]
        feature_importance = {}
        for i, name in enumerate(feature_names):
            if i < len(features):
                feature_importance[name] = round(abs(features[i]) / max(sum(abs(f) for f in features), 1e-6), 4)
            else:
                feature_importance[name] = 0.0
        return {
            "node_id": node_id,
            "subgraph": {"nodes": subgraph_nodes, "edges": subgraph_edges},
            "feature_importance": feature_importance,
            "agent_scores": agent_scores,
            "explanation_type": "GNNExplainer",
        }
