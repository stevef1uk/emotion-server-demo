# MCP Inspector Setup for Emotion Server

This guide shows how to use the `working_solution.py` with the MCP Inspector on Modal.

## 🚀 Quick Start

### 1. Install MCP Inspector
```bash
npm install -g @modelcontextprotocol/inspector
```

### 2. Run MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```

### 3. Connect to the Emotion Server
When prompted for server configuration:
- **Command:** `python`
- **Args:** `working_solution.py --stdio`
- **Working Directory:** `/Users/stevef/dev/emotion-server-demo/src/modal-mcp`

## 🧪 Testing

### Test the MCP Server Locally
```bash
cd /Users/stevef/dev/emotion-server-demo/src/modal-mcp
python test_mcp_inspector.py
```

### Test with MCP Inspector
1. Start MCP Inspector: `npx @modelcontextprotocol/inspector`
2. Configure connection as shown above
3. Test the `emotion_detection` tool with sample text

## 📡 Available Tools

### `emotion_detection`
- **Description:** Analyze text to detect emotions using AI
- **Input:** `text` (string) - The text to analyze
- **Output:** Emotion analysis with confidence score

## 🔧 Modes

The `working_solution.py` supports two modes:

### Stdio Mode (for MCP Inspector)
```bash
python working_solution.py --stdio
```

### Web Server Mode (for Modal deployment)
```bash
python working_solution.py
# or
modal deploy working_solution.py
```

## 🌐 Modal Deployment

Deploy to Modal for public access:
```bash
modal deploy working_solution.py
```

This creates a web server at:
`https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run`

## 📝 Example Usage

### Via MCP Inspector
1. Open MCP Inspector
2. Connect to the server
3. Use the `emotion_detection` tool with text like:
   - "I am so excited about this!"
   - "This is really frustrating."
   - "I feel great today!"

### Via Direct API (when deployed)
```python
import requests

response = requests.post(
    "https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run/mcp",
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

## 🛠️ Troubleshooting

### Common Issues
1. **Import errors**: Make sure you're in the correct directory
2. **Connection issues**: Verify the working directory path
3. **Tool not found**: Check that the server is running in stdio mode

### Debug Mode
Run with debug logging:
```bash
PYTHONPATH=. python working_solution.py --stdio
```

## 📋 Requirements

- Python 3.11+
- Modal account and CLI
- Node.js (for MCP Inspector)
- Internet connection (for emotion detection API)
