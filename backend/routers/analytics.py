"""Analytics endpoints — net worth, allocation, XIRR, price refresh.

Phase 2: net worth + allocation + manual price refresh.
Phase 3: XIRR, benchmark comparison, tax insights.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user
from models.user import User
from models.profile import Profile
from models.mutual_fund import MutualFundHolding
from models.stock import StockHolding
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


@router.get("/xirr")
def xirr_endpoint(
    profile_id: int | None = None,
    folio_number: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """XIRR calculation — Phase 3 implementation."""
    raise HTTPException(status_code=501, detail="XIRR will be implemented in Phase 3.")
