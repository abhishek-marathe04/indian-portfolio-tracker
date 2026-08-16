from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func
from database import Base


class PortfolioSnapshot(Base):
    """Month-end total portfolio value, sourced from each CAS's own trailing
    12-month valuation trend table. Multiple CAS uploads spread across years
    build up a continuous multi-year history."""
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_month = Column(Date, nullable=False, index=True)   # first day of the month
    total_value = Column(Float, nullable=False)
    cas_source_file = Column(String(256), nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
