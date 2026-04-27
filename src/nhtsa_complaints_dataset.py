import os
import time
from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd
import requests

from nhtsa_config import generate_vehicle_list

API_URL = "https://api.nhtsa.gov/complaints/complaintsByVehicle"



REQUEST_DELAY_SECONDS = 0.25
REQUEST_TIMEOUT = 30
COMPLAINT_CAP = 25  


PART_KEYWORDS: Dict[str, List[str]] = {
    # Drivetrain
    "cv_wellness": [
        "cv joint",
        "constant velocity joint",
        "cv axle",
        "axle clicking",
        "cv boot",
        "front axle",
        "half shaft",
    ],
    "wb_wellness": [
        "wheel bearing",
        "bearing noise",
        "hub bearing",
        "humming noise",
        "growling noise",
    ],
    "brk_wellness": [
        "brake",
        "brakes",
        "brake pad",
        "brake rotor",
        "brake caliper",
        "brake failure",
        "parking brake",
        "abs",
        "anti-lock brake",
        "stopping distance",
    ],

    # Electrical
    "bat_wellness": [
        "battery",
        "dead battery",
        "battery drain",
        "battery failed",
        "12v battery",
        "12-volt battery",
    ],
    "alt_wellness": [
        "alternator",
        "charging system",
        "not charging",
        "battery not charging",
        "voltage regulator",
    ],
    "sta_wellness": [
        "starter",
        "starter motor",
        "no crank",
        "won't crank",
        "would not crank",
        "slow crank",
    ],

    # Engine
    "coolant_wellness": [
        "coolant",
        "overheat",
        "overheating",
        "radiator",
        "water pump",
        "thermostat",
        "cooling system",
        "head gasket",
    ],
    "ignition_wellness": [
        "ignition",
        "spark plug",
        "spark plugs",
        "ignition coil",
        "coil pack",
        "misfire",
    ],
    "fuel_wellness": [
        "fuel pump",
        "fuel injector",
        "fuel injectors",
        "fuel system",
        "stalling",
        "stalls",
        "loss of power",
        "hesitation",
    ],
}


SYSTEM_COMPONENT_HINTS: Dict[str, List[str]] = {
    "drivetrain": [
        "POWER TRAIN",
        "SERVICE BRAKES",
        "WHEELS",
        "SUSPENSION",
    ],
    "electrical": [
        "ELECTRICAL SYSTEM",
    ],
    "engine": [
        "ENGINE",
        "ENGINE AND ENGINE COOLING",
        "FUEL/PROPULSION SYSTEM",
    ],
}


PART_TO_SYSTEM = {
    "cv_wellness": "drivetrain",
    "wb_wellness": "drivetrain",
    "brk_wellness": "drivetrain",
    "bat_wellness": "electrical",
    "alt_wellness": "electrical",
    "sta_wellness": "electrical",
    "coolant_wellness": "engine",
    "ignition_wellness": "engine",
    "fuel_wellness": "engine",
}


