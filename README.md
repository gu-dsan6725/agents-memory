# Agent Memory Patterns: Course Labs

This repository contains two hands-on lab assignments that teach fundamental and advanced memory management patterns for AI agents, from basic conversation history to sophisticated memory systems with summarization and semantic search.

## Course Structure

### Problem 1: Simple Memory Agent (50 points)

**Directory**: [simple-memory-agent/](simple-memory-agent/) | **Exercise**: [EXERCISE.md](simple-memory-agent/EXERCISE.md)

Build a conversational agent with basic memory management using a circular buffer pattern. This lab demonstrates how to maintain conversation context across multiple turns, implement memory constraints with sliding windows, and manage token budgets effectively. You'll implement a simple in-memory circular buffer that stores recent conversation history, automatically evicts old messages when capacity is reached, and formats conversation history for LLM context. The system uses Amazon Bedrock's Claude for conversation and demonstrates the fundamentals of stateful agent design. This is a solved example that provides the foundation for understanding agent memory patterns.

**Key Learning Objectives**:
- Understanding conversation state management
- Implementing circular buffer data structures
- Managing token budgets and context windows
- Formatting conversation history for LLMs
- Basic memory eviction strategies
- Building stateful conversational agents

### Problem 2: Conversational Memory Agent (100 points)

**Directory**: [conversational-memory-agent/](conversational-memory-agent/) | **Exercise**: [EXERCISE.md](conversational-memory-agent/EXERCISE.md)

Implement an advanced memory system that goes beyond simple conversation history to include memory summarization, semantic search, and multi-tier memory architecture. This lab teaches how to build a hierarchical memory system with short-term (conversation buffer), medium-term (summarized conversations), and long-term (semantic vector store) memory tiers. You'll implement automatic conversation summarization when buffers fill up, use embeddings for semantic similarity search across conversation history, and create memory retrieval strategies that combine recency and relevance. The architecture demonstrates production-ready patterns for agents that need to maintain context over extended interactions while managing token costs effectively.

**Key Learning Objectives**:
- Multi-tier memory architecture design
- Conversation summarization with LLMs
- Semantic memory with embeddings and vector search
- Memory retrieval strategies (recency + relevance)
- Long-term context management
- Token cost optimization with summarization
- When to use different memory patterns

## Prerequisites

- Python 3.11+
- API keys:
  - **Anthropic Claude** (Required): https://console.anthropic.com/
  - Alternative: **AWS Account with Amazon Bedrock access** (Claude models enabled)

## Quick Start

### 1. Install uv (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Install Dependencies

```bash
cd agents-memory
uv sync
```

### 3. Configure API Keys

Each lab has its own `.env.example` file:

```bash
# For Problem 1
cd simple-memory-agent
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY or AWS credentials

# For Problem 2
cd ../conversational-memory-agent
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY or AWS credentials
```

### 4. Work on Labs

**Problem 1 (Solved Example)**:
```bash
cd simple-memory-agent
uv run python agent.py
# Review the implementation and run the example
```

**Problem 2 (Student Exercise)**:
```bash
cd conversational-memory-agent
# Follow instructions in EXERCISE.md
uv run python agent.py
```

## Project Structure

```
agents-memory/
├── README.md                              # This file
├── pyproject.toml                         # Project dependencies
│
├── simple-memory-agent/                   # Problem 1 (50 points) - SOLVED
│   ├── EXERCISE.md                        # Lab walkthrough
│   ├── README.md                          # Technical documentation
│   ├── architecture.md                    # System architecture
│   ├── agent.py                           # Main agent implementation
│   ├── memory.py                          # Circular buffer memory
│   ├── test_agent.py                      # Test examples
│   └── .env.example                       # Environment template
│
└── conversational-memory-agent/           # Problem 2 (100 points)
    ├── EXERCISE.md                        # Lab instructions
    ├── README.md                          # Technical documentation
    ├── architecture.md                    # Implementation guide
    ├── agent.py                           # Main file (TODO: implement)
    ├── memory/
    │   ├── short_term.py                  # Conversation buffer
    │   ├── medium_term.py                 # Summarization layer
    │   └── long_term.py                   # Vector store (TODO)
    └── .env.example                       # Environment template
```

## Grading

### Problem 1: Simple Memory Agent (50 points)

**This is a solved example - no deliverables required**

Students should review and understand:
- How circular buffers work
- Memory eviction strategies
- Conversation context formatting
- Token budget management

### Problem 2: Conversational Memory Agent (100 points)

**Deliverables**:
- [ ] Implemented `long_term.py` with semantic vector store
- [ ] Completed memory retrieval logic in `agent.py`
- [ ] Implemented conversation summarization in `medium_term.py`
- [ ] Test output files demonstrating memory capabilities
- [ ] Code follows project standards (type hints, docstrings, error handling)

**Evaluation Criteria**:
- Vector store implementation (25 points)
- Summarization logic (20 points)
- Memory retrieval strategy (25 points)
- Multi-turn conversation handling (20 points)
- Code quality and standards (10 points)

## Memory Patterns Overview

### Pattern 1: Circular Buffer (Problem 1)
Simple FIFO queue for conversation history with fixed capacity. Best for:
- Short conversations
- Simple chatbots
- Limited context requirements
- Fast, in-memory operations

### Pattern 2: Hierarchical Memory (Problem 2)
Multi-tier memory with summarization and semantic search. Best for:
- Long-running conversations
- Complex agents requiring historical context
- Production applications
- Cost-sensitive deployments

### Pattern Comparison

| Feature | Circular Buffer | Hierarchical Memory |
|---------|----------------|---------------------|
| Complexity | Low | High |
| Token Cost | Low (fixed) | Medium (summarization) |
| Context Retention | Limited | Extensive |
| Semantic Search | No | Yes |
| Implementation Time | Fast | Moderate |
| Best For | Demos, simple bots | Production agents |

## Resources

### Official Documentation
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)

### Learning Resources
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) - Anthropic's guide
- [Memory in LLM Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) - Lilian Weng's blog

## Troubleshooting

### Memory Usage Issues
```bash
# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

### API Key Issues
```bash
# Verify keys are set
echo $ANTHROPIC_API_KEY
# For AWS Bedrock
aws bedrock list-foundation-models --region us-east-1
```

### Vector Store Issues
```python
# Check embedding dimensions
embeddings = model.embed("test")
print(f"Embedding dimensions: {len(embeddings)}")
```

## Submission

Submit to your course platform:
1. Your completed code files for Problem 2
2. Test output files demonstrating memory functionality
3. A brief write-up answering the reflection questions in EXERCISE.md
4. Discussion of trade-offs between memory patterns

## Solutions Branch

Reference implementations are available in the `solutions` branch:
```bash
git checkout solutions
```

**Important**: Problem 1 is already solved in the main branch. Problem 2 solutions are in the solutions branch for reference if you're stuck.

## Next Steps

After completing these labs, explore:
- **agents-observability-and-evals**: Learn to monitor and evaluate agent performance
- **advanced-agentic-patterns**: Multi-agent orchestration and coordination
- Production deployment patterns with memory persistence
- Memory optimization techniques for cost reduction
