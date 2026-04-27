import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import WellnessPrediction
from api.schemas import PredictRequest, PredictResponse
from api.services.predictor import run_prediction

router = APIRouter(prefix="/predict", tags=["Predict"])


@router.post("", response_model=PredictResponse)
def predict(req: PredictRequest, db: Session = Depends(get_db)):
    try:
        result = run_prediction(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if req.vehicle_id:
        try:
            db.add(WellnessPrediction(
                prediction_id=str(uuid.uuid4()),
                vehicle_id=req.vehicle_id,
                overall_score=result["overall_avg"],
                engine_score=result["engine"]["system_avg"],
                drivetrain_score=result["drivetrain"]["system_avg"],
                electrical_score=result["electrical"]["system_avg"],
            ))
            db.commit()
        except Exception as e:
            print(f"Warning: could not save prediction: {e}")
            db.rollback()

    return result
