"""
Generate GRASP 10-Agent Architecture Flow Diagram
Reference: grasp_architecture_white.png
Upgraded with exactly 10 agents in Layer 3:
- Group A (All 3 kept): DDoS, Behavior, Spike
- Group B (4 kept, 5 harder removed): Port Scan, Brute Force, C2 Beacon, Ransomware
- Group C (2 kept): SQLi/XSS, Signature
- Group D (1 kept, 2 harder removed): GCN
Total in L3: 10 Agents. Harder 7 removed: Lateral Mvmt, Exfiltration, MITM, Supply Inject, Priv Esc, LSTM (Temporal APT), Autoencoder (Zero-Day).
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(10.5, 10.5), dpi=200)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# Canvas boundaries
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica', 'Segoe UI']

def draw_rounded_box(ax, x, y, w, h, bg_color, border_color, border_width=1.5, radius=1.6, zorder=2):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.15,rounding_size={radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=border_width,
        zorder=zorder
    )
    ax.add_patch(box)
    return box

# ==========================================
# 0. TOP: NETWORK TRAFFIC INPUT
# ==========================================
top_y = 92.5
top_h = 6.2
draw_rounded_box(ax, 2, top_y, 93, top_h, '#F8FAFC', '#CBD5E1', border_width=1.5, radius=1.5, zorder=2)
ax.text(4.0, top_y + top_h/2, "NETWORK TRAFFIC INPUT", fontsize=11, fontweight='bold', va='center', ha='left', color='#0F172A', zorder=10)

# Laptop Icon
lx, ly = 48, top_y + 3.8
ax.plot([lx - 3.2, lx + 3.2], [ly - 1.2, ly - 1.2], color='#0F172A', lw=2.5, zorder=4)
ax.plot([lx - 2.5, lx + 2.5], [ly - 1.0, ly - 1.0], color='#334155', lw=1.5, zorder=4)
ax.add_patch(patches.Rectangle((lx - 2.3, ly - 0.9), 4.6, 2.7, facecolor='#0F172A', edgecolor='#0F172A', zorder=4))
ax.add_patch(patches.Rectangle((lx - 2.0, ly - 0.6), 4.0, 2.1, facecolor='#E2E8F0', edgecolor='#0F172A', lw=0.5, zorder=5))

ax.text(lx + 4.2, top_y + 3.8, "Attacker", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#0F172A', zorder=10)
ax.text(lx + 4.2, top_y + 1.8, "(chaos_attacker.py / Kali Linux)", fontsize=8.5, va='center', ha='left', color='#475569', zorder=10)

# Arrow Top -> L1
ax.annotate('', xy=(48, 91.5), xytext=(48, 92.5),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.5, headwidth=6, headlength=6), zorder=8)

# ==========================================
# 1. LAYER 1: INGESTION & PRE-CLASSIFICATION
# ==========================================
l1_y = 83.2
l1_h = 7.6
draw_rounded_box(ax, 2, l1_y, 93, l1_h, '#E0F2FE', '#0284C7', border_width=1.8, radius=1.8, zorder=2)
ax.text(3.5, l1_y + l1_h - 2.4, "L1: INGESTION &", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#0369A1', zorder=10)
ax.text(3.5, l1_y + 2.4, "PRE-CLASSIFICATION", fontsize=9.5, fontweight='bold', va='center', ha='left', color='#0369A1', zorder=10)

draw_rounded_box(ax, 26, l1_y + 1.4, 22, 4.8, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(37, l1_y + 3.8, "Scapy Live Capture", fontsize=10, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

ax.annotate('', xy=(52.2, l1_y + 3.8), xytext=(48.2, l1_y + 3.8),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)

draw_rounded_box(ax, 52.8, l1_y + 1.4, 39, 4.8, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(72.3, l1_y + 3.8, "FastAPI Attack Detection Middleware", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Arrow L1 -> L2
ax.annotate('', xy=(48, 81.9), xytext=(48, 83.0),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.5, headwidth=6, headlength=6), zorder=8)

# ==========================================
# 2. LAYER 2: BUFFERING & QUEUE
# ==========================================
l2_y = 73.6
l2_h = 7.6
draw_rounded_box(ax, 2, l2_y, 93, l2_h, '#CCFBF1', '#0D9488', border_width=1.8, radius=1.8, zorder=2)
ax.text(3.5, l2_y + l2_h - 2.4, "L2: BUFFERING", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#0F766E', zorder=10)
ax.text(3.5, l2_y + 2.4, "& QUEUE", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#0F766E', zorder=10)

draw_rounded_box(ax, 22, l2_y + 1.4, 19, 4.8, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(31.5, l2_y + 4.3, "LRU Cache", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)
ax.text(31.5, l2_y + 2.4, "(10K dedup)", fontsize=8.5, va='center', ha='center', color='#475569', zorder=10)

ax.annotate('', xy=(44.2, l2_y + 3.8), xytext=(41.2, l2_y + 3.8),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)

draw_rounded_box(ax, 44.8, l2_y + 1.4, 23, 4.8, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(56.3, l2_y + 4.3, "asyncio.Queue", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)
ax.text(56.3, l2_y + 2.4, "(50K backpressure)", fontsize=8.5, va='center', ha='center', color='#475569', zorder=10)

ax.annotate('', xy=(71.0, l2_y + 3.8), xytext=(68.0, l2_y + 3.8),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)

draw_rounded_box(ax, 71.6, l2_y + 1.4, 20.8, 4.8, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(82.0, l2_y + 3.8, "Stream Consumer", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Arrow L2 -> L3
ax.annotate('', xy=(48, 72.3), xytext=(48, 73.4),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.5, headwidth=6, headlength=6), zorder=8)

# ==========================================
# 3. LAYER 3: 10-AGENT PARALLEL SWARM
# ==========================================
l3_y = 42.0
l3_h = 30.2
draw_rounded_box(ax, 2, l3_y, 93, l3_h, '#DCFCE7', '#16A34A', border_width=1.8, radius=1.8, zorder=2)
ax.text(3.5, l3_y + l3_h - 2.6, "L3: 10-AGENT PARALLEL SWARM", fontsize=11, fontweight='bold', va='center', ha='left', color='#15803D', zorder=10)

# AgentBus pill
bus_w, bus_h = 32, 4.4
bus_x = 48 - bus_w/2
bus_y = l3_y + l3_h - 5.4
draw_rounded_box(ax, bus_x, bus_y, bus_w, bus_h, '#FFFFFF', '#0F172A', border_width=1.5, radius=2.2, zorder=4)
ax.text(48, bus_y + 2.8, "AgentBus", fontsize=10, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)
ax.text(48, bus_y + 1.2, "(Thread-Safe Pub/Sub)", fontsize=8.0, va='center', ha='center', color='#475569', zorder=10)

g_y = l3_y + 1.5
g_h = 21.0

# Group A (IsolationForest x3) - ALL 3 KEPT
gA_x, gA_w = 3.2, 20.8
draw_rounded_box(ax, gA_x, g_y, gA_w, g_h, '#BBF7D0', '#15803D', border_width=1.5, radius=1.5, zorder=3)
ax.text(gA_x + gA_w/2, g_y + g_h - 1.8, "Group A", fontsize=10, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)
ax.text(gA_x + gA_w/2, g_y + g_h - 3.6, "IsolationForest ×3", fontsize=8.6, fontweight='bold', va='center', ha='center', color='#15803D', zorder=10)

gA_agents = ["DDoS", "Behavior", "Spike"]
for idx, ag in enumerate(gA_agents):
    ag_y = g_y + g_h - 8.2 - idx * 4.6
    draw_rounded_box(ax, gA_x + 1.6, ag_y, gA_w - 3.2, 3.8, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
    ax.text(gA_x + gA_w/2, ag_y + 1.9, ag, fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Group B (RandomForest x4) - 4 EASY DEMO AGENTS KEPT
gB_x, gB_w = 25.2, 36.8
draw_rounded_box(ax, gB_x, g_y, gB_w, g_h, '#86EFAC', '#16A34A', border_width=1.5, radius=1.5, zorder=3)
ax.text(gB_x + gB_w/2, g_y + g_h - 1.8, "Group B", fontsize=10, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)
ax.text(gB_x + gB_w/2, g_y + g_h - 3.6, "RandomForest ×4", fontsize=8.6, fontweight='bold', va='center', ha='center', color='#15803D', zorder=10)

col_w = gB_w/2 - 2.2
b_row1_y = g_y + g_h - 8.4
b_row2_y = g_y + g_h - 13.8

# Port Scan
draw_rounded_box(ax, gB_x + 1.6, b_row1_y, col_w, 4.2, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
ax.text(gB_x + 1.6 + col_w/2, b_row1_y + 2.1, "Port Scan", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Brute Force
draw_rounded_box(ax, gB_x + gB_w/2 + 0.6, b_row1_y, col_w, 4.2, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
ax.text(gB_x + gB_w/2 + 0.6 + col_w/2, b_row1_y + 2.1, "Brute Force", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# C2 Beacon
draw_rounded_box(ax, gB_x + 1.6, b_row2_y, col_w, 4.2, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
ax.text(gB_x + 1.6 + col_w/2, b_row2_y + 2.1, "C2 Beacon", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Ransomware
draw_rounded_box(ax, gB_x + gB_w/2 + 0.6, b_row2_y, col_w, 4.2, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
ax.text(gB_x + gB_w/2 + 0.6 + col_w/2, b_row2_y + 2.1, "Ransomware", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Subtitle pill in Group B
draw_rounded_box(ax, gB_x + 2.5, g_y + 1.0, gB_w - 5.0, 2.8, '#F0FDF4', '#15803D', border_width=1.0, radius=0.8, zorder=4)
ax.text(gB_x + gB_w/2, g_y + 2.4, "Fast Attack-Response Demo Set", fontsize=7.8, fontweight='bold', va='center', ha='center', color='#166534', zorder=10)

# Group C (TF-IDF + LogReg x2) - ALL 2 KEPT
gC_x, gC_w = 63.2, 17.2
draw_rounded_box(ax, gC_x, g_y, gC_w, g_h, '#D9F99D', '#65A30D', border_width=1.5, radius=1.5, zorder=3)
ax.text(gC_x + gC_w/2, g_y + g_h - 1.8, "Group C", fontsize=10, fontweight='bold', va='center', ha='center', color='#365314', zorder=10)
ax.text(gC_x + gC_w/2, g_y + g_h - 3.6, "TF-IDF + LogReg ×2", fontsize=8.0, fontweight='bold', va='center', ha='center', color='#4D7C0F', zorder=10)

gC_agents = ["SQLi/XSS", "Signature"]
for idx, ag in enumerate(gC_agents):
    ag_y = g_y + g_h - 8.4 - idx * 5.4
    draw_rounded_box(ax, gC_x + 1.4, ag_y, gC_w - 2.8, 4.2, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
    ax.text(gC_x + gC_w/2, ag_y + 2.1, ag, fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Group D (PyTorch DL x1) - GCN KEPT
gD_x, gD_w = 81.6, 13.0
draw_rounded_box(ax, gD_x, g_y, gD_w, g_h, '#4ADE80', '#15803D', border_width=1.5, radius=1.5, zorder=3)
ax.text(gD_x + gD_w/2, g_y + g_h - 1.8, "Group D", fontsize=10, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)
ax.text(gD_x + gD_w/2, g_y + g_h - 3.6, "PyTorch DL ×1", fontsize=8.0, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)

draw_rounded_box(ax, gD_x + 1.4, g_y + g_h - 8.4, gD_w - 2.8, 4.2, '#FFFFFF', '#0F172A', border_width=1.2, radius=1.0, zorder=4)
ax.text(gD_x + gD_w/2, g_y + g_h - 6.3, "GCN", fontsize=10, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

draw_rounded_box(ax, gD_x + 1.2, g_y + 2.0, gD_w - 2.4, 7.0, '#F0FDF4', '#15803D', border_width=1.0, radius=0.8, zorder=4)
ax.text(gD_x + gD_w/2, g_y + 6.8, "Graph", fontsize=8.0, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)
ax.text(gD_x + gD_w/2, g_y + 5.0, "Topology", fontsize=8.0, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)
ax.text(gD_x + gD_w/2, g_y + 3.2, "Classifier", fontsize=8.0, fontweight='bold', va='center', ha='center', color='#14532D', zorder=10)

# Connect AgentBus to the 4 groups (Curved Arrows from bottom edge of AgentBus)
ax.annotate('', xy=(gA_x + gA_w/2, g_y + g_h), xytext=(bus_x + 1.5, bus_y + 1.0),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.16", color="#0F172A", lw=1.6), zorder=8)
ax.annotate('', xy=(gB_x + gB_w/2, g_y + g_h), xytext=(bus_x + 9, bus_y),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.06", color="#0F172A", lw=1.6), zorder=8)
ax.annotate('', xy=(gC_x + gC_w/2, g_y + g_h), xytext=(bus_x + bus_w - 9, bus_y),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.06", color="#0F172A", lw=1.6), zorder=8)
ax.annotate('', xy=(gD_x + gD_w/2, g_y + g_h), xytext=(bus_x + bus_w - 1.5, bus_y + 1.0),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.16", color="#0F172A", lw=1.6), zorder=8)

# Arrow L3 -> L4
ax.annotate('', xy=(48, 40.7), xytext=(48, 41.8),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.5, headwidth=6, headlength=6), zorder=8)

# ==========================================
# 4. LAYER 4: BAYESIAN CONSENSUS
# ==========================================
l4_y = 31.4
l4_h = 8.6
draw_rounded_box(ax, 2, l4_y, 93, l4_h, '#FEF3C7', '#F59E0B', border_width=1.8, radius=1.8, zorder=2)
ax.text(3.5, l4_y + l4_h - 2.8, "L4: BAYESIAN", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#B45309', zorder=10)
ax.text(3.5, l4_y + 2.8, "CONSENSUS", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#B45309', zorder=10)

draw_rounded_box(ax, 22, l4_y + 1.8, 28, 5.2, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(36, l4_y + 4.9, "Bayesian Fusion Engine", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)
ax.text(36, l4_y + 3.0, "(confidence-weighted)", fontsize=8.5, va='center', ha='center', color='#475569', zorder=10)

ax.annotate('', xy=(53.5, l4_y + 4.4), xytext=(50.4, l4_y + 4.4),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)

draw_rounded_box(ax, 54, l4_y + 1.8, 20, 5.2, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(64, l4_y + 4.4, "Decision Engine", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Branches to QUARANTINE / PASS
ax.annotate('', xy=(78.2, l4_y + 5.7), xytext=(74.5, l4_y + 4.7),
            arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)
ax.text(79.0, l4_y + 5.7, "QUARANTINE", fontsize=9.5, fontweight='bold', va='center', ha='left', color='#DC2626', zorder=10)

ax.annotate('', xy=(78.2, l4_y + 3.1), xytext=(74.5, l4_y + 4.1),
            arrowprops=dict(facecolor='#16A34A', edgecolor='#16A34A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)
ax.text(79.0, l4_y + 3.1, "PASS", fontsize=9.5, fontweight='bold', va='center', ha='left', color='#16A34A', zorder=10)

# Arrow L4 -> L5
ax.annotate('', xy=(48, 30.1), xytext=(48, 31.2),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.5, headwidth=6, headlength=6), zorder=8)

# ==========================================
# 5. LAYER 5: AI EXPLAINABILITY
# ==========================================
l5_y = 20.8
l5_h = 8.6
draw_rounded_box(ax, 2, l5_y, 93, l5_h, '#F3E8FF', '#9333EA', border_width=1.8, radius=1.8, zorder=2)
ax.text(3.5, l5_y + l5_h - 2.8, "L5: AI", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#7E22CE', zorder=10)
ax.text(3.5, l5_y + 2.8, "EXPLAINABILITY", fontsize=9.5, fontweight='bold', va='center', ha='left', color='#7E22CE', zorder=10)

draw_rounded_box(ax, 22, l5_y + 1.8, 17, 5.2, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(30.5, l5_y + 4.9, "SHAP Agent", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)
ax.text(30.5, l5_y + 3.0, "Attribution", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

ax.annotate('', xy=(42.2, l5_y + 4.4), xytext=(39.2, l5_y + 4.4),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)

draw_rounded_box(ax, 42.8, l5_y + 1.8, 23, 5.2, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(54.3, l5_y + 4.9, "Ollama + Llama 3.1", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)
ax.text(54.3, l5_y + 3.0, "(localhost:11434)", fontsize=8.5, va='center', ha='center', color='#475569', zorder=10)

ax.annotate('', xy=(69.0, l5_y + 4.4), xytext=(66.0, l5_y + 4.4),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.4, headwidth=5.5, headlength=5.5), zorder=8)

draw_rounded_box(ax, 69.6, l5_y + 1.8, 23.6, 5.2, '#FFFFFF', '#0F172A', border_width=1.4, radius=1.2, zorder=3)
ax.text(81.4, l5_y + 4.4, "Remediation Engine", fontsize=9.5, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# Arrow L5 -> L6
ax.annotate('', xy=(48, 19.5), xytext=(48, 20.6),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.5, headwidth=6, headlength=6), zorder=8)

# ==========================================
# 6. LAYER 6: REACT DASHBOARD
# ==========================================
l6_y = 4.8
l6_h = 14.4
draw_rounded_box(ax, 2, l6_y, 74, l6_h, '#EFF6FF', '#2563EB', border_width=1.8, radius=1.8, zorder=2)
ax.text(3.5, l6_y + l6_h - 4.5, "L6: REACT", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#1D4ED8', zorder=10)
ax.text(3.5, l6_y + l6_h - 7.5, "DASHBOARD", fontsize=10.5, fontweight='bold', va='center', ha='left', color='#1D4ED8', zorder=10)

# Inner sub-container
in_w, in_h = 56, 11.8
in_x, in_y = 18.5, l6_y + 1.3
draw_rounded_box(ax, in_x, in_y, in_w, in_h, '#DBEAFE', '#3B82F6', border_width=1.3, radius=1.4, zorder=3)
ax.text(in_x + in_w/2, in_y + in_h - 1.8, "React 18 + Vite 5 + Zustand", fontsize=10, fontweight='bold', va='center', ha='center', color='#1E40AF', zorder=10)

# 3 Dashboard views
vw = 16.8
views = [
    ("Live Threat\nMonitor", in_x + 1.4),
    ("Network Topology\nGraph", in_x + 19.6),
    ("LLM Analysis\nDrawer", in_x + 37.8),
]
for label, vx in views:
    draw_rounded_box(ax, vx, in_y + 1.4, vw, 7.0, '#FFFFFF', '#0F172A', border_width=1.3, radius=1.0, zorder=4)
    ax.text(vx + vw/2, in_y + 4.9, label, fontsize=9.2, fontweight='bold', va='center', ha='center', color='#0F172A', zorder=10)

# ==========================================
# 7. WEBSOCKET INSTANT BROADCAST (Dashed line)
# ==========================================
ws_start_x = 92.0
ws_start_y = l1_y + 3.8
ws_mid_x = 96.5
ws_turn_y = l6_y + l6_h + 0.6
ws_entry_x = 72.0

# Path: from L1 middleware -> right to 96.5 -> down to 20.0 -> left to 72.0 -> down into L6 top
ax.plot([ws_start_x, ws_mid_x, ws_mid_x, ws_entry_x, ws_entry_x],
        [ws_start_y, ws_start_y, ws_turn_y, ws_turn_y, l6_y + l6_h],
        color='#0F172A', lw=1.5, ls='--', zorder=8)
ax.annotate('', xy=(ws_entry_x, l6_y + l6_h - 0.2), xytext=(ws_entry_x, l6_y + l6_h + 1.0),
            arrowprops=dict(facecolor='#0F172A', edgecolor='#0F172A', width=1.3, headwidth=5, headlength=5), zorder=8)

ax.text(ws_mid_x - 1.2, 53.0, "Instant WebSocket Broadcast",
        fontsize=8.5, fontweight='bold', color='#0F172A', rotation=90, va='center', ha='right', zorder=10,
        bbox=dict(boxstyle='square,pad=0.25', facecolor='#FFFFFF', edgecolor='#CBD5E1', lw=0.8))

# ==========================================
# 8. LEGEND BOX (Bottom Right)
# ==========================================
leg_x, leg_y, leg_w, leg_h = 77.2, 4.8, 17.8, 14.4
draw_rounded_box(ax, leg_x, leg_y, leg_w, leg_h, '#F8FAFC', '#94A3B8', border_width=1.2, radius=1.2, zorder=3)
ax.text(leg_x + leg_w/2, leg_y + leg_h - 1.6, "ARCHITECTURE LEGEND", fontsize=7.2, fontweight='bold', va='center', ha='center', color='#334155', zorder=10)

legend_items = [
    ("Layer Boundary", '#E0F2FE', '#0284C7'),
    ("Group A (IsoForest ×3)", '#BBF7D0', '#15803D'),
    ("Group B (RandForest ×4)", '#86EFAC', '#16A34A'),
    ("Group C (NLP LogReg ×2)", '#D9F99D', '#65A30D'),
    ("Group D (PyG GCN ×1)", '#4ADE80', '#15803D'),
]

for idx, (label, fcolor, ecolor) in enumerate(legend_items):
    item_y = leg_y + leg_h - 3.7 - idx * 2.0
    badge = FancyBboxPatch((leg_x + 1.2, item_y - 0.6), 3.0, 1.2,
                           boxstyle="round,pad=0.1,rounding_size=0.3",
                           facecolor=fcolor, edgecolor=ecolor, lw=1.0, zorder=4)
    ax.add_patch(badge)
    ax.text(leg_x + 4.8, item_y, label, fontsize=6.8, va='center', ha='left', color='#1E293B', zorder=10)

draw_rounded_box(ax, leg_x + 1.2, leg_y + 0.8, leg_w - 2.4, 2.2, '#ECFDF5', '#059669', border_width=1.0, radius=0.6, zorder=4)
ax.text(leg_x + leg_w/2, leg_y + 1.9, "10 Active Swarm Agents", fontsize=7.0, fontweight='bold', va='center', ha='center', color='#047857', zorder=10)

plt.tight_layout(pad=0.2)
plt.savefig('grasp_architecture_white_10agents.png', dpi=200, facecolor='#FFFFFF', edgecolor='none')
plt.savefig('grasp_architecture_10agents.svg', facecolor='#FFFFFF', edgecolor='none')
print("Successfully generated updated diagram!")
