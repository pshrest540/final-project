import secrets
import string
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import PairingCode, User
from api.schemas import PairingCodeOut
from api.dependencies import get_current_user

router = APIRouter(prefix="/pairing", tags=["Pairing"])

_CHARSET = string.ascii_uppercase + string.digits  # A-Z 0-9, 36 chars → 36^5 ≈ 60M combinations
_TTL_MINUTES = 5


def _make_code(db: Session) -> str:
    for _ in range(30):
        code = "".join(secrets.choice(_CHARSET) for _ in range(5))
        if not db.query(PairingCode).filter(PairingCode.code == code).first():
            return code
    raise HTTPException(status_code=500, detail="Could not generate a unique pairing code")


def _upsert(user_id: str, db: Session) -> PairingCodeOut:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=_TTL_MINUTES)
    code = _make_code(db)

    existing = db.query(PairingCode).filter(PairingCode.user_id == user_id).first()
    if existing:
        existing.code = code
        existing.expires_at = expires_at
    else:
        db.add(PairingCode(user_id=user_id, code=code, expires_at=expires_at))
    db.commit()
    return PairingCodeOut(code=code, expires_at=expires_at)


@router.get("/me", response_model=PairingCodeOut)
def get_pairing_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return existing code if still valid, otherwise generate a fresh one."""
    if current_user.account_type == "business":
        raise HTTPException(status_code=403, detail="Customers only")

    existing = db.query(PairingCode).filter(PairingCode.user_id == current_user.user_id).first()
    if existing:
        exp = existing.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp > datetime.now(timezone.utc):
            return PairingCodeOut(code=existing.code, expires_at=exp)

    return _upsert(current_user.user_id, db)


@router.post("/generate", response_model=PairingCodeOut)
def refresh_pairing_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force-generate a new code immediately, invalidating the old one."""
    if current_user.account_type == "business":
        raise HTTPException(status_code=403, detail="Customers only")
    return _upsert(current_user.user_id, db)
