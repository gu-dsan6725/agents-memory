# Simple Memory Agent - Lab Exercises

## Overview

This lab contains exercises to help you understand multi-tenant memory systems and implement production-ready web APIs with memory. You will first run and understand the demo agent, then convert it into a FastAPI application with user isolation and multi-session tracking.

## Reference Implementation

Before starting Problem 2, review the streaming stock agent example from the Advanced Agentic Patterns course:
- **Location**: `~/repos/advanced-agentic-patterns/streaming-stock-agent/`
- **Key concepts**: FastAPI setup, Server-Sent Events (SSE) streaming, Pydantic models, endpoint design

---

## Problem 1: Understanding the Memory Agent (10 Points)

### Objective

Run the demo agent to understand how semantic memory works across a conversation. The agent demonstrates different types of memory (factual, semantic, preference, episodic) within a single conversation session.

### What is agent.py?

The `agent.py` file contains a **pre-programmed demonstration** with a canned conversation between a user (Alice) and the agent. This is **not** an interactive chat - it's a scripted demo designed to showcase different memory capabilities:

1. **Turn 1-2**: Alice introduces herself and shares project information (factual + semantic memory)
2. **Turn 3**: Tests memory recall - agent retrieves name and occupation
3. **Turn 4**: Explicit memory insertion - Alice states preferences
4. **Turn 5**: Tests preference retrieval - agent recalls coding preferences
5. **Turn 6**: New topic (neural networks) - no memory search needed
6. **Turn 7**: Tests episodic recall - agent remembers the ML project

**All of this happens in ONE session** (you'll see a session ID like `75c52f1d` in the logs), demonstrating how the memory system:
- Automatically stores conversations in the background
- Semantically searches when needed
- Explicitly stores important information via tool calls
- Recalls context across multiple conversation turns

### Requirements

#### 1. Run the Agent Demo

Execute the agent and capture its output to a log file:

```bash
uv run python agent.py 2>&1 | tee agent_output.log
```

**What this does:**
- `uv run python agent.py` - Runs the demo agent
- `2>&1` - Redirects both stdout and stderr to capture all output
- `| tee agent_output.log` - Displays output on screen AND saves to file

The demo takes about 30-60 seconds to complete.

#### 2. Review the Output

Open `agent_output.log` and look for:

**Session Information:**
```
Initializing Agent - user: demo_user, agent: memory-agent, session: 75c52f1d
```
- **user_id**: `demo_user` - The user identifier
- **agent_id**: `memory-agent` - The agent identifier
- **session/run_id**: `75c52f1d` - Unique session ID for this conversation

**Turn-by-Turn Conversations:**
Each turn shows:
- User input
- Agent response
- Tool calls (when agent uses memory tools)

**Tool Usage Examples:**
```
Tool #1: insert_memory
Tool #2: insert_memory
Tool #3: insert_memory
```

When you see these, the agent is explicitly storing information.

**Memory Statistics (at end):**
```
Memory Statistics:
  Total memories stored: 17

Sample memories:
  - Name is Alice
  - Familiar with scikit-learn, TensorFlow, Keras, and PyTorch libraries
  - Can help debug machine learning code issues
```

#### 3. Understand Different Memory Types

In the output, identify examples of each memory type:

**Factual Memory** (Turn 1):
- "Name is Alice"
- "Is a software engineer"
- "Specializes in Python"

**Semantic Memory** (Turn 2):
- "Working on a machine learning project"
- "Uses scikit-learn for the project"
- "Familiar with scikit-learn, TensorFlow, Keras, PyTorch"

**Preference Memory** (Turn 4-5):
- "Favorite programming language is Python"
- "Prefers clean, maintainable code"

**Episodic Memory** (Turn 7):
- Remembers the specific ML project mentioned earlier
- Recalls the conversation context

**Key Observations:**
1. All memories are isolated by `user_id="demo_user"`
2. All memories are tagged with `session=75c52f1d`
3. Agent automatically decides when to search memory (Turns 3, 5, 7)
4. Agent uses `insert_memory` tool for explicit storage (Turns 1, 2, 4)
5. Background storage happens after each turn

#### 4. Commit the Log File

This proves you ran the code successfully:

```bash
git add agent_output.log
git commit -m "Add agent demo output log"
```

### Deliverables (10 Points)

1. **agent_output.log** (5 points) - Committed to git showing successful execution
2. **Understanding document** (5 points) - Brief write-up (can be added to README or separate file) explaining:
   - What the 7 turns demonstrate
   - Examples of each memory type you found in the output
   - How session IDs are used
   - When the agent searches memory vs. when it inserts

### Evaluation Criteria

- **Execution** (5 pts): `agent_output.log` shows complete demo run with all 7 turns
- **Understanding** (5 pts): Document shows clear comprehension of:
  - Different memory types
  - Tool usage patterns
  - Session tracking
  - Automatic vs. explicit memory storage

---

## Problem 2: FastAPI Agent Application

### Objective

