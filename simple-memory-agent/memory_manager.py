"""
Memory management abstraction layer for agent memory operations.

This module provides a backend-agnostic interface for memory management,
currently implemented with Mem0 but designed to be swappable with other
solutions (langmem, custom implementations, etc.). The abstraction allows
the agent to remain independent of the specific memory backend.

Memory Types:
- Semantic: Facts, knowledge, and information extracted from conversations
- Episodic: Specific conversation turns and interaction history
- Preference: User preferences, likes/dislikes, and behavioral patterns
- Summary: Condensed summaries of longer conversation sequences

Usage Example:
    import asyncio

    # Initialize memory manager (synchronous)
    manager = MemoryManager(
        user_id="user_123",
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )

    # All memory operations are async and must be awaited
    async def example_usage():
        # Insert memory directly
        result = await manager.insert(
            content="User prefers Python for data processing",
            metadata={"type": "preference", "category": "programming"}
        )

        # Search for memories
        memories = await manager.search(query="programming preferences", limit=5)

        # Add conversation turn (episodic memory)
        await manager.add_conversation(
            user_message="What's my favorite language?",
            assistant_message="You prefer Python for data processing."
        )

        # Export all memories
        export_data = await manager.export(format="json")

        # Get statistics
        stats = await manager.get_stats()

        # Clear all memories (use with caution!)
        await manager.clear()

    # Run async operations
    asyncio.run(example_usage())

Integration with Agent:
    The MemoryManager can be used directly in agent.py to replace inline
    memory operations, making the agent backend-independent. All methods
    must be awaited:

    # In agent.py __init__:
    self.memory_manager = MemoryManager(user_id, model, api_key)

    # Replace direct memory.add() calls (use await):
    await self.memory_manager.add_conversation(user_input, response_text)

    # Use in tools (use await):
    search_results = await self.memory_manager.search(query, limit)
    insert_result = await self.memory_manager.insert(content, metadata)
"""

import json
import logging
import os
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from mem0 import AsyncMemory


# Configure logging
logger = logging.getLogger(__name__)

# Suppress Mem0 internal error logs for known non-fatal PointStruct validation errors
# See KNOWN_ISSUES.md for details about Mem0 1.x bug with event='NONE' updates
# GitHub issues: #3640, #3780 | PR: #3653 (pending merge)
logging.getLogger("mem0").setLevel(logging.CRITICAL)
logging.getLogger("mem0.memory").setLevel(logging.CRITICAL)
logging.getLogger("mem0.memory.main").setLevel(logging.CRITICAL)


# Monkey patch Mem0's LiteLLM to fix Anthropic compatibility issue
# Anthropic models don't allow both temperature and top_p to be set
def _patch_mem0_litellm():
    """
    Patch Mem0's LiteLLM implementation to remove top_p for Anthropic models.

    This fixes the issue where Mem0 sends both temperature and top_p to Anthropic,
    which rejects requests with both parameters set.
    """
    try:
        from mem0.llms.litellm import LiteLLM
        import litellm

        # Store original method
        original_generate = LiteLLM.generate_response

        def patched_generate_response(self, messages, response_format=None, tools=None, tool_choice="auto"):
            """Patched version that removes top_p for Anthropic models."""
            if not litellm.supports_function_calling(self.config.model):
                raise ValueError(f"Model '{self.config.model}' in litellm does not support function calling.")

            params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }

            # Only add top_p for non-Anthropic models
            model_name = self.config.model.lower()
            if "claude" not in model_name and "anthropic" not in model_name:
                params["top_p"] = self.config.top_p

            if response_format:
                params["response_format"] = response_format
            if tools:
                params["tools"] = tools
                params["tool_choice"] = tool_choice

            response = litellm.completion(**params)
            return self._parse_response(response, tools)

        # Replace the method
        LiteLLM.generate_response = patched_generate_response
        logger.info("Successfully patched Mem0 LiteLLM for Anthropic compatibility")

    except Exception as e:
        logger.warning(f"Could not patch Mem0 LiteLLM: {e}")


# Apply the patch immediately
_patch_mem0_litellm()

# Constants
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
QDRANT_PATH: str = "./qdrant_data"
COLLECTION_NAME: str = "agent_memories"
EMBEDDING_DIMS: int = 384


