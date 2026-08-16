"""CAS upload and parse router.

POST /api/cas/upload            — single CAS PDF upload + parse.
POST /api/cas/bulk-upload       — multiple CAS PDFs, one password, background queue.
GET  /api/cas/bulk-status/{id}  — poll per-file progress for a bulk upload job.
GET  /api/cas/imports           — list past import records.
"""
from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import SessionLocal, get_db
from models.mutual_fund import MutualFundHolding, MutualFundTransaction
from models.nps import NPS
from models.portfolio_snapshot import PortfolioSnapshot
from models.profile import Profile
from models.stock import StockHolding
from routers.auth import get_current_user
from models.user import User
from services.cas_parser import parse_cas_pdf, deduplicate_transactions

router = APIRouter(prefix="/api/cas", tags=["cas"])

# Uploads directory (relative to project root)
_UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory store for bulk upload job state.
# Key: job_id (str), Value: job dict (see _make_file_entry / _make_job).
_bulk_jobs: dict[str, dict] = {}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_file_entry(filename: str) -> dict:
    return {
        "filename": filename,
        "status": "queued",       # queued | processing | done | duplicate | error
        "message": "",
        "folios_found": 0,
        "new_transactions": 0,
    }


def _is_newer_or_unknown(new_date, existing_date) -> bool:
    """True if the incoming statement should be allowed to overwrite the
    current snapshot — i.e. we have no basis to say it's older."""
    if new_date is None or existing_date is None:
        return True
    return new_date >= existing_date


def _upsert_holding(db: Session, profile_id: int, folio: object, statement_date) -> MutualFundHolding:
    """Insert or update a MutualFundHolding row.

    Keyed on (profile_id, folio_number, isin) rather than folio_number alone —
    a single folio can hold multiple schemes, so folio_number isn't unique by itself.
    units_held/current_value are only overwritten if this statement is not older
    than the one that last set them, so uploading historical CAS files out of
    order can't clobber the current portfolio snapshot with stale numbers.
    """
    query = db.query(MutualFundHolding).filter(
        MutualFundHolding.profile_id == profile_id,
        MutualFundHolding.folio_number == folio.folio_number,
    )
    if folio.isin:
        query = query.filter(MutualFundHolding.isin == folio.isin)
    else:
        query = query.filter(MutualFundHolding.scheme_name == folio.scheme_name)
    holding = query.first()

    if holding is None:
        holding = MutualFundHolding(
            profile_id=profile_id,
            folio_number=folio.folio_number,
            scheme_name=folio.scheme_name,
            scheme_code=folio.scheme_code,
            isin=folio.isin,
            amc_name=folio.amc_name,
            units_held=folio.units_held,
            current_value=folio.current_value,
            cas_statement_date=statement_date,
        )
        db.add(holding)
    else:
        holding.scheme_name = folio.scheme_name
        holding.scheme_code = holding.scheme_code or folio.scheme_code
        holding.isin = holding.isin or folio.isin
        holding.amc_name = folio.amc_name
        if _is_newer_or_unknown(statement_date, holding.cas_statement_date):
            holding.units_held = folio.units_held
            if folio.current_value is not None:
                holding.current_value = folio.current_value
            if statement_date is not None:
                holding.cas_statement_date = statement_date
    return holding


def _upsert_equity_holding(db: Session, profile_id: int, eq: object, statement_date) -> StockHolding:
    """Insert or update a StockHolding row keyed on (profile_id, isin).

    CAS has no NSE/BSE ticker symbol, only ISIN — the ISIN is used as the
    ticker placeholder since the column is required and non-null.
    quantity/current_price are only overwritten if this statement is not
    older than the one that last set them (see _upsert_holding).
    """
    holding = (
        db.query(StockHolding)
        .filter(StockHolding.profile_id == profile_id, StockHolding.isin == eq.isin)
        .first()
    )
    if holding is None:
        holding = StockHolding(
            profile_id=profile_id,
            exchange="NSE",
            ticker=eq.isin,
            company_name=eq.name,
            isin=eq.isin,
            quantity=eq.quantity,
            current_price=eq.market_price,
            broker="CAS Import",
            cas_statement_date=statement_date,
        )
        db.add(holding)
    else:
        if eq.name and eq.name != "Unknown Security":
            holding.company_name = eq.name
        if _is_newer_or_unknown(statement_date, holding.cas_statement_date):
            holding.quantity = eq.quantity
            if eq.market_price is not None:
                holding.current_price = eq.market_price
            if statement_date is not None:
                holding.cas_statement_date = statement_date
    return holding


