#!/usr/bin/env python3
"""
Test the Modal service connection directly
"""

import requests
import json

def test_modal_service():
    """Test the Modal service directly"""
    server_url = "https://stevef1uk--mcp-emotion-server-working-solution-serve.modal.run"
    
    print("Testing Modal service directly...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        print(f"Health status: {response.status_code}")
        print(f"Health response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test 2: Initialize
    print("\n2. Testing initialize...")
    try:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            f"{server_url}/mcp",
            json=init_request,
            timeout=10
        )
        print(f"Initialize status: {response.status_code}")
        print(f"Initialize response: {response.json()}")
    except Exception as e:
        print(f"Initialize failed: {e}")
        return
    
    # Test 3: List tools
    print("\n3. Testing tools/list...")
    try:
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            f"{server_url}/mcp",
            json=list_request,
            timeout=10
        )
        print(f"Tools list status: {response.status_code}")
        print(f"Tools list response: {response.json()}")
    except Exception as e:
        print(f"Tools list failed: {e}")
        return
    
    # Test 4: Call emotion detection
    print("\n4. Testing emotion detection...")
    try:
        call_request = {
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
        
        response = requests.post(
            f"{server_url}/mcp",
            json=call_request,
            timeout=30
        )
        print(f"Emotion detection status: {response.status_code}")
        print(f"Emotion detection response: {response.json()}")
    except Exception as e:
        print(f"Emotion detection failed: {e}")
        return
    
    print("\n✅ All Modal service tests passed!")

if __name__ == "__main__":
    test_modal_service()
