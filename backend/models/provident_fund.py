from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class ProvidentFund(Base):
    """PPF, EPF, GPF, or VPF account."""
    __tablename__ = "provident_funds"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(8), nullable=False, default="PPF")   # PPF | EPF | GPF | VPF
    account_number = Column(String(64), nullable=True)
    bank_or_employer = Column(String(128), nullable=True)
    opening_balance = Column(Float, nullable=False, default=0.0)
    current_balance = Column(Float, nullable=False, default=0.0)
    interest_rate = Column(Float, nullable=True)              # current FY rate
    maturity_date = Column(Date, nullable=True)
    # JSON array: [{"year": "2023-24", "amount": 150000}, ...]
    annual_contributions = Column(Text, nullable=True)
    employer_contribution = Column(Float, nullable=True)      # EPF only, per year
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
