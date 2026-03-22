from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class SukanyaSamriddhi(Base):
    """Sukanya Samriddhi Yojana (SSY) account — for girl child."""
    __tablename__ = "sukanya_samriddhi"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    account_number = Column(String(64), nullable=True)
    post_office_bank = Column(String(128), nullable=True)
    date_of_birth_child = Column(Date, nullable=True)
    account_opening_date = Column(Date, nullable=False)
    # 21 years from opening, or after marriage post 18
    maturity_date = Column(Date, nullable=True)
    current_balance = Column(Float, nullable=False, default=0.0)
    interest_rate = Column(Float, nullable=True)
    # JSON array: [{"year": "2023-24", "amount": 50000}, ...]
    annual_contributions = Column(Text, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
