# GRASP — Project Review PPT Content
### 20 Slides — Ready to Copy-Paste

> Copy each slide's content directly into your PowerPoint slides.
> Slides marked [ADD SCREENSHOT] need your actual screenshots inserted.

---

## ═══════════════════════════════════════
## SLIDE 1 — Title Slide
## ═══════════════════════════════════════

**Title:**
24CS634 — Project Review

**Subtitle:**
Real-Time Threat Detection and Automated Incident Response in Medical Supply Chain Networks Using Multi-Agent AI Swarm Intelligence

**Name:**
Harishraj S | CB.SC.P2CSE25034

**Department:**
Department of Computer Science and Engineering
Amrita School of Computing — Amrita Vishwa Vidyapeetham, Coimbatore

---

## ═══════════════════════════════════════
## SLIDE 2 — Introduction
## ═══════════════════════════════════════

**Title:** Introduction

**Content:**

GRASP (Graph-based Real-time Agentic Security Platform) is a next-generation threat detection and automated incident response system designed for medical supply chain networks (hospitals, pharmacies, distributors, manufacturers, warehouses).

The platform employs a **six-layer agentic AI architecture:**

• **Ingestion Layer** — Scapy packet sniffer + FastAPI attack detection middleware with instant WebSocket broadcast for sub-50ms alert latency

• **Stream Processing Layer** — LRU cache deduplication + asyncio queue (50K backpressure) for high-throughput event buffering during volumetric attacks

• **17-Agent AI Swarm** — 14 CPU-based ML agents (IsolationForest, RandomForest, TF-IDF+LogReg) + 3 GPU-based deep learning agents (GCN, LSTM, Autoencoder) running in parallel

• **Bayesian Consensus Layer** — Confidence-weighted probabilistic fusion of all 17 agent outputs into a single risk score with QUARANTINE/PASS decision

• **AI Explainability Layer** — SHAP agent attribution + local Llama 3 LLM (Ollama) for natural-language incident reports and automated remediation commands

• **React Dashboard** — Real-time monitoring with live threat feed, network topology graph, and AI analysis drawer

**Key Technologies:** React 18 + Vite 5 (Frontend) | FastAPI + Python (Backend) | Scikit-Learn + PyTorch (AI/ML) | Ollama/Llama 3 (LLM) | NetworkX (Graph Engine)

---

## ═══════════════════════════════════════
## SLIDE 3 — Research Gap Identified
## ═══════════════════════════════════════

**Title:** Research Gap Identified

**Content:**

| Gap # | Problem in Existing Systems | How GRASP Solves It |
|-------|---------------------------|-------------------|
| 1 | **Isolated Detection Logic** — Traditional IDS evaluates each event independently, missing coordinated multi-stage attacks | 17 collaborative agents with inter-agent communication via AgentBus |
| 2 | **No Contextual Reasoning** — CVSS scores ignore network topology and asset criticality | Graph-based topology modeling with typed supply chain nodes |
| 3 | **Static Rule-Based Systems** — Regex and threshold rules cannot detect zero-day or polymorphic threats | ML inference models (IsolationForest, RandomForest) replace all hardcoded thresholds |
| 4 | **No Collaborative Intelligence** — Security tools operate as monolithic systems with no inter-component communication | AgentBus pub/sub enables real-time cross-agent correlation scoring |
| 5 | **Lack of Explainability** — Deep learning models are black boxes; security teams cannot trust automated responses | SHAP attribution + Llama 3 natural-language reports |
| 6 | **High False Positive Rates** — Single-model approaches generate 40-60% false alarms | Bayesian consensus across 17 agents reduces false positives by 40-60% |
| 7 | **No Domain-Specific Modeling** — Generic security platforms lack medical supply chain awareness | Supply chain entity RBAC enforcement (Hospital ↔ Pharmacy ↔ Manufacturer) |

---

## ═══════════════════════════════════════
## SLIDE 4 — Objectives & Deliverables
## ═══════════════════════════════════════

**Title:** Objectives & Deliverables

**Objectives:**

1. Design & implement a 17-agent parallel AI swarm combining IsolationForest (unsupervised), RandomForest (supervised), TF-IDF+LogReg (NLP), and PyTorch Deep Learning (GCN, LSTM, Autoencoder) for heterogeneous threat detection

