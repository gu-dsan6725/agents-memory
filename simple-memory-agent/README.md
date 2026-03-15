# Simple Memory Agent - Technical Documentation

## Overview

This is a **solved reference implementation** of a conversational agent with circular buffer memory. It demonstrates the fundamental pattern for maintaining conversation context across multiple turns while respecting token budget constraints.

## Architecture

### Components

1. **ConversationMemory** (`memory.py`)
   - Circular buffer using `collections.deque`
   - Automatic FIFO eviction when full
   - Token estimation
   - Message validation

2. **SimpleMemoryAgent** (`agent.py`)
   - Stateful conversational agent
   - Integrates with Anthropic Claude API
   - Manages conversation flow
   - Memory lifecycle management

### Data Flow

```
User Input
    ↓
Add to Memory Buffer
    ↓
Retrieve Full History
    ↓
Format for Claude API
    ↓
Call Claude with Context
    ↓
Receive Response
    ↓
Add Response to Memory
    ↓
Return to User
```

## Memory Management

### Circular Buffer Implementation

The `ConversationMemory` class uses Python's `collections.deque` with `maxlen`:

```python
self.messages: deque = deque(maxlen=max_turns * 2)
```

**Properties**:
- **Fixed size**: `max_turns * 2` (user + assistant messages)
- **Automatic eviction**: Oldest message dropped when full
- **O(1) operations**: Append and pop are constant time
- **Thread-safe**: Deque operations are atomic

### Token Budget

**Estimation Formula**:
```
tokens ≈ characters / 4
```

**Example**:
- Max 10 turns = 20 messages
- Average 200 chars/message = 4,000 chars
- Estimated tokens: 1,000

**Claude Context Limits**:
- Claude 3 Haiku: 200K tokens
- Claude 3 Sonnet: 200K tokens
- Claude 3 Opus: 200K tokens

This implementation is conservative, using ~1-2K tokens for conversation history.

## API Reference

### ConversationMemory

```python
class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        """Initialize memory buffer.

        Args:
            max_turns: Maximum conversation turns to store
        """

    def add_user_message(self, content: str) -> None:
        """Add user message to buffer."""

    def add_assistant_message(self, content: str) -> None:
        """Add assistant response to buffer."""

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in conversation order."""

    def get_turn_count(self) -> int:
        """Get number of complete turns."""

    def is_full(self) -> bool:
        """Check if buffer is at capacity."""

    def clear(self) -> None:
        """Clear all messages."""

    def estimate_tokens(self) -> int:
        """Estimate total tokens in buffer."""
```

### SimpleMemoryAgent

```python
class SimpleMemoryAgent:
    def __init__(
        self,
        max_turns: int = 10,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None
    ):
        """Initialize agent.

        Args:
            max_turns: Maximum conversation turns to remember
            model: Claude model identifier
            api_key: Anthropic API key
        """

    def chat(
        self,
        user_input: str,
        max_tokens: int = 1024
    ) -> str:
        """Process user input and return response.

        Args:
            user_input: User's message
            max_tokens: Max tokens in response

        Returns:
            Assistant's response
        """

    def reset(self) -> None:
        """Clear conversation memory."""

    def get_turn_count(self) -> int:
        """Get current turn count."""

    def is_memory_full(self) -> bool:
        """Check if memory is full."""
```

## Usage Examples

### Basic Conversation

```python
from agent import SimpleMemoryAgent

# Create agent
agent = SimpleMemoryAgent(max_turns=5)

# Multi-turn conversation
response1 = agent.chat("My name is Alice")
print(response1)  # "Nice to meet you, Alice!"

response2 = agent.chat("What's my name?")
print(response2)  # "Your name is Alice."

# Reset conversation
agent.reset()
```

### Monitoring Memory

```python
agent = SimpleMemoryAgent(max_turns=3)

# Check memory status
print(f"Turns: {agent.get_turn_count()}")
print(f"Full: {agent.is_memory_full()}")
print(f"Tokens: {agent.memory.estimate_tokens()}")
```

### Running the Demo

```bash
# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run demo
uv run python agent.py
```

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Required for Claude API access
- `AWS_REGION`: Optional, for AWS Bedrock
- `AWS_ACCESS_KEY_ID`: Optional, for AWS Bedrock
- `AWS_SECRET_ACCESS_KEY`: Optional, for AWS Bedrock

### Memory Tuning

Choose `max_turns` based on use case:

| Use Case | Turns | Rationale |
|----------|-------|-----------|
| Quick Q&A | 3-5 | Minimal context needed |
| Chatbot | 10-15 | Balance context and memory |
| Assistant | 20-30 | More context for complex tasks |

**Trade-offs**:
- **Small buffer**: Fast, cheap, but limited context
- **Large buffer**: Rich context, but higher token cost

## Performance

### Benchmarks

Operations are O(1) amortized:

```
add_message:        ~0.001ms
get_messages:       ~0.01ms (depends on buffer size)
estimate_tokens:    ~0.1ms
```

### Memory Usage

```
Buffer of 20 messages (10 turns):
- Messages: ~20 KB
- Deque overhead: ~1 KB
- Total: ~21 KB per agent instance
```

## Limitations

1. **No Long-term Memory**: Old context is permanently lost
2. **No Semantic Search**: Cannot retrieve specific past information
3. **Fixed Capacity**: Same size regardless of message importance
4. **No Summarization**: Cannot compress old context
5. **No Persistence**: Memory cleared on restart

**When to Use This Pattern**:
- Short conversations (< 50 turns)
- Stateless applications
- Demos and prototypes
- Cost-sensitive deployments

**When to Use Hierarchical Memory (Problem 2)**:
- Long-running conversations
- Complex agents needing historical context
- Production applications
- Semantic search requirements

## Troubleshooting

### API Key Errors

```bash
ValueError: API key required
```

**Solution**: Set `ANTHROPIC_API_KEY` in `.env` file

### Memory Not Persisting

**Issue**: Context lost between turns

**Solution**: Verify messages are added to buffer:
```python
print(agent.memory.get_messages())
```

### Token Limit Exceeded

```bash
anthropic.BadRequestError: prompt is too long
```

**Solution**: Reduce `max_turns` or shorten messages

## Testing

```bash
# Run agent demo
uv run python agent.py

# Test specific scenarios
uv run python test_agent.py
```

## Next Steps

After understanding this implementation:

1. Study the code in `memory.py` and `agent.py`
2. Run the demo to see memory limits in action
3. Experiment with different `max_turns` values
4. Proceed to **Problem 2** for hierarchical memory

## References

- [Anthropic Claude API Documentation](https://docs.anthropic.com/claude/reference)
- [Python collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Circular Buffer Pattern](https://en.wikipedia.org/wiki/Circular_buffer)
