"""Authentication router: login, logout, current user, and health check."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import check_db_status, get_db
from models.user import User

router = APIRouter(tags=["auth"])

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_COOKIE_NAME = "access_token"
_ALGORITHM = "HS256"


def _secret_key() -> str:
    key = os.getenv("JWT_SECRET")
    if not key:
        raise RuntimeError("JWT_SECRET is not set in .env")
    return key


def _session_hours() -> int:
    return int(os.getenv("SESSION_HOURS", "8"))


# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=_session_hours())
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, _secret_key(), algorithm=_ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """FastAPI dependency — validates the JWT cookie and returns the User row."""
    token = request.cookies.get(_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[_ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api/health")
def health_check():
    """Public health-check endpoint. Returns app version and DB connectivity."""
    return {
        "status": "ok",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "db_status": check_db_status(),
    }


@router.post("/api/auth/login")
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(user.username)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=_session_hours() * 3600,
        samesite="lax",
        # secure=True  ← enable when serving over HTTPS
    )
    return {"message": "Login successful", "username": user.username}


@router.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(_COOKIE_NAME)
    return {"message": "Logged out"}


@router.get("/api/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "created_at": current_user.created_at,
    }


@router.post("/api/auth/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
