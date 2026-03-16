# Agent Memory Patterns

This repository contains a hands-on lab that teaches production-ready memory management for AI agents using modern open-source tools. Learn how to build agents with semantic memory capabilities using Mem0, Strands SDK, and Groq.

## Overview

Modern AI agents need memory to maintain context across conversations and provide personalized experiences. This lab teaches you how to use production-ready memory frameworks rather than building from scratch, focusing on understanding different memory approaches and when to use them.

**What You'll Learn**:
- Semantic memory with Mem0
- Tool-based agent patterns with Strands SDK
- Automatic vs explicit memory storage
- When to use different memory solutions (Mem0, langmem, AWS Bedrock)
- Production-ready memory architectures

**Time**: 2-3 hours | **Points**: 100 | **Difficulty**: Intermediate

## Memory Solutions Landscape

When building AI agents, you have multiple options for memory management:

### 1. Open Source Solutions

**Mem0** (Used in this lab)
- Easy to use, production-ready
- Local or cloud deployment
- Multiple vector store backends
- Semantic search built-in
- **Best for**: Most use cases, learning, production

**langmem**
- Pure open source
- Self-hosted, full control
- Requires infrastructure setup
- **Best for**: Custom requirements, full control needed

### 2. Cloud Provider Solutions

**AWS Bedrock AgentCore Memory**
- Fully managed by AWS
- Enterprise features
- Integration with AWS services
- **Best for**: Enterprise, existing AWS infrastructure

### Why This Lab Uses Mem0

This lab uses Mem0 because it:
- Works entirely locally (no cloud account needed)
- Provides production-ready patterns
- Is free to use
- Offers multiple backend options
- Has excellent documentation
- Bridges learning and production deployment

## Lab Structure

### Simple Memory Agent (100 points)

**Directory**: [simple-memory-agent/](simple-memory-agent/) | **Exercise**: [EXERCISE.md](simple-memory-agent/EXERCISE.md)

Build a memory-enabled agent using Mem0, Strands SDK, and Groq. This lab demonstrates production-ready memory patterns with automatic conversation storage and semantic search capabilities.

**Architecture**:
```
User Input → Mem0 (automatic storage) → Agent (Strands SDK)
                                          ├── Tool: search_memory()
                                          └── Tool: insert_memory()
Agent Response → Mem0 (automatic storage) → User
```

**Key Learning Objectives**:
- Using Mem0 for semantic memory management
- Building tool-based agents with Strands SDK
- Understanding automatic vs explicit memory storage
- Implementing memory search with semantic similarity
- Designing agents that decide when to recall information
- Production-ready memory architectures

**Technologies**:
- **Mem0**: Semantic memory framework
- **Strands SDK**: Agent orchestration with tool support
- **Groq**: Free, fast LLM inference (no credit card required)
- **Qdrant**: Local vector database
- **HuggingFace**: Free embeddings (MiniLM)

### Optional: Conversational Memory Agent

**Directory**: [conversational-memory-agent/](conversational-memory-agent/)

This directory contains legacy code demonstrating manual memory implementation patterns. It's optional and provided for educational comparison. The main lab focuses on using production tools (Mem0) rather than building memory systems from scratch.

## Prerequisites

- Python 3.11+
- Groq API key (free, no credit card): https://console.groq.com/

That's it! No cloud accounts or paid services required.

## Quick Start

### 1. Install uv (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Get Free Groq API Key

1. Visit https://console.groq.com/
2. Sign up (no credit card needed)
3. Create API key
4. Copy key for next step

### 3. Install Dependencies

```bash
cd agents-memory
uv sync
```

### 4. Configure API Key

```bash
cd simple-memory-agent
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 5. Run the Demo

```bash
uv run python agent.py
```

You should see the agent demonstrate memory capabilities:
- Remembering your name across turns
- Searching memory for past context
- Explicitly storing important information

### 6. Complete the Lab

Follow the instructions in [simple-memory-agent/EXERCISE.md](simple-memory-agent/EXERCISE.md) to:
1. Understand the architecture
2. Extend the agent with new capabilities
3. Test memory behavior across scenarios
4. Write a brief reflection on memory patterns

## Project Structure

```
agents-memory/
├── README.md                              # This file
├── pyproject.toml                         # Project dependencies
├── MEMORY_OPTIONS.md                      # Comparison of memory solutions
│
├── simple-memory-agent/                   # Main lab (100 points)
│   ├── EXERCISE.md                        # Lab instructions
│   ├── README.md                          # Technical documentation
│   ├── agent.py                           # Memory-enabled agent
│   └── .env.example                       # Environment template
│
└── conversational-memory-agent/           # Optional: Legacy reference
    └── (manual memory implementation)
