import sys
import os
import json
import random
import numpy as np
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =====================================================
# POLICY INPUT
# =====================================================
POLICY = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "Free Metro Rides For Women"
)

CUSTOM_POLICY = None
# Support stacked policies: pass as JSON list ["Policy A", "Policy B"]
ACTIVE_POLICIES = []
try:
    parsed = json.loads(POLICY)
    if isinstance(parsed, dict) and "name" in parsed:
        CUSTOM_POLICY = parsed
        POLICY = parsed["name"]
        ACTIVE_POLICIES = [POLICY]
    elif isinstance(parsed, list):
        ACTIVE_POLICIES = parsed
        POLICY = " + ".join(parsed)
    else:
        ACTIVE_POLICIES = [POLICY]
except Exception:
    ACTIVE_POLICIES = [POLICY]

# =====================================================
# TIME OF DAY SLOTS
# =====================================================
TIME_SLOTS = ["Morning Peak", "Afternoon", "Evening Peak"]

TIME_MODIFIERS = {
    "Morning Peak": {
        "Metro":   {"time": -1, "comfort": -2},
        "Bus":     {"time": -1, "comfort": -2},
        "Auto":    {"time": -2, "comfort":  0},
        "Walking": {"time":  0, "comfort":  0}
    },
    "Afternoon": {
        "Metro":   {"time":  1, "comfort":  1},
        "Bus":     {"time":  1, "comfort":  1},
        "Auto":    {"time":  1, "comfort":  0},
        "Walking": {"time":  0, "comfort":  1}
    },
    "Evening Peak": {
        "Metro":   {"time": -1, "comfort": -2},
        "Bus":     {"time": -2, "comfort": -2},
        "Auto":    {"time": -2, "comfort":  0},
        "Walking": {"time":  0, "comfort":  0}
    }
}

# =====================================================
# BASE TRANSPORT ATTRIBUTES
# =====================================================
BASE_TRANSPORTS = {
    "Metro":   {"cost": 5, "time": 8, "comfort": 7, "safety": 8},
    "Bus":     {"cost": 8, "time": 5, "comfort": 4, "safety": 5},
    "Auto":    {"cost": 3, "time": 9, "comfort": 8, "safety": 6},
    "Walking": {"cost": 10,"time": 2, "comfort": 2, "safety": 7}
}

DELHI_ZONES = {
    "Connaught Place":  {"lat": 28.6315, "lng": 77.2167},
    "Lajpat Nagar":     {"lat": 28.5700, "lng": 77.2433},
    "Dwarka":           {"lat": 28.5921, "lng": 77.0460},
    "Rohini":           {"lat": 28.7041, "lng": 77.1025},
    "Noida Sector 18":  {"lat": 28.5695, "lng": 77.3218},
    "Saket":            {"lat": 28.5244, "lng": 77.2090},
    "Janakpuri":        {"lat": 28.6282, "lng": 77.0822},
    "Nehru Place":      {"lat": 28.5491, "lng": 77.2536},
    "Karol Bagh":       {"lat": 28.6514, "lng": 77.1907},
    "Vasant Kunj":      {"lat": 28.5273, "lng": 77.1571},
    "Gurugram Border":  {"lat": 28.4595, "lng": 77.0266},
    "Shahdara":         {"lat": 28.6692, "lng": 77.2952},
    "Uttam Nagar":      {"lat": 28.6215, "lng": 77.0588},
    "Dilshad Garden":   {"lat": 28.6820, "lng": 77.3180},
    "Chandni Chowk":    {"lat": 28.6505, "lng": 77.2303},
    "Sadar Bazar":      {"lat": 28.6587, "lng": 77.1883},
}

