"""
Conversational agent with hierarchical memory system.

TODO: Complete this module to implement the full memory lifecycle.
"""

import logging
import os
from typing import (
    Dict,
    List,
    Optional,
)

from anthropic import Anthropic
from dotenv import load_dotenv

from memory.short_term import ShortTermMemory
from memory.medium_term import SummaryMemory
from memory.long_term import SemanticMemory


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ConversationalMemoryAgent:
    """Agent with hierarchical memory: short-term, medium-term, and long-term.

    This agent implements a sophisticated memory system that:
    1. Maintains recent context in short-term memory (circular buffer)
    2. Summarizes old conversations when buffer fills
    3. Stores summaries in long-term memory with semantic search
    4. Retrieves relevant context combining recency and relevance
    """

    def __init__(
        self,
        short_term_turns: int = 10,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None
    ):
        """Initialize the conversational memory agent.

        Args:
            short_term_turns: Maximum turns in short-term memory
            model: Claude model for conversations
            api_key: Anthropic API key (reads from env if not provided)
        """
        # Get API key
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # TODO: Initialize API client
        # Hint: self.client = Anthropic(api_key=api_key)

        # TODO: Initialize three memory tiers
        # Hint:
        # self.short_term = ShortTermMemory(max_turns=short_term_turns)
        # self.medium_term = SummaryMemory(self.client)
        # self.long_term = SemanticMemory()

        # TODO: Store configuration
        self.model = model
        self.system_prompt = (
            "You are a helpful assistant with hierarchical memory. "
            "You can recall information from previous conversations."
        )

        # TODO: Track global turn counter
        # Hint: self.total_turns = 0

        logger.info(
            f"Initialized ConversationalMemoryAgent with "
            f"short-term: {short_term_turns} turns, model: {model}"
        )


    def chat(
        self,
        user_input: str,
        max_tokens: int = 1024
    ) -> str:
        """Process user input with hierarchical memory management.

        This is the core method that implements the memory lifecycle:
        1. Add user message to short-term
        2. Check if short-term is full → summarize if needed
        3. Retrieve context (short-term + relevant long-term)
        4. Call Claude with context
        5. Add response to short-term
        6. Return response

        Args:
            user_input: User's message
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        logger.info(f"Processing user input (turn {self.total_turns + 1})")

        # TODO: Add user message to short-term memory
        # Hint: self.short_term.add_user_message(user_input)

        # TODO: Increment turn counter
        # Hint: self.total_turns += 1

        # TODO: Check if short-term memory is full
        # If full, trigger summarization:
        #   1. Get all messages from short-term
        #   2. Calculate turn range for this batch
        #   3. Generate summary using medium-term
        #   4. Add summary to long-term with embedding
        #   5. Clear short-term memory
        # Hint: if self.short_term.is_full():
        #           self._handle_memory_overflow()

        # TODO: Retrieve context for LLM
        # Hint: context = self._retrieve_context(user_input)

        # TODO: Call Claude with context
        # Hint: Use self.client.messages.create()

        # TODO: Extract response text

        # TODO: Add assistant response to short-term memory

        # TODO: Return response

        logger.info(
            f"Response generated. Memory: "
            f"short-term {self.short_term.get_turn_count()} turns, "
            f"long-term {self.long_term.get_summary_count()} summaries"
        )

        return "TODO: Implement chat method"


    def _handle_memory_overflow(self) -> None:
        """Handle short-term memory overflow by summarizing and archiving.

        This private method:
        1. Gets messages from short-term memory
        2. Generates a summary
        3. Stores summary in long-term memory
        4. Clears short-term memory
        """
        # TODO: Get all messages from short-term
        # Hint: messages = self.short_term.get_messages()

        # TODO: Calculate turn range for this batch
        # Hint: Use self.total_turns and short_term turn count

        # TODO: Generate summary
        # Hint: summary = self.medium_term.summarize_conversation(messages, turn_range)

        # TODO: Add summary to long-term memory with embedding
        # Hint: self.long_term.add_summary(summary, turn_range)

        # TODO: Clear short-term memory
        # Hint: self.short_term.clear()

        logger.info(
            f"Memory overflow handled: summarized and archived turns "
            f"{turn_range[0]}-{turn_range[1]}"
        )


    def _retrieve_context(
        self,
        current_message: str
    ) -> List[Dict[str, str]]:
        """Retrieve relevant context for current message.

        Strategy:
        1. Always include all short-term memory (recent context)
        2. Search long-term for semantically relevant summaries
        3. Format summaries as system messages
        4. Combine: [summary messages] + [recent messages]

        Args:
            current_message: Current user message

        Returns:
            List of messages formatted for Claude API
        """
        # TODO: Get all messages from short-term memory
        # Hint: recent_messages = self.short_term.get_messages()

        # TODO: Search long-term memory for relevant summaries
        # Hint: relevant_summaries = self.long_term.search(current_message, top_k=3)

        # TODO: Format summaries as system messages
        # Hint: Create messages like:
        # {"role": "system", "content": f"Previous conversation: {summary}"}

        # TODO: Combine summary messages + recent messages
        # Order: [summaries first] + [recent messages]

        # TODO: Return combined context

        logger.debug(
            f"Retrieved context: {len(relevant_summaries)} summaries + "
            f"{len(recent_messages)} recent messages"
        )

        return []


    def reset(self) -> None:
        """Clear all memory tiers and start fresh."""
        # TODO: Clear all three memory tiers
        # Hint: Call clear() on short_term, long_term, and reset turn counter

        logger.info("Reset all memory tiers")


    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about memory usage.

        Returns:
            Dictionary with memory statistics
        """
        # TODO: Implement statistics
        # Hint: Return dict with:
        # - total_turns
        # - short_term_turns
        # - long_term_summaries

        return {
            "total_turns": 0,
            "short_term_turns": 0,
            "long_term_summaries": 0,
        }


def _run_demo() -> None:
    """Run a demonstration of the hierarchical memory agent."""
    print("=" * 60)
    print("Conversational Memory Agent Demo")
    print("=" * 60)
    print()

    # TODO: Create agent with small short-term buffer
    # agent = ConversationalMemoryAgent(short_term_turns=5)

    # TODO: Run test conversation demonstrating:
    # 1. Short conversation (no summarization)
    # 2. Memory overflow (triggers summarization)
    # 3. Semantic recall (retrieves old relevant context)

    print("\nDemo not yet implemented. Complete the TODOs first!")


if __name__ == "__main__":
    _run_demo()
