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

# Load .env before any module that reads env vars (database.py, auth.py, …)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from database import init_db  # noqa: E402
from routers import auth, cas, assets, analytics, export, profiles  # noqa: E402
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
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow same-WiFi phone browsers on the local network.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(cas.router)
app.include_router(assets.router)
app.include_router(analytics.router)
app.include_router(export.router)

# ── Static frontend (React SPA) ───────────────────────────────────────────────
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        file_path = _FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_FRONTEND_DIST / "index.html"))
else:
    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(str(Path(__file__).parent.parent / "templates" / "placeholder.html"))
