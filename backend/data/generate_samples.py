"""
GRASP — Sample Data Generator
Generates CSV samples for all agents to provide visible "raw data" for project reviews.
"""
import os
import pandas as pd
import numpy as np
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.ai_model.train_cpu_ml_agents import (
    generate_ddos_features, generate_behavior_features, generate_spike_features,
    generate_exfiltration_features, generate_port_scan_features, generate_lateral_movement_features,
    generate_bruteforce_features, generate_supply_inject_features, generate_priv_escalation_features,
    generate_mitm_features, generate_ransomware_features, generate_c2_beacon_features,
    generate_sqli_xss_corpus, generate_signature_corpus
)

DATA_DIR = os.path.dirname(__file__)

def save_numerical(name, X, cols, y=None):
    df = pd.DataFrame(X, columns=cols)
    if y is not None:
        df["is_attack"] = y
    else:
        # For unsupervised agents (iforest), we don't have y, so we just mark the half/half split
        df["is_anomaly"] = [0] * (len(X) // 2) + [1] * (len(X) - len(X) // 2)
    
    path = os.path.join(DATA_DIR, f"{name}_sample.csv")
    df.head(500).to_csv(path, index=False)
    print(f"[OK] Generated {path}")

def save_text(name, texts, labels):
    df = pd.DataFrame({"payload": texts, "is_attack": labels})
    path = os.path.join(DATA_DIR, f"{name}_sample.csv")
    df.head(500).to_csv(path, index=False)
    print(f"[OK] Generated {path}")

def main():
    print("Generating CSV samples for project review...")
    
    # Isolation Forest Agents
    save_numerical("ddos", generate_ddos_features(1000), 
                   ["in_degree", "out_degree", "bytes_recv", "pkt_rate", "syn_ratio", "unique_src_ips", "avg_pkt_size", "connection_duration"])
    
    save_numerical("behavior", generate_behavior_features(1000), 
                   ["in_degree", "out_degree", "bytes_out", "bytes_in", "out_in_ratio"])
    
    save_numerical("spike", generate_spike_features(1000), 
                   ["current_degree", "rolling_mean", "rolling_std", "z_score", "delta_from_prev"])
    
    # Random Forest Agents
    X, y = generate_exfiltration_features(1000)
    save_numerical("exfiltration", X, ["bytes_out", "bytes_in", "out_in_ratio", "unique_dst_ips", "avg_payload_size", "session_duration", "out_degree", "protocol_diversity"], y)
    
    X, y = generate_port_scan_features(1000)
    save_numerical("port_scan", X, ["unique_targets", "unique_ports", "scan_rate", "syn_only_ratio", "avg_pkt_size", "rst_ratio", "total_connections", "connection_failures"], y)
    
    X, y = generate_lateral_movement_features(1000)
    save_numerical("lateral_movement", X, ["hop_count", "internal_connections", "unique_subnets", "time_spread", "auth_events", "new_hosts_contacted", "protocol_switch_count", "priv_level_delta"], y)
    
    X, y = generate_bruteforce_features(1000)
    save_numerical("brute_force", X, ["auth_failures", "auth_rate", "unique_usernames", "lockout_count", "time_between_attempts", "password_entropy_avg", "geo_distance", "success_ratio"], y)
    
    X, y = generate_supply_inject_features(1000)
    save_numerical("supply_inject", X, ["new_edges_count", "node_age_hours", "supplier_reputation_score", "edge_weight_anomaly", "cross_tier_connection", "cert_validity_days", "api_call_frequency", "payload_hash_novelty"], y)
    
    X, y = generate_priv_escalation_features(1000)
    save_numerical("priv_escalation", X, ["rbac_violations", "out_degree", "target_criticality", "role_change_count", "admin_api_calls", "sudo_events", "new_permissions_granted", "time_since_last_role_change"], y)
    
    X, y = generate_mitm_features(1000)
    save_numerical("mitm", X, ["path_deviation", "direct_edge_exists", "betweenness_centrality", "arp_mismatch_count", "cert_chain_length", "tls_downgrade_flag", "duplicate_mac_count", "packet_delay_variance"], y)
    
    X, y = generate_ransomware_features(1000)
    save_numerical("ransomware", X, ["file_lock_events", "affected_nodes", "encryption_rate", "unique_extensions", "ransom_note_detected", "lateral_spread_hops", "time_window_density", "api_crypto_calls"], y)
    
    X, y = generate_c2_beacon_features(1000)
    save_numerical("c2_beacon", X, ["interval_mean", "interval_std", "interval_cv", "fft_peak_prominence", "regularity_score", "packet_size_uniformity", "dns_query_entropy", "jitter_ratio"], y)
    
    # NLP Agents
    texts, labels = generate_sqli_xss_corpus(1000)
    save_text("sqli_xss", texts, labels)
    
    texts, labels = generate_signature_corpus(1000)
    save_text("signature", texts, labels)

    print("\nAll 14 CSV files generated successfully in backend/data/")

if __name__ == "__main__":
    main()
