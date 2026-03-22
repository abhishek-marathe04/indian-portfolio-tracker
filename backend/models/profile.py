from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Profile(Base):
    """A family member profile. PAN is stored AES-256 encrypted."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    # self | spouse | child | parent | other
    relationship = Column(String(32), nullable=False, default="self")
    date_of_birth = Column(Date, nullable=True)
    # AES-256-GCM encrypted; None if not provided
    pan_number_encrypted = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
