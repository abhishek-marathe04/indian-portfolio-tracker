"""CAS PDF parser — supports CAMS and KFintech Consolidated Account Statements.

Usage:
    result = parse_cas_pdf(pdf_bytes, password="ABCDE123401011990")
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import pdfplumber
import PyPDF2

# ── Regex patterns ────────────────────────────────────────────────────────────

# CAS type detection
_CAMS_RE = re.compile(r'\bCAMS\b|Computer Age Management Services', re.IGNORECASE)
_KFIN_RE = re.compile(r'\bKFin\b|\bKarvy\b|\bKFINTECH\b', re.IGNORECASE)

# Investor info
_PAN_RE = re.compile(r'PAN\s*[:\-]?\s*([A-Z]{5}\d{4}[A-Z])', re.IGNORECASE)
_INVESTOR_CAMS_RE = re.compile(r'Investor\s*:\s*(.+?)(?:\n|\r|Email|Mobile|PAN)', re.IGNORECASE | re.DOTALL)
_INVESTOR_KFIN_RE = re.compile(r'(?:^|\n)\s*Name\s*:\s*(.+?)(?:\n|\r)', re.IGNORECASE)

# Folio — "Folio No: 12345678 / 90" or "Folio No: 12345678/90" or without spaces
_FOLIO_RE = re.compile(r'Folio\s+No[.:\-]?\s*(\S+(?:\s*/\s*\S+)?)', re.IGNORECASE)

# AMC / scheme block separators (lines of dashes or equals)
_SEPARATOR_RE = re.compile(r'^[-=]{10,}', re.MULTILINE)

# ISIN
_ISIN_RE = re.compile(r'\bINF[A-Z0-9]{9}\b|\bIN[A-Z0-9]{10}\b')

# Transaction line — one of several formats:
# DD-Mon-YYYY  description  amount   units   nav   balance
# DD/MM/YYYY  description  amount   units   nav   balance
_DATE_RE = re.compile(r'\b(\d{2}[-/]\w{3}[-/]\d{4}|\d{2}/\d{2}/\d{4})\b')
_NUMBER_RE = re.compile(r'[\d,]+\.\d+')

# Statement period end date — "...FOR THE PERIOD FROM 01-07-2026 ... TO 31-07-2026"
# or "... AS ON 31-07-2026" — used as the snapshot date for holdings.
_STATEMENT_TO_RE = re.compile(r'\bTO\s+(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}[-/]\w{3}[-/]\d{4})\b')
_STATEMENT_ASOF_RE = re.compile(r'as\s+on\s+(\d{2}[-/]\d{2}[-/]\d{4}|\d{2}[-/]\w{3}[-/]\d{4})', re.IGNORECASE)

# Closing balance
_CLOSING_RE = re.compile(
    r'Closing\s+(?:Unit\s+)?Balance\s*[:\-]?\s*([\d,]+\.?\d*)',
    re.IGNORECASE,
)

# Opening balance
_OPENING_RE = re.compile(
    r'Opening\s+(?:Unit\s+)?Balance\s*[:\-]?\s*([\d,]+\.?\d*)',
    re.IGNORECASE,
)

# Current / market value
_MARKET_VALUE_RE = re.compile(
    r'(?:Market Value|Current Value)\s+as\s+on\s+[\w\-]+\s*[:\-]?\s*(?:Rs\.?\s*)?([\d,]+\.?\d*)',
    re.IGNORECASE,
)

# Transaction type keywords
_TYPE_MAP = [
    ('switch_in',   re.compile(r'switch\s*in', re.IGNORECASE)),
    ('switch_out',  re.compile(r'switch\s*out', re.IGNORECASE)),
    ('redemption',  re.compile(r'redempt|redeem', re.IGNORECASE)),
    ('dividend',    re.compile(r'dividend|div\s', re.IGNORECASE)),
    ('sip',         re.compile(r'\bsip\b|systematic|instalment|installment', re.IGNORECASE)),
    ('purchase',    re.compile(r'purchase|subscript|new|addition', re.IGNORECASE)),
]

# ── CDSL consolidated CAS (demat + MF folios + NPS bundled in one PDF) ────────

_CDSL_CONSOLIDATED_RE = re.compile(
    r'SECURITIES\s+HELD\s+IN\s+DEMAT|Central\s+Depository\s+Services', re.IGNORECASE
)
_INVESTOR_CDSL_RE = re.compile(r'([A-Z][A-Z .]{4,60})\s*\(\s*PAN\s*:\s*[A-Z]{5}\d{4}[A-Z]\s*\)')

_MF_VALUATION_ROW_RE = re.compile(
    r'(INF[A-Z0-9]{9})\s+(\d+/\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+'
    r'([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+(-?[\d,]+\.\d+)\s+(-?[\d,]+\.\d+)'
)
_SCHEME_HEADER_RE = re.compile(r'ISIN\s*:\s*(INF[A-Z0-9]{9})\s+UCC\s*:\s*(\S+)')
_MF_TXN_LINE_RE = re.compile(r'^\s*(\d{2}-\d{2}-\d{4})\s+(.*)')
_MF_OPENING_RE = re.compile(r'Opening Balance\s+([\d,]+\.\d+)')
_MF_CLOSING_RE = re.compile(r'Closing Balance\s+([\d,]+\.\d+)')

_HOLDING_ROW_RE = re.compile(
    r'\b(IN[A-Z0-9]{10})\b(.*?)\s+'
    r'((?:[\d,]+\.\d+|--)(?:\s+(?:[\d,]+\.\d+|--)){2,7})\s*$'
)

_NPS_PRAN_RE = re.compile(r'PRAN\s*ID\s*:\s*(\d+)')
_NPS_TIER_RE = re.compile(r'Tier\s*Status\s*:\s*(\d)')
_NPS_SCHEME_ROW_RE = re.compile(
    r'SCHEME\s+([A-Z])\s*-\s*TIER\s*I\b[^\n]*?'
    r'([A-Za-z .]+?Pension Fund Management\s*(?:Ltd|Limited)?)\s+'
    r'([\d,]+\.\d+)\s+([\d,]+\.\d+)'
)
_NPS_PORTFOLIO_VALUE_RE = re.compile(r'Portfolio Value\s*`?\s*([\d,]+\.\d+)')
_NPS_SCHEME_PCT_FIELD = {'E': 'equity_pct', 'C': 'corporate_bond_pct', 'G': 'govt_bond_pct'}

_MONTH_ABBR = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
}
_TREND_ROW_RE = re.compile(
    r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s+([\d,]+\.\d+)',
    re.MULTILINE,
)


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class Transaction:
    folio_number: str
    transaction_date: date
    transaction_type: str        # purchase | redemption | sip | switch_in | switch_out | dividend
    units: float | None
    nav: float | None
    amount: float | None
    description: str


@dataclass
class FolioHolding:
    folio_number: str
    scheme_name: str
    scheme_code: str | None       # AMFI code (not always in CAS)
    isin: str | None
    amc_name: str
    units_held: float
    current_value: float | None
    transactions: list[Transaction] = field(default_factory=list)


@dataclass
class EquityHolding:
    isin: str
    name: str
    quantity: float
    market_price: float | None
    current_value: float | None
    broker: str | None = None


@dataclass
class NPSHoldingData:
    pran_number: str | None
    tier: str
    fund_manager: str | None
    current_value: float | None
    equity_pct: float | None
    corporate_bond_pct: float | None
    govt_bond_pct: float | None


@dataclass
class CASResult:
    investor_name: str
    pan: str | None
    cas_type: str                  # "CAMS" | "KFintech" | "CDSL-Consolidated" | "unknown"
    folios: list[FolioHolding]
    equity_holdings: list[EquityHolding] = field(default_factory=list)
    nps_accounts: list[NPSHoldingData] = field(default_factory=list)
    portfolio_snapshots: list[dict] = field(default_factory=list)   # [{'month': date, 'total_value': float}]
    statement_date: date | None = None   # CAS period-end date — snapshot "as of" date
    raw_text: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_number(s: str) -> float | None:
    """Convert '1,23,456.78' → 123456.78."""
    if not s:
        return None
    try:
        return float(s.replace(',', ''))
    except ValueError:
        return None


def _parse_date(s: str) -> date | None:
    """Parse DD-Mon-YYYY or DD/MM/YYYY → date."""
    s = s.strip()
    for fmt in ('%d-%b-%Y', '%d/%m/%Y', '%d-%B-%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _classify_tx_type(desc: str) -> str:
    for tx_type, pattern in _TYPE_MAP:
        if pattern.search(desc):
            return tx_type
    return 'purchase'


def _extract_text(pdf_bytes: bytes, password: str) -> str:
    """Decrypt and extract all text from a PDF."""
    # Try pdfplumber directly (handles most CAS PDFs)
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes), password=password) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=3)
                if text:
                    pages.append(text)
            if pages:
                return '\n'.join(pages)
    except Exception:
        pass

    # Fallback: decrypt with PyPDF2, then re-open with pdfplumber
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    if reader.is_encrypted:
        result = reader.decrypt(password)
        if result == 0:
            raise ValueError(
                "Incorrect PDF password. "
                "For CAS PDFs the password is typically your PAN (uppercase) + date of birth (DDMMYYYY)."
            )

    # Write decrypted version in memory and open with pdfplumber
    writer = PyPDF2.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)

    with pdfplumber.open(buf) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=3)
            if text:
                pages.append(text)
        return '\n'.join(pages)


# ── Core parser ───────────────────────────────────────────────────────────────

def _extract_statement_date(text: str) -> date | None:
    m = _STATEMENT_TO_RE.search(text[:3000])
    if not m:
        m = _STATEMENT_ASOF_RE.search(text[:3000])
    if not m:
        return None
    return _parse_date(m.group(1).replace('/', '-'))


def _detect_cas_type(text: str) -> str:
    if _CAMS_RE.search(text[:2000]):
        return 'CAMS'
    if _KFIN_RE.search(text[:2000]):
        return 'KFintech'
    return 'unknown'


def _extract_investor_info(text: str, cas_type: str) -> tuple[str, str | None]:
    """Return (investor_name, pan)."""
    name = 'Unknown'

    if cas_type == 'CAMS':
        m = _INVESTOR_CAMS_RE.search(text[:3000])
        if m:
            name = m.group(1).strip().split('\n')[0].strip()
    else:
        m = _INVESTOR_KFIN_RE.search(text[:3000])
        if m:
            name = m.group(1).strip()

    if name == 'Unknown':
        m = _INVESTOR_CDSL_RE.search(text[:5000])
        if m:
            name = m.group(1).strip()

    pan_m = _PAN_RE.search(text[:5000])
    pan = pan_m.group(1).upper() if pan_m else None
    return name, pan


def _split_amc_blocks(text: str) -> list[tuple[str, str]]:
    """Split the CAS text into (amc_name, block_text) pairs.

    Heuristic: AMC sections are separated by lines of dashes/equals OR by
    lines in ALL CAPS that precede a "Folio No" line.
    """
    # Strategy: find every occurrence of "Folio No" and walk backwards to find
    # the AMC name, then collect the text until the next folio marker.
    folio_positions = [m.start() for m in _FOLIO_RE.finditer(text)]
    if not folio_positions:
        return []

    blocks = []
    for i, pos in enumerate(folio_positions):
        end = folio_positions[i + 1] if i + 1 < len(folio_positions) else len(text)
        block = text[max(0, pos - 500): end]   # include some context before

        # Try to extract AMC name: last ALL-CAPS line before the folio line
        before = text[max(0, pos - 500): pos]
        lines = [l.strip() for l in before.split('\n') if l.strip()]
        amc_name = 'Unknown AMC'
        for line in reversed(lines[-10:]):
            # AMC names are usually >= 5 chars, mixed or all caps, end without ':'
            if len(line) >= 5 and not line.endswith(':') and not _FOLIO_RE.search(line):
                amc_name = line
                break

        blocks.append((amc_name, text[pos:end]))

    return blocks


def _parse_folio_block(amc_name: str, block: str) -> FolioHolding | None:
    """Parse a single folio block into a FolioHolding."""
    # Folio number
    folio_m = _FOLIO_RE.search(block)
    if not folio_m:
        return None
    folio_number = folio_m.group(1).replace(' ', '')

    # Scheme name: usually the first non-empty line after the folio line
    folio_end = folio_m.end()
    after_folio = block[folio_end:folio_end + 400]
    lines_after = [l.strip() for l in after_folio.split('\n') if l.strip()]

    scheme_name = 'Unknown Scheme'
    isin = None
    for line in lines_after[:5]:
        if 'ISIN' in line.upper():
            # e.g. "HDFC Top 100 Fund - Growth (ISIN: INF179K01HF5)"
            isin_m = _ISIN_RE.search(line)
            if isin_m:
                isin = isin_m.group(0)
            scheme_name = re.sub(r'\s*\(ISIN\s*:.*?\)', '', line).strip()
            break
        # Skip lines that look like metadata (Advisor, Nominee, Mode)
        if re.match(r'(Advisor|Nominee|Mode|Registrar|KYC)', line, re.IGNORECASE):
            continue
        if len(line) > 5:
            scheme_name = line
            # Check if ISIN is on the same line without parens
            isin_m = _ISIN_RE.search(line)
            if isin_m:
                isin = isin_m.group(0)
            break

    # Closing balance (units held)
    closing_m = _CLOSING_RE.search(block)
    units_held = _parse_number(closing_m.group(1)) if closing_m else 0.0

    # Current / market value
    mv_m = _MARKET_VALUE_RE.search(block)
    current_value = _parse_number(mv_m.group(1)) if mv_m else None

    # Parse transactions
    transactions = _parse_transactions(folio_number, block)

    return FolioHolding(
        folio_number=folio_number,
        scheme_name=scheme_name,
        scheme_code=None,   # AMFI code not in CAS; will be resolved via mfapi.in later
        isin=isin,
        amc_name=amc_name,
        units_held=units_held or 0.0,
        current_value=current_value,
        transactions=transactions,
    )


def _parse_transactions(folio_number: str, block: str) -> list[Transaction]:
    """Extract transactions from a folio block using a line-by-line scanner."""
    transactions: list[Transaction] = []

    lines = block.split('\n')
    for line in lines:
        # A transaction line must start with a date
        date_m = re.match(r'\s*(\d{2}[-/]\w{3}[-/]\d{4}|\d{2}/\d{2}/\d{4})\s+(.*)', line)
        if not date_m:
            continue

        date_str = date_m.group(1)
        rest = date_m.group(2).strip()

        tx_date = _parse_date(date_str)
        if tx_date is None:
            continue

        # Extract numbers from the rest of the line
        numbers = [_parse_number(n) for n in _NUMBER_RE.findall(rest)]

        # Remove numbers from rest to get description
        desc = _NUMBER_RE.sub('', rest).strip(' |-')
        # Clean up repeated spaces
        desc = re.sub(r'\s{2,}', ' ', desc).strip()

        # Numbers in a CAMS transaction line are typically:
        # amount  units  nav  balance  (4 numbers)
        # Or for opening/closing: just the unit balance
        amount = nav = units = None
        if len(numbers) >= 3:
            amount = numbers[0]
            units = numbers[1]
            nav = numbers[2]
        elif len(numbers) == 2:
            amount = numbers[0]
            units = numbers[1]
        elif len(numbers) == 1:
            units = numbers[0]

        tx_type = _classify_tx_type(desc)

        # Skip "Opening Balance" pseudo-transactions
        if re.search(r'opening\s+balance', desc, re.IGNORECASE):
            continue

        transactions.append(Transaction(
            folio_number=folio_number,
            transaction_date=tx_date,
            transaction_type=tx_type,
            units=units,
            nav=nav,
            amount=amount,
            description=desc,
        ))

    return transactions


# ── CDSL consolidated CAS parsing ──────────────────────────────────────────────
#
# A CDSL/NSDL "master" CAS bundles three unrelated sections in one PDF: demat
# holdings (equities + MF units bought via demat), MF folios held with an RTA
# (CAMS/KFin), and NPS. Headers/footers are bilingual (Hindi+English rendered
# character-interleaved by pdfplumber) and unusable for parsing, but the actual
# data rows are clean. Each section below is parsed independently and anchored
# on data patterns rather than section-title text, since the titles are often
# garbled while the data rows are not.

def _is_cdsl_consolidated(text: str) -> bool:
    return bool(_CDSL_CONSOLIDATED_RE.search(text[:3000]))


def _split_amc_scheme(raw_name: str) -> tuple[str, str]:
    """Split a demat security name of the form 'AMC LTD#AMC MF-Scheme Name'."""
    if '#' in raw_name:
        amc, rest = raw_name.split('#', 1)
        scheme = re.sub(r'^\S+\s+MF-', '', rest).strip()
        return amc.strip(), (scheme or rest.strip())
    return 'Unknown AMC', raw_name


def _parse_mf_identity(text: str) -> dict[tuple[str, str], dict]:
    """Map (folio_number, isin) -> {amc_name, scheme_name, scheme_code} from
    the clean 'MF Folios' account-details block (not the garbled RTA statement)."""
    start = text.find('MF Folios')
    end = text.find('NPS-SP')
    section = text[start:end] if start != -1 and end != -1 else text

    records: dict[tuple[str, str], dict] = {}
    for block in re.split(r'(?=AMC Name\s*:)', section)[1:]:
        amc_m = re.match(r'AMC Name\s*:\s*(.+)', block)
        scheme_m = re.search(r'Scheme Name\s*:\s*(.+?)\s+Scheme Code\s*:\s*(\S+)', block)
        folio_m = re.search(r'Folio No\s*:\s*(\S+)', block)
        isin_m = re.search(r'ISIN\s*:\s*(\S+)', block)
        if not (amc_m and scheme_m and folio_m and isin_m):
            continue
        key = (folio_m.group(1).strip(), isin_m.group(1).strip())
        records[key] = {
            'amc_name': amc_m.group(1).strip(),
            'scheme_name': scheme_m.group(1).strip(),
            'scheme_code': scheme_m.group(2).strip(),
        }
    return records


def _parse_mf_valuation_rows(text: str) -> list[dict]:
    """Parse the RTA-held MF valuation/summary table — the authoritative
    current snapshot of units held and market value per (isin, folio)."""
    rows = []
    for m in _MF_VALUATION_ROW_RE.finditer(text):
        rows.append({
            'isin': m.group(1),
            'folio_number': m.group(2),
            'units': _parse_number(m.group(3)),
            'nav': _parse_number(m.group(4)),
            'invested': _parse_number(m.group(5)),
            'current_value': _parse_number(m.group(6)),
        })
    return rows


def _parse_mf_rta_blocks(text: str) -> list[tuple[str, str]]:
    """Return (isin, block_text) for each real per-scheme transaction block.

    'ISIN : X UCC : Y' also appears in the clean identity section (one per
    folio), so a candidate is only kept if it's actually followed by an
    Opening/Closing Balance line before the next anchor — that's true only
    for the real RTA transaction-statement blocks.
    """
    anchors = list(_SCHEME_HEADER_RE.finditer(text))
    blocks = []
    for i, m in enumerate(anchors):
        end = anchors[i + 1].start() if i + 1 < len(anchors) else len(text)
        segment = text[m.end():end]
        if 'Opening Balance' not in segment and 'Closing Balance' not in segment:
            continue
        blocks.append((m.group(1), segment))
    return blocks


def _parse_scheme_block_transactions(block: str) -> tuple[float | None, list[Transaction]]:
    """Parse Opening/Closing balance + transaction lines from one scheme block.
    Returns (closing_balance, transactions) — folio_number is resolved by the caller."""
    closing_m = _MF_CLOSING_RE.search(block)
    closing = _parse_number(closing_m.group(1)) if closing_m else None

    txns: list[Transaction] = []
    lines = block.split('\n')
    for idx, line in enumerate(lines):
        m = _MF_TXN_LINE_RE.match(line)
        if not m:
            continue
        tx_date = _parse_date(m.group(1))
        if tx_date is None:
            continue
        rest = m.group(2).strip()

        numbers = [_parse_number(n) for n in _NUMBER_RE.findall(rest)]
        desc = _NUMBER_RE.sub('', rest).strip(' |-')
        desc = re.sub(r'\s{2,}', ' ', desc).strip()

        if idx > 0:
            prev = lines[idx - 1].strip()
            if prev and not _MF_TXN_LINE_RE.match(prev) and 'Balance' not in prev and len(prev) < 60:
                desc = f'{prev} {desc}'.strip()

        # Column order in this format: amount, nav, price (dup of nav), units, ...
        amount = nav = units = None
        if len(numbers) >= 4:
            amount, nav, units = numbers[0], numbers[1], numbers[3]
        elif len(numbers) == 3:
            amount, nav, units = numbers[0], numbers[1], numbers[2]
        elif numbers:
            units = numbers[-1]

        txns.append(Transaction(
            folio_number='',   # resolved by caller once closing balance is known
            transaction_date=tx_date,
            transaction_type=_classify_tx_type(desc),
            units=units,
            nav=nav,
            amount=amount,
            description=desc,
        ))
    return closing, txns


def _resolve_folio_for_block(isin: str, closing: float | None, valuation_rows: list[dict]) -> str | None:
    candidates = [r for r in valuation_rows if r['isin'] == isin]
    if not candidates:
        return None
    if closing is not None:
        for r in candidates:
            if r['units'] is not None and abs(r['units'] - closing) < 0.01:
                return r['folio_number']
    return candidates[0]['folio_number']


def _parse_mf_rta_section(text: str) -> list[FolioHolding]:
    identity = _parse_mf_identity(text)
    valuation_rows = _parse_mf_valuation_rows(text)

    transactions_by_isin: dict[str, list[Transaction]] = {}
    for isin, block in _parse_mf_rta_blocks(text):
        closing, txns = _parse_scheme_block_transactions(block)
        folio_number = _resolve_folio_for_block(isin, closing, valuation_rows)
        for t in txns:
            t.folio_number = folio_number or ''
        transactions_by_isin.setdefault(isin, []).extend(txns)

    folios = []
    for row in valuation_rows:
        key = (row['folio_number'], row['isin'])
        ident = identity.get(key, {})
        folio_txns = [
            t for t in transactions_by_isin.get(row['isin'], [])
            if t.folio_number == row['folio_number']
        ]
        folios.append(FolioHolding(
            folio_number=row['folio_number'],
            scheme_name=ident.get('scheme_name', 'Unknown Scheme'),
            scheme_code=ident.get('scheme_code'),
            isin=row['isin'],
            amc_name=ident.get('amc_name', 'Unknown AMC'),
            units_held=row['units'] or 0.0,
            current_value=row['current_value'],
            transactions=folio_txns,
        ))
    return folios


def _parse_demat_holdings(text: str) -> tuple[list[EquityHolding], list[FolioHolding]]:
    """Parse the demat 'HOLDING STATEMENT' rows: <ISIN> <bal cols...> <price> <value>.
    INF-prefixed ISINs are mutual fund units held in demat form; everything
    else (equities, REITs, SGBs) is returned as an EquityHolding."""
    equities: list[EquityHolding] = []
    mf_in_demat: list[FolioHolding] = []

    lines = text.split('\n')
    for idx, line in enumerate(lines):
        m = _HOLDING_ROW_RE.search(line)
        if not m:
            continue
        if re.search(r'\d+/\d+', line):
            continue   # MF RTA valuation-table row (folio number token), not a demat holding
        isin = m.group(1)
        same_line_name = m.group(2).strip()
        tokens = m.group(3).split()
        if len(tokens) < 3:
            continue
        balance_str, price_str, value_str = tokens[-3], tokens[-2], tokens[-1]
        if '--' in (balance_str, price_str, value_str):
            continue
        quantity = _parse_number(balance_str) or 0.0
        price = _parse_number(price_str)
        value = _parse_number(value_str)

        def _is_noise(s: str) -> bool:
            return (not s or _ISIN_RE.search(s) or 'Value' in s
                    or s.startswith('Page') or re.match(r'^[\d,.\-\s]+$', s))

        prior_parts: list[str] = []
        for back in (2, 1):
            if idx - back < 0:
                continue
            prev = lines[idx - back].strip()
            prior_parts = [] if _is_noise(prev) else prior_parts + [prev]

        next_part = []
        if idx + 1 < len(lines):
            nxt = lines[idx + 1].strip()
            if not _is_noise(nxt):
                next_part = [nxt]

        name_parts = prior_parts + ([same_line_name] if same_line_name else []) + next_part
        name = re.sub(r'\s{2,}', ' ', ' '.join(name_parts)).strip() or 'Unknown Security'

        if isin.startswith('INF'):
            amc_name, scheme_name = _split_amc_scheme(name)
            mf_in_demat.append(FolioHolding(
                folio_number=f'DEMAT-{isin}',
                scheme_name=scheme_name,
                scheme_code=None,
                isin=isin,
                amc_name=amc_name,
                units_held=quantity,
                current_value=value,
                transactions=[],
            ))
        else:
            equities.append(EquityHolding(
                isin=isin,
                name=name,
                quantity=quantity,
                market_price=price,
                current_value=value,
            ))

    return equities, mf_in_demat


def _parse_portfolio_valuation_trend(text: str) -> list[dict]:
    """Parse the trailing-12-month 'Portfolio Valuation' table (whole-portfolio
    month-end value — demat + MF + NPS combined). Unlike most of this document
    this table is not bilingually garbled."""
    start = text.find('Portfolio Valuation')
    if start == -1:
        return []
    end = text.find('Asset Class', start)
    section = text[start:end] if end != -1 else text[start:start + 2000]

    rows = []
    for m in _TREND_ROW_RE.finditer(section):
        month_name, year, value_str = m.group(1), int(m.group(2)), m.group(3)
        rows.append({
            'month': date(year, _MONTH_ABBR[month_name], 1),
            'total_value': _parse_number(value_str),
        })
    return rows


def _parse_nps_section(text: str) -> list[NPSHoldingData]:
    start = text.find('NPS PRAN HELD WITH CRA')
    if start == -1:
        return []
    section = text[start:start + 6000]

    pran_m = _NPS_PRAN_RE.search(section)
    tier_m = _NPS_TIER_RE.search(text)
    pran = pran_m.group(1) if pran_m else None
    tier = f'Tier{tier_m.group(1)}' if tier_m else 'Tier1'

    fund_manager: str | None = None
    scheme_values: dict[str, float] = {}
    for m in _NPS_SCHEME_ROW_RE.finditer(section):
        letter = m.group(1)
        fm = ' '.join(m.group(2).split())
        units = _parse_number(m.group(3))
        nav = _parse_number(m.group(4))
        fund_manager = fund_manager or fm
        if units is not None and nav is not None:
            scheme_values[letter] = scheme_values.get(letter, 0.0) + units * nav

    total = sum(scheme_values.values())
    pv_m = _NPS_PORTFOLIO_VALUE_RE.search(section)
    current_value = _parse_number(pv_m.group(1)) if pv_m else (total or None)

    equity_pct = corporate_pct = govt_pct = None
    if total:
        equity_pct = round(scheme_values.get('E', 0.0) / total * 100, 2)
        corporate_pct = round(scheme_values.get('C', 0.0) / total * 100, 2)
        govt_pct = round(scheme_values.get('G', 0.0) / total * 100, 2)

    return [NPSHoldingData(
        pran_number=pran,
        tier=tier,
        fund_manager=fund_manager,
        current_value=current_value,
        equity_pct=equity_pct,
        corporate_bond_pct=corporate_pct,
        govt_bond_pct=govt_pct,
    )]


# ── Public API ────────────────────────────────────────────────────────────────

def parse_cas_pdf(pdf_bytes: bytes, password: str) -> CASResult:
    """Parse a CAMS or KFintech CAS PDF.

    Args:
        pdf_bytes: Raw bytes of the CAS PDF file.
        password:  PDF password — typically PAN (uppercase) + DOB (DDMMYYYY).

    Returns:
        CASResult with investor info and list of FolioHoldings.

    Raises:
        ValueError: If the password is wrong or the PDF cannot be parsed.
    """
    raw_text = _extract_text(pdf_bytes, password)
    if not raw_text or len(raw_text) < 100:
        raise ValueError("Could not extract text from PDF. Is it a valid CAS PDF?")

    cas_type = _detect_cas_type(raw_text)
    investor_name, pan = _extract_investor_info(raw_text, cas_type)
    statement_date = _extract_statement_date(raw_text)

    equity_holdings: list[EquityHolding] = []
    nps_accounts: list[NPSHoldingData] = []
    portfolio_snapshots: list[dict] = []

    if _is_cdsl_consolidated(raw_text):
        folios = _parse_mf_rta_section(raw_text)
        equity_holdings, mf_in_demat = _parse_demat_holdings(raw_text)
        folios.extend(mf_in_demat)
        nps_accounts = _parse_nps_section(raw_text)
        portfolio_snapshots = _parse_portfolio_valuation_trend(raw_text)
        if cas_type == 'unknown':
            cas_type = 'CDSL-Consolidated'
    else:
        amc_blocks = _split_amc_blocks(raw_text)
        folios = []
        for amc_name, block in amc_blocks:
            holding = _parse_folio_block(amc_name, block)
            if holding:
                folios.append(holding)

    return CASResult(
        investor_name=investor_name,
        pan=pan,
        cas_type=cas_type,
        folios=folios,
        equity_holdings=equity_holdings,
        nps_accounts=nps_accounts,
        portfolio_snapshots=portfolio_snapshots,
        statement_date=statement_date,
        raw_text=raw_text,
    )


def deduplicate_transactions(
    existing: list[dict[str, Any]],
    incoming: list[Transaction],
) -> list[Transaction]:
    """Return only transactions not already in the database.

    Duplicate key: (folio_number, transaction_date, transaction_type, units, amount).
    """
    existing_keys = {
        (
            r['folio_number'],
            str(r['transaction_date'])[:10],
            r['transaction_type'],
            r.get('units'),
            r.get('amount'),
        )
        for r in existing
    }

    new_txns = []
    for tx in incoming:
        key = (
            tx.folio_number,
            str(tx.transaction_date),
            tx.transaction_type,
            tx.units,
            tx.amount,
        )
        if key not in existing_keys:
            new_txns.append(tx)
    return new_txns