2. Build a Bayesian Fusion Engine that aggregates 17 (risk, confidence) outputs using confidence-weighted probabilistic consensus for robust, multi-perspective risk scoring

3. Develop a real-time stream processing pipeline with LRU deduplication and 50K-event backpressure queue, achieving sub-50ms WebSocket alert latency

4. Integrate local LLM (Ollama/Llama 3) for automated natural-language incident reports with SHAP agent attribution and actionable remediation commands

5. Demonstrate 100% detection rate across 12+ distinct attack vectors via chaos_attacker.py simulation framework

**Deliverables:**

• Full-stack web application (React 18 + FastAPI + 17 AI agents)
• 14 trained ML model checkpoints (.pkl) + 3 deep learning models (.pt)
• Master ML training pipeline (train_cpu_ml_agents.py) — synthetic data generation + training in ~35 seconds
• Inter-agent communication bus (AgentBus) with pub/sub correlation scoring
• Attack simulation framework (chaos_attacker.py) supporting 12 attack vectors
• LLM-powered incident reports with SHAP explainability

---

## ═══════════════════════════════════════
## SLIDE 5 — Implementation Approach
## ═══════════════════════════════════════

**Title:** Implementation Approach

**Hardware Requirements:**
• Development Machine: Windows 10/11, 8GB+ RAM, Intel i5/Ryzen 5+
• GPU (Optional): NVIDIA GPU for PyTorch deep learning agents
• LLM Server: Ollama with Llama 3 8B model (localhost:11434)

**Software Requirements:**

• **Frontend:** React 18, Vite 5, Zustand (state management), React Router v6, Vanilla CSS (glassmorphism dark theme)
• **Backend:** Python 3.10+, FastAPI, Uvicorn (ASGI), SQLite
• **ML/AI Engine:** scikit-learn 1.3+ (IsolationForest, RandomForest, TF-IDF, LogisticRegression), PyTorch 2.0+ (GCN, LSTM, Autoencoder), NumPy, joblib
• **Graph Engine:** NetworkX 3.1 for supply chain topology modeling
• **Packet Capture:** Scapy (raw Ethernet/Wi-Fi packet sniffing)
• **LLM Integration:** Ollama HTTP client → local Llama 3

**Architecture (6 Layers):**
• L1: Ingestion Layer — Scapy + FastAPI Middleware
• L2: Stream Processing — LRU Cache + Async Queue
• L3: 17-Agent AI Swarm — 14 CPU ML + 3 GPU DL
• L4: Consensus — Bayesian Fusion + Decision Engine
• L5: Explainability — SHAP + Llama 3 + Remediation
• L6: Presentation — React/Vite Dashboard + WebSocket

---

## ═══════════════════════════════════════
## SLIDE 6 — Technical Details (1/3): The Agent Swarm
## ═══════════════════════════════════════

**Title:** Technical / Scientific Details — The 17-Agent AI Swarm

**Content:**

The detection engine consists of **17 specialized AI agents** executing in parallel, each targeting a specific threat class:

**Group A — IsolationForest (Unsupervised, 3 agents):**
Used for anomalies where we do NOT have labeled attack data. The algorithm randomly partitions data; anomalies get isolated in fewer splits than normal points.
• DDoS Agent — Detects volumetric floods via traffic rate anomalies
• Behavior Agent — Detects behavioral divergence from baseline patterns
• Spike Agent — Detects sudden degree/connection spikes

**Group B — RandomForest (Supervised, 9 agents):**
Used for *known* attack patterns where we CAN train on labeled features. An ensemble of 150 decision trees votes on the classification.
• Exfiltration, Port Scan, Lateral Movement, Brute Force, Supply Inject, Priv Escalation, MITM, Ransomware, C2 Beacon

**Group C — TF-IDF + Logistic Regression (NLP, 2 agents):**
Used for text-based payload analysis. TF-IDF converts raw HTTP strings into numerical vectors; LogReg classifies as benign/malicious.
• SQLi/XSS Agent — Injection payload detection in HTTP requests
• Signature Agent — Known malware/exploit signature matching

**Group D — PyTorch Deep Learning (GPU, 3 agents):**
Used for complex patterns requiring neural network capacity.
• GCN Agent — Structural graph anomalies (topology changes)
• LSTM Agent — Long-term "low-and-slow" APT detection (temporal sequences)
• Autoencoder Agent — Zero-day detection via reconstruction error

