from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base


class StockHolding(Base):
    __tablename__ = "stock_holdings"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    exchange = Column(String(8), nullable=False, default="NSE")   # NSE | BSE
    ticker = Column(String(32), nullable=False, index=True)
    company_name = Column(String(256), nullable=True)
    isin = Column(String(16), nullable=True)
    quantity = Column(Float, nullable=False, default=0.0)
    avg_buy_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    # Zerodha | Groww | Angel | other
    broker = Column(String(64), nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    action = Column(String(8), nullable=False)   # buy | sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    brokerage = Column(Float, nullable=True, default=0.0)
    notes = Column(Text, nullable=True)