def _upsert_nps(db: Session, profile_id: int, nps_data: object, statement_date) -> NPS:
    """Insert or update an NPS row keyed on (profile_id, pran_number).

    current_value/pcts are only overwritten if this statement is not older
    than the one that last set them (see _upsert_holding).
    """
    account = (
        db.query(NPS)
        .filter(NPS.profile_id == profile_id, NPS.pran_number == nps_data.pran_number)
        .first()
    )
    if account is None:
        account = NPS(
            profile_id=profile_id,
            pran_number=nps_data.pran_number,
            tier=nps_data.tier,
            fund_manager=nps_data.fund_manager,
            equity_pct=nps_data.equity_pct,
            corporate_bond_pct=nps_data.corporate_bond_pct,
            govt_bond_pct=nps_data.govt_bond_pct,
            current_value=nps_data.current_value,
            cas_statement_date=statement_date,
        )
        db.add(account)
    else:
        account.fund_manager = nps_data.fund_manager or account.fund_manager
        if _is_newer_or_unknown(statement_date, account.cas_statement_date):
            account.equity_pct = nps_data.equity_pct
            account.corporate_bond_pct = nps_data.corporate_bond_pct
            account.govt_bond_pct = nps_data.govt_bond_pct
            account.current_value = nps_data.current_value
            if statement_date is not None:
                account.cas_statement_date = statement_date
    return account


def _upsert_portfolio_snapshot(db: Session, profile_id: int, snap: dict, source_file: str) -> PortfolioSnapshot:
    """Insert or update a month-end PortfolioSnapshot keyed on (profile_id, month)."""
    row = (
        db.query(PortfolioSnapshot)
        .filter(PortfolioSnapshot.profile_id == profile_id, PortfolioSnapshot.snapshot_month == snap['month'])
        .first()
    )
    if row is None:
        row = PortfolioSnapshot(
            profile_id=profile_id,
            snapshot_month=snap['month'],
            total_value=snap['total_value'],
            cas_source_file=source_file,
        )
        db.add(row)
    else:
        row.total_value = snap['total_value']
        row.cas_source_file = source_file
    return row


def _import_cas_to_db(
    db: Session,
    profile_id: int,
    pdf_bytes: bytes,
    password: str,
    safe_filename: str,
) -> dict:
    """Parse a CAS PDF and persist to DB. Returns a summary dict.

    Raises ValueError on bad password / unrecognised format.
    """
    result = parse_cas_pdf(pdf_bytes, password)

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

        _upsert_holding(db, profile_id, folio, result.statement_date)
        db.flush()

        if is_new:
            new_folios += 1
        else:
            updated_folios += 1

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
                "folio_number": r.folio_number,
                "transaction_date": r.transaction_date,
                "transaction_type": r.transaction_type,
                "units": r.units,
                "amount": r.amount,
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
                cas_source_file=safe_filename,
            ))
        new_transactions += len(new_txns)

    new_equity_holdings = 0
    for eq in result.equity_holdings:
        is_new = (
            db.query(StockHolding)
            .filter(StockHolding.profile_id == profile_id, StockHolding.isin == eq.isin)
            .first()
        ) is None
        _upsert_equity_holding(db, profile_id, eq, result.statement_date)
        if is_new:
            new_equity_holdings += 1

    for nps_data in result.nps_accounts:
        _upsert_nps(db, profile_id, nps_data, result.statement_date)

    for snap in result.portfolio_snapshots:
        _upsert_portfolio_snapshot(db, profile_id, snap, safe_filename)

    db.commit()

    return {
        "cas_type": result.cas_type,
        "investor_name": result.investor_name,
        "pan": result.pan,
        "statement_date": result.statement_date.isoformat() if result.statement_date else None,
        "folios_found": len(result.folios),
        "new_folios": new_folios,
        "updated_folios": updated_folios,
        "new_transactions": new_transactions,
        "equity_holdings_found": len(result.equity_holdings),
        "new_equity_holdings": new_equity_holdings,
        "nps_accounts_found": len(result.nps_accounts),
        "portfolio_snapshots_found": len(result.portfolio_snapshots),
    }


# ── Background worker for bulk uploads ────────────────────────────────────────

