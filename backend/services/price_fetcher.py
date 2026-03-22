"""Live price fetching from free public APIs.

Phase 1 stub — full implementation in Phase 2.
Sources: AMFI (mfapi.in), NSE/BSE, CoinGecko, yfinance.
"""
from __future__ import annotations

import httpx

AMFI_NAV_URL = "https://api.mfapi.in/mf/{scheme_code}"


async def fetch_nav(scheme_code: str) -> float | None:
    """Fetch latest NAV for an AMFI scheme code."""
    url = AMFI_NAV_URL.format(scheme_code=scheme_code)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return float(data["data"][0]["nav"])
        except Exception:
            return None


async def fetch_crypto_price_inr(coin_id: str) -> float | None:
    """Fetch INR price of a cryptocurrency from CoinGecko (no API key required)."""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=inr"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            return float(data[coin_id]["inr"])
        except Exception:
            return None