# Archetype -> preferred zones for geographic map accuracy
ARCHETYPE_ZONES = {
    "School Student":       ["Rohini", "Dwarka", "Janakpuri", "Uttam Nagar", "Dilshad Garden", "Shahdara"],
    "Female Student":       ["Rohini", "Dwarka", "Janakpuri", "Uttam Nagar", "Dilshad Garden", "Shahdara"],
    "Female Office Worker": ["Connaught Place", "Nehru Place", "Saket", "Lajpat Nagar", "Gurugram Border"],
    "Male Office Worker":   ["Connaught Place", "Nehru Place", "Noida Sector 18", "Saket", "Vasant Kunj"],
    "Auto Driver":          ["Karol Bagh", "Lajpat Nagar", "Connaught Place", "Nehru Place", "Shahdara"],
    "Shop Owner":           ["Karol Bagh", "Lajpat Nagar", "Sadar Bazar", "Chandni Chowk", "Nehru Place"],
    "Elderly Resident":     ["Lajpat Nagar", "Saket", "Vasant Kunj", "Dwarka", "Rohini"],
    "Delivery Worker":      ["Connaught Place", "Karol Bagh", "Nehru Place", "Noida Sector 18", "Lajpat Nagar"],
}

# =====================================================
# UTILITIES
# =====================================================
def count_transports(citizens):
    display_map = {
        "Auto Rickshaw": "Auto", "Cab": "Auto", "Car": "Auto",
        "Scooter": "Auto", "Bike": "Auto",
    }
    counts = Counter()
    for c in citizens:
        t = c["current_transport"]
        counts[display_map.get(t, t)] += 1
    return dict(counts)

def get_income_bracket(income):
    if income < 10000: return "low"
    elif income < 50000: return "middle"
    else: return "high"

# =====================================================
# POLICY ENGINE — all 12 policies + School Student
# =====================================================
def get_transport_scores(citizen, time_slot="Morning Peak"):
    transports = {k: dict(v) for k, v in BASE_TRANSPORTS.items()}

    # Apply time modifiers
    mods = TIME_MODIFIERS.get(time_slot, {})
    for mode, delta in mods.items():
        if mode in transports:
            for attr, change in delta.items():
                transports[mode][attr] = max(1, min(10, transports[mode][attr] + change))

    ctype = citizen["type"]
    dist  = citizen["commute_distance_km"]

    # ── Custom NLP policy ──────────────────────────────────────────────────
    if CUSTOM_POLICY and "effects" in CUSTOM_POLICY:
        for mode, attrs in CUSTOM_POLICY["effects"].items():
            if mode in transports:
                for attr, val in attrs.items():
                    transports[mode][attr] = val

    # ── Stackable Policies (each block applies independently) ───────────────
    for active_policy in ACTIVE_POLICIES:
        if active_policy == "Free Metro Rides For Women":
            if ctype in ["Female Student", "Female Office Worker", "School Student"]:
                transports["Metro"]["cost"] = 10

        if active_policy == "50% Bus Fare Reduction":
            transports["Bus"]["cost"] = min(10, transports["Bus"]["cost"] + 2)
            if ctype == "School Student":
                transports["Bus"]["safety"] = min(10, transports["Bus"]["safety"] + 1)

        if active_policy == "Congestion Tax":
            transports["Auto"]["cost"] = max(1, transports["Auto"]["cost"] - 2)

        if active_policy == "New Metro Line":
            transports["Metro"]["time"] = min(10, transports["Metro"]["time"] + 2)

        if active_policy == "Metro Operating Hours Extended to 2 AM":
            transports["Metro"]["safety"]  = min(10, transports["Metro"]["safety"] + 2)
            transports["Metro"]["comfort"] = min(10, transports["Metro"]["comfort"] + 1)
            transports["Auto"]["cost"]     = max(1,  transports["Auto"]["cost"] - 2)

        if active_policy == "Airport Express Fare Reduction":
            if dist >= 15:
                transports["Metro"]["cost"] = min(10, transports["Metro"]["cost"] + 3)
                transports["Metro"]["time"] = min(10, transports["Metro"]["time"] + 2)

        if active_policy == "Reserved Student Coaches":
            if ctype in ["Female Student", "School Student"]:
                transports["Metro"]["comfort"] = 10
                transports["Metro"]["safety"]  = 10
                transports["Bus"]["comfort"]   = min(10, transports["Bus"]["comfort"] + 2)
                transports["Bus"]["safety"]    = min(10, transports["Bus"]["safety"] + 2)

        if active_policy == "Personal Carbon Budget":
            transports["Metro"]["cost"] = min(10, transports["Metro"]["cost"] + 2)
            transports["Bus"]["cost"]   = min(10, transports["Bus"]["cost"] + 2)
            transports["Auto"]["cost"]  = max(1,  transports["Auto"]["cost"] - 3)

        if active_policy == "Free Transit Birthdays":
            if random.random() < (1/365 * 100):
                transports["Metro"]["cost"] = 10
                transports["Bus"]["cost"]   = 10

        if active_policy == "Car-Free School Zones":
            if ctype in ["Female Student", "School Student"]:
                transports["Walking"]["comfort"] = min(10, transports["Walking"]["comfort"] + 4)
                transports["Walking"]["safety"]  = min(10, transports["Walking"]["safety"] + 3)
                transports["Bus"]["safety"]      = min(10, transports["Bus"]["safety"] + 2)
            if ctype == "School Student":
                transports["Bus"]["cost"]        = min(10, transports["Bus"]["cost"] + 2)
                transports["Walking"]["comfort"] = min(10, transports["Walking"]["comfort"] + 1)

        if active_policy == "One-Ticket City":
            transports["Metro"]["time"]    = min(10, transports["Metro"]["time"] + 2)
            transports["Bus"]["time"]      = min(10, transports["Bus"]["time"] + 2)
            transports["Metro"]["comfort"] = min(10, transports["Metro"]["comfort"] + 1)
            transports["Bus"]["comfort"]   = min(10, transports["Bus"]["comfort"] + 1)

        if active_policy == "Free EV Parking":
            if dist <= 5:
                transports["Walking"]["comfort"] = min(10, transports["Walking"]["comfort"] + 2)
                transports["Metro"]["cost"]      = min(10, transports["Metro"]["cost"] + 1)

    return transports

