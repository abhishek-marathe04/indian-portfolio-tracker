from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class MutualFundHolding(Base):
    __tablename__ = "mutual_fund_holdings"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    folio_number = Column(String(64), nullable=False, index=True)
    scheme_name = Column(String(256), nullable=False)
    scheme_code = Column(String(32), nullable=True)   # AMFI code
    amc_name = Column(String(128), nullable=True)
    units_held = Column(Float, nullable=False, default=0.0)
    avg_nav = Column(Float, nullable=True)
    current_nav = Column(Float, nullable=True)
    invested_amount = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())


class MutualFundTransaction(Base):
    __tablename__ = "mutual_fund_transactions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    folio_number = Column(String(64), nullable=False, index=True)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    # purchase | redemption | switch_in | switch_out | dividend | sip
    transaction_type = Column(String(32), nullable=False)
    units = Column(Float, nullable=True)
    nav = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    cas_source_file = Column(String(256), nullable=True)
