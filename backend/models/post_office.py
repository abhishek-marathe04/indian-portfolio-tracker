from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class PostOfficeScheme(Base):
    """NSC, KVP, MIS, SCSS, POMIS, TD and similar post-office instruments."""
    __tablename__ = "post_office_schemes"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    # NSC | KVP | MIS | SCSS | POMIS | TD
    scheme_type = Column(String(8), nullable=False)
    account_number = Column(String(64), nullable=True)
    post_office = Column(String(128), nullable=True)
    principal_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=True)
    maturity_amount = Column(Float, nullable=True)            # auto-calculated
    # monthly | quarterly | annual | on_maturity
    payout_frequency = Column(String(16), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
