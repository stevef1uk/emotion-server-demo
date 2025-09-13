import modal
import threading
import time
import requests
import json
import sys
import logging
from flask import Flask, request, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class MCPEmotionServer:
    """MCP Server for emotion detection that works with MCP Inspector"""
    
    def __init__(self):
        self.tools = {
            "emotion_detection": {
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
        }
    
    def handle_request(self, request_data):
        """Handle incoming MCP requests"""
        try:
            method = request_data.get("method")
            request_id = request_data.get("id")
            params = request_data.get("params", {})
            
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
                            "version": "1.0.0",
                            "description": "MCP server for emotion detection using AI"
                        }
                    }
                }
                
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list(self.tools.values())
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
            
            return response
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
    
    def run_stdio(self):
        """Run the MCP server on stdio for MCP Inspector compatibility"""
        logger.info("Starting MCP Emotion Server on stdio")
        
        while True:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse JSON-RPC request
                try:
                    request_data = json.loads(line)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                    }
                    print(json.dumps(error_response), flush=True)
                    continue
                
                # Handle the request
                response = self.handle_request(request_data)
                
                # Send response to stdout
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                logger.error("Error processing request: %s", e)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Server error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)

# Create Flask app for web server mode
web_app = Flask(__name__)
mcp_server = MCPEmotionServer()

# Configure Flask to run on the correct host and port for Modal
if __name__ != "__main__":
    web_app.config['HOST'] = '0.0.0.0'
    web_app.config['PORT'] = 8000

@web_app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """Handle MCP protocol messages via HTTP"""
    try:
        data = request.get_json()
        if not data:
            return {"error": "No JSON data provided"}, 400
        
        response = mcp_server.handle_request(data)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }), 500

@web_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "server": "MCP Emotion Server",
        "version": "1.0.0",
        "tools": ["emotion_detection"]
    }

@web_app.route('/sse', methods=['GET'])
def sse_endpoint():
    """Handle SSE connections for MCP protocol."""
    from flask import Response
    
    def generate_sse():
        # Send initial connection event
        yield "data: {\"type\": \"connected\", \"message\": \"MCP server connected\"}\n\n"
        # Send a few more events and then close
        yield "data: {\"type\": \"ready\", \"message\": \"MCP server ready\"}\n\n"
        yield "data: {\"type\": \"heartbeat\", \"timestamp\": " + str(int(__import__('time').time())) + "}\n\n"
    
    return Response(
        generate_sse(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@web_app.route('/message', methods=['POST'])
def message_endpoint():
    """Handle MCP protocol messages directly (legacy endpoint)."""
    try:
        data = request.get_json()
        if not data:
            return {"error": "No JSON data provided"}, 400
        
        response = mcp_server.handle_request(data)
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id") if 'data' in locals() else None,
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }), 500

@web_app.route('/', methods=['GET'])
def root_endpoint():
    """Root endpoint with server information"""
    return {
        "name": "MCP Emotion Server",
        "version": "1.0.0",
        "description": "MCP server for emotion detection using AI",
        "endpoints": {
            "mcp": "/mcp",
            "message": "/message", 
            "sse": "/sse",
            "health": "/health"
        },
        "tools": ["emotion_detection"]
    }

@app.function(
    image=image,
    cpu=2,
    memory=4096,
    max_containers=1,  # Only one container at a time
    timeout=600,
    min_containers=0  # No keep-warm, container shuts down after idle
)
@modal.web_server(port=8000)
def serve():
    """Modal web server implementation"""
    # Start Flask app in a thread
    def run_flask():
        web_app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start
    time.sleep(2)
    
    return web_app

def main():
    """Main function - supports both stdio and web server modes"""
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # Run in stdio mode for MCP Inspector
        server = MCPEmotionServer()
        server.run_stdio()
    else:
        # Run in web server mode for Modal deployment
        print("Starting MCP Emotion Server in web mode...")
        print("For stdio mode (MCP Inspector), run: python working_solution.py --stdio")
        print("For Modal deployment, run: modal deploy working_solution.py")
        
        # This will only run when not deployed to Modal
        if __name__ == "__main__":
            web_app.run(host="0.0.0.0", port=8000, debug=True)

if __name__ == "__main__":
    main()