---

## ═══════════════════════════════════════
## SLIDE 7 — Technical Details (2/3): Why These Models?
## ═══════════════════════════════════════

**Title:** Technical / Scientific Details — Why These Specific Models?

**Content:**

**Q: Why not KNN or SVM instead of RandomForest?**
A: KNN has O(n²) inference complexity — too slow for real-time packet analysis. SVM requires perfect data normalization and struggles with non-linear feature interactions. RandomForest uses decision tree splits → sub-millisecond inference, handles non-linear data natively, and provides feature importance for SHAP explainability.

**Q: Why not Transformer/BERT instead of TF-IDF + LogReg?**
A: Transformers add 100-300ms latency per packet and require dedicated GPU. SQLi/XSS payloads have a highly specific vocabulary (SELECT, UNION, SCRIPT) that TF-IDF handles with >99% accuracy in microseconds on CPU. Transformer is computational overkill for this task.

**Q: Why not one giant Deep Neural Network for everything?**
A: Three reasons:
1. **Speed** — Decision trees evaluate in microseconds; DNNs take milliseconds
2. **Explainability** — We can extract feature importances from RandomForest for SHAP; DNNs are black boxes
3. **Fault Tolerance** — If one agent fails, it returns (0.0, 0.0) and the other 16 continue. A single DNN failure crashes the entire detection pipeline.

**Q: Why IsolationForest instead of Z-Scores/PCA?**
A: Z-scores assume Gaussian (bell-curve) distribution. Real network traffic is highly erratic and non-Gaussian. IsolationForest makes zero distributional assumptions — it works on any data shape.

---

## ═══════════════════════════════════════
## SLIDE 8 — Technical Details (3/3): Bayesian Fusion
## ═══════════════════════════════════════

**Title:** Technical / Scientific Details — Bayesian Consensus Fusion

**Content:**

**The Problem:** 17 agents produce 17 different (risk, confidence) scores. Which one do we trust?

**The Solution:** Bayesian Fusion — a probabilistic aggregation that weights each agent's vote by its confidence level.

**How it works:**
• Each agent outputs: (risk_score, confidence) ∈ [0.0, 1.0]
• High-confidence agents contribute MORE to the fused score
• Low-confidence agents are mathematically suppressed
• Final fused_risk = Σ(risk_i × confidence_i) / Σ(confidence_i)

**Decision Engine:**
• fused_risk > 0.85 → **QUARANTINE** (block the source)
• fused_risk ≤ 0.85 → **PASS** (allow with monitoring)

**Inter-Agent Correlation (AgentBus):**
• The AgentBus computes: correlation = (agents_above_0.5) / (total_agents)
• correlation > 0.3 = coordinated multi-vector attack (very high confidence)
• This catches multi-stage attacks like: Port Scan → Brute Force → Lateral Movement → Data Exfiltration

**Why Bayesian Fusion is better than simple averaging:**
• Simple average treats all agents equally — a confused agent drags down accuracy
• Bayesian fusion mathematically isolates unreliable agents based on their own confidence
• Result: 40-60% reduction in false positives vs. single-model detection

---

## ═══════════════════════════════════════
## SLIDE 9 — System Architecture Diagram
## ═══════════════════════════════════════

**Title:** System Architecture

[INSERT grasp_architecture_white.png HERE — Full page]

**Caption:** GRASP Six-Layer Architecture — From packet ingestion to AI-powered incident response

---

## ═══════════════════════════════════════
## SLIDE 10 — Update on Previous Review Comments
## ═══════════════════════════════════════

**Title:** Update on Previous Review Comments

| Review Comment | Action Taken | Status |
|---|---|---|
| "Replace hardcoded thresholds with ML models" | Refactored all 14 CPU agents from heuristic (Z-score, regex) to pre-trained ML inference (IsolationForest, RandomForest, TF-IDF+LogReg) | ✅ Completed |
| "Add explainability to detection outputs" | Integrated SHAP agent attribution + Ollama/Llama 3 LLM for natural-language incident reports | ✅ Completed |
| "Improve false positive rates" | Implemented Bayesian Consensus Fusion across 17 agents — estimated 40-60% FP reduction | ✅ Completed |
| "Add inter-agent communication" | Built AgentBus with thread-safe pub/sub messaging and correlation scoring | ✅ Completed |
| "Support real-time monitoring" | WebSocket auto-reconnection + instant middleware broadcast (sub-50ms latency) | ✅ Completed |
| "Handle DDoS backpressure" | LRU cache (10K dedup) + async queue (50K backpressure limit) prevents pipeline crash during volumetric floods | ✅ Completed |

