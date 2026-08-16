"""Analytics endpoints — net worth, allocation, XIRR, price refresh.

Phase 2: net worth + allocation + manual price refresh.
Phase 3: XIRR, benchmark comparison, tax insights.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from models.user import User
from models.profile import Profile
from models.mutual_fund import MutualFundHolding, MutualFundTransaction
from models.stock import StockHolding, StockTransaction
from models.deposit import Deposit
from models.provident_fund import ProvidentFund
from models.sukanya_samriddhi import SukanyaSamriddhi
from models.nps import NPS
from models.gold import GoldHolding
from models.real_estate import RealEstate
from models.international_holding import InternationalHolding
from models.crypto import CryptoHolding
from models.post_office import PostOfficeScheme
from models.savings_account import SavingsAccount
from models.portfolio_snapshot import PortfolioSnapshot
from services.xirr import xirr as compute_xirr

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _safe(v) -> float:
    """Return float or 0 for None."""
    return float(v) if v is not None else 0.0


def _net_worth_for_profile(profile_id: int, db: Session) -> dict:
    """Compute net worth breakdown for one profile."""

    mf_value = sum(
        _safe(h.current_value)
        for h in db.query(MutualFundHolding).filter(MutualFundHolding.profile_id == profile_id)
    )
    mf_invested = sum(
        _safe(h.invested_amount)
        for h in db.query(MutualFundHolding).filter(MutualFundHolding.profile_id == profile_id)
    )

    stocks_value = sum(
        _safe(h.quantity) * _safe(h.current_price)
        for h in db.query(StockHolding).filter(StockHolding.profile_id == profile_id)
    )
    stocks_invested = sum(
        _safe(h.quantity) * _safe(h.avg_buy_price)
        for h in db.query(StockHolding).filter(StockHolding.profile_id == profile_id)
    )

    deposits_value = sum(
        _safe(d.principal_amount)
        for d in db.query(Deposit).filter(Deposit.profile_id == profile_id, Deposit.is_active == True)
    )

    pf_value = sum(
        _safe(p.current_balance)
        for p in db.query(ProvidentFund).filter(ProvidentFund.profile_id == profile_id)
    )

    ssy_value = sum(
        _safe(s.current_balance)
        for s in db.query(SukanyaSamriddhi).filter(SukanyaSamriddhi.profile_id == profile_id)
    )

    nps_value = sum(
        _safe(n.current_value)
        for n in db.query(NPS).filter(NPS.profile_id == profile_id)
    )

    gold_value = sum(
        (_safe(g.quantity_grams or g.units or 0)) * _safe(g.current_price_per_gram_or_unit or 0)
        for g in db.query(GoldHolding).filter(GoldHolding.profile_id == profile_id)
    )

    re_value = sum(
        _safe(r.current_estimated_value) - _safe(r.outstanding_loan_amount)
        for r in db.query(RealEstate).filter(RealEstate.profile_id == profile_id)
    )

    intl_value = sum(
        _safe(h.quantity) * _safe(h.current_price_inr or 0)
        for h in db.query(InternationalHolding).filter(InternationalHolding.profile_id == profile_id)
    )
    intl_invested = sum(
        _safe(h.quantity) * _safe(h.avg_buy_price_usd or 0)
        for h in db.query(InternationalHolding).filter(InternationalHolding.profile_id == profile_id)
    )

    crypto_value = sum(
        _safe(c.quantity) * _safe(c.current_price_inr or 0)
        for c in db.query(CryptoHolding).filter(CryptoHolding.profile_id == profile_id)
    )
    crypto_invested = sum(
        _safe(c.quantity) * _safe(c.avg_buy_price_inr or 0)
        for c in db.query(CryptoHolding).filter(CryptoHolding.profile_id == profile_id)
    )

    po_value = sum(
        _safe(p.principal_amount)
        for p in db.query(PostOfficeScheme).filter(PostOfficeScheme.profile_id == profile_id)
    )

    savings_value = sum(
        _safe(s.current_balance)
        for s in db.query(SavingsAccount).filter(SavingsAccount.profile_id == profile_id)
    )

    total = (
        mf_value + stocks_value + deposits_value + pf_value + ssy_value
        + nps_value + gold_value + re_value + intl_value + crypto_value
        + po_value + savings_value
    )
    total_invested = mf_invested + stocks_invested + intl_invested + crypto_invested

    return {
        "profile_id": profile_id,
        "total_value": round(total, 2),
        "total_invested": round(total_invested, 2),
        "gain_loss": round(total_invested and (total - total_invested) or 0, 2),
        "gain_loss_pct": round(
            ((total - total_invested) / total_invested * 100) if total_invested else 0, 2
        ),
        "breakdown": {
            "mutual_funds": round(mf_value, 2),
            "stocks": round(stocks_value, 2),
            "deposits": round(deposits_value, 2),
            "provident_fund": round(pf_value, 2),
            "sukanya_samriddhi": round(ssy_value, 2),
            "nps": round(nps_value, 2),
            "gold": round(gold_value, 2),
            "real_estate": round(re_value, 2),
            "international": round(intl_value, 2),
            "crypto": round(crypto_value, 2),
            "post_office": round(po_value, 2),
            "savings": round(savings_value, 2),
        },
    }


@router.get("/net-worth")
def net_worth(
    profile_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return net worth breakdown.

    - `?profile_id=N` → single profile
    - No param → all profiles + consolidated total
    """
    if profile_id is not None:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return _net_worth_for_profile(profile_id, db)

    profiles = db.query(Profile).all()
    per_profile = [_net_worth_for_profile(p.id, db) for p in profiles]

    consolidated_total = sum(p["total_value"] for p in per_profile)
    consolidated_invested = sum(p["total_invested"] for p in per_profile)

    # Sum breakdown keys
    breakdown_keys = list(per_profile[0]["breakdown"].keys()) if per_profile else []
    consolidated_breakdown = {
        k: round(sum(p["breakdown"][k] for p in per_profile), 2)
        for k in breakdown_keys
    }

    return {
        "consolidated": {
            "total_value": round(consolidated_total, 2),
            "total_invested": round(consolidated_invested, 2),
            "gain_loss": round(consolidated_total - consolidated_invested, 2),
            "gain_loss_pct": round(
                ((consolidated_total - consolidated_invested) / consolidated_invested * 100)
                if consolidated_invested else 0,
                2,
            ),
            "breakdown": consolidated_breakdown,
        },
        "per_profile": per_profile,
    }


