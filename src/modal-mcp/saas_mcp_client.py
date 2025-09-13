#!/usr/bin/env python3
"""
SaaS MCP Client - Connect to the public MCP server for SaaS tools
This script can be used by SaaS tools to connect to your public MCP server
"""

import sys
import json
import requests
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SaaSMCPClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SaaS-MCP-Client/1.0'
        })
    
    def handle_request(self, request_data):
        """Forward MCP request to public server"""
        try:
            # Try the main MCP endpoint first
            response = self.session.post(
                f"{self.server_url}/mcp",
                json=request_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Fallback to message endpoint for compatibility
            try:
                response = self.session.post(
                    f"{self.server_url}/message",
                    json=request_data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e2:
                logger.error(f"Error calling MCP server: {e2}")
                return {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "error": {"code": -32603, "message": f"Server error: {str(e2)}"}
                }
    
    def run_stdio(self):
        """Run the MCP client on stdio for SaaS tools"""
        logger.info(f"Connecting to SaaS MCP server: {self.server_url}")
        
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
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                    }
                    print(json.dumps(error_response), flush=True)
                    continue
                
                # Forward to public server
                response = self.handle_request(request)
                
                # Send response to stdout
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Client error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)

def main():
    """Main function"""
    # Get server URL from environment or use default
    server_url = os.environ.get('MCP_SERVER_URL', 'https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run')
    
    client = SaaSMCPClient(server_url)
    client.run_stdio()

if __name__ == "__main__":
    main()
