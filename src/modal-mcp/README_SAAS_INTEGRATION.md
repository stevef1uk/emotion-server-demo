# SaaS Integration Guide for MCP Emotion Server

This guide shows how to integrate the MCP Emotion Server with SaaS solutions that need to access it over the internet.

## 🚀 Quick Setup

### 1. Deploy the MCP Server to Modal
```bash
cd /Users/stevef/dev/emotion-server-demo/src/modal-mcp
modal deploy working_solution.py
```

This creates a public endpoint at:
`https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run`

### 2. Test the Public Server
```bash
# Test health endpoint
curl https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/health

# Test MCP endpoint
curl -X POST https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

## 🔧 SaaS Tool Integration

### For MCP Inspector (Remote Server)
1. **Install MCP Inspector:**
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Run MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector
   ```

3. **Configure Connection:**
   - **Command:** `python`
   - **Args:** `saas_mcp_client.py`
   - **Working Directory:** `/Users/stevef/dev/emotion-server-demo/src/modal-mcp`

### For Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "emotion-detection": {
      "command": "python",
      "args": ["/Users/stevef/dev/emotion-server-demo/src/modal-mcp/saas_mcp_client.py"],
      "cwd": "/Users/stevef/dev/emotion-server-demo/src/modal-mcp"
    }
  }
}
```

### For Other SaaS Tools
Use the `saas_mcp_client.py` script as a bridge between your SaaS tool and the public MCP server.

## 📡 API Endpoints

The public server provides multiple endpoints for compatibility:

- **`/mcp`** - Main MCP protocol endpoint (recommended)
- **`/message`** - Legacy MCP protocol endpoint
- **`/sse`** - Server-Sent Events endpoint
- **`/health`** - Health check
- **`/`** - Server information

## 🛠️ Available Tools

### `emotion_detection`
- **Description:** Analyze text to detect emotions using AI
- **Input:** `text` (string) - The text to analyze
- **Output:** Emotion analysis with confidence score

## 📝 Example Usage

### Direct API Calls
```python
import requests

# Initialize the MCP server
init_response = requests.post(
    "https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/mcp",
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "my-saas-tool",
                "version": "1.0.0"
            }
        }
    }
)

# List available tools
tools_response = requests.post(
    "https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/mcp",
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
)

# Call emotion detection
emotion_response = requests.post(
    "https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/mcp",
    json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "emotion_detection",
            "arguments": {
                "text": "I am so excited about this new feature!"
            }
        }
    }
)

print(emotion_response.json())
```

### Using the SaaS MCP Client
```bash
# Set custom server URL (optional)
export MCP_SERVER_URL="https://your-custom-server.modal.run"

# Run the client
python saas_mcp_client.py
```

## 🌐 Environment Variables

- **`MCP_SERVER_URL`** - Override the default server URL
- **`LOG_LEVEL`** - Set logging level (DEBUG, INFO, WARNING, ERROR)

## 🔒 Security Considerations

- The server is publicly accessible
- No authentication is required (suitable for demo/testing)
- For production use, consider adding API keys or authentication
- Rate limiting is handled by Modal's infrastructure

## 🛠️ Troubleshooting

### Common Issues
1. **Connection timeout**: Check if the Modal server is running
2. **404 errors**: Verify the endpoint URLs
3. **JSON parse errors**: Ensure proper JSON formatting

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python saas_mcp_client.py
```

### Health Check
```bash
curl https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/health
```

## 📋 Requirements

- Python 3.11+
- Modal account and CLI
- Internet connection
- SaaS tool that supports MCP protocol

## 🚀 Deployment Commands

```bash
# Deploy to Modal
modal deploy working_solution.py

# Check deployment status
modal app list

# View logs
modal app logs mcp-emotion-server-working-solution

# Test locally before deployment
python working_solution.py
```

## 📊 Monitoring

Monitor your MCP server through:
- Modal dashboard: https://modal.com/dashboard
- Server health endpoint: `/health`
- Server info endpoint: `/`
