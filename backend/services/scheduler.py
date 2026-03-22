"""APScheduler background jobs — daily price refresh and optional nightly snapshot.

Scheduler is started by main.py on app startup.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _refresh_nav_prices() -> None:
    """Fetch latest MF NAVs from AMFI and update price_cache."""
    logger.info("[scheduler] NAV refresh job triggered (Phase 2 implementation pending)")


async def _refresh_stock_prices() -> None:
    """Fetch latest NSE/BSE stock prices."""
    logger.info("[scheduler] Stock price refresh job triggered (Phase 2 implementation pending)")


def start_scheduler() -> None:
    """Register jobs and start the background scheduler."""
    # Daily NAV refresh at 10 PM IST (16:30 UTC)
    scheduler.add_job(_refresh_nav_prices, "cron", hour=16, minute=30, id="nav_refresh", replace_existing=True)
    # Daily stock price refresh at 4 PM IST (10:30 UTC)
    scheduler.add_job(_refresh_stock_prices, "cron", hour=10, minute=30, id="stock_refresh", replace_existing=True)

    scheduler.start()
    logger.info("[scheduler] APScheduler started — NAV @ 10 PM IST, stocks @ 4 PM IST")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
