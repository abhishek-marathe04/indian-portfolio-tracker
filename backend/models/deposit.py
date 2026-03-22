from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Deposit(Base):
    """Fixed Deposit or Recurring Deposit."""
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(4), nullable=False, default="FD")   # FD | RD
    bank_name = Column(String(128), nullable=False)
    branch = Column(String(128), nullable=True)
    principal_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)            # annual % rate
    # monthly | quarterly | annual
    compounding = Column(String(16), nullable=False, default="quarterly")
    start_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=True)
    maturity_amount = Column(Float, nullable=True)           # auto-calculated
    is_joint = Column(Boolean, nullable=False, default=False)
    joint_holder_name = Column(String(128), nullable=True)
    nomination = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
