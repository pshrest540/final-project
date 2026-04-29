import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import (
    BusinessCustomerLink, ComponentReplacement, ScheduledMaintenance,
    ServiceLog, ServiceProposal, User, Vehicle,
)
from api.schemas import ServiceProposalCreate, ServiceProposalOut
from api.dependencies import get_current_user

router = APIRouter(prefix="/sharing/proposals", tags=["Proposals"])

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


def _task_name(proposal_type: str, task_key: str) -> str:
    if proposal_type == "maintenance":
        return MAINTENANCE_TASKS.get(task_key, {}).get("name", task_key)
    return COMPONENT_NAMES.get(task_key, task_key)


def _proposal_out(p: ServiceProposal, db: Session) -> dict:
    business = db.query(User).filter(User.user_id == p.business_user_id).first()
    vehicle  = db.query(Vehicle).filter(Vehicle.vehicle_id == p.vehicle_id).first()
    biz_name  = (business.business_name or business.full_name or business.email) if business else ""
    v_label   = f"{vehicle.year} {vehicle.brand} {vehicle.model}" if vehicle else p.vehicle_id
    return {
        "id":               p.id,
        "business_user_id": p.business_user_id,
        "customer_user_id": p.customer_user_id,
        "vehicle_id":       p.vehicle_id,
        "proposal_type":    p.proposal_type,
        "task_key":         p.task_key,
        "task_name":        _task_name(p.proposal_type, p.task_key),
        "service_mileage":  p.service_mileage,
        "replacement_info": p.replacement_info,
        "technician_name":  p.technician_name,
        "cost":             p.cost,
        "notes":            p.notes,
        "status":           p.status,
        "created_at":       p.created_at,
        "resolved_at":      p.resolved_at,
        "business_name":    biz_name,
        "vehicle_label":    v_label,
    }


def _require_linked_vehicle(vehicle_id: str, business: User, db: Session) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if not vehicle.share_enabled:
        raise HTTPException(status_code=403, detail="Customer has not enabled sharing for this vehicle")
    link = (
        db.query(BusinessCustomerLink)
        .filter(
            BusinessCustomerLink.business_user_id == business.user_id,
            BusinessCustomerLink.customer_user_id == vehicle.owner_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=403, detail="Not linked to this customer")
    return vehicle


@router.post("", response_model=ServiceProposalOut, status_code=status.HTTP_201_CREATED)
def create_proposal(
    body: ServiceProposalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.account_type != "business":
        raise HTTPException(status_code=403, detail="Business account required")

    if body.proposal_type == "maintenance":
        if body.task_key not in MAINTENANCE_TASKS:
            raise HTTPException(status_code=400, detail=f"Unknown maintenance task: {body.task_key}")
    elif body.proposal_type == "replacement":
        if body.task_key not in COMPONENT_NAMES:
            raise HTTPException(status_code=400, detail=f"Unknown component: {body.task_key}")
    else:
        raise HTTPException(status_code=400, detail="proposal_type must be 'maintenance' or 'replacement'")

    vehicle = _require_linked_vehicle(body.vehicle_id, current_user, db)

    existing = (
        db.query(ServiceProposal)
        .filter(
            ServiceProposal.vehicle_id == body.vehicle_id,
            ServiceProposal.proposal_type == body.proposal_type,
            ServiceProposal.task_key == body.task_key,
            ServiceProposal.status == "pending",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="A pending proposal for this service already exists")

    proposal = ServiceProposal(
        id=str(uuid.uuid4()),
        business_user_id=current_user.user_id,
        customer_user_id=vehicle.owner_id,
        vehicle_id=vehicle.vehicle_id,
        proposal_type=body.proposal_type,
        task_key=body.task_key,
        service_mileage=body.service_mileage,
        replacement_info=body.replacement_info,
        technician_name=body.technician_name,
        cost=body.cost,
        notes=body.notes,
        status="pending",
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return _proposal_out(proposal, db)


@router.get("/incoming", response_model=list[ServiceProposalOut])
def get_incoming(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proposals = (
        db.query(ServiceProposal)
        .filter(ServiceProposal.customer_user_id == current_user.user_id)
        .order_by(ServiceProposal.created_at.desc())
        .all()
    )
    return [_proposal_out(p, db) for p in proposals]


@router.get("/outgoing", response_model=list[ServiceProposalOut])
def get_outgoing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.account_type != "business":
        raise HTTPException(status_code=403, detail="Business account required")
    proposals = (
        db.query(ServiceProposal)
        .filter(ServiceProposal.business_user_id == current_user.user_id)
        .order_by(ServiceProposal.created_at.desc())
        .all()
    )
    return [_proposal_out(p, db) for p in proposals]


@router.patch("/{proposal_id}/accept", response_model=ServiceProposalOut)
def accept_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proposal = db.query(ServiceProposal).filter(ServiceProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.customer_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your proposal")
    if proposal.status != "pending":
        raise HTTPException(status_code=400, detail="Proposal is no longer pending")

    _vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == proposal.vehicle_id).first()
    if not _vehicle or not _vehicle.share_enabled:
        raise HTTPException(status_code=403, detail="Sharing is no longer enabled for this vehicle")

    if proposal.proposal_type == "maintenance":
        interval = MAINTENANCE_TASKS[proposal.task_key]["interval"]
        record = (
            db.query(ScheduledMaintenance)
            .filter(
                ScheduledMaintenance.vehicle_id == proposal.vehicle_id,
                ScheduledMaintenance.task_key == proposal.task_key,
            )
            .first()
        )
        if record:
            record.last_service_mileage = proposal.service_mileage
            record.interval_miles = interval
        else:
            db.add(ScheduledMaintenance(
                id=str(uuid.uuid4()),
                vehicle_id=proposal.vehicle_id,
                task_key=proposal.task_key,
                last_service_mileage=proposal.service_mileage,
                interval_miles=interval,
            ))

    elif proposal.proposal_type == "replacement":
        record = (
            db.query(ComponentReplacement)
            .filter(
                ComponentReplacement.vehicle_id == proposal.vehicle_id,
                ComponentReplacement.component_key == proposal.task_key,
            )
            .first()
        )
        if record:
            record.replaced_at_mileage = proposal.service_mileage
            record.notes = proposal.notes
        else:
            db.add(ComponentReplacement(
                id=str(uuid.uuid4()),
                vehicle_id=proposal.vehicle_id,
                component_key=proposal.task_key,
                replaced_at_mileage=proposal.service_mileage,
                notes=proposal.notes,
            ))

    # Write a service log entry so the customer has a full history record
    business = db.query(User).filter(User.user_id == proposal.business_user_id).first()
    db.add(ServiceLog(
        id=str(uuid.uuid4()),
        vehicle_id=proposal.vehicle_id,
        entry_type=proposal.proposal_type,
        task_key=proposal.task_key,
        service_mileage=proposal.service_mileage,
        replacement_info=proposal.replacement_info,
        technician_name=proposal.technician_name,
        shop_name=business.business_name if business else None,
        cost=proposal.cost,
        notes=proposal.notes,
        logged_by_user_id=proposal.business_user_id,
    ))

    proposal.status = "accepted"
    proposal.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)
    return _proposal_out(proposal, db)


@router.patch("/{proposal_id}/deny", response_model=ServiceProposalOut)
def deny_proposal(
    proposal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proposal = db.query(ServiceProposal).filter(ServiceProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.customer_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your proposal")
    if proposal.status != "pending":
        raise HTTPException(status_code=400, detail="Proposal is no longer pending")

    proposal.status = "denied"
    proposal.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(proposal)
    return _proposal_out(proposal, db)
