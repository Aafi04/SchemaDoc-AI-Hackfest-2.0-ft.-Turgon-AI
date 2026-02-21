from langgraph.graph import StateGraph, END
from src.core.state import AgentState
from src.core.config import AppConfig

# Import Nodes
from src.pipeline.nodes.validation_node import validate_schema_node
from src.pipeline.nodes.enrichment_node import enrich_metadata_node

# We need a wrapper for the raw extraction since it was a class method
from src.backend.connectors.sql_connector import SQLConnector

def extraction_node(state: AgentState):
    """Entry point: Connects to DB and gets raw schema."""
    conn_str = state["connection_string"]
    # Initialize connector
    connector = SQLConnector(conn_str)
    # Get Data
    raw_schema = connector.get_live_schema()
    return {"schema_raw": raw_schema}

def should_continue(state: AgentState):
    """Edge Logic: Decide whether to retry, finish, or error out."""
    status = state.get("validation_status", "PENDING")
    retry_count = state.get("retry_count", 0)
    
    if status == "PASSED":
        return "end"
    
    if retry_count >= AppConfig.MAX_RETRIES:
        return "max_retries"
    
    return "retry"

def build_pipeline():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("extract", extraction_node)
    workflow.add_node("enrich", enrich_metadata_node)
    workflow.add_node("validate", validate_schema_node)
    
    # Set Entry Point
    workflow.set_entry_point("extract")
    
    # Define Edges
    workflow.add_edge("extract", "enrich")
    workflow.add_edge("enrich", "validate")
    
    # Conditional Edge from Validator
    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "end": END,
            "retry": "enrich",  # Loop back to AI
            "max_retries": END  # Give up (could go to a fallback node)
        }
    )
    
    return workflow.compile()
