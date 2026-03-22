"""CSV and Excel export service — Phase 4 implementation.

Stub in Phase 1.
"""
from __future__ import annotations


def export_to_csv(asset_type: str, profile_id: int | None = None) -> bytes:
    """Return CSV bytes for the given asset type. Phase 4."""
    raise NotImplementedError("Export will be implemented in Phase 4.")


def export_full_portfolio_excel(profile_id: int | None = None) -> bytes:
    """Return multi-sheet Excel workbook bytes. Phase 4."""
    raise NotImplementedError("Excel export will be implemented in Phase 4.")
