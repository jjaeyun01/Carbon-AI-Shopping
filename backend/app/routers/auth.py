import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth import create_access_token, decode_token, hash_password, verify_password
from app.database import get_db
from app.models import EmailVerificationToken, User
from app.services.email_service import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

VERIFICATION_TOKEN_EXPIRE_HOURS = 24


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResendRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None


def get_current_user(token: str, db: Session) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def _create_verification_token(user_id: int, db: Session) -> str:
    # Remove any existing tokens for this user first
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user_id
    ).delete()

    token_str = secrets.token_urlsafe(32)
    db.add(EmailVerificationToken(
        user_id=user_id,
        token=token_str,
        expires_at=datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS),
    ))
    return token_str


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    user = User(
        email=body.email,
        username=body.username,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        is_verified=False,
    )
    db.add(user)
    db.flush()  # Assign user.id without committing yet

    token_str = _create_verification_token(user.id, db)
    db.commit()
    db.refresh(user)

    try:
        send_verification_email(user.email, user.full_name or user.username, token_str)
    except Exception as exc:
        # Don't block registration if email fails — token is in DB
        print(f"[WARNING] Verification email failed: {exc}")

    return {
        "message": "Account created. Please check your email to verify your account.",
        "email": user.email,
        "requires_verification": True,
    }


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    record = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token == token)
        .first()
    )
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    if record.expires_at < datetime.utcnow():
        db.delete(record)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Verification link has expired. Please request a new one.",
        )

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.delete(record)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    return {
        "message": "Email verified successfully. Welcome to Novera!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
        ),
    }


@router.post("/resend-verification")
def resend_verification(body: ResendRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    # Return the same message regardless to avoid email enumeration
    if not user or user.is_verified:
        return {"message": "If that email is registered and unverified, a new link has been sent."}

    token_str = _create_verification_token(user.id, db)
    db.commit()

    try:
        send_verification_email(user.email, user.full_name or user.username, token_str)
    except Exception as exc:
        print(f"[WARNING] Verification email failed: {exc}")

    return {"message": "If that email is registered and unverified, a new link has been sent."}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in. Check your inbox.",
        )

    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
        ),
    }


@router.get("/me")
def get_me(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
    )
