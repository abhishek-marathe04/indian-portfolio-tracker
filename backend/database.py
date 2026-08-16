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
        portfolio_snapshot,
    )

    Base.metadata.create_all(bind=engine)
    _ensure_columns()
    return True


def _ensure_columns() -> None:
    """Lightweight migration for columns added after a table already existed."""
    additions = {
        "mutual_fund_holdings": [("isin", "VARCHAR(16)"), ("cas_statement_date", "DATE")],
        "stock_holdings": [("cas_statement_date", "DATE")],
        "nps_accounts": [("cas_statement_date", "DATE")],
    }
    with engine.connect() as conn:
        for table, columns in additions.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))}
            if not existing:
                continue   # table doesn't exist yet — create_all will have already added the column fresh
            for column_name, column_type in columns:
                if column_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}"))
        conn.commit()


def check_db_status() -> str:
    """Return 'connected' or an error string."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "connected"
    except Exception as exc:
        return f"error: {exc}"
