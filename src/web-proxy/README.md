# Emotion Web UI & Gateway Proxy Pod

A high-performance, ultra-lean Go pod (~15MB) that serves the public web UI for the Emotion Detection Service and securely proxies requests through the **Agent Gateway Policy Enforcement Point**.

## Features

- **Zero Secret Exposure:** `DELEGATION_ID` and `AGENT_SECRET` are managed entirely server-side (injected via Kubernetes Secret). The browser never receives or handles gateway secrets.
- **Embedded Static UI:** Fast, modern single-binary web interface (`//go:embed`) with live emotion probability distribution charts and pre-filled samples.
- **Automatic Token Lifecycle:** Automatically mints, caches, and rotates 15-minute Bearer tokens against the gateway `/token` endpoint.
- **Human-in-the-Loop Integration:** When detailed emotion spectrum queries are marked high-risk by gateway policy, the UI cleanly handles the `202 Accepted` hold state and links to the approval queue.
- **Native ARM64 Build:** Optimized for Raspberry Pi 5 k3s cluster deployment.

## Building the ARM64 Image

```bash
cd src/web-proxy
docker buildx build --platform linux/arm64 -t stevef1uk/emotion-web:arm64 --push .
```

## Running Locally

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Set your `DELEGATION_ID` and `AGENT_SECRET` in `.env`.
3. Run the Go server:
   ```bash
   export $(cat .env | xargs)
   go run .
   ```
4. Visit `http://localhost:8080`.
