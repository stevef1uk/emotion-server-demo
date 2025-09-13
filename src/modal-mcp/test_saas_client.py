#!/usr/bin/env python3
"""
Test the SaaS MCP client with the public server
"""

import json
import subprocess
import sys
import time

def test_saas_client():
    """Test the SaaS MCP client"""
    print("Testing SaaS MCP Client with public server...")
    
    # Start the SaaS MCP client
    process = subprocess.Popen(
        [sys.executable, "saas_mcp_client.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test 1: Initialize
        print("\n1. Testing initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-saas-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(2)
        response = process.stdout.readline()
        if response:
            init_response = json.loads(response.strip())
            print(f"Initialize response: {init_response}")
        else:
            print("No response received")
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"Error output: {stderr_output}")
            return
        
        # Test 2: List tools
        print("\n2. Testing tools/list...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_request) + "\n")
        process.stdin.flush()
        
        time.sleep(2)
        response = process.stdout.readline()
        if response:
            list_response = json.loads(response.strip())
            print(f"Tools list response: {list_response}")
        else:
            print("No response for tools/list")
        
        # Test 3: Call emotion detection tool
        print("\n3. Testing tools/call...")
        call_request = {
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
        
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        time.sleep(3)  # Give more time for the emotion detection API call
        response = process.stdout.readline()
        if response:
            call_response = json.loads(response.strip())
            print(f"Tool call response: {call_response}")
        else:
            print("No response for tools/call")
        
        print("\n✅ SaaS client test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Error output: {stderr_output}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_saas_client()