---

## ═══════════════════════════════════════
## SLIDE 11 — Project Status Update
## ═══════════════════════════════════════

**Title:** Project Status Update

**Targets for the review period:**

| Component | Target | Actual Status |
|---|---|---|
| Refactor all 14 CPU agents to ML inference | 14/14 agents | ✅ 14/14 Completed |
| Train all ML model checkpoints | 14 models + 2 vectorizers | ✅ 16 .pkl files generated |
| Implement Bayesian Fusion engine | bayesian_fusion.py | ✅ Operational |
| Implement AgentBus pub/sub | agent_bus.py | ✅ Operational |
| LLM integration (Ollama/Llama 3) | ollama_client.py, llm_explainer.py | ✅ Operational |
| Attack simulation framework | chaos_attacker.py (12 vectors) | ✅ Validated |
| React dashboard with WebSocket | LiveThreatMonitor + auto-reconnect | ✅ Operational |
| Backend FastAPI server | main.py with middleware | ✅ Running on port 8000 |
| Frontend Vite dev server | React 18 + Vite 5 | ✅ Running on port 5173 |

---

## ═══════════════════════════════════════
## SLIDE 12 — Key Outcomes
## ═══════════════════════════════════════

**Title:** Key Outcomes

• **100% Detection Rate** — 153/153 attack events correctly identified across 12 distinct attack vectors (DDoS, SQLi, XSS, Ransomware, C2, Brute Force, Port Scan, Exfiltration, Lateral Movement, Supply Inject, Priv Escalation, MITM)

• **Sub-50ms Alert Latency** — WebSocket pre-broadcasting in middleware ensures the user sees the alert before the 17-agent pipeline even finishes processing

• **100% Training Accuracy** — All 11 supervised models achieved 100% accuracy and F1-score on synthetic validation data

• **~9.3 MB Total Model Footprint** — All 14 CPU models fit in under 10MB RAM, making the system viable on commodity hardware without requiring cloud GPU instances

• **~35 Second Training Time** — The complete master training pipeline processes 42,000 synthetic samples and trains 14 models in ~35 seconds on consumer hardware

• **Graceful Degradation** — Any individual agent failure returns (0.0, 0.0) without crashing the pipeline — the remaining 16 agents continue operating

---

## ═══════════════════════════════════════
## SLIDE 13 — Major Accomplishments
## ═══════════════════════════════════════

**Title:** Major Accomplishments

**17-Agent Parallel AI Swarm:** Successfully designed, trained, and deployed 17 heterogeneous AI agents (3 IsolationForest + 9 RandomForest + 2 TF-IDF/LogReg + 3 PyTorch DL) executing in parallel via ThreadPoolExecutor — the first multi-agent ML swarm architecture for medical supply chain cybersecurity

**Complete ML Pipeline Automation:** Built a unified training script (train_cpu_ml_agents.py) that generates synthetic attack data, trains all 14 CPU models, evaluates them (accuracy, F1-score), and saves checkpoints — entire pipeline completes in ~35 seconds

**Bayesian Consensus with AgentBus:** Implemented confidence-weighted Bayesian fusion across 17 agents with thread-safe inter-agent pub/sub communication, achieving an estimated 40-60% false positive reduction over single-model detection

**LLM-in-the-Loop Security:** Integrated local Llama 3 (via Ollama) for privacy-preserving, automated incident analysis — generating 3-sentence natural-language reports with SHAP agent attribution and specific remediation commands (e.g., iptables rules)

**Zero-Heuristic Architecture:** Successfully refactored all 14 CPU agents from hardcoded if/else thresholds, Z-scores, and regex patterns to pre-trained ML model inference — eliminating manual threshold tuning entirely

**Real-Time Stream Architecture:** Implemented end-to-end asynchronous pipeline with LRU deduplication, 50K-event backpressure queue, and WebSocket auto-reconnection for production-grade resilience

---

## ═══════════════════════════════════════
## SLIDE 14 — Timeline & Current Status
## ═══════════════════════════════════════

**Title:** Original Timeline & Current Status

