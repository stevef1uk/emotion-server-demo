#!/usr/bin/env python3
"""
Quick test script to verify the emotion API integration
"""

import requests
import json

def test_emotion_api():
    """Test if the emotion API is running and responding correctly"""
    
    print("🔍 Testing emotion API connection...")
    
    try:
        # Test basic connectivity using the health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Emotion API is running and accessible")
        else:
            print(f"⚠️ Emotion API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Emotion API is not accessible: {e}")
        print("💡 Make sure to start the emotion service first:")
        print("   cd src && IMAGE_TAG=amd64 docker-compose up --build -d")
        return False
    
    # Test emotion prediction
    test_messages = [
        "I am so happy today!",
        "I am absolutely furious with this service!",
        "I'm feeling confused about my order",
        "Thank you for your excellent support!"
    ]
    
    print("\n🧪 Testing emotion predictions...")
    
    for message in test_messages:
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json={"text": message},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ '{message[:30]}...' → {result}")
            else:
                print(f"❌ Failed to predict emotion for: '{message[:30]}...' (Status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error predicting emotion for: '{message[:30]}...' - {e}")
    
    print("\n🎉 API test completed!")
    return True

if __name__ == "__main__":
    test_emotion_api()
