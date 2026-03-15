# Problem 2: Conversational Memory Agent - Exercise

## Overview

Implement an advanced hierarchical memory system that maintains conversation context across extended interactions using summarization and semantic search.

**Time to Complete**: 3-4 hours
**Points**: 100

## Learning Objectives

By completing this exercise, you will:

1. Implement a multi-tier memory architecture
2. Use LLMs for conversation summarization
3. Build semantic memory with embeddings and vector search
4. Create intelligent memory retrieval strategies
5. Manage long-term context efficiently
6. Optimize token costs through summarization

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Hierarchical Memory System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SHORT-TERM MEMORY (Circular Buffer)                    │   │
│  │  ┌────┬────┬────┬────┬────┬────┬────┬────┐            │   │
│  │  │ M1 │ M2 │ M3 │ M4 │ M5 │ M6 │ M7 │ M8 │            │   │
│  │  └────┴────┴────┴────┴────┴────┴────┴────┘            │   │
│  │  Recent 10 turns - fast access                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓ (when full)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MEDIUM-TERM MEMORY (Summaries)                         │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Summary 1: Turns 1-10                           │  │   │
│  │  │  "User discussed X, agent provided Y..."         │  │   │
│  │  ├──────────────────────────────────────────────────┤  │   │
│  │  │  Summary 2: Turns 11-20                          │  │   │
│  │  │  "Conversation shifted to Z..."                  │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │  Compressed context - moderate access                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓ (indexed)                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  LONG-TERM MEMORY (Semantic Vector Store)              │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Embedding: [0.2, -0.1, 0.5, ...]  → Summary 1  │  │   │
│  │  │  Embedding: [-0.3, 0.4, 0.1, ...]  → Summary 2  │  │   │
│  │  │  Embedding: [0.1, 0.2, -0.3, ...]  → Summary 3  │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │  Semantic search - selective retrieval                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  MEMORY RETRIEVAL STRATEGY                              │   │
│  │  1. Always include short-term (recent context)          │   │
│  │  2. Search long-term for relevant summaries             │   │
│  │  3. Combine for LLM context                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Tasks

### Task 1: Implement Long-Term Memory (25 points)

**File**: `memory/long_term.py`

Implement a semantic vector store for conversation summaries:

```python
class SemanticMemory:
    """Long-term memory with semantic search capabilities."""

    def __init__(self):
        # TODO: Initialize storage for embeddings and summaries
        pass

    def add_summary(
        self,
        summary: str,
        turn_range: tuple[int, int]
    ) -> None:
        """Store a summary with its embedding.

        Args:
            summary: Compressed conversation summary
            turn_range: (start_turn, end_turn) for this summary
        """
        # TODO: Generate embedding for summary
        # TODO: Store summary with embedding and metadata
        pass

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for relevant summaries.

        Args:
            query: Search query (usually current user message)
            top_k: Number of most relevant summaries to return

        Returns:
            List of relevant summaries with metadata
        """
        # TODO: Generate query embedding
        # TODO: Compute cosine similarity with stored embeddings
        # TODO: Return top-k most similar summaries
        pass
```

**Requirements**:
- Use scikit-learn's `cosine_similarity` for vector comparison
- Store embeddings as numpy arrays
- Include metadata: turn range, timestamp, summary text
- Handle empty memory case

**Hints**:
- For embeddings, you can use a simple bag-of-words with TF-IDF
- Or use Claude to generate embeddings (see below)
- Cosine similarity formula: `dot(A, B) / (norm(A) * norm(B))`

**Claude Embeddings Example**:
```python
# Simple approach: use Claude to generate embeddings
# (In production, use dedicated embedding models)
def generate_embedding(text: str) -> List[float]:
    # Placeholder: use TF-IDF or simple word vectors
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text])
    return vectors.toarray()[0].tolist()
```

### Task 2: Implement Conversation Summarization (20 points)

**File**: `memory/medium_term.py`

Implement automatic summarization when short-term memory fills:

```python
class SummaryMemory:
    """Medium-term memory with conversation summarization."""

    def __init__(
        self,
        api_client,
        model: str = "claude-3-5-haiku-20241022"
    ):
        # TODO: Initialize with API client and model
        pass

    def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        turn_range: tuple[int, int]
    ) -> str:
        """Generate a concise summary of conversation turns.

        Args:
            messages: List of conversation messages
            turn_range: (start, end) turn numbers

        Returns:
            Compressed summary of the conversation
        """
        # TODO: Format messages for summarization
        # TODO: Create summarization prompt
        # TODO: Call Claude to generate summary
        # TODO: Return summary text
        pass
```

**Summarization Prompt Template**:
```python
SUMMARY_PROMPT = """Summarize the following conversation segment concisely.
Focus on:
- Key information exchanged
- User requests and agent responses
- Important facts or preferences mentioned
- Action items or decisions made

Conversation:
{conversation}

Provide a concise summary (2-3 sentences):"""
```

**Requirements**:
- Keep summaries under 200 tokens
- Preserve critical information (user name, preferences, etc.)
- Use efficient model (Haiku) for cost optimization
- Handle API errors gracefully

### Task 3: Implement Memory Retrieval Strategy (25 points)

**File**: `agent.py`

Implement intelligent memory retrieval that combines recent and relevant context:

```python
def _retrieve_context(
    self,
    current_message: str
) -> List[Dict[str, str]]:
    """Retrieve relevant context for current message.

    Strategy:
    1. Always include short-term memory (recent turns)
    2. Search long-term for semantically relevant summaries
    3. Combine and format for LLM

    Args:
        current_message: Current user message

    Returns:
        List of messages including context
    """
    # TODO: Get all messages from short-term memory

    # TODO: Search long-term memory for relevant summaries

    # TODO: Format summaries as context messages

    # TODO: Combine: [summaries] + [recent messages]

    # TODO: Return formatted context
    pass
```

