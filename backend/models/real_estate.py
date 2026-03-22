from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class RealEstate(Base):
    """Real estate property — residential, commercial, plot, or agricultural."""
    __tablename__ = "real_estate"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    property_name = Column(String(256), nullable=False)
    # residential | commercial | plot | agricultural
    property_type = Column(String(16), nullable=False, default="residential")
    address = Column(Text, nullable=True)
    city = Column(String(64), nullable=True)
    state = Column(String(64), nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Float, nullable=True)
    registration_cost = Column(Float, nullable=True)
    stamp_duty = Column(Float, nullable=True)
    other_costs = Column(Float, nullable=True)
    current_estimated_value = Column(Float, nullable=True)    # manual update
    outstanding_loan_amount = Column(Float, nullable=True)
    rental_income_monthly = Column(Float, nullable=True)
    is_joint = Column(Boolean, nullable=False, default=False)
    joint_holder_name = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    last_valuation_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
