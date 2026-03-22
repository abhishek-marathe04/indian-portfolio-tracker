"""CAS upload and parsing router — Phase 2 implementation.

Stub in Phase 1: route registered so the API surface is consistent.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/cas", tags=["cas"])


@router.post("/upload")
def upload_cas(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="CAS upload will be implemented in Phase 2.")