def _run_bulk_job(
    job_id: str,
    file_data: list[dict],   # [{"filename": str, "bytes": bytes}]
    password: str,
    profile_id: int,
) -> None:
    """Process each file sequentially in a background thread."""
    job = _bulk_jobs[job_id]
    total_new_transactions = 0

    for i, fd in enumerate(file_data):
        job["files"][i]["status"] = "processing"
        safe_name = fd["filename"].replace(" ", "_")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_path = _UPLOADS_DIR / f"{timestamp}_{safe_name}"

        db = SessionLocal()
        try:
            summary = _import_cas_to_db(db, profile_id, fd["bytes"], password, safe_name)

            # Archive PDF
            with open(archive_path, "wb") as fh:
                fh.write(fd["bytes"])

            if (
                summary["new_transactions"] == 0
                and summary["new_folios"] == 0
                and summary["new_equity_holdings"] == 0
            ):
                job["files"][i]["status"] = "duplicate"
                job["files"][i]["message"] = "Already imported — skipped"
            else:
                job["files"][i]["status"] = "done"
                job["files"][i]["message"] = (
                    f"{summary['new_transactions']} transaction(s), "
                    f"{summary['folios_found']} folio(s), "
                    f"{summary['equity_holdings_found']} equity holding(s), "
                    f"{summary['nps_accounts_found']} NPS account(s)"
                )

            job["files"][i]["folios_found"] = summary["folios_found"]
            job["files"][i]["new_transactions"] = summary["new_transactions"]
            total_new_transactions += summary["new_transactions"]

        except ValueError as exc:
            db.rollback()
            job["files"][i]["status"] = "error"
            job["files"][i]["message"] = str(exc)
        except Exception as exc:
            db.rollback()
            job["files"][i]["status"] = "error"
            job["files"][i]["message"] = f"Unexpected error: {exc}"
        finally:
            db.close()
            job["processed"] += 1

    job["status"] = "complete"
    job["total_new_transactions"] = total_new_transactions


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_cas(
    file: UploadFile = File(..., description="CAS PDF file"),
    password: str = Form(..., description="PDF password (PAN + DOB in DDMMYYYY)"),
    profile_id: int = Form(..., description="Family member profile ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and parse a single CAS PDF.

    The password is used only for decryption and is **never stored**.
    The PDF is archived in uploads/ with a timestamp prefix.
    """
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    pdf_bytes = await file.read()
    if len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="Uploaded file is too small to be a valid PDF")

    safe_name = (file.filename or "cas.pdf").replace(" ", "_")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_path = _UPLOADS_DIR / f"{timestamp}_{safe_name}"

    try:
        summary = _import_cas_to_db(db, profile_id, pdf_bytes, password, safe_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse CAS PDF: {exc}")

    with open(archive_path, "wb") as fh:
        fh.write(pdf_bytes)

    return {
        "status": "success",
        "cas_type": summary["cas_type"],
        "investor_name": summary["investor_name"],
        "pan_detected": summary["pan"],
        "statement_date": summary["statement_date"],
        "folios_found": summary["folios_found"],
        "new_folios": summary["new_folios"],
        "updated_folios": summary["updated_folios"],
        "new_transactions": summary["new_transactions"],
        "equity_holdings_found": summary["equity_holdings_found"],
        "new_equity_holdings": summary["new_equity_holdings"],
        "nps_accounts_found": summary["nps_accounts_found"],
        "archived_as": archive_path.name,
        "message": (
            f"{summary['new_transactions']} new transaction(s) imported across "
            f"{summary['new_folios']} new and {summary['updated_folios']} updated folio(s). "
            f"{summary['equity_holdings_found']} equity/demat holding(s) and "
            f"{summary['nps_accounts_found']} NPS account(s) also found."
        ),
    }


@router.post("/bulk-upload")
async def bulk_upload_cas(
    files: List[UploadFile] = File(..., description="One or more CAS PDF files"),
    password: str = Form(..., description="PDF password — same for all files (PAN + DOB in DDMMYYYY)"),
    profile_id: int = Form(..., description="Family member profile ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Queue multiple CAS PDFs for sequential background processing.

    Returns a job_id immediately. Poll GET /api/cas/bulk-status/{job_id} for
    per-file progress.

    A single password is assumed across all files (standard PAN-based CAS
    password). Files are processed sequentially; duplicates are silently skipped.
    """
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Read all bytes while the request is still open
    file_data: list[dict] = []
    for f in files:
        data = await f.read()
        if len(data) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' is too small to be a valid PDF",
            )
        file_data.append({"filename": f.filename or "cas.pdf", "bytes": data})

    # Create job record
    job_id = str(uuid.uuid4())
    _bulk_jobs[job_id] = {
        "status": "running",
        "total_files": len(file_data),
        "processed": 0,
        "total_new_transactions": 0,
        "files": [_make_file_entry(fd["filename"]) for fd in file_data],
    }

    # Spawn background thread (daemon so it doesn't block shutdown)
    thread = threading.Thread(
        target=_run_bulk_job,
        args=(job_id, file_data, password, profile_id),
        daemon=True,
    )
    thread.start()

    return {
        "job_id": job_id,
        "total_files": len(file_data),
        "message": f"{len(file_data)} file(s) queued for processing.",
    }


@router.get("/bulk-status/{job_id}")
def get_bulk_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    """Poll the status of a bulk CAS upload job.

    Returns overall job status and per-file progress:
      - queued     — waiting to be processed
      - processing — currently being parsed
      - done       — imported successfully (with transaction counts)
      - duplicate  — entire file was already in DB, skipped
      - error      — failed (wrong password, bad format, etc.)
    """
    job = _bulk_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Bulk upload job not found")
    return job


@router.get("/imports")
def list_imports(current_user: User = Depends(get_current_user)):
    """List archived CAS PDF files from the uploads directory."""
    files = sorted(_UPLOADS_DIR.glob("*.pdf"), reverse=True)
    return [
        {
            "filename": f.name,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "uploaded_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
        for f in files
    ]
