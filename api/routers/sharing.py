import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from api.db.models import BusinessCustomerLink, PairingCode, ServiceProposal, User, Vehicle
from api.db.session import get_db
from api.dependencies import get_current_user
from api.schemas import CustomerLinkCreate, LinkedBusinessOut, LinkedCustomerOut

router = APIRouter(prefix="/sharing", tags=["Sharing"])


def _require_business(user: User) -> None:
    if user.account_type != "business":
        raise HTTPException(status_code=403, detail="Business account required")


def _shared_vehicle_count(customer_id: str, db: Session) -> int:
    return (
        db.query(Vehicle)
        .filter(Vehicle.owner_id == customer_id, Vehicle.share_enabled.is_(True))
        .count()
    )


def _linked_customer_out(customer: User, db: Session) -> LinkedCustomerOut:
    return LinkedCustomerOut(
        user_id=customer.user_id,
        email=customer.email,
        full_name=customer.full_name,
        business_name=customer.business_name,
        shared_vehicle_count=_shared_vehicle_count(customer.user_id, db),
    )


@router.get("/customers", response_model=list[LinkedCustomerOut])
def list_linked_customers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_business(current_user)
    rows = (
        db.query(User)
        .join(BusinessCustomerLink, BusinessCustomerLink.customer_user_id == User.user_id)
        .filter(BusinessCustomerLink.business_user_id == current_user.user_id)
        .order_by(User.email.asc())
        .all()
    )
    return [_linked_customer_out(customer, db) for customer in rows]


@router.post("/customers", response_model=LinkedCustomerOut, status_code=status.HTTP_201_CREATED)
def link_customer(
    body: CustomerLinkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_business(current_user)

    pairing = db.query(PairingCode).filter(PairingCode.code == body.pairing_code.upper()).first()
    if not pairing:
        raise HTTPException(status_code=404, detail="Invalid connection code")

    exp = pairing.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Connection code has expired — ask the customer to generate a new one")

    customer = db.query(User).filter(User.user_id == pairing.user_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer account not found")

    existing = (
        db.query(BusinessCustomerLink)
        .filter(
            BusinessCustomerLink.business_user_id == current_user.user_id,
            BusinessCustomerLink.customer_user_id == customer.user_id,
        )
        .first()
    )
    if not existing:
        db.add(
            BusinessCustomerLink(
                id=str(uuid.uuid4()),
                business_user_id=current_user.user_id,
                customer_user_id=customer.user_id,
            )
        )
    # Invalidate the code after successful use
    db.delete(pairing)
    db.commit()
    return _linked_customer_out(customer, db)


@router.delete("/customers/{customer_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_customer(
    customer_user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_business(current_user)
    link = (
        db.query(BusinessCustomerLink)
        .filter(
            BusinessCustomerLink.business_user_id == current_user.user_id,
            BusinessCustomerLink.customer_user_id == customer_user_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Customer link not found")
    # Cancel all pending proposals between this business and the customer's vehicles
    customer_vehicle_ids = [
        v.vehicle_id
        for v in db.query(Vehicle).filter(Vehicle.owner_id == customer_user_id).all()
    ]
    if customer_vehicle_ids:
        (
            db.query(ServiceProposal)
            .filter(
                ServiceProposal.business_user_id == current_user.user_id,
                ServiceProposal.vehicle_id.in_(customer_vehicle_ids),
                ServiceProposal.status == "pending",
            )
            .update({"status": "cancelled"}, synchronize_session=False)
        )
    db.delete(link)
    db.commit()
    return None


@router.get("/businesses", response_model=list[LinkedBusinessOut])
def list_linked_businesses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Customer: see which businesses are linked to their account."""
    if current_user.account_type == "business":
        raise HTTPException(status_code=403, detail="Customers only")
    rows = (
        db.query(User)
        .join(BusinessCustomerLink, BusinessCustomerLink.business_user_id == User.user_id)
        .filter(BusinessCustomerLink.customer_user_id == current_user.user_id)
        .order_by(User.email.asc())
        .all()
    )
    return [
        LinkedBusinessOut(
            user_id=u.user_id,
            email=u.email,
            business_name=u.business_name,
        )
        for u in rows
    ]


@router.delete("/businesses/{business_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_business(
    business_user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Customer: remove a business from their account and cancel all pending proposals from them."""
    if current_user.account_type == "business":
        raise HTTPException(status_code=403, detail="Customers only")
    link = (
        db.query(BusinessCustomerLink)
        .filter(
            BusinessCustomerLink.business_user_id == business_user_id,
            BusinessCustomerLink.customer_user_id == current_user.user_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Business link not found")
    # Cancel all pending proposals from this business across all customer vehicles
    my_vehicle_ids = [
        v.vehicle_id
        for v in db.query(Vehicle).filter(Vehicle.owner_id == current_user.user_id).all()
    ]
    if my_vehicle_ids:
        (
            db.query(ServiceProposal)
            .filter(
                ServiceProposal.business_user_id == business_user_id,
                ServiceProposal.vehicle_id.in_(my_vehicle_ids),
                ServiceProposal.status == "pending",
            )
            .update({"status": "cancelled"}, synchronize_session=False)
        )
    db.delete(link)
    db.commit()
    return None
