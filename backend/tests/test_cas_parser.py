"""Unit tests for the CDSL consolidated CAS parser.

Fixture text below is fabricated to mimic the real document's structure
(verified against a real CDSL CAS during development) — no real personal
data (PAN, folio numbers, holdings) is used anywhere in these tests.
"""
from datetime import date

from services.cas_parser import (
    Transaction,
    _classify_tx_type,
    _extract_statement_date,
    _is_cdsl_consolidated,
    _parse_date,
    _parse_demat_holdings,
    _parse_mf_rta_section,
    _parse_nps_section,
    _parse_number,
    _parse_portfolio_valuation_trend,
    _split_amc_scheme,
    deduplicate_transactions,
)

SAMPLE_CDSL_TEXT = """
SECURITIES HELD IN DEMAT
CONSOLIDATED ACCOUNT STATEMENT (CAS) FOR SECURITIES HELD IN DEMAT
FORM AND INVESTMENTS IN MUTUAL FUNDS FOR THE PERIOD FROM 01-07-2026
TO 31-07-2026

TESTUSER SAMPLE ( PAN :ABCDE1234F )

MF Folios
AMC Name : Sample Mutual Fund
Scheme Name : Sample Growth Fund - Direct Plan Scheme Code : SGF1
Folio No : 11112222/0 Mode of Holding : Single
ISIN : INF111100001 UCC : SAMPLE001 RTA : CAMS

AMC Name : Sample Mutual Fund
Scheme Name : Sample Debt Fund - Direct Plan Scheme Code : SDF1
Folio No : 11112222/0 Mode of Holding : Single
ISIN : INF111100002 UCC : SAMPLE002 RTA : CAMS

NPS-SP : SAMPLE PRAN ID : 111122223333

HOLDING STATEMENT AS ON 31-07-2026
Some AMC Ltd#Some MF-Demat Held Fund-Growth
INF999900009 500.000 -- -- -- 500.000 20.0000 10000.00

Sample Equity Description Line
INE999900001 SAMPLE EQUITY LIMITED 10.000 -- -- -- 10.000 100.0000 1000.00

ISIN : INF111100001 UCC : SAMPLE001
Opening Balance 100.000
13-07-2026 Purchase - Systematic- SIP Instalment 5/12 5000.00 50.0000 50.0000 100.000 .10 0 0
Closing Balance 200.000

Sample Growth Fund - Direct Plan INF111100001 11112222/0 200.000 55.0000 10000.00 11000.00 1000.00 10.00
Sample Debt Fund - Direct Plan INF111100002 11112222/0 50.000 20.0000 900.00 1000.00 100.00 11.11
Grand Total 10900.00 12000.00

NPS PRAN HELD WITH CRA
NPS-SP : SAMPLE PRAN ID : 111122223333
Tier Status : 1
NPS TRUST- A/C SAMPLE PENSION FUND
MANAGEMENT LIMITED SCHEME E - TIER I HDFC Pension Fund Management Ltd 100.0000 50.0000
POP
NPS TRUST- A/C SAMPLE PENSION FUND
MANAGEMENT LIMITED SCHEME C - TIER I HDFC Pension Fund Management Ltd 200.0000 30.0000
POP
Portfolio Value ` 11000.00 as on 31-07-2026

Portfolio Valuation
Aug 2025 100000.00
Sep 2025 110000.00 10000.00 10.00
Asset Class Value Percentage
"""


# ── Small pure-function helpers ────────────────────────────────────────────

def test_parse_number_handles_indian_grouping():
    assert _parse_number("1,23,456.78") == 123456.78


def test_parse_number_returns_none_for_empty_or_invalid():
    assert _parse_number("") is None
    assert _parse_number("not-a-number") is None


def test_parse_date_supports_all_known_formats():
    assert _parse_date("13-Jul-2026") == date(2026, 7, 13)
    assert _parse_date("13/07/2026") == date(2026, 7, 13)
    assert _parse_date("13-July-2026") == date(2026, 7, 13)
    assert _parse_date("13-07-2026") == date(2026, 7, 13)   # the format that was silently dropping txns


def test_parse_date_returns_none_for_garbage():
    assert _parse_date("not a date") is None


def test_classify_tx_type_recognizes_sip_synonyms():
    assert _classify_tx_type("Purchase - Systematic- Normal - Instalment 5/12") == "sip"
    assert _classify_tx_type("Redemption of units") == "redemption"
    assert _classify_tx_type("Dividend Payout") == "dividend"
    assert _classify_tx_type("Switch In from another scheme") == "switch_in"
    assert _classify_tx_type("Additional Purchase") == "purchase"


def test_split_amc_scheme_with_hash_separator():
    amc, scheme = _split_amc_scheme("HDFC AMC LTD#HDFC MF-HDFC Balanced Advantage Fund-Growth")
    assert amc == "HDFC AMC LTD"
    assert scheme == "HDFC Balanced Advantage Fund-Growth"


def test_split_amc_scheme_without_hash_separator():
    amc, scheme = _split_amc_scheme("Some Fund Name With No Hash")
    assert amc == "Unknown AMC"
    assert scheme == "Some Fund Name With No Hash"


