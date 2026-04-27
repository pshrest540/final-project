"""
Loads all 3 .joblib model bundles once at startup and stores them
in a module-level dict so every router can import and reuse them
without re-loading from disk on each request.
"""

import os
import joblib

_models: dict = {}


def _limit_prediction_workers(bundle: dict) -> dict:
    """
    Keep hosted inference from trying to use every available CPU.
    The saved bundles contain MultiOutputRegressor -> RandomForestRegressor.
    """
    model = bundle.get("model")
    if hasattr(model, "n_jobs"):
        model.n_jobs = 1
    for estimator in getattr(model, "estimators_", []):
        if hasattr(estimator, "n_jobs"):
            estimator.n_jobs = 1
    return bundle

def get_models() -> dict:
    """Return the loaded models dict. Call after startup."""
    return _models

def load_all_models():
    """Called once at FastAPI startup. Loads all 3 system models."""
    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  
    MODELS_DIR = os.path.join(BASE_DIR, "models")

    for system in ("drivetrain", "electrical", "engine"):
        path = os.path.join(MODELS_DIR, f"{system}_model.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model not found: {path}\n"
                f"Run `python train/train_models.py` first to generate model files."
            )
        _models[system] = _limit_prediction_workers(joblib.load(path))

    print(f"[startup] Loaded {len(_models)} models: {list(_models.keys())}")
