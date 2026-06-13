# 🚇 Delhi's Digital Twin
### Agent-Based Urban Policy Simulator

> Simulate how 100 Delhi citizens respond to transport policies — powered by autonomous AI agents, real-time analytics, and LLM-generated policy briefs.

🔗 **Live App:** [delhi-digital-twin.streamlit.app](https://delhi-digital-twin.streamlit.app/)

---

## 🌆 What Is This?

Delhi's Digital Twin is an **agent-based urban mobility simulator**. It models 100 Delhi citizens — students, office workers, auto drivers, shop owners — each with unique cost, time, comfort, and safety preferences. When you apply a transport policy, every agent independently decides whether to switch their mode of transport.

Five autonomous AI agents then analyse the outcome from different perspectives: Government, Transport Authority, Environment, Citizens, and Business — each generating an LLM-powered policy brief.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **LLM Agent Reports** | Claude generates intelligent policy briefs for 5 agent personas |
| 🎬 **Live Simulation Replay** | Watch 100 citizens make decisions in real time with a live chart |
| 🚆 **Animated Metro Map** | CSS-animated Delhi metro map with moving trains, buses & autos |
| 🧑 **Custom Citizen Builder** | Simulate any citizen — set type, income, distance, see their choice |
| 📡 **Radar Chart** | 5-axis spider chart across Mobility, Environment, Equity, Economy, Safety |
| ⚖️ **Equity Analysis** | Public transport adoption by low / middle / high income brackets |
| ⏰ **Time-of-Day Simulation** | Morning Peak, Afternoon, Evening Peak with different crowd modifiers |
| 🎯 **Confidence Intervals** | 5 simulation runs with ±1σ error bars for statistical rigour |
| 📄 **PDF Export** | One-click formatted report with all metrics and agent briefs |
| 💬 **Natural Language Policy** | Type any policy in plain English — Claude maps it to parameters |
| 📊 **Multi-Policy Comparison** | Run all 12 policies, ranked table + grouped bar chart |

---

## 🗳️ 12 Simulated Policies

**Classic**
- Free Metro Rides For Women
- 50% Bus Fare Reduction
- Congestion Tax
- New Metro Line

**New**
- 🌙 Metro Operating Hours Extended to 2 AM
- ✈️ Airport Express Fare Reduction
- 🎓 Reserved Student Coaches
- 🌿 Personal Carbon Budget for Transportation
- 🎂 Free Transit Birthdays
- 🏫 Car-Free School Zones
- 🎫 One-Ticket City
- ⚡ Free EV Parking

---

## 🧠 How It Works

```
enhanced_citizens.json          ← 100 citizens with sensitivity scores
        ↓
simulation.py                   ← Policy engine + agent decisions
  ├── get_transport_scores()     ← Apply policy effects to transport attributes
  ├── choose_best_transport()    ← Each agent picks highest-scoring mode
  ├── run_with_confidence()      ← 5 runs for statistical range
  ├── compute_equity()           ← Income-bracket analysis
  └── run_time_of_day()          ← Morning / Afternoon / Evening Peak
        ↓
results.json + map_data.json    ← Simulation outputs
        ↓
app.py                          ← Streamlit UI + LLM agent reports + charts
```

Each citizen has:
- **Type**: Female Student / Female Office Worker / Male Office Worker / Auto Driver / Shop Owner
- **Sensitivities** (1–10): budget, time, comfort, safety
- **Goal**: minimize cost / minimize time / maximize income / balance

Transport modes scored on: **cost · time · comfort · safety**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/himanihassija/delhi-digital-twin.git
cd delhi-digital-twin
pip install -r requirements.txt
```

### Run

```bash
# Step 1 — generate citizen profiles (only needed once)
python enhance_citizens.py

# Step 2 — launch the app
python -m streamlit run app.py
```

---

## 📁 Project Structure

```
delhi-digital-twin/
│
├── app.py                  # Streamlit UI — all features
├── simulation.py           # Core agent simulation engine
├── enhance_citizens.py     # Adds sensitivity scores to citizens
│
├── citizens.json           # Base citizen dataset (100 citizens)
├── enhanced_citizens.json  # Citizens with sensitivity scores (generated)
│
├── results.json            # Last simulation output
├── map_data.json           # Citizen map positions (generated)
├── updated_citizens.json   # Post-simulation citizen states (generated)
│
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🧩 Citizen Archetypes

| Type | Budget | Time | Comfort | Safety | Goal |
|---|---|---|---|---|---|
| Female Student | 8–10 | 4–6 | 2–5 | 7–10 | Minimize cost |
| Female Office Worker | 5–7 | 8–10 | 6–8 | 7–10 | Minimize travel time |
| Male Office Worker | 5–7 | 8–10 | 6–8 | 5–8 | Minimize travel time |
| Auto Driver | 4–6 | 7–9 | 3–5 | 4–7 | Maximize income |
| Shop Owner | 6–8 | 5–7 | 5–7 | 5–8 | Balance cost & time |

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit, HTML/CSS/JS (animated metro map)
- **Simulation**: Python, NumPy, Matplotlib
- **AI**: Anthropic Claude API (claude-sonnet-4-6)
- **PDF**: ReportLab
- **Data**: Custom JSON citizen dataset

---

## 🏙️ Built For

**FAR AWAY Hackathon** — Round 1 Online MVP Submission
Theme: Urban Intelligence / Smart Cities
Submission deadline: 14 June 2026

---

## 📄 License

MIT License — feel free to fork, extend, and build on this.

---

<p align="center">Built with ❤️ for Delhi · Powered by Claude · Simulated by Agents</p>
