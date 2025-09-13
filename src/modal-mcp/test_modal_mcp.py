#!/usr/bin/env python3
"""
Test the Modal MCP server deployment
"""

import requests
import json
import time

def test_modal_mcp():
    """Test the Modal MCP server deployment"""
    
    # The Modal deployment URL
    base_url = "https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run"
    
    print(f"Testing Modal MCP server at: {base_url}")
    
    # First, establish an SSE connection
    print("\n0. Establishing SSE connection...")
    session_id = "test-session-123"
    try:
        sse_response = requests.get(f"{base_url}/sse?sessionId={session_id}", stream=True, timeout=10)
        print(f"SSE connection status: {sse_response.status_code}")
        if sse_response.status_code != 200:
            print(f"SSE connection failed: {sse_response.text}")
            return False
        print("✅ SSE connection established")
    except Exception as e:
        print(f"SSE connection failed: {e}")
        return False
    
    # Test 1: Initialize
    print("\n1. Testing MCP initialization...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(f"{base_url}/message?sessionId=test-session-123", json=init_request, headers=headers, timeout=30)
        print(f"Initialize response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Initialize result: {json.dumps(result, indent=2)}")
        else:
            print(f"Initialize error: {response.text}")
    except Exception as e:
        print(f"Initialize request failed: {e}")
        return False
    
    # Test 2: List tools
    print("\n2. Testing tools/list...")
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(f"{base_url}/message?sessionId=test-session-123", json=tools_request, headers=headers, timeout=30)
        print(f"Tools list response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Tools list result: {json.dumps(result, indent=2)}")
        else:
            print(f"Tools list error: {response.text}")
    except Exception as e:
        print(f"Tools list request failed: {e}")
        return False
    
    # Test 3: Emotion detection
    print("\n3. Testing emotion_detection...")
    emotion_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "emotion_detection",
            "arguments": {
                "text": "I am so excited about this!"
            }
        }
    }
    
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(f"{base_url}/message?sessionId=test-session-123", json=emotion_request, headers=headers, timeout=60)
        print(f"Emotion detection response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Emotion detection result: {json.dumps(result, indent=2)}")
        else:
            print(f"Emotion detection error: {response.text}")
    except Exception as e:
        print(f"Emotion detection request failed: {e}")
        return False
    
    print("\n✅ Modal MCP server test completed!")
    return True

if __name__ == "__main__":
    test_modal_mcp()
