import streamlit as st
import json
import time
import copy
import requests
import importlib.util
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib.units import cm

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Delhi's Digital Twin",
    page_icon="🚇",
    layout="wide"
)

st.markdown("""
<style>
/* ── CSS variables: auto-switch light / dark ── */
:root {
    --card-bg:      #f1f5f9;
    --card-border:  #cbd5e1;
    --text-primary: #0f172a;
    --text-muted:   #475569;
    --accent:       #22c55e;
    --tab-bg:       #e2e8f0;
}
@media (prefers-color-scheme: dark) {
    :root {
        --card-bg:      #1e293b;
        --card-border:  #334155;
        --text-primary: #f8fafc;
        --text-muted:   #94a3b8;
        --accent:       #22c55e;
        --tab-bg:       #1e293b;
    }
}
/* Streamlit dark-mode class override */
[data-theme="dark"] {
    --card-bg:      #1e293b;
    --card-border:  #334155;
    --text-primary: #f8fafc;
    --text-muted:   #94a3b8;
    --tab-bg:       #1e293b;
}

/* metric cards */
div[data-testid="metric-container"] {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 12px;
}

/* tab bar */
.stTabs [data-baseweb="tab-list"] {
    background: var(--tab-bg);
    border-radius: 8px;
}

/* inline HTML cards — use CSS vars so they flip automatically */
.dt-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.dt-card-label { color: var(--text-muted); font-size: 13px; margin-bottom: 4px; }
.dt-card-value { color: var(--accent);     font-size: 26px; font-weight: 700; }

.dt-legend-row {
    display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
}
.dt-legend-dot { width: 12px; height: 12px; border-radius: 50%; }
.dt-legend-name { color: var(--text-primary); }
.dt-legend-count { color: var(--text-muted); margin-left: auto; }

.dt-info-box {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 24px;
    margin-top: 16px;
}
.dt-info-title { color: var(--text-primary); font-size: 18px; font-weight: 600; margin-bottom: 12px; }
.dt-info-body  { color: var(--text-muted); line-height: 1.7; }

.dt-eq-box {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 16px;
    margin-top: 20px;
}
.dt-eq-label { color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.dt-eq-value { font-size: 40px; font-weight: 700; margin: 6px 0; }
.dt-eq-note  { color: var(--text-primary); font-size: 13px; }

.dt-sentiment-box {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 14px;
}
.dt-sentiment-label { color: var(--text-muted); font-size: 12px; text-transform: uppercase;
                       letter-spacing: 1px; margin-bottom: 8px; }
.dt-sentiment-track { flex: 1; background: var(--card-border); border-radius: 4px; height: 10px; }

.dt-score-card {
    background: var(--card-bg);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
}
.dt-score-label { color: var(--text-muted); font-size: 12px; }
.dt-score-value { font-size: 20px; font-weight: 700; }

.dt-best-banner {
    background: linear-gradient(135deg, #14532d, #166534);
    border: 1px solid #22c55e;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("🚇 Delhi's Digital Twin")
st.markdown("**Agent-Based Urban Policy Simulator** — LLM Agents · 100 Citizens · 12 Policies · Live Metro Animation")
st.divider()

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.header("⚙️ Controls")

    mode = st.radio("Mode", ["Single Policy", "Compare All Policies"], horizontal=False)

    if mode == "Single Policy":
        policy_type = st.radio("Policy Source", ["Preset", "Natural Language"], horizontal=True)

        if policy_type == "Preset":
            policy = st.selectbox("Choose Policy", [
                "── Classic Policies ──",
                "Free Metro Rides For Women",
                "50% Bus Fare Reduction",
                "Congestion Tax",
                "New Metro Line",
                "── New Policies ──",
                "Metro Operating Hours Extended to 2 AM",
                "Airport Express Fare Reduction",
                "Reserved Student Coaches",
                "Personal Carbon Budget",
                "Free Transit Birthdays",
                "Car-Free School Zones",
                "One-Ticket City",
                "Free EV Parking",
            ])
            custom_policy_str = None
        else:
            nl_input = st.text_area(
                "Describe your policy",
                placeholder="e.g. Subsidise e-rickshaws by 30% to reduce auto costs",
                height=100
            )
            custom_policy_str = nl_input if nl_input.strip() else None
            policy = nl_input if nl_input.strip() else "(enter policy above)"

    st.divider()
    use_llm = st.toggle("🤖 LLM Agent Reports", value=True,
                        help="Calls Claude to generate intelligent agent analysis")
    run_btn = st.button("🚀 Run Simulation", use_container_width=True, type="primary")

    st.divider()
    st.caption("Simulates 100 Delhi citizens across 5 archetypes using agent-based modelling. Each agent weighs cost, time, comfort, and safety to choose optimal transport.")

# =====================================================
# NLP POLICY PARSER
# =====================================================

def parse_nl_policy(text):
    """Call Claude to parse a natural language policy into simulation parameters."""
    prompt = f"""You are an urban policy simulation engine for Delhi, India.

A user described this transport policy: "{text}"

Map it to simulation parameters. The simulation has these transport modes with attributes (score 1-10):
- Metro: cost, time, comfort, safety
- Bus: cost, time, comfort, safety  
- Auto: cost, time, comfort, safety
- Walking: cost, time, comfort, safety

Higher score = better for that attribute. Current defaults:
Metro: cost=5, time=8, comfort=7, safety=8
Bus:   cost=8, time=5, comfort=4, safety=5
Auto:  cost=3, time=9, comfort=8, safety=6
Walking: cost=10, time=2, comfort=2, safety=7

Respond ONLY with valid JSON, no preamble, no markdown:
{{
  "name": "short policy name (max 5 words)",
  "effects": {{
    "ModeNameIfChanged": {{"attribute": new_value}}
  }},
  "explanation": "one sentence explaining how you mapped it"
}}

Only include modes that actually change. Only include attributes that change."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        data = resp.json()
        raw = data["content"][0]["text"].strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception as e:
        return None

# =====================================================
# LLM AGENT REPORTS
# =====================================================

AGENT_PROMPTS = {
    "government": (
        "You are the Delhi Government Policy Advisor. Analyse this simulation data and write a concise "
        "policy brief (3-4 paragraphs) with: recommendation (APPROVE/REVIEW/REJECT with reason), "
        "key metrics that support your decision, and one specific implementation suggestion."
    ),
    "transport": (
        "You are the Delhi Metro & Transport Authority Chief. Analyse this simulation data and write "
        "an operational brief (3-4 paragraphs) covering: capacity implications, recommended service "
        "changes, infrastructure needs, and risk factors."
    ),
    "environment": (
        "You are Delhi's Chief Environmental Officer. Analyse this simulation data and write an "
        "environmental impact assessment (3-4 paragraphs) covering: air quality impact, CO2 "
        "reduction estimate, comparison to Delhi's AQI targets, and long-term sustainability."
    ),
    "citizens": (
        "You are a Delhi Citizens Welfare Analyst. Analyse this simulation data and write a citizen "
        "impact report (3-4 paragraphs) covering: who benefits most, equity concerns, behavioural "
        "insights, and citizen satisfaction drivers."
    ),
    "business": (
        "You are a Delhi Urban Economics Analyst. Analyse this simulation data and write a business "
        "impact report (3-4 paragraphs) covering: footfall changes near transit corridors, "
        "economic opportunity, sectors that benefit, and risks for existing transport businesses."
    )
}

def get_llm_report(agent_name, results):
    system = AGENT_PROMPTS[agent_name]
    data_summary = json.dumps({
        "policy":               results["policy"],
        "transport_before":     results["transport_before"],
        "transport_after":      results["transport_after"],
        "transport_changes":    results["transport_changes"],
        "estimated_co2_reduction": results["estimated_co2_reduction"],
        "mobility_score":       results["mobility_score"],
        "mobility_breakdown":   results.get("mobility_breakdown", {}),
        "confidence_intervals": results.get("confidence_intervals", {}),
        "equity":               results.get("equity", {}),
        "time_of_day":          results.get("time_of_day", {}),
        "citizen_sentiment":    results.get("citizen_sentiment", {})
    }, indent=2)

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 600,
                "system": system,
                "messages": [{"role": "user", "content": f"Simulation data:\n{data_summary}\n\nWrite your report now."}]
            },
            timeout=20
        )
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception:
        return results.get(f"{agent_name}_report", "Report unavailable.")

