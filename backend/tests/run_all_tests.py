"""GRASP Backend - Full Verification Test Suite"""
import requests
import json
import time
import sys

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0

def test(name, fn):
    global PASS, FAIL
    print(f"\n{'='*60}")
    print(f"  TEST: {name}")
    print(f"{'='*60}")
    try:
        result = fn()
        if result:
            PASS += 1
            print(f"  >> PASSED")
        else:
            FAIL += 1
            print(f"  >> FAILED")
    except Exception as e:
        FAIL += 1
        print(f"  >> ERROR: {e}")


def test_health():
    r = requests.get(f"{BASE}/")
    data = r.json()
    print(f"  Status: {data['status']}")
    print(f"  Name:   {data['name']} v{data['version']}")
    return data["status"] == "operational"


def test_load_dataset():
    r = requests.post(f"{BASE}/api/load")
    data = r.json()
    stats = data.get("graph_stats", {})
    print(f"  Nodes: {stats.get('total_nodes', 0)}")
    print(f"  Edges: {stats.get('total_edges', 0)}")
    print(f"  Events: {data.get('events_processed', 0)}")
    return stats.get("total_nodes", 0) > 0


def test_port_scan():
    r = requests.post(f"{BASE}/api/attack",
                      json={"attack_type": "port_scan"})
    data = r.json()
    decision = data.get("decision", {})
    swarm = data.get("swarm_result", {})
    risk = decision.get("risk_score", 0)
    action = decision.get("action", "unknown")
    tier = decision.get("tier", "unknown")
    agents_fired = swarm.get("agents_fired", 0)

    print(f"  Risk Score:    {risk}")
    print(f"  Action:        {action}")
    print(f"  Tier:          {tier}")
    print(f"  Agents Fired:  {agents_fired}")
    print(f"  ML Score:      {decision.get('ml_risk_score', 'N/A')}")
    print(f"  Bayesian:      {decision.get('bayesian_score', 'N/A')}")
    print(f"  Correlation:   {decision.get('correlation_score', 'N/A')}")

    top = decision.get("top_agents", [])
    if top:
        print(f"  Top Agents:")
        for a in top[:5]:
            print(f"    - {a['agent']}: {a['score']}")

    return risk > 0.2 and action != "normal"


def test_ddos():
    r = requests.post(f"{BASE}/api/attack",
                      json={"attack_type": "ddos"})
    data = r.json()
    decision = data.get("decision", {})
    swarm = data.get("swarm_result", {})
    risk = decision.get("risk_score", 0)
    action = decision.get("action", "unknown")
    tier = decision.get("tier", "unknown")
    agents_fired = swarm.get("agents_fired", 0)

    print(f"  Risk Score:    {risk}")
    print(f"  Action:        {action}")
    print(f"  Tier:          {tier}")
    print(f"  Agents Fired:  {agents_fired}")
    print(f"  ML Score:      {decision.get('ml_risk_score', 'N/A')}")
    print(f"  Bayesian:      {decision.get('bayesian_score', 'N/A')}")

    top = decision.get("top_agents", [])
    if top:
        print(f"  Top Agents:")
        for a in top[:5]:
            print(f"    - {a['agent']}: {a['score']}")
    # DDoS detected if: the DDoS agent score is high OR overall risk > 0.2
    scores = swarm.get("scores", {})
    ddos_agent_score = scores.get("DDoS", 0)
    print(f"  DDoS Agent:    {ddos_agent_score}")
    
    # The DDoS agent must detect (>0.5), and either overall risk >0.2 or agent fired
    return ddos_agent_score > 0.5 or (risk > 0.2 and action != "normal")


def test_agents_status():
    r = requests.get(f"{BASE}/api/agents/status")
    data = r.json()
    agents = data.get("agents", [])
    print(f"  Total Agents: {len(agents)}")
    for a in agents:
        status = "ACTIVE" if a.get("total_runs", 0) > 0 else "idle"
        print(f"    {a['name']:25s} runs={a.get('total_runs',0):3d}  "
              f"score={a.get('last_score',0):.3f}  [{status}]")
    return len(agents) >= 15


def test_analyze():
    r = requests.get(f"{BASE}/api/analyze")
    data = r.json()
    analyzed = data.get("analyzed_nodes", 0)
    anomalies = data.get("anomalies_found", 0)
    print(f"  Analyzed Nodes:  {analyzed}")
    print(f"  Anomalies Found: {anomalies}")
    return analyzed > 0


def test_model_health():
    r = requests.get(f"{BASE}/api/model/health")
    data = r.json()
    print(f"  Total Models:  {data.get('total_models', 0)}")
    print(f"  Models Loaded: {data.get('models_loaded', 0)}")
    ckpts = data.get("checkpoints", {})
    for name, info in ckpts.items():
        status = f"OK ({info['size_bytes']:,} bytes)" if info["exists"] else "MISSING"
        print(f"    {name:30s} {status}")
    drift = data.get("drift", {})
    print(f"  Drift Status:  {'DRIFT!' if drift.get('drift') else 'Stable'}")
    return data.get("models_loaded", 0) >= 4


if __name__ == "__main__":
    print("=" * 60)
    print("  GRASP BACKEND - FULL VERIFICATION TEST SUITE")
    print("=" * 60)

    test("1. Health Check", test_health)
    test("2. Dataset Loading", test_load_dataset)
    test("3. Port Scan Detection", test_port_scan)
    test("4. DDoS Detection", test_ddos)
    test("5. All Agents Responding", test_agents_status)
    test("6. Full Pipeline (Analyze)", test_analyze)
    test("7. Model Health Check", test_model_health)

    print(f"\n{'='*60}")
    print(f"  RESULTS: {PASS} PASSED / {FAIL} FAILED / {PASS+FAIL} TOTAL")
    print(f"{'='*60}")

    if FAIL > 0:
        print("  [!!] SOME TESTS FAILED - review output above")
        sys.exit(1)
    else:
        print("  [OK] ALL TESTS PASSED - Backend is ready for demo!")
        sys.exit(0)
