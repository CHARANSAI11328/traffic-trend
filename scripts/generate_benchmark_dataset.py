"""
Benchmark Demonstration Dataset Generator
Generates realistic, statistically calibrated multi-year road accident records.
Explicitly tagged as a demonstration dataset per project guidelines.
"""
import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Set deterministic random seed
random.seed(42)
np.random.seed(42)

def generate_benchmark_dataset(num_records: int = 3500) -> pd.DataFrame:
    """Generates multi-year road accident records based on official road safety report distributions."""
    
    # Regional clusters with centroid coordinates
    regions = [
        {"state": "Maharashtra", "district": "Mumbai", "lat": 19.0760, "lon": 72.8777, "type": "Urban"},
        {"state": "Maharashtra", "district": "Pune", "lat": 18.5204, "lon": 73.8567, "type": "Urban"},
        {"state": "Maharashtra", "district": "Nagpur", "lat": 21.1458, "lon": 79.0882, "type": "Rural"},
        {"state": "Karnataka", "district": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "type": "Urban"},
        {"state": "Karnataka", "district": "Mysuru", "lat": 12.2958, "lon": 76.6394, "type": "Urban"},
        {"state": "Karnataka", "district": "Belagavi", "lat": 15.8497, "lon": 74.4977, "type": "Rural"},
        {"state": "Tamil Nadu", "district": "Chennai", "lat": 13.0827, "lon": 80.2707, "type": "Urban"},
        {"state": "Tamil Nadu", "district": "Coimbatore", "lat": 11.0168, "lon": 76.9558, "type": "Urban"},
        {"state": "Tamil Nadu", "district": "Madurai", "lat": 9.9252, "lon": 78.1198, "type": "Rural"},
        {"state": "Delhi NCT", "district": "South Delhi", "lat": 28.5355, "lon": 77.2410, "type": "Urban"},
        {"state": "Delhi NCT", "district": "North Delhi", "lat": 28.7041, "lon": 77.1025, "type": "Urban"},
        {"state": "Gujarat", "district": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "type": "Urban"},
        {"state": "Gujarat", "district": "Surat", "lat": 21.1702, "lon": 72.8311, "type": "Urban"},
        {"state": "Gujarat", "district": "Vadodara", "lat": 22.3072, "lon": 73.1812, "type": "Rural"},
        {"state": "Uttar Pradesh", "district": "Lucknow", "lat": 26.8467, "lon": 80.9462, "type": "Urban"},
        {"state": "Uttar Pradesh", "district": "Kanpur", "lat": 26.4499, "lon": 80.3319, "type": "Urban"},
        {"state": "Uttar Pradesh", "district": "Varanasi", "lat": 25.3176, "lon": 82.9739, "type": "Rural"},
        {"state": "Rajasthan", "district": "Jaipur", "lat": 26.9124, "lon": 75.7873, "type": "Urban"},
        {"state": "Rajasthan", "district": "Jodhpur", "lat": 26.2389, "lon": 73.0243, "type": "Rural"},
        {"state": "West Bengal", "district": "Kolkata", "lat": 22.5726, "lon": 88.3639, "type": "Urban"},
        {"state": "Telangana", "district": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "type": "Urban"},
        {"state": "Kerala", "district": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366, "type": "Urban"},
        {"state": "Kerala", "district": "Ernakulam", "lat": 9.9816, "lon": 76.2999, "type": "Urban"}
    ]

    road_types = ["National Highway", "State Highway", "Expressway", "Urban Arterial", "Rural District Road"]
    road_weights = [0.35, 0.25, 0.12, 0.20, 0.08]

    road_conditions = ["Dry & Clear", "Wet & Slippery", "Potholed / Under Construction", "Flooded / Waterlogged"]
    road_cond_weights = [0.70, 0.18, 0.09, 0.03]

    weathers = ["Clear / Sunny", "Rainy / Monsoonal", "Dense Fog / Low Visibility", "Overcast / Stormy"]
    weather_weights = [0.72, 0.16, 0.08, 0.04]

    light_conditions = ["Daylight", "Dark - Street Lights Lit", "Dark - Street Lights Unlit", "Dusk / Twilight"]
    light_weights = [0.55, 0.25, 0.12, 0.08]

    collision_types = ["Head-on Collision", "Rear-end Collision", "Side-swipe / T-Bone", "Hit Pedestrian", "Hit Fixed Object", "Vehicle Rollover"]
    collision_weights = [0.24, 0.28, 0.20, 0.14, 0.08, 0.06]

    vehicle_types = ["Two-Wheeler (Motorcycle/Scooter)", "Car / Private SUV", "Heavy Commercial Truck", "Bus / Public Transit", "Auto-Rickshaw", "Bicycle", "Pedestrian"]
    vehicle_weights = [0.38, 0.28, 0.16, 0.07, 0.06, 0.03, 0.02]

    contributing_factors = [
        "Overspeeding Above Limit",
        "Distracted Driving / Mobile Phone Use",
        "Driving Under Influence (Alcohol/Drugs)",
        "Lane Infiltration / Wrong-Side Driving",
        "Jumping Traffic Signal / Red Light",
        "Poor Road Surface / Sudden Pothole",
        "Adverse Weather / Sudden Reduced Visibility",
        "Mechanical Failure / Tire Blowout"
    ]
    factor_weights = [0.45, 0.18, 0.12, 0.10, 0.05, 0.04, 0.03, 0.03]

    start_date = datetime(2019, 1, 1)
    end_date = datetime(2024, 9, 30)
    delta_days = (end_date - start_date).days

    records = []

    for i in range(1, num_records + 1):
        accident_id = f"ACC-IND-{2019 + (i % 6)}-{i:06d}"
        
        # Pick date
        random_day = random.randint(0, delta_days)
        acc_date = start_date + timedelta(days=random_day)
        
        # Pick hour with realistic rush-hour and late night weighting
        # Peak 1: 08-11 (Morning rush), Peak 2: 17-21 (Evening rush), Night: 22-02 (Heavy trucks)
        hour_weights = [
            0.02, 0.02, 0.02, 0.01, 0.01, 0.02, # 00-05
            0.04, 0.06, 0.08, 0.07, 0.05, 0.04, # 06-11
            0.04, 0.04, 0.04, 0.05, 0.06, 0.08, # 12-17
            0.09, 0.08, 0.06, 0.05, 0.04, 0.03  # 18-23
        ]
        hour = random.choices(range(24), weights=hour_weights, k=1)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        acc_time = f"{hour:02d}:{minute:02d}:{second:02d}"

        # Region
        reg = random.choice(regions)
        state = reg["state"]
        district = reg["district"]
        loc_type = reg["type"]
        
        # Jitter coordinates slightly (+/- 0.08 degrees) to simulate real district dispersion
        lat = round(reg["lat"] + random.uniform(-0.08, 0.08), 5)
        lon = round(reg["lon"] + random.uniform(-0.08, 0.08), 5)

        # Environmental factors
        road_type = random.choices(road_types, weights=road_weights, k=1)[0]
        road_cond = random.choices(road_conditions, weights=road_cond_weights, k=1)[0]
        weather = random.choices(weathers, weights=weather_weights, k=1)[0]
        light = random.choices(light_conditions, weights=light_weights, k=1)[0]
        col_type = random.choices(collision_types, weights=collision_weights, k=1)[0]
        veh_type = random.choices(vehicle_types, weights=vehicle_weights, k=1)[0]
        factor = random.choices(contributing_factors, weights=factor_weights, k=1)[0]

        # Vehicles involved
        if col_type in ["Hit Pedestrian", "Hit Fixed Object", "Vehicle Rollover"]:
            n_vehicles = 1
        elif col_type in ["Rear-end Collision", "Head-on Collision", "Side-swipe / T-Bone"]:
            n_vehicles = random.choices([2, 3, 4], weights=[0.85, 0.12, 0.03], k=1)[0]
        else:
            n_vehicles = 2

        # Severity & Casualties calculation (Statistically grounded)
        # Higher lethality: Head-on, Hit Pedestrian, Expressway, Night Unlit, Heavy Truck, Two-Wheeler
        lethality_score = 0.0
        if road_type in ["Expressway", "National Highway"]:
            lethality_score += 0.25
        if col_type in ["Head-on Collision", "Hit Pedestrian"]:
            lethality_score += 0.35
        if veh_type in ["Two-Wheeler (Motorcycle/Scooter)", "Bicycle", "Pedestrian"]:
            lethality_score += 0.30
        if "Dark" in light:
            lethality_score += 0.15
        if factor in ["Overspeeding Above Limit", "Driving Under Influence (Alcohol/Drugs)"]:
            lethality_score += 0.20

        # Random baseline modifier
        dice = random.random()
        
        if dice < (0.12 + (lethality_score * 0.18)):
            # Fatal crash
            severity = "Fatal"
            fatalities = random.choices([1, 2, 3, 4], weights=[0.82, 0.13, 0.04, 0.01], k=1)[0]
            injuries = random.choices([0, 1, 2, 3], weights=[0.40, 0.35, 0.18, 0.07], k=1)[0]
        elif dice < (0.42 + (lethality_score * 0.15)):
            # Grievous injury
            severity = "Grievous Injury"
            fatalities = 0
            injuries = random.choices([1, 2, 3, 4], weights=[0.70, 0.20, 0.07, 0.03], k=1)[0]
        elif dice < 0.85:
            # Minor injury
            severity = "Minor Injury"
            fatalities = 0
            injuries = random.choices([1, 2], weights=[0.85, 0.15], k=1)[0]
        else:
            # Property damage only
            severity = "Property Damage Only"
            fatalities = 0
            injuries = 0

        records.append({
            "accident_id": accident_id,
            "accident_date": acc_date.strftime("%Y-%m-%d"),
            "accident_time": acc_time,
            "year": acc_date.year,
            "month": acc_date.strftime("%B"),
            "day_of_week": acc_date.strftime("%A"),
            "hour_of_day": hour,
            "state": state,
            "district": district,
            "location_type": loc_type,
            "latitude": lat,
            "longitude": lon,
            "road_type": road_type,
            "road_condition": road_cond,
            "weather": weather,
            "light_condition": light,
            "accident_severity": severity,
            "fatalities_count": fatalities,
            "injured_count": injuries,
            "vehicles_involved_count": n_vehicles,
            "collision_type": col_type,
            "primary_vehicle_type": veh_type,
            "contributing_factor": factor,
            "data_origin": "BENCHMARK DEMONSTRATION DATASET (DO NOT TREAT AS OFFICIAL POLICE RECORD WITHOUT AUDIT)"
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_benchmark_dataset(num_records=3500)
    
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = raw_dir / "traffic_accidents_benchmark_demonstration.csv"
    xlsx_path = raw_dir / "traffic_accidents_benchmark_demonstration.xlsx"
    
    df.to_csv(csv_path, index=False, encoding="utf-8")
    df.to_excel(xlsx_path, index=False, engine="openpyxl")
    
    print(f"Benchmark demonstration dataset generated successfully:")
    print(f"CSV:  {csv_path} ({len(df)} records)")
    print(f"XLSX: {xlsx_path} ({len(df)} records)")