# =====================================================
# AGENT DECISION ENGINE
# =====================================================
def choose_best_transport(citizen, time_slot="Morning Peak"):
    options  = get_transport_scores(citizen, time_slot)
    distance = citizen["commute_distance_km"]
    ctype    = citizen["type"]
    best     = None
    best_score = -999999

    for mode, v in options.items():
        score = (
            citizen["budget_sensitivity"]  * v["cost"] +
            citizen["time_sensitivity"]    * v["time"] +
            citizen["comfort_sensitivity"] * v["comfort"] +
            citizen["safety_sensitivity"]  * v["safety"]
        )

        if mode == "Walking":
            # School students: strong walking bonus for very short school distances
            if ctype == "School Student" and distance <= 3:
                score += 50
            elif distance <= 2:
                score += 40
            elif distance <= 5:
                score += 10
            else:
                score -= 100
        elif mode == "Metro":
            if distance >= 5:  score += 15
            if distance >= 10: score += 25
        elif mode == "Bus":
            if distance >= 3:  score += 10
            if distance >= 8:  score += 15
            # School students: bus preferred over auto for safety
            if ctype == "School Student": score += 8
        elif mode == "Auto":
            if distance >= 3:  score += 10
            if distance >= 8:  score += 5
            # School students: auto discouraged (safety, cost)
            if ctype == "School Student": score -= 15

        score = score / 10
        if score > best_score:
            best_score = score
            best = mode

    return best

# =====================================================
# CORE SIMULATION
# =====================================================
def run_once(citizens_input, time_slot="Morning Peak"):
    import copy
    citizens = copy.deepcopy(citizens_input)
    before   = count_transports(citizens)
    switches = 0
    co2_reduction = 0

    for c in citizens:
        old = c["current_transport"]
        # Normalise old transport for comparison
        _old_display = {"Auto Rickshaw":"Auto","Cab":"Auto","Car":"Auto","Scooter":"Auto","Bike":"Auto"}.get(old, old)
        new = choose_best_transport(c, time_slot)
        if _old_display != new:
            switches += 1
            if _old_display == "Auto"   and new == "Metro": co2_reduction += 5
            elif _old_display == "Auto" and new == "Bus":   co2_reduction += 3
            elif _old_display == "Bus"  and new == "Metro": co2_reduction += 2
        c["current_transport"] = new

    after = count_transports(citizens)
    return dict(before), dict(after), switches, co2_reduction, citizens