def test_deduplicate_transactions_filters_existing_and_keeps_new():
    existing = [{
        "folio_number": "11112222/0",
        "transaction_date": date(2026, 7, 13),
        "transaction_type": "sip",
        "units": 100.0,
        "amount": 5000.0,
    }]
    incoming = [
        Transaction("11112222/0", date(2026, 7, 13), "sip", 100.0, 50.0, 5000.0, "dup"),
        Transaction("11112222/0", date(2026, 8, 13), "sip", 100.0, 50.0, 5000.0, "new"),
    ]
    result = deduplicate_transactions(existing, incoming)
    assert len(result) == 1
    assert result[0].description == "new"


# ── CDSL format detection & statement date ─────────────────────────────────

def test_is_cdsl_consolidated_detects_demat_marker():
    assert _is_cdsl_consolidated(SAMPLE_CDSL_TEXT) is True
    assert _is_cdsl_consolidated("plain CAMS statement, nothing special") is False


def test_extract_statement_date_reads_period_end():
    assert _extract_statement_date(SAMPLE_CDSL_TEXT) == date(2026, 7, 31)


# ── MF RTA folio section: identity + valuation + transactions ─────────────

def test_mf_rta_section_builds_one_folio_per_scheme():
    folios = _parse_mf_rta_section(SAMPLE_CDSL_TEXT)
    assert len(folios) == 2

    growth = next(f for f in folios if f.isin == "INF111100001")
    assert growth.folio_number == "11112222/0"
    assert growth.amc_name == "Sample Mutual Fund"
    assert growth.scheme_name == "Sample Growth Fund - Direct Plan"
    assert growth.units_held == 200.0
    assert growth.current_value == 11000.0

    debt = next(f for f in folios if f.isin == "INF111100002")
    assert debt.units_held == 50.0
    assert debt.current_value == 1000.0


def test_mf_rta_section_parses_transaction_with_correct_column_order():
    folios = _parse_mf_rta_section(SAMPLE_CDSL_TEXT)
    growth = next(f for f in folios if f.isin == "INF111100001")
    assert len(growth.transactions) == 1

    txn = growth.transactions[0]
    assert txn.transaction_date == date(2026, 7, 13)
    assert txn.transaction_type == "sip"
    assert txn.amount == 5000.0
    assert txn.nav == 50.0
    assert txn.units == 100.0                 # not 50.0 — that's the (skipped) duplicate price column
    assert txn.folio_number == "11112222/0"    # resolved via closing-balance match, not stated in-block


def test_mf_rta_section_scheme_with_no_activity_has_no_transactions():
    folios = _parse_mf_rta_section(SAMPLE_CDSL_TEXT)
    debt = next(f for f in folios if f.isin == "INF111100002")
    assert debt.transactions == []


# ── Demat holdings: equities vs MF-in-demat ────────────────────────────────

def test_parse_demat_holdings_splits_equity_from_mf_in_demat():
    equities, mf_in_demat = _parse_demat_holdings(SAMPLE_CDSL_TEXT)

    assert len(equities) == 1
    assert equities[0].isin == "INE999900001"
    assert equities[0].quantity == 10.0
    assert equities[0].market_price == 100.0
    assert equities[0].current_value == 1000.0

    assert len(mf_in_demat) == 1
    assert mf_in_demat[0].isin == "INF999900009"
    assert mf_in_demat[0].folio_number == "DEMAT-INF999900009"
    assert mf_in_demat[0].units_held == 500.0
    assert mf_in_demat[0].current_value == 10000.0


def test_parse_demat_holdings_ignores_mf_valuation_table_rows():
    """The MF RTA valuation table also has an ISIN followed by numbers on one
    line ('<scheme> <isin> <folio> <units> ...') — the folio token ('N/N')
    must exclude those rows from being misread as demat holdings."""
    equities, mf_in_demat = _parse_demat_holdings(SAMPLE_CDSL_TEXT)
    all_isins = {e.isin for e in equities} | {f.isin for f in mf_in_demat}
    assert "INF111100001" not in all_isins
    assert "INF111100002" not in all_isins


# ── NPS ─────────────────────────────────────────────────────────────────────

def test_parse_nps_section_computes_scheme_breakdown():
    accounts = _parse_nps_section(SAMPLE_CDSL_TEXT)
    assert len(accounts) == 1
    acct = accounts[0]

    assert acct.pran_number == "111122223333"
    assert acct.tier == "Tier1"
    assert acct.fund_manager == "HDFC Pension Fund Management Ltd"
    assert acct.current_value == 11000.0
    # scheme E value = 100 * 50 = 5000; scheme C value = 200 * 30 = 6000; total = 11000
    assert acct.equity_pct == round(5000 / 11000 * 100, 2)
    assert acct.corporate_bond_pct == round(6000 / 11000 * 100, 2)
    assert acct.govt_bond_pct == 0.0


def test_parse_nps_section_returns_empty_when_no_nps_present():
    assert _parse_nps_section("some unrelated text with no NPS section") == []


# ── Portfolio valuation trend ───────────────────────────────────────────────

def test_parse_portfolio_valuation_trend_reads_month_rows():
    rows = _parse_portfolio_valuation_trend(SAMPLE_CDSL_TEXT)
    assert rows == [
        {"month": date(2025, 8, 1), "total_value": 100000.0},
        {"month": date(2025, 9, 1), "total_value": 110000.0},
    ]


def test_parse_portfolio_valuation_trend_empty_when_table_absent():
    assert _parse_portfolio_valuation_trend("no trend table here") == []
