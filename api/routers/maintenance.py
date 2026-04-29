import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import BusinessCustomerLink, User, Vehicle, ScheduledMaintenance, ComponentReplacement, ServiceLog
from api.schemas import (
    MaintenanceTaskOut, LogServiceRequest,
    ComponentReplacementOut, LogReplacementRequest,
    ServiceLogCreate, ServiceLogOut,
)
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


def _get_readable_vehicle(vehicle_id: str, user: User, db: Session) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id == user.user_id:
        return vehicle
    if user.account_type == "business" and vehicle.share_enabled:
        link = (
            db.query(BusinessCustomerLink)
            .filter(
                BusinessCustomerLink.business_user_id == user.user_id,
                BusinessCustomerLink.customer_user_id == vehicle.owner_id,
            )
            .first()
        )
        if link:
            return vehicle
    raise HTTPException(status_code=404, detail="Vehicle not found")


@router.get("/vehicles/{vehicle_id}/maintenance", response_model=list[MaintenanceTaskOut])
def get_maintenance(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = _get_readable_vehicle(vehicle_id, current_user, db)
    records = {
        r.task_key: r
        for r in db.query(ScheduledMaintenance)
        .filter(ScheduledMaintenance.vehicle_id == vehicle_id)
        .all()
    }
    latest_logs: dict[str, ServiceLog] = {}
    for entry in (
        db.query(ServiceLog)
        .filter(ServiceLog.vehicle_id == vehicle_id, ServiceLog.entry_type == "maintenance")
        .order_by(ServiceLog.service_mileage.desc(), ServiceLog.logged_at.desc())
        .all()
    ):
        latest_logs.setdefault(entry.task_key, entry)

    tasks = []
    for key in MAINTENANCE_TASKS:
        latest = latest_logs.get(key)
        if latest:
            interval = records.get(key).interval_miles if records.get(key) else MAINTENANCE_TASKS[key]["interval"]
            next_due = latest.service_mileage + interval
            remaining = next_due - vehicle.current_mileage
            tasks.append(MaintenanceTaskOut(
                task_key=key,
                task_name=MAINTENANCE_TASKS[key]["name"],
                interval_miles=interval,
                last_service_mileage=latest.service_mileage,
                next_due_mileage=next_due,
                miles_remaining=remaining,
                status=_status(remaining),
            ))
        else:
            tasks.append(_build_out(key, None, vehicle.current_mileage))
    return tasks


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
    _get_readable_vehicle(vehicle_id, current_user, db)
    latest_logs: dict[str, ServiceLog] = {}
    for entry in (
        db.query(ServiceLog)
        .filter(ServiceLog.vehicle_id == vehicle_id, ServiceLog.entry_type == "replacement")
        .order_by(ServiceLog.service_mileage.desc(), ServiceLog.logged_at.desc())
        .all()
    ):
        latest_logs.setdefault(entry.task_key, entry)

    return [
        ComponentReplacementOut(
            component_key=task_key,
            component_name=COMPONENT_NAMES.get(task_key, task_key),
            replaced_at_mileage=entry.service_mileage,
            notes=entry.notes,
        )
        for task_key, entry in latest_logs.items()
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


# ── Service log ───────────────────────────────────────────────────────────────

ALL_TASK_NAMES: dict[str, str] = {
    **{k: v["name"] for k, v in MAINTENANCE_TASKS.items()},
    **COMPONENT_NAMES,
}


def _log_out(entry: ServiceLog) -> ServiceLogOut:
    return ServiceLogOut(
        id=entry.id,
        vehicle_id=entry.vehicle_id,
        entry_type=entry.entry_type,
        task_key=entry.task_key,
        task_name=ALL_TASK_NAMES.get(entry.task_key, entry.task_key),
        service_mileage=entry.service_mileage,
        replacement_info=entry.replacement_info,
        shop_name=entry.shop_name,
        technician_name=entry.technician_name,
        cost=entry.cost,
        notes=entry.notes,
        logged_at=entry.logged_at,
    )


def _refresh_current_state_from_logs(vehicle_id: str, entry_type: str, task_key: str, db: Session) -> None:
    latest = (
        db.query(ServiceLog)
        .filter(
            ServiceLog.vehicle_id == vehicle_id,
            ServiceLog.entry_type == entry_type,
            ServiceLog.task_key == task_key,
        )
        .order_by(ServiceLog.service_mileage.desc(), ServiceLog.logged_at.desc())
        .first()
    )

    if entry_type == "maintenance":
        record = (
            db.query(ScheduledMaintenance)
            .filter(
                ScheduledMaintenance.vehicle_id == vehicle_id,
                ScheduledMaintenance.task_key == task_key,
            )
            .first()
        )
        if latest:
            interval = MAINTENANCE_TASKS[task_key]["interval"]
            if record:
                record.last_service_mileage = latest.service_mileage
                record.interval_miles = interval
            else:
                db.add(ScheduledMaintenance(
                    id=str(uuid.uuid4()),
                    vehicle_id=vehicle_id,
                    task_key=task_key,
                    last_service_mileage=latest.service_mileage,
                    interval_miles=interval,
                ))
        elif record:
            db.delete(record)

    elif entry_type == "replacement":
        record = (
            db.query(ComponentReplacement)
            .filter(
                ComponentReplacement.vehicle_id == vehicle_id,
                ComponentReplacement.component_key == task_key,
            )
            .first()
        )
        if latest:
            if record:
                record.replaced_at_mileage = latest.service_mileage
                record.notes = latest.notes
            else:
                db.add(ComponentReplacement(
                    id=str(uuid.uuid4()),
                    vehicle_id=vehicle_id,
                    component_key=task_key,
                    replaced_at_mileage=latest.service_mileage,
                    notes=latest.notes,
                ))
        elif record:
            db.delete(record)


@router.get("/vehicles/{vehicle_id}/service-log", response_model=list[ServiceLogOut])
def get_service_log(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_readable_vehicle(vehicle_id, current_user, db)
    entries = (
        db.query(ServiceLog)
        .filter(ServiceLog.vehicle_id == vehicle_id)
        .order_by(ServiceLog.logged_at.desc())
        .all()
    )
    return [_log_out(e) for e in entries]


@router.post("/vehicles/{vehicle_id}/service-log", response_model=ServiceLogOut, status_code=status.HTTP_201_CREATED)
def create_service_log(
    vehicle_id: str,
    body: ServiceLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.entry_type == "maintenance":
        if body.task_key not in MAINTENANCE_TASKS:
            raise HTTPException(status_code=400, detail=f"Unknown maintenance task: {body.task_key}")
    elif body.entry_type == "replacement":
        if body.task_key not in COMPONENT_NAMES:
            raise HTTPException(status_code=400, detail=f"Unknown component: {body.task_key}")
    else:
        raise HTTPException(status_code=400, detail="entry_type must be 'maintenance' or 'replacement'")

    vehicle = _get_owned_vehicle(vehicle_id, current_user, db)
    shop_name = current_user.business_name if current_user.account_type == "business" else None

    # Write full history entry
    entry = ServiceLog(
        id=str(uuid.uuid4()),
        vehicle_id=vehicle_id,
        entry_type=body.entry_type,
        task_key=body.task_key,
        service_mileage=body.service_mileage,
        replacement_info=body.replacement_info,
        shop_name=shop_name,
        technician_name=body.technician_name,
        cost=body.cost,
        notes=body.notes,
        logged_by_user_id=current_user.user_id,
    )
    db.add(entry)

    # Also update the current-state table so the dashboard display stays accurate
    if body.entry_type == "maintenance":
        interval = MAINTENANCE_TASKS[body.task_key]["interval"]
        record = (
            db.query(ScheduledMaintenance)
            .filter(
                ScheduledMaintenance.vehicle_id == vehicle_id,
                ScheduledMaintenance.task_key == body.task_key,
            )
            .first()
        )
        if record:
            record.last_service_mileage = body.service_mileage
        else:
            db.add(ScheduledMaintenance(
                id=str(uuid.uuid4()),
                vehicle_id=vehicle_id,
                task_key=body.task_key,
                last_service_mileage=body.service_mileage,
                interval_miles=interval,
            ))
    else:
        record = (
            db.query(ComponentReplacement)
            .filter(
                ComponentReplacement.vehicle_id == vehicle_id,
                ComponentReplacement.component_key == body.task_key,
            )
            .first()
        )
        if record:
            record.replaced_at_mileage = body.service_mileage
            record.notes = body.notes
        else:
            db.add(ComponentReplacement(
                id=str(uuid.uuid4()),
                vehicle_id=vehicle_id,
                component_key=body.task_key,
                replaced_at_mileage=body.service_mileage,
                notes=body.notes,
            ))

    db.commit()
    db.refresh(entry)
    return _log_out(entry)


@router.delete("/vehicles/{vehicle_id}/service-log/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_log(
    vehicle_id: str,
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_vehicle(vehicle_id, current_user, db)
    entry = (
        db.query(ServiceLog)
        .filter(ServiceLog.id == log_id, ServiceLog.vehicle_id == vehicle_id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    entry_type = entry.entry_type
    task_key = entry.task_key
    db.delete(entry)
    db.flush()
    _refresh_current_state_from_logs(vehicle_id, entry_type, task_key, db)
    db.commit()