# =====================================================
# CONFIDENCE INTERVALS
# =====================================================
def run_with_confidence(citizens_base, time_slot="Morning Peak", n=5):
    import copy
    mobility_scores, co2_scores, switch_counts = [], [], []
    for _ in range(n):
        citizens = copy.deepcopy(citizens_base)
        for c in citizens:
            for key in ["budget_sensitivity","time_sensitivity","comfort_sensitivity","safety_sensitivity"]:
                if key in c:
                    c[key] = max(1, min(10, c[key] + random.randint(-1, 1)))
        before, after, sw, co2, _ = run_once(citizens, time_slot)
        private_before = sum(before.get(m,0) for m in ["Auto"])
        private_after  = sum(after.get(m,0)  for m in ["Auto"])
        transit_before = before.get("Metro",0) + before.get("Bus",0)
        transit_after  = after.get("Metro",0)  + after.get("Bus",0)
        mob = (max(0,(private_before-private_after)*0.5) +
               max(0,(transit_after-transit_before)*0.4) +
               max(0,sw*0.25) + max(0,co2*0.5))
        mobility_scores.append(mob)
        co2_scores.append(co2)
        switch_counts.append(sw)

    def ci(vals):
        arr = np.array(vals)
        return round(float(arr.mean()),1), round(float(arr.std()),1), int(arr.min()), int(arr.max())

    return {"mobility": ci(mobility_scores), "co2": ci(co2_scores), "switches": ci(switch_counts)}

# =====================================================
# MOBILITY BREAKDOWN
# =====================================================
def compute_mobility_breakdown(switches, co2, after, before):
    private_before = before.get("Auto", 0)
    private_after  = after.get("Auto", 0)
    transit_before = before.get("Metro",0) + before.get("Bus",0)
    transit_after  = after.get("Metro",0)  + after.get("Bus",0)
    congestion = max(0, int((private_before - private_after) * 0.5))
    transit    = max(0, int((transit_after - transit_before) * 0.4))
    cost_sav   = max(0, int(switches * 0.25))
    co2_pts    = max(0, int(co2 * 0.5))
    total = congestion + transit + cost_sav + co2_pts
    return {
        "total": total,
        "reduced_congestion":    congestion,
        "public_transit_adoption": transit,
        "cost_savings":          cost_sav,
        "co2_reduction":         co2_pts,
    }

# =====================================================
# EQUITY
# =====================================================
def compute_equity(citizens_before, citizens_after):
    brackets = {
        "low":    {"before_pub":0,"after_pub":0,"total":0},
        "middle": {"before_pub":0,"after_pub":0,"total":0},
        "high":   {"before_pub":0,"after_pub":0,"total":0},
    }
    public_modes = {"Metro","Bus"}
    display_map  = {"Auto Rickshaw":"Auto","Cab":"Auto","Car":"Auto","Scooter":"Auto","Bike":"Auto"}

    for cb, ca in zip(citizens_before, citizens_after):
        br = get_income_bracket(cb["monthly_income"])
        brackets[br]["total"] += 1
        if display_map.get(cb["current_transport"], cb["current_transport"]) in public_modes:
            brackets[br]["before_pub"] += 1
        if ca["current_transport"] in public_modes:
            brackets[br]["after_pub"] += 1

    result = {}
    for br, d in brackets.items():
        total = max(d["total"], 1)
        before_pct = round(d["before_pub"] / total * 100, 1)
        after_pct  = round(d["after_pub"]  / total * 100, 1)
        result[br] = {
            "before_pct": before_pct,
            "after_pct":  after_pct,
            "gain":       round(after_pct - before_pct, 1),
            "total":      d["total"],
        }

    low_gain    = result["low"]["gain"]
    mid_gain    = result["middle"]["gain"]
    high_gain   = result["high"]["gain"]
    # Equity index: reward absolute gains for low-income, penalise if high-income gains >> low-income
    # Base = how much low-income gained (0-50 → 0-50 points)
    # Gap adjustment: if high gains much more than low, subtract proportionally
    abs_gain_score = min(50, max(0, low_gain))               # up to 50 pts for low-income gain
    gap_penalty    = max(0, (high_gain - low_gain) * 1.5)    # penalty only when high >> low
    equity_index   = max(0, min(100, round(50 + abs_gain_score - gap_penalty, 1)))
    return {"brackets": result, "equity_index": equity_index}

