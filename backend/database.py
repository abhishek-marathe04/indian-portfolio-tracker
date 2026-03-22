import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure the data directory exists next to this file
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "portfolio.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Import every model module so SQLAlchemy sees them."""
    # noqa: F401 — imported for side-effects (table registration)
    from models import (  # noqa: F401
        user,
        profile,
        mutual_fund,
        stock,
        deposit,
        provident_fund,
        sukanya_samriddhi,
        nps,
        gold,
        real_estate,
        international_holding,
        crypto,
        post_office,
        goal,
        savings_account,
        price_cache,
    )

    Base.metadata.create_all(bind=engine)
    return True


def check_db_status() -> str:
    """Return 'connected' or an error string."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "connected"
    except Exception as exc:
        return f"error: {exc}"
