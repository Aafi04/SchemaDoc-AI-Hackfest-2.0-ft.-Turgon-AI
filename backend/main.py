"""
SchemaDoc AI — FastAPI Backend Entry Point.
Production-grade API server wrapping the LangGraph pipeline.
"""
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core.config import settings
from backend.api.routes import pipeline, chat, export, schema

# ── Logging ──
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("SchemaDoc_API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown events."""
    logger.info("🚀 SchemaDoc AI API starting up...")
    try:
        settings.validate_keys()
        logger.info("✅ Configuration validated.")
    except Exception as e:
        logger.warning(f"⚠️ Config warning: {e}")
    yield
    logger.info("SchemaDoc AI API shutting down.")


# ── App Instance ──
app = FastAPI(
    title="SchemaDoc AI",
    description="AI-Powered Data Dictionary Generator — API Backend",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──
app.include_router(pipeline.router)
app.include_router(schema.router)
app.include_router(chat.router)
app.include_router(export.router)


# ── Reset Session ──
@app.post("/api/reset")
async def reset_session():
    """Clear all in-memory pipeline runs, report caches, and schema cache."""
    from backend.services.pipeline_service import clear_all_runs
    from backend.api.routes.export import _report_cache

    clear_all_runs()
    _report_cache.clear()

    cache_file = settings.DATA_DIR / "schema_cache.json"
    if cache_file.exists():
        cache_file.unlink()

    logger.info("Session reset — all runs, caches, and artifacts cleared.")
    return {"status": "ok", "message": "Session reset successfully"}


# ── Health Check ──
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "SchemaDoc AI API",
        "version": "2.0.0",
    }


@app.get("/")
async def root():
    return {
        "message": "SchemaDoc AI API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
