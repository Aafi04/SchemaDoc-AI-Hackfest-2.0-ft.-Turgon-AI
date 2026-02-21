import sys
import json
import logging
from pathlib import Path
from decimal import Decimal # <--- Added Import

# Ensure src is in python path
sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.graph import build_pipeline
from src.core.config import AppConfig

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SchemaDoc_Runner")

# <--- Added Helper Class --->
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def main():
    # 1. validate Config
    try:
        AppConfig.validate()
        logger.info("Configuration loaded successfully.")
    except Exception as e:
        logger.error(f"Config Error: {e}")
        return

    # 2. Define Inputs
    # We use the demo DB we just created
    db_path = AppConfig.DATA_DIR / "demo.db"
    if not db_path.exists():
        logger.error(f"Database not found at {db_path}. Run 'python setup_demo.py' first.")
        return

    initial_state = {
        "connection_string": f"sqlite:///{db_path}",
        "retry_count": 0,
        "errors": [],
        "schema_raw": {},
        "schema_enriched": {}
    }

    # 3. Build & Run Graph
    logger.info("Starting SchemaDoc Pipeline...")
    app = build_pipeline()
    
    # invoke() runs the graph until it hits END
    final_state = app.invoke(initial_state)

    # 4. Output Results
    if final_state.get("validation_status") == "PASSED":
        print("\n" + "="*60)
        print("PIPELINE SUCCESS! ENRICHED DOCUMENTATION:")
        print("="*60 + "\n")
        
        enriched = final_state["schema_enriched"]
        # <--- UPDATED PRINT STATEMENT --->
        print(json.dumps(enriched, indent=2, cls=DecimalEncoder))
        
        # Save to artifact
        output_file = AppConfig.OUTPUT_DIR / "documentation.json"
        with open(output_file, "w") as f:
            # <--- UPDATED SAVE STATEMENT --->
            json.dump(enriched, f, indent=2, cls=DecimalEncoder)
        print(f"\nSaved artifact to {output_file}")
        
    else:
        print("\n" + "="*60)
        print("PIPELINE FAILED")
        print("="*60 + "\n")
        print("Errors:", final_state.get("errors"))

if __name__ == "__main__":
    main()