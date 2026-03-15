"""
Stateless memory-enabled agent for multi-tenant API use.

This version of the agent does NOT bind user_id/run_id at initialization.
Instead, user context is passed per request in the chat() method.

This allows ONE agent instance to serve ALL users and sessions.
"""

import asyncio
import json
import logging
import os
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from dotenv import load_dotenv
from duckduckgo_search import DDGS
from strands import (
    Agent as StrandsAgent,
    tool,
)
from strands.models import LiteLLMModel

from memory_manager import MemoryManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
DEFAULT_MODEL: str = "claude-haiku-4-5-20251001"


def _run_async(coro):
    """Run async coroutine in sync context."""
    try:
        loop = asyncio.get_running_loop()
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(coro)
    except RuntimeError:
        return asyncio.run(coro)
    except ImportError:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()


def _create_search_memory_tool(
    memory_manager: MemoryManager,
    user_id: str,
    agent_id: str,
    run_id: str
):
    """Create search_memory tool with user context."""
    @tool
    async def search_memory(query: str, limit: int = 5) -> str:
        """Search for relevant information from previous conversations."""
        try:
            limit = int(limit) if limit is not None else 5
            logger.info(f"Searching memories for user={user_id}: '{query}' (limit={limit})")

            results = await memory_manager.search(
                user_id=user_id,
                query=query,
                limit=limit,
                agent_id=agent_id,
                run_id=run_id
            )

            if not results:
                return json.dumps({
                    "status": "success",
                    "count": 0,
                    "memories": [],
                    "message": "No relevant memories found"
                }, indent=2)

            response = {
                "status": "success",
                "count": len(results),
                "memories": results
            }

            logger.info(f"Found {len(results)} memories for user={user_id}")
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    return search_memory


def _create_insert_memory_tool(
    memory_manager: MemoryManager,
    user_id: str,
    agent_id: str,
    run_id: str
):
    """Create insert_memory tool with user context."""
    @tool
    async def insert_memory(
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Explicitly store important information in long-term memory."""
        try:
            logger.info(f"Inserting memory for user={user_id}: '{content[:100]}...'")

            result = await memory_manager.insert(
                user_id=user_id,
                content=content,
                agent_id=agent_id,
                run_id=run_id,
                metadata=metadata
            )

            response = {
                "status": result.get("status", "success"),
                "message": result.get("message", "Memory stored successfully"),
                "content": content,
                "metadata": metadata
            }

            logger.info(f"Memory inserted for user={user_id}")
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error inserting memory: {e}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    return insert_memory


def _create_web_search_tool():
    """Create web_search tool."""
    @tool
    def web_search(query: str, max_results: int = 3) -> str:
        """Search the web for current information."""
        try:
            max_results = int(max_results) if max_results is not None else 3
            max_results = max(1, min(max_results, 10))

            logger.info(f"Web search: '{query}' (max_results={max_results})")

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return json.dumps({
                    "status": "success",
                    "count": 0,
                    "results": [],
                    "message": "No search results found"
                }, indent=2)

            search_results = [{
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            } for r in results]

            response = {
                "status": "success",
                "count": len(search_results),
                "results": search_results
            }

            logger.info(f"Found {len(search_results)} web results")
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return json.dumps({"status": "error", "message": str(e)}, indent=2)

    return web_search


def _build_system_prompt() -> str:
    """Load system prompt from file."""
    prompt_file = os.path.join(
        os.path.dirname(__file__),
        "prompts",
        "system_prompt.txt"
    )

    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"System prompt file not found: {prompt_file}")
        raise


class StatelessAgent:
    """
    Stateless multi-tenant agent.

    ONE instance serves ALL users and sessions. User context (user_id, run_id)
    is passed per request to the chat() method, not stored in the instance.

    This enables true multi-tenant API deployment where a single agent handles
    all requests with proper memory isolation.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None
    ):
        """
        Initialize stateless agent.

        Args:
            model: LLM model to use
            api_key: API key for LLM provider

        Note:
            Does NOT take user_id or run_id - these are passed per request.
        """
        # Get API key
        if api_key:
            resolved_api_key = api_key
        else:
            resolved_api_key = (
                os.getenv("ANTHROPIC_API_KEY") or
                os.getenv("GROQ_API_KEY") or
                os.getenv("OPENAI_API_KEY") or
                os.getenv("GEMINI_API_KEY")
            )

        if not resolved_api_key:
            raise ValueError("API key required")

        # Set environment variables for LiteLLM
        for key in ["ANTHROPIC_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"]:
            if os.getenv(key):
                os.environ[key] = os.getenv(key)

        self.model = model

        # Initialize multi-tenant MemoryManager (shared across all requests)
        self.memory_manager = MemoryManager(
            model=model,
            api_key=resolved_api_key
        )

        # Load system prompt once
        self.system_prompt = _build_system_prompt()

        # Initialize LiteLLM model once
        self.litellm_model = LiteLLMModel(model_id=model)

        logger.info(f"Initialized StatelessAgent with model {model}")


    def chat(
        self,
        query: str,
        user_id: str,
        run_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> str:
        """
        Process user query with memory context.

        Args:
            query: User's message
            user_id: User identifier for memory isolation
            run_id: Session identifier (auto-generated if None)
            agent_id: Agent identifier (defaults to "memory-agent")

        Returns:
            Agent's response text
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        # Auto-generate run_id if not provided
        if not run_id:
            import uuid
            run_id = str(uuid.uuid4())[:8]

        # Default agent_id
        if not agent_id:
            agent_id = "memory-agent"

        logger.info(
            f"Processing chat - user: {user_id}, session: {run_id}, "
            f"query length: {len(query)}"
        )

        # Create tools with user context for THIS request
        search_tool = _create_search_memory_tool(
            self.memory_manager,
            user_id,
            agent_id,
            run_id
        )
        insert_tool = _create_insert_memory_tool(
            self.memory_manager,
            user_id,
            agent_id,
            run_id
        )
        web_tool = _create_web_search_tool()

        # Create ephemeral Strands agent for this request
        strands_agent = StrandsAgent(
            model=self.litellm_model,
            system_prompt=self.system_prompt,
            tools=[search_tool, insert_tool, web_tool]
        )

        try:
            # Process message
            result = strands_agent(query)

            # Extract text response
            response_text = self._extract_response_text(result)

            logger.info(
                f"Response generated - user: {user_id}, session: {run_id}, "
                f"length: {len(response_text)}"
            )

            # Store conversation in background
            self._store_conversation_async(
                user_id=user_id,
                run_id=run_id,
                agent_id=agent_id,
                user_message=query,
                assistant_message=response_text
            )

            return response_text

        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            raise


    def _extract_response_text(self, result) -> str:
        """Extract text from Strands agent result."""
        content = result.message.get("content", [])
        text_parts = []

        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_parts.append(block["text"])

        return " ".join(text_parts).strip()


    def _store_conversation_async(
        self,
        user_id: str,
        run_id: str,
        agent_id: str,
        user_message: str,
        assistant_message: str
    ) -> None:
        """Store conversation in memory backend."""
        try:
            _run_async(
                self.memory_manager.add_conversation(
                    user_id=user_id,
                    user_message=user_message,
                    assistant_message=assistant_message,
                    agent_id=agent_id,
                    run_id=run_id
                )
            )
            logger.debug(f"Stored conversation for user={user_id}, session={run_id}")

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
