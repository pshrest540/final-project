import os
import subprocess
import sys
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from api.schemas import RetrainResponse
from api.models.loader import load_all_models
from api.db.models import User
from api.dependencies import require_admin

router = APIRouter(prefix="/retrain", tags=["Retrain"])


def _run_training():
    BASE_DIR     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    train_script = os.path.join(BASE_DIR, "train", "train_models.py")

    result = subprocess.run(
        [sys.executable, train_script],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Training failed:\n{result.stderr}")

    load_all_models()
    return result.stdout


@router.post("", response_model=RetrainResponse)
def retrain(
    background_tasks: BackgroundTasks,
    _admin: User = Depends(require_admin),
):
    try:
        background_tasks.add_task(_run_training)
        return RetrainResponse(
            status="accepted",
            message="Retraining started in the background. Models will reload automatically when complete.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
