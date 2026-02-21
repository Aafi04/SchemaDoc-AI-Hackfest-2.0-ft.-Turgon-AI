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
    """List available demo databases."""
    data_dir = settings.DATA_DIR
    databases = []

    chinook_path = data_dir / "chinook.db"
    if chinook_path.exists():
        databases.append({
            "id": "chinook",
            "name": "Chinook Database (11 Tables)",
            "connection_string": f"sqlite:///{chinook_path}",
            "tables": 11,
        })

    demo_path = data_dir / "demo.db"
    if demo_path.exists():
        databases.append({
            "id": "demo",
            "name": "Demo Database (3 Tables)",
            "connection_string": f"sqlite:///{demo_path}",
            "tables": 3,
        })

    return {"databases": databases}
