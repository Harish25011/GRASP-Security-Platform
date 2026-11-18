"""
Feature engineering for graph nodes.
Computes degree, centrality, traffic volume and timing features.
"""
import networkx as nx
import numpy as np


class FeatureEngineer:
    """Computes node-level and edge-level features."""
    
    def compute_node_features(self, graph: nx.DiGraph) -> dict:
        """Compute feature vectors for all nodes."""
        degree_cent = nx.degree_centrality(graph)
        try:
            between_cent = nx.betweenness_centrality(graph)
        except Exception:
            between_cent = {n: 0.0 for n in graph.nodes()}
        try:
            closeness_cent = nx.closeness_centrality(graph)
        except Exception:
            closeness_cent = {n: 0.0 for n in graph.nodes()}
        
        features = {}
        for node in graph.nodes():
            in_deg = graph.in_degree(node)
            out_deg = graph.out_degree(node)
            
            out_bytes = sum(d.get("bytes_sent", 0) for _, _, d in graph.out_edges(node, data=True))
            in_bytes = sum(d.get("bytes_recv", 0) for _, _, d in graph.in_edges(node, data=True))
            
            features[node] = {
                "degree_centrality": degree_cent.get(node, 0),
                "betweenness_centrality": between_cent.get(node, 0),
                "closeness_centrality": closeness_cent.get(node, 0),
                "in_degree": in_deg,
                "out_degree": out_deg,
                "total_degree": in_deg + out_deg,
                "out_bytes": out_bytes,
                "in_bytes": in_bytes,
                "byte_ratio": out_bytes / max(in_bytes, 1),
                "neighbor_count": len(set(graph.predecessors(node)) | set(graph.successors(node))),
            }
        
        return features
    
    def to_feature_matrix(self, features: dict) -> tuple:
        """Convert feature dict to numpy matrix."""
        node_ids = list(features.keys())
        matrix = np.array([
            list(features[n].values()) for n in node_ids
        ], dtype=np.float32)
        return node_ids, matrix
