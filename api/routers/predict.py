import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import Vehicle, WellnessPrediction, ComponentReplacement
from api.schemas import PredictRequest, PredictResponse
from api.services.auth import decode_access_token
from api.services.predictor import run_prediction

router = APIRouter(prefix="/predict", tags=["Predict"])

_optional_bearer = HTTPBearer(auto_error=False)


@router.post("", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
):
    component_overrides: dict = {}
    vehicle = None

    if req.vehicle_id:
        # Require auth and ownership before attaching a prediction to a vehicle
        user_id = decode_access_token(credentials.credentials) if credentials else None
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required to save predictions")
        vehicle = db.query(Vehicle).filter(
            Vehicle.vehicle_id == req.vehicle_id,
            Vehicle.owner_id == user_id,
        ).first()
        if not vehicle:
            raise HTTPException(status_code=403, detail="Vehicle not found or not yours")

        # Build component overrides: effective mileage = miles since replacement
        for r in db.query(ComponentReplacement).filter(
            ComponentReplacement.vehicle_id == req.vehicle_id
        ).all():
            component_overrides[r.component_key] = max(
                vehicle.current_mileage - r.replaced_at_mileage, 0
            )

    try:
        result = run_prediction(req, component_overrides or None)
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed. Please try again.")

    result["replacements_applied"] = list(component_overrides.keys())

    if vehicle:
        try:
            db.add(WellnessPrediction(
                prediction_id=str(uuid.uuid4()),
                vehicle_id=req.vehicle_id,
                overall_score=result["overall_avg"],
                engine_score=result["engine"]["system_avg"],
                drivetrain_score=result["drivetrain"]["system_avg"],
                electrical_score=result["electrical"]["system_avg"],
                cv_wellness=result["drivetrain"]["cv_wellness"],
                wb_wellness=result["drivetrain"]["wb_wellness"],
                brk_wellness=result["drivetrain"]["brk_wellness"],
                bat_wellness=result["electrical"]["bat_wellness"],
                alt_wellness=result["electrical"]["alt_wellness"],
                sta_wellness=result["electrical"]["sta_wellness"],
                coolant_wellness=result["engine"]["coolant_wellness"],
                ignition_wellness=result["engine"]["ignition_wellness"],
                fuel_wellness=result["engine"]["fuel_wellness"],
            ))
            db.commit()
        except Exception as e:
            print(f"Warning: could not save prediction: {e}")
            db.rollback()

    return result
