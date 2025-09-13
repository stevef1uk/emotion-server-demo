import modal
import subprocess
import threading
import time
import requests
from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler

# Define the app
app = modal.App("mcp-emotion-server-working-solution")

# Create a Modal image that matches your working Docker setup
image = modal.Image.debian_slim(python_version="3.11").pip_install("flask", "requests").apt_install("wget", "nodejs", "npm").run_commands([
    "wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz",
    "tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz",
    "rm go1.22.0.linux-amd64.tar.gz",
    "npm install -g supergateway"
]).env({"PATH": "/usr/local/go/bin:${PATH}"})

def detect_emotion(text):
    """Call the Modal emotion service"""
    try:
        url = "https://stevef1uk--emotion-server-serve.modal.run/predict"
        payload = {"text": text}
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        emotion = result.get('emotion', 'unknown')
        confidence = result.get('confidence', 0.0)
        
        return f"Emotion: {emotion} (Confidence: {confidence:.2%})"
        
    except Exception as e:
        return f"Error detecting emotion: {str(e)}"

# Create Flask app
web_app = Flask(__name__)

# Configure Flask to run on the correct host and port for Modal
if __name__ != "__main__":
    web_app.config['HOST'] = '0.0.0.0'
    web_app.config['PORT'] = 8000

@web_app.route('/sse')
def sse_endpoint():
    """Handle SSE connections for MCP protocol."""
    return "SSE endpoint - MCP server is running", 200

@web_app.route('/message', methods=['POST'])
def message_endpoint():
    """Handle MCP protocol messages directly."""
    try:
        data = request.get_json()
        if not data:
            return {"error": "No JSON data provided"}, 400
        
        method = data.get("method")
        request_id = data.get("id")
        params = data.get("params", {})
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "Emotion Detection MCP Server",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "emotion_detection",
                            "description": "Analyze text to detect emotions using AI",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "The text to analyze for emotion"
                                    }
                                },
                                "required": ["text"]
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "emotion_detection":
                text = arguments.get("text", "")
                emotion_result = detect_emotion(text)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": emotion_result
                            }
                        ],
                        "isError": False
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }), 500

@app.function(
    image=image,
    cpu=2,
    memory=4096,
    max_containers=1,
    timeout=600
)
@modal.web_server(port=8000)
def serve():
    """Working MCP server implementation"""
    # Start Flask app in a thread
    def run_flask():
        web_app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(2)
    
    return web_app