# =====================================================
# TIME OF DAY
# =====================================================
def run_time_of_day(citizens_base):
    import copy
    results = {}
    for slot in TIME_SLOTS:
        before, after, sw, co2, _ = run_once(copy.deepcopy(citizens_base), slot)
        total = max(sum(after.values()), 1)
        results[slot] = {
            "switches":       sw,
            "co2":            co2,
            "transport_after": dict(after),
            "metro_share":    round(after.get("Metro",0) / total * 100, 1),
        }
    return results

# =====================================================
# SENTIMENT (all 12 policies + School Student references)
# =====================================================
POLICY_SENTIMENT = {
    "Free Metro Rides For Women": {
        "benefits": ["Free metro access for female commuters and school students",
                     "Improved gender equity in transit", "Higher safety for women and children"],
        "complaints": ["Peak-hour crowding on metro", "Limited coverage in outer districts"],
    },
    "50% Bus Fare Reduction": {
        "benefits": ["Affordable bus travel for daily commuters", "Relief for low-income households",
                     "Cheaper school commute for children"],
        "complaints": ["Bus overcrowding at key stops", "Strain on DMRC bus budget"],
    },
    "Congestion Tax": {
        "benefits": ["Reduced road congestion city-wide", "Cleaner air in central Delhi"],
        "complaints": ["Higher auto fares for short trips", "Burden on gig economy workers"],
    },
    "New Metro Line": {
        "benefits": ["Faster commute on new metro corridor", "Less dependency on private vehicles"],
        "complaints": ["Construction disruption near new line", "Last-mile connectivity gaps"],
    },
    "Metro Operating Hours Extended to 2 AM": {
        "benefits": ["Safe late-night travel option", "Boost for Delhi's night economy"],
        "complaints": ["Higher operational cost for DMRC", "Low ridership after midnight"],
    },
    "Airport Express Fare Reduction": {
        "benefits": ["Cheaper airport access for all income groups", "Reduced cab bookings to airport"],
        "complaints": ["Revenue loss for airport express operator", "Crowding at terminal stations"],
    },
    "Reserved Student Coaches": {
        "benefits": ["Safe dedicated coaches for school children and college students",
                     "Higher metro and bus adoption among youth",
                     "Reduced harassment incidents for young commuters"],
        "complaints": ["Reduced capacity for other passengers", "Difficult to enforce at all stations"],
    },
    "Personal Carbon Budget": {
        "benefits": ["Incentivises shift to public transport", "Measurable CO₂ accountability"],
        "complaints": ["Complex to implement and monitor", "Penalises citizens with no alternatives"],
    },
    "Free Transit Birthdays": {
        "benefits": ["Fun policy — boosts public goodwill", "Encourages first-time metro users"],
        "complaints": ["Difficult to verify without ID checks", "Negligible impact on daily ridership"],
    },
    "Car-Free School Zones": {
        "benefits": ["Safe walking routes for school children", "Reduced school-run traffic",
                     "Cleaner air around schools"],
        "complaints": ["Inconvenience for parents with long commutes", "Enforcement challenges"],
    },
    "One-Ticket City": {
        "benefits": ["Seamless metro-bus transfers", "Encourages multi-modal commuting"],
        "complaints": ["High integration cost across agencies", "Technical glitches during rollout"],
    },
    "Free EV Parking": {
        "benefits": ["Incentivises EV adoption", "Reduces parking congestion near transit hubs"],
        "complaints": ["Benefits mainly car-owning households", "Limited impact on public transit use"],
    },
}

