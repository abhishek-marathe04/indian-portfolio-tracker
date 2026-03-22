"""Asset CRUD endpoints — Phase 2 full implementation.

Phase 1: stubs for all asset-class routes so the API surface is declared.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/assets", tags=["assets"])

_PHASE2_MSG = "Full asset CRUD will be implemented in Phase 2."


@router.get("/mutual-funds")
def list_mutual_funds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/stocks")
def list_stocks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/deposits")
def list_deposits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/provident-funds")
def list_provident_funds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/sukanya-samriddhi")
def list_ssy(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/nps")
def list_nps(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/gold")
def list_gold(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/real-estate")
def list_real_estate(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/international")
def list_international(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/crypto")
def list_crypto(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/post-office")
def list_post_office(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/savings-accounts")
def list_savings_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)


@router.get("/goals")
def list_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    raise HTTPException(status_code=501, detail=_PHASE2_MSG)
