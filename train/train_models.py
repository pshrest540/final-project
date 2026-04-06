import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))   
ROOT_DIR   = os.path.dirname(BASE_DIR)                    
DATA_DIR   = os.path.join(ROOT_DIR, "data", "processed")  
MODELS_DIR = os.path.join(ROOT_DIR, "models")             

os.makedirs(MODELS_DIR, exist_ok=True)

print("Loading data from:", DATA_DIR)

drivetrain  = pd.read_csv(os.path.join(DATA_DIR, "drivetrain_physics.csv"))
electrical  = pd.read_csv(os.path.join(DATA_DIR, "electrical_physics.csv"))
engine      = pd.read_csv(os.path.join(DATA_DIR, "engine_physics.csv"))
brand_model = pd.read_csv(os.path.join(DATA_DIR, "brand_model_reliability.csv"))

print(f"  drivetrain_physics.csv  : {drivetrain.shape}")
print(f"  electrical_physics.csv  : {electrical.shape}")
print(f"  engine_physics.csv      : {engine.shape}")
print(f"  brand_model_reliability : {brand_model.shape}")

SYSTEMS = {
    "drivetrain": {
        "df":        drivetrain,
        "features":  ["year", "mileage", "rough_scale", "torque_scale", "stop_scale", "drive_score"],
        "targets":   ["cv_wellness", "wb_wellness", "brk_wellness"],
        "brand_col": "drive_score",
    },
    "electrical": {
        "df":        electrical,
        "features":  ["year", "mileage", "temp_scale", "habit_scale", "idle_scale", "elec_score"],
        "targets":   ["bat_wellness", "alt_wellness", "sta_wellness"],
        "brand_col": "elec_score",
    },
    "engine": {
        "df":        engine,
        "features":  ["year", "mileage", "temp_scale", "idle_scale", "habit_scale", "engine_score"],
        "targets":   ["coolant_wellness", "ignition_wellness", "fuel_wellness"],
        "brand_col": "engine_score",
    },
}

ENGINEERED_COLS = ["vehicle_age", "age_x_mileage", "mileage_per_year", "log_mileage"]

def engineer_features(df):
    df = df.copy()
    current_year = 2024
    df["vehicle_age"]      = current_year - df["year"]
    df["age_x_mileage"]    = df["vehicle_age"] * df["mileage"]        
    df["mileage_per_year"] = df["mileage"] / df["vehicle_age"].clip(lower=1)
    df["log_mileage"]      = np.log1p(df["mileage"])
    return df

def merge_brand_scores(df, brand_col):
  
    scores = brand_model[brand_col].values
    np.random.seed(42)
    df = df.copy()
    df[brand_col] = np.random.choice(scores, size=len(df), replace=True)
    return df

results = {}

for system_name, config in SYSTEMS.items():
    print(f"\n{'='*55}")
    print(f"  Training: {system_name.upper()}")
    print(f"{'='*55}")

    df        = config["df"].copy()
    targets   = config["targets"]
    brand_col = config["brand_col"]

    df = merge_brand_scores(df, brand_col)
    df = engineer_features(df)

    all_features = config["features"] + ENGINEERED_COLS

    X = df[all_features]
    y = df[targets]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("model",  MultiOutputRegressor(
            RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_leaf=4,
                n_jobs=-1,
                random_state=42
            )
        ))
    ])

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"\n  {'Target':<25} {'MAE':>8} {'R2':>8}")
    print(f"  {'-'*43}")

    per_target = {}
    for i, target in enumerate(targets):
        mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
        r2  = r2_score(y_test.iloc[:, i], y_pred[:, i])
        print(f"  {target:<25} {mae:>8.2f} {r2:>8.3f}")
        per_target[target] = {"MAE": round(mae, 2), "R2": round(r2, 3)}

    overall_mae = mean_absolute_error(y_test, y_pred)
    overall_r2  = r2_score(y_test, y_pred)
    print(f"\n  Overall MAE: {overall_mae:.2f}  |  Overall R2: {overall_r2:.3f}")

    model_path = os.path.join(MODELS_DIR, f"{system_name}_model.joblib")
    joblib.dump({
        "model":       model,        
        "features":    all_features, 
        "targets":     targets,     
        "brand_col":   brand_col,    
        "overall_mae": round(overall_mae, 2),
        "overall_r2":  round(overall_r2, 3),
        "per_target":  per_target,
    }, model_path)

    print(f"  Saved -> {model_path}")
    results[system_name] = per_target

print(f"\n{'='*55}")
print("  TRAINING COMPLETE")
print(f"{'='*55}")
for system, target_results in results.items():
    print(f"\n  {system.upper()}")
    for target, metrics in target_results.items():
        print(f"    {target:<25} MAE={metrics['MAE']:>6.2f}  R2={metrics['R2']:>6.3f}")

print(f"\n  Models saved to: {MODELS_DIR}")
