import numpy as np
import pandas as pd
import os
from typing import Optional
from datetime import datetime
from api.models.loader import get_models

CURRENT_YEAR = datetime.now().year

# Maps each component key → (system name, output index)
COMPONENT_MAP: dict[str, tuple[str, int]] = {
    "cv_joints":      ("drivetrain", 0),
    "wheel_bearings": ("drivetrain", 1),
    "brakes":         ("drivetrain", 2),
    "battery":        ("electrical", 0),
    "alternator":     ("electrical", 1),
    "starter":        ("electrical", 2),
    "coolant_system": ("engine",     0),
    "ignition":       ("engine",     1),
    "fuel_system":    ("engine",     2),
}


def _engineer(year: int, mileage: int) -> dict:
    vehicle_age      = max(CURRENT_YEAR - year, 0)
    age_x_mileage    = vehicle_age * mileage
    mileage_per_year = mileage / max(vehicle_age, 1)
    log_mileage      = np.log1p(mileage)
    return {
        "vehicle_age": vehicle_age,
        "age_x_mileage": age_x_mileage,
        "mileage_per_year": mileage_per_year,
        "log_mileage": log_mileage,
    }


def _lookup_brand_scores(brand: str, model: str) -> dict:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
    brand_df = pd.read_csv(os.path.join(DATA_DIR, "brand_model_reliability.csv"))

    row = brand_df[
        (brand_df["brand"].str.lower() == brand.lower()) &
        (brand_df["model"].str.lower() == model.lower())
    ]

    if row.empty:
        row = brand_df[brand_df["brand"].str.lower() == brand.lower()]
        if row.empty:
            return {"elec_score": 5, "drive_score": 5, "engine_score": 5}

    return {
        "elec_score":   int(row["elec_score"].mean()),
        "drive_score":  int(row["drive_score"].mean()),
        "engine_score": int(row["engine_score"].mean()),
    }


def _predict_system(system: str, feature_row: list) -> np.ndarray:
    bundle   = get_models()[system]
    features = bundle.get("features")
    X        = pd.DataFrame([feature_row], columns=features) if features else [feature_row]
    scores   = bundle["model"].predict(X)[0]
    return np.clip(scores, 5, 100)


def _brand_multiplier(score: int, strength: float = 0.04) -> float:
    return 1.0 + ((score - 5) * strength)


def _apply_brand_adjustment(scores, brand_score: int, strength: float = 0.04) -> np.ndarray:
    mult     = _brand_multiplier(brand_score, strength)
    adjusted = np.array(scores, dtype=float) * mult
    return np.clip(adjusted, 5, 100)


def _build_system_features(system: str, mileage: int, year: int, req) -> list:
    """Build the feature vector for a system using the given mileage/year."""
    eng = _engineer(year, mileage)
    base = [year, mileage]
    derived = [eng["vehicle_age"], eng["age_x_mileage"], eng["mileage_per_year"], eng["log_mileage"]]
    if system == "drivetrain":
        stress = [req.rough_scale, req.torque_scale, req.stop_scale]
    elif system == "electrical":
        stress = [req.temp_scale, req.habit_scale, req.idle_scale]
    else:  # engine
        stress = [req.temp_scale, req.idle_scale, req.habit_scale]
    return base + stress + derived


def run_prediction(req, component_overrides: Optional[dict] = None) -> dict:
    """
    component_overrides: {component_key: effective_mileage}
    For each replaced component, the model is re-run with the effective mileage
    (miles since the replacement) and CURRENT_YEAR (new part), and only that
    component's index is taken from the result.
    """
    component_overrides = component_overrides or {}
    brand = _lookup_brand_scores(req.brand, req.model)

    # ── Original predictions using full vehicle mileage ───────────────────────
    dt_feat = _build_system_features("drivetrain", req.mileage, req.year, req)
    cv, wb, brk = _predict_system("drivetrain", dt_feat)
    cv, wb, brk = _apply_brand_adjustment([cv, wb, brk], brand["drive_score"])

    el_feat = _build_system_features("electrical", req.mileage, req.year, req)
    bat, alt, sta = _predict_system("electrical", el_feat)
    bat, alt, sta = _apply_brand_adjustment([bat, alt, sta], brand["elec_score"])

    en_feat = _build_system_features("engine", req.mileage, req.year, req)
    coolant, ignition, fuel = _predict_system("engine", en_feat)
    coolant, ignition, fuel = _apply_brand_adjustment([coolant, ignition, fuel], brand["engine_score"])

    # ── Per-component overrides for replaced parts ────────────────────────────
    # Re-run only the affected system with effective mileage; take only that
    # component's index from the result so other components are unaffected.
    for comp_key, eff_mileage in component_overrides.items():
        if comp_key not in COMPONENT_MAP:
            continue
        system, idx = COMPONENT_MAP[comp_key]
        eff_mileage  = max(int(eff_mileage), 0)

        # Treat the new part as if it were installed in CURRENT_YEAR with eff_mileage miles
        eff_feat   = _build_system_features(system, eff_mileage, CURRENT_YEAR, req)
        eff_scores = _predict_system(system, eff_feat)

        if system == "drivetrain":
            eff_scores = _apply_brand_adjustment(eff_scores, brand["drive_score"])
            if idx == 0:   cv  = eff_scores[0]
            elif idx == 1: wb  = eff_scores[1]
            else:          brk = eff_scores[2]
        elif system == "electrical":
            eff_scores = _apply_brand_adjustment(eff_scores, brand["elec_score"])
            if idx == 0:   bat = eff_scores[0]
            elif idx == 1: alt = eff_scores[1]
            else:          sta = eff_scores[2]
        else:  # engine
            eff_scores = _apply_brand_adjustment(eff_scores, brand["engine_score"])
            if idx == 0:   coolant  = eff_scores[0]
            elif idx == 1: ignition = eff_scores[1]
            else:          fuel     = eff_scores[2]

    dt_avg  = round(float(np.mean([cv, wb, brk])), 2)
    el_avg  = round(float(np.mean([bat, alt, sta])), 2)
    en_avg  = round(float(np.mean([coolant, ignition, fuel])), 2)
    overall = round(float(np.mean([dt_avg, el_avg, en_avg])), 2)

    return {
        "vehicle": f"{req.year} {req.brand} {req.model} — {req.mileage:,} miles",
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
            "coolant_wellness":   round(float(coolant),  2),
            "ignition_wellness":  round(float(ignition), 2),
            "fuel_wellness":      round(float(fuel),     2),
            "system_avg":         en_avg,
        },
        "overall_avg": overall,
    }
