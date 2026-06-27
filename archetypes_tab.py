"""
archetypes_tab.py
Renders the full Archetypes deep-dive tab in Delhi Digital Twin.
Import and call render_archetypes_tab(results, citizens_before, citizens_after)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

# ── Archetype metadata ────────────────────────────────────────────────────────
ARCHETYPE_META = {
    "School Student": {
        "emoji": "🎒",
        "color": "#f472b6",
        "desc": "Ages 10–17. Dependent on parents for fares. Walks short distances, takes bus for longer routes. Safety and zero cost are top priorities.",
        "sensitivities": {"Budget": 9.5, "Safety": 9.0, "Comfort": 4.5, "Time": 4.5},
        "policy_sensitivity": ["Car-Free School Zones", "Reserved Student Coaches", "50% Bus Fare Reduction"],
    },
    "Female Student": {
        "emoji": "📚",
        "color": "#a78bfa",
        "desc": "Ages 17–24. College-going women with minimal income. Prefer metro for safety, highly budget-constrained, commute 2–20 km.",
        "sensitivities": {"Budget": 9.0, "Safety": 8.5, "Time": 5.5, "Comfort": 3.5},
        "policy_sensitivity": ["Free Metro Rides For Women", "Reserved Student Coaches", "50% Bus Fare Reduction"],
    },
    "Female Office Worker": {
        "emoji": "💼",
        "color": "#60a5fa",
        "desc": "Ages 23–40. Professional women prioritising speed and safety. Longest commutes (8–28 km), willing to pay for comfort.",
        "sensitivities": {"Time": 9.0, "Safety": 8.5, "Comfort": 7.5, "Budget": 6.0},
        "policy_sensitivity": ["Free Metro Rides For Women", "One-Ticket City", "New Metro Line"],
    },
    "Male Office Worker": {
        "emoji": "🧑‍💻",
        "color": "#34d399",
        "desc": "Ages 23–42. Time-driven commuters. Mix of metro, bike and car. Moderate safety concern, commute 8–30 km.",
        "sensitivities": {"Time": 8.5, "Comfort": 7.5, "Budget": 6.0, "Safety": 6.0},
        "policy_sensitivity": ["New Metro Line", "Congestion Tax", "One-Ticket City"],
    },
    "Auto Driver": {
        "emoji": "🛺",
        "color": "#fbbf24",
        "desc": "Ages 28–55. Income-maximisers who drive 30–70 km daily. Negatively affected by congestion tax. Rarely switch to public transit.",
        "sensitivities": {"Time": 8.0, "Budget": 5.0, "Safety": 5.5, "Comfort": 4.0},
        "policy_sensitivity": ["Congestion Tax", "Free EV Parking", "Personal Carbon Budget"],
    },
    "Shop Owner": {
        "emoji": "🏪",
        "color": "#f97316",
        "desc": "Ages 28–55. Short commuters (2–12 km) who balance cost and time. High income variability. Prefer bike or car for flexibility.",
        "sensitivities": {"Budget": 7.5, "Time": 6.0, "Comfort": 6.5, "Safety": 6.5},
        "policy_sensitivity": ["Car-Free School Zones", "Congestion Tax", "One-Ticket City"],
    },
    "Elderly Resident": {
        "emoji": "👴",
        "color": "#94a3b8",
        "desc": "Ages 60–80. Comfort and safety trump everything. Short trips (1–8 km). Prefer bus or walking. Fixed income, very price sensitive.",
        "sensitivities": {"Safety": 9.0, "Comfort": 8.5, "Budget": 8.5, "Time": 3.5},
        "policy_sensitivity": ["50% Bus Fare Reduction", "Free Transit Birthdays", "One-Ticket City"],
    },
    "Delivery Worker": {
        "emoji": "📦",
        "color": "#ef4444",
        "desc": "Ages 20–38. Gig economy riders covering 15–60 km daily on bike or scooter. Speed obsessed, low income, minimal safety concern.",
        "sensitivities": {"Time": 9.0, "Budget": 7.5, "Comfort": 3.5, "Safety": 4.5},
        "policy_sensitivity": ["Free EV Parking", "Personal Carbon Budget", "Congestion Tax"],
    },
}

TRANSPORT_DISPLAY_MAP = {
    "Auto Rickshaw": "Auto", "Cab": "Auto", "Car": "Auto",
    "Scooter": "Auto", "Bike": "Auto",
    "Walking": "Walking", "Bus": "Bus", "Metro": "Metro",
}

TRANSPORT_COLORS = {
    "Metro": "#22c55e", "Bus": "#3b82f6", "Auto": "#f59e0b", "Walking": "#8b5cf6"
}


def _normalize_transport(t):
    return TRANSPORT_DISPLAY_MAP.get(t, "Auto")


def _dark_fig(w=9, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color("#475569")
    ax.tick_params(colors="#94a3b8", labelsize=9)
    ax.yaxis.label.set_color("#94a3b8")
    ax.xaxis.label.set_color("#94a3b8")
    ax.title.set_color("#f8fafc")
    return fig, ax


def compute_archetype_breakdown(citizens_before, citizens_after):
    """
    Returns dict: archetype -> {
        before: {Metro:N, Bus:N, Auto:N, Walking:N},
        after:  {Metro:N, Bus:N, Auto:N, Walking:N},
        switches: N,
        total: N,
        switch_pct: float,
        pub_transit_gain: float  (% using public transit after - before)
    }
    """
    data = {}
    for cb, ca in zip(citizens_before, citizens_after):
        atype = cb["type"]
        if atype not in data:
            data[atype] = {
                "before": {"Metro": 0, "Bus": 0, "Auto": 0, "Walking": 0},
                "after":  {"Metro": 0, "Bus": 0, "Auto": 0, "Walking": 0},
                "switches": 0,
                "total": 0,
            }
        d = data[atype]
        d["total"] += 1
        tb = _normalize_transport(cb["current_transport"])
        ta = _normalize_transport(ca["current_transport"])
        d["before"][tb] = d["before"].get(tb, 0) + 1
        d["after"][ta]  = d["after"].get(ta, 0) + 1
        if tb != ta:
            d["switches"] += 1

    for atype, d in data.items():
        total = max(d["total"], 1)
        d["switch_pct"] = round(d["switches"] / total * 100, 1)
        pub_before = (d["before"].get("Metro", 0) + d["before"].get("Bus", 0)) / total * 100
        pub_after  = (d["after"].get("Metro", 0)  + d["after"].get("Bus", 0))  / total * 100
        d["pub_transit_gain"] = round(pub_after - pub_before, 1)

    return data


def _plot_archetype_transport(breakdown, policy_name):
    """Grouped bar: before/after public transit % per archetype."""
    archetypes = [a for a in ARCHETYPE_META if a in breakdown]
    before_pub = []
    after_pub  = []
    for a in archetypes:
        d = breakdown[a]
        total = max(d["total"], 1)
        before_pub.append(round((d["before"].get("Metro", 0) + d["before"].get("Bus", 0)) / total * 100, 1))
        after_pub.append( round((d["after"].get("Metro", 0)  + d["after"].get("Bus", 0))  / total * 100, 1))

    short_labels = [ARCHETYPE_META[a]["emoji"] + " " + a.split()[0] for a in archetypes]
    x = np.arange(len(archetypes))
    w = 0.35

    fig, ax = _dark_fig(10, 4)
    bars_b = ax.bar(x - w/2, before_pub, w, label="Before", color="#475569", alpha=0.8)
    bars_a = ax.bar(x + w/2, after_pub,  w, label="After",  color="#22c55e", alpha=0.9)

    for bar, val in zip(bars_a, after_pub):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                    f"{val:.0f}%", ha="center", va="bottom", color="#22c55e", fontsize=8, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("% Using Public Transit")
    ax.set_title(f"Public Transit Adoption by Archetype — {policy_name[:35]}")
    ax.legend(facecolor="#1e293b", labelcolor="#f8fafc", edgecolor="#334155", fontsize=9)
    ax.set_ylim(0, max(max(after_pub, default=0), max(before_pub, default=0)) + 15)
    plt.tight_layout()
    return fig


def _plot_sensitivity_radar(archetype_name):
    """Radar/spider chart of an archetype's sensitivity profile."""
    meta = ARCHETYPE_META.get(archetype_name, {})
    sens = meta.get("sensitivities", {})
    labels = list(sens.keys())
    values = list(sens.values())
    values += values[:1]

    N = len(labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"polar": True})
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.spines["polar"].set_color("#334155")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=10, color="#f8fafc")
    ax.set_yticklabels([])
    ax.set_ylim(0, 10)

    color = meta.get("color", "#22c55e")
    ax.plot(angles, values, color=color, linewidth=2)
    ax.fill(angles, values, color=color, alpha=0.25)

    # Gridlines
    for r in [2, 4, 6, 8, 10]:
        ax.plot(angles, [r] * (N + 1), color="#334155", linewidth=0.5, linestyle="--")

    plt.tight_layout()
    return fig