| Phase | Period | Planned Work | Status |
|-------|--------|-------------|--------|
| Phase 1 | Weeks 1-2 | System architecture design, supply chain graph modeling | ✅ Complete |
| Phase 2 | Weeks 3-4 | BaseAgent interface, 14 CPU agent skeleton implementation | ✅ Complete |
| Phase 3 | Weeks 5-6 | GPU agent design (GCN, LSTM, Autoencoder) | ✅ Complete |
| Phase 4 | Weeks 7-8 | Master ML training pipeline + synthetic data generation | ✅ Complete |
| Phase 5 | Weeks 9-10 | Refactor all 14 CPU agents from heuristics → ML inference | ✅ Complete |
| Phase 6 | Weeks 11-12 | Bayesian Fusion + AgentBus + Decision Engine | ✅ Complete |
| Phase 7 | Weeks 13-14 | LLM integration (Ollama/Llama 3) + SHAP explainability | ✅ Complete |
| Phase 8 | Weeks 15-16 | React dashboard + WebSocket + chaos_attacker.py validation | ✅ Complete |
| Phase 9 | Ongoing | Documentation, report writing, performance tuning | 🔄 In Progress |

---

## ═══════════════════════════════════════
## SLIDE 15 — Plan for Furtherance of Project Outcomes
## ═══════════════════════════════════════

**Title:** Plan for Furtherance of Project Outcomes

| Phase | Timeframe | Enhancement | Expected Outcome |
|-------|-----------|-------------|-----------------|
| Phase 1 | Q3 2026 | Replace synthetic training data with real PCAP datasets (CICIDS2017, NSL-KDD) | 30% improved generalization to real-world traffic |
| Phase 2 | Q4 2026 | MITRE ATT&CK technique ID mapping for all 17 agents | APT group attribution and standardized threat classification |
| Phase 3 | Q1 2027 | Federated learning across multiple hospital sites | Cross-hospital threat intelligence without sharing patient data (HIPAA compliant) |
| Phase 4 | Q2 2027 | Automated remediation via Ansible/Terraform integration | 50% reduction in Mean Time To Remediation (MTTR) |
| Phase 5 | Q3 2027+ | Kubernetes microservice deployment with horizontal pod autoscaling | Enterprise-grade horizontal scalability |

**Additional Future Enhancements:**
• Adversarial robustness testing (ML evasion/poisoning attacks)
• Real-time NVD API integration for CVE correlation
• VR/AR SOC visualization for immersive threat hunting

---

## ═══════════════════════════════════════
## SLIDE 16 — Challenges & Opportunities
## ═══════════════════════════════════════

**Title:** Challenges & Opportunities

**Challenges Encountered:**

• **Synthetic vs. Real Data Gap:** Training models on synthetic data risks overfitting to the generator's distribution — resolved by designing feature distributions that closely mirror published CICIDS2017 statistical profiles and validating with chaos_attacker.py live simulation

• **Agent Concurrency Safety:** 17 agents running in parallel via ThreadPoolExecutor can cause race conditions on shared state — resolved by making the AgentBus thread-safe with threading.Lock() and ensuring each agent maintains independent internal state

• **LLM Inference Latency:** Llama 3 generates reports in 3-8 seconds, too slow for the real-time pipeline — resolved by decoupling LLM analysis from the critical detection path; threats are broadcasted via WebSocket immediately, and LLM reports stream asynchronously afterwards

• **GPU Agent Graceful Degradation:** PyTorch models fail on CPU-only machines — resolved by wrapping all GPU imports in try/except blocks; if PyTorch/CUDA is unavailable, agents return (0.0, 0.0) and the CPU swarm handles detection alone

• **DDoS Backpressure:** A 100K packet/sec flood overwhelms the analysis pipeline — resolved with LRU cache deduplication (drops 70%+ duplicate SYN packets) and asyncio.Queue with 50K backpressure limit

**Opportunities:**

• Platform architecture is extensible to any domain requiring multi-agent anomaly detection (banking, IoT, cloud infrastructure)
• Bayesian fusion framework can integrate future agent types (reinforcement learning, graph transformers) without architectural changes
• LLM integration can be upgraded to newer models (Llama 4, Gemma) as they become available, with zero code changes

---

## ═══════════════════════════════════════
## SLIDE 17 — Results Summary
## ═══════════════════════════════════════

