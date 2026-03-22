"""Family profile CRUD — create, read, update, delete profiles."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.profile import Profile
from routers.auth import get_current_user
from models.user import User
from services.encryption import decrypt, encrypt

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProfileCreate(BaseModel):
    name: str
    relationship: str = "self"
    date_of_birth: Optional[date] = None
    pan_number: Optional[str] = None    # plain text — encrypted before storage


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    date_of_birth: Optional[date] = None
    pan_number: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _profile_to_dict(p: Profile) -> dict:
    pan: Optional[str] = None
    if p.pan_number_encrypted:
        try:
            pan = decrypt(p.pan_number_encrypted)
        except Exception:
            pan = "***decryption error***"
    return {
        "id": p.id,
        "name": p.name,
        "relationship": p.relationship,
        "date_of_birth": p.date_of_birth,
        "pan_number": pan,
        "created_at": str(p.created_at) if p.created_at else None,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
def list_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [_profile_to_dict(p) for p in db.query(Profile).all()]


@router.post("", status_code=201)
def create_profile(
    data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pan_enc = encrypt(data.pan_number.upper().strip()) if data.pan_number else None
    profile = Profile(
        name=data.name,
        relationship=data.relationship,
        date_of_birth=data.date_of_birth,
        pan_number_encrypted=pan_enc,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _profile_to_dict(profile)


@router.get("/{profile_id}")
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Profile).filter(Profile.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profile_to_dict(p)


@router.put("/{profile_id}")
def update_profile(
    profile_id: int,
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Profile).filter(Profile.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")

    if data.name is not None:
        p.name = data.name
    if data.relationship is not None:
        p.relationship = data.relationship
    if data.date_of_birth is not None:
        p.date_of_birth = data.date_of_birth
    if data.pan_number is not None:
        p.pan_number_encrypted = encrypt(data.pan_number.upper().strip())

    db.commit()
    db.refresh(p)
    return _profile_to_dict(p)


@router.delete("/{profile_id}", status_code=204)
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = db.query(Profile).filter(Profile.id == profile_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(p)
    db.commit()