def _plot_archetype_mode_split(breakdown, archetype_name):
    """Donut / bar showing mode split before vs after for one archetype."""
    d = breakdown.get(archetype_name, {})
    if not d:
        return None

    modes = ["Metro", "Bus", "Auto", "Walking"]
    before_vals = [d["before"].get(m, 0) for m in modes]
    after_vals  = [d["after"].get(m, 0)  for m in modes]
    colors_list = [TRANSPORT_COLORS[m] for m in modes]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_alpha(0)
    for ax in [ax1, ax2]:
        ax.set_facecolor("none")

    for ax, vals, title in [(ax1, before_vals, "Before"), (ax2, after_vals, "After")]:
        non_zero = [(m, v, c) for m, v, c in zip(modes, vals, colors_list) if v > 0]
        if non_zero:
            labels_nz, vals_nz, colors_nz = zip(*non_zero)
            wedges, texts, autotexts = ax.pie(
                vals_nz, labels=labels_nz, colors=colors_nz,
                autopct="%1.0f%%", startangle=90,
                textprops={"color": "#f8fafc", "fontsize": 9},
                wedgeprops={"linewidth": 1, "edgecolor": "#0f172a"}
            )
            for at in autotexts:
                at.set_color("#0f172a")
                at.set_fontweight("bold")
        ax.set_title(title, color="#f8fafc", fontsize=11)

    plt.suptitle(f"{archetype_name} — Mode Split", color="#f8fafc", fontsize=12, y=1.02)
    plt.tight_layout()
    return fig


