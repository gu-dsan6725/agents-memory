"""
Simple memory agent with circular buffer conversation history.

This module demonstrates a basic conversational agent that maintains
context using a circular buffer memory pattern.
"""

import logging
import os
from typing import Optional

from anthropic import Anthropic
from dotenv import load_dotenv

from memory import ConversationMemory


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,p%(process)s,{%(filename)s:%(lineno)d},%(levelname)s,%(message)s",
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SimpleMemoryAgent:
    """Conversational agent with circular buffer memory.

    This agent maintains conversation context using a fixed-size circular
    buffer that automatically evicts old messages when full.

    Attributes:
        client: Anthropic API client
        memory: Circular buffer for conversation history
        model: Claude model identifier
        system_prompt: System instructions for the agent
    """

    def __init__(
        self,
        max_turns: int = 10,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None
    ):
        """Initialize the simple memory agent.

        Args:
            max_turns: Maximum conversation turns to remember
            model: Claude model to use
            api_key: Anthropic API key (reads from env if not provided)
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = Anthropic(api_key=api_key)
        self.memory = ConversationMemory(max_turns=max_turns)
        self.model = model
        self.system_prompt = (
            "You are a helpful assistant with memory of our conversation. "
            "You can reference previous messages in our discussion."
        )

        logger.info(
            f"Initialized SimpleMemoryAgent with model {model} "
            f"and max {max_turns} turns"
        )


    def chat(
        self,
        user_input: str,
        max_tokens: int = 1024
    ) -> str:
        """Process user input and return assistant response.

        This method:
        1. Adds user message to memory
        2. Retrieves full conversation history
        3. Calls Claude with history as context
        4. Adds assistant response to memory
        5. Returns the response

        Args:
            user_input: User's message
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response text
        """
        if not user_input or not user_input.strip():
            raise ValueError("User input cannot be empty")

        logger.info(f"Processing user input (length: {len(user_input)} chars)")

        # Add user message to memory
        self.memory.add_user_message(user_input)

        # Get full conversation history
        messages = self.memory.get_messages()

        logger.debug(f"Sending {len(messages)} messages to Claude")
        logger.debug(f"Estimated tokens: {self.memory.estimate_tokens()}")

        try:
            # Call Claude with conversation history
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=messages
            )

            # Extract response text
            assistant_response = response.content[0].text

            # Add assistant response to memory
            self.memory.add_assistant_message(assistant_response)

            logger.info(
                f"Received response (length: {len(assistant_response)} chars). "
                f"Memory: {self.memory.get_turn_count()}/{self.memory.max_turns} turns"
            )

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise


    def reset(self) -> None:
        """Clear conversation memory and start fresh."""
        self.memory.clear()
        logger.info("Reset conversation memory")


    def get_turn_count(self) -> int:
        """Get current number of conversation turns.

        Returns:
            Number of complete turns in memory
        """
        return self.memory.get_turn_count()


    def is_memory_full(self) -> bool:
        """Check if memory buffer is at capacity.

        Returns:
            True if buffer is full
        """
        return self.memory.is_full()


def _run_demo() -> None:
    """Run a demonstration of the simple memory agent."""
    print("=" * 60)
    print("Simple Memory Agent Demo")
    print("=" * 60)
    print()

    # Create agent with small buffer to demonstrate memory limits
    agent = SimpleMemoryAgent(max_turns=3)

    print("Agent initialized with max 3 conversation turns.\n")

    # Conversation sequence
    conversations = [
        ("My name is Alice and I love programming.", "Introduction"),
        ("What is my name?", "Memory recall - should work"),
        ("I also enjoy hiking on weekends.", "Additional info"),
        ("What are my hobbies?", "Memory recall - should work"),
        ("What is Python?", "New topic"),
        ("Do you remember my name from the beginning?", "Memory recall - may fail!"),
    ]

    for i, (user_msg, description) in enumerate(conversations, 1):
        print(f"\n{'─' * 60}")
        print(f"Turn {i}: {description}")
        print(f"{'─' * 60}")
        print(f"User: {user_msg}")

        response = agent.chat(user_msg)
        print(f"Assistant: {response}")

        print(
            f"\nMemory status: {agent.get_turn_count()}/{agent.memory.max_turns} turns"
        )
        if agent.is_memory_full():
            print("⚠️  Buffer is FULL - oldest messages will be evicted!")

    print("\n" + "=" * 60)
    print("Demo completed. Notice how early context is lost!")
    print("=" * 60)


if __name__ == "__main__":
    _run_demo()
