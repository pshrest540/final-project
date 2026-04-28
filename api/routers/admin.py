from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.db.session import get_db
from api.db.models import User, Vehicle, WellnessPrediction
from api.dependencies import require_admin
from api.schemas import UserOut, UserAdminOut, AdminStats, AccountTypeUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
def get_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return AdminStats(
        total_users=db.query(func.count(User.user_id)).scalar() or 0,
        total_vehicles=db.query(func.count(Vehicle.vehicle_id)).scalar() or 0,
        total_predictions=db.query(func.count(WellnessPrediction.prediction_id)).scalar() or 0,
    )


@router.get("/users", response_model=list[UserAdminOut])
def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        v_count = (
            db.query(func.count(Vehicle.vehicle_id))
            .filter(Vehicle.owner_id == u.user_id)
            .scalar() or 0
        )
        p_count = (
            db.query(func.count(WellnessPrediction.prediction_id))
            .join(Vehicle, WellnessPrediction.vehicle_id == Vehicle.vehicle_id)
            .filter(Vehicle.owner_id == u.user_id)
            .scalar() or 0
        )
        result.append(UserAdminOut(
            user_id=u.user_id,
            email=u.email,
            account_type=u.account_type,
            full_name=u.full_name,
            business_name=u.business_name,
            created_at=u.created_at,
            vehicle_count=v_count,
            prediction_count=p_count,
        ))
    return result


@router.patch("/users/{user_id}/account-type", response_model=UserOut)
def change_account_type(
    user_id: str,
    body: AccountTypeUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if body.account_type not in ("personal", "business"):
        raise HTTPException(status_code=400, detail="account_type must be 'personal' or 'business'")
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own account type")
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.account_type = body.account_type
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
