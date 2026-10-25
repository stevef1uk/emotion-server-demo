# Emotion Detection MCP Server

A modern, high-performance **Model Context Protocol (MCP)** server written in Go (`github.com/mark3labs/mcp-go`), providing AI-powered emotion detection capabilities to MCP-enabled clients (Claude Desktop, Agent Gateway, MCP Inspector, Gradio UI).

## Features

- **Multi-Architecture**: Cross-compiled for both **linux/amd64 (x86_64)** and **linux/arm64 (ARM)**.
- **Dual Transport**: Supports **Streamable-HTTP** (`/mcp`) and **Server-Sent Events** (`/sse` + `/message`) concurrently on the same port, plus standard **stdio** mode.
- **Ultra-Lean Container**: Alpine-based minimal image (~25MB), statically linked, zero Node.js/NPM dependencies.
- **Model Security Compliant**: Interfaces cleanly with the `secure_packager`-protected emotion inference container.
- **Observability**: Built-in `/health` and `/healthz` endpoints, and `config://server` resource.

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `MCP_HOST` | `0.0.0.0` | Bind host address |
| `MCP_PORT` | `9000` | Bind port number |
| `MCP_TRANSPORT` | `dual` | `dual` (Streamable-HTTP + SSE), `stdio`, `streamable-http`, or `sse` |
| `EMOTION_SERVICE_URL` | `http://emotion-api:8000/predict` | Backend endpoint for emotion inference |
| `EMOTION_DETAILED_URL`| (derived) | Backend endpoint for detailed probabilities (`/predict_detailed`) |

## Available MCP Tools

### 1. `emotion_detection`
- **Description**: Analyze text to detect primary emotion using the fine-tuned Gemma model.
- **Input**:
  - `text` (string, required): Sentence or paragraph to analyze.
  - `accurate` (boolean, optional, default: `true`): Use high-accuracy inference sampling.
- **Output**: `"Emotion: happiness (Confidence: 98.50%)"`

### 2. `emotion_detection_detailed`
- **Description**: Detailed emotion analysis returning probabilities across all 14 emotion categories.
- **Input**:
  - `text` (string, required): Text to analyze.
- **Output**: JSON string containing `predicted_emotion`, `confidence`, and `all_emotions` distribution.

## Available Resources
- `config://server`: Current server metadata, version, runtime OS/architecture, and active backend URL.

## Available Prompts
- `analyze_emotion`: Pre-structured prompt for empathetic customer service responses based on emotion detection.

## Building Multi-Arch Images

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <registry>/emotion-mcp:latest \
  --push .
```
