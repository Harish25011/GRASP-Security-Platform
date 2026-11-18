"""
NetworkX graph builder for medical supply chain network.
"""
import networkx as nx
import random
import copy


class GraphBuilder:
    """Builds and manages the supply chain network graph."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self._node_counter = 0
    
    def build_from_events(self, events: list) -> nx.DiGraph:
        """Build graph from event data."""
        for event in events:
            src = event.get("source_ip", f"node_{self._node_counter}")
            dst = event.get("dest_ip", f"node_{self._node_counter + 1}")
            self._node_counter += 2
            
            if not self.graph.has_node(src):
                self.graph.add_node(src, **self._default_node_attrs(src))
            if not self.graph.has_node(dst):
                self.graph.add_node(dst, **self._default_node_attrs(dst))
            
            self.graph.add_edge(src, dst,
                protocol=event.get("protocol", "TCP"),
                bytes_sent=event.get("bytes_sent", 0),
                bytes_recv=event.get("bytes_recv", 0),
                timestamp=event.get("timestamp", ""),
            )
        
        self._compute_features()
        return self.graph
    
    def build_sample_graph(self, num_nodes: int = 30, num_edges: int = 50) -> nx.DiGraph:
        """Build a realistic sample supply chain graph."""
        node_types = ["Hospital", "Supplier", "Distributor", "Manufacturer", "Pharmacy", "Warehouse", "Lab"]
        
        for i in range(num_nodes):
            node_id = f"192.168.1.{10 + i}"
            self.graph.add_node(node_id,
                node_type=random.choice(node_types),
                label=f"{random.choice(node_types)}-{i:02d}",
                risk_score=0.0,
                status="active",
                features=[],
            )
        
        nodes = list(self.graph.nodes())
        for _ in range(num_edges):
            src, dst = random.sample(nodes, 2)
            self.graph.add_edge(src, dst,
                protocol=random.choice(["TCP", "UDP", "HTTP", "HTTPS"]),
                bytes_sent=random.randint(100, 50000),
                bytes_recv=random.randint(100, 30000),
            )
        
        self._compute_features()
        return self.graph
    
    def _default_node_attrs(self, node_id: str) -> dict:
        return {
            "node_type": "Unknown",
            "label": node_id,
            "risk_score": 0.0,
            "status": "active",
            "features": [],
        }
    
    def _compute_features(self):
        """Compute graph-based features for each node."""
        degree_centrality = nx.degree_centrality(self.graph)
        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except Exception:
            betweenness = {n: 0.0 for n in self.graph.nodes()}
        
        for node in self.graph.nodes():
            in_deg = self.graph.in_degree(node)
            out_deg = self.graph.out_degree(node)
            
            out_bytes = sum(d.get("bytes_sent", 0) for _, _, d in self.graph.out_edges(node, data=True))
            in_bytes = sum(d.get("bytes_recv", 0) for _, _, d in self.graph.in_edges(node, data=True))
            
            self.graph.nodes[node]["features"] = [
                degree_centrality.get(node, 0),
                betweenness.get(node, 0),
                in_deg,
                out_deg,
                out_bytes,
                in_bytes,
                out_bytes / max(in_bytes, 1),
            ]
    
    def freeze(self) -> nx.DiGraph:
        """Create a deep copy snapshot for thread-safe parallel reading."""
        return copy.deepcopy(self.graph)
    
    def to_cytoscape(self) -> dict:
        """Export graph as Cytoscape.js compatible JSON."""
        elements = []
        for node, data in self.graph.nodes(data=True):
            elements.append({
                "data": {
                    "id": node,
                    "label": data.get("label", node),
                    "node_type": data.get("node_type", "Unknown"),
                    "risk_score": data.get("risk_score", 0.0),
                    "status": data.get("status", "active"),
                }
            })
        for src, dst, data in self.graph.edges(data=True):
            elements.append({
                "data": {
                    "source": src,
                    "target": dst,
                    "protocol": data.get("protocol", ""),
                    "bytes_sent": data.get("bytes_sent", 0),
                }
            })
        return {"elements": elements}
    
    def get_stats(self) -> dict:
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "density": round(nx.density(self.graph), 4),
            "connected_components": nx.number_weakly_connected_components(self.graph),
        }
