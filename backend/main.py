"""FastAPI application entry point for Indian Portfolio Tracker."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Load .env before anything else
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from database import init_db  # noqa: E402 (must come after dotenv load)
from routers import auth, cas, assets, analytics, export  # noqa: E402
from services.scheduler import start_scheduler, stop_scheduler  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

_FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Initialising database …")
    init_db()
    logger.info("Database ready at backend/data/portfolio.db")

    start_scheduler()

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    stop_scheduler()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Indian Portfolio Tracker",
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="Local-first personal portfolio tracker for Indian investors.",
    lifespan=lifespan,
    # Disable docs in production-like runs; keep enabled for development ease
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow same-WiFi phone browsers (any origin on the local network).
# In production/cloud deployment you would restrict this list.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(cas.router)
app.include_router(assets.router)
app.include_router(analytics.router)
app.include_router(export.router)

# ── Profiles router (Phase 1 — basic CRUD) ───────────────────────────────────
from fastapi import Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date as _date

from database import get_db
from routers.auth import get_current_user
from models.user import User
from models.profile import Profile
from services.encryption import encrypt, decrypt


class ProfileCreate(BaseModel):
    name: str
    relationship: str = "self"
    date_of_birth: Optional[_date] = None
    pan_number: Optional[str] = None


class ProfileOut(BaseModel):
    id: int
    name: str
    relationship: str
    date_of_birth: Optional[_date]
    pan_number: Optional[str]   # decrypted for display
    created_at: Optional[str]

    model_config = {"from_attributes": True}


from fastapi import APIRouter as _APIRouter

profiles_router = _APIRouter(prefix="/api/profiles", tags=["profiles"])


@profiles_router.get("")
def list_profiles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Profile).all()
    result = []
    for p in rows:
        pan = None
        if p.pan_number_encrypted:
            try:
                pan = decrypt(p.pan_number_encrypted)
            except Exception:
                pan = "***decryption error***"
        result.append({
            "id": p.id,
            "name": p.name,
            "relationship": p.relationship,
            "date_of_birth": p.date_of_birth,
            "pan_number": pan,
            "created_at": str(p.created_at) if p.created_at else None,
        })
    return result


@profiles_router.post("", status_code=201)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pan_enc = encrypt(data.pan_number.upper()) if data.pan_number else None
    profile = Profile(
        name=data.name,
        relationship=data.relationship,
        date_of_birth=data.date_of_birth,
        pan_number_encrypted=pan_enc,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id, "name": profile.name, "relationship": profile.relationship}


@profiles_router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()


app.include_router(profiles_router)

# ── Static frontend ───────────────────────────────────────────────────────────
# Serve the built React app if it exists; otherwise fall back to a minimal page.
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Serve the React SPA for any non-API path."""
        file_path = _FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_FRONTEND_DIST / "index.html"))
else:
    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(str(Path(__file__).parent.parent / "templates" / "placeholder.html"))
