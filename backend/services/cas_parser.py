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
    ('sip',         re.compile(r'\bsip\b', re.IGNORECASE)),
    ('purchase',    re.compile(r'purchase|subscript|new|addition', re.IGNORECASE)),
]


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
class CASResult:
    investor_name: str
    pan: str | None
    cas_type: str                  # "CAMS" | "KFintech" | "unknown"
    folios: list[FolioHolding]
    raw_text: str


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
    for fmt in ('%d-%b-%Y', '%d/%m/%Y', '%d-%B-%Y'):
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

    amc_blocks = _split_amc_blocks(raw_text)
    folios: list[FolioHolding] = []
    for amc_name, block in amc_blocks:
        holding = _parse_folio_block(amc_name, block)
        if holding:
            folios.append(holding)

    return CASResult(
        investor_name=investor_name,
        pan=pan,
        cas_type=cas_type,
        folios=folios,
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
