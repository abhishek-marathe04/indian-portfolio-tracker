"""CAS upload and parse router.

POST /api/cas/upload  — accepts a CAS PDF + password, parses it, inserts
                        MF holdings and transactions, returns a summary.
GET  /api/cas/imports — list past import records.
"""
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models.mutual_fund import MutualFundHolding, MutualFundTransaction
from models.profile import Profile
from routers.auth import get_current_user
from models.user import User
from services.cas_parser import parse_cas_pdf, deduplicate_transactions

router = APIRouter(prefix="/api/cas", tags=["cas"])

# Uploads directory (relative to project root)
_UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _upsert_holding(db: Session, profile_id: int, folio: object) -> MutualFundHolding:
    """Insert or update a MutualFundHolding row."""
    holding = (
        db.query(MutualFundHolding)
        .filter(
            MutualFundHolding.profile_id == profile_id,
            MutualFundHolding.folio_number == folio.folio_number,
        )
        .first()
    )
    if holding is None:
        holding = MutualFundHolding(
            profile_id=profile_id,
            folio_number=folio.folio_number,
            scheme_name=folio.scheme_name,
            scheme_code=folio.scheme_code,
            amc_name=folio.amc_name,
            units_held=folio.units_held,
            current_value=folio.current_value,
        )
        db.add(holding)
    else:
        # Update existing
        holding.scheme_name = folio.scheme_name
        holding.amc_name = folio.amc_name
        holding.units_held = folio.units_held
        if folio.current_value is not None:
            holding.current_value = folio.current_value
    return holding


@router.post("/upload")
async def upload_cas(
    file: UploadFile = File(..., description="CAS PDF file"),
    password: str = Form(..., description="PDF password (PAN + DOB in DDMMYYYY)"),
    profile_id: int = Form(..., description="Family member profile ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and parse a CAS PDF.

    The password is used only for decryption and is **never stored**.
    The PDF is archived in uploads/ with a timestamp prefix.
    """
    # Validate profile exists
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    # Read file bytes
    pdf_bytes = await file.read()
    if len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="Uploaded file is too small to be a valid PDF")

    # Parse
    try:
        result = parse_cas_pdf(pdf_bytes, password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse CAS PDF: {exc}"
        )

    # Archive the original PDF
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    safe_name = (file.filename or 'cas.pdf').replace(' ', '_')
    archive_path = _UPLOADS_DIR / f"{timestamp}_{safe_name}"
    with open(archive_path, 'wb') as f:
        f.write(pdf_bytes)

    # Persist to database
    new_folios = 0
    updated_folios = 0
    new_transactions = 0

    for folio in result.folios:
        is_new = (
            db.query(MutualFundHolding)
            .filter(
                MutualFundHolding.profile_id == profile_id,
                MutualFundHolding.folio_number == folio.folio_number,
            )
            .first()
        ) is None

        _upsert_holding(db, profile_id, folio)
        db.flush()   # so holding.id is available

        if is_new:
            new_folios += 1
        else:
            updated_folios += 1

        # Deduplicate transactions
        existing_raw = (
            db.query(MutualFundTransaction)
            .filter(
                MutualFundTransaction.profile_id == profile_id,
                MutualFundTransaction.folio_number == folio.folio_number,
            )
            .all()
        )
        existing_dicts = [
            {
                'folio_number': r.folio_number,
                'transaction_date': r.transaction_date,
                'transaction_type': r.transaction_type,
                'amount': r.amount,
            }
            for r in existing_raw
        ]

        new_txns = deduplicate_transactions(existing_dicts, folio.transactions)
        for tx in new_txns:
            db.add(MutualFundTransaction(
                profile_id=profile_id,
                folio_number=tx.folio_number,
                transaction_date=tx.transaction_date,
                transaction_type=tx.transaction_type,
                units=tx.units,
                nav=tx.nav,
                amount=tx.amount,
                cas_source_file=safe_name,
            ))
        new_transactions += len(new_txns)

    db.commit()

    return {
        "status": "success",
        "cas_type": result.cas_type,
        "investor_name": result.investor_name,
        "pan_detected": result.pan,
        "folios_found": len(result.folios),
        "new_folios": new_folios,
        "updated_folios": updated_folios,
        "new_transactions": new_transactions,
        "archived_as": archive_path.name,
        "message": (
            f"{new_transactions} new transaction(s) imported across "
            f"{new_folios} new and {updated_folios} updated folio(s)."
        ),
    }


@router.get("/imports")
def list_imports(current_user: User = Depends(get_current_user)):
    """List archived CAS PDF files from the uploads directory."""
    files = sorted(_UPLOADS_DIR.glob('*.pdf'), reverse=True)
    return [
        {
            "filename": f.name,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "uploaded_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
        for f in files
    ]
