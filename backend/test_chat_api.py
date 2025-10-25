"""
Quick API test for chat endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_chat_endpoint():
    """Test POST /api/chat"""
    print("\n=== Testing Chat Endpoint ===")
    
    payload = {
        "user_id": "farmer_123",
        "farm_id": "farm_456",
        "message": "How is my wheat crop doing?",
        "include_context": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Intent detected: {data.get('intent')}")
            print(f"✓ Confidence: {data.get('confidence_level')}")
            print(f"✓ Response preview: {data.get('response_text')[:100]}...")
            print(f"✓ Suggestions count: {len(data.get('suggestions', []))}")
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_chat_history():
    """Test GET /api/chat/history/{farm_id}"""
    print("\n=== Testing Chat History ===")
    
    farm_id = "farm_456"
    
    try:
        response = requests.get(f"{BASE_URL}/chat/history/{farm_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Retrieved {data.get('count')} messages")
            print(f"✓ Farm ID: {data.get('farm_id')}")
        else:
            print(f"✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_voice_endpoint():
    """Test POST /api/chat/voice (future)"""
    print("\n=== Testing Voice Endpoint ===")
    
    # Query params since it's not fully implemented yet
    params = {
        "user_id": "farmer_123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/voice", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Message: {data.get('message')}")
            print(f"✓ Status: {data.get('status')}")
        else:
            print(f"✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Chat API Endpoint Tests")
    print("=" * 60)
    print("Make sure the server is running on http://localhost:8000")
    
    test_chat_endpoint()
    test_chat_history()
    test_voice_endpoint()
    
    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)
