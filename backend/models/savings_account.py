from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class SavingsAccount(Base):
    """Bank savings / current / salary account for net-worth context."""
    __tablename__ = "savings_accounts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_name = Column(String(128), nullable=False)
    # savings | current | salary
    account_type = Column(String(16), nullable=False, default="savings")
    account_number_last4 = Column(String(4), nullable=True)
    current_balance = Column(Float, nullable=False, default=0.0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
