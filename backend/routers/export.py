"""Export endpoints (CSV, Excel, HTML snapshot) — Phase 4/5."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/csv/{asset_type}")
def export_csv(asset_type: str, current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="CSV export will be implemented in Phase 4.")


@router.get("/excel")
def export_excel(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="Excel export will be implemented in Phase 4.")


@router.post("/snapshot")
def export_snapshot(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail="HTML snapshot will be implemented in Phase 5.")
