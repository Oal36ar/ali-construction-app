#!/usr/bin/env python3
"""
Complete Route Testing Script
Tests all FastAPI routes after route registration fixes
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
                if isinstance(data, dict):
                    # For form data
                    response = requests.post(url, data=data, timeout=30)
                else:
                    # For JSON data
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
                "response": response.text[:300]
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "❌ FAIL",
            "error": str(e)
        }

def test_frontend_proxy(endpoint, method="GET", data=None):
    """Test endpoint through frontend proxy"""
    url = f"{FRONTEND_URL}/api{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            if isinstance(data, dict):
                response = requests.post(url, data=data, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
        
        return {
            "status": "✅ PROXY OK" if response.status_code < 500 else "❌ PROXY FAIL",
            "response_time": f"{response.elapsed.total_seconds():.3f}s",
            "status_code": response.status_code
        }
    except Exception as e:
        return {
            "status": "❌ PROXY FAIL",
            "error": str(e)
        }

def run_comprehensive_route_test():
    """Run comprehensive test of all routes after fixes"""
    print("🔧 COMPLETE ROUTE TESTING AFTER FIXES")
    print("=" * 70)
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # First test the new startup-check endpoint
    print(f"\n📋 === STARTUP CHECK ===")
    startup_result = test_endpoint("GET", "/startup-check")
    if startup_result["status"].startswith("✅"):
        startup_data = startup_result["data"]
        print(f"✅ Startup Check: {startup_data['status']}")
        print(f"📊 Routes Loaded: {startup_data['routes_loaded']}")
        print(f"📊 Missing Routes: {startup_data['missing_routes']}")
        print(f"📊 All Routes Ready: {startup_data['all_routes_ready']}")
    else:
        print(f"❌ Startup Check Failed: {startup_result['error']}")

    # Test all critical route categories
    tests = [
        # Core status endpoints
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/status", "Status endpoint"),
        ("GET", "/startup-check", "Startup check (NEW)"),
        
        # Chat endpoints
        ("POST", "/chat", "Chat endpoint", {"message": "Hello, route test!"}),
        ("GET", "/tools/available", "Available tools"),
        
        # File upload endpoint  
        ("POST", "/upload/", "File upload", None, {"test_file": ("test.txt", "Route test content", "text/plain")}),
        
        # Reminder endpoints
        ("GET", "/reminders/all", "Get all reminders"),
        ("POST", "/reminders/", "Create reminder", {
            "title": "Route Test Reminder",
            "date": "2024-12-31",
            "time": "09:00",
            "description": "Created by route test script",
            "priority": "medium",
            "category": "test"
        }),
        
        # History endpoints
        ("GET", "/history/activity", "Activity history"),
        
        # Confirmation endpoint
        ("POST", "/confirm/", "Confirm action", {
            "decision": "yes",
            "session_id": "route_test_session"
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
        print(f"         {method} {endpoint}")
        
        # Test direct backend
        result = test_endpoint(method, endpoint, data, files)
        results[endpoint] = result
        
        if result["status"].startswith("✅"):
            passed_tests += 1
            print(f"         {result['status']} ({result.get('response_time', 'N/A')})")
            
            # Test through frontend proxy if backend works
            if endpoint in ["/status", "/startup-check", "/chat", "/reminders/all"]:
                proxy_result = test_frontend_proxy(endpoint, method, data)
                print(f"         Proxy: {proxy_result['status']} ({proxy_result.get('response_time', 'N/A')})")
        else:
            failed_tests += 1
            print(f"         {result['status']} - {result.get('error', 'Unknown error')}")

    # Test docs endpoint
    print(f"\n[{total_tests + 1}] Testing API Documentation")
    docs_result = test_endpoint("GET", "/docs")
    if docs_result["status"].startswith("✅"):
        print(f"         ✅ API Docs available at {BACKEND_URL}/docs")
    else:
        print(f"         ❌ API Docs not accessible")

    # Summary
    print("\n" + "=" * 70)
    print("🎯 ROUTE TEST SUMMARY")
    print("=" * 70)
    
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📊 Total:  {total_tests}")
    
    if failed_tests == 0:
        print(f"\n🎉 ALL ROUTES WORKING! Full frontend-backend connectivity achieved.")
        print(f"🚀 Ready for production:")
        print(f"   Backend: {BACKEND_URL}")
        print(f"   Frontend: {FRONTEND_URL}")
        print(f"   API Docs: {BACKEND_URL}/docs")
    else:
        print(f"\n⚠️  {failed_tests} route(s) still failing. Check error details above.")

    # Detailed results for debugging
    print(f"\n📋 DETAILED RESULTS:")
    for endpoint, result in results.items():
        status = result["status"]
        if status.startswith("❌"):
            print(f"   {endpoint}: {status} - {result.get('error', 'No details')}")
            if 'response' in result:
                print(f"      Response: {result['response'][:100]}...")
        elif status.startswith("✅"):
            print(f"   {endpoint}: {status}")

    return passed_tests, failed_tests, results

def quick_frontend_test():
    """Quick test of frontend proxy functionality"""
    print(f"\n🌐 FRONTEND PROXY TEST")
    print("=" * 40)
    
    proxy_tests = [
        ("/status", "GET"),
        ("/startup-check", "GET"),
        ("/reminders/all", "GET")
    ]
    
    for endpoint, method in proxy_tests:
        result = test_frontend_proxy(endpoint, method)
        print(f"  {method} /api{endpoint}: {result['status']}")

if __name__ == "__main__":
    try:
        passed, failed, results = run_comprehensive_route_test()
        
        # Quick frontend proxy test
        quick_frontend_test()
        
        # Save results to file
        with open("route_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "passed": passed,
                "failed": failed,
                "results": results,
                "backend_url": BACKEND_URL,
                "frontend_url": FRONTEND_URL
            }, f, indent=2)
            
        print(f"\n📁 Results saved to: route_test_results.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test framework error: {e}") 