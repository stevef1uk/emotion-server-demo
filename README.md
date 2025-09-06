# Emotion API Stack

A complete Docker Compose setup for the Emotion API service with UI and MCP server.

## Architecture

The stack consists of three main services:

1. **Emotion API** (`emotion-api`) - Main Go server with llama.cpp integration
2. **Python UI** (`emotion-ui`) - Python Flask/FastAPI server providing web interface
3. **MCP Server** (`emotion-mcp`) - Go-based MCP server for external integrations

## Prerequisites

- Docker and Docker Compose installed
- Required files and directories (see Project Structure below)

## Project Structure

```
.
├── docker-compose.yml
├── Dockerfile                     # Main emotion API
├── python_server/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── emotion_server.py
│   └── ...
├── mcp-go-server/
│   ├── Dockerfile
│   ├── go.mod
│   ├── go.sum
│   ├── main/
│   └── ...
├── keys/
│   └── public_key.pem
├── gemma3_emotion_model_unsloth/
│   └── release/
│       ├── encrypted_files.zip
│       └── token.txt
└── server/                        # Go server source
    ├── go.mod
    ├── go.sum
    └── ...
```

## Quick Start

1. **Clone/prepare your project** with all required files

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Or manually:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Wait for services to start** (may take a few minutes for first run)

4. **Access the services**:
   - Emotion API: http://localhost:8000
   - Python UI: http://localhost:5001
   - Prediction endpoint: http://localhost:5001/predict
   - MCP Server: http://localhost:9000

## Service Details

### Emotion API (Port 8000, 8080)
- Main Go server handling emotion analysis
- Internal llama.cpp server on port 8080
- Decrypts and loads the ML model on startup
- Provides REST API endpoints

### Python UI (Port 5001)
- Python web server providing user interface
- Proxies requests to the main Emotion API
- Provides `/predict` endpoint for external access
- Environment variable: `EMOTION_API_URL=http://emotion-api:8000`

### MCP Server (Port 9000)
- Go-based MCP (Model Context Protocol) server
- Connects to Python UI's prediction endpoint
- Environment variable: `EMOTION_SERVICE_URL=http://emotion-ui:5001/predict`

## Environment Variables

### Emotion API
- `MODEL_PATH=/app/model`
- `LLAMA_SERVER_URL=http://127.0.0.1:8080`
- `LLAMA_SERVER_PORT=8080`
- `GO_SERVER_PORT=8000`
- `PUBLIC_KEY_PATH=/app/keys/public_key.pem`
- `TOKEN_FILE_PATH=/app/gemma3_emotion_model_unsloth/release/token.txt`
- `ENCRYPTED_ZIP_PATH=/app/gemma3_emotion_model_unsloth/release/encrypted_files.zip`
- `DECRYPT_OUTPUT_DIR=/app/model`

### Python UI
- `EMOTION_API_URL=http://emotion-api:8000`

### MCP Server
- `EMOTION_SERVICE_URL=http://emotion-ui:5001/predict`
- `MCP_SERVER_PORT=9000`

## Management Commands

### Start services
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f emotion-api
docker-compose logs -f emotion-ui
docker-compose logs -f emotion-mcp
```

### Stop services
```bash
docker-compose down
```

### Rebuild services
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Check service status
```bash
docker-compose ps
```

### Restart a service
```bash
docker-compose restart emotion-api
```

## Troubleshooting

### Services won't start
1. Check logs: `docker-compose logs -f [service-name]`
2. Verify all required files exist (see Project Structure)
3. Ensure ports 5001, 8000, 8080, 9000 are available
4. Check Docker daemon is running

### Model decryption fails
1. Verify `public_key.pem` exists and is valid
2. Check `token.txt` contains valid decryption token
3. Ensure `encrypted_files.zip` is present and not corrupted

### Connection issues between services
1. Services communicate via Docker network `emotion_network`
2. Check service dependencies in docker-compose.yml
3. Verify health checks are passing
4. Use service names (not localhost) for inter-service communication

### Health checks failing
Services include health checks that verify they're responding correctly:
- Emotion API: `curl -f http://localhost:8000/health`
- Python UI: `curl -f http://localhost:5001/health`
- MCP Server: `curl -f http://localhost:9000/health`

Add these endpoints to your applications if they don't exist.

## Development

### Local development
For local development, you can override specific services:

```bash
# Run only emotion-api and emotion-ui, develop MCP locally
docker-compose up emotion-api emotion-ui
cd mcp-go-server && go run ./main
```

### Updating a service
```bash
# Rebuild and restart specific service
docker-compose build emotion-ui
docker-compose up -d emotion-ui
```

## Security Notes

- Services run as non-root users where possible
- Only necessary ports are exposed
- Encrypted model files require proper decryption keys
- Consider adding authentication for production use

## Production Deployment

For production deployment:

1. **Use environment-specific compose files**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Set up proper secrets management** for keys and tokens

3. **Configure reverse proxy** (nginx/traefik) for SSL termination

4. **Set up monitoring and logging**

5. **Configure backup for model data volume**
