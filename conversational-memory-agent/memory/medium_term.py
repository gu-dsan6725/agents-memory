"""
Medium-term memory with conversation summarization.

TODO: Complete this module to implement conversation summarization.
"""

import logging
from typing import (
    Dict,
    List,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


class SummaryMemory:
    """Medium-term memory that generates conversation summaries.

    This class uses an LLM to compress conversation history into
    concise summaries, reducing token usage while preserving key information.
    """

    def __init__(
        self,
        api_client,
        model: str = "claude-3-5-haiku-20241022"
    ):
        """Initialize summary memory.

        Args:
            api_client: Anthropic API client instance
            model: Claude model for summarization (use efficient Haiku model)
        """
        # TODO: Store API client and model
        # TODO: Initialize any additional state needed
        pass


    def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        turn_range: tuple[int, int]
    ) -> str:
        """Generate a concise summary of conversation turns.

        This method takes a list of conversation messages and creates
        a compressed summary that captures the key information.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            turn_range: (start_turn, end_turn) for metadata

        Returns:
            Compressed summary string (target: under 200 tokens)

        Example:
            messages = [
                {"role": "user", "content": "My name is Alice"},
                {"role": "assistant", "content": "Nice to meet you, Alice!"},
                {"role": "user", "content": "I love programming"},
                {"role": "assistant", "content": "That's great! What languages?"}
            ]
            summary = summarize_conversation(messages, (1, 2))
            # Returns: "User Alice introduced herself and expressed interest
            #           in programming. Agent acknowledged and asked follow-up."
        """
        # TODO: Format messages into a readable conversation string
        # Hint: Create a string like:
        # "User: My name is Alice\nAssistant: Nice to meet you, Alice!\n..."

        # TODO: Create a summarization prompt
        # Hint: Use a clear prompt that asks Claude to:
        # - Summarize concisely (2-3 sentences)
        # - Preserve key facts (names, preferences, decisions)
        # - Focus on important information, not pleasantries

        # TODO: Call Claude API to generate summary
        # Hint: Use the API client with max_tokens=200

        # TODO: Extract and return the summary text

        # TODO: Add error handling for API failures

        logger.info(f"Generated summary for turns {turn_range[0]}-{turn_range[1]}")
        return "TODO: Implement summarization"


    def _format_messages_for_summary(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """Format messages into a readable conversation string.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted conversation string
        """
        # TODO: Implement message formatting
        # Hint: Join messages with newlines, format as "Role: Content"
        pass


    def _create_summary_prompt(
        self,
        conversation: str
    ) -> str:
        """Create the summarization prompt.

        Args:
            conversation: Formatted conversation string

        Returns:
            Prompt for summarization
        """
        # TODO: Implement prompt creation
        # Hint: Include clear instructions for concise summarization
        pass
