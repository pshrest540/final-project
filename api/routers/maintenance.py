import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import User, Vehicle, ScheduledMaintenance, ComponentReplacement
from api.schemas import MaintenanceTaskOut, LogServiceRequest, ComponentReplacementOut, LogReplacementRequest
from api.dependencies import get_current_user

router = APIRouter(tags=["Maintenance"])

# Default intervals in miles for each scheduled task
MAINTENANCE_TASKS: dict[str, dict] = {
    "oil_change":         {"name": "Oil Change",         "interval": 5_000},
    "tire_rotation":      {"name": "Tire Rotation",      "interval": 7_500},
    "air_filter":         {"name": "Air Filter",         "interval": 15_000},
    "cabin_air_filter":   {"name": "Cabin Air Filter",   "interval": 20_000},
    "spark_plugs":        {"name": "Spark Plugs",        "interval": 30_000},
    "brake_fluid":        {"name": "Brake Fluid",        "interval": 30_000},
    "transmission_fluid": {"name": "Transmission Fluid", "interval": 45_000},
    "coolant_flush":      {"name": "Coolant Flush",      "interval": 30_000},
}


def _status(miles_remaining: Optional[int]) -> str:
    if miles_remaining is None:
        return "unknown"
    if miles_remaining > 500:
        return "ok"
    if miles_remaining > 0:
        return "due_soon"
    return "overdue"


def _build_out(task_key: str, record: Optional[ScheduledMaintenance], current_mileage: int) -> MaintenanceTaskOut:
    meta = MAINTENANCE_TASKS[task_key]
    if record and record.last_service_mileage is not None:
        next_due  = record.last_service_mileage + record.interval_miles
        remaining = next_due - current_mileage
        return MaintenanceTaskOut(
            task_key=task_key,
            task_name=meta["name"],
            interval_miles=record.interval_miles,
            last_service_mileage=record.last_service_mileage,
            next_due_mileage=next_due,
            miles_remaining=remaining,
            status=_status(remaining),
        )
    return MaintenanceTaskOut(
        task_key=task_key,
        task_name=meta["name"],
        interval_miles=meta["interval"],
    )


def _get_owned_vehicle(vehicle_id: str, user: User, db: Session) -> Vehicle:
    v = db.query(Vehicle).filter(
        Vehicle.vehicle_id == vehicle_id,
        Vehicle.owner_id == user.user_id,
    ).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return v


@router.get("/vehicles/{vehicle_id}/maintenance", response_model=list[MaintenanceTaskOut])
def get_maintenance(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = _get_owned_vehicle(vehicle_id, current_user, db)
    records = {
        r.task_key: r
        for r in db.query(ScheduledMaintenance)
        .filter(ScheduledMaintenance.vehicle_id == vehicle_id)
        .all()
    }
    return [_build_out(key, records.get(key), vehicle.current_mileage) for key in MAINTENANCE_TASKS]


@router.post("/vehicles/{vehicle_id}/maintenance/{task_key}", response_model=MaintenanceTaskOut)
def log_service(
    vehicle_id: str,
    task_key: str,
    body: LogServiceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if task_key not in MAINTENANCE_TASKS:
        raise HTTPException(status_code=400, detail=f"Unknown maintenance task: {task_key}")
    vehicle = _get_owned_vehicle(vehicle_id, current_user, db)
    interval = body.interval_miles or MAINTENANCE_TASKS[task_key]["interval"]

    record = (
        db.query(ScheduledMaintenance)
        .filter(
            ScheduledMaintenance.vehicle_id == vehicle_id,
            ScheduledMaintenance.task_key == task_key,
        )
        .first()
    )
    if record:
        record.last_service_mileage = body.service_mileage
        record.interval_miles = interval
    else:
        record = ScheduledMaintenance(
            id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            task_key=task_key,
            last_service_mileage=body.service_mileage,
            interval_miles=interval,
        )
        db.add(record)
    db.commit()
    db.refresh(record)
    return _build_out(task_key, record, vehicle.current_mileage)


# ── Component replacements ─────────────────────────────────────────────────────

COMPONENT_NAMES: dict[str, str] = {
    "cv_joints":      "CV Joints",
    "wheel_bearings": "Wheel Bearings",
    "brakes":         "Brakes",
    "battery":        "Battery",
    "alternator":     "Alternator",
    "starter":        "Starter Motor",
    "coolant_system": "Coolant System",
    "ignition":       "Ignition",
    "fuel_system":    "Fuel System",
}


@router.get("/vehicles/{vehicle_id}/replacements", response_model=list[ComponentReplacementOut])
def get_replacements(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_vehicle(vehicle_id, current_user, db)
    records = (
        db.query(ComponentReplacement)
        .filter(ComponentReplacement.vehicle_id == vehicle_id)
        .all()
    )
    return [
        ComponentReplacementOut(
            component_key=r.component_key,
            component_name=COMPONENT_NAMES.get(r.component_key, r.component_key),
            replaced_at_mileage=r.replaced_at_mileage,
            notes=r.notes,
        )
        for r in records
    ]


@router.post("/vehicles/{vehicle_id}/replacements/{component_key}", response_model=ComponentReplacementOut)
def log_replacement(
    vehicle_id: str,
    component_key: str,
    body: LogReplacementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if component_key not in COMPONENT_NAMES:
        raise HTTPException(status_code=400, detail=f"Unknown component: {component_key}")
    _get_owned_vehicle(vehicle_id, current_user, db)

    record = (
        db.query(ComponentReplacement)
        .filter(
            ComponentReplacement.vehicle_id == vehicle_id,
            ComponentReplacement.component_key == component_key,
        )
        .first()
    )
    if record:
        record.replaced_at_mileage = body.replaced_at_mileage
        record.notes = body.notes
    else:
        record = ComponentReplacement(
            id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            component_key=component_key,
            replaced_at_mileage=body.replaced_at_mileage,
            notes=body.notes,
        )
        db.add(record)
    db.commit()
    db.refresh(record)
    return ComponentReplacementOut(
        component_key=record.component_key,
        component_name=COMPONENT_NAMES[record.component_key],
        replaced_at_mileage=record.replaced_at_mileage,
        notes=record.notes,
    )


@router.delete("/vehicles/{vehicle_id}/replacements/{component_key}", status_code=204)
def delete_replacement(
    vehicle_id: str,
    component_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_vehicle(vehicle_id, current_user, db)
    record = (
        db.query(ComponentReplacement)
        .filter(
            ComponentReplacement.vehicle_id == vehicle_id,
            ComponentReplacement.component_key == component_key,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No replacement record found")
    db.delete(record)
    db.commit()