```

## Key Concepts

### Automatic vs Explicit Memory

**Automatic Storage**: Every conversation turn is stored in Mem0
- User messages stored automatically
- Agent responses stored automatically
- Background process, transparent to user
- Always available for semantic search

**Explicit Storage**: Agent deliberately stores information
- When user says "remember this"
- When agent identifies key facts or preferences
- Uses `insert_memory` tool
- Can include metadata and tags

### Semantic Search

Mem0 uses embeddings to find relevant memories by meaning, not just keywords:

```
User: "What's my job?"
↓
Query embedding: [0.2, -0.1, 0.5, ...]
↓
Compare to all memory embeddings
↓
Top match: "Alice is a software engineer" (similarity: 0.89)
```

This enables natural, intelligent memory recall.

### When to Search Memory

The agent decides when to search based on:
- User asks about past conversations
- Question could benefit from historical context
- Proactive recall could improve response quality

This decision-making is key to intelligent memory systems.

## Grading

### Simple Memory Agent (100 points)

**Deliverables**:
- [ ] Completed code with new capability (40 points)
- [ ] Test output files demonstrating memory behavior (40 points)
- [ ] Brief report on memory patterns (20 points)

**Evaluation Criteria**:
- New capability implementation and design
- Test coverage of memory scenarios
- Understanding of memory patterns and trade-offs
- Code quality and documentation

See [simple-memory-agent/EXERCISE.md](simple-memory-agent/EXERCISE.md) for detailed requirements.

## Memory Pattern Comparison

| Feature | Manual (Circular Buffer) | Mem0 | langmem | AWS Bedrock |
|---------|-------------------------|------|---------|-------------|
| Setup Complexity | Low | Low | Medium | High |
| Cost | Free | Free/Paid | Free | Paid |
| Semantic Search | No | Yes | Yes | Yes |
| Production Ready | No | Yes | Yes | Yes |
| Learning Curve | Easy | Easy | Medium | Medium |
| Best For | Learning, demos | Most cases | Custom needs | Enterprise |

## Troubleshooting

### Groq API Key Issues

```bash
ValueError: API key required
```

**Solution**: Set `GROQ_API_KEY` in `.env` file

### Mem0 Installation Issues

```bash
uv pip install mem0ai
```

### Qdrant Connection Errors

Delete `./memory_db` directory and restart:
```bash
rm -rf simple-memory-agent/memory_db
uv run python simple-memory-agent/agent.py
```

### Embedding Model Download

First run downloads MiniLM model (approximately 100MB). This is normal and only happens once.

### Memory Not Persisting

Check that `./memory_db` directory exists and has write permissions:
```bash
ls -la simple-memory-agent/memory_db
```

## Resources

### Documentation
- [Mem0 Documentation](https://docs.mem0.ai/)
- [Strands SDK Documentation](https://github.com/awslabs/strands)
- [Groq Documentation](https://console.groq.com/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

### Learning Resources
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) - Anthropic's guide
- [Memory in LLM Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) - Lilian Weng's blog
- [Sentence Transformers](https://www.sbert.net/) - Embedding models

## Next Steps

After completing this lab:
- Explore advanced memory patterns (summarization, consolidation)
- Try different vector databases (ChromaDB, Pinecone)
- Build multi-agent systems with shared memory
- Study AWS Bedrock AgentCore memory for enterprise use cases
- Implement memory in your own production agents

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review [MEMORY_OPTIONS.md](MEMORY_OPTIONS.md) for architecture guidance
3. Consult the [simple-memory-agent/README.md](simple-memory-agent/README.md) technical docs
4. Check Mem0 and Strands SDK documentation

## License

This educational material is provided for learning purposes. See individual dependencies for their licenses.
