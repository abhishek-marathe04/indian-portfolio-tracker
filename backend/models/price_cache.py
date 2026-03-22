from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from database import Base


class PriceCache(Base):
    """Cached live prices fetched from external APIs (AMFI, NSE, CoinGecko, etc.)."""
    __tablename__ = "price_cache"

    id = Column(Integer, primary_key=True, index=True)
    # amfi_nav | nse_stock | bse_stock | gold | usd_inr | us_stock | crypto
    asset_type = Column(String(16), nullable=False, index=True)
    # ticker / AMFI code / coin symbol / "GOLD" / "USDINR"
    symbol = Column(String(64), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("asset_type", "symbol", name="uq_price_cache_type_symbol"),
    )
