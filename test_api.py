import requests
import json

def test_api():
    """Test the PDF Reminder Extraction API"""
    base_url = "http://127.0.0.1:8001"
    
    print("=== Testing PDF Reminder Extraction API ===\n")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test 2: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root Endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root Endpoint Failed: {e}")
    
    # Test 3: Confirm reminders
    try:
        data = {
            "reminders": [
                {"event": "Omar visa renewal", "date": "2027-05-20"},
                {"event": "Final design submission", "date": "2025-12-01"}
            ],
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/confirm-reminders", json=data)
        print(f"✅ Confirm Reminders: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Confirm Reminders Failed: {e}")
    
    # Test 4: Get reminders
    try:
        response = requests.get(f"{base_url}/reminders/test_user")
        print(f"✅ Get Reminders: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Get Reminders Failed: {e}")
    
    print(f"\n🌐 API Documentation: {base_url}/docs")
    print(f"🔧 Interactive API: {base_url}/redoc")
    print(f"\n📄 To test PDF upload:")
    print(f"   curl -X POST '{base_url}/upload' -F 'file=@your_document.pdf'")
    
    return True

if __name__ == "__main__":
    test_api() 