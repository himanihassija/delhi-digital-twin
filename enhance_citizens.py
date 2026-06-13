import json
import random

with open("citizens.json", "r") as f:
    citizens = json.load(f)

for citizen in citizens:

    citizen_type = citizen["type"]

    if citizen_type == "Female Student":
        citizen["budget_sensitivity"] = random.randint(8, 10)
        citizen["time_sensitivity"] = random.randint(4, 6)
        citizen["comfort_sensitivity"] = random.randint(2, 5)
        citizen["safety_sensitivity"] = random.randint(7, 10)
        citizen["goal"] = "minimize_cost"

    elif citizen_type == "Female Office Worker":
        citizen["budget_sensitivity"] = random.randint(5, 7)
        citizen["time_sensitivity"] = random.randint(8, 10)
        citizen["comfort_sensitivity"] = random.randint(6, 8)
        citizen["safety_sensitivity"] = random.randint(7, 10)
        citizen["goal"] = "minimize_travel_time"

    elif citizen_type == "Male Office Worker":
        citizen["budget_sensitivity"] = random.randint(5, 7)
        citizen["time_sensitivity"] = random.randint(8, 10)
        citizen["comfort_sensitivity"] = random.randint(6, 8)
        citizen["safety_sensitivity"] = random.randint(5, 8)
        citizen["goal"] = "minimize_travel_time"

    elif citizen_type == "Auto Driver":
        citizen["budget_sensitivity"] = random.randint(4, 6)
        citizen["time_sensitivity"] = random.randint(7, 9)
        citizen["comfort_sensitivity"] = random.randint(3, 5)
        citizen["safety_sensitivity"] = random.randint(4, 7)
        citizen["goal"] = "maximize_income"

    elif citizen_type == "Shop Owner":
        citizen["budget_sensitivity"] = random.randint(6, 8)
        citizen["time_sensitivity"] = random.randint(5, 7)
        citizen["comfort_sensitivity"] = random.randint(5, 7)
        citizen["safety_sensitivity"] = random.randint(5, 8)
        citizen["goal"] = "balance_cost_time"

with open("enhanced_citizens.json", "w") as f:
    json.dump(citizens, f, indent=4)

print(f"Enhanced {len(citizens)} citizens successfully!")