"""
Core prediction logic.
Builds feature vectors, runs inference, and packages results.
Kept separate from the router so it can be tested independently.
"""

import numpy as np
import pandas as pd
import os
from api.models.loader import get_models

CURRENT_YEAR = 2024

def _engineer(year: int, mileage: int) -> dict:
    """Compute derived features shared by all 3 systems."""
    vehicle_age      = CURRENT_YEAR - year
    age_x_mileage    = vehicle_age * mileage
    mileage_per_year = mileage / max(vehicle_age, 1)
    log_mileage      = np.log1p(mileage)
    return {
        "vehicle_age":      vehicle_age,
        "age_x_mileage":    age_x_mileage,
        "mileage_per_year": mileage_per_year,
        "log_mileage":      log_mileage,
    }

def _lookup_brand_scores(brand: str, model: str) -> dict:
    """Look up reliability scores from brand_model_reliability.csv."""
    BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR  = os.path.join(BASE_DIR, "data", "processed")
    brand_df  = pd.read_csv(os.path.join(DATA_DIR, "brand_model_reliability.csv"))

    row = brand_df[
        (brand_df["brand"].str.lower() == brand.lower()) &
        (brand_df["model"].str.lower() == model.lower())
    ]

    if row.empty:
        # Fallback to brand average if exact model not found
        row = brand_df[brand_df["brand"].str.lower() == brand.lower()]
        if row.empty:
            return {"elec_score": 5, "drive_score": 5, "engine_score": 5}

    return {
        "elec_score":   int(row["elec_score"].mean()),
        "drive_score":  int(row["drive_score"].mean()),
        "engine_score": int(row["engine_score"].mean()),
    }

def _predict_system(system: str, feature_row: list) -> np.ndarray:
    """Run inference for one system and return clipped scores."""
    bundle = get_models()[system]
    scores = bundle["model"].predict([feature_row])[0]
    return np.clip(scores, 5, 100)

def run_prediction(req) -> dict:
    """
    Main prediction function.
    Takes a PredictRequest, returns a dict matching PredictResponse shape.
    """
    eng   = _engineer(req.year, req.mileage)
    brand = _lookup_brand_scores(req.brand, req.model)

    # ── Drivetrain ─────────────────────────────────────────────────────────────
    dt_features = [
        req.year, req.mileage,
        req.rough_scale, req.torque_scale, req.stop_scale,
        brand["drive_score"],
        eng["vehicle_age"], eng["age_x_mileage"],
        eng["mileage_per_year"], eng["log_mileage"],
    ]
    cv, wb, brk = _predict_system("drivetrain", dt_features)
    dt_avg = round(float(np.mean([cv, wb, brk])), 2)

    # ── Electrical ─────────────────────────────────────────────────────────────
    el_features = [
        req.year, req.mileage,
        req.temp_scale, req.habit_scale, req.idle_scale,
        brand["elec_score"],
        eng["vehicle_age"], eng["age_x_mileage"],
        eng["mileage_per_year"], eng["log_mileage"],
    ]
    bat, alt, sta = _predict_system("electrical", el_features)
    el_avg = round(float(np.mean([bat, alt, sta])), 2)

    # ── Engine ─────────────────────────────────────────────────────────────────
    en_features = [
        req.year, req.mileage,
        req.temp_scale, req.idle_scale, req.habit_scale,
        brand["engine_score"],
        eng["vehicle_age"], eng["age_x_mileage"],
        eng["mileage_per_year"], eng["log_mileage"],
    ]
    coolant, ignition, fuel = _predict_system("engine", en_features)
    en_avg = round(float(np.mean([coolant, ignition, fuel])), 2)

    overall = round(float(np.mean([dt_avg, el_avg, en_avg])), 2)

    return {
        "vehicle":    f"{req.year} {req.brand} {req.model} — {req.mileage:,} miles",
        "drivetrain": {
            "cv_wellness":  round(float(cv),  2),
            "wb_wellness":  round(float(wb),  2),
            "brk_wellness": round(float(brk), 2),
            "system_avg":   dt_avg,
        },
        "electrical": {
            "bat_wellness": round(float(bat), 2),
            "alt_wellness": round(float(alt), 2),
            "sta_wellness": round(float(sta), 2),
            "system_avg":   el_avg,
        },
        "engine": {
            "coolant_wellness":  round(float(coolant),  2),
            "ignition_wellness": round(float(ignition), 2),
            "fuel_wellness":     round(float(fuel),     2),
            "system_avg":        en_avg,
        },
        "overall_avg": overall,
    }
