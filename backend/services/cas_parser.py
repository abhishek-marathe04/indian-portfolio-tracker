"""CAS PDF parser — Phase 2 implementation.

Stub in Phase 1; will parse CAMS + KFintech Consolidated Account Statements.
"""
from __future__ import annotations

from typing import Any


def parse_cas_pdf(pdf_path: str, password: str) -> dict[str, Any]:
    """Parse a CAS PDF and return structured transaction data.

    Returns:
        {
            "investor_name": str,
            "pan": str,
            "folios": [...],
            "transactions": [...],
        }

    Raises NotImplementedError until Phase 2.
    """
    raise NotImplementedError("CAS parser will be implemented in Phase 2.")
