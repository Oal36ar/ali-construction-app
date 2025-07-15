#!/usr/bin/env python3
"""
Frontend-Backend Connection Test Script
Tests all API endpoints used by the React frontend
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_endpoint(method, endpoint, data=None, files=None, expected_status=200):
    """Test a single endpoint and return results"""
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, data=data, files=files, timeout=30)
            elif data:
                response = requests.post(url, json=data, timeout=30)
            else:
                response = requests.post(url, timeout=30)
        else:
            return {"status": "SKIP", "reason": f"Method {method} not implemented"}

        if response.status_code == expected_status:
            try:
                response_data = response.json()
                return {
                    "status": "✅ PASS",
                    "response_time": f"{response.elapsed.total_seconds():.3f}s",
                    "data": response_data
                }
            except:
                return {
                    "status": "✅ PASS",
                    "response_time": f"{response.elapsed.total_seconds():.3f}s",
                    "data": response.text[:200]
                }
        else:
            return {
                "status": "❌ FAIL",
                "error": f"HTTP {response.status_code}",
                "response": response.text[:200]
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "❌ FAIL",
            "error": str(e)
        }

def run_comprehensive_test():
    """Run comprehensive test of all endpoints"""
    print("🚀 FRONTEND-BACKEND CONNECTION TEST")
    print("=" * 60)
    print(f"Testing backend: {BACKEND_URL}")
    print(f"Frontend should be at: {FRONTEND_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        # Core status endpoints
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/status", "Status endpoint (NEW)"),
        
        # Chat endpoints
        ("POST", "/chat", "Chat endpoint", {"message": "Hello, test connection"}),
        ("GET", "/tools/available", "Available tools"),
        
        # File upload endpoint  
        ("POST", "/upload/", "File upload", None, {"test_file": ("test.txt", "This is a test file content", "text/plain")}),
        
        # Reminder endpoints
        ("GET", "/reminders/all", "Get reminders"),
        ("POST", "/reminders/", "Create reminder", {
            "title": "Test Reminder",
            "due_date": "2024-12-31",
            "description": "Test reminder created by connection test"
        }),
        
        # History endpoints
        ("GET", "/history/activity", "Activity history"),
        
        # Confirmation endpoint
        ("POST", "/confirm/", "Confirm action", {
            "decision": "yes",
            "session_id": "test_session_123"
        }),
        
        # Test endpoint
        ("POST", "/test/full", "Full backend test"),
    ]

    results = {}
    total_tests = len(tests)
    passed_tests = 0
    failed_tests = 0

    for i, test_data in enumerate(tests, 1):
        method, endpoint, description = test_data[:3]
        data = test_data[3] if len(test_data) > 3 else None
        files = test_data[4] if len(test_data) > 4 else None
        
        print(f"\n[{i:2d}/{total_tests}] Testing {description}")
        print(f"       {method} {endpoint}")
        
        result = test_endpoint(method, endpoint, data, files)
        results[endpoint] = result
        
        if result["status"].startswith("✅"):
            passed_tests += 1
            print(f"       {result['status']} ({result.get('response_time', 'N/A')})")
        else:
            failed_tests += 1
            print(f"       {result['status']} - {result.get('error', 'Unknown error')}")
    
    # Test proxy functionality
    print(f"\n[{total_tests + 1}] Testing Vite proxy functionality")
    try:
        # This would test if the proxy is working from frontend perspective
        proxy_test_note = """
        ℹ️  PROXY TEST: 
        Frontend calls to /api/* should proxy to backend automatically.
        Start both servers and visit http://localhost:5173 to test:
        
        cd backend && python main.py     # Terminal 1
        cd frontend && npm run dev       # Terminal 2
        """
        print(proxy_test_note)
        results["/api/*"] = {"status": "ℹ️  MANUAL", "note": "Test by visiting frontend"}
    except Exception as e:
        results["/api/*"] = {"status": "❌ FAIL", "error": str(e)}

    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📊 Total:  {total_tests}")
    
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! Frontend-backend connection is ready.")
        print(f"🚀 Start both servers:")
        print(f"   cd backend && python main.py")
        print(f"   cd frontend && npm run dev")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check backend server status.")
        
    # Detailed results for debugging
    print(f"\n📋 DETAILED RESULTS:")
    for endpoint, result in results.items():
        status = result["status"]
        if status.startswith("❌"):
            print(f"   {endpoint}: {status} - {result.get('error', 'No details')}")
        elif status.startswith("✅"):
            print(f"   {endpoint}: {status}")
        else:
            print(f"   {endpoint}: {status}")

    return passed_tests, failed_tests, results

if __name__ == "__main__":
    try:
        passed, failed, results = run_comprehensive_test()
        
        # Save results to file
        with open("connection_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "passed": passed,
                "failed": failed,
                "results": results,
                "backend_url": BACKEND_URL,
                "frontend_url": FRONTEND_URL
            }, f, indent=2)
            
        print(f"\n📁 Results saved to: connection_test_results.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test framework error: {e}") 