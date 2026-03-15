# Known Issues

## Mem0 Validation Errors (Non-Fatal)

### Issue Description

When running the agent, you may see Pydantic validation errors in the logs:

```
ERROR,Error awaiting memory task (async): 6 validation errors for PointStruct
vector.list[float]
  Input should be a valid list [type=list_type, input_value=None, input_type=NoneType]
```

### Root Cause

**Confirmed bug in Mem0 1.x** (works in 0.1.116, broken in 1.0.0+):

When Mem0 determines that a memory doesn't need updating (`event='NONE'`), it attempts to update only the metadata by calling:
```python
self.vector_store.update(
    vector_id=memory_id,
    vector=None,  # Keep same embeddings
    payload=updated_metadata
)
```

However, Qdrant's `PointStruct` validation requires `vector` to be `List[float]`, not `None`, causing the validation error.

**Scenario**: This occurs when:
1. Adding duplicate memory content with different session IDs (agent_id, run_id)
2. Mem0 detects no content change (`event='NONE'`)
3. Mem0 tries to update metadata while preserving the existing vector
4. Passes `vector=None` which fails Pydantic validation

### Impact

**None - The errors are non-fatal and do not affect functionality:**

- ✅ Memories are successfully stored
- ✅ Search works correctly
- ✅ All operations complete successfully
- ✅ Agent continues working normally

Mem0 handles these errors internally, likely through retry logic or by filtering out failed embeddings.

### Verification

You can verify memories are working despite the errors:

```bash
uv run python -c "
import asyncio
from memory_manager import MemoryManager
import os

async def test():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    mm = MemoryManager(model='claude-haiku-4-5-20251001', api_key=api_key)

    # Add and search
    await mm.insert(user_id='test', content='Test memory')
    results = await mm.search(user_id='test', query='test')
    print(f'Memories stored and retrieved: {len(results)} found')

asyncio.run(test())
"
```

### Status

- **Version**: Mem0 1.0.5 (latest as of 2024-03-15)
- **Severity**: Low (cosmetic error messages only)
- **GitHub Issues**:
  - [#3640](https://github.com/mem0ai/mem0/issues/3640) - Original report
  - [#3780](https://github.com/mem0ai/mem0/issues/3780) - Duplicate with more details
- **Fix PR**: [#3653](https://github.com/mem0ai/mem0/pull/3653) - Open, not yet merged
- **Workaround**: Suppress Mem0 error logs (see below)

### Additional Context

The errors typically appear during:
1. Initial memory insertion when multiple memories are extracted from a conversation
2. Parallel embedding generation
3. First-time HuggingFace model loading

The embedder (sentence-transformers/all-MiniLM-L6-v2) loads successfully and generates embeddings despite the errors.

### Workaround: Suppress Error Logs

To suppress these non-fatal error messages, add this to your code before initializing MemoryManager:

```python
import logging

# Suppress Mem0 internal error logs (PointStruct validation errors are non-fatal)
logging.getLogger("mem0").setLevel(logging.CRITICAL)
logging.getLogger("mem0.memory").setLevel(logging.CRITICAL)
logging.getLogger("mem0.memory.main").setLevel(logging.CRITICAL)
```

This is **recommended by Mem0 community members** in issue [#3780](https://github.com/mem0ai/mem0/issues/3780#issuecomment-2507764445).

### Recommendations

1. **Suppress the logs** using the code above - errors are meaningless and non-fatal
2. **Monitor Mem0 releases** - PR #3653 will fix this when merged
3. **Focus on functional tests** - verify memories are stored and retrieved correctly
4. **Don't downgrade** - Mem0 1.x has important features (async-by-default, rerankers)

### Related Issues

- Mem0 GitHub: Check for similar issues with async embedding generation
- Related to parallel memory insertion in Mem0's internal architecture
