# Problem 1: Simple Memory Agent - Walkthrough

## Overview

This is a **solved example** that demonstrates the fundamental pattern for maintaining conversation memory in AI agents. Study this implementation to understand how circular buffers work before moving to Problem 2.

**Time to Review**: 30-45 minutes
**Points**: 50 (understanding check only)

## Learning Objectives

By studying this solved example, you will understand:

1. How to maintain conversation state across multiple turns
2. The circular buffer data structure for memory management
3. Token budget management and context window constraints
4. Formatting conversation history for LLM context
5. Basic memory eviction strategies (FIFO)

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Simple Memory Agent                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         Circular Buffer Memory              │    │
│  │  ┌────┬────┬────┬────┬────┬────┬────┬────┐ │    │
│  │  │ M1 │ M2 │ M3 │ M4 │ M5 │ M6 │ M7 │ M8 │ │    │
│  │  └────┴────┴────┴────┴────┴────┴────┴────┘ │    │
│  │         ^                             ^      │    │
│  │      oldest                      newest      │    │
│  │                                              │    │
│  │  When buffer is full:                        │    │
│  │  - New message evicts oldest message         │    │
│  │  - FIFO (First In, First Out) strategy      │    │
│  └────────────────────────────────────────────┘    │
│                       ↓                             │
│  ┌────────────────────────────────────────────┐    │
│  │        Format for LLM Context               │    │
│  │                                              │    │
│  │  System: You are a helpful assistant...     │    │
│  │  User: [message 1]                          │    │
│  │  Assistant: [response 1]                    │    │
│  │  User: [message 2]                          │    │
│  │  Assistant: [response 2]                    │    │
│  │  ...                                         │    │
│  └────────────────────────────────────────────┘    │
│                       ↓                             │
│  ┌────────────────────────────────────────────┐    │
│  │              Claude API                     │    │
│  │        (Amazon Bedrock or Anthropic)        │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Key Concepts

### 1. Circular Buffer

A circular buffer is a fixed-size data structure that overwrites the oldest data when full:

```python
class CircularBuffer:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.buffer = []

    def add(self, item):
        if len(self.buffer) >= self.max_size:
            self.buffer.pop(0)  # Remove oldest
        self.buffer.append(item)  # Add newest
```

**Benefits**:
- Fixed memory footprint
- Predictable token usage
- Simple implementation
- Fast operations (O(1) amortized)

**Trade-offs**:
- Loses old context
- No semantic awareness
- Cannot retrieve specific memories

### 2. Token Budget Management

LLMs have context window limits (e.g., Claude 3: 200K tokens). We must:

1. **Track token usage**: Approximate tokens per message
2. **Set buffer limits**: Conservative estimate to avoid exceeding limits
3. **Format efficiently**: Minimize system prompt overhead

```python
# Rough estimate: 1 token ≈ 4 characters
def estimate_tokens(text: str) -> int:
    return len(text) // 4

# Set buffer size based on token budget
MAX_CONTEXT_TOKENS = 4000
AVG_MESSAGE_TOKENS = 100
MAX_MESSAGES = MAX_CONTEXT_TOKENS // AVG_MESSAGE_TOKENS  # 40 messages
```

### 3. Conversation Formatting

Conversation history must be formatted for the LLM:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Tell me more."},
]
```

## Code Walkthrough

### File: `memory.py`

The circular buffer implementation:

```python
from collections import deque
from typing import Dict, List

class ConversationMemory:
    """Circular buffer for conversation history."""

    def __init__(
        self,
        max_turns: int = 10
    ):
        """Initialize memory with maximum conversation turns.

        Args:
            max_turns: Maximum number of conversation turns to store
        """
        self.max_turns = max_turns
        self.messages: deque = deque(maxlen=max_turns * 2)

    def add_user_message(self, content: str) -> None:
        """Add a user message to memory."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to memory."""
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in conversation order."""
        return list(self.messages)

    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages.clear()
```

**Key Points**:
- Uses `collections.deque` with `maxlen` for automatic eviction
- Stores messages as role-content dictionaries
- Simple API: add messages, retrieve history, clear

### File: `agent.py`

The conversational agent using memory:

```python
import os
from anthropic import Anthropic
from memory import ConversationMemory

class SimpleMemoryAgent:
    """Conversational agent with circular buffer memory."""

    def __init__(
        self,
        max_turns: int = 10,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.memory = ConversationMemory(max_turns=max_turns)
        self.model = model
        self.system_prompt = "You are a helpful assistant with memory of our conversation."

    def chat(self, user_input: str) -> str:
        """Process user input and return assistant response."""
        # Add user message to memory
        self.memory.add_user_message(user_input)

        # Get full conversation history
        messages = self.memory.get_messages()

        # Call Claude with conversation history
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages
        )

        # Extract response text
        assistant_response = response.content[0].text

        # Add assistant response to memory
        self.memory.add_assistant_message(assistant_response)

        return assistant_response
```

**Key Points**:
- Memory is passed to LLM on every turn
- Agent automatically maintains conversation context
- Simple stateful interface: just call `chat()`

## Running the Example

### 1. Set up environment

```bash
cd simple-memory-agent
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Run the agent

```bash
uv run python agent.py
```

### 3. Test conversation

```python
# The agent demonstrates multi-turn memory:

agent = SimpleMemoryAgent(max_turns=5)

# Turn 1
response1 = agent.chat("My name is Alice")
# Assistant: Nice to meet you, Alice!

# Turn 2
response2 = agent.chat("What is my name?")
# Assistant: Your name is Alice.

# Turn 3 (6 turns later, after buffer fills)
response3 = agent.chat("Do you remember my name?")
# Assistant: I don't see your name in our recent conversation...
```

## Understanding Memory Limits

When the circular buffer fills up:

```
Initial state (max_turns=3):
┌────────────────────────────────────┐
│ Buffer: [empty]                    │
└────────────────────────────────────┘

After 3 turns:
┌────────────────────────────────────┐
│ Buffer: [U1, A1, U2, A2, U3, A3]   │
│         (FULL)                     │
└────────────────────────────────────┘

After 4th turn:
┌────────────────────────────────────┐
│ Buffer: [U2, A2, U3, A3, U4, A4]   │
│         ^^^^^                      │
│         U1, A1 evicted!            │
└────────────────────────────────────┘
```

The agent **loses memory** of U1 and A1!

## Study Questions

Consider these questions as you review the code:

1. **Why use a circular buffer instead of storing all messages?**
   - Hint: Think about token limits and cost

2. **What happens to old context when the buffer fills up?**
   - Hint: Trace through several conversation turns

3. **How would you handle system-critical information?**
   - Hint: What if user says "My password is X" and it gets evicted?

4. **What are the limitations of this approach?**
   - Hint: Consider long conversations, important facts, semantic search

5. **When is this pattern sufficient?**
   - Hint: Think about use cases and conversation length

## Next Steps

After understanding this example, proceed to **Problem 2** where you'll implement:

- Multi-tier memory (short, medium, long-term)
- Conversation summarization to compress old context
- Semantic search with embeddings
- Intelligent memory retrieval strategies

## Reflection Questions (Not Graded)

Write brief answers to these questions:

1. Explain how the circular buffer prevents memory from growing indefinitely.

2. What are the trade-offs between a small buffer (5 turns) vs large buffer (50 turns)?

3. How would you modify this design if the agent needed to remember specific user preferences forever?

4. Describe a scenario where this simple memory pattern would be insufficient.

These reflections will help you appreciate why Problem 2's hierarchical memory system is necessary for production agents.
