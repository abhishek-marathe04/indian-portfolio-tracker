#!/usr/bin/env python3
"""
First-time setup for Indian Portfolio Tracker.

Usage:
    python setup.py

What it does:
1. Checks that a .env file exists (copies .env.example if missing).
2. Loads .env so database.py can find the data directory.
3. Creates the SQLite database and all tables.
4. Prompts for an admin username + password and creates the user row.
"""
from __future__ import annotations

import getpass
import os
import shutil
import sys
from pathlib import Path

# ── Working directory must be the project root ────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add backend/ to sys.path so we can import from it
sys.path.insert(0, str(BACKEND_DIR))


def ensure_env() -> None:
    env_file = PROJECT_ROOT / ".env"
    example_file = PROJECT_ROOT / ".env.example"

    if not env_file.exists():
        if example_file.exists():
            shutil.copy(example_file, env_file)
            print(f"  Created .env from .env.example")
            print(f"  ⚠️  Open .env and update JWT_SECRET and ENCRYPTION_KEY before first use!\n")
        else:
            print("  ⚠️  Neither .env nor .env.example found. Please create .env manually.")
            sys.exit(1)
    else:
        print("  .env already exists — skipping copy")


def load_env() -> None:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")


def check_secrets() -> None:
    """Warn if the user hasn't changed the placeholder secrets."""
    jwt_secret = os.getenv("JWT_SECRET", "")
    enc_key = os.getenv("ENCRYPTION_KEY", "")

    if not jwt_secret or "change-this" in jwt_secret:
        print("\n  ⚠️  WARNING: JWT_SECRET in .env is still the placeholder value.")
        print("     Generate a real secret: python -c \"import secrets; print(secrets.token_hex(32))\"")
        print("     Then update JWT_SECRET in your .env file.\n")

    if not enc_key or "change-this" in enc_key:
        print("\n  ⚠️  WARNING: ENCRYPTION_KEY in .env is still the placeholder value.")
        print("     Generate a real key: python -c \"import secrets; print(secrets.token_hex(32))\"")
        print("     Then update ENCRYPTION_KEY in your .env file.\n")


def init_database() -> None:
    from database import init_db, DB_PATH
    print(f"  Database path: {DB_PATH}")
    init_db()
    print("  All tables created (or verified existing).")


def create_admin_user() -> None:
    from database import SessionLocal
    from models.user import User
    from routers.auth import hash_password

    db = SessionLocal()
    try:
        existing_count = db.query(User).count()
        if existing_count > 0:
            print(f"\n  Found {existing_count} existing user(s). Skipping user creation.")
            print("  To reset, delete backend/data/portfolio.db and re-run setup.py")
            return

        print("\n  Create your admin account")
        print("  ─────────────────────────")

        while True:
            username = input("  Username: ").strip()
            if username:
                break
            print("  Username cannot be empty.")

        # Check for duplicate just in case
        if db.query(User).filter(User.username == username).first():
            print(f"  User '{username}' already exists. Exiting.")
            return

        while True:
            password = getpass.getpass("  Password: ")
            confirm = getpass.getpass("  Confirm password: ")
            if not password:
                print("  Password cannot be empty.")
            elif password != confirm:
                print("  Passwords do not match. Try again.")
            else:
                break

        user = User(username=username, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        print(f"\n  ✅ User '{username}' created successfully.")
    finally:
        db.close()


def ensure_dirs() -> None:
    """Create runtime directories that must exist before first run."""
    dirs = [
        PROJECT_ROOT / "uploads",
        PROJECT_ROOT / "exports",
        BACKEND_DIR / "data",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  Runtime directories verified (uploads/, exports/, backend/data/)")


def main() -> None:
    print("\n" + "━" * 54)
    print("  🇮🇳  Indian Portfolio Tracker — First-Time Setup")
    print("━" * 54 + "\n")

    print("Step 1/4 — Environment file")
    ensure_env()
    load_env()
    check_secrets()

    print("Step 2/4 — Directories")
    ensure_dirs()

    print("\nStep 3/4 — Database")
    init_database()

    print("\nStep 4/4 — Admin user")
    create_admin_user()

    print("\n" + "━" * 54)
    print("  Setup complete!")
    print("  Start the app with:  ./run.sh   (Mac/Linux)")
    print("                       run.bat    (Windows)")
    print("━" * 54 + "\n")


if __name__ == "__main__":
    main()
