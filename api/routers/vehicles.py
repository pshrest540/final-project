import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import User, Vehicle, WellnessPrediction
from api.schemas import VehicleCreate, VehicleOut, PredictionOut, VehicleMileageUpdate
from api.dependencies import get_current_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def _get_owned_vehicle(vehicle_id: str, current_user: User, db: Session) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your vehicle")
    return vehicle


@router.get("", response_model=list[VehicleOut])
def list_vehicles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Vehicle).filter(Vehicle.owner_id == current_user.user_id).all()


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    body: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = Vehicle(
        vehicle_id=str(uuid.uuid4()),
        owner_id=current_user.user_id,
        brand=body.brand,
        model=body.model,
        year=body.year,
        current_mileage=body.current_mileage,
        vin=body.vin,
        customer_name=body.customer_name,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_vehicle(vehicle_id, current_user, db)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = _get_owned_vehicle(vehicle_id, current_user, db)
    db.delete(vehicle)
    db.commit()
    return None


@router.patch("/{vehicle_id}/mileage", response_model=VehicleOut)
def update_mileage(
    vehicle_id: str,
    body: VehicleMileageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = _get_owned_vehicle(vehicle_id, current_user, db)
    if body.current_mileage < vehicle.current_mileage:
        raise HTTPException(status_code=400, detail="Mileage cannot be decreased")
    vehicle.current_mileage = body.current_mileage
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/{vehicle_id}/predictions", response_model=list[PredictionOut])
def list_predictions(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_vehicle(vehicle_id, current_user, db)
    return (
        db.query(WellnessPrediction)
        .filter(WellnessPrediction.vehicle_id == vehicle_id)
        .order_by(WellnessPrediction.calculated_at.desc())
        .all()
    )


@router.delete("/{vehicle_id}/predictions/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(
    vehicle_id: str,
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_vehicle(vehicle_id, current_user, db)
    prediction = db.query(WellnessPrediction).filter(
        WellnessPrediction.vehicle_id == vehicle_id,
        WellnessPrediction.prediction_id == prediction_id,
    ).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    db.delete(prediction)
    db.commit()
    return None
