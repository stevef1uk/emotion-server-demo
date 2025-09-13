# Public MCP Emotion Server

This is a public MCP server that provides emotion detection capabilities to 3rd party SaaS tools.

## 🚀 Deployment

Deploy the public MCP server to Modal:

```bash
modal deploy public_mcp_server.py
```

This will create a public endpoint at:
`https://stevef1uk--mcp-emotion-server-public-serve.modal.run`

## 🔧 Usage with 3rd Party Tools

### For MCP Inspector:
1. **Run MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector
   ```

2. **Connect to:**
   - **Command:** `python`
   - **Args:** `public_mcp_client.py`
   - **Working Directory:** `/Users/stevef/dev/emotion-server-demo/src/modal-mcp`

### For Claude Desktop:
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "emotion-detection": {
      "command": "python",
      "args": ["/Users/stevef/dev/emotion-server-demo/src/modal-mcp/public_mcp_client.py"],
      "cwd": "/Users/stevef/dev/emotion-server-demo/src/modal-mcp"
    }
  }
}
```

### For Other Tools:
Use the `public_mcp_client.py` script as a bridge between your tool and the public MCP server.

## 📡 API Endpoints

- **`/mcp`** - Main MCP protocol endpoint
- **`/health`** - Health check
- **`/info`** - Server information

## 🛠️ Available Tools

### `emotion_detection`
- **Description:** Analyze text to detect emotions using AI
- **Input:** `text` (string) - The text to analyze
- **Output:** Emotion analysis with confidence score

## 🔗 Server Information

- **Name:** Emotion Detection MCP Server (Public)
- **Version:** 1.0.0
- **Protocol:** MCP over HTTP
- **Backend:** Modal emotion service

## 📝 Example Usage

```python
# Test the server directly
import requests

response = requests.post(
    "https://stevef1uk--mcp-emotion-server-public-serve.modal.run/mcp",
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "emotion_detection",
            "arguments": {
                "text": "I am so excited about this!"
            }
        }
    }
)

print(response.json())
```

## 🌐 Public Access

This MCP server is publicly accessible and can be used by anyone. The emotion detection is powered by your Modal emotion service running in the cloud.
