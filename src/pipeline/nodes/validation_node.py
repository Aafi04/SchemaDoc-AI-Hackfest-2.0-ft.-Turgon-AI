import logging
from typing import Dict, Any, List, Set
from src.core.state import AgentState
from src.core.config import AppConfig

logger = logging.getLogger(__name__)

def validate_schema_node(state: AgentState) -> Dict[str, Any]:
    """
    DETERMINISTIC NODE:
    Compares the AI-enriched schema against the rigid 'schema_raw' source of truth.
    
    CRITICAL: This node is the 'Gatekeeper'. If the AI hallucinates or misses 
    columns, this node fails the state, triggering a retry or a fallback.
    """
    raw = state.get("schema_raw", {})
    enriched = state.get("schema_enriched", {})
    current_retries = state.get("retry_count", 0)
    
    errors: List[str] = []
    
    logger.info(f"Validating schema integrity (Attempt {current_retries + 1}/{AppConfig.MAX_RETRIES})...")

    # 1. Check Table Counts
    if len(raw) != len(enriched):
        errors.append(f"CRITICAL: Table count mismatch. Raw has {len(raw)}, AI returned {len(enriched)}.")

    # 2. Deep Column Verification
    for table_name, raw_table_data in raw.items():
        # A. Check Table Existence
        if table_name not in enriched:
            errors.append(f"Missing Table: '{table_name}' was dropped by AI.")
            continue
        
        # B. Check Column Sets
        # We compare the keys of the 'columns' dictionary
        raw_cols: Set[str] = set(raw_table_data["columns"].keys())
        enriched_cols: Set[str] = set(enriched[table_name]["columns"].keys())
        
        # Detect Data Loss (The "BLOB Trap" mentioned in Audit)
        missing = raw_cols - enriched_cols
        if missing:
            errors.append(f"Table '{table_name}' is missing columns: {list(missing)}")
        
        # Detect Hallucinations (AI inventing columns)
        extra = enriched_cols - raw_cols
        if extra:
            errors.append(f"Table '{table_name}' has hallucinated columns: {list(extra)}")

    # 3. Decision Logic
    if errors:
        logger.warning(f"Validation Failed with {len(errors)} errors.")
        return {
            "errors": errors,
            "validation_status": "FAILED",
            "retry_count": current_retries + 1 # Increment to track loop depth
        }
    else:
        logger.info("Validation Passed. Schema integrity verified.")
        return {
            "errors": [], # Clear errors on success
            "validation_status": "PASSED"
        }