def _policy_impact_ranking(breakdown, policy_name):
    """Return archetypes sorted by absolute public transit gain — most benefited first."""
    ranked = []
    for atype, d in breakdown.items():
        gain = d.get("pub_transit_gain", 0)
        switches = d["switches"]
        total = d["total"]
        ranked.append({
            "archetype": atype,
            "gain": gain,
            "switches": switches,
            "total": total,
            "switch_pct": d["switch_pct"],
        })
    ranked.sort(key=lambda x: x["gain"], reverse=True)
    return ranked


# ── Main render function ───────────────────────────────────────────────────────
def render_archetypes_tab(results, citizens_before, citizens_after):
    """Call this inside a Streamlit tab to render the full archetype deep-dive."""

    policy_name = results.get("policy", "Unknown Policy")
    breakdown = compute_archetype_breakdown(citizens_before, citizens_after)
    ranked = _policy_impact_ranking(breakdown, policy_name)

    st.markdown("### 🧩 Archetype Overview")
    st.caption(f"How each of the 8 citizen archetypes responded to **{policy_name}**")

    # ── Impact ranking cards ──────────────────────────────────────────────────
    st.markdown("#### 🏆 Policy Impact by Archetype")
    cols = st.columns(4)
    for i, row in enumerate(ranked[:4]):
        meta = ARCHETYPE_META.get(row["archetype"], {})
        gain = row["gain"]
        color = "#22c55e" if gain > 5 else "#f59e0b" if gain > 0 else "#ef4444"
        sign = "+" if gain >= 0 else ""
        with cols[i]:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;border-radius:10px;
                        padding:14px;text-align:center;">
              <div style="font-size:22px">{meta.get("emoji","")}</div>
              <div style="color:#f8fafc;font-size:12px;font-weight:600;margin:4px 0">
                {row["archetype"]}</div>
              <div style="color:{color};font-size:20px;font-weight:700">
                {sign}{gain:.1f}%</div>
              <div style="color:#94a3b8;font-size:11px">transit gain</div>
              <div style="color:#94a3b8;font-size:11px">{row["switches"]}/{row["total"]} switched</div>
            </div>""", unsafe_allow_html=True)

    cols2 = st.columns(4)
    for i, row in enumerate(ranked[4:]):
        meta = ARCHETYPE_META.get(row["archetype"], {})
        gain = row["gain"]
        color = "#22c55e" if gain > 5 else "#f59e0b" if gain > 0 else "#ef4444"
        sign = "+" if gain >= 0 else ""
        with cols2[i]:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;border-radius:10px;
                        padding:14px;text-align:center;">
              <div style="font-size:22px">{meta.get("emoji","")}</div>
              <div style="color:#f8fafc;font-size:12px;font-weight:600;margin:4px 0">
                {row["archetype"]}</div>
              <div style="color:{color};font-size:20px;font-weight:700">
                {sign}{gain:.1f}%</div>
              <div style="color:#94a3b8;font-size:11px">transit gain</div>
              <div style="color:#94a3b8;font-size:11px">{row["switches"]}/{row["total"]} switched</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Grouped bar: public transit adoption ─────────────────────────────────
    st.markdown("#### 📊 Public Transit Adoption — Before vs After")
    fig = _plot_archetype_transport(breakdown, policy_name)
    st.pyplot(fig)
    plt.close(fig)

    st.divider()

    # ── Per-archetype deep dive ───────────────────────────────────────────────
    st.markdown("#### 🔍 Per-Archetype Deep Dive")
    archetypes_present = [a for a in ARCHETYPE_META if a in breakdown]
    selected = st.selectbox("Select archetype to explore", archetypes_present,
                            format_func=lambda a: f"{ARCHETYPE_META[a]['emoji']} {a}")

    if selected:
        meta = ARCHETYPE_META[selected]
        d = breakdown[selected]

        col_desc, col_radar = st.columns([2, 1])
        with col_desc:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px">
              <div style="font-size:28px;margin-bottom:8px">{meta["emoji"]} {selected}</div>
              <div style="color:#94a3b8;line-height:1.7;font-size:14px">{meta["desc"]}</div>
              <div style="margin-top:14px">
                <span style="color:#64748b;font-size:12px;text-transform:uppercase;
                             letter-spacing:1px">Most impacted by</span><br>
                {"".join(f'<span style="background:#1e3a5f;color:#60a5fa;padding:3px 8px;'
                         f'border-radius:4px;font-size:12px;margin:3px 2px;display:inline-block">'
                         f'{p}</span>' for p in meta["policy_sensitivity"])}
              </div>
            </div>""", unsafe_allow_html=True)

        with col_radar:
            st.markdown("**Sensitivity Profile**")
            fig_r = _plot_sensitivity_radar(selected)
            st.pyplot(fig_r)
            plt.close(fig_r)

        st.markdown("<br>", unsafe_allow_html=True)

        # Mode split before/after
        col_split, col_stats = st.columns([2, 1])
        with col_split:
            st.markdown("**Mode Split Before → After**")
            fig_m = _plot_archetype_mode_split(breakdown, selected)
            if fig_m:
                st.pyplot(fig_m)
                plt.close(fig_m)

        with col_stats:
            gain = d["pub_transit_gain"]
            color = "#22c55e" if gain > 5 else "#f59e0b" if gain > 0 else "#ef4444"
            sign = "+" if gain >= 0 else ""
            st.markdown("**Policy Response**")
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;gap:10px;margin-top:8px">
              <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;
                          padding:14px;text-align:center">
                <div style="color:#94a3b8;font-size:11px">Citizens</div>
                <div style="color:#f8fafc;font-size:22px;font-weight:700">{d["total"]}</div>
              </div>
              <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;
                          padding:14px;text-align:center">
                <div style="color:#94a3b8;font-size:11px">Mode Switches</div>
                <div style="color:#f97316;font-size:22px;font-weight:700">{d["switches"]}</div>
                <div style="color:#94a3b8;font-size:11px">({d["switch_pct"]}%)</div>
              </div>
              <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;
                          padding:14px;text-align:center">
                <div style="color:#94a3b8;font-size:11px">Transit Gain</div>
                <div style="color:{color};font-size:22px;font-weight:700">{sign}{gain}%</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown("#### 📋 Full Archetype Summary Table")
    rows = []
    for a in ARCHETYPE_META:
        if a not in breakdown:
            continue
        d = breakdown[a]
        meta = ARCHETYPE_META[a]
        gain = d["pub_transit_gain"]
        verdict = "✅ Benefits" if gain > 5 else "⚠️ Moderate" if gain > 0 else "❌ Minimal"
        rows.append({
            "Archetype": f"{meta['emoji']} {a}",
            "Count": d["total"],
            "Switches": d["switches"],
            "Switch %": f"{d['switch_pct']}%",
            "Transit Gain": f"+{gain}%" if gain >= 0 else f"{gain}%",
            "Policy Verdict": verdict,
        })

    # Render as HTML table for styling
    header_cols = ["Archetype", "Count", "Switches", "Switch %", "Transit Gain", "Policy Verdict"]
    rows_html = ""
    for row in rows:
        gain_raw = float(row["Transit Gain"].replace("%", "").replace("+", ""))
        gain_color = "#22c55e" if gain_raw > 5 else "#f59e0b" if gain_raw > 0 else "#ef4444"
        rows_html += f"""<tr>
          <td style="padding:10px 14px;color:#f8fafc;font-weight:500">{row["Archetype"]}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:center">{row["Count"]}</td>
          <td style="padding:10px 14px;color:#f97316;text-align:center">{row["Switches"]}</td>
          <td style="padding:10px 14px;color:#94a3b8;text-align:center">{row["Switch %"]}</td>
          <td style="padding:10px 14px;color:{gain_color};text-align:center;font-weight:700">{row["Transit Gain"]}</td>
          <td style="padding:10px 14px;text-align:center">{row["Policy Verdict"]}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;background:#1e293b;
                  border:1px solid #334155;border-radius:10px;overflow:hidden">
      <thead>
        <tr style="background:#0f172a">
          {"".join(f'<th style="padding:10px 14px;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:1px;text-align:{"left" if i==0 else "center"}">{h}</th>' for i, h in enumerate(header_cols))}
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)
