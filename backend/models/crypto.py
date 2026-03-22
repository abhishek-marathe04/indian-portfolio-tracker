from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class CryptoHolding(Base):
    """Cryptocurrency holding on any exchange."""
    __tablename__ = "crypto_holdings"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    coin_symbol = Column(String(16), nullable=False, index=True)   # BTC | ETH | ...
    coin_name = Column(String(64), nullable=True)
    # WazirX | CoinDCX | Binance | other
    exchange = Column(String(32), nullable=True)
    quantity = Column(Float, nullable=False, default=0.0)
    avg_buy_price_inr = Column(Float, nullable=True)
    current_price_inr = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
