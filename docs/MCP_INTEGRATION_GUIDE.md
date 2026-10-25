# MCP Emotion Server: Integration Guide for Projects & Agents

## 1. Overview & Service Identity
The **Emotion Detection MCP Server** is a native Go service (`github.com/mark3labs/mcp-go`) that provides AI-powered emotion classification across **14 distinct categories**:
`anger 😡`, `confusion 😕`, `desire 🧚`, `disgust 🤢`, `fear 😨`, `guilt 😔`, `happiness 😊`, `love ❤️`, `neutral 😐`, `sadness 😢`, `sarcasm 🤨`, `shame 😳`, `surprise 😲`.

It connects to an underlying fine-tuned **Gemma 3** inference engine running on `llama.cpp`.

---

## 2. Network Endpoints & Transports

The server runs on **port 9000** (default) and provides concurrent dual-transport support:

| Endpoint | Protocol / Transport | Primary Consumers |
| :--- | :--- | :--- |
| `POST /mcp` | **Streamable-HTTP** (Stateless JSON-RPC 2.0) | Claude Desktop, Agent Gateway, CrewAI, AutoGen, MCP Inspector |
| `GET /sse` | **Server-Sent Events (SSE)** | Gradio UI (`ui.py`), web clients |
| `POST /message?sessionId=...` | HTTP POST for SSE sessions | Paired with `/sse` handshake |
| `GET /health` & `/healthz` | HTTP Health probes | Kubernetes probes, Docker healthchecks |

---

## 3. Tool Specifications

### Tool 1: `emotion_detection`
- **Purpose**: Fast primary emotion prediction with confidence score.
- **Parameters**:
  - `text` (*string, required*): The sentence, message, or transcript to analyze.
  - `accurate` (*boolean, optional, default: `true`*): Whether to return true probability sampling.
- **Output (TextContent)**:
  ```text
  Emotion: happiness (Confidence: 98.50%)
  ```

### Tool 2: `emotion_detection_detailed`
- **Purpose**: Full spectrum breakdown of all 14 emotion probabilities.
- **Parameters**:
  - `text` (*string, required*): Text to analyze.
- **Output (JSON in TextContent)**:
  ```json
  {
    "predicted_emotion": "neutral",
    "confidence": 0.752,
    "all_emotions": {
      "anger": 0.004,
      "confusion": 0.149,
      "desire": 0.000,
      "disgust": 0.059,
      "fear": 0.000,
      "guilt": 0.001,
      "happiness": 0.007,
      "love": 0.001,
      "neutral": 0.752,
      "sadness": 0.017,
      "sarcasm": 0.000,
      "shame": 0.007,
      "surprise": 0.001
    }
  }
  ```

---

## 4. Model Protection & Licensing Architecture

- **Encryption Scheme**: Model weights (`encrypted_files.zip`) are encrypted using `secure_packager` with asymmetric RSA-OAEP key wrapping and vendor-signed license token `token.txt`.
- **Public / Unlicensed Behavior**: Without `customer_private.pem`, the model cannot be decrypted. The MCP server returns:
  > `Emotion Service API License Required: The emotion detection model is encrypted and protected. Running locally via Docker Compose requires a valid customer private key and license. When running from the public repository without a mounted license key, the model remains locked. To obtain access or a commercial license, please visit https://emotion-service-api.sjfisher.com or contact sales@sjfisher.com.`
- **Managed k3s Behavior**: The Kubernetes secret `emotion-service-keys` injects `customer_private.pem` and `token.txt`, decrypting the model at startup.

---

## 5. How to Connect from Another Project

### A. Over Kubernetes / k3s
When deployed using `k8s/emotion-mcp-sidecar.yaml`, another pod in the cluster connects via:
- **URL**: `http://emotion-mcp.default.svc.cluster.local:9000/mcp` (or simply `http://emotion-mcp:9000/mcp`)
- **Protocol**: Streamable-HTTP (`POST`)

### B. Over Docker Compose
Add `emotion-mcp` to your network or reference `http://emotion-mcp:9000/mcp`.

### C. Direct Curl / HTTP JSON-RPC Call
```bash
curl -s -X POST http://<host>:9000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "emotion_detection",
      "arguments": {
        "text": "I am so impressed with this new feature!"
      }
    }
  }'
```

---

## 6. Project Files Quick Reference
- Source code: [`src/mcp-go-server/`](../src/mcp-go-server/)
- Dockerfile (Multi-Arch): [`src/mcp-go-server/Dockerfile`](../src/mcp-go-server/Dockerfile)
- Sidecar Manifest for k3s: [`k8s/emotion-mcp-sidecar.yaml`](../k8s/emotion-mcp-sidecar.yaml)
- Secret Generator for k3s: [`k8s/create-secret.sh`](../k8s/create-secret.sh)
- Packaging Script: [`scripts/package-model-for-k3s.sh`](../scripts/package-model-for-k3s.sh)
