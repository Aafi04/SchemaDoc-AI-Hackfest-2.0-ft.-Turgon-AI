"""
Chat API Routes — NL → SQL with streaming support.
POST /api/chat — Send a message, get AI response
"""
import json
import logging
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from shared.schemas import ChatRequest, ChatResponse
from backend.services.pipeline_service import get_run
from backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a natural language question, get schema-grounded AI response."""
    run = get_run(request.run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{request.run_id}' not found")

    schema_data = run.get("schema_enriched")
    if not schema_data:
        raise HTTPException(status_code=400, detail="Pipeline run has no enriched schema data")

    try:
        context_json = json.dumps(schema_data, cls=DecimalEncoder)
        system_prompt = f"""You are a Senior Database Architect and SQL Expert.

SCHEMA CONTEXT (AI-enriched data dictionary):
{context_json}

DIRECTIVES:
1. If the user asks a natural language question about the data, generate the EXACT SQL query needed.
2. Output SQL in a ```sql code block.
3. Briefly explain the query logic referencing the schema descriptions and relationships.
4. All JOINs must use the exact foreign key relationships from the schema context.
5. If asked about schema metadata (PII columns, health scores, etc.), answer from context directly.
6. Be concise and precise."""

        messages = [SystemMessage(content=system_prompt)]
        for msg in request.history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=request.message))

        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
        )
        response = llm.invoke(messages)
        response_text = response.content.strip()

        # Extract SQL if present
        import re
        sql_match = re.search(r"```sql\s*(.*?)\s*```", response_text, re.DOTALL)
        sql_query = sql_match.group(1).strip() if sql_match else None

        return ChatResponse(response=response_text, sql_query=sql_query)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
