# Kubernetes / k3s Deployment Guide for Emotion MCP Server

This directory provides Kubernetes manifests for deploying the MCP Emotion Server on **k3s** or any standard Kubernetes cluster.

## Architecture Patterns

### 1. Unified Sidecar Pod (`k8s/emotion-mcp-sidecar.yaml`) — Recommended
In this pattern, both the protected model inference engine (`emotion-api`) and the lightweight Go MCP server (`emotion-mcp`) run inside the **same Pod**:
- **Preserves Model Security**: The model weights remain protected by `secure_packager` inside their container.
- **Fast Local Communication**: The MCP server forwards inference requests to `http://127.0.0.1:8000` via loopback, eliminating network latency.
- **Atomic Deployment**: Both components scale and deploy together as a single Kubernetes workload.

To apply:
```bash
kubectl apply -f k8s/emotion-mcp-sidecar.yaml
```

### 2. Standalone MCP Server (`k8s/emotion-mcp-standalone.yaml`)
In this pattern, `emotion-mcp` runs as an independent deployment and connects to an existing `emotion-api` service (or a cloud endpoint such as Modal) via `EMOTION_SERVICE_URL`.

To apply:
```bash
kubectl apply -f k8s/emotion-mcp-standalone.yaml
```

---

## Building Multi-Architecture Container Images (x86_64 and ARM64)

To build the `emotion-mcp` image for multi-arch deployment without compiling on the k3s host:

```bash
# Ensure buildx instance is active
docker buildx create --use --name multiarch-builder || docker buildx use multiarch-builder

# Build and push both amd64 and arm64 in a single manifest
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <your-registry>/emotion-mcp:latest \
  -f src/mcp-go-server/Dockerfile \
  --push \
  src/mcp-go-server
```

---

## Verifying Deployment

Once deployed, port-forward the MCP service to test locally:

```bash
kubectl port-forward svc/emotion-mcp 9000:9000
```

### Health Check
```bash
curl -s http://localhost:9000/health
```

### Streamable-HTTP Test (Claude Desktop / Agent Gateway / MCP Inspector)
```bash
curl -s -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"emotion_detection","arguments":{"text":"I am really excited about this launch!"}}}'
```

### SSE Test (Gradio UI)
Connect to `http://localhost:9000/sse` using Server-Sent Events.
