"""
Short-term memory using circular buffer (same as Problem 1).

This module is provided as-is from the simple memory agent example.
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


class ShortTermMemory:
    """Circular buffer for recent conversation history.

    This is the same implementation as ConversationMemory from Problem 1,
    renamed for clarity in the hierarchical memory system.
    """

    def __init__(
        self,
        max_turns: int = 10
    ):
        """Initialize short-term memory.

        Args:
            max_turns: Maximum conversation turns to store
        """
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")

        self.max_turns = max_turns
        self.messages: deque = deque(maxlen=max_turns * 2)
        logger.info(f"Initialized short-term memory with max {max_turns} turns")


    def add_user_message(
        self,
        content: str
    ) -> None:
        """Add a user message to the buffer."""
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        message = {"role": "user", "content": content}
        self.messages.append(message)


    def add_assistant_message(
        self,
        content: str
    ) -> None:
        """Add an assistant message to the buffer."""
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        message = {"role": "assistant", "content": content}
        self.messages.append(message)


    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in conversation order."""
        return list(self.messages)


    def get_turn_count(self) -> int:
        """Get the current number of complete conversation turns."""
        return len(self.messages) // 2


    def is_full(self) -> bool:
        """Check if the memory buffer is at maximum capacity."""
        return len(self.messages) >= self.max_turns * 2


    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages.clear()
        logger.info("Cleared short-term memory")