**Requirements**:
- Always include all short-term messages
- Retrieve top-3 most relevant summaries from long-term
- Format summaries as system messages
- Total context should fit in token budget

**Context Format Example**:
```python
context = [
    {
        "role": "system",
        "content": "Previous conversation summary: [summary text]"
    },
    {
        "role": "user",
        "content": "Earlier message..."
    },
    {
        "role": "assistant",
        "content": "Earlier response..."
    },
    # ... recent messages
]
```

### Task 4: Implement Memory Lifecycle (20 points)

**File**: `agent.py`

Handle the full memory lifecycle:

```python
def chat(
    self,
    user_input: str
) -> str:
    """Process user input with hierarchical memory management."""

    # TODO: Add user message to short-term memory

    # TODO: Check if short-term memory is full
    # If full:
    #   - Get messages from short-term
    #   - Generate summary with medium-term
    #   - Add summary to long-term with embedding
    #   - Clear short-term memory

    # TODO: Retrieve context (short-term + relevant long-term)

    # TODO: Call Claude with context

    # TODO: Add response to short-term memory

    # TODO: Return response
```

**Requirements**:
- Trigger summarization when short-term is full
- Store summaries before clearing short-term
- Maintain turn counters across memory tiers
- Log memory operations for debugging

### Task 5: Testing and Validation (10 points)

Create test scenarios demonstrating memory capabilities:

```python
def test_long_conversation():
    """Test memory across 50+ turns."""
    agent = ConversationalMemoryAgent(short_term_turns=5)

    # Turn 1-5: Introduce user info
    agent.chat("My name is Bob")
    agent.chat("I work as a teacher")
    agent.chat("I love hiking and photography")

    # Turn 6-30: Different topics (triggers summarization)
    for i in range(25):
        agent.chat(f"Tell me about topic {i}")

    # Turn 31: Recall early information
    response = agent.chat("What do you know about me?")

    # Agent should retrieve "Bob, teacher, hiking, photography"
    # from long-term memory even though short-term was cleared
    assert "Bob" in response or "teacher" in response
```

**Test Cases**:
1. Short conversation (< 10 turns) - no summarization
2. Medium conversation (20 turns) - one summarization
3. Long conversation (50+ turns) - multiple summaries
4. Semantic recall - retrieve old relevant context
5. Memory persistence - information not lost

## Starter Code

The starter code provides:

1. **`memory/short_term.py`**: Circular buffer (from Problem 1)
2. **`memory/medium_term.py`**: Skeleton for summarization
3. **`memory/long_term.py`**: Skeleton for vector store
4. **`agent.py`**: Main agent skeleton with TODOs

## Deliverables

Submit these files:

1. **`memory/long_term.py`**: Completed semantic memory implementation
2. **`memory/medium_term.py`**: Completed summarization logic
3. **`agent.py`**: Completed agent with memory lifecycle
4. **Test outputs**:
   - `test_short.txt`: Conversation under 10 turns
   - `test_medium.txt`: Conversation with 20 turns
   - `test_long.txt`: Conversation with 50+ turns showing recall

5. **Brief report** (`REPORT.md`):
   - Explain your retrieval strategy
   - Discuss trade-offs in your design
   - Performance observations (token usage, response time)

## Grading Rubric

| Component | Points | Criteria |
|-----------|--------|----------|
| Long-term memory | 25 | Vector store, search, embeddings |
| Summarization | 20 | Prompt design, API integration |
| Retrieval strategy | 25 | Context selection, relevance |
| Memory lifecycle | 20 | Summarization trigger, cleanup |
| Code quality | 10 | Type hints, docs, error handling |

## Tips

### Embedding Approaches

**Option 1: TF-IDF (Simple)**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(max_features=100)
embeddings = vectorizer.fit_transform(summaries).toarray()
```

**Option 2: Sentence Transformers (Advanced)**
```python
# Not required, but if you want to use it:
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(summaries)
```

### Token Budget Management

```python
# Estimate tokens
def estimate_tokens(text: str) -> int:
    return len(text) // 4

# Target: Keep total context under 4000 tokens
short_term_tokens = sum(estimate_tokens(msg["content"]) for msg in messages)
summary_tokens = sum(estimate_tokens(s["summary"]) for s in summaries)
total_tokens = short_term_tokens + summary_tokens

print(f"Context tokens: {total_tokens}")
```

### Debugging Memory

```python
# Add logging to track memory operations
logger.info(f"Short-term: {agent.short_term.get_turn_count()} turns")
logger.info(f"Summaries: {len(agent.long_term.summaries)}")
logger.info(f"Retrieved {len(relevant_summaries)} relevant summaries")
```

## Common Pitfalls

1. **Not clearing short-term after summarization**
   - Result: Memory grows indefinitely

2. **Poor summarization prompts**
   - Result: Summaries lose critical information

3. **Inefficient retrieval**
   - Result: High token costs or missing relevant context

4. **Not handling edge cases**
   - Empty memory, no relevant summaries, API errors

## Extension Ideas (Optional)

After completing the core requirements:

1. **Importance scoring**: Weight summaries by importance
2. **Memory consolidation**: Merge similar summaries
3. **Persistent storage**: Save memory to disk
4. **User preferences**: Separate storage for user facts
5. **Memory decay**: Reduce relevance of old memories over time

## Resources

- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [Scikit-learn Cosine Similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)
- [TF-IDF Vectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

## Questions?

Review Problem 1's circular buffer implementation for inspiration. The hierarchical memory builds on those concepts but adds summarization and semantic search layers.

Good luck!
