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

#### 2. Analyze Output and Write Explanation

**⚠️ ACADEMIC INTEGRITY REQUIREMENT:**

You MUST write your explanation document **yourself** - do NOT use ChatGPT, Claude, or any other AI tool to generate this document. This is an analysis exercise to ensure you understand the system. AI-generated submissions will receive a zero.

**Task:** Create a file named `agent_output_explanation.md` analyzing your `agent_output.log`.

**What to include in your explanation:**

1. **Session Information** - Identify and explain the user_id, agent_id, and run_id
2. **Memory Types** - Find and categorize examples of:
   - Factual memory (personal facts: name, occupation, etc.)
   - Semantic memory (knowledge/concepts learned)
   - Preference memory (likes/dislikes, coding preferences)
   - Episodic memory (specific events/projects recalled)
3. **Tool Usage Patterns** - When does the agent use `insert_memory` tool vs. automatic background storage?
4. **Memory Recall** - Which turns trigger memory search? How do you know?
5. **Single Session** - Explain how all 7 turns happen in ONE session and why that matters

**What we're looking for:**
- Evidence you READ the log file (specific line numbers, quotes from output)
- YOUR understanding in YOUR words (not AI-generated prose)
- Specific examples from the output supporting your analysis
- Clear explanations of when/why memory operations occur
- Understanding of single-session vs. multi-session concepts

**Format:** Use markdown with clear headers. Length: 1-2 pages. Be specific and cite examples from your log.

**Hints:**
- Look for patterns in which turns show "Tool #X: insert_memory"
- Compare turns 3, 5, 7 - what do they have in common?
- Check the "Memory Statistics" section at the end
- Notice when the agent's response changes based on previous turns
- Trace a single piece of information (like "Alice") through multiple turns

#### 3. Commit Your Work

Commit both files to prove you completed the exercise:

```bash
git add agent_output.log agent_output_explanation.md
git commit -m "Problem 1: Memory agent demo and analysis"
```

### Deliverables (10 Points)

**Required files (both must be committed to git):**

1. **agent_output.log** (3 points)
   - Shows successful execution of demo
   - Contains all 7 conversation turns
   - Includes memory statistics at end

2. **agent_output_explanation.md** (7 points)
   - Written by YOU (not AI-generated) ⚠️
   - Analyzes the log file with specific examples
   - Identifies all 4 memory types with quotes from output
   - Explains tool usage patterns
   - Demonstrates understanding of single-session behavior

### Evaluation Criteria

**Execution (3 points):**
- ✅ `agent_output.log` exists and shows complete demo (all 7 turns)
- ✅ Log shows initialization with user_id, agent_id, session_id
- ✅ Log includes memory statistics

**Analysis (7 points):**
- **Thoroughness** (3 pts): Covers all required topics (session info, memory types, tool usage, recall patterns, single-session concept)
- **Specificity** (2 pts): Cites specific examples/quotes from output, includes line numbers or turn numbers
- **Understanding** (2 pts): Explanations show genuine comprehension, written in student's own words (not AI-generated)

**Academic Integrity:**
- AI-generated submissions = **0 points** for analysis portion
- We can detect AI writing patterns - don't risk it
- This is about YOUR learning and understanding

---

## Problem 2: FastAPI Agent Application

### Objective

