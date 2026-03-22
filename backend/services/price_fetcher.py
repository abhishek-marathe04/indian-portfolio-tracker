"""Live price fetching from free public APIs.

Sources:
  - AMFI / mfapi.in        — Mutual Fund NAVs (no API key)
  - NSE India              — NSE stock prices (unofficial JSON)
  - CoinGecko              — Crypto prices in INR (no API key)
  - ExchangeRate-API       — USD/INR conversion (no API key)
  - yfinance               — US stocks (no API key)

All fetched prices are cached in the price_cache table.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy.orm import Session

from models.price_cache import PriceCache

logger = logging.getLogger(__name__)

# ── API URLs ──────────────────────────────────────────────────────────────────

_AMFI_ALL_NAVS = "https://api.mfapi.in/mf"
_AMFI_SCHEME_URL = "https://api.mfapi.in/mf/{scheme_code}"
_NSE_QUOTE_URL = "https://www.nseindia.com/api/quote-equity?symbol={symbol}"
_COINGECKO_PRICE_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids={ids}&vs_currencies=inr"
)
_EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/USD"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _upsert_cache(db: Session, asset_type: str, symbol: str, price: float, currency: str = "INR") -> None:
    """Insert or update a PriceCache row."""
    row = (
        db.query(PriceCache)
        .filter(PriceCache.asset_type == asset_type, PriceCache.symbol == symbol)
        .first()
    )
    if row:
        row.price = price
        row.currency = currency
        row.fetched_at = datetime.now(timezone.utc)
    else:
        db.add(PriceCache(
            asset_type=asset_type,
            symbol=symbol,
            price=price,
            currency=currency,
        ))


def get_cached_price(db: Session, asset_type: str, symbol: str) -> float | None:
    row = (
        db.query(PriceCache)
        .filter(PriceCache.asset_type == asset_type, PriceCache.symbol == symbol)
        .first()
    )
    return row.price if row else None


# ── AMFI / Mutual Fund NAV ────────────────────────────────────────────────────

async def fetch_nav(scheme_code: str, db: Session | None = None) -> float | None:
    """Fetch latest NAV for a given AMFI scheme code."""
    url = _AMFI_SCHEME_URL.format(scheme_code=scheme_code)
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            nav = float(data["data"][0]["nav"])
            if db is not None:
                _upsert_cache(db, "amfi_nav", str(scheme_code), nav)
                db.commit()
            return nav
        except Exception as exc:
            logger.warning("NAV fetch failed for scheme %s: %s", scheme_code, exc)
            return None


async def fetch_all_navs(db: Session) -> dict[str, float]:
    """Fetch all AMFI NAVs and cache them.

    Returns dict of {scheme_code: nav}.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(_AMFI_ALL_NAVS)
            resp.raise_for_status()
            schemes = resp.json()
            nav_map: dict[str, float] = {}
            for scheme in schemes:
                code = str(scheme.get("schemeCode", ""))
                nav_str = scheme.get("nav") or scheme.get("navAmount")
                if code and nav_str:
                    try:
                        nav = float(str(nav_str).replace(',', ''))
                        nav_map[code] = nav
                        _upsert_cache(db, "amfi_nav", code, nav)
                    except (ValueError, TypeError):
                        pass
            db.commit()
            logger.info("Cached %d AMFI NAVs", len(nav_map))
            return nav_map
        except Exception as exc:
            logger.error("Failed to fetch all AMFI NAVs: %s", exc)
            return {}


# ── NSE / BSE Stocks ──────────────────────────────────────────────────────────

_NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; portfolio-tracker/1.0)",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com",
}


async def fetch_nse_price(symbol: str, db: Session | None = None) -> float | None:
    """Fetch current price for an NSE-listed stock."""
    url = _NSE_QUOTE_URL.format(symbol=symbol.upper())
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        try:
            # NSE requires a cookie — visit the main page first
            await client.get("https://www.nseindia.com", headers=_NSE_HEADERS)
            resp = await client.get(url, headers=_NSE_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            price = float(data["priceInfo"]["lastPrice"])
            if db is not None:
                _upsert_cache(db, "nse_stock", symbol.upper(), price)
                db.commit()
            return price
        except Exception as exc:
            logger.warning("NSE price fetch failed for %s: %s", symbol, exc)
            return None


async def fetch_stock_prices_batch(
    symbols: list[str], db: Session
) -> dict[str, float]:
    """Fetch prices for multiple NSE symbols concurrently."""
    tasks = [fetch_nse_price(sym, db=None) for sym in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    price_map: dict[str, float] = {}
    for sym, result in zip(symbols, results):
        if isinstance(result, float):
            price_map[sym] = result
            _upsert_cache(db, "nse_stock", sym.upper(), result)
    db.commit()
    return price_map


# ── Cryptocurrency (CoinGecko) ────────────────────────────────────────────────

async def fetch_crypto_prices_inr(
    coin_ids: list[str], db: Session | None = None
) -> dict[str, float]:
    """Fetch INR prices for multiple CoinGecko coin IDs.

    coin_ids are CoinGecko IDs e.g. 'bitcoin', 'ethereum', 'matic-network'.
    """
    url = _COINGECKO_PRICE_URL.format(ids=','.join(coin_ids))
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            result: dict[str, float] = {}
            for coin_id in coin_ids:
                price = data.get(coin_id, {}).get('inr')
                if price is not None:
                    result[coin_id] = float(price)
                    if db is not None:
                        _upsert_cache(db, "crypto", coin_id.lower(), float(price))
            if db is not None:
                db.commit()
            return result
        except Exception as exc:
            logger.warning("CoinGecko fetch failed: %s", exc)
            return {}


# ── USD / INR exchange rate ───────────────────────────────────────────────────

async def fetch_usd_inr(db: Session | None = None) -> float | None:
    """Fetch current USD/INR rate from ExchangeRate-API (free, no key)."""
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(_EXCHANGE_RATE_URL)
            resp.raise_for_status()
            data = resp.json()
            rate = float(data["rates"]["INR"])
            if db is not None:
                _upsert_cache(db, "fx", "USDINR", rate)
                db.commit()
            return rate
        except Exception as exc:
            logger.warning("USD/INR fetch failed: %s", exc)
            return None


# ── US Stocks (yfinance) ──────────────────────────────────────────────────────

def fetch_us_stock_price(ticker: str, db: Session | None = None) -> float | None:
    """Fetch latest US stock price in USD via yfinance (synchronous)."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = float(info.last_price)
        if db is not None:
            _upsert_cache(db, "us_stock", ticker.upper(), price, currency="USD")
            db.commit()
        return price
    except Exception as exc:
        logger.warning("yfinance fetch failed for %s: %s", ticker, exc)
        return None


# ── Manual price refresh endpoint helper ─────────────────────────────────────

async def refresh_mf_navs_for_portfolio(db: Session) -> int:
    """Fetch NAVs for all MF holdings in the DB that have a scheme_code.

    Returns the number of NAVs updated.
    """
    from models.mutual_fund import MutualFundHolding
    from sqlalchemy import update

    holdings = (
        db.query(MutualFundHolding)
        .filter(MutualFundHolding.scheme_code.isnot(None))
        .all()
    )
    updated = 0
    for holding in holdings:
        nav = await fetch_nav(holding.scheme_code)
        if nav is not None:
            holding.current_nav = nav
            holding.current_value = round(holding.units_held * nav, 2)
            _upsert_cache(db, "amfi_nav", holding.scheme_code, nav)
            updated += 1
    db.commit()
    return updated