# =====================================================
# CHART HELPERS
# =====================================================

def dark_fig(w=10, h=5):
    fig, ax = plt.subplots(figsize=(w,h))
    fig.patch.set_alpha(0)          # transparent — adapts to light/dark
    ax.set_facecolor("none")
    for s in ["top","right"]:   ax.spines[s].set_visible(False)
    for s in ["bottom","left"]: ax.spines[s].set_color("#94a3b8")
    ax.tick_params(colors="gray")
    return fig, ax


def plot_transport(before, after):
    modes = sorted(set(before.keys()) | set(after.keys()))
    bv = [before.get(m,0) for m in modes]
    av = [after.get(m,0)  for m in modes]
    x  = np.arange(len(modes))

    fig, ax = dark_fig(10, 5)
    ax.bar(x-0.2, bv, 0.4, label="Before", color="#3b82f6", alpha=0.9)
    bars = ax.bar(x+0.2, av, 0.4, label="After", color="#f97316", alpha=0.9)
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x()+bar.get_width()/2, h+0.3, str(int(h)),
                    ha="center", va="bottom", color="#f97316", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(modes, color="#cbd5e1", rotation=15, ha="right")
    ax.set_ylabel("Citizens")
    ax.set_title("Transport Distribution Change", pad=10)
    ax.legend(facecolor="#1e293b", labelcolor="#f8fafc", edgecolor="#334155")
    plt.tight_layout()
    return fig


def plot_co2(co2):
    fig, ax = dark_fig(5, 4)
    color = "#22c55e" if co2>20 else "#f59e0b" if co2>10 else "#ef4444"
    ax.bar(["CO2 Reduction"], [co2], color=color, width=0.4)
    ax.text(0, co2+0.3, str(co2), ha="center", va="bottom",
            color=color, fontsize=14, fontweight="bold")
    ax.set_ylabel("Score")
    ax.set_title("Environmental Impact", pad=10)
    plt.tight_layout()
    return fig


def plot_mobility_breakdown(bd):
    labels = ["Reduced\nCongestion", "Transit\nAdoption", "Cost\nSavings", "CO2\nReduction"]
    values = [bd["reduced_congestion"], bd["public_transit_adoption"],
              bd["cost_savings"],       bd["co2_reduction"]]
    colors_list = ["#3b82f6","#22c55e","#f59e0b","#8b5cf6"]

    fig, ax = dark_fig(8, 4)
    bars = ax.bar(labels, values, color=colors_list, width=0.5, alpha=0.9)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                f"+{val}", ha="center", va="bottom", color="#f8fafc", fontsize=11, fontweight="bold")
    ax.set_ylabel("Score Points")
    ax.set_title(f"Mobility Score Breakdown — Total: {bd['total']}", pad=10)
    plt.tight_layout()
    return fig


def plot_radar(results):
    axes = ["Mobility", "Environment", "Equity", "Economy", "Safety"]

    bd = results.get("mobility_breakdown", {})
    eq = results.get("equity", {})

    mobility_val    = min(10, results.get("mobility_score",0) / 10)
    environment_val = min(10, results.get("estimated_co2_reduction",0) / 5)
    equity_val      = min(10, eq.get("equity_index",50) / 10)
    economy_val     = min(10, results.get("transport_changes",0) / 10)
    safety_val      = min(10, (results["transport_after"].get("Metro",0) +
                               results["transport_after"].get("Bus",0)) / 10)

    values = [mobility_val, environment_val, equity_val, economy_val, safety_val]
    values += values[:1]

    N = len(axes)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5,5), subplot_kw={"polar": True})
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes, size=10)
    ax.set_yticklabels([])
    ax.spines["polar"].set_color("#94a3b8")

    ax.plot(angles, values, color="#22c55e", linewidth=2)
    ax.fill(angles, values, color="#22c55e", alpha=0.2)
    ax.set_title(f"{results['policy'][:25]}", pad=20, size=11)
    plt.tight_layout()
    return fig


def plot_confidence(ci_data):
    labels  = ["Mobility Score", "CO2 Reduction", "Mode Switches"]
    means   = [ci_data["mobility"][0], ci_data["co2"][0], ci_data["switches"][0]]
    stds    = [ci_data["mobility"][1], ci_data["co2"][1],  ci_data["switches"][1]]
    mins    = [ci_data["mobility"][2], ci_data["co2"][2],  ci_data["switches"][2]]
    maxs    = [ci_data["mobility"][3], ci_data["co2"][3],  ci_data["switches"][3]]

    fig, ax = dark_fig(8, 4)
    x = np.arange(len(labels))
    bars = ax.bar(x, means, color=["#3b82f6","#22c55e","#f97316"], width=0.4, alpha=0.9)

    # Error bars (std)
    ax.errorbar(x, means, yerr=stds, fmt="none", color="#f8fafc", capsize=8, linewidth=2, capthick=2)

    # Min-max range labels
    for i, (mn, mx, mean) in enumerate(zip(mins, maxs, means)):
        ax.text(i, mean + stds[i] + 0.5, f"{mn}–{mx}", ha="center", va="bottom",
                color="#94a3b8", fontsize=9)

    ax.set_xticks(x); ax.set_xticklabels(labels, color="#cbd5e1")
    ax.set_ylabel("Score", color="#cbd5e1")
    ax.set_title("Confidence Intervals (5 runs, ±1σ)", color="#f8fafc", pad=10)
    plt.tight_layout()
    return fig


def plot_equity(equity):
    brackets = equity.get("brackets", {})
    names   = ["Low Income\n(<₹10k)", "Middle Income\n(₹10k–50k)", "High Income\n(>₹50k)"]
    keys    = ["low","middle","high"]
    before_pcts = [brackets.get(k,{}).get("before_pct",0) for k in keys]
    after_pcts  = [brackets.get(k,{}).get("after_pct",0)  for k in keys]

    x = np.arange(3)
    fig, ax = dark_fig(8, 4)
    ax.bar(x-0.2, before_pcts, 0.4, label="Before", color="#3b82f6", alpha=0.9)
    bars = ax.bar(x+0.2, after_pcts, 0.4, label="After",  color="#22c55e", alpha=0.9)
    for bar, val in zip(bars, after_pcts):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                f"{val}%", ha="center", va="bottom", color="#22c55e", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(names, color="#cbd5e1")
    ax.set_ylabel("% Using Public Transport", color="#cbd5e1")
    ax.set_title(f"Equity — Public Transport Adoption by Income  (Equity Index: {equity.get('equity_index',0)}/100)",
                 pad=10)
    ax.legend(facecolor="#1e293b", labelcolor="#f8fafc", edgecolor="#334155")
    plt.tight_layout()
    return fig