def compute_sentiment(switches, co2, after, before, policy):
    metro_growth = after.get("Metro",0) - before.get("Metro",0)
    base = 60
    if switches > 150: base += 20
    elif switches > 75: base += 10
    if co2 > 20: base += 10
    elif co2 > 10: base += 5
    base = min(100, base + random.randint(-3,3))

    ps = POLICY_SENTIMENT.get(policy, {
        "benefits":   ["Improved urban mobility overall"],
        "complaints": ["Adjustment period for new policy"],
    })
    benefits   = ps["benefits"][:]
    complaints = ps["complaints"][:]
    if metro_growth > 100:
        if "Metro overcrowding during peak hours" not in complaints:
            complaints.insert(0, "Metro overcrowding during peak hours")
    return {"score": base, "top_complaints": complaints[:3], "top_benefits": benefits[:3]}

# =====================================================
# MAP DATA — geographic, archetype-based
# =====================================================
def generate_map_data(citizens):
    color_map = {"Metro":"#22c55e","Bus":"#3b82f6","Auto":"#f59e0b","Walking":"#8b5cf6"}
    display_map = {"Auto Rickshaw":"Auto","Cab":"Auto","Car":"Auto","Scooter":"Auto","Bike":"Auto"}
    points = []

    for c in citizens:
        # Use home_zone if available, else fall back to archetype-preferred zone
        zone_name = c.get("home_zone")
        if not zone_name or zone_name not in DELHI_ZONES:
            preferred = ARCHETYPE_ZONES.get(c["type"], list(DELHI_ZONES.keys()))
            zone_name = random.choice(preferred)

        zone = DELHI_ZONES[zone_name]
        # Scatter radius based on distance: further commuters live further from center
        scatter = min(0.025, c["commute_distance_km"] / 1000)
        t = c["current_transport"]
        display = display_map.get(t, t)

        points.append({
            "id":        c["id"],
            "type":      c["type"],
            "zone":      zone_name,
            "lat":       zone["lat"] + random.uniform(-scatter, scatter),
            "lng":       zone["lng"] + random.uniform(-scatter, scatter),
            "transport": display,
            "color":     color_map.get(display, "#6b7280"),
            "income":    c["monthly_income"],
            "age":       c.get("age", 30),
        })
    return points

# =====================================================
# CHARTS
# =====================================================
def create_transport_chart(before, after):
    modes = sorted(set(before.keys()) | set(after.keys()))
    bv = [before.get(m,0) for m in modes]
    av = [after.get(m,0)  for m in modes]
    x  = np.arange(len(modes))

    fig, ax = plt.subplots(figsize=(10,6))
    fig.patch.set_alpha(0); ax.set_facecolor("none")
    ax.bar(x-0.2, bv, 0.4, label="Before", color="#3b82f6", alpha=0.9)
    bars = ax.bar(x+0.2, av, 0.4, label="After", color="#f97316", alpha=0.9)
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x()+bar.get_width()/2, h+0.3, str(int(h)),
                    ha="center", va="bottom", color="#f97316", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(modes, rotation=15, ha="right")
    ax.set_ylabel("Citizens")
    ax.set_title(f"Transport Impact — {POLICY}", pad=10)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["bottom","left"]: ax.spines[s].set_color("#94a3b8")
    ax.legend()
    plt.tight_layout()
    plt.savefig("transport_impact.png", dpi=100, transparent=True)
    plt.close()

def create_co2_chart(co2):
    fig, ax = plt.subplots(figsize=(6,4))
    fig.patch.set_alpha(0); ax.set_facecolor("none")
    color = "#22c55e" if co2>20 else "#f59e0b" if co2>10 else "#ef4444"
    ax.bar(["CO2 Reduction"], [co2], color=color, width=0.4)
    ax.text(0, co2+0.3, str(co2), ha="center", va="bottom",
            color=color, fontsize=14, fontweight="bold")
    ax.set_ylabel("Score"); ax.set_title(f"CO2 Impact — {POLICY}", pad=10)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["bottom","left"]: ax.spines[s].set_color("#94a3b8")
    plt.tight_layout()
    plt.savefig("co2_impact.png", dpi=100, transparent=True)
    plt.close()

