from typing import TypedDict, List, Dict, Any, Optional, Union

# data structures

class ColumnStats(TypedDict):
    # deterministic statistical profile of a column.
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    sample_values: List[Any]
    min_value: Optional[Union[int, float]]
    max_value: Optional[Union[int, float]]
    mean_value: Optional[float]

class ColumnMetadata(TypedDict):
    # The atomic unit of our data dictionary.
    name: str
    original_type: str
    
    # enriched fields filled by ai
    description: Optional[str]
    business_logic: Optional[str]
    potential_pii: bool
    tags: List[str]
    
    # quality metrics (filled by profiler)
    stats: Optional[ColumnStats]

class ForeignKey(TypedDict):
    column: str
    referred_table: str
    referred_column: str

class TableSchema(TypedDict):
    #Represents a single table's state.
    table_name: str
    row_count: int
    columns: Dict[str, ColumnMetadata]
    health_score: float # 0.0 to 1.0
    foreign_keys: List[ForeignKey]
    
    # context
    description: Optional[str]

# Pipeline State

class AgentState(TypedDict):
    #The shared memory of the LangGraph pipeline.
    
    # 1. Inputs
    connection_string: str
    
    # 2. Deterministic Layer (The Source of Truth)
    # Keys are table names
    schema_raw: Dict[str, TableSchema]
    
    # 3. Probabilistic Layer (The AI Enrichment)
    # Separated to prevent AI hallucinations from overwriting actual schema
    schema_enriched: Dict[str, TableSchema]
    
    # 4. Orchestration Control
    errors: List[str]
    retry_count: int
    validation_status: str # "PENDING", "PASSED", "FAILED"
    
    # 5. Final Output
    final_markdown: str
