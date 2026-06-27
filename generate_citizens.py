"""
generate_citizens.py
Run once to produce enhanced_citizens.json with 1000 citizens across 8 archetypes.
Usage: python generate_citizens.py
"""

import json
import random

random.seed(42)

ARCHETYPES = {
    "School Student": {
        "count": 120,
        "age_range": (10, 17),
        "income_range": (0, 0),
        "budget_range": (9, 10),
        "time_range": (3, 6),
        "comfort_range": (3, 6),
        "safety_range": (8, 10),
        "goal": "minimize_cost",
        "distance_range": (1, 8),
        "preferred_zones": ["Rohini", "Dwarka", "Janakpuri", "Uttam Nagar",
                            "Dilshad Garden", "Shahdara", "Lajpat Nagar"],
        "transports": ["Walking", "Bus", "Auto Rickshaw"],
        "transport_weights": [0.45, 0.40, 0.15],
    },
    "Female Student": {
        "count": 140,
        "age_range": (17, 24),
        "income_range": (2000, 9000),
        "budget_range": (8, 10),
        "time_range": (4, 7),
        "comfort_range": (2, 5),
        "safety_range": (7, 10),
        "goal": "minimize_cost",
        "distance_range": (2, 20),
        "preferred_zones": ["Rohini", "Dwarka", "Janakpuri", "Uttam Nagar",
                            "Dilshad Garden", "Shahdara"],
        "transports": ["Metro", "Bus", "Walking"],
        "transport_weights": [0.5, 0.4, 0.1],
    },
    "Female Office Worker": {
        "count": 130,
        "age_range": (23, 40),
        "income_range": (25000, 90000),
        "budget_range": (5, 7),
        "time_range": (8, 10),
        "comfort_range": (6, 9),
        "safety_range": (7, 10),
        "goal": "minimize_travel_time",
        "distance_range": (8, 28),
        "preferred_zones": ["Connaught Place", "Nehru Place", "Saket",
                            "Lajpat Nagar", "Gurugram Border"],
        "transports": ["Metro", "Cab", "Car", "Bus"],
        "transport_weights": [0.45, 0.25, 0.2, 0.1],
    },
    "Male Office Worker": {
        "count": 150,
        "age_range": (23, 42),
        "income_range": (28000, 100000),
        "budget_range": (5, 7),
        "time_range": (7, 10),
        "comfort_range": (6, 9),
        "safety_range": (4, 8),
        "goal": "minimize_travel_time",
        "distance_range": (8, 30),
        "preferred_zones": ["Connaught Place", "Nehru Place", "Noida Sector 18",
                            "Saket", "Vasant Kunj"],
        "transports": ["Metro", "Bike", "Car", "Bus"],
        "transport_weights": [0.35, 0.25, 0.25, 0.15],
    },
    "Auto Driver": {
        "count": 100,
        "age_range": (28, 55),
        "income_range": (18000, 40000),
        "budget_range": (4, 6),
        "time_range": (7, 9),
        "comfort_range": (3, 5),
        "safety_range": (4, 7),
        "goal": "maximize_income",
        "distance_range": (30, 70),
        "preferred_zones": ["Karol Bagh", "Lajpat Nagar", "Connaught Place",
                            "Nehru Place", "Shahdara"],
        "transports": ["Auto Rickshaw"],
        "transport_weights": [1.0],
    },
    "Shop Owner": {
        "count": 100,
        "age_range": (28, 55),
        "income_range": (30000, 120000),
        "budget_range": (6, 9),
        "time_range": (5, 7),
        "comfort_range": (5, 8),
        "safety_range": (5, 8),
        "goal": "balance_cost_time",
        "distance_range": (2, 12),
        "preferred_zones": ["Karol Bagh", "Lajpat Nagar", "Sadar Bazar",
                            "Chandni Chowk", "Nehru Place"],
        "transports": ["Bike", "Scooter", "Car", "Walking"],
        "transport_weights": [0.3, 0.25, 0.3, 0.15],
    },
    "Elderly Resident": {
        "count": 120,
        "age_range": (60, 80),
        "income_range": (8000, 35000),
        "budget_range": (7, 10),
        "time_range": (2, 5),
        "comfort_range": (7, 10),
        "safety_range": (8, 10),
        "goal": "maximize_comfort_safety",
        "distance_range": (1, 8),
        "preferred_zones": ["Lajpat Nagar", "Saket", "Vasant Kunj", "Dwarka", "Rohini"],
        "transports": ["Bus", "Walking", "Auto Rickshaw"],
        "transport_weights": [0.4, 0.35, 0.25],
    },
    "Delivery Worker": {
        "count": 140,
        "age_range": (20, 38),
        "income_range": (12000, 25000),
        "budget_range": (6, 9),
        "time_range": (8, 10),
        "comfort_range": (2, 5),
        "safety_range": (3, 6),
        "goal": "maximize_income",
        "distance_range": (15, 60),
        "preferred_zones": ["Connaught Place", "Karol Bagh", "Nehru Place",
                            "Noida Sector 18", "Lajpat Nagar"],
        "transports": ["Bike", "Scooter", "Auto Rickshaw"],
        "transport_weights": [0.5, 0.3, 0.2],
    },
}

DELHI_ZONES = [
    "Connaught Place", "Lajpat Nagar", "Dwarka", "Rohini", "Noida Sector 18",
    "Saket", "Janakpuri", "Nehru Place", "Karol Bagh", "Vasant Kunj",
    "Gurugram Border", "Shahdara", "Uttam Nagar", "Dilshad Garden",
    "Chandni Chowk", "Sadar Bazar",
]

def pick_zone(preferred):
    if random.random() < 0.7:
        return random.choice(preferred)
    return random.choice(DELHI_ZONES)

citizens = []
cid = 1

for archetype, cfg in ARCHETYPES.items():
    for _ in range(cfg["count"]):
        income = random.randint(*cfg["income_range"])
        citizen = {
            "id": cid,
            "type": archetype,
            "age": random.randint(*cfg["age_range"]),
            "monthly_income": income,
            "current_transport": random.choices(cfg["transports"], weights=cfg["transport_weights"])[0],
            "commute_distance_km": round(random.uniform(*cfg["distance_range"]), 1),
            "home_zone": pick_zone(cfg["preferred_zones"]),
            "budget_sensitivity":  random.randint(*cfg["budget_range"]),
            "time_sensitivity":    random.randint(*cfg["time_range"]),
            "comfort_sensitivity": random.randint(*cfg["comfort_range"]),
            "safety_sensitivity":  random.randint(*cfg["safety_range"]),
            "goal": cfg["goal"],
        }
        citizens.append(citizen)
        cid += 1

random.shuffle(citizens)
for i, c in enumerate(citizens):
    c["id"] = i + 1

with open("enhanced_citizens.json", "w") as f:
    json.dump(citizens, f, indent=2)

print(f"Generated {len(citizens)} citizens across {len(ARCHETYPES)} archetypes:")
breakdown = {}
for c in citizens:
    breakdown[c["type"]] = breakdown.get(c["type"], 0) + 1
for t, n in sorted(breakdown.items()):
    print(f"  {t}: {n}")
