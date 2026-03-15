#!/bin/bash

# Carol Session 1 - Demonstrate user isolation
echo "=== Carol Session 1 ===" > carol_output.txt
echo "" >> carol_output.txt

# Turn 1
echo "User: Hi, I'm Carol. I'm a data scientist." >> carol_output.txt
response=$(curl -s -X POST http://127.0.0.1:9090/invocation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "carol",
    "run_id": "carol-session-1",
    "query": "Hi, I'\''m Carol. I'\''m a data scientist."
  }' | jq -r '.response')
echo "Agent: $response" >> carol_output.txt
echo "" >> carol_output.txt

# Turn 2 - Ask about programming languages (should NOT know Alice's Python preference)
echo "User: What programming languages do I like?" >> carol_output.txt
response=$(curl -s -X POST http://127.0.0.1:9090/invocation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "carol",
    "run_id": "carol-session-1",
    "query": "What programming languages do I like?"
  }' | jq -r '.response')
echo "Agent: $response" >> carol_output.txt
echo "" >> carol_output.txt

# Turn 3 - Try to access Alice's information (should fail)
echo "User: Do you know what Alice prefers?" >> carol_output.txt
response=$(curl -s -X POST http://127.0.0.1:9090/invocation \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "carol",
    "run_id": "carol-session-1",
    "query": "Do you know what Alice prefers?"
  }' | jq -r '.response')
echo "Agent: $response" >> carol_output.txt
echo "" >> carol_output.txt