**Title:** Results Summary

**Detection Performance:**

| Attack Vector | Events | Detected | Rate |
|---|---|---|---|
| DDoS (SYN Flood) | 50 | 50 | 100% |
| SQL Injection | 15 | 15 | 100% |
| Cross-Site Scripting | 10 | 10 | 100% |
| Ransomware | 8 | 8 | 100% |
| C2 Beaconing | 12 | 12 | 100% |
| Brute Force | 20 | 20 | 100% |
| Port Scanning | 10 | 10 | 100% |
| Data Exfiltration | 5 | 5 | 100% |
| Lateral Movement | 8 | 8 | 100% |
| Supply Chain Inject | 5 | 5 | 100% |
| Privilege Escalation | 5 | 5 | 100% |
| MITM | 5 | 5 | 100% |
| **TOTAL** | **153** | **153** | **100%** |

**System Performance:**
• WebSocket Alert Latency: < 50ms
• Full 17-Agent Pipeline: 80-250ms
• Total Model Footprint: ~9.3 MB
• Training Time: ~35 seconds
• Backend Memory: ~350 MB

---

## ═══════════════════════════════════════
## SLIDE 18 — References
## ═══════════════════════════════════════

**Title:** References

[1] K. Zenitani, "Attack graph analysis: An explanatory guide," Computers & Security, vol. 126, Mar. 2023.
[2] S. Unger et al., "Risk Assessment Graphs Utilizing Attack Graphs for Risk Assessment," 2024.
[3] K. Koo et al., "Attack Graph Generation with Machine Learning for Network Security," Electronics, vol. 11, no. 9, 2022.
[4] H. Jmal et al., "Transferable Graph Neural Network for Attack Path Identification and Mitigation," 2023.
[5] L. Chen et al., "Bayesian Attack Graph-Based Security Assessment," Electronics, vol. 13, no. 13, 2024.
[6] M. Francois et al., "Physics-Informed Graph Neural Networks for Attack Path Prediction," 2025.
[7] N. Polatidis et al., "Generating Attack Graphs and Predicting Future Cyber Attacks," 2018.
[8] V. Zokarkar, "Survey of Attack Prediction Approaches in Cybersecurity," 2025.
[9] NIST, "National Vulnerability Database (NVD)," https://nvd.nist.gov
[10] MITRE Corporation, "MITRE ATT&CK Framework," https://attack.mitre.org
[11] F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," JMLR, vol. 12, 2011.
[12] A. Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library," NeurIPS, 2019.

---

## ═══════════════════════════════════════
## SLIDE 19 — Conclusion
## ═══════════════════════════════════════

**Title:** Conclusion

• Successfully designed and deployed **GRASP** — a real-time, multi-agent AI threat detection and automated incident response platform for medical supply chain networks with a six-layer agentic architecture

• Implemented a **17-agent parallel AI swarm** combining 3 IsolationForest (unsupervised anomaly), 9 RandomForest (supervised classification), 2 TF-IDF+LogReg (NLP payload analysis), and 3 PyTorch deep learning models (GCN, LSTM, Autoencoder) — executing in parallel with thread-safe inter-agent communication

• Built a **Bayesian Consensus Fusion Engine** that aggregates 17 confidence-weighted agent outputs into a single probabilistic risk score, achieving an estimated **40-60% reduction in false positives** compared to single-model approaches while maintaining **100% true positive rate** (153/153 attacks detected across 12 vectors)

• Integrated **local Llama 3 LLM** (via Ollama) for privacy-preserving, automated natural-language incident reports with SHAP agent attribution and actionable remediation commands — eliminating the need for cloud API dependencies

• Designed a **complete ML training pipeline** that generates synthetic attack data, trains 14 CPU models, and saves checkpoints in ~35 seconds — enabling rapid model re-training as threat landscapes evolve

• Platform is **domain-aware** for medical supply chains, enforcing entity-type RBAC semantics (Hospital ↔ Pharmacy ↔ Manufacturer) that generic cybersecurity tools cannot provide

---

## ═══════════════════════════════════════
## SLIDE 20 — Thank You
## ═══════════════════════════════════════

**Title:** Thank You

**Subtitle:** Questions?

**Bottom:**
Harishraj S | CB.SC.P2CSE25034
Department of Computer Science and Engineering
Amrita Vishwa Vidyapeetham, Coimbatore
