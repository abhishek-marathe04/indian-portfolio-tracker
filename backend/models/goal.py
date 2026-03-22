from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Goal(Base):
    """Financial goal with optional link to specific holdings."""
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    # NULL means family-level goal
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    # Retirement | Child Education | Home | Wedding | Travel | Emergency Fund | custom
    name = Column(String(128), nullable=False)
    target_amount = Column(Float, nullable=False)
    target_date = Column(Date, nullable=True)
    current_value = Column(Float, nullable=True, default=0.0)
    # JSON: {"mutual_fund": [1,2], "stock": [3], ...}
    linked_asset_ids = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
