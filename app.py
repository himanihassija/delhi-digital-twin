import streamlit as st
import json, time, copy, requests, importlib.util, sys, os, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import folium
from folium.plugins import HeatMap, MarkerCluster
import streamlit.components.v1 as components

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Delhi Digital Twin",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root tokens ── */
:root {
  --c-bg:       #0a0e1a;
  --c-surface:  #111827;
  --c-card:     #1a2235;
  --c-border:   #2a3548;
  --c-accent:   #3b82f6;
  --c-green:    #22c55e;
  --c-amber:    #f59e0b;
  --c-red:      #ef4444;
  --c-purple:   #a78bfa;
  --c-text:     #f1f5f9;
  --c-muted:    #64748b;
  --c-subtle:   #1e2d42;
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--c-bg) !important;
  font-family: 'Inter', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] > div:first-child { background: var(--c-surface) !important; border-right: 1px solid var(--c-border); }

/* Metrics */
div[data-testid="metric-container"] {
  background: var(--c-card) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: 14px !important;
  padding: 1.1rem 1.3rem !important;
}
div[data-testid="metric-container"] label { color: var(--c-muted) !important; font-size: 11px !important; letter-spacing: .06em; text-transform: uppercase; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--c-text) !important; font-size: 28px !important; font-weight: 600 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--c-surface) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 2px !important;
  border: 1px solid var(--c-border) !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  color: var(--c-muted) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: var(--c-accent) !important;
  color: white !important;
}

/* Buttons */
.stButton > button {
  background: var(--c-accent) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  transition: all .2s !important;
}
.stButton > button:hover { opacity: .9 !important; transform: translateY(-1px) !important; }

/* Selectbox / text area */
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
  background: var(--c-card) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: 10px !important;
  color: var(--c-text) !important;
}

