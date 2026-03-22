"""Analytics endpoints (XIRR, allocation, benchmarks, tax) — Phase 3."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

_PHASE3_MSG = "Analytics will be implemented in Phase 3."


@router.get("/xirr")
def xirr(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE3_MSG)


@router.get("/allocation")
def allocation(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE3_MSG)


@router.get("/net-worth")
def net_worth(current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE3_MSG)
