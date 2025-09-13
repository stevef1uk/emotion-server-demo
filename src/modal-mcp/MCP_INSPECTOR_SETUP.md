# MCP Inspector Setup Guide

## ❌ Common Mistake
**Don't try to connect MCP Inspector directly to HTTP endpoints!**

MCP Inspector expects a **stdio-based MCP server**, not HTTP endpoints. The `/sse` endpoint returning 200 OK doesn't mean MCP Inspector can connect to it.

## ✅ Correct Setup

### Step 1: Deploy Your Server to Modal
```bash
cd /Users/stevef/dev/emotion-server-demo/src/modal-mcp
modal deploy working_solution.py
```

### Step 2: Install MCP Inspector
```bash
npm install -g @modelcontextprotocol/inspector
```

### Step 3: Run MCP Inspector
```bash
npx @modelcontextprotocol/inspector
```

### Step 4: Configure Connection
When MCP Inspector asks for server configuration, use:

- **Command:** `python`
- **Args:** `saas_mcp_client.py`
- **Working Directory:** `/Users/stevef/dev/emotion-server-demo/src/modal-mcp`

## 🔍 How It Works

1. **MCP Inspector** → communicates via stdio → **saas_mcp_client.py**
2. **saas_mcp_client.py** → makes HTTP requests → **Modal server**
3. **Modal server** → processes emotion detection → **returns response**
4. **Response flows back** through the same chain

## 🧪 Test First

Before using with MCP Inspector, test the setup:

```bash
python test_saas_client.py
```

This will verify that:
- The SaaS client can connect to your Modal server
- The emotion detection API works
- The MCP protocol communication is working

## 🛠️ Troubleshooting

### If MCP Inspector says "didn't connect":
1. Make sure you're using `saas_mcp_client.py`, not the HTTP URL
2. Verify the working directory path is correct
3. Test with `test_saas_client.py` first
4. Check that your Modal server is deployed and running

### If you get connection errors:
1. Check Modal deployment status: `modal app list`
2. Test the server directly: `curl https://your-server.modal.run/health`
3. Check the SaaS client logs for specific error messages

## 📋 Summary

- **MCP Inspector** = stdio-based tool
- **Your Modal server** = HTTP-based server  
- **saas_mcp_client.py** = bridge between them
- **Don't connect MCP Inspector directly to HTTP endpoints!**
