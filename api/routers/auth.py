import uuid
from random import SystemRandom

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.db.models import User
from api.schemas import UserCreate, UserLogin, UserOut, Token, AccountUpdate
from api.services.auth import hash_password, verify_password, create_access_token
from api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])
_rng = SystemRandom()


def _generate_share_code(db: Session) -> str:
    for _ in range(100):
        code = f"{_rng.randrange(1_000_000):06d}"
        if not db.query(User).filter(User.share_code == code).first():
            return code
    raise HTTPException(status_code=500, detail="Could not create a unique share ID")


def _ensure_share_code(user: User, db: Session) -> User:
    if user.share_code:
        return user
    user.share_code = _generate_share_code(db)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        user_id=str(uuid.uuid4()),
        email=body.email,
        password_hash=hash_password(body.password),
        account_type=body.account_type or "personal",
        share_code=_generate_share_code(db),
        business_name=body.business_name,
        full_name=body.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(
        access_token=create_access_token(user.user_id),
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user = _ensure_share_code(user, db)
    return Token(
        access_token=create_access_token(user.user_id),
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return UserOut.model_validate(_ensure_share_code(current_user, db))


@router.patch("/me", response_model=UserOut)
def update_me(
    body: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    changing_sensitive = body.email is not None or body.new_password is not None
    if changing_sensitive:
        if not body.current_password:
            raise HTTPException(status_code=400, detail="current_password required to change email or password")
        if not verify_password(body.current_password, current_user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect current password")

    if body.email is not None and body.email != current_user.email:
        if db.query(User).filter(User.email == body.email, User.user_id != current_user.user_id).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = body.email

    if body.new_password is not None:
        current_user.password_hash = hash_password(body.new_password)

    if body.full_name is not None:
        current_user.full_name = body.full_name or None

    if body.business_name is not None:
        current_user.business_name = body.business_name or None

    db.commit()
    db.refresh(current_user)
    return UserOut.model_validate(current_user)


class _DeleteBody(AccountUpdate):
    pass


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    body: _DeleteBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.current_password:
        raise HTTPException(status_code=400, detail="current_password required")
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
    db.delete(current_user)
    db.commit()
