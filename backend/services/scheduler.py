"""APScheduler background jobs.

Jobs:
  - Daily MF NAV refresh at 10 PM IST (16:30 UTC)
  - Daily stock price refresh at 4 PM IST (10:30 UTC)
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _job_refresh_navs() -> None:
    """Refresh NAVs for all MF holdings with a scheme_code."""
    try:
        from database import SessionLocal
        from services.price_fetcher import refresh_mf_navs_for_portfolio
        db = SessionLocal()
        try:
            updated = await refresh_mf_navs_for_portfolio(db)
            logger.info("[scheduler] NAV refresh: updated %d holding(s)", updated)
        finally:
            db.close()
    except Exception as exc:
        logger.error("[scheduler] NAV refresh failed: %s", exc)


async def _job_refresh_stock_prices() -> None:
    """Refresh prices for all NSE stock holdings."""
    try:
        from database import SessionLocal
        from models.stock import StockHolding
        from services.price_fetcher import fetch_stock_prices_batch
        db = SessionLocal()
        try:
            symbols = [
                h.ticker
                for h in db.query(StockHolding)
                .filter(StockHolding.exchange == "NSE")
                .all()
            ]
            if symbols:
                prices = await fetch_stock_prices_batch(list(set(symbols)), db)
                # Update current_price on each holding
                for holding in db.query(StockHolding).filter(StockHolding.exchange == "NSE").all():
                    if holding.ticker in prices:
                        holding.current_price = prices[holding.ticker]
                db.commit()
                logger.info("[scheduler] Stock price refresh: updated %d symbol(s)", len(prices))
        finally:
            db.close()
    except Exception as exc:
        logger.error("[scheduler] Stock price refresh failed: %s", exc)


def start_scheduler() -> None:
    """Register all jobs and start the APScheduler."""
    # 10 PM IST = 16:30 UTC
    scheduler.add_job(
        _job_refresh_navs, "cron", hour=16, minute=30,
        id="nav_refresh", replace_existing=True,
    )
    # 4 PM IST = 10:30 UTC
    scheduler.add_job(
        _job_refresh_stock_prices, "cron", hour=10, minute=30,
        id="stock_refresh", replace_existing=True,
    )
    scheduler.start()
    logger.info("[scheduler] Started — NAV @ 10 PM IST, stocks @ 4 PM IST")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
