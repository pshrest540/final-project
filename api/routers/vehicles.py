import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import BusinessCustomerLink, ServiceProposal, User, Vehicle, WellnessPrediction
from api.schemas import (
    PredictionOut,
    VehicleCreate,
    VehicleMileageUpdate,
    VehicleOut,
    VehicleShareUpdate,
)
from api.dependencies import get_current_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def _owner_name(owner: Optional[User]) -> Optional[str]:
    if not owner:
        return None
    return owner.full_name or owner.business_name or owner.email


def _vehicle_out(vehicle: Vehicle, is_shared: bool = False) -> dict:
    owner = vehicle.owner
    return {
        "vehicle_id": vehicle.vehicle_id,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "year": vehicle.year,
        "current_mileage": vehicle.current_mileage,
        "vin": vehicle.vin,
        "customer_name": vehicle.customer_name,
        "share_enabled": bool(vehicle.share_enabled),
        "is_shared": is_shared,
        "owner_email": owner.email if owner else None,
        "owner_name": _owner_name(owner),
        "added_on": vehicle.added_on,
    }


def _get_owned_vehicle(vehicle_id: str, current_user: User, db: Session) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your vehicle")
    return vehicle


def _is_linked_shared_vehicle(vehicle: Vehicle, current_user: User, db: Session) -> bool:
    if current_user.account_type != "business":
        return False
    if vehicle.owner_id == current_user.user_id or not vehicle.share_enabled:
        return False
    link = (
        db.query(BusinessCustomerLink)
        .filter(
            BusinessCustomerLink.business_user_id == current_user.user_id,
            BusinessCustomerLink.customer_user_id == vehicle.owner_id,
        )
        .first()
    )
    return link is not None


def _get_accessible_vehicle(vehicle_id: str, current_user: User, db: Session) -> tuple[Vehicle, bool]:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id == current_user.user_id:
        return vehicle, False
    if _is_linked_shared_vehicle(vehicle, current_user, db):
        return vehicle, True
    raise HTTPException(status_code=404, detail="Vehicle not found")


@router.get("", response_model=list[VehicleOut])
def list_vehicles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.owner_id == current_user.user_id)
        .order_by(Vehicle.added_on.desc())
        .all()
    )
    out = [_vehicle_out(vehicle, is_shared=False) for vehicle in vehicles]

    if current_user.account_type == "business":
        shared = (
            db.query(Vehicle)
            .join(BusinessCustomerLink, BusinessCustomerLink.customer_user_id == Vehicle.owner_id)
            .filter(
                BusinessCustomerLink.business_user_id == current_user.user_id,
                Vehicle.share_enabled.is_(True),
            )
            .order_by(Vehicle.added_on.desc())
            .all()
        )
        out.extend(_vehicle_out(vehicle, is_shared=True) for vehicle in shared)

    return out


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    body: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.account_type == "business":
        raise HTTPException(status_code=403, detail="Business accounts cannot add vehicles directly")
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
    return _vehicle_out(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle, is_shared = _get_accessible_vehicle(vehicle_id, current_user, db)
    return _vehicle_out(vehicle, is_shared=is_shared)


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
    vehicle.current_mileage = body.current_mileage
    db.commit()
    db.refresh(vehicle)
    return _vehicle_out(vehicle)


@router.patch("/{vehicle_id}/sharing", response_model=VehicleOut)
def update_vehicle_sharing(
    vehicle_id: str,
    body: VehicleShareUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = _get_owned_vehicle(vehicle_id, current_user, db)
    vehicle.share_enabled = body.share_enabled
    if not body.share_enabled:
        # Cancel all pending proposals for this vehicle so nothing lingers after sharing is revoked
        (
            db.query(ServiceProposal)
            .filter(
                ServiceProposal.vehicle_id == vehicle_id,
                ServiceProposal.status == "pending",
            )
            .update({"status": "cancelled"}, synchronize_session=False)
        )
    db.commit()
    db.refresh(vehicle)
    return _vehicle_out(vehicle)


@router.get("/{vehicle_id}/predictions", response_model=list[PredictionOut])
def list_predictions(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_accessible_vehicle(vehicle_id, current_user, db)
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