def fetch_complaints(make: str, model: str, year: int, timeout: int = REQUEST_TIMEOUT) -> List[dict]:
    params = {
        "make": make,
        "model": model,
        "modelYear": year,
    }
    response = requests.get(API_URL, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    return data.get("results", [])


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def get_summary(complaint: dict) -> str:
    # Some records may vary a bit. Prefer summary-like text if present.
    for key in ("summary", "SUMMARY", "Complaint Summary"):
        if key in complaint and complaint[key]:
            return str(complaint[key])
    return ""


def get_components(complaint: dict) -> str:
    for key in ("components", "COMPONENTS", "Component"):
        if key in complaint and complaint[key]:
            return str(complaint[key])
    return ""


def complaint_matches_system(components: str, system_name: str) -> bool:
    upper_components = (components or "").upper()
    return any(hint in upper_components for hint in SYSTEM_COMPONENT_HINTS[system_name])


def complaint_matches_keywords(summary: str, keywords: List[str]) -> bool:
    text = normalize_text(summary)
    return any(keyword in text for keyword in keywords)


def count_part_complaints(complaints: List[dict], part_name: str) -> int:
    """
    Counts complaints relevant to a specific part.
    We require the keyword match in complaint summary text.
    Component buckets are used as a soft filter to make matching more relevant.
    """
    system_name = PART_TO_SYSTEM[part_name]
    keywords = PART_KEYWORDS[part_name]

    count = 0
    for complaint in complaints:
        summary = get_summary(complaint)
        components = get_components(complaint)

        if not summary:
            continue

        keyword_hit = complaint_matches_keywords(summary, keywords)
        system_hit = complaint_matches_system(components, system_name)

        # Count complaint if:
        # 1) keyword appears in summary, and
        # 2) component bucket matches OR summary is explicitly part-specific
        if keyword_hit and (system_hit or True):
            count += 1

    return count


def complaint_count_to_score(count: int, cap: int = COMPLAINT_CAP) -> float:
    """
    Convert complaint count into a 5-100 score.

    0 complaints => 100
    cap complaints or more => 5
    """
    clipped = min(count, cap)
    score = 100 - (clipped / cap) * 95
    return round(max(5.0, score), 2)


def compute_system_averages(row: dict) -> None:
    row["drivetrain_score"] = round(
        (row["cv_wellness"] + row["wb_wellness"] + row["brk_wellness"]) / 3, 2
    )
    row["electrical_score"] = round(
        (row["bat_wellness"] + row["alt_wellness"] + row["sta_wellness"]) / 3, 2
    )
    row["engine_score"] = round(
        (row["coolant_wellness"] + row["ignition_wellness"] + row["fuel_wellness"]) / 3, 2
    )
    row["overall_score"] = round(
        (row["drivetrain_score"] + row["electrical_score"] + row["engine_score"]) / 3, 2
    )


def build_row(make: str, model: str, year: int, complaints: List[dict]) -> dict:
    row = {
        "brand": make,
        "model": model,
        "year": year,
        "total_complaints": len(complaints),
    }

    for part_name in PART_KEYWORDS.keys():
        count = count_part_complaints(complaints, part_name)
        row[f"{part_name}_complaints"] = count
        row[part_name] = complaint_count_to_score(count)

    compute_system_averages(row)
    return row


def save_outputs(df: pd.DataFrame, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    main_path = os.path.join(out_dir, "nhtsa_component_scores.csv")
    df.to_csv(main_path, index=False)

    # Optional compact lookup table by brand/model/year with system averages only
    lookup_cols = [
        "brand",
        "model",
        "year",
        "total_complaints",
        "drivetrain_score",
        "electrical_score",
        "engine_score",
        "overall_score",
    ]
    lookup_path = os.path.join(out_dir, "nhtsa_system_scores_lookup.csv")
    df[lookup_cols].to_csv(lookup_path, index=False)

    print(f"\nSaved full dataset to: {main_path}")
    print(f"Saved system lookup to: {lookup_path}")


def main():
    vehicles = generate_vehicle_list()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    out_dir = os.path.join(project_root, "data", "processed")

    rows = []
    failures = []

    print(f"Generating dataset for {len(vehicles)} make/model/year combinations...\n")

    for i, (make, model, year) in enumerate(vehicles, start=1):
        print(f"[{i}/{len(vehicles)}] Fetching {year} {make} {model}...")

        try:
            complaints = fetch_complaints(make, model, year)
            row = build_row(make, model, year, complaints)
            rows.append(row)

            print(
                f"  complaints={row['total_complaints']}, "
                f"drive={row['drivetrain_score']}, "
                f"elec={row['electrical_score']}, "
                f"engine={row['engine_score']}, "
                f"overall={row['overall_score']}"
            )
        except Exception as e:
            failures.append((make, model, year, str(e)))
            print(f"  failed: {e}")

        time.sleep(REQUEST_DELAY_SECONDS)

    df = pd.DataFrame(rows)
    save_outputs(df, out_dir)

    if failures:
        fail_path = os.path.join(out_dir, "nhtsa_generation_failures.csv")
        pd.DataFrame(
            failures,
            columns=["brand", "model", "year", "error"]
        ).to_csv(fail_path, index=False)
        print(f"Saved failures log to: {fail_path}")

    print("\nPreview:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()