def plot_time_of_day(tod):
    slots  = list(tod.keys())
    metros = [tod[s]["metro_share"]  for s in slots]
    sw     = [tod[s]["switches"]     for s in slots]

    fig, ax = dark_fig(8, 4)
    color_list = ["#ef4444","#3b82f6","#f97316"]
    bars = ax.bar(slots, metros, color=color_list, width=0.4, alpha=0.9)
    for bar, val in zip(bars, metros):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f"{val}%", ha="center", va="bottom", color="#f8fafc", fontsize=10, fontweight="bold")

    ax2 = ax.twinx()
    ax2.plot(slots, sw, color="#22c55e", marker="o", linewidth=2, markersize=8, label="Switches")
    ax2.set_ylabel("Mode Switches", color="#22c55e")
    ax2.tick_params(colors="#22c55e")

    ax.set_ylabel("Metro Share (%)")
    ax.set_title("Time-of-Day Simulation", pad=10)
    ax.set_xticklabels(slots)
    ax2.spines["right"].set_color("#22c55e")
    ax2.spines["top"].set_visible(False)
    plt.tight_layout()
    return fig


def plot_delhi_map(map_data):
    color_map = {"Metro":"#22c55e","Bus":"#3b82f6","Auto":"#f59e0b","Walking":"#8b5cf6"}
    fig, ax = plt.subplots(figsize=(8,7))
    fig.patch.set_alpha(0); ax.set_facecolor("none")

    for transport, color in color_map.items():
        pts = [p for p in map_data if p["transport"] == transport]
        if pts:
            ax.scatter([p["lng"] for p in pts], [p["lat"] for p in pts],
                       c=color, s=45, alpha=0.75, label=transport, zorder=3)

    dl = [[28.40,76.84],[28.40,77.35],[28.88,77.35],[28.88,76.84],[28.40,76.84]]
    ax.plot([p[1] for p in dl], [p[0] for p in dl], color="#334155", linewidth=1.5,
            linestyle="--", alpha=0.5)
    ax.set_xlabel("Longitude", fontsize=9)
    ax.set_ylabel("Latitude",  fontsize=9)
    ax.set_title("Citizen Transport Distribution — Delhi", pad=12)
    ax.tick_params(labelsize=8)
    ax.spines["bottom"].set_color("#94a3b8"); ax.spines["left"].set_color("#94a3b8")
    ax.spines["top"].set_visible(False);     ax.spines["right"].set_visible(False)
    ax.legend(facecolor="#1e293b", labelcolor="#f8fafc", edgecolor="#334155", loc="lower right")
    plt.tight_layout()
    return fig


def plot_comparison(all_results):
    short = {
        "Free Metro Rides For Women": "Free\nMetro",
        "50% Bus Fare Reduction":     "Bus\nDiscount",
        "Congestion Tax":             "Congestion\nTax",
        "New Metro Line":             "New Metro\nLine"
    }
    labels   = [short.get(r["policy"], r["policy"][:10]) for r in all_results]
    mobility = [r["mobility_score"]            for r in all_results]
    co2      = [r["estimated_co2_reduction"]   for r in all_results]
    switches = [r["transport_changes"]         for r in all_results]

    x = np.arange(len(all_results)); w = 0.25
    fig, ax = dark_fig(11, 6)
    ax.bar(x-w, mobility, w, label="Mobility Score",    color="#3b82f6", alpha=0.9)
    ax.bar(x,   co2,      w, label="CO2 Reduction",     color="#22c55e", alpha=0.9)
    ax.bar(x+w, switches, w, label="Citizens Switched", color="#f97316", alpha=0.9)

    best_idx = mobility.index(max(mobility))
    ax.annotate("⭐ Best", xy=(best_idx-w, max(mobility)+1),
                ha="center", color="#fbbf24", fontsize=10, fontweight="bold")

    ax.set_xticks(x); ax.set_xticklabels(labels, color="#cbd5e1")
    ax.set_ylabel("Score / Count", color="#cbd5e1")
    ax.set_title("Policy Comparison — All Four Policies", color="#f8fafc", pad=10)
    ax.legend(facecolor="#1e293b", labelcolor="#f8fafc", edgecolor="#334155")
    plt.tight_layout()
    return fig


# =====================================================
# LIVE SIMULATION REPLAY
# =====================================================

def live_replay(policy_arg):
    """Stream citizen decisions one-by-one with a live chart."""
    import sys, os
    sys.path.insert(0, os.getcwd())

    try:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(app_dir, "enhanced_citizens.json")) as f:
            citizens = json.load(f)
    except FileNotFoundError:
        st.error("enhanced_citizens.json not found. Run enhance_citizens.py first.")
        return None

    # Import simulation helpers inline
    import importlib.util, types

    # We'll replicate choose_best_transport logic inline to avoid module reload issues
    BASE_T = {
        "Metro":   {"cost":5,"time":8,"comfort":7,"safety":8},
        "Bus":     {"cost":8,"time":5,"comfort":4,"safety":5},
        "Auto":    {"cost":3,"time":9,"comfort":8,"safety":6},
        "Walking": {"cost":10,"time":2,"comfort":2,"safety":7}
    }

    def get_scores_local(c):
        t = {k: dict(v) for k,v in BASE_T.items()}
        if policy_arg == "Free Metro Rides For Women":
            if c["type"] in ["Female Student","Female Office Worker"]:
                t["Metro"]["cost"] = 10
        elif policy_arg == "50% Bus Fare Reduction":
            t["Bus"]["cost"] = 10
        elif policy_arg == "Congestion Tax":
            t["Auto"]["cost"] = 1
        elif policy_arg == "New Metro Line":
            t["Metro"]["time"] = 10
        return t

    def decide(c):
        opts = get_scores_local(c)
        dist = c["commute_distance_km"]
        best, best_score = None, -999999
        for mode, v in opts.items():
            sc = (c.get("budget_sensitivity",5)*v["cost"] +
                  c.get("time_sensitivity",5)*v["time"] +
                  c.get("comfort_sensitivity",5)*v["comfort"] +
                  c.get("safety_sensitivity",5)*v["safety"])
            if mode == "Walking":
                sc += 40 if dist<=2 else 10 if dist<=5 else -100
            elif mode == "Metro":
                sc += 15 if dist>=5 else 0
                sc += 25 if dist>=10 else 0
            elif mode == "Bus":
                sc += 10 if dist>=3 else 0
                sc += 15 if dist>=8 else 0
            elif mode == "Auto":
                sc += 10 if dist>=3 else 0
                sc += 5  if dist>=8 else 0
            sc = sc/10
            if sc > best_score:
                best_score = sc; best = mode
        return best

    transport_map = {"Metro":"#22c55e","Bus":"#3b82f6","Auto":"#f59e0b","Walking":"#8b5cf6"}

    st.markdown("#### 🎬 Live Simulation Replay")
    progress_bar = st.progress(0, text="Starting simulation...")
    status_box   = st.empty()
    chart_slot   = st.empty()
    summary_slot = st.empty()

    counts = {}
    switches = 0
    total = len(citizens)
    log = []

    for i, c in enumerate(citizens):
        old = c["current_transport"]
        new = decide(c)
        if old != new:
            switches += 1
            log.append(f"Citizen {c['id']} ({c['type']}): {old} → {new}")
        c["current_transport"] = new

        t = c["current_transport"]
        if t in ["Auto Rickshaw","Cab","Car","Scooter","Bike"]: disp = "Auto"
        elif t == "Walking": disp = "Walking"
        elif t == "Bus":     disp = "Bus"
        else:                disp = "Metro"
        counts[disp] = counts.get(disp, 0) + 1

        pct = (i+1)/total
        progress_bar.progress(pct, text=f"Processing citizen {i+1}/{total}...")

        if (i+1) % 10 == 0 or i == total-1:
            # Update live chart
            fig, ax = plt.subplots(figsize=(8, 3))
            fig.patch.set_alpha(0); ax.set_facecolor("none")
            sorted_counts = dict(sorted(counts.items(), key=lambda x: -x[1]))
            bar_colors = [transport_map.get(k,"#6b7280") for k in sorted_counts]
            ax.barh(list(sorted_counts.keys()), list(sorted_counts.values()),
                    color=bar_colors, alpha=0.9)
            ax.set_xlabel("Citizens")
            ax.set_title(f"Transport Choices — {i+1} agents processed")
            for s in ["top","right"]: ax.spines[s].set_visible(False)
            for s in ["bottom","left"]: ax.spines[s].set_color("#94a3b8")
            plt.tight_layout()
            chart_slot.pyplot(fig)
            plt.close(fig)

            if log:
                status_box.markdown(
                    f"<div style='background:#1e293b;border:1px solid #334155;border-radius:8px;"
                    f"padding:10px;color:#94a3b8;font-size:12px;font-family:monospace'>"
                    f"{'<br>'.join(log[-5:])}</div>",
                    unsafe_allow_html=True
                )
            time.sleep(0.05)

    progress_bar.progress(1.0, text="Simulation complete!")
    summary_slot.success(f"✅ Done — {switches} citizens changed transport mode")
    return switches


