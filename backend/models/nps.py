from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class NPS(Base):
    """National Pension System account."""
    __tablename__ = "nps_accounts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    pran_number = Column(String(16), nullable=True)
    tier = Column(String(8), nullable=False, default="Tier1")   # Tier1 | Tier2
    # SBI | LIC | HDFC | ICICI | Kotak | UTI | Aditya Birla
    fund_manager = Column(String(32), nullable=True)
    # LC25 | LC50 | LC75 | AC | custom
    scheme_preference = Column(String(16), nullable=True)
    equity_pct = Column(Float, nullable=True)
    corporate_bond_pct = Column(Float, nullable=True)
    govt_bond_pct = Column(Float, nullable=True)
    current_nav = Column(Float, nullable=True)
    units_held = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    employer_contribution_annual = Column(Float, nullable=True)
    self_contribution_annual = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
