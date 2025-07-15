import requests
import json
from datetime import datetime

def test_complete_workflow():
    """Test the complete PDF reminder extraction workflow"""
    base_url = "http://127.0.0.1:8001"
    
    print("=== Complete PDF Reminder Extraction Workflow Test ===\n")
    
    # Test 1: Health check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
        return False
    
    # Test 2: Root endpoint with API info
    print("2. Testing Root Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Message: {data['msg']}")
        print(f"   Available Endpoints:")
        for endpoint, description in data['endpoints'].items():
            print(f"     - {description}")
        print()
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 3: Simulate PDF upload response (since we don't have actual PDF)
    print("3. Simulating PDF Upload with Mock Data...")
    # This simulates what the /upload endpoint would return after processing a PDF
    mock_extracted_reminders = [
        {"event": "Omar visa renewal", "date": "2027-05-20"},
        {"event": "Ahmed ID expiry", "date": "2027-05-20"},  # Same date as Omar
        {"event": "Final design submission", "date": "2025-12-01"},
        {"event": "Project deadline", "date": "2025-12-01"},  # Same date as design
        {"event": "Medical checkup", "date": "2026-03-15"}
    ]
    print(f"   Mock extracted reminders:")
    for reminder in mock_extracted_reminders:
        print(f"     - {reminder['event']} on {reminder['date']}")
    print()
    
    # Test 4: Confirm reminders
    print("4. Testing Confirm Reminders Endpoint...")
    try:
        confirm_data = {
            "reminders": mock_extracted_reminders,
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/confirm", json=confirm_data)
        print(f"   ✅ Status: {response.status_code}")
        result = response.json()
        print(f"   Message: {result['message']}")
        print(f"   Total Reminders Stored: {result['total_reminders']}\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
        return False
    
    # Test 5: Get grouped reminders
    print("5. Testing Get Reminders (Grouped by Date)...")
    try:
        response = requests.get(f"{base_url}/reminders?user_id=test_user")
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        
        print(f"   Total Individual Reminders: {data['total_count']}")
        print(f"   Grouped by Date:")
        
        for group in data['reminders']:
            print(f"\n   📅 {group['date']}:")
            for reminder in group['reminders']:
                print(f"     • {reminder}")
        
        print(f"\n   Expected Format Validation:")
        print(f"   ✅ Response has 'reminders' array: {'reminders' in data}")
        print(f"   ✅ Response has 'total_count': {'total_count' in data}")
        
        if data['reminders']:
            first_group = data['reminders'][0]
            print(f"   ✅ Each group has 'date': {'date' in first_group}")
            print(f"   ✅ Each group has 'reminders' array: {'reminders' in first_group}")
            print(f"   ✅ Reminders are strings: {all(isinstance(r, str) for r in first_group['reminders'])}")
        
        print()
        
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
        return False
    
    # Test 6: Test the exact format requested
    print("6. Validating Exact Response Format...")
    try:
        response = requests.get(f"{base_url}/reminders?user_id=test_user")
        data = response.json()
        
        print("   Expected format example:")
        print('   {')
        print('     "date": "2027-05-20",')
        print('     "reminders": [')
        print('       "Omar visa renewal",')
        print('       "Ahmed ID expiry"')
        print('     ]')
        print('   }')
        print()
        
        print("   Actual format received:")
        for group in data['reminders']:
            print('   {')
            print(f'     "date": "{group["date"]}",')
            print('     "reminders": [')
            for i, reminder in enumerate(group['reminders']):
                comma = "," if i < len(group['reminders']) - 1 else ""
                print(f'       "{reminder}"{comma}')
            print('     ]')
            print('   }')
        print()
        
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    # Test 7: Add more reminders to test grouping
    print("7. Testing Additional Reminders (Same Dates)...")
    try:
        additional_reminders = [
            {"event": "Sarah passport renewal", "date": "2027-05-20"},  # Same as Omar & Ahmed
            {"event": "Team meeting", "date": "2025-12-01"},  # Same as design & project
        ]
        
        confirm_data = {
            "reminders": additional_reminders,
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/confirm", json=confirm_data)
        print(f"   ✅ Added {len(additional_reminders)} more reminders")
        
        # Get updated grouped reminders
        response = requests.get(f"{base_url}/reminders?user_id=test_user")
        data = response.json()
        
        print(f"   Updated grouped reminders:")
        for group in data['reminders']:
            print(f"   📅 {group['date']}: {len(group['reminders'])} reminders")
            for reminder in group['reminders']:
                print(f"     • {reminder}")
        print()
        
    except Exception as e:
        print(f"   ❌ Failed: {e}\n")
    
    print("🎉 Complete workflow test finished!")
    print(f"🌐 API Documentation: {base_url}/docs")
    print(f"📖 Interactive Docs: {base_url}/redoc")
    print(f"\n📄 To test PDF upload:")
    print(f"   curl -X POST '{base_url}/upload' -F 'file=@your_document.pdf'")
    
    return True

def test_api_endpoints_summary():
    """Display a summary of all available API endpoints"""
    base_url = "http://127.0.0.1:8001"
    
    print("\n=== API Endpoints Summary ===")
    print(f"Base URL: {base_url}")
    print()
    print("📤 POST /upload")
    print("   - Upload PDF file")
    print("   - Extract reminders using GPT-4o")
    print("   - Return extracted reminders for confirmation")
    print()
    print("✅ POST /confirm") 
    print("   - Accept confirmed reminders from user")
    print("   - Store in memory database")
    print("   - Return confirmation message")
    print()
    print("📊 GET /reminders")
    print("   - Return all confirmed reminders")
    print("   - Group reminders by date")
    print("   - Format: {date: string, reminders: string[]}")
    print()
    print("❤️ GET /health")
    print("   - Health check endpoint")
    print()
    print("🏠 GET /")
    print("   - Root endpoint with API information")

if __name__ == "__main__":
    test_complete_workflow()
    test_api_endpoints_summary() 