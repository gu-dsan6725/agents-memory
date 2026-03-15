"""
Circular buffer memory for conversational agents.

This module implements a simple FIFO (First In, First Out) memory
buffer for storing conversation history with automatic eviction of
oldest messages when capacity is reached.
"""

import logging
from collections import deque
from typing import (
    Dict,
    List,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Circular buffer for conversation history management.

    This class implements a fixed-size conversation buffer that automatically
    evicts the oldest messages when the maximum capacity is reached. It maintains
    conversation turns (user message + assistant response pairs).

    Attributes:
        max_turns: Maximum number of conversation turns to store
        messages: Deque storing message dictionaries with role and content
    """

    def __init__(
        self,
        max_turns: int = 10
    ):
        """Initialize conversation memory with maximum turns.

        Args:
            max_turns: Maximum number of conversation turns (user + assistant pairs)
                      to store. Each turn consists of 2 messages, so buffer size
                      is max_turns * 2.
        """
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")

        self.max_turns = max_turns
        # Use deque with maxlen for automatic FIFO eviction
        # Each turn has 2 messages (user + assistant), so maxlen = max_turns * 2
        self.messages: deque = deque(maxlen=max_turns * 2)
        logger.info(f"Initialized conversation memory with max {max_turns} turns")


    def add_user_message(
        self,
        content: str
    ) -> None:
        """Add a user message to the conversation buffer.

        Args:
            content: The user's message content
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        message = {"role": "user", "content": content}
        self.messages.append(message)
        logger.debug(f"Added user message. Buffer size: {len(self.messages)}")


    def add_assistant_message(
        self,
        content: str
    ) -> None:
        """Add an assistant message to the conversation buffer.

        Args:
            content: The assistant's response content
        """
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        message = {"role": "assistant", "content": content}
        self.messages.append(message)
        logger.debug(f"Added assistant message. Buffer size: {len(self.messages)}")


    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in conversation order.

        Returns:
            List of message dictionaries, each with 'role' and 'content' keys
        """
        return list(self.messages)


    def get_turn_count(self) -> int:
        """Get the current number of complete conversation turns.

        Returns:
            Number of complete turns (user + assistant pairs)
        """
        return len(self.messages) // 2


    def is_full(self) -> bool:
        """Check if the memory buffer is at maximum capacity.

        Returns:
            True if buffer is full, False otherwise
        """
        return len(self.messages) >= self.max_turns * 2


    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages.clear()
        logger.info("Cleared conversation memory")


    def estimate_tokens(self) -> int:
        """Estimate total tokens in current conversation history.

        Uses rough approximation: 1 token ≈ 4 characters

        Returns:
            Estimated token count
        """
        total_chars = sum(len(msg["content"]) for msg in self.messages)
        estimated_tokens = total_chars // 4
        logger.debug(f"Estimated tokens: {estimated_tokens}")
        return estimated_tokens
