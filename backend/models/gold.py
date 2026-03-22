from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class GoldHolding(Base):
    """Gold in any form — physical, SGB, digital, ETF, or fund."""
    __tablename__ = "gold_holdings"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    # physical | SGB | digital_gold | gold_etf | gold_fund
    type = Column(String(16), nullable=False, default="physical")
    quantity_grams = Column(Float, nullable=True)             # physical / digital
    units = Column(Float, nullable=True)                      # ETF / fund
    buy_price_per_gram_or_unit = Column(Float, nullable=True)
    current_price_per_gram_or_unit = Column(Float, nullable=True)
    purchase_date = Column(Date, nullable=True)
    sgb_series = Column(String(64), nullable=True)
    sgb_maturity_date = Column(Date, nullable=True)
    sgb_interest_rate = Column(Float, nullable=True, default=2.5)
    custodian = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
