import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
# Import every model so its table is registered on Base.metadata before create_all.
from models import (  # noqa: F401
    user, profile, mutual_fund, stock, deposit, provident_fund,
    sukanya_samriddhi, nps, gold, real_estate, international_holding,
    crypto, post_office, goal, savings_account, price_cache, portfolio_snapshot,
)
from models.profile import Profile


@pytest.fixture()
def db_session():
    """A fresh in-memory SQLite DB per test — isolated from the real dev DB."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def profile_id(db_session) -> int:
    p = Profile(name="Test Profile", relationship="self")
    db_session.add(p)
    db_session.commit()
    return p.id
