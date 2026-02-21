"""
Pipeline API Routes.
POST /api/pipeline/run — Start a new pipeline run
GET  /api/pipeline/runs — List all runs
GET  /api/pipeline/run/{run_id} — Get run results
"""
import logging
from fastapi import APIRouter, HTTPException
from shared.schemas import PipelineRunRequest, PipelineRunResponse
from backend.services.pipeline_service import execute_pipeline, get_run, list_runs
from backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pipeline", tags=["Pipeline"])


@router.post("/run")
async def run_pipeline(request: PipelineRunRequest):
    """Start a new pipeline analysis run."""
    try:
        settings.validate_keys()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = execute_pipeline(request.connection_string)
    return result


@router.get("/runs")
async def get_all_runs():
    """List all pipeline runs."""
    return list_runs()


@router.get("/run/{run_id}")
async def get_pipeline_run(run_id: str):
    """Get results of a specific pipeline run."""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run


@router.get("/databases")
async def list_available_databases():
    """List available databases — cloud PostgreSQL + local SQLite."""
    databases = []
    neon_url = settings.NEON_DATABASE_URL

    # ── Cloud PostgreSQL (Neon) — always available when configured ──
    if neon_url:
        base = neon_url.split("?")[0]
        params = "sslmode=require"

        for db_id, name, schema, tables in [
            ("olist", "Olist E-Commerce Brazil (8 Tables) [PostgreSQL]", "olist", 8),
            ("bikestore", "Bike Store Sales (9 Tables) [PostgreSQL]", "bikestore", 9),
            ("chinook", "Chinook Music Store (11 Tables) [PostgreSQL]", "chinook", 11),
        ]:
            databases.append({
                "id": db_id,
                "name": name,
                "connection_string": f"{base}?{params}&pg_schema={schema}",
                "tables": tables,
            })

    # ── Local SQLite fallback (for development) ──
    data_dir = settings.DATA_DIR

    for db_id, name, filename, table_count in [
        ("chinook_local", "Chinook Music Store (11 Tables) [SQLite]", "chinook.db", 11),
        ("olist_local", "Olist E-Commerce Brazil (8 Tables) [SQLite]", "olist.db", 8),
        ("bikestore_local", "Bike Store Sales (9 Tables) [SQLite]", "bikestore.db", 9),
        ("demo", "Demo Database (3 Tables) [SQLite]", "demo.db", 3),
    ]:
        path = data_dir / filename
        if path.exists():
            databases.append({
                "id": db_id,
                "name": name,
                "connection_string": f"sqlite:///{path}",
                "tables": table_count,
            })

    return {"databases": databases}
