from fastapi import APIRouter, HTTPException
from api.schemas import PredictRequest, PredictResponse
from api.services.predictor import run_prediction

router = APIRouter(prefix="/predict", tags=["Predict"])

@router.post("", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    Predict health scores for all 3 vehicle systems.

    Returns scores (0–100) for:
    - **Engine**: coolant, ignition, fuel
    - **Drivetrain**: CV joints, wheel bearings, brakes
    - **Electrical**: battery, alternator, starter
    """
    try:
        return run_prediction(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