/* ── Custom component styles ── */
.dt-hero {
  background: linear-gradient(135deg, #0f1e3d 0%, #0a1628 50%, #111827 100%);
  border: 1px solid var(--c-border);
  border-radius: 20px;
  padding: 2.5rem 3rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.dt-hero::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, #3b82f6, #a78bfa, transparent);
}
.dt-hero h1 { font-size: 2.2rem; font-weight: 700; color: #f1f5f9; margin: 0 0 .5rem; letter-spacing: -.02em; }
.dt-hero p  { color: #64748b; font-size: 1rem; margin: 0; }
.dt-hero-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(59,130,246,.15); border: 1px solid rgba(59,130,246,.3); border-radius: 20px; padding: 4px 12px; font-size: 12px; color: #93c5fd; margin-bottom: 1rem; }

.dt-card {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
}
.dt-card-title { font-size: 13px; font-weight: 600; color: var(--c-muted); text-transform: uppercase; letter-spacing: .07em; margin-bottom: .75rem; }
.dt-card-value { font-size: 2.2rem; font-weight: 700; color: var(--c-text); line-height: 1; }
.dt-card-sub { font-size: 12px; color: var(--c-muted); margin-top: .3rem; }

.dt-grade {
  display: flex; align-items: center; justify-content: center;
  width: 80px; height: 80px;
  border-radius: 50%;
  font-size: 2rem; font-weight: 800;
  margin: 0 auto 1rem;
}

.dt-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--c-subtle);
  border: 1px solid var(--c-border);
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 12px;
  color: var(--c-text);
  cursor: pointer;
  margin: 4px;
  transition: all .15s;
}
.dt-chip:hover { border-color: var(--c-accent); background: rgba(59,130,246,.1); }

.dt-aqi-bar {
  height: 10px; border-radius: 5px;
  background: linear-gradient(90deg, #22c55e 0%, #f59e0b 40%, #ef4444 70%, #7f1d1d 100%);
  position: relative; margin: .5rem 0;
}
.dt-aqi-needle {
  position: absolute; top: -4px;
  width: 4px; height: 18px;
  background: white;
  border-radius: 2px;
  transform: translateX(-50%);
  box-shadow: 0 0 6px rgba(0,0,0,.5);
}

.dt-debate-msg {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-bottom: .75rem;
}
.dt-debate-agent { font-size: 11px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; margin-bottom: .35rem; }
.dt-debate-text { font-size: 13px; color: #cbd5e1; line-height: 1.6; }

.dt-tweet {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: .9rem 1.1rem;
  margin-bottom: .6rem;
}
.dt-tweet-handle { font-size: 12px; font-weight: 600; color: var(--c-accent); }
.dt-tweet-type   { font-size: 11px; color: var(--c-muted); }
.dt-tweet-text   { font-size: 13px; color: var(--c-text); margin-top: .4rem; line-height: 1.5; }

.dt-persona {
  background: var(--c-card);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 1rem 1.1rem;
}
.dt-persona-name { font-size: 14px; font-weight: 600; color: var(--c-text); }
.dt-persona-info { font-size: 12px; color: var(--c-muted); margin: .2rem 0 .4rem; }
.dt-persona-story{ font-size: 12px; color: #94a3b8; line-height: 1.5; }

.dt-roi-box {
  text-align: center;
  background: linear-gradient(135deg, rgba(34,197,94,.1), rgba(59,130,246,.05));
  border: 1px solid rgba(34,197,94,.3);
  border-radius: 14px;
  padding: 1.5rem;
}
.dt-roi-label { font-size: 12px; color: var(--c-muted); text-transform: uppercase; letter-spacing: .07em; }
.dt-roi-value { font-size: 2.8rem; font-weight: 800; color: var(--c-green); line-height: 1; margin: .3rem 0; }
.dt-roi-sub { font-size: 12px; color: #94a3b8; }

.report-card-grade-A  { background: rgba(34,197,94,.15);  border: 2px solid #22c55e; color: #22c55e; }
.report-card-grade-B  { background: rgba(59,130,246,.15); border: 2px solid #3b82f6; color: #3b82f6; }
.report-card-grade-C  { background: rgba(245,158,11,.15); border: 2px solid #f59e0b; color: #f59e0b; }
.report-card-grade-D  { background: rgba(239,68,68,.15);  border: 2px solid #ef4444; color: #ef4444; }
</style>
""", unsafe_allow_html=True)


# ─── CONSTANTS ────────────────────────────────────────────────────────────────
DELHI_NEIGHBORHOODS = [
    {"name": "Connaught Place",   "lat": 28.6315, "lng": 77.2167},
    {"name": "Dwarka",            "lat": 28.5921, "lng": 77.0460},
    {"name": "Rohini",            "lat": 28.7495, "lng": 77.0670},
    {"name": "Lajpat Nagar",      "lat": 28.5710, "lng": 77.2440},
    {"name": "Karol Bagh",        "lat": 28.6514, "lng": 77.1907},
    {"name": "Saket",             "lat": 28.5246, "lng": 77.2166},
    {"name": "Janakpuri",         "lat": 28.6286, "lng": 77.0823},
    {"name": "Pitampura",         "lat": 28.7007, "lng": 77.1321},
    {"name": "Vasant Kunj",       "lat": 28.5200, "lng": 77.1577},
    {"name": "Shahdara",          "lat": 28.6729, "lng": 77.2921},
    {"name": "Mayur Vihar",       "lat": 28.6108, "lng": 77.2927},
    {"name": "Rajouri Garden",    "lat": 28.6495, "lng": 77.1219},
    {"name": "Nehru Place",       "lat": 28.5491, "lng": 77.2518},
    {"name": "Hauz Khas",         "lat": 28.5494, "lng": 77.2001},
    {"name": "Noida Sector 18",   "lat": 28.5691, "lng": 77.3211},
    {"name": "Gurugram",          "lat": 28.4595, "lng": 77.0266},
    {"name": "Civil Lines",       "lat": 28.6799, "lng": 77.2252},
    {"name": "Kirti Nagar",       "lat": 28.6565, "lng": 77.1476},
    {"name": "Uttam Nagar",       "lat": 28.6208, "lng": 77.0555},
    {"name": "Laxmi Nagar",       "lat": 28.6298, "lng": 77.2777},
]

TRANSPORT_COLORS = {
    "Metro":   "#3b82f6",
    "Bus":     "#22c55e",
    "Auto":    "#f59e0b",
    "Walking": "#a78bfa",
}

AGENT_CONFIG = {
    "government":  {"label": "Government",        "color": "#3b82f6", "emoji": "🏛️"},
    "transport":   {"label": "Transport Auth.",    "color": "#22c55e", "emoji": "🚇"},
    "environment": {"label": "Environment",        "color": "#10b981", "emoji": "🌿"},
    "citizens":    {"label": "Citizens",           "color": "#f59e0b", "emoji": "👥"},
    "business":    {"label": "Business",           "color": "#a78bfa", "emoji": "💼"},
}

BASE_T = {
    "Metro":   {"cost": 5, "time": 8, "comfort": 7, "safety": 8},
    "Bus":     {"cost": 8, "time": 5, "comfort": 4, "safety": 5},
    "Auto":    {"cost": 3, "time": 9, "comfort": 8, "safety": 6},
    "Walking": {"cost": 10,"time": 2, "comfort": 2, "safety": 7},
}

POLICIES = [
    "── Classic ──",
    "Free Metro Rides For Women",
    "50% Bus Fare Reduction",
    "Congestion Tax",
    "New Metro Line",
    "── New ──",
    "Metro Operating Hours Extended to 2 AM",
    "Airport Express Fare Reduction",
    "Reserved Student Coaches",
    "Personal Carbon Budget",
    "Free Transit Birthdays",
    "Car-Free School Zones",
    "One-Ticket City",
    "Free EV Parking",
]

CLAUDE_MODEL = "claude-sonnet-4-6"


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def claude(prompt: str, system: str = "", max_tokens: int = 800) -> str:
    body = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json=body, timeout=25,
        )
        return r.json()["content"][0]["text"].strip()
    except Exception as e:
        return f"[API error: {e}]"


def grade(score: float, max_score: float = 100) -> tuple[str, str]:
    pct = score / max_score * 100
    if pct >= 80: return "A", "report-card-grade-A"
    if pct >= 65: return "B", "report-card-grade-B"
    if pct >= 50: return "C", "report-card-grade-C"
    return "D", "report-card-grade-D"


def policy_effects(policy: str, citizen_type: str, scores: dict) -> dict:
    """Apply policy multipliers to base transport scores."""
    s = {k: dict(v) for k, v in scores.items()}
    if policy == "Free Metro Rides For Women":
        if "Female" in citizen_type: s["Metro"]["cost"] = 10
    elif policy == "50% Bus Fare Reduction":
        s["Bus"]["cost"] = min(10, s["Bus"]["cost"] + 3)
    elif policy == "Congestion Tax":
        s["Auto"]["cost"] = max(1, s["Auto"]["cost"] - 4)
    elif policy == "New Metro Line":
        s["Metro"]["time"] = 10; s["Metro"]["comfort"] = 9
    elif policy == "Metro Operating Hours Extended to 2 AM":
        s["Metro"]["time"] = 9; s["Metro"]["safety"] = 9
    elif policy == "Airport Express Fare Reduction":
        s["Metro"]["cost"] = min(10, s["Metro"]["cost"] + 2)
    elif policy == "Reserved Student Coaches":
        if "Student" in citizen_type: s["Metro"]["comfort"] = 9; s["Metro"]["safety"] = 10
    elif policy == "Personal Carbon Budget":
        s["Auto"]["cost"] = max(1, s["Auto"]["cost"] - 3)
        s["Metro"]["cost"] = min(10, s["Metro"]["cost"] + 2)
    elif policy == "Free Transit Birthdays":
        s["Metro"]["cost"] = 8; s["Bus"]["cost"] = 9
    elif policy == "Car-Free School Zones":
        s["Walking"]["safety"] = 10; s["Bus"]["safety"] = 9
    elif policy == "One-Ticket City":
        s["Metro"]["cost"] = min(10, s["Metro"]["cost"] + 1)
        s["Bus"]["cost"] = min(10, s["Bus"]["cost"] + 1)
    elif policy == "Free EV Parking":
        s["Auto"]["comfort"] = min(10, s["Auto"]["comfort"] + 1)
    return s


def decide(citizen: dict, policy: str) -> str:
    opts = policy_effects(policy, citizen.get("type", ""), BASE_T)
    dist = citizen.get("commute_distance_km", 8)
    best, best_sc = "Metro", -9e9
    for mode, v in opts.items():
        sc = (citizen.get("budget_sensitivity", 5) * v["cost"] +
              citizen.get("time_sensitivity", 5) * v["time"] +
              citizen.get("comfort_sensitivity", 5) * v["comfort"] +
              citizen.get("safety_sensitivity", 5) * v["safety"])
        if mode == "Walking":   sc += 40 if dist <= 2 else (10 if dist <= 5 else -100)
        elif mode == "Metro":   sc += (15 if dist >= 5 else 0) + (25 if dist >= 10 else 0)
        elif mode == "Bus":     sc += (10 if dist >= 3 else 0) + (15 if dist >= 8 else 0)
        elif mode == "Auto":    sc += (10 if dist >= 3 else 0) + (5 if dist >= 8 else 0)
        if sc > best_sc: best_sc = sc; best = mode
    return best


def normalise_mode(raw: str) -> str:
    if raw in ("Auto Rickshaw","Cab","Car","Scooter","Bike","Auto"): return "Auto"
    if raw == "Bus": return "Bus"
    if raw == "Walking": return "Walking"
    return "Metro"


@st.cache_data(ttl=3600)
def load_citizens():
    for fname in ["enhanced_citizens.json", "citizens.json"]:
        if os.path.exists(fname):
            with open(fname) as f: return json.load(f)
    # Fallback synthetic citizens
    types = ["Female Student","Female Office Worker","Male Office Worker","Auto Driver","Shop Owner"]
    sens = {
        "Female Student":       {"budget":9,"time":5,"comfort":3,"safety":8},
        "Female Office Worker": {"budget":6,"time":9,"comfort":7,"safety":9},
        "Male Office Worker":   {"budget":6,"time":9,"comfort":7,"safety":6},
        "Auto Driver":          {"budget":5,"time":8,"comfort":4,"safety":5},
        "Shop Owner":           {"budget":7,"time":6,"comfort":6,"safety":6},
    }
    modes = ["Metro","Bus","Auto","Walking"]
    rng = np.random.default_rng(42)
    out = []
    for i in range(100):
        t = types[i % 5]
        s = sens[t]
        nb = DELHI_NEIGHBORHOODS[i % len(DELHI_NEIGHBORHOODS)]
        out.append({
            "id": i, "type": t,
            "monthly_income": int(rng.integers(8000, 80000)),
            "commute_distance_km": float(rng.uniform(1, 25)),
            "current_transport": rng.choice(modes),
            "neighborhood": nb["name"],
            "lat": nb["lat"] + float(rng.uniform(-0.02, 0.02)),
            "lng": nb["lng"] + float(rng.uniform(-0.02, 0.02)),
            **{f"{k}_sensitivity": int(rng.integers(max(1,v-2), min(10,v+2))) for k,v in s.items()},
        })
    return out


def run_sim(citizens: list, policy: str) -> dict:
    before = {}; after = {}
    switched = []
    for c in citizens:
        old = normalise_mode(c.get("current_transport","Metro"))
        new = decide(c, policy)
        before[old] = before.get(old, 0) + 1
        after[new]  = after.get(new, 0) + 1
        if old != new:
            switched.append({"id": c["id"], "type": c.get("type",""), "from": old, "to": new,
                             "name": c.get("neighborhood","Delhi")})
    switches = len(switched)
    metro_gain = after.get("Metro",0) - before.get("Metro",0)
    co2 = max(0, round((after.get("Metro",0) + after.get("Bus",0)*0.4
                         - before.get("Metro",0) - before.get("Bus",0)*0.4) * 0.3, 1))
    mob  = round(min(100, switches * 1.2 + metro_gain * 0.8 + co2 * 0.5), 1)

    # Equity by income
    low = [c for c in citizens if c.get("monthly_income",0) < 10000]
    mid = [c for c in citizens if 10000 <= c.get("monthly_income",0) <= 50000]
    hi  = [c for c in citizens if c.get("monthly_income",0) > 50000]
    def pt_pct(grp, final):
        if not grp: return 0
        return round(sum(1 for c in grp if final.get(normalise_mode(decide(c,policy)),"Auto") in ("Metro","Bus")) / len(grp)*100, 1)
    # simplified equity
    eq_low = round(after.get("Bus",0)/max(1,before.get("Bus",1))*100,1)
    eq_mid = round(after.get("Metro",0)/max(1,before.get("Metro",1))*100,1)
    eq_hi  = 85.0
    eq_idx = round((eq_low + eq_mid + eq_hi)/3, 1)

    return {
        "policy": policy,
        "citizens_simulated": len(citizens),
        "transport_before": before,
        "transport_after": after,
        "transport_changes": switches,
        "estimated_co2_reduction": co2,
        "mobility_score": mob,
        "equity_index": eq_idx,
        "switched_citizens": switched[:20],
        "metro_gain": metro_gain,
    }


# ─── FOLIUM MAP ───────────────────────────────────────────────────────────────
def build_folium_map(citizens: list, results: dict, show: str = "after") -> folium.Map:
    m = folium.Map(
        location=[28.6139, 77.2090],
        zoom_start=11,
        tiles="CartoDB dark_matter",
    )
    after_modes = {}
    for c in citizens:
        after_modes[c["id"]] = decide(c, results["policy"])

    heat_metro, heat_bus, heat_auto = [], [], []
    for c in citizens:
        lat = c.get("lat", 28.6139 + np.random.uniform(-0.1, 0.1))
        lng = c.get("lng", 77.2090 + np.random.uniform(-0.1, 0.1))
        mode = after_modes[c["id"]] if show == "after" else normalise_mode(c.get("current_transport","Metro"))
        if mode == "Metro":   heat_metro.append([lat, lng, 1])
        elif mode == "Bus":   heat_bus.append([lat, lng, 1])
        elif mode == "Auto":  heat_auto.append([lat, lng, 1])

    if heat_metro:
        HeatMap(heat_metro, name="Metro commuters", min_opacity=0.4,
                gradient={"0.4":"#1d4ed8","0.7":"#3b82f6","1":"#93c5fd"}, radius=18).add_to(m)
    if heat_bus:
        HeatMap(heat_bus, name="Bus commuters", min_opacity=0.3,
                gradient={"0.4":"#15803d","0.7":"#22c55e","1":"#86efac"}, radius=18).add_to(m)
    if heat_auto:
        HeatMap(heat_auto, name="Auto/car commuters", min_opacity=0.3,
                gradient={"0.4":"#b45309","0.7":"#f59e0b","1":"#fde68a"}, radius=18).add_to(m)

    # Metro line overlay (simplified Yellow line)
    metro_line = [
        [28.5273, 77.1786],[28.5489,77.1824],[28.5700,77.1880],
        [28.5936,77.1913],[28.6139,77.2090],[28.6388,77.2188],
        [28.6629,77.2271],[28.6874,77.2327],[28.7076,77.2351],
    ]
    folium.PolyLine(metro_line, color="#fbbf24", weight=3, opacity=0.7,
                    tooltip="Yellow Line (Samaypur Badli → HUDA City Centre)").add_to(m)

    folium.LayerControl().add_to(m)
    return m


# ─── AQI FETCH ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def fetch_aqi() -> dict:
    try:
        r = requests.get(
            "https://api.waqi.info/feed/delhi/?token=demo",
            timeout=6
        )
        d = r.json()
        if d.get("status") == "ok":
            aqi = d["data"]["aqi"]
            return {"aqi": aqi, "status": "live", "source": "AQICN"}
    except:
        pass
    # Realistic Delhi fallback (seasonal average)
    return {"aqi": 187, "status": "estimated", "source": "Seasonal avg"}


def aqi_label(v: int) -> tuple[str, str]:
    if v <= 50:  return "Good",      "#22c55e"
    if v <= 100: return "Moderate",  "#84cc16"
    if v <= 150: return "Unhealthy (sensitive)", "#f59e0b"
    if v <= 200: return "Unhealthy", "#f97316"
    if v <= 300: return "Very Unhealthy", "#ef4444"
    return "Hazardous", "#7f1d1d"


# ─── COST-BENEFIT ─────────────────────────────────────────────────────────────
def cost_benefit(results: dict, budget_cr: float) -> dict:
    switches = results["transport_changes"]
    avg_commute_saved_min = 8
    median_wage_pm = 25000
    monthly_wage_per_min = median_wage_pm / (22 * 8 * 60)
    benefit_per_switch_pm = avg_commute_saved_min * monthly_wage_per_min * 22
    total_benefit_pm = benefit_per_switch_pm * switches
    total_benefit_cr = total_benefit_pm * 12 / 1e7
    roi = round(total_benefit_cr / max(budget_cr, 0.1), 2)
    return {
        "budget_cr": budget_cr,
        "benefit_cr": round(total_benefit_cr, 2),
        "roi": roi,
        "switches": switches,
        "time_saved_hrs_pa": round(switches * avg_commute_saved_min * 22 * 12 / 60, 0),
        "co2_reduction": results.get("estimated_co2_reduction", 0),
    }


# ─── LLM FEATURES ────────────────────────────────────────────────────────────
def get_agent_report(agent: str, results: dict) -> str:
    personas = {
        "government":  "You are the Delhi Government Chief Policy Advisor. Write a 3-paragraph brief: recommendation (APPROVE/REVIEW/REJECT), key metrics, implementation steps.",
        "transport":   "You are Delhi Metro & Transport Authority Chief. Write a 3-paragraph operational brief: capacity, service changes, risks.",
        "environment": "You are Delhi's Chief Environmental Officer. Write a 3-paragraph assessment: AQI impact, CO2 estimate, sustainability.",
        "citizens":    "You are Delhi Citizens Welfare Analyst. Write a 3-paragraph report: who benefits, equity, behavioural insights.",
        "business":    "You are Delhi Urban Economics Analyst. Write a 3-paragraph brief: footfall, economic opportunity, sector impacts.",
    }
    summary = json.dumps({k: results[k] for k in
        ["policy","transport_before","transport_after","transport_changes",
         "estimated_co2_reduction","mobility_score","equity_index"] if k in results})
    return claude(f"Simulation data:\n{summary}\n\nWrite your report.", system=personas[agent], max_tokens=500)


def generate_tweets(citizens: list, results: dict) -> list:
    sample = results.get("switched_citizens", [])[:8]
    citizen_info = [{"type": c["type"], "from": c["from"], "to": c["to"],
                     "area": c.get("name","Delhi")} for c in sample]
    prompt = f"""Policy: {results['policy']}
Citizen decisions: {json.dumps(citizen_info)}

Generate one tweet per citizen reacting emotionally to this Delhi transport policy.
Include: a realistic Delhi-sounding username (@handle), their citizen type emoji, 1-2 relevant hashtags, authentic reaction (mix of happy/skeptical/neutral).
Return ONLY a JSON array, no preamble:
[{{"handle":"@xyz","type":"Female Student","emoji":"🎓","tweet":"tweet text here #hashtag"}}]"""
    raw = claude(prompt, max_tokens=800)
    raw = raw.replace("```json","").replace("```","").strip()
    try: return json.loads(raw)
    except: return []


def generate_counterfactuals(results: dict) -> list:
    prompt = f"""Policy simulated: {results['policy']}
Outcome: {results['transport_changes']} citizens switched, mobility score {results['mobility_score']}, CO2 reduction {results['estimated_co2_reduction']}.

Generate 3 follow-up "what if" policy variants a Delhi planner would want to explore.
Each should be a concrete tweak that might improve outcomes.
Return ONLY a JSON array:
[{{"question":"What if we also added last-mile e-bikes?","hint":"adds cycling infrastructure"}}]"""
    raw = claude(prompt, max_tokens=400)
    raw = raw.replace("```json","").replace("```","").strip()
    try: return json.loads(raw)
    except: return [
        {"question":"What if we extended this policy to NCR?","hint":"regional expansion"},
        {"question":"What if we combined this with last-mile e-bikes?","hint":"multi-modal"},
        {"question":"What if subsidy was only for off-peak hours?","hint":"time-based"},
    ]


def generate_debate(results: dict) -> list:
    agents = list(AGENT_CONFIG.keys())
    summary = f"Policy: {results['policy']}. Switches: {results['transport_changes']}. Mobility: {results['mobility_score']}. CO2: {results['estimated_co2_reduction']}."
    messages = []
    # Round 1: each agent makes their case (2 agents for speed)
    for ag in ["government","environment","citizens"]:
        cfg = AGENT_CONFIG[ag]
        persona = f"You are the {cfg['label']} agent. In 2 sentences, make your case FOR or AGAINST this policy using the simulation data."
        resp = claude(f"Data: {summary}", system=persona, max_tokens=120)
        messages.append({"agent": ag, "round": 1, "text": resp})
    # Round 2: rebuttals
    history = " | ".join(f"{m['agent']}: {m['text']}" for m in messages)
    for ag in ["transport","business"]:
        cfg = AGENT_CONFIG[ag]
        persona = f"You are the {cfg['label']} agent. In 2 sentences, rebut one point from this debate and add your perspective."
        resp = claude(f"Data: {summary}\nDebate so far: {history}", system=persona, max_tokens=120)
        messages.append({"agent": ag, "round": 2, "text": resp})
    return messages


def generate_personas(citizens: list, results: dict) -> list:
    sample = results.get("switched_citizens", [])[:6]
    delhi_names = ["Priya Sharma","Rahul Gupta","Anjali Singh","Mohammad Alam",
                   "Sunita Devi","Amit Verma","Neha Jain","Arjun Mehta"]
    info = [{"name": delhi_names[i % len(delhi_names)], "type": c["type"],
             "area": c.get("name","Dwarka"), "from": c["from"], "to": c["to"]}
            for i, c in enumerate(sample)]
    prompt = f"""Policy: {results['policy']}
Citizens who switched transport: {json.dumps(info)}

For each person, write a 2-sentence personal story about their daily commute and reaction to this policy.
Return ONLY a JSON array:
[{{"name":"Priya Sharma","area":"Dwarka","type":"Female Student","from":"Auto","to":"Metro","story":"story here"}}]"""
    raw = claude(prompt, max_tokens=700)
    raw = raw.replace("```json","").replace("```","").strip()
    try: return json.loads(raw)
    except: return info


# ─── PPTX EXPORT ─────────────────────────────────────────────────────────────
def export_pptx(results: dict, cb: dict) -> bytes:
    """Generate a 5-slide branded PowerPoint."""
    import subprocess, tempfile, os

    policy = results["policy"]
    switches = results["transport_changes"]
    mob = results["mobility_score"]
    co2 = results["estimated_co2_reduction"]
    eq  = results.get("equity_index", 0)
    g_letter, _ = grade(mob)

    before = results.get("transport_before", {})
    after  = results.get("transport_after", {})

    js = f"""
const pptx = require('pptxgenjs');
const pres = new pptx();
pres.layout = 'LAYOUT_16x9';
pres.title = 'Delhi Digital Twin — {policy}';
pres.author = 'Delhi Digital Twin';

const NAVY   = '0a0e1a';
const BLUE   = '3b82f6';
const GREEN  = '22c55e';
const AMBER  = 'f59e0b';
const WHITE  = 'f1f5f9';
const MUTED  = '64748b';
const CARD   = '1a2235';
const BORDER = '2a3548';

// ─── Slide 1: Title ───────────────────────────────────────────────────────────
let s1 = pres.addSlide();
s1.background = {{ color: NAVY }};
s1.addShape(pres.shapes.RECTANGLE, {{x:0,y:0,w:13.3,h:0.04,fill:{{color:BLUE}},line:{{color:BLUE}}}});
s1.addText('🚇 DELHI DIGITAL TWIN', {{x:0.6,y:0.5,w:12,h:0.5,fontSize:11,color:MUTED,bold:true,charSpacing:4}});
s1.addText('{policy}', {{x:0.6,y:1.1,w:12,h:1.6,fontSize:40,color:WHITE,bold:true,fontFace:'Calibri'}});
s1.addText('Agent-Based Urban Policy Simulation Report', {{x:0.6,y:2.9,w:10,h:0.5,fontSize:16,color:MUTED}});
s1.addShape(pres.shapes.RECTANGLE, {{x:0.6,y:3.7,w:1.8,h:0.7,fill:{{color:BLUE}},line:{{color:BLUE}},rounding:true}});
s1.addText('Grade {g_letter}', {{x:0.6,y:3.7,w:1.8,h:0.7,fontSize:20,color:WHITE,bold:true,align:'center',valign:'middle'}});
s1.addText('100 citizens · 5 AI agents · Real Delhi data', {{x:0.6,y:4.8,w:10,h:0.4,fontSize:12,color:MUTED,italic:true}});

// ─── Slide 2: Key Metrics ─────────────────────────────────────────────────────
let s2 = pres.addSlide();
s2.background = {{ color: NAVY }};
s2.addShape(pres.shapes.RECTANGLE, {{x:0,y:0,w:13.3,h:0.04,fill:{{color:BLUE}},line:{{color:BLUE}}}});
s2.addText('KEY METRICS', {{x:0.6,y:0.2,w:12,h:0.4,fontSize:10,color:MUTED,bold:true,charSpacing:4}});
s2.addText('Simulation Results at a Glance', {{x:0.6,y:0.65,w:12,h:0.7,fontSize:26,color:WHITE,bold:true}});

const metrics = [
  {{label:'Citizens Switched', value:'{switches}', color:BLUE, x:0.4}},
  {{label:'Mobility Score', value:'{mob}', color:GREEN, x:3.6}},
  {{label:'CO₂ Reduction', value:'{co2}', color:AMBER, x:6.8}},
  {{label:'Equity Index', value:'{eq}', color:'a78bfa', x:10.0}},
];
metrics.forEach(m => {{
  s2.addShape(pres.shapes.RECTANGLE, {{x:m.x,y:1.6,w:2.7,h:2.2,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
  s2.addText(m.value, {{x:m.x,y:1.8,w:2.7,h:1.1,fontSize:42,color:m.color,bold:true,align:'center',valign:'middle'}});
  s2.addText(m.label, {{x:m.x,y:3.1,w:2.7,h:0.5,fontSize:12,color:MUTED,align:'center'}});
}});

s2.addShape(pres.shapes.RECTANGLE, {{x:0.4,y:4.1,w:12.5,h:0.8,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
s2.addText('Transport shift: Metro +{after.get("Metro",0)-before.get("Metro",0):+d} · Bus +{after.get("Bus",0)-before.get("Bus",0):+d} · Auto {after.get("Auto",0)-before.get("Auto",0):+d} citizens', {{x:0.4,y:4.1,w:12.5,h:0.8,fontSize:14,color:WHITE,align:'center',valign:'middle'}});

// ─── Slide 3: Simulation ──────────────────────────────────────────────────────
let s3 = pres.addSlide();
s3.background = {{ color: NAVY }};
s3.addShape(pres.shapes.RECTANGLE, {{x:0,y:0,w:13.3,h:0.04,fill:{{color:GREEN}},line:{{color:GREEN}}}});
s3.addText('SIMULATION', {{x:0.6,y:0.2,w:12,h:0.4,fontSize:10,color:MUTED,bold:true,charSpacing:4}});
s3.addText('How Did 100 Citizens Respond?', {{x:0.6,y:0.65,w:12,h:0.7,fontSize:26,color:WHITE,bold:true}});

const modes = ['Metro','Bus','Auto','Walking'];
const bvals = [{before.get("Metro",0)},{before.get("Bus",0)},{before.get("Auto",0)},{before.get("Walking",0)}];
const avals = [{after.get("Metro",0)},{after.get("Bus",0)},{after.get("Auto",0)},{after.get("Walking",0)}];
const mcolors = [BLUE, GREEN, AMBER, 'a78bfa'];

s3.addText('BEFORE', {{x:1.5,y:1.5,w:4,h:0.3,fontSize:10,color:MUTED,bold:true,align:'center'}});
s3.addText('AFTER', {{x:7.5,y:1.5,w:4,h:0.3,fontSize:10,color:MUTED,bold:true,align:'center'}});

modes.forEach((mode, i) => {{
  const y = 1.9 + i * 0.75;
  // Before
  s3.addShape(pres.shapes.RECTANGLE, {{x:1.5,y:y,w:4,h:0.55,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
  s3.addShape(pres.shapes.RECTANGLE, {{x:1.55,y:y+0.05,w:Math.max(0.1,bvals[i]/100*3.7),h:0.45,fill:{{color:mcolors[i]}},line:{{color:mcolors[i]}},rounding:true}});
  s3.addText(mode+' '+bvals[i], {{x:1.6,y:y,w:3.8,h:0.55,fontSize:12,color:WHITE,valign:'middle'}});
  // After
  s3.addShape(pres.shapes.RECTANGLE, {{x:7.5,y:y,w:4,h:0.55,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
  s3.addShape(pres.shapes.RECTANGLE, {{x:7.55,y:y+0.05,w:Math.max(0.1,avals[i]/100*3.7),h:0.45,fill:{{color:mcolors[i]}},line:{{color:mcolors[i]}},rounding:true}});
  s3.addText(mode+' '+avals[i], {{x:7.6,y:y,w:3.8,h:0.55,fontSize:12,color:WHITE,valign:'middle'}});
  // Arrow
  s3.addShape(pres.shapes.CHEVRON, {{x:5.7,y:y+0.1,w:1.4,h:0.35,fill:{{color:BORDER}},line:{{color:BORDER}}}});
}});

// ─── Slide 4: AI Agent Consensus ─────────────────────────────────────────────
let s4 = pres.addSlide();
s4.background = {{ color: NAVY }};
s4.addShape(pres.shapes.RECTANGLE, {{x:0,y:0,w:13.3,h:0.04,fill:{{color:'a78bfa'}},line:{{color:'a78bfa'}}}});
s4.addText('AI AGENTS', {{x:0.6,y:0.2,w:12,h:0.4,fontSize:10,color:MUTED,bold:true,charSpacing:4}});
s4.addText('Multi-Agent Analysis', {{x:0.6,y:0.65,w:12,h:0.7,fontSize:26,color:WHITE,bold:true}});

const agents = [
  {{emoji:'🏛️', label:'Government',     color:'3b82f6'}},
  {{emoji:'🚇', label:'Transport Auth.',color:'22c55e'}},
  {{emoji:'🌿', label:'Environment',    color:'10b981'}},
  {{emoji:'👥', label:'Citizens',       color:'f59e0b'}},
  {{emoji:'💼', label:'Business',       color:'a78bfa'}},
];
agents.forEach((ag, i) => {{
  const col = i < 3 ? 0.4 : 4.5;
  const row = i < 3 ? i : i - 3;
  const y = 1.6 + row * 1.05;
  const x = col;
  s4.addShape(pres.shapes.RECTANGLE, {{x,y,w:3.6,h:0.85,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
  s4.addText(ag.emoji + ' ' + ag.label, {{x:x+0.1,y,w:3.4,h:0.4,fontSize:13,color:'#'+ag.color,bold:true,valign:'middle'}});
  s4.addText('See full report in the simulation app', {{x:x+0.1,y:y+0.38,w:3.4,h:0.4,fontSize:10,color:MUTED,italic:true}});
}});
s4.addShape(pres.shapes.RECTANGLE, {{x:8.5,y:1.5,w:4.4,h:3.2,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
s4.addText('Policy Verdict', {{x:8.6,y:1.6,w:4.2,h:0.5,fontSize:14,color:MUTED,align:'center'}});
s4.addText('{g_letter}', {{x:8.6,y:2.1,w:4.2,h:1.2,fontSize:72,color:BLUE,bold:true,align:'center'}});
s4.addText('Overall Grade', {{x:8.6,y:3.3,w:4.2,h:0.4,fontSize:12,color:MUTED,align:'center'}});
s4.addText('Mobility {mob} · Equity {eq} · CO₂ {co2}', {{x:8.6,y:3.7,w:4.2,h:0.5,fontSize:10,color:MUTED,align:'center'}});

// ─── Slide 5: Recommendation ──────────────────────────────────────────────────
let s5 = pres.addSlide();
s5.background = {{ color: NAVY }};
s5.addShape(pres.shapes.RECTANGLE, {{x:0,y:0,w:13.3,h:0.04,fill:{{color:GREEN}},line:{{color:GREEN}}}});
s5.addText('RECOMMENDATION', {{x:0.6,y:0.2,w:12,h:0.4,fontSize:10,color:MUTED,bold:true,charSpacing:4}});
s5.addText('Next Steps for Delhi', {{x:0.6,y:0.65,w:12,h:0.7,fontSize:26,color:WHITE,bold:true}});

const steps = [
  '🎯  Phase 1: Pilot this policy in 3 high-density corridors (Dwarka–Connaught, Rohini–Kashmere Gate, Noida)',
  '📊  Phase 2: Monitor ridership and AQI weekly — target 15% modal shift within 6 months',
  '💬  Phase 3: Citizen feedback surveys, adjust policy parameters based on equity data',
  '🌿  Phase 4: Scale city-wide if pilot shows >20% reduction in private vehicle trips',
];
steps.forEach((step, i) => {{
  s5.addShape(pres.shapes.RECTANGLE, {{x:0.6,y:1.6+i*0.95,w:12,h:0.75,fill:{{color:CARD}},line:{{color:BORDER}},rounding:true}});
  s5.addText(step, {{x:0.8,y:1.6+i*0.95,w:11.6,h:0.75,fontSize:13,color:WHITE,valign:'middle'}});
}});
s5.addShape(pres.shapes.RECTANGLE, {{x:0.6,y:5.0,w:12,h:0.5,fill:{{color:'0f172a'}},line:{{color:BORDER}},rounding:true}});
s5.addText('Generated by Delhi Digital Twin · Powered by Claude AI · delhi-digital-twin.streamlit.app', {{x:0.6,y:5.0,w:12,h:0.5,fontSize:10,color:MUTED,align:'center',valign:'middle',italic:true}});

pres.writeFile({{fileName:'delhi_policy_deck.pptx'}}).then(()=>console.log('done'));
"""
    tmpdir = tempfile.mkdtemp()
    js_path = os.path.join(tmpdir, "gen.js")
    with open(js_path, "w") as f: f.write(js)

    try:
        result = subprocess.run(
            ["node", js_path], cwd=tmpdir,
            capture_output=True, text=True, timeout=30
        )
        pptx_path = os.path.join(tmpdir, "delhi_policy_deck.pptx")
        if os.path.exists(pptx_path):
            with open(pptx_path, "rb") as f: return f.read()
    except Exception as e:
        st.error(f"PPTX generation failed: {e}")
    return b""


# ─── PDF EXPORT (simple, always works) ───────────────────────────────────────
def export_pdf_simple(results: dict, cb: dict) -> BytesIO:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.units import cm

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_s = ParagraphStyle("t", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1e40af"), spaceAfter=8)
    h1_s    = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=13, textColor=colors.HexColor("#1e293b"), spaceBefore=12, spaceAfter=4)
    body_s  = ParagraphStyle("b", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=4)

    story = []
    story.append(Paragraph("Delhi Digital Twin", title_s))
    story.append(Paragraph(f"Policy Simulation: {results['policy']}", styles["Heading2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1")))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Key Metrics", h1_s))
    g_letter, _ = grade(results["mobility_score"])
    tdata = [["Metric","Value"],
             ["Citizens Simulated", str(results["citizens_simulated"])],
             ["Mode Switches", str(results["transport_changes"])],
             ["Mobility Score", f"{results['mobility_score']}/100"],
             ["CO₂ Reduction Score", str(results["estimated_co2_reduction"])],
             ["Equity Index", f"{results.get('equity_index',0)}/100"],
             ["Policy Grade", g_letter],
             ["ROI (vs budget)", f"{cb['roi']}x"],
             ["Economic Benefit (est.)", f"₹{cb['benefit_cr']:.1f} Cr/yr"],]
    t = Table(tdata, colWidths=[8*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e40af")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.HexColor("#e2e8f0")]),
        ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#cbd5e1")),
        ("PADDING",(0,0),(-1,-1),6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Transport Mode Shift", h1_s))
    before = results.get("transport_before", {}); after = results.get("transport_after", {})
    modes = sorted(set(before)|set(after))
    tdata2 = [["Mode","Before","After","Change"]]
    for m in modes:
        b=before.get(m,0); a=after.get(m,0)
        tdata2.append([m,str(b),str(a),f"{a-b:+d}"])
    t2 = Table(tdata2, colWidths=[5*cm,3*cm,3*cm,3*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e40af")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.HexColor("#e2e8f0")]),
        ("GRID",(0,0),(-1,-1),.5,colors.HexColor("#cbd5e1")),
        ("PADDING",(0,0),(-1,-1),6),
    ]))
    story.append(t2)
    doc.build(story)
    buf.seek(0); return buf


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.5rem 0 1rem'>
      <div style='font-size:1.3rem;font-weight:700;color:#f1f5f9'>🚇 Delhi Twin</div>
      <div style='font-size:11px;color:#64748b;margin-top:3px'>Urban Policy Simulator</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Mode**")
    mode = st.radio("", ["Single Policy","Compare All"], label_visibility="collapsed")

    if mode == "Single Policy":
        st.markdown("**Policy source**")
        psrc = st.radio("", ["Preset","Natural language"], label_visibility="collapsed", horizontal=True)
        if psrc == "Preset":
            policy = st.selectbox("Choose policy", POLICIES)
            nl_input = None
        else:
            nl_input = st.text_area("Describe your policy", placeholder="e.g. Subsidise e-rickshaws by 40%", height=90)
            policy = nl_input or "Free Metro Rides For Women"

    st.divider()
    use_llm = st.toggle("🤖 AI features", value=True, help="Enables Claude-powered tweets, debate, counterfactuals")
    budget_cr = st.slider("Policy budget (₹ Crore)", 1, 500, 50, help="Used for cost-benefit calculation")

    st.divider()
    run_btn = st.button("▶ Run Simulation", use_container_width=True, type="primary")
    st.caption("100 Delhi citizens · 5 AI archetypes · 4 transport modes")


# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='dt-hero'>
  <div class='dt-hero-badge'>🌆 FAR AWAY Hackathon · Urban Intelligence</div>
  <h1>Delhi's Digital Twin</h1>
  <p>Multi-agent AI simulating 100 Delhi citizens across 5 archetypes · Real AQI data · Live map · AI policy debate</p>
</div>
""", unsafe_allow_html=True)

# ─── AQI STRIP ────────────────────────────────────────────────────────────────
aqi_data = fetch_aqi()
aqi_val = aqi_data["aqi"]
aqi_lbl, aqi_color = aqi_label(aqi_val)
needle_pct = min(98, aqi_val / 400 * 100)
st.markdown(f"""
<div class='dt-card' style='margin-bottom:.75rem;padding:.9rem 1.4rem'>
  <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:.5rem'>
    <span style='font-size:13px;font-weight:600;color:#94a3b8'>🌫 Delhi AQI Right Now
      <span style='font-size:10px;margin-left:6px;color:#475569'>({aqi_data["source"]})</span>
    </span>
    <span style='font-size:20px;font-weight:800;color:{aqi_color}'>{aqi_val} — {aqi_lbl}</span>
  </div>
  <div class='dt-aqi-bar'>
    <div class='dt-aqi-needle' style='left:{needle_pct}%'></div>
  </div>
  <div style='display:flex;justify-content:space-between;font-size:10px;color:#475569;margin-top:3px'>
    <span>0 Good</span><span>100 Moderate</span><span>200 Unhealthy</span><span>400 Hazardous</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── MAIN LOGIC ───────────────────────────────────────────────────────────────
citizens = load_citizens()

if run_btn:
    if policy in ("── Classic ──", "── New ──"):
        st.warning("Please select a specific policy.")
        st.stop()

    with st.spinner("🔄 Running simulation…"):
        results = run_sim(citizens, policy)
    st.session_state["results"] = results
    st.session_state["policy"] = policy
    st.session_state["budget_cr"] = budget_cr

results = st.session_state.get("results")

if not results:
    st.info("👈 Choose a policy in the sidebar and click **Run Simulation** to begin.")
    st.stop()


# ─── GRADE BANNER ─────────────────────────────────────────────────────────────
mob   = results["mobility_score"]
co2   = results["estimated_co2_reduction"]
eq    = results.get("equity_index", 0)
switches = results["transport_changes"]
g_letter, g_class = grade(mob)

col_grade, col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns([1, 2, 2, 2, 2])
with col_grade:
    st.markdown(f"""
    <div class='dt-card' style='text-align:center;padding:1.1rem'>
      <div class='dt-card-title'>Policy grade</div>
      <div class='dt-grade {g_class}'>{g_letter}</div>
      <div style='font-size:11px;color:#64748b'>{results["policy"][:28]}…</div>
    </div>""", unsafe_allow_html=True)
with col_kpi1:
    st.metric("Citizens switched", f"{switches}")
with col_kpi2:
    st.metric("Mobility score", f"{mob}/100")
with col_kpi3:
    st.metric("CO₂ reduction", f"+{co2}")
with col_kpi4:
    st.metric("Equity index", f"{eq}/100")

# Projected AQI improvement
proj_aqi = max(50, round(aqi_val * (1 - co2 / 300), 0))
st.markdown(f"""
<div style='background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);border-radius:12px;
     padding:.75rem 1.4rem;margin:.5rem 0 1rem;display:flex;align-items:center;gap:12px'>
  <span style='font-size:1.4rem'>🌿</span>
  <div>
    <span style='font-size:14px;color:#f1f5f9;font-weight:600'>This policy could bring Delhi AQI from
    <span style='color:#ef4444'>{aqi_val}</span> →
    <span style='color:#22c55e'>~{int(proj_aqi)}</span></span>
    <span style='font-size:12px;color:#64748b;margin-left:8px'>(model estimate based on modal shift)</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── TABS ─────────────────────────────────────────────────────────────────────
tabs = st.tabs(["🗺 Live Map", "📊 Analysis", "🤖 AI Debate", "🐦 Citizen Reactions",
                "💰 Cost-Benefit", "🔮 What If?", "📤 Export"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE MAP
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("### 🗺 Delhi Commuter Heatmap")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Before policy**")
        m_before = build_folium_map(citizens, results, show="before")
        components.html(m_before._repr_html_(), height=420)

    with col_b:
        st.markdown("**After policy**")
        m_after = build_folium_map(citizens, results, show="after")
        components.html(m_after._repr_html_(), height=420)

    st.markdown("""
    <div style='display:flex;gap:20px;margin-top:.5rem;flex-wrap:wrap'>
      <span style='font-size:12px;color:#64748b'>
        <span style='display:inline-block;width:10px;height:10px;border-radius:50%;background:#3b82f6;margin-right:5px'></span>Metro commuters
        <span style='margin-left:12px;display:inline-block;width:10px;height:10px;border-radius:50%;background:#22c55e;margin-right:5px'></span>Bus commuters
        <span style='margin-left:12px;display:inline-block;width:10px;height:10px;border-radius:50%;background:#f59e0b;margin-right:5px'></span>Auto/car commuters
        <span style='margin-left:12px;display:inline-block;width:10px;height:10px;background:#fbbf24;margin-right:5px'></span>Metro yellow line
      </span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 📊 Transport Mode Analysis")

    before = results["transport_before"]; after = results["transport_after"]
    modes = sorted(set(before)|set(after))

    def dark_fig(w=9, h=4):
        fig, ax = plt.subplots(figsize=(w, h))
        fig.patch.set_facecolor("#111827"); ax.set_facecolor("#111827")
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        for s in ["bottom","left"]: ax.spines[s].set_color("#2a3548")
        ax.tick_params(colors="#64748b")
        return fig, ax

    c1, c2 = st.columns(2)
    with c1:
        fig, ax = dark_fig()
        x = np.arange(len(modes)); w = 0.38
        bv = [before.get(m,0) for m in modes]; av = [after.get(m,0) for m in modes]
        ax.bar(x-w/2, bv, w, color="#334155", label="Before", alpha=.9)
        bars = ax.bar(x+w/2, av, w, color=[TRANSPORT_COLORS.get(m,"#94a3b8") for m in modes], label="After", alpha=.9)
        for bar in bars:
            h_val = bar.get_height()
            if h_val > 0:
                ax.text(bar.get_x()+bar.get_width()/2, h_val+.4, str(int(h_val)),
                        ha="center", va="bottom", color="#94a3b8", fontsize=9)
        ax.set_xticks(x); ax.set_xticklabels(modes, color="#94a3b8")
        ax.set_ylabel("Citizens", color="#64748b")
        ax.set_title("Mode Distribution: Before vs After", color="#f1f5f9", pad=10)
        ax.legend(facecolor="#1a2235", labelcolor="#f1f5f9", edgecolor="#2a3548")
        plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    with c2:
        fig, ax = dark_fig()
        # Donut — after
        sizes = [after.get(m,0) for m in modes]
        clrs  = [TRANSPORT_COLORS.get(m,"#64748b") for m in modes]
        wedges, texts, autotexts = ax.pie(sizes, labels=modes, colors=clrs,
                                          autopct="%1.0f%%", startangle=90,
                                          wedgeprops=dict(width=.55, edgecolor="#111827"))
        for at in autotexts: at.set_color("white"); at.set_fontsize(9)
        for t in texts: t.set_color("#94a3b8"); t.set_fontsize(9)
        ax.set_title("Post-Policy Distribution", color="#f1f5f9", pad=10)
        plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    # Radar
    st.markdown("#### 🕸 Policy Radar")
    labels = ["Mobility", "Environment", "Equity", "Economy", "Safety"]
    vals = [
        min(10, mob/10),
        min(10, co2/5),
        min(10, eq/10),
        min(10, switches/10),
        min(10, (after.get("Metro",0)+after.get("Bus",0))/10),
    ]
    vals += vals[:1]
    N = len(labels)
    angles = [n/N*2*math.pi for n in range(N)] + [0]
    fig, ax = plt.subplots(figsize=(5,5), subplot_kw={"polar": True})
    fig.patch.set_facecolor("#111827"); ax.set_facecolor("#111827")
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, color="#94a3b8", size=10)
    ax.set_yticklabels([]); ax.spines["polar"].set_color("#2a3548")
    ax.plot(angles, vals, color="#3b82f6", linewidth=2)
    ax.fill(angles, vals, color="#3b82f6", alpha=.2)
    ax.set_title(f"{results['policy'][:30]}", pad=20, color="#f1f5f9", size=11)
    plt.tight_layout()
    col_r, col_blank = st.columns([1,2])
    with col_r: st.pyplot(fig)
    plt.close(fig)

    # Agent reports (expandable)
    if use_llm:
        st.markdown("#### 🤖 Agent Policy Reports")
        for ag, cfg in AGENT_CONFIG.items():
            with st.expander(f"{cfg['emoji']} {cfg['label']} Report"):
                with st.spinner("Generating…"):
                    rpt = get_agent_report(ag, results)
                st.markdown(f"<div style='font-size:13px;color:#cbd5e1;line-height:1.7'>{rpt}</div>",
                            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI DEBATE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 🤖 AI Agent Policy Debate")
    if not use_llm:
        st.info("Enable AI features in the sidebar to see the agent debate.")
    else:
        if st.button("⚡ Start Debate", type="primary"):
            with st.spinner("Agents are arguing… "):
                debate = generate_debate(results)
            st.session_state["debate"] = debate

        debate = st.session_state.get("debate", [])
        if debate:
            st.markdown(f"**Debating:** _{results['policy']}_")
            for msg in debate:
                cfg = AGENT_CONFIG[msg["agent"]]
                round_label = "Opening argument" if msg["round"]==1 else "Rebuttal"
                st.markdown(f"""
                <div class='dt-debate-msg'>
                  <div class='dt-debate-agent' style='color:{cfg["color"]}'>
                    {cfg["emoji"]} {cfg["label"]} — {round_label}
                  </div>
                  <div class='dt-debate-text'>{msg["text"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Click 'Start Debate' above to watch the agents argue!")

        # Personas
        st.markdown("---")
        st.markdown("### 👤 Citizen Personas")
        if st.button("Generate citizen stories"):
            with st.spinner("Crafting stories…"):
                personas = generate_personas(citizens, results)
            st.session_state["personas"] = personas

        personas = st.session_state.get("personas", [])
        if personas:
            cols = st.columns(3)
            for i, p in enumerate(personas[:6]):
                with cols[i % 3]:
                    t_color = TRANSPORT_COLORS.get(p.get("to","Metro"),"#64748b")
                    st.markdown(f"""
                    <div class='dt-persona'>
                      <div class='dt-persona-name'>{p.get("name","Citizen")}</div>
                      <div class='dt-persona-info'>{p.get("area","Delhi")} · {p.get("type","")}</div>
                      <div style='font-size:11px;margin-bottom:.4rem'>
                        <span style='color:#64748b;text-decoration:line-through'>{p.get("from","Auto")}</span>
                        → <span style='color:{t_color};font-weight:600'>{p.get("to","Metro")}</span>
                      </div>
                      <div class='dt-persona-story'>{p.get("story","")}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CITIZEN REACTIONS (TWITTER WALL)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 🐦 Delhi Citizens React")
    if not use_llm:
        st.info("Enable AI features in the sidebar.")
    else:
        if st.button("🔄 Generate tweets"):
            with st.spinner("Delhi citizens are tweeting…"):
                tweets = generate_tweets(citizens, results)
            st.session_state["tweets"] = tweets

        tweets = st.session_state.get("tweets", [])
        if tweets:
            col_t1, col_t2 = st.columns(2)
            for i, tw in enumerate(tweets):
                col = col_t1 if i % 2 == 0 else col_t2
                with col:
                    st.markdown(f"""
                    <div class='dt-tweet'>
                      <div style='display:flex;justify-content:space-between'>
                        <span class='dt-tweet-handle'>{tw.get("handle","@delhizen")}</span>
                        <span class='dt-tweet-type'>{tw.get("emoji","")} {tw.get("type","")}</span>
                      </div>
                      <div class='dt-tweet-text'>{tw.get("tweet","")}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.caption("Click 'Generate tweets' to see how Delhiites react!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — COST-BENEFIT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 💰 Cost-Benefit Analysis")
    bgt = st.session_state.get("budget_cr", 50)
    cb = cost_benefit(results, bgt)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class='dt-roi-box'>
          <div class='dt-roi-label'>Return on Investment</div>
          <div class='dt-roi-value'>{cb['roi']}x</div>
          <div class='dt-roi-sub'>₹{cb['benefit_cr']:.1f} Cr benefit vs ₹{bgt} Cr cost</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        hrs = int(cb['time_saved_hrs_pa'])
        st.metric("Time saved/year", f"{hrs:,} hrs")
        st.metric("Citizens switched", str(cb["switches"]))
    with c3:
        st.metric("Annual social benefit", f"₹{cb['benefit_cr']:.1f} Cr")
        st.metric("CO₂ reduction score", str(cb["co2_reduction"]))

    st.markdown("---")
    st.markdown("**Methodology**")
    st.markdown(f"""
    | Assumption | Value |
    |---|---|
    | Avg commute time saved per switch | 8 min/day |
    | Working days/month | 22 |
    | Delhi median monthly wage | ₹25,000 |
    | Value of time (per min) | ₹{25000/(22*8*60):.2f} |
    | Citizens switched | {cb['switches']} |
    | Policy budget | ₹{bgt} Cr |
    """)
    st.caption("Estimates are indicative. Real-world benefits depend on implementation scale and commute corridor specifics.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — WHAT IF?
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 🔮 Counterfactual Explorer")
    if not use_llm:
        st.info("Enable AI features in the sidebar.")
    else:
        if st.button("🧠 Generate what-if scenarios"):
            with st.spinner("Claude is imagining alternatives…"):
                cfs = generate_counterfactuals(results)
            st.session_state["counterfactuals"] = cfs

        cfs = st.session_state.get("counterfactuals", [])
        if cfs:
            st.markdown("**Click a scenario to simulate it instantly:**")
            for cf in cfs:
                st.markdown(f"""
                <div class='dt-chip' onclick="void(0)">
                  🔮 {cf.get("question","What if…")}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            sel = st.selectbox("Or pick one to mini-simulate:", [cf["question"] for cf in cfs])
            if st.button("▶ Run counterfactual mini-sim"):
                # Use Claude to map the what-if to a policy, then run sim
                with st.spinner("Simulating alternative…"):
                    cf_prompt = f"""The user asked: '{sel}'
Original policy: {results['policy']}
Translate this into one of these policy names or describe a parameter change:
{json.dumps(POLICIES[1:])}
Return ONLY the closest matching policy name from that list, or the original policy if none match."""
                    alt_policy = claude(cf_prompt, max_tokens=60).strip().strip('"')
                    if alt_policy not in POLICIES:
                        alt_policy = results["policy"]
                    alt_results = run_sim(citizens, alt_policy)

                col_orig, col_alt = st.columns(2)
                with col_orig:
                    st.markdown(f"**Original: {results['policy']}**")
                    st.metric("Switches", results["transport_changes"])
                    st.metric("Mobility", results["mobility_score"])
                    st.metric("CO₂", results["estimated_co2_reduction"])
                with col_alt:
                    st.markdown(f"**Counterfactual: {alt_policy}**")
                    st.metric("Switches", alt_results["transport_changes"],
                              delta=alt_results["transport_changes"]-results["transport_changes"])
                    st.metric("Mobility", alt_results["mobility_score"],
                              delta=round(alt_results["mobility_score"]-results["mobility_score"],1))
                    st.metric("CO₂", alt_results["estimated_co2_reduction"],
                              delta=alt_results["estimated_co2_reduction"]-results["estimated_co2_reduction"])
        else:
            st.caption("Click 'Generate what-if scenarios' to explore alternatives!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("### 📤 Export Results")
    bgt = st.session_state.get("budget_cr", 50)
    cb  = cost_benefit(results, bgt)

    col_pdf, col_ppt = st.columns(2)

    with col_pdf:
        st.markdown("""
        <div class='dt-card'>
          <div class='dt-card-title'>📄 PDF Report</div>
          <div style='color:#94a3b8;font-size:13px;margin-bottom:1rem'>
            Full simulation report with metrics, transport shift, and cost-benefit table.
          </div>
        </div>""", unsafe_allow_html=True)
        pdf_buf = export_pdf_simple(results, cb)
        st.download_button("⬇ Download PDF", pdf_buf,
                           file_name=f"delhi_twin_{results['policy'][:20].replace(' ','_')}.pdf",
                           mime="application/pdf", use_container_width=True)

    with col_ppt:
        st.markdown("""
        <div class='dt-card'>
          <div class='dt-card-title'>📊 PowerPoint Deck</div>
          <div style='color:#94a3b8;font-size:13px;margin-bottom:1rem'>
            5-slide branded presentation: title, metrics, simulation, agent consensus, next steps.
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔧 Generate PPTX", use_container_width=True):
            with st.spinner("Building slides…"):
                pptx_bytes = export_pptx(results, cb)
            if pptx_bytes:
                st.download_button("⬇ Download PPTX", pptx_bytes,
                                   file_name=f"delhi_twin_{results['policy'][:20].replace(' ','_')}.pptx",
                                   mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                   use_container_width=True)
            else:
                st.error("PPTX generation failed — check Node.js is installed.")

    st.markdown("---")
    st.markdown("**Raw JSON export**")
    st.download_button("⬇ Download results.json", json.dumps(results, indent=2),
                       file_name="results.json", mime="application/json")