# =====================================================
# FALLBACK AGENT TEXT
# =====================================================
def government_agent_text(r):
    before = r["transport_before"].get("Metro",0)
    after  = r["transport_after"].get("Metro",0)
    increase = after - before
    decision = "APPROVE" if increase > 30 else "REVIEW"
    return (f"Recommendation: {decision}\nPolicy: {r['policy']}\n"
            f"Metro Growth: {increase} users\nCO2 Score: {r['estimated_co2_reduction']}")

def transport_agent_text(r):
    mg = r["transport_after"].get("Metro",0) - r["transport_before"].get("Metro",0)
    bc = r["transport_after"].get("Bus",0)   - r["transport_before"].get("Bus",0)
    return (f"Total Mode Switches: {r['transport_changes']}\n"
            f"Metro demand: +{mg}\nBus demand: {bc:+d}")

def environment_agent_text(r):
    co2 = r["estimated_co2_reduction"]
    level = "High" if co2>50 else "Medium" if co2>20 else "Low"
    return f"Environmental Impact: {level}\nCO2 Score: {co2}"

def citizen_agent_text(r):
    s = r.get("citizen_sentiment",{})
    return (f"{r['transport_changes']} citizens changed behavior.\n"
            f"Satisfaction: {s.get('score','N/A')}/100")

def business_agent_text(r):
    ma = r["transport_after"].get("Metro",0)
    mb = r["transport_before"].get("Metro",0)
    return (f"Metro Users After: {ma} (new: {ma-mb})\n"
            f"Footfall uplift near metro: +{(ma-mb)*2} persons/day")

# =====================================================
# MAIN
# =====================================================
app_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "."
citizens_path = os.path.join(app_dir, "enhanced_citizens.json")

import os
with open(citizens_path, "r") as f:
    citizens_base = json.load(f)

import copy
import os
before, after, switches, co2, citizens_updated = run_once(citizens_base, "Morning Peak")
breakdown = compute_mobility_breakdown(switches, co2, after, before)
city_score = breakdown["total"]
ci_data    = run_with_confidence(citizens_base, "Morning Peak", n=5)
equity     = compute_equity(citizens_base, citizens_updated)
tod        = run_time_of_day(citizens_base)
sentiment  = compute_sentiment(switches, co2, after, before, POLICY)
map_data   = generate_map_data(citizens_updated)

results = {
    "policy":             POLICY,
    "city_score":         city_score,
    "mobility_score":     city_score,
    "mobility_breakdown": breakdown,
    "confidence_intervals": ci_data,
    "equity":             equity,
    "time_of_day":        tod,
    "citizen_sentiment":  sentiment,
    "citizens_simulated": len(citizens_base),
    "transport_changes":  switches,
    "estimated_co2_reduction": co2,
    "transport_before":   before,
    "transport_after":    after,
    "government_report":  government_agent_text({"policy":POLICY,"transport_before":before,"transport_after":after,"estimated_co2_reduction":co2,"transport_changes":switches}),
    "transport_report":   transport_agent_text({"transport_before":before,"transport_after":after,"transport_changes":switches}),
    "environment_report": environment_agent_text({"estimated_co2_reduction":co2,"transport_before":before,"transport_after":after}),
    "citizen_report":     citizen_agent_text({"transport_changes":switches,"citizen_sentiment":sentiment}),
    "business_report":    business_agent_text({"transport_before":before,"transport_after":after}),
}

results_path     = os.path.join(app_dir, "results.json")
map_data_path    = os.path.join(app_dir, "map_data.json")
citizens_out     = os.path.join(app_dir, "updated_citizens.json")

with open(citizens_out, "w")  as f: json.dump(citizens_updated, f, indent=2)
with open(results_path, "w")  as f: json.dump(results, f, indent=2)
with open(map_data_path, "w") as f: json.dump(map_data, f, indent=2)

create_transport_chart(before, after)
create_co2_chart(co2)

print(f"\nSIMULATION COMPLETE — {POLICY}")
print(f"Citizens: {len(citizens_base)} | Archetypes: 8")
print(f"Mobility: {city_score} [{ci_data['mobility'][2]}–{ci_data['mobility'][3]}]")
print(f"CO2: {co2} | Switches: {switches}")
print(f"Equity: {equity['equity_index']}/100 | Satisfaction: {sentiment['score']}/100")
