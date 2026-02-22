"""
Pipeline orchestration service.
Manages pipeline runs, caches results, tracks execution.
"""
import uuid
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.pipeline.graph import build_pipeline
from backend.core.config import settings
from backend.core.utils import DecimalEncoder

logger = logging.getLogger(__name__)


# In-memory store for pipeline runs (replace with DB in production)
_pipeline_runs: Dict[str, Dict[str, Any]] = {}


def clear_all_runs():
    """Wipe every pipeline run from memory."""
    _pipeline_runs.clear()


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    return _pipeline_runs.get(run_id)


def list_runs() -> list:
    return [
        {
            "run_id": k,
            "status": v["status"],
            "created_at": v["created_at"],
            "schema_enriched": v.get("schema_enriched"),
            "pipeline_log": v.get("pipeline_log", []),
            "errors": v.get("errors", []),
        }
        for k, v in sorted(_pipeline_runs.items(), key=lambda x: x[1]["created_at"], reverse=True)
    ]


def execute_pipeline(connection_string: str) -> Dict[str, Any]:
    """
    Execute the LangGraph pipeline synchronously and return results.
    Tracks execution steps for the pipeline integrity log.
    """
    run_id = str(uuid.uuid4())[:8]

    run_record = {
        "run_id": run_id,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "connection_string": connection_string,
        "schema_enriched": None,
        "pipeline_log": [],
        "errors": [],
    }
    _pipeline_runs[run_id] = run_record

    try:
        initial_state = {
            "connection_string": connection_string,
            "retry_count": 0,
            "errors": [],
            "schema_raw": {},
            "schema_enriched": {},
        }

        app = build_pipeline()
        pipeline_log = []
        enrich_count = 0
        final_state = dict(initial_state)

        for event in app.stream(initial_state):
            for node_name, node_output in event.items():
                final_state.update(node_output)

                if node_name == "extract":
                    table_count = len(node_output.get("schema_raw", {}))
                    total_cols = sum(
                        len(t.get("columns", {}))
                        for t in node_output.get("schema_raw", {}).values()
                    )
                    pipeline_log.append({
                        "step": "extract",
                        "status": "success",
                        "message": f"Extracted {table_count} tables, {total_cols} columns with statistical profiling",
                        "icon": "🔬",
                        "errors": [],
                    })

                elif node_name == "enrich":
                    enrich_count += 1
                    pipeline_log.append({
                        "step": "enrich",
                        "status": "success",
                        "message": f"AI enrichment pass {enrich_count} — Gemini analysis with ReAct tool-calling",
                        "icon": "🧠",
                        "errors": [],
                    })

                elif node_name == "validate":
                    v_status = node_output.get("validation_status", "PENDING")
                    v_errors = node_output.get("errors", [])
                    if v_status == "PASSED":
                        pipeline_log.append({
                            "step": "validate",
                            "status": "passed",
                            "message": "Validation PASSED — zero hallucinations, zero data loss",
                            "icon": "✅",
                            "errors": [],
                        })
                    else:
                        pipeline_log.append({
                            "step": "validate",
                            "status": "failed",
                            "message": f"Validation FAILED — {len(v_errors)} integrity violation(s) caught",
                            "icon": "🔄",
                            "errors": v_errors,
                        })

        # Finalize
        if final_state.get("validation_status") == "PASSED":
            # JSON-serialize to clean Decimal types
            clean_enriched = json.loads(
                json.dumps(final_state["schema_enriched"], cls=DecimalEncoder)
            )
            run_record["status"] = "completed"
            run_record["schema_enriched"] = clean_enriched
            run_record["pipeline_log"] = pipeline_log
        else:
            run_record["status"] = "failed"
            run_record["errors"] = final_state.get("errors", [])
            run_record["pipeline_log"] = pipeline_log

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}")
        run_record["status"] = "failed"
        run_record["errors"] = [str(e)]

    _pipeline_runs[run_id] = run_record
    return run_record
