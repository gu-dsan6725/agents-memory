"""
FastAPI Agent Application with Multi-Tenant Memory Support.

This application provides REST endpoints for conversing with the memory agent.
Each user has isolated memory, and sessions are tracked via run_id.

Usage:
    uv run uvicorn agent_api:app --reload --host 127.0.0.1 --port 9090

Endpoints:
    GET  /ping         - Health check
    POST /invocation   - Conversation with agent
"""

import logging
import os
from typing import (
    Any,
    Dict,
    Optional,
)

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from agent import Agent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Memory Agent API",
    description="Multi-tenant conversational agent with semantic memory",
    version="1.0.0"
)

# Session cache: run_id -> Agent instance
# Each session (run_id) gets its own Agent to maintain conversation context
_session_cache: Dict[str, Agent] = {}


def _get_or_create_agent(
    user_id: str,
    run_id: str
) -> Agent:
    """
    Get existing Agent for session or create new one.

    ONE Agent per session (run_id). This allows the Strands Agent to maintain
    conversation context across multiple turns within the same session.

    Args:
        user_id: User identifier for memory isolation
        run_id: Session identifier

    Returns:
        Agent instance for this session
    """
    # Check if we already have an agent for this session
    if run_id in _session_cache:
        logger.info(f"Reusing existing agent for session: {run_id}")
        return _session_cache[run_id]

    # Create new agent for this session
    logger.info(f"Creating new agent for session: {run_id}")

    api_key = (
        os.getenv("ANTHROPIC_API_KEY") or
        os.getenv("GROQ_API_KEY") or
        os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "No API key configured. Set ANTHROPIC_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY"
        )

    # Create agent with user_id and run_id
    agent = Agent(
        user_id=user_id,
        run_id=run_id,
        api_key=api_key
    )

    # Cache it for this session
    _session_cache[run_id] = agent

    logger.info(f"Cached agent for session: {run_id} (cache size: {len(_session_cache)})")

    return agent


# Pydantic Models
class PingResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")


class InvocationRequest(BaseModel):
    """Request model for agent invocation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "alice",
                "run_id": "session-1",
                "query": "Hi, I'm Alice. I'm a software engineer.",
                "metadata": {"source": "web"}
            }
        }
    )

    user_id: str = Field(..., description="User identifier for memory isolation")
    run_id: Optional[str] = Field(None, description="Session ID (auto-generated if not provided)")
    query: str = Field(..., description="User's message to the agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata/tags")


class InvocationResponse(BaseModel):
    """Response model for agent invocation."""
    user_id: str = Field(..., description="User identifier")
    run_id: str = Field(..., description="Session identifier")
    query: str = Field(..., description="User's query")
    response: str = Field(..., description="Agent's response")


@app.get("/ping", response_model=PingResponse)
async def ping():
    """
    Health check endpoint.

    Returns:
        PingResponse with service status
    """
    logger.info("Ping endpoint called")
    return PingResponse(
        status="ok",
        message="Memory Agent API is running"
    )


@app.post("/invocation", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    """
    Invoke the memory agent with a user query.

    Creates an ephemeral agent instance for the request, processes the query,
    and returns the agent's response. Memory is persisted across requests for
    the same user_id.

    Args:
        request: InvocationRequest with user_id, run_id, query, metadata

    Returns:
        InvocationResponse with agent's reply

    Raises:
        HTTPException: If agent invocation fails
    """
    try:
        # Auto-generate run_id if not provided
        import uuid
        run_id = request.run_id or str(uuid.uuid4())[:8]

        logger.info(
            f"Invocation request - user: {request.user_id}, "
            f"run_id: {run_id}, "
            f"query length: {len(request.query)}"
        )

        # Get or create agent for this session
        # If run_id exists in cache, reuse the same Agent instance
        # This allows Strands to maintain conversation context within the session
        agent = _get_or_create_agent(
            user_id=request.user_id,
            run_id=run_id
        )

        # Get agent response (simple chat call, agent already has user_id/run_id)
        response_text = agent.chat(request.query)

        logger.info(
            f"Agent response generated - user: {request.user_id}, "
            f"session: {run_id}, "
            f"response length: {len(response_text)}"
        )

        return InvocationResponse(
            user_id=request.user_id,
            run_id=run_id,
            query=request.query,
            response=response_text
        )

    except ValueError as e:
        logger.error(f"Validation error in invocation: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error in invocation: {e}")
        raise HTTPException(status_code=500, detail=f"Agent invocation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9090)