def _initialize_mem0_config(
    model: str,
    api_key: str
) -> Dict[str, Any]:
    """Initialize Mem0 configuration with Qdrant and HuggingFace embeddings.

    Args:
        model: LLM model identifier for Mem0 operations
        api_key: API key for the LLM provider

    Returns:
        Configuration dictionary for Mem0 initialization
    """
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "path": QDRANT_PATH,
                "collection_name": COLLECTION_NAME,
                "embedding_model_dims": EMBEDDING_DIMS,
            }
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": EMBEDDING_MODEL,
            }
        },
        "llm": {
            "provider": "litellm",
            "config": {
                "model": model,
                "api_key": api_key,
                "temperature": 0.7,
                # Note: Anthropic models don't allow both temperature and top_p
                # So we only set temperature here
            }
        }
    }

    logger.info(f"Initialized Mem0 config with Qdrant at {QDRANT_PATH}")
    logger.debug(f"Config:\n{json.dumps(config, indent=2, default=str)}")

    return config


class MemoryManager:
    """Abstract memory management that can be swapped with different backends.

    This pattern allows replacing Mem0 with other solutions (langmem, custom, etc.)
    while keeping the agent interface the same. The manager handles all memory
    operations including storage, retrieval, search, and export.

    Memory categorization:
    - Semantic memories: Facts, knowledge, preferences extracted from conversations
    - Episodic memories: Specific conversation turns and interaction sequences
    - Preference memories: User likes, dislikes, and behavioral patterns
    - Summary memories: Condensed representations of conversation history

    IMPORTANT: This class uses async/await patterns. All memory operations
    (insert, search, get_all, add_conversation, clear, export, get_stats)
    are async methods and must be awaited.

    Attributes:
        user_id: User identifier for memory association
        memory: Backend memory instance (currently Mem0 AsyncMemory)
    """

    def __init__(
        self,
        model: str,
        api_key: str
    ):
        """Initialize the memory manager with backend configuration.

        This creates a SINGLE multi-tenant MemoryManager that services all users
        and sessions. User identification and session context are passed as parameters
        to each method call, not stored as instance variables.

        Args:
            model: LLM model identifier for memory operations
            api_key: API key for the LLM provider

        Raises:
            ValueError: If api_key is missing

        Note:
            Multi-tenant architecture:
            - ONE MemoryManager instance serves ALL users/sessions
            - user_id, agent_id, run_id passed as method parameters
            - Each user's memories are isolated by user_id
            - Sessions organized by run_id for better context tracking
            - Efficient resource usage (single backend connection)
        """
        if not api_key:
            raise ValueError("api_key is required for memory operations")

        logger.info("Initializing multi-tenant MemoryManager (services all users/sessions)")

        # Initialize Mem0 async backend
        config = _initialize_mem0_config(model, api_key)

        # AsyncMemory.from_config is async, so we need to run it synchronously
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            # If there's already a loop, run in thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, AsyncMemory.from_config(config))
                self.memory = future.result()
        except RuntimeError:
            # No loop running, safe to use asyncio.run()
            self.memory = asyncio.run(AsyncMemory.from_config(config))

        logger.info("Async memory backend initialized successfully")


    async def insert(
        self,
        user_id: str,
        content: str,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Insert memory asynchronously for a specific user/session.

        This async method stores content in the memory backend with optional metadata.
        Multi-tenant: user_id, agent_id, and run_id are passed as parameters to
        isolate memories per user and organize by session.

        Memory type examples:
        - Semantic: "User is a software engineer specializing in Python"
        - Preference: "User prefers clean, maintainable code over clever solutions"
        - Episodic: Conversation turn stored with timestamp
        - Summary: "User discussed machine learning projects for 10 minutes"

        Args:
            user_id: User identifier (required for multi-tenant isolation)
            content: The information to store in memory
            agent_id: Agent identifier for multi-agent scenarios (optional)
            run_id: Session/conversation identifier (optional)
            metadata: Optional metadata dictionary (e.g., type, timestamp, tags)

        Returns:
            Dictionary with operation status and stored information

        Raises:
            ValueError: If user_id or content is empty
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if not content or not content.strip():
            raise ValueError("Memory content cannot be empty")

        try:
            logger.info(
                f"Inserting memory for user={user_id}, agent={agent_id}, "
                f"session={run_id}: '{content[:100]}...'"
            )
            logger.debug(f"Metadata: {metadata}")

            # Merge provided metadata with session context
            full_metadata = metadata or {}
            if agent_id:
                full_metadata["agent_id"] = agent_id
            if run_id:
                full_metadata["run_id"] = run_id

            # Store in Mem0 async backend with full context
            await self.memory.add(
                messages=[{"role": "user", "content": content}],
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                metadata=full_metadata
            )

            logger.info(f"Memory stored for user={user_id} with context (agent={agent_id}, session={run_id})")

            result = {
                "status": "success",
                "message": "Memory stored successfully",
                "content": content,
                "metadata": metadata,
                "user_id": user_id
            }

            logger.info("Memory inserted successfully")
            logger.debug(f"Result:\n{json.dumps(result, indent=2, default=str)}")

            return result

        except Exception as e:
            logger.error(f"Error inserting memory: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


    async def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        run_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories asynchronously for a specific user with optional filtering.

        Performs semantic search across stored memories using vector similarity.
        Multi-tenant: user_id isolates search to specific user's memories.
        Returns the most relevant memories ranked by relevance score. Must be awaited.

        IMPORTANT: Search retrieves memories from ALL sessions for the user (cross-session recall).
        We do NOT filter by run_id during search - we want the agent to recall information
        from any previous conversation, not just the current session.

        Args:
            user_id: User identifier (required for multi-tenant isolation)
            query: Search query to find relevant memories
            limit: Maximum number of memories to return (default: 5)
            run_id: Provided for context but NOT used in search (cross-session recall)
            agent_id: Filter by specific agent (optional)
            metadata_filters: Filter by metadata (e.g., {"tags": {"in": ["work"]}})

        Returns:
            List of memory dictionaries with content, scores, and metadata

        Raises:
            ValueError: If user_id or query is empty, or limit is invalid

        Note:
            Multi-tenant filtering:
            - Each user only sees their own memories (user_id isolation)
            - Searches across ALL sessions (no run_id filter for cross-session recall)
            - Optional agent filter: search(user_id, query, agent_id="assistant-1")
            - Optional metadata filter: search(user_id, query, metadata_filters={"tags": {"in": ["work"]}})
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        try:
            logger.info(
                f"Searching memories for user={user_id}: '{query}' "
                f"(limit={limit}, searching across ALL sessions)"
            )

            # Build search parameters
            search_params = {
                "query": query,
                "user_id": user_id,
                "limit": limit
            }

            # NOTE: We do NOT pass run_id to search!
            # We want cross-session memory recall - the agent should remember
            # information from ALL previous sessions, not just the current one.
            # User isolation is handled by user_id alone.

            if agent_id:
                search_params["agent_id"] = agent_id
            # run_id is intentionally NOT included - we want cross-session recall
            if metadata_filters:
                search_params["metadata_filters"] = metadata_filters

            # Search using Mem0 async backend with filters
            results = await self.memory.search(**search_params)

            if not results:
                logger.info("No memories found for query")
                return []

            # Normalize results to consistent format
            memories = []
            for mem in results:
                if isinstance(mem, dict):
                    memories.append({
                        "id": mem.get("id", "unknown"),
                        "memory": mem.get("memory", str(mem)),
                        "score": mem.get("score", 1.0),
                        "created_at": mem.get("created_at", ""),
                        "metadata": mem.get("metadata", {})
                    })
                else:
                    # Handle string results from backend
                    memories.append({
                        "id": "unknown",
                        "memory": str(mem),
                        "score": 1.0,
                        "created_at": "",
                        "metadata": {}
                    })

            logger.info(f"Found {len(memories)} relevant memories")
            logger.debug(f"Results:\n{json.dumps(memories, indent=2, default=str)}")

            return memories

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []


    async def export(
        self,
        user_id: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Export all memories to JSON or other format asynchronously.

        Retrieves all stored memories for the user and formats them for export.
        Useful for backup, analysis, or migration to other systems. Must be awaited.

        Args:
            user_id: User identifier (required for multi-tenant isolation)
            format: Export format (currently only "json" supported)

        Returns:
            Dictionary containing all memories and metadata

        Raises:
            ValueError: If user_id is empty or format is not supported
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        if format not in ["json"]:
            raise ValueError(f"Unsupported export format: {format}. Use 'json'")

        try:
            logger.info(f"Exporting memories for user={user_id} in {format} format")

            # Get all memories from async backend
            all_memories = await self.memory.get_all(user_id=user_id)

            export_data = {
                "user_id": user_id,
                "format": format,
                "memory_count": len(all_memories),
                "memories": all_memories,
                "backend": "mem0",
                "collection": COLLECTION_NAME
            }

            logger.info(f"Exported {len(all_memories)} memories for user={user_id}")
            logger.debug(f"Export data:\n{json.dumps(export_data, indent=2, default=str)}")

            return export_data

        except Exception as e:
            logger.error(f"Error exporting memories for user={user_id}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "user_id": user_id
            }


    async def get_all(
        self,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all memories for a specific user asynchronously.

        Retrieves all stored memories for the given user, optionally limited to a
        specific count. Multi-tenant: user_id isolates memories to specific user.
        Returns memories in reverse chronological order (newest first). Must be awaited.

        Args:
            user_id: User identifier (required for multi-tenant isolation)
            limit: Optional maximum number of memories to return

        Returns:
            List of all memory dictionaries for the user

        Raises:
            ValueError: If user_id is empty
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        try:
            logger.info(f"Retrieving all memories for user={user_id}")

            # Get all memories from async backend for specific user
            memories = await self.memory.get_all(user_id=user_id)

            # Ensure memories is a list (some backends might return dict-like objects)
            if isinstance(memories, dict):
                # If it's a dict, try to extract the memories list
                memories = memories.get("results", memories.get("memories", []))

            # Convert to list if needed
            if not isinstance(memories, list):
                memories = list(memories) if hasattr(memories, '__iter__') else []

            if limit and limit > 0:
                memories = memories[:limit]
                logger.info(f"Limited results to {limit} memories for user={user_id}")

            logger.info(f"Retrieved {len(memories)} total memories for user={user_id}")
            logger.debug(f"Memories:\n{json.dumps(memories, indent=2, default=str)}")

            return memories

        except Exception as e:
            logger.error(f"Error retrieving all memories for user={user_id}: {e}")
            return []


    async def clear(self, user_id: str) -> None:
        """Clear all memories for a specific user asynchronously.

        WARNING: This operation permanently deletes all stored memories for
        the user. Multi-tenant: only affects specified user's memories.
        Use with caution. Cannot be undone. Must be awaited.

        Args:
            user_id: User identifier (required for multi-tenant isolation)

        Raises:
            ValueError: If user_id is empty
            RuntimeError: If memory deletion fails
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        try:
            logger.warning(f"Clearing all memories for user: {user_id}")

            # Get all memories from async backend for specific user
            all_memories = await self.memory.get_all(user_id=user_id)
            memory_count = len(all_memories)

            # Delete each memory individually using async backend
            for mem in all_memories:
                # Handle both dict and string formats
                if isinstance(mem, dict):
                    memory_id = mem.get("id")
                    if memory_id:
                        await self.memory.delete(memory_id=memory_id)
                elif isinstance(mem, str):
                    # If mem is a string, it might be the memory ID itself
                    logger.debug(f"Skipping string memory entry: {mem[:50]}...")

            logger.info(f"Cleared {memory_count} memories successfully")

        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            raise RuntimeError(f"Failed to clear memories: {e}") from e


    async def add_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_message: str,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a conversation turn to memory asynchronously for a specific user/session.

        Stores a complete conversation exchange (user message + assistant response)
        as an episodic memory. Multi-tenant: user_id isolates conversation history.
        This method is typically called automatically by the agent after each interaction.

        Args:
            user_id: User identifier (required for multi-tenant isolation)
            user_message: User's message
            assistant_message: Assistant's response
            agent_id: Agent identifier (optional)
            run_id: Session/conversation identifier (optional)
            metadata: Optional metadata for the conversation turn
        """
        try:
            messages = [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message}
            ]

            # Enhance metadata with session context
            full_metadata = metadata or {}
            full_metadata.update({
                "conversation_turn": True,
                "type": "episodic"
            })

            logger.debug(
                f"Adding conversation for user={user_id}, agent={agent_id}, session={run_id} "
                f"(user msg length: {len(user_message)})"
            )

            await self.memory.add(
                messages=messages,
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                metadata=full_metadata
            )

            logger.debug(f"Conversation stored for user={user_id} with context (agent={agent_id}, session={run_id})")

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            # Don't raise - conversation storage failure shouldn't break agent


    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a specific user asynchronously.

        Multi-tenant: returns stats only for specified user's memories.
        Must be awaited.

        Args:
            user_id: User identifier (required for multi-tenant isolation)

        Returns:
            Dictionary containing memory count and other statistics

        Raises:
            ValueError: If user_id is empty
        """
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        try:
            all_memories = await self.memory.get_all(user_id=user_id)

            stats = {
                "user_id": user_id,
                "total_memories": len(all_memories),
                "backend": "mem0",
                "collection": COLLECTION_NAME
            }

            logger.info(f"Memory stats for user={user_id}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting memory stats for user={user_id}: {e}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
