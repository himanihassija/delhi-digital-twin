# Delhi's Digital Twin

**Agent-Based Urban Transport Policy Simulator**

Simulate how 1,000 Delhi citizens independently decide their transport mode in response to any policy intervention, choose from 12 presets, stack two policies together, or describe your own in plain English and let Claude parse it into simulation parameters.

---

## What It Does

Each citizen is a software agent with their own income, commute distance, home zone, and sensitivity scores across cost, time, comfort, and safety. When a policy is applied, every agent re-evaluates their transport options and switches if a better mode exists. The aggregate of 1,000 individual decisions produces city-level metrics: mobility score, CO2 reduction, equity index, and citizen satisfaction.

---

## Features

| Feature | Description |
|---|---|
| **1,000 Citizens ·   8 Archetypes** | School Student, Female Student, Female Office Worker, Male Office Worker, Auto Driver, Shop Owner, Elderly Resident, Delivery Worker |
| **12 Preset Policies** | Free Metro Rides For Women, 50% Bus Fare Reduction, Congestion Tax, New Metro Line, Metro 2AM, Airport Express Discount, Reserved Student Coaches, Personal Carbon Budget, Free Transit Birthdays, Car-Free School Zones, One-Ticket City, Free EV Parking |
| **Policy Stacking** | Combine any two policies and simulate their compound effect — additive modifiers stack cleanly across all archetypes |
| **Compare All 12** | Run all policies in one click and rank them by mobility, CO2, switches, satisfaction, and equity |
| **LLM Analyst Agents** | Five Claude powered agents (Government, Transport, Environment, Citizens, Business) each write independent policy briefs |
| **Social Reactions Feed** | Claude generates 6 Hinglish social media posts — one per archetype — reacting to the active policy |
| **6-Month Adoption Curve** | Logistic ramp showing how ridership shifts gradually after policy launch, not just a single snapshot |
| **Equity Analysis** | Tracks public transit adoption gains across low, middle, and high income brackets with a rebalanced equity index |
| **Confidence Intervals** | 5 run Monte Carlo with randomised sensitivity scores to show result stability |
| **Time-of-Day Simulation** | Morning Peak, Afternoon, and Evening Peak produce different adoption and CO2 profiles |
| **Live Simulation Replay** | Watch all 1,000 citizen decisions stream in real time with a live bar chart |
| **Animated Metro Map** | Metro animation scaled to actual ridership counts after simulation |
| **Custom Citizen Builder** | Drop in any archetype, income, and commute distance and see their optimal transport choice |
| **PDF Export** | Download a full policy report with metrics, transport tables, and all five agent reports |
| **Natural Language Policy** | Describe a policy in plain English and Claude parses it into simulation parameters automatically |

---

## Architecture
enhanced_citizens.json          <- 1,000 pre-generated citizens with archetype attributes

simulation.py                   <- Core engine: policy modifiers, agent decisions, equity, CI, ToD

app.py                          <- Streamlit UI: sidebar, charts, LLM calls, PDF export

archetypes_tab.py               <- Per-archetype breakdown visualisation

generate_citizens.py            <- One-time citizen generation script

**Policy engine** — each policy applies additive score modifiers to transport mode attributes (cost, time, comfort, safety, each 1-10). Multiple policies stack independently. Each citizen runs a weighted utility maximisation across all four modes.

**LLM layer** — six Claude API calls per simulation: five specialist analyst agents and one social reactions feed. All calls are optional; the simulation runs fully offline without them.

---

## Setup

```bash
pip install streamlit anthropic requests numpy matplotlib reportlab
python generate_citizens.py      # generates enhanced_citizens.json (run once)
streamlit run app.py
```

Add your Anthropic API key to the environment or Streamlit secrets:

```bash
export ANTHROPIC_API_KEY=sk-...
```

---

## Metrics Explained

- **Mobility Score** — composite of congestion reduction, transit adoption, cost savings, and CO2 points
- **CO2 Score** — weighted count of high-emission to low-emission mode switches (Auto to Metro = 5 pts, Auto to Bus = 3 pts, Bus to Metro = 2 pts)
- **Equity Index** — rewards absolute low-income transit gains; penalises only when high-income gains significantly exceed low-income gains (higher = more pro-poor)
- **Citizen Satisfaction** — based on switch volume, CO2 impact, and policy-specific sentiment data

---

## Policies at a Glance

**Classic**
- **Free Metro Rides For Women** — cost score maxed for Female Students, Female Office Workers, School Students
- **50% Bus Fare Reduction** — bus cost boost for all; safety bonus for School Students
- **Congestion Tax** — auto cost penalty, pushes agents toward metro and bus
- **New Metro Line** — metro time score boost, benefits long-distance commuters most

**Extended**
- **Metro 2AM** — safety and comfort boost for Metro; night economy impact
- **Airport Express Fare Reduction** — metro cost and time boost for commutes of 15 km or more
- **Reserved Student Coaches** — metro and bus comfort and safety maxed for students
- **Personal Carbon Budget** — metro and bus rewarded, auto penalised for all archetypes
- **Free Transit Birthdays** — stochastic 1/365 free transit day; low aggregate impact, high goodwill
- **Car-Free School Zones** — walking and bus safety boost near schools
- **One-Ticket City** — metro and bus time and comfort boost for seamless transfers
- **Free EV Parking** — metro cost boost for short-distance commuters
