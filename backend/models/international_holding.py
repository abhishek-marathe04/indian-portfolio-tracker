from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class InternationalHolding(Base):
    """US / international stock holdings."""
    __tablename__ = "international_holdings"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    # Vested | INDmoney | Groww | other
    platform = Column(String(32), nullable=True)
    ticker = Column(String(16), nullable=False, index=True)
    # NYSE | NASDAQ | LSE | other
    exchange = Column(String(16), nullable=True)
    company_name = Column(String(256), nullable=True)
    quantity = Column(Float, nullable=False, default=0.0)
    avg_buy_price_usd = Column(Float, nullable=True)
    current_price_usd = Column(Float, nullable=True)
    current_price_inr = Column(Float, nullable=True)
    buy_date = Column(Date, nullable=True)
    # Liberalised Remittance Scheme: amount remitted (USD)
    lrs_amount_used = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