@router.get("/allocation")
def allocation(
    profile_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return asset allocation as percentages — useful for donut charts."""
    if profile_id is not None:
        data = _net_worth_for_profile(profile_id, db)
    else:
        result = net_worth(profile_id=None, db=db, current_user=current_user)
        data = result["consolidated"]   # type: ignore[index]

    total = data["total_value"]
    if total == 0:
        return {"total_value": 0, "allocation": {}}

    allocation_pct = {
        k: round(v / total * 100, 2)
        for k, v in data["breakdown"].items()
        if v > 0
    }
    return {
        "total_value": total,
        "allocation": allocation_pct,
        "breakdown_inr": data["breakdown"],
    }


@router.post("/refresh-prices")
async def refresh_prices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger a NAV refresh for all MF holdings that have scheme codes."""
    from services.price_fetcher import refresh_mf_navs_for_portfolio
    updated = await refresh_mf_navs_for_portfolio(db)
    return {"message": f"Updated NAVs for {updated} holding(s)."}


# Asset classes CAS/broker imports give us dated transaction history for —
# the only ones a real XIRR can be computed from. Other asset classes only
# have a current-value snapshot, so they're excluded.
XIRR_ASSET_TYPES = ("all", "mutual_funds", "stocks")


def _mf_cash_flows(
    profile_ids: list[int], db: Session, folio_number: str | None = None
) -> list[tuple[date, float]]:
    """Mutual fund cash flows: purchases/SIPs as outflows, redemptions as inflows,
    plus current holding value as a final inflow today. Optionally scoped to a
    single folio."""
    txn_query = db.query(MutualFundTransaction).filter(MutualFundTransaction.profile_id.in_(profile_ids))
    holding_query = db.query(MutualFundHolding).filter(MutualFundHolding.profile_id.in_(profile_ids))
    if folio_number is not None:
        txn_query = txn_query.filter(MutualFundTransaction.folio_number == folio_number)
        holding_query = holding_query.filter(MutualFundHolding.folio_number == folio_number)

    flows: list[tuple[date, float]] = []
    for t in txn_query.all():
        if t.amount is None:
            continue
        sign = -1 if t.transaction_type in ("purchase", "sip", "switch_in") else 1
        d = t.transaction_date
        flows.append((d.date() if hasattr(d, "date") else d, sign * t.amount))

    current_value = sum(_safe(h.current_value) for h in holding_query)
    if current_value:
        flows.append((date.today(), current_value))
    return flows


def _stock_cash_flows(profile_ids: list[int], db: Session) -> list[tuple[date, float]]:
    """Stock cash flows: buys as outflows, sells as inflows (net of brokerage),
    plus current holding value as a final inflow today."""
    txns = (
        db.query(StockTransaction)
        .filter(StockTransaction.profile_id.in_(profile_ids))
        .all()
    )
    flows: list[tuple[date, float]] = []
    for t in txns:
        if t.price is None or t.quantity is None:
            continue
        gross = t.price * t.quantity
        brokerage = _safe(t.brokerage)
        amount = -(gross + brokerage) if t.action == "buy" else (gross - brokerage)
        d = t.transaction_date
        flows.append((d.date() if hasattr(d, "date") else d, amount))

    current_value = sum(
        _safe(h.quantity) * _safe(h.current_price)
        for h in db.query(StockHolding).filter(StockHolding.profile_id.in_(profile_ids))
    )
    if current_value:
        flows.append((date.today(), current_value))
    return flows


def _xirr_from_flows(flows: list[tuple[date, float]]) -> float | None:
    if len(flows) < 2:
        return None
    paired = sorted(flows)
    sorted_dates = [d for d, _ in paired]
    sorted_amounts = [a for _, a in paired]
    result = compute_xirr(sorted_amounts, sorted_dates)
    return round(result * 100, 2) if result is not None else None


def _xirr_for_asset_type(
    asset_type: str, profile_ids: list[int], db: Session, folio_number: str | None = None
) -> float | None:
    if asset_type == "mutual_funds":
        return _xirr_from_flows(_mf_cash_flows(profile_ids, db, folio_number))
    if asset_type == "stocks":
        return _xirr_from_flows(_stock_cash_flows(profile_ids, db))
    return _xirr_from_flows(_mf_cash_flows(profile_ids, db) + _stock_cash_flows(profile_ids, db))


_XIRR_NOTES = {
    "all": (
        "XIRR is computed from mutual fund and stock transactions imported via CAS/broker "
        "statements — other asset classes don't have transaction-level history yet."
    ),
    "mutual_funds": "XIRR computed from mutual fund transactions imported via CAS.",
    "stocks": "XIRR computed from stock buy/sell transactions imported via CAS.",
}


@router.get("/performance")
def performance(
    profile_id: int | None = None,
    asset_type: str = "all",
    folio_number: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Portfolio value over time + XIRR, optionally scoped to one asset type.

    The value-over-time series is built from each uploaded CAS's own
    trailing-12-month valuation trend table (whole portfolio: demat + MF +
    NPS combined) — uploading CAS files spread across years builds up a
    continuous multi-year history as the trailing windows overlap.

    `asset_type` scopes the XIRR figure only (mutual_funds | stocks | all) —
    those are the only asset classes with dated transaction history to
    compute a real XIRR from. `folio_number` further narrows to a single
    mutual fund folio and is only honoured when `asset_type=mutual_funds`.
    """
    if asset_type not in XIRR_ASSET_TYPES:
        raise HTTPException(status_code=400, detail=f"asset_type must be one of {XIRR_ASSET_TYPES}")
    if folio_number is not None and asset_type != "mutual_funds":
        raise HTTPException(status_code=400, detail="folio_number is only valid with asset_type=mutual_funds")

    if profile_id is not None:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile_ids = [profile_id]
    else:
        profile_ids = [p.id for p in db.query(Profile).all()]

    rows = (
        db.query(PortfolioSnapshot)
        .filter(PortfolioSnapshot.profile_id.in_(profile_ids))
        .all()
    )
    by_month: dict[date, float] = {}
    for r in rows:
        by_month[r.snapshot_month] = by_month.get(r.snapshot_month, 0.0) + r.total_value

    value_over_time = [
        {"month": m.isoformat(), "total_value": round(v, 2)}
        for m, v in sorted(by_month.items())
    ]

    note = _XIRR_NOTES[asset_type]
    if folio_number is not None:
        note = f"XIRR computed from transactions in folio {folio_number} only."

    return {
        "value_over_time": value_over_time,
        "xirr_pct": (
            _xirr_for_asset_type(asset_type, profile_ids, db, folio_number) if profile_ids else None
        ),
        "xirr_asset_type": asset_type,
        "xirr_note": note,
    }


@router.get("/xirr")
def xirr_endpoint(
    profile_id: int | None = None,
    asset_type: str = "all",
    folio_number: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """XIRR for a single profile or consolidated across all profiles, scoped
    to one asset type (mutual_funds | stocks | all), and optionally a single
    mutual fund folio."""
    if asset_type not in XIRR_ASSET_TYPES:
        raise HTTPException(status_code=400, detail=f"asset_type must be one of {XIRR_ASSET_TYPES}")
    if folio_number is not None and asset_type != "mutual_funds":
        raise HTTPException(status_code=400, detail="folio_number is only valid with asset_type=mutual_funds")

    if profile_id is not None:
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile_ids = [profile_id]
    else:
        profile_ids = [p.id for p in db.query(Profile).all()]

    return {
        "xirr_pct": (
            _xirr_for_asset_type(asset_type, profile_ids, db, folio_number) if profile_ids else None
        ),
        "asset_type": asset_type,
    }
