"""Tests for the CAS -> DB upsert logic in routers/cas.py, focused on the
statement-date guard: an older CAS upload must never overwrite a holding's
current units/value/price with stale numbers, regardless of upload order.
"""
from datetime import date

from models.mutual_fund import MutualFundHolding
from models.nps import NPS
from models.stock import StockHolding
from routers.cas import _upsert_equity_holding, _upsert_holding, _upsert_nps
from services.cas_parser import EquityHolding, FolioHolding, NPSHoldingData

JULY = date(2026, 7, 31)
JANUARY = date(2026, 1, 31)   # older than JULY


def _folio(units, value, folio_number="F1", isin="INF000000001", scheme_name="Scheme A"):
    return FolioHolding(
        folio_number=folio_number, scheme_name=scheme_name, scheme_code="SC1",
        isin=isin, amc_name="Test AMC", units_held=units, current_value=value,
        transactions=[],
    )


def _equity(quantity, price, isin="INE000000001", name="Test Equity"):
    return EquityHolding(isin=isin, name=name, quantity=quantity, market_price=price, current_value=quantity * price)


def _nps(current_value, pran="1234567890"):
    return NPSHoldingData(
        pran_number=pran, tier="Tier1", fund_manager="Test Fund Manager",
        current_value=current_value, equity_pct=50.0, corporate_bond_pct=30.0, govt_bond_pct=20.0,
    )


# ── Mutual fund holdings ────────────────────────────────────────────────────

def test_upsert_holding_creates_new_row(db_session, profile_id):
    _upsert_holding(db_session, profile_id, _folio(100.0, 5000.0), JULY)
    db_session.commit()

    rows = db_session.query(MutualFundHolding).all()
    assert len(rows) == 1
    assert rows[0].units_held == 100.0
    assert rows[0].current_value == 5000.0
    assert rows[0].cas_statement_date == JULY


def test_upsert_holding_newer_statement_overwrites_snapshot(db_session, profile_id):
    _upsert_holding(db_session, profile_id, _folio(100.0, 5000.0), JANUARY)
    db_session.commit()

    _upsert_holding(db_session, profile_id, _folio(150.0, 8000.0), JULY)
    db_session.commit()

    row = db_session.query(MutualFundHolding).one()
    assert row.units_held == 150.0
    assert row.current_value == 8000.0
    assert row.cas_statement_date == JULY


def test_upsert_holding_older_statement_does_not_clobber_snapshot(db_session, profile_id):
    """The bug this guards against: uploading a historical CAS after the
    current one must not roll the portfolio view back to stale numbers."""
    _upsert_holding(db_session, profile_id, _folio(150.0, 8000.0), JULY)
    db_session.commit()

    _upsert_holding(db_session, profile_id, _folio(100.0, 5000.0), JANUARY)
    db_session.commit()

    row = db_session.query(MutualFundHolding).one()
    assert row.units_held == 150.0
    assert row.current_value == 8000.0
    assert row.cas_statement_date == JULY


def test_upsert_holding_unknown_statement_date_is_permissive(db_session, profile_id):
    """A CAS whose statement date couldn't be parsed still updates the
    snapshot — we have no basis to say it's older, so default to allowing it."""
    _upsert_holding(db_session, profile_id, _folio(150.0, 8000.0), JULY)
    db_session.commit()

    _upsert_holding(db_session, profile_id, _folio(200.0, 9000.0), None)
    db_session.commit()

    row = db_session.query(MutualFundHolding).one()
    assert row.units_held == 200.0
    assert row.current_value == 9000.0


def test_upsert_holding_same_folio_different_schemes_creates_two_rows(db_session, profile_id):
    """A single folio can hold multiple schemes — folio_number alone must
    not collapse them into one row (the original bug)."""
    _upsert_holding(db_session, profile_id, _folio(100.0, 5000.0, folio_number="F1", isin="INF111", scheme_name="Scheme A"), JULY)
    _upsert_holding(db_session, profile_id, _folio(50.0, 2000.0, folio_number="F1", isin="INF222", scheme_name="Scheme B"), JULY)
    db_session.commit()

    rows = db_session.query(MutualFundHolding).filter(MutualFundHolding.folio_number == "F1").all()
    assert len(rows) == 2
    assert {r.scheme_name for r in rows} == {"Scheme A", "Scheme B"}


# ── Equity / demat holdings ─────────────────────────────────────────────────

def test_upsert_equity_holding_older_statement_does_not_clobber_snapshot(db_session, profile_id):
    _upsert_equity_holding(db_session, profile_id, _equity(10.0, 500.0), JULY)
    db_session.commit()

    _upsert_equity_holding(db_session, profile_id, _equity(5.0, 400.0), JANUARY)
    db_session.commit()

    row = db_session.query(StockHolding).one()
    assert row.quantity == 10.0
    assert row.current_price == 500.0
    assert row.ticker == "INE000000001"   # ISIN used as ticker placeholder


def test_upsert_equity_holding_newer_statement_overwrites_snapshot(db_session, profile_id):
    _upsert_equity_holding(db_session, profile_id, _equity(10.0, 500.0), JANUARY)
    db_session.commit()

    _upsert_equity_holding(db_session, profile_id, _equity(20.0, 600.0), JULY)
    db_session.commit()

    row = db_session.query(StockHolding).one()
    assert row.quantity == 20.0
    assert row.current_price == 600.0


# ── NPS ─────────────────────────────────────────────────────────────────────

def test_upsert_nps_older_statement_does_not_clobber_snapshot(db_session, profile_id):
    _upsert_nps(db_session, profile_id, _nps(100000.0), JULY)
    db_session.commit()

    _upsert_nps(db_session, profile_id, _nps(80000.0), JANUARY)
    db_session.commit()

    row = db_session.query(NPS).one()
    assert row.current_value == 100000.0


def test_upsert_nps_newer_statement_overwrites_snapshot(db_session, profile_id):
    _upsert_nps(db_session, profile_id, _nps(80000.0), JANUARY)
    db_session.commit()

    _upsert_nps(db_session, profile_id, _nps(100000.0), JULY)
    db_session.commit()

    row = db_session.query(NPS).one()
    assert row.current_value == 100000.0
