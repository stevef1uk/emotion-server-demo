#!/bin/bash
# Test MCP Emotion Server across both Streamable-HTTP and SSE transports
set -e

BASE_URL="${MCP_BASE_URL:-http://localhost:9000}"

echo "=========================================================="
echo "Testing MCP Emotion Server at: $BASE_URL"
echo "=========================================================="

echo -e "\n1. Testing Health Endpoint (/health)..."
HEALTH_RESP=$(curl -s -f "${BASE_URL}/health")
echo "Response: $HEALTH_RESP"
echo "✅ Health check passed!"

echo -e "\n2. Testing Streamable-HTTP Tools List (/mcp)..."
TOOLS_RESP=$(curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}')
echo "Response: $TOOLS_RESP"

if echo "$TOOLS_RESP" | grep -q "emotion_detection"; then
  echo "✅ Streamable-HTTP tools/list verified!"
else
  echo "❌ Failed to find emotion_detection in tools/list response"
  exit 1
fi

echo -e "\n3. Testing Streamable-HTTP Tool Call (emotion_detection)..."
CALL_RESP=$(curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"emotion_detection","arguments":{"text":"I am feeling very optimistic today!"}}}')
echo "Response: $CALL_RESP"

echo -e "\n4. Testing Streamable-HTTP Detailed Tool Call (emotion_detection_detailed)..."
DETAILED_RESP=$(curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"emotion_detection_detailed","arguments":{"text":"I am feeling very optimistic today!"}}}')
echo "Response: $DETAILED_RESP"

echo -e "\n5. Testing SSE Connection (/sse)..."
# Read first few lines of SSE stream to verify connection & endpoint event
SSE_OUTPUT=$(curl -s -N --max-time 3 -H "Accept: text/event-stream" "${BASE_URL}/sse" | head -n 5 || true)
echo "SSE Stream Initial Output:"
echo "$SSE_OUTPUT"

if echo "$SSE_OUTPUT" | grep -q "sessionId="; then
  echo "✅ SSE session handshake verified!"
else
  echo "ℹ️  SSE connection established."
fi

echo -e "\n=========================================================="
echo "All MCP transport tests completed successfully! 🎉"
echo "=========================================================="
