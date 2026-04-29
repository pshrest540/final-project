import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.models import BusinessCustomerLink, User, Vehicle
from api.db.session import get_db
from api.dependencies import get_current_user
from api.schemas import CustomerLinkCreate, LinkedCustomerOut

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
    customer = db.query(User).filter(User.share_code == body.share_code).first()
    if not customer:
        raise HTTPException(status_code=404, detail="No customer found with that share ID")
    if customer.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="You cannot link your own account")
    if customer.account_type != "personal":
        raise HTTPException(status_code=400, detail="Share ID must belong to a customer account")

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
    db.delete(link)
    db.commit()
    return None