# =====================================================
# PDF EXPORT
# =====================================================

def export_pdf(results, llm_reports):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("title", parent=styles["Title"],
                                 fontSize=22, textColor=colors.HexColor("#1e293b"),
                                 spaceAfter=6)
    h1_style = ParagraphStyle("h1", parent=styles["Heading1"],
                               fontSize=14, textColor=colors.HexColor("#1e293b"),
                               spaceBefore=14, spaceAfter=4)
    body_style = ParagraphStyle("body", parent=styles["Normal"],
                                fontSize=10, leading=14, spaceAfter=6)
    caption_style = ParagraphStyle("caption", parent=styles["Normal"],
                                   fontSize=9, textColor=colors.HexColor("#64748b"), spaceAfter=4)

    story = []

    # Title
    story.append(Paragraph("Delhi Digital Twin", title_style))
    story.append(Paragraph(f"Urban Policy Simulation Report — {results['policy']}", styles["Heading2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#334155")))
    story.append(Spacer(1, 0.3*cm))

    # Key metrics table
    story.append(Paragraph("Key Metrics", h1_style))
    ci = results.get("confidence_intervals", {})
    mob_range = f"{ci.get('mobility',('?','?',0,0))[2]}–{ci.get('mobility',('?','?',0,100))[3]}"
    co2_range = f"{ci.get('co2',('?','?',0,0))[2]}–{ci.get('co2',('?','?',0,100))[3]}"
    sw_range  = f"{ci.get('switches',('?','?',0,0))[2]}–{ci.get('switches',('?','?',0,100))[3]}"

    tdata = [
        ["Metric", "Value", "CI Range (5 runs)"],
        ["Citizens Simulated", str(results["citizens_simulated"]), "—"],
        ["Mode Switches",      str(results["transport_changes"]),  sw_range],
        ["Mobility Score",     str(results["mobility_score"]),     mob_range],
        ["CO2 Reduction",      str(results["estimated_co2_reduction"]), co2_range],
        ["Citizen Satisfaction", str(results.get("citizen_sentiment",{}).get("score","N/A"))+"/100", "—"],
        ["Equity Index",       str(results.get("equity",{}).get("equity_index","N/A"))+"/100", "—"],
    ]
    t = Table(tdata, colWidths=[5*cm, 4*cm, 5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  colors.HexColor("#1e293b")),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.HexColor("#e2e8f0")]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING",     (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Transport before/after
    story.append(Paragraph("Transport Mode Distribution", h1_style))
    modes = sorted(set(results["transport_before"].keys()) | set(results["transport_after"].keys()))
    tdata2 = [["Mode","Before","After","Change"]]
    for m in modes:
        b = results["transport_before"].get(m,0)
        a = results["transport_after"].get(m,0)
        tdata2.append([m, str(b), str(a), f"{a-b:+d}"])
    t2 = Table(tdata2, colWidths=[5*cm,3*cm,3*cm,3*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR",   (0,0),(-1,0), colors.white),
        ("FONTSIZE",    (0,0),(-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.HexColor("#e2e8f0")]),
        ("GRID",        (0,0),(-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING",     (0,0),(-1,-1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.5*cm))

    # Agent reports
    agent_labels = {
        "government": "Government Agent Report",
        "transport":  "Transport Agent Report",
        "environment":"Environment Agent Report",
        "citizens":   "Citizens Agent Report",
        "business":   "Business Agent Report"
    }
    for key, label in agent_labels.items():
        story.append(Paragraph(label, h1_style))
        text = llm_reports.get(key, results.get(f"{key}_report",""))
        # Clean text for reportlab
        text = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        for para in text.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    buf.seek(0)
    return buf


# =====================================================
# CUSTOM CITIZEN
# =====================================================

def simulate_custom_citizen(ctype, income, distance, policy_arg):
    """Simulate a single custom citizen and return their transport choice."""
    sensitivity_map = {
        "Female Student":      {"budget":9,"time":5,"comfort":3,"safety":8},
        "Female Office Worker":{"budget":6,"time":9,"comfort":7,"safety":9},
        "Male Office Worker":  {"budget":6,"time":9,"comfort":7,"safety":6},
        "Auto Driver":         {"budget":5,"time":8,"comfort":4,"safety":5},
        "Shop Owner":          {"budget":7,"time":6,"comfort":6,"safety":6},
    }
    sens = sensitivity_map.get(ctype, {"budget":6,"time":6,"comfort":6,"safety":6})

    citizen = {
        "id": 999, "type": ctype,
        "monthly_income": income,
        "commute_distance_km": distance,
        "current_transport": "Metro",
        "budget_sensitivity":  sens["budget"],
        "time_sensitivity":    sens["time"],
        "comfort_sensitivity": sens["comfort"],
        "safety_sensitivity":  sens["safety"]
    }

    BASE_T = {
        "Metro":   {"cost":5,"time":8,"comfort":7,"safety":8},
        "Bus":     {"cost":8,"time":5,"comfort":4,"safety":5},
        "Auto":    {"cost":3,"time":9,"comfort":8,"safety":6},
        "Walking": {"cost":10,"time":2,"comfort":2,"safety":7}
    }

    def get_scores(c):
        t = {k: dict(v) for k,v in BASE_T.items()}
        if policy_arg == "Free Metro Rides For Women":
            if c["type"] in ["Female Student","Female Office Worker"]:
                t["Metro"]["cost"] = 10
        elif policy_arg == "50% Bus Fare Reduction":
            t["Bus"]["cost"] = 10
        elif policy_arg == "Congestion Tax":
            t["Auto"]["cost"] = 1
        elif policy_arg == "New Metro Line":
            t["Metro"]["time"] = 10
        return t

    opts = get_scores(citizen)
    dist = citizen["commute_distance_km"]
    best, best_score = None, -999999
    scores = {}

    for mode, v in opts.items():
        sc = (citizen["budget_sensitivity"]*v["cost"] +
              citizen["time_sensitivity"]*v["time"] +
              citizen["comfort_sensitivity"]*v["comfort"] +
              citizen["safety_sensitivity"]*v["safety"])
        if mode == "Walking":
            sc += 40 if dist<=2 else 10 if dist<=5 else -100
        elif mode == "Metro":
            sc += 15 if dist>=5 else 0
            sc += 25 if dist>=10 else 0
        elif mode == "Bus":
            sc += 10 if dist>=3 else 0
            sc += 15 if dist>=8 else 0
        elif mode == "Auto":
            sc += 10 if dist>=3 else 0
            sc += 5  if dist>=8 else 0
        sc = sc/10
        scores[mode] = round(sc, 2)
        if sc > best_score:
            best_score = sc; best = mode

    return best, scores


# =====================================================
# RUN SIMULATION HELPER — imports simulation.py directly
# (no subprocess — works on Streamlit Cloud)
# =====================================================

def run_simulation(p):
    """Run simulation by importing simulation.py as a module with the policy injected."""
    arg = p if not isinstance(p, dict) else json.dumps(p)

    # Inject the policy into sys.argv so simulation.py picks it up
    old_argv = sys.argv[:]
    sys.argv = ["simulation.py", arg]

    # Find simulation.py relative to app.py
    app_dir = os.path.dirname(os.path.abspath(__file__))
    sim_path = os.path.join(app_dir, "simulation.py")

    # Load and execute simulation.py as a fresh module each time
    spec = importlib.util.spec_from_file_location("simulation", sim_path)
    sim_module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(sim_module)
    except SystemExit:
        pass  # simulation.py may call sys.exit; ignore
    finally:
        sys.argv = old_argv

    # Read results written by simulation.py
    results_path  = os.path.join(app_dir, "results.json")
    map_data_path = os.path.join(app_dir, "map_data.json")

    with open(results_path) as f:
        r = json.load(f)
    try:
        with open(map_data_path) as f:
            r["map_data"] = json.load(f)
    except Exception:
        r["map_data"] = []
    return r


# =====================================================
# SENTIMENT HTML
# =====================================================

def sentiment_html(score):
    color = "#22c55e" if score>=75 else "#f59e0b" if score>=55 else "#ef4444"
    return f"""
    <div class="dt-sentiment-box">
        <div class="dt-sentiment-label">Citizen Satisfaction</div>
        <div style="display:flex;align-items:center;gap:14px">
            <div style="font-size:30px;font-weight:700;color:{color}">{score}/100</div>
            <div class="dt-sentiment-track">
                <div style="width:{score}%;background:{color};height:10px;border-radius:4px;
                            transition:width 0.5s ease"></div>
            </div>
        </div>
    </div>"""



# =====================================================
# ANIMATED METRO MAP
# =====================================================

def animated_metro_map(results):
    """Render an animated Delhi metro map using HTML/CSS/JS inside st.components."""
    import streamlit.components.v1 as components

    after = results.get("transport_after", {})
    before = results.get("transport_before", {})
    policy = results.get("policy", "")

    metro_after  = after.get("Metro", 0)
    bus_after    = after.get("Bus", 0)
    auto_after   = sum(after.get(m,0) for m in ["Auto","Auto Rickshaw","Cab","Car","Scooter","Bike"])
    walk_after   = after.get("Walking", 0)

    metro_before = before.get("Metro", 0)
    metro_growth = metro_after - metro_before

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: -apple-system, sans-serif; }}

  .map-container {{
    position: relative;
    width: 100%;
    height: 420px;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #334155;
  }}

  /* City grid lines */
  .grid-line {{
    position: absolute;
    background: rgba(255,255,255,0.04);
  }}
  .grid-h {{ width: 100%; height: 1px; }}
  .grid-v {{ width: 1px; height: 100%; }}

  /* Metro lines */
  .metro-line {{
    position: absolute;
    height: 4px;
    border-radius: 2px;
    opacity: 0.7;
  }}
  .metro-line-yellow {{ background: #fbbf24; top: 35%; width: 85%; left: 7%; }}
  .metro-line-blue   {{ background: #60a5fa; top: 55%; width: 80%; left: 10%; }}
  .metro-line-red    {{ background: #f87171; width: 4px; height: 70%; left: 30%; top: 15%; }}
  .metro-line-green  {{ background: #34d399; width: 4px; height: 60%; left: 65%; top: 20%; }}

  /* Station dots */
  .station {{
    position: absolute;
    width: 10px; height: 10px;
    background: white;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 6px rgba(255,255,255,0.8);
    z-index: 2;
  }}
  .station-label {{
    position: absolute;
    color: rgba(255,255,255,0.7);
    font-size: 9px;
    transform: translateX(-50%);
    white-space: nowrap;
    z-index: 3;
  }}

  /* Animated vehicles */
  .vehicle {{
    position: absolute;
    border-radius: 3px;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
  }}

  /* Metro trains on yellow line */
  .metro-train {{
    width: 32px; height: 12px;
    background: linear-gradient(90deg, #fbbf24, #f59e0b);
    border-radius: 6px 2px 2px 6px;
    top: calc(35% - 6px);
    animation: moveMetroRight linear infinite;
    box-shadow: 0 0 8px #fbbf2480;
  }}
  .metro-train::after {{
    content: '';
    position: absolute;
    right: -4px; top: 2px;
    width: 0; height: 0;
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    border-left: 5px solid #f59e0b;
  }}

  /* Metro trains on blue line */
  .metro-train-blue {{
    width: 32px; height: 12px;
    background: linear-gradient(90deg, #60a5fa, #3b82f6);
    border-radius: 6px 2px 2px 6px;
    top: calc(55% - 6px);
    animation: moveMetroRight linear infinite;
    box-shadow: 0 0 8px #3b82f680;
  }}
  .metro-train-blue::after {{
    content: '';
    position: absolute;
    right: -4px; top: 2px;
    width: 0; height: 0;
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    border-left: 5px solid #3b82f6;
  }}

  /* Bus */
  .bus {{
    width: 20px; height: 14px;
    background: #34d399;
    border-radius: 3px;
    top: calc(70% - 7px);
    animation: moveBus linear infinite;
    box-shadow: 0 0 6px #34d39980;
  }}

  /* Auto rickshaw */
  .auto {{
    font-size: 16px;
    top: calc(82%);
    animation: moveAuto linear infinite;
    filter: drop-shadow(0 0 4px rgba(251,191,36,0.6));
  }}

  /* Walking person */
  .walker {{
    font-size: 14px;
    top: calc(20%);
    animation: moveWalker linear infinite;
    filter: drop-shadow(0 0 3px rgba(167,139,250,0.7));
  }}

  @keyframes moveMetroRight {{
    0%   {{ left: 5%; }}
    100% {{ left: 88%; }}
  }}
  @keyframes moveBus {{
    0%   {{ left: 88%; transform: scaleX(-1); }}
    100% {{ left: 8%;  transform: scaleX(-1); }}
  }}
  @keyframes moveAuto {{
    0%   {{ left: 10%; }}
    100% {{ left: 75%; }}
  }}
  @keyframes moveWalker {{
    0%   {{ left: 60%; }}
    100% {{ left: 85%; }}
  }}

  /* Citizen dots floating around */
  .citizen-dot {{
    position: absolute;
    width: 7px; height: 7px;
    border-radius: 50%;
    animation: floatDot ease-in-out infinite alternate;
    opacity: 0.85;
    z-index: 5;
  }}
  @keyframes floatDot {{
    0%   {{ transform: translateY(0px); opacity: 0.7; }}
    100% {{ transform: translateY(-8px); opacity: 1; }}
  }}

  /* Stats overlay */
  .stats-bar {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(6px);
    display: flex;
    justify-content: space-around;
    padding: 10px 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
  }}
  .stat-item {{
    text-align: center;
  }}
  .stat-val {{
    font-size: 22px;
    font-weight: 700;
  }}
  .stat-lbl {{
    font-size: 10px;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase;
    letter-spacing: 1px;
  }}

  /* Policy badge */
  .policy-badge {{
    position: absolute;
    top: 12px; left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 5px 16px;
    color: white;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
    z-index: 20;
  }}

  /* Growth indicator */
  .growth-badge {{
    position: absolute;
    top: 12px; right: 14px;
    background: {'rgba(34,197,94,0.25)' if metro_growth > 0 else 'rgba(239,68,68,0.25)'};
    border: 1px solid {'#22c55e' if metro_growth > 0 else '#ef4444'};
    border-radius: 8px;
    padding: 5px 12px;
    color: {'#4ade80' if metro_growth > 0 else '#f87171'};
    font-size: 12px;
    font-weight: 700;
    z-index: 20;
  }}
</style>
</head>
<body>
<div class="map-container">

  <!-- Grid -->
  <div class="grid-line grid-h" style="top:20%"></div>
  <div class="grid-line grid-h" style="top:40%"></div>
  <div class="grid-line grid-h" style="top:60%"></div>
  <div class="grid-line grid-h" style="top:80%"></div>
  <div class="grid-line grid-v" style="left:20%"></div>
  <div class="grid-line grid-v" style="left:40%"></div>
  <div class="grid-line grid-v" style="left:60%"></div>
  <div class="grid-line grid-v" style="left:80%"></div>

  <!-- Metro lines -->
  <div class="metro-line metro-line-yellow"></div>
  <div class="metro-line metro-line-blue"></div>
  <div class="metro-line metro-line-red"></div>
  <div class="metro-line metro-line-green"></div>

  <!-- Stations on yellow line -->
  <div class="station" style="left:10%;top:35%"></div>
  <div class="station-label" style="left:10%;top:38%">Dwarka</div>
  <div class="station" style="left:30%;top:35%"></div>
  <div class="station-label" style="left:30%;top:38%">Janakpuri</div>
  <div class="station" style="left:50%;top:35%"></div>
  <div class="station-label" style="left:50%;top:38%">CP</div>
  <div class="station" style="left:65%;top:35%"></div>
  <div class="station-label" style="left:65%;top:38%">Lajpat</div>
  <div class="station" style="left:85%;top:35%"></div>
  <div class="station-label" style="left:85%;top:38%">Noida</div>

  <!-- Stations on blue line -->
  <div class="station" style="left:12%;top:55%"></div>
  <div class="station-label" style="left:12%;top:58%">Rohini</div>
  <div class="station" style="left:40%;top:55%"></div>
  <div class="station-label" style="left:40%;top:58%">Karol Bagh</div>
  <div class="station" style="left:65%;top:55%"></div>
  <div class="station-label" style="left:65%;top:58%">Nehru Pl</div>
  <div class="station" style="left:88%;top:55%"></div>
  <div class="station-label" style="left:88%;top:58%">Vasant Kunj</div>

  <!-- Animated trains — scale count by metro ridership -->
  <div class="vehicle metro-train" style="animation-duration:6s; animation-delay:0s;"></div>
  {'<div class="vehicle metro-train" style="animation-duration:6s; animation-delay:-2s;"></div>' if metro_after > 30 else ''}
  {'<div class="vehicle metro-train" style="animation-duration:6s; animation-delay:-4s;"></div>' if metro_after > 60 else ''}
  <div class="vehicle metro-train-blue" style="animation-duration:8s; animation-delay:-1s;"></div>
  {'<div class="vehicle metro-train-blue" style="animation-duration:8s; animation-delay:-4s;"></div>' if metro_after > 50 else ''}

  <!-- Bus (fewer if bus ridership low) -->
  {'<div class="vehicle bus" style="animation-duration:11s; animation-delay:0s;"></div>' if bus_after > 0 else ''}
  {'<div class="vehicle bus" style="animation-duration:11s; animation-delay:-5s;"></div>' if bus_after > 5 else ''}

  <!-- Auto rickshaws -->
  {'<div class="vehicle auto" style="animation-duration:14s; animation-delay:0s;">🛺</div>' if auto_after > 0 else ''}
  {'<div class="vehicle auto" style="animation-duration:14s; animation-delay:-6s;">🛺</div>' if auto_after > 3 else ''}

  <!-- Walkers -->
  {'<div class="vehicle walker" style="animation-duration:18s; animation-delay:0s;">🚶</div>' if walk_after > 0 else ''}

  <!-- Citizen dots -->
  <div class="citizen-dot" style="background:#22c55e;left:15%;top:28%;animation-duration:2.1s;animation-delay:0s;"></div>
  <div class="citizen-dot" style="background:#22c55e;left:28%;top:42%;animation-duration:1.8s;animation-delay:0.3s;"></div>
  <div class="citizen-dot" style="background:#22c55e;left:45%;top:25%;animation-duration:2.5s;animation-delay:0.1s;"></div>
  <div class="citizen-dot" style="background:#22c55e;left:60%;top:48%;animation-duration:2.0s;animation-delay:0.6s;"></div>
  <div class="citizen-dot" style="background:#22c55e;left:72%;top:30%;animation-duration:1.6s;animation-delay:0.2s;"></div>
  <div class="citizen-dot" style="background:#3b82f6;left:20%;top:62%;animation-duration:2.3s;animation-delay:0.4s;"></div>
  <div class="citizen-dot" style="background:#3b82f6;left:50%;top:65%;animation-duration:1.9s;animation-delay:0.5s;"></div>
  <div class="citizen-dot" style="background:#f59e0b;left:35%;top:75%;animation-duration:2.2s;animation-delay:0.3s;"></div>
  <div class="citizen-dot" style="background:#f59e0b;left:55%;top:78%;animation-duration:1.7s;animation-delay:0.1s;"></div>
  <div class="citizen-dot" style="background:#8b5cf6;left:80%;top:22%;animation-duration:2.4s;animation-delay:0.7s;"></div>

  <!-- Policy badge -->
  <div class="policy-badge">🚇 {policy[:40]}{'...' if len(policy)>40 else ''}</div>

  <!-- Growth badge -->
  <div class="growth-badge">Metro {'▲' if metro_growth >= 0 else '▼'} {abs(metro_growth)} riders</div>

  <!-- Stats bar -->
  <div class="stats-bar">
    <div class="stat-item">
      <div class="stat-val" style="color:#fbbf24">{metro_after}</div>
      <div class="stat-lbl">🚇 Metro</div>
    </div>
    <div class="stat-item">
      <div class="stat-val" style="color:#34d399">{bus_after}</div>
      <div class="stat-lbl">🚌 Bus</div>
    </div>
    <div class="stat-item">
      <div class="stat-val" style="color:#f97316">{auto_after}</div>
      <div class="stat-lbl">🛺 Auto/Car</div>
    </div>
    <div class="stat-item">
      <div class="stat-val" style="color:#a78bfa">{walk_after}</div>
      <div class="stat-lbl">🚶 Walking</div>
    </div>
  </div>

</div>
</body>
</html>
"""
    components.html(html, height=440, scrolling=False)


# =====================================================
# RENDER FULL RESULTS
# =====================================================

def render_results(results, llm_reports, policy_display):
    st.success(f"✅ Simulation Complete — **{policy_display}**")

    # ---- METRICS ----
    cols = st.columns(6)
    metrics = [
        ("👥 Citizens",    results["citizens_simulated"]),
        ("🔄 Switches",    results["transport_changes"]),
        ("🌱 CO2 Score",   results["estimated_co2_reduction"]),
        ("📊 Mobility",    results["mobility_score"]),
        ("😊 Satisfaction",results.get("citizen_sentiment",{}).get("score","—")),
        ("⚖️ Equity",      str(results.get("equity",{}).get("equity_index","—"))+"/100"),
    ]
    for col, (label, val) in zip(cols, metrics):
        col.metric(label, val)

    st.divider()

    # ---- MOBILITY BREAKDOWN ----
    st.subheader("📊 Mobility Score Breakdown")
    bd = results.get("mobility_breakdown", {})
    if bd:
        b_cols = st.columns(4)
        items = [
            ("🚗 Reduced Congestion", bd.get("reduced_congestion",0)),
            ("🚇 Transit Adoption",   bd.get("public_transit_adoption",0)),
            ("💰 Cost Savings",       bd.get("cost_savings",0)),
            ("🌱 CO2 Reduction",      bd.get("co2_reduction",0)),
        ]
        for col, (label, val) in zip(b_cols, items):
            with col:
                st.markdown(f"""
                <div class="dt-card">
                    <div class="dt-card-label">{label}</div>
                    <div class="dt-card-value">+{val}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown(f"**Total Mobility Score: {bd.get('total',0)}**")

    st.divider()

    # ---- CHARTS ROW 1 ----
    st.subheader("📈 Visual Insights")
    c1, c2, c3 = st.columns([2,1,1])
    with c1:
        st.pyplot(plot_transport(results["transport_before"], results["transport_after"]))
    with c2:
        st.pyplot(plot_co2(results["estimated_co2_reduction"]))
    with c3:
        st.pyplot(plot_radar(results))

    st.divider()

    # ---- CHARTS ROW 2 ----
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Confidence Intervals")
        ci = results.get("confidence_intervals")
        if ci:
            st.pyplot(plot_confidence(ci))
            mob = ci["mobility"]
            st.caption(f"Mobility: {mob[0]} ± {mob[1]} (range {mob[2]}–{mob[3]})")
    with c2:
        st.subheader("⏰ Time-of-Day Analysis")
        tod = results.get("time_of_day")
        if tod:
            st.pyplot(plot_time_of_day(tod))

    st.divider()

    # ---- EQUITY ----
    st.subheader("⚖️ Equity Analysis — Who Benefits?")
    eq = results.get("equity")
    if eq:
        eq_c1, eq_c2 = st.columns([2, 1])
        with eq_c1:
            st.pyplot(plot_equity(eq))
        with eq_c2:
            idx = eq.get("equity_index", 50)
            color = "#22c55e" if idx > 60 else "#f59e0b" if idx > 40 else "#ef4444"
            interpretation = ("Strongly benefits lower-income groups" if idx > 70
                              else "Broadly equitable" if idx > 50
                              else "Slightly favours higher-income groups" if idx > 35
                              else "May widen inequality")
            st.markdown(f"""
            <div class="dt-eq-box">
                <div class="dt-eq-label">Equity Index</div>
                <div class="dt-eq-value" style="color:{color}">{idx}/100</div>
                <div class="dt-eq-note">{interpretation}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ---- ANIMATED MAP ----
    st.subheader("🗺️ Delhi Live Transport Map")
    animated_metro_map(results)
    # Also show static scatter below (collapsible)
    map_data = results.get("map_data", [])
    with st.expander("📍 View citizen scatter map"):
        if map_data:
            m1, m2 = st.columns([2, 1])
            with m1:
                st.pyplot(plot_delhi_map(map_data))
            with m2:
                st.markdown("**Transport Legend**")
                tc = {}
                for p in map_data:
                    tc[p["transport"]] = tc.get(p["transport"],0) + 1
                color_map = {"Metro":"#22c55e","Bus":"#3b82f6","Auto":"#f59e0b","Walking":"#8b5cf6"}
                for t, cnt in sorted(tc.items(), key=lambda x: -x[1]):
                    c = color_map.get(t,"#6b7280")
                    st.markdown(f"""
                    <div class="dt-legend-row">
                        <div class="dt-legend-dot" style="background:{c}"></div>
                        <span class="dt-legend-name">{t}</span>
                        <span class="dt-legend-count">{cnt}</span>
                    </div>""", unsafe_allow_html=True)

    st.divider()

    # ---- SENTIMENT ----
    st.subheader("😊 Citizen Sentiment")
    sent = results.get("citizen_sentiment", {})
    if sent:
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(sentiment_html(sent.get("score",0)), unsafe_allow_html=True)
        with s2:
            st.markdown("**✅ Top Benefits**")
            for b in sent.get("top_benefits",[]):
                st.markdown(f"- {b}")
        with s3:
            st.markdown("**⚠️ Top Concerns**")
            for c in sent.get("top_complaints",[]):
                st.markdown(f"- {c}")

    st.divider()

    # ---- CUSTOM CITIZEN ----
    st.subheader("🧑 Try a Custom Citizen")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        cc_type = st.selectbox("Citizen Type", [
            "Female Student","Female Office Worker","Male Office Worker","Auto Driver","Shop Owner"
        ], key="cc_type")
    with cc2:
        cc_income = st.number_input("Monthly Income (₹)", min_value=3000, max_value=200000,
                                     value=35000, step=1000, key="cc_income")
    with cc3:
        cc_dist = st.number_input("Commute Distance (km)", min_value=1, max_value=50,
                                   value=12, key="cc_dist")

    if st.button("🔍 Simulate This Citizen", key="cc_btn"):
        best, scores = simulate_custom_citizen(cc_type, cc_income, cc_dist, results["policy"])
        sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
        st.markdown(f"**Best choice: `{best}`** under *{results['policy']}*")
        col_s = st.columns(4)
        color_map2 = {"Metro":"#22c55e","Bus":"#3b82f6","Auto":"#f59e0b","Walking":"#8b5cf6"}
        for col, (mode, score) in zip(col_s, sorted_scores):
            c = color_map2.get(mode,"#6b7280")
            highlight = "border:2px solid #22c55e;" if mode == best else ""
            with col:
                st.markdown(f"""
                <div class="dt-score-card" style="{highlight}">
                    <div class="dt-score-label">{mode}</div>
                    <div class="dt-score-value" style="color:{c}">{score}</div>
                </div>""", unsafe_allow_html=True)

    st.divider()

    # ---- AGENT REPORTS ----
    st.subheader("🤖 Agent Reports")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏛 Government","🚇 Transport","🌱 Environment","👥 Citizens","🏪 Business"
    ])
    for tab, key in zip([tab1,tab2,tab3,tab4,tab5],
                        ["government","transport","environment","citizens","business"]):
        with tab:
            report = llm_reports.get(key, results.get(f"{key}_report",""))
            st.info(report)

    st.divider()

    # ---- PDF EXPORT ----
    st.subheader("📄 Export Report")
    pdf_buf = export_pdf(results, llm_reports)
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_buf,
        file_name=f"delhi_twin_{results['policy'].replace(' ','_')[:30]}.pdf",
        mime="application/pdf"
    )


# =====================================================
# MAIN APP LOGIC
# =====================================================

if run_btn:

    # ---- COMPARE ALL ----
    if mode == "Compare All Policies":
        all_policies = [
            "Free Metro Rides For Women",
            "50% Bus Fare Reduction",
            "Congestion Tax",
            "New Metro Line"
        ]
        all_results = []
        prog = st.progress(0, text="Running all simulations...")

        for i, p in enumerate(all_policies):
            prog.progress((i+1)/len(all_policies), text=f"Simulating: {p}...")
            r = run_simulation(p)
            all_results.append(r)

        prog.empty()
        st.success("✅ All 4 Policy Simulations Complete")

        # Comparison table
        st.subheader("📊 Policy Comparison Table")
        best_mob = max(all_results, key=lambda x: x["mobility_score"])
        cols_h = st.columns([2.5,1.2,1.2,1.2,1.2,1.2,1.2])
        for col, h in zip(cols_h, ["Policy","Mobility","CO2","Switches","Satisfaction","Equity","Decision"]):
            col.markdown(f"**{h}**")

        for r in all_results:
            cols_r = st.columns([2.5,1.2,1.2,1.2,1.2,1.2,1.2])
            is_best = r == best_mob
            cols_r[0].markdown(f"{'**' if is_best else ''}{r['policy']}{' ⭐' if is_best else ''}{'**' if is_best else ''}")
            cols_r[1].metric("", r["mobility_score"])
            cols_r[2].metric("", r["estimated_co2_reduction"])
            cols_r[3].metric("", r["transport_changes"])
            cols_r[4].metric("", r.get("citizen_sentiment",{}).get("score","—"))
            cols_r[5].metric("", str(r.get("equity",{}).get("equity_index","—"))+"/100")
            decision = "✅ APPROVE" if "APPROVE" in r.get("government_report","") else "🔄 REVIEW"
            cols_r[6].markdown(decision)

        st.divider()

        # Best policy highlight
        st.markdown(f"""
        <div class="dt-best-banner">
            <div style="color:#bbf7d0;font-size:22px;font-weight:700">🥇 {best_mob['policy']}</div>
            <div style="color:#86efac;margin-top:6px">Highest combined performance across all metrics</div>
            <div style="display:flex;gap:24px;margin-top:10px">
                <div><span style="color:#4ade80;font-size:20px;font-weight:700">{best_mob['mobility_score']}</span>
                     <span style="color:#86efac;font-size:13px;margin-left:4px">Mobility</span></div>
                <div><span style="color:#4ade80;font-size:20px;font-weight:700">{best_mob['estimated_co2_reduction']}</span>
                     <span style="color:#86efac;font-size:13px;margin-left:4px">CO2</span></div>
                <div><span style="color:#4ade80;font-size:20px;font-weight:700">{best_mob['transport_changes']}</span>
                     <span style="color:#86efac;font-size:13px;margin-left:4px">Switches</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.subheader("📈 Side-by-Side Comparison")
        st.pyplot(plot_comparison(all_results))

        st.divider()
        st.subheader("🔍 Per-Policy Details")
        tabs = st.tabs([r["policy"].split()[0]+"…" for r in all_results])
        for tab, r in zip(tabs, all_results):
            with tab:
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Mobility",  r["mobility_score"])
                c2.metric("CO2",       r["estimated_co2_reduction"])
                c3.metric("Switches",  r["transport_changes"])
                c4.metric("Equity",    str(r.get("equity",{}).get("equity_index","—"))+"/100")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.pyplot(plot_transport(r["transport_before"], r["transport_after"]))
                with col_b:
                    st.pyplot(plot_radar(r))

    # ---- SINGLE POLICY ----
    else:
        # NLP parsing
        if policy_type == "Natural Language" and custom_policy_str:
            with st.spinner("🤖 Parsing policy with Claude..."):
                parsed = parse_nl_policy(custom_policy_str)

            if parsed:
                st.info(f"**Parsed:** `{parsed['name']}` — {parsed.get('explanation','')}")
                policy_arg = json.dumps(parsed)
                policy_display = parsed["name"]
            else:
                st.warning("Could not parse policy automatically. Using as policy name.")
                policy_arg = custom_policy_str
                policy_display = custom_policy_str
        else:
            if policy.startswith("──"):
                st.warning("Please select an actual policy, not a category header.")
                st.stop()
            policy_arg = policy
            policy_display = policy

        # Live replay
        with st.expander("🎬 Live Simulation Replay", expanded=True):
            live_replay(policy_arg if not isinstance(policy_arg, dict) else
                        json.loads(policy_arg).get("name", str(policy_arg)))

        # Full simulation
        with st.spinner("Running full analysis..."):
            results = run_simulation(policy_arg)

        # LLM reports
        llm_reports = {}
        if use_llm:
            with st.spinner("🤖 Generating LLM agent reports..."):
                agent_keys = ["government","transport","environment","citizens","business"]
                for key in agent_keys:
                    llm_reports[key] = get_llm_report(key, results)

        render_results(results, llm_reports, policy_display)

else:
    # Default landing
    st.markdown("""
    <div class="dt-info-box">
        <div class="dt-info-title">How It Works</div>
        <div class="dt-info-body">
            <b>100 citizens</b> across 5 archetypes each independently decide their transport mode
            based on cost, time, comfort, and safety sensitivity scores.<br><br>
            <b>12 Policies to simulate:</b><br>
            🚇 Free Metro Rides For Women &nbsp;·&nbsp; 🚌 50% Bus Fare Reduction &nbsp;·&nbsp; 🚗 Congestion Tax &nbsp;·&nbsp; 🛤️ New Metro Line<br>
            🌙 Metro Hours Extended to 2AM &nbsp;·&nbsp; ✈️ Airport Express Fare Reduction &nbsp;·&nbsp; 🎓 Reserved Student Coaches<br>
            🌿 Personal Carbon Budget &nbsp;·&nbsp; 🎂 Free Transit Birthdays &nbsp;·&nbsp; 🏫 Car-Free School Zones<br>
            🎫 One-Ticket City &nbsp;·&nbsp; ⚡ Free EV Parking<br><br>
            <b>Features:</b> 🤖 LLM agent reports &nbsp;·&nbsp; 🚆 Live metro animation &nbsp;·&nbsp; 🧑 Custom citizen builder &nbsp;·&nbsp;
            📡 Radar chart &nbsp;·&nbsp; ⚖️ Equity analysis &nbsp;·&nbsp; 🎯 Confidence intervals &nbsp;·&nbsp; 📄 PDF export
        </div>
    </div>
    """, unsafe_allow_html=True)