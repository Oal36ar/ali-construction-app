#!/usr/bin/env python3
"""
Comprehensive Integration Test for FastAPI + LangChain Backend
Tests all major endpoints manually without external test runners

Usage: python tests/test_backend_all.py
"""

import requests
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import time

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

class BackendIntegrationTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        self.uploaded_file_context = None
        
        # Test files paths
        self.test_dir = Path(__file__).parent
        self.sample_pdf = self.test_dir / "sample.pdf"
        self.sample_csv = self.test_dir / "sample.csv"
        
        print(f"🧪 Backend Integration Test")
        print(f"🌐 Target URL: {self.base_url}")
        print(f"📁 Test files directory: {self.test_dir}")
        print(f"=" * 60)
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, details))
        
        if success:
            print(f"{status} {test_name}")
        else:
            print(f"{status} {test_name} - {details}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.RequestException as e:
            print(f"❌ Network error for {method} {endpoint}: {e}")
            return None
    
    def test_health_check(self) -> bool:
        """Test GET /health"""
        print("\n🔍 Testing Health Check...")
        
        response = self.make_request("GET", "/health")
        if not response:
            self.log_test("/health", False, "Network error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Check if response has expected structure
                if "status" in data and "services" in data:
                    self.log_test("/health", True)
                    return True
                else:
                    self.log_test("/health", False, f"Missing expected fields in response")
                    return False
            except json.JSONDecodeError:
                self.log_test("/health", False, "Invalid JSON response")
                return False
        else:
            self.log_test("/health", False, f"Status code: {response.status_code}")
            return False
    
    def test_startup_check(self) -> bool:
        """Test GET /startup-check (must include all_routes_ready: true)"""
        print("\n🚀 Testing Startup Check...")
        
        response = self.make_request("GET", "/startup-check")
        if not response:
            self.log_test("/startup-check", False, "Network error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Must include all_routes_ready: true
                if data.get("all_routes_ready") == True:
                    self.log_test("/startup-check", True)
                    return True
                else:
                    self.log_test("/startup-check", False, f"all_routes_ready: {data.get('all_routes_ready')}")
                    return False
            except json.JSONDecodeError:
                self.log_test("/startup-check", False, "Invalid JSON response")
                return False
        else:
            self.log_test("/startup-check", False, f"Status code: {response.status_code}")
            return False
    
    def test_upload_pdf(self) -> bool:
        """Test POST /upload with PDF file"""
        print("\n📄 Testing Upload PDF...")
        
        if not self.sample_pdf.exists():
            self.log_test("/upload (PDF)", False, "Sample PDF file not found")
            return False
        
        try:
            with open(self.sample_pdf, 'rb') as f:
                files = {'file': ('sample.pdf', f, 'application/pdf')}
                response = self.make_request("POST", "/upload", files=files)
            
            if not response:
                self.log_test("/upload (PDF)", False, "Network error")
                return False
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check for required fields
                    if "filename" in data and "extracted_data" in data:
                        self.uploaded_file_context = f"Previously uploaded: {data['filename']}"
                        self.log_test("/upload (PDF)", True)
                        return True
                    else:
                        self.log_test("/upload (PDF)", False, "Missing required response fields")
                        return False
                except json.JSONDecodeError:
                    self.log_test("/upload (PDF)", False, "Invalid JSON response")
                    return False
            else:
                self.log_test("/upload (PDF)", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/upload (PDF)", False, f"File operation error: {e}")
            return False
    
    def test_upload_csv(self) -> bool:
        """Test POST /upload with CSV file"""
        print("\n📊 Testing Upload CSV...")
        
        if not self.sample_csv.exists():
            self.log_test("/upload (CSV)", False, "Sample CSV file not found")
            return False
        
        try:
            with open(self.sample_csv, 'rb') as f:
                files = {'file': ('sample.csv', f, 'text/csv')}
                response = self.make_request("POST", "/upload", files=files)
            
            if not response:
                self.log_test("/upload (CSV)", False, "Network error")
                return False
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check for required fields
                    if "filename" in data and "extracted_data" in data:
                        if not self.uploaded_file_context:
                            self.uploaded_file_context = f"Previously uploaded: {data['filename']}"
                        self.log_test("/upload (CSV)", True)
                        return True
                    else:
                        self.log_test("/upload (CSV)", False, "Missing required response fields")
                        return False
                except json.JSONDecodeError:
                    self.log_test("/upload (CSV)", False, "Invalid JSON response")
                    return False
            else:
                self.log_test("/upload (CSV)", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("/upload (CSV)", False, f"File operation error: {e}")
            return False
    
    def test_chat_plain(self) -> bool:
        """Test POST /chat with simple message"""
        print("\n💬 Testing Chat (Plain)...")
        
        data = {'message': 'Hello'}
        response = self.make_request("POST", "/chat", data=data)
        
        if not response:
            self.log_test("/chat (plain)", False, "Network error")
            return False
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                # Check for response field
                if "response" in response_data and response_data["response"]:
                    self.log_test("/chat (plain)", True)
                    return True
                else:
                    self.log_test("/chat (plain)", False, "Missing or empty response field")
                    return False
            except json.JSONDecodeError:
                self.log_test("/chat (plain)", False, "Invalid JSON response")
                return False
        else:
            self.log_test("/chat (plain)", False, f"Status code: {response.status_code}")
            return False
    
    def test_chat_contextual(self) -> bool:
        """Test POST /chat with contextual message about uploaded file"""
        print("\n🗨️  Testing Chat (Contextual)...")
        
        message = "Summarize the uploaded file"
        if self.uploaded_file_context:
            message = f"Summarize the construction project details from the uploaded files"
        
        data = {'message': message}
        response = self.make_request("POST", "/chat", data=data)
        
        if not response:
            self.log_test("/chat (context)", False, "Network error")
            return False
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                # Check for response field
                if "response" in response_data and response_data["response"]:
                    self.log_test("/chat (context)", True)
                    return True
                else:
                    self.log_test("/chat (context)", False, "Missing or empty response field")
                    return False
            except json.JSONDecodeError:
                self.log_test("/chat (context)", False, "Invalid JSON response")
                return False
        else:
            self.log_test("/chat (context)", False, f"Status code: {response.status_code}")
            return False
    
    def test_reminders_all(self) -> bool:
        """Test GET /reminders/all"""
        print("\n📋 Testing Reminders...")
        
        response = self.make_request("GET", "/reminders/all")
        
        if not response:
            self.log_test("/reminders/all", False, "Network error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Should return a list (even if empty)
                if isinstance(data, list):
                    self.log_test("/reminders/all", True)
                    return True
                else:
                    self.log_test("/reminders/all", False, f"Expected list, got {type(data)}")
                    return False
            except json.JSONDecodeError:
                self.log_test("/reminders/all", False, "Invalid JSON response")
                return False
        else:
            self.log_test("/reminders/all", False, f"Status code: {response.status_code}")
            return False
    
    def test_history_activity(self) -> bool:
        """Test GET /history/activity"""
        print("\n📚 Testing History...")
        
        response = self.make_request("GET", "/history/activity")
        
        if not response:
            self.log_test("/history/activity", False, "Network error")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Should have summary field and activity arrays
                if "summary" in data and ("recent_chats" in data or "recent_uploads" in data):
                    self.log_test("/history/activity", True)
                    return True
                else:
                    self.log_test("/history/activity", False, "Missing expected fields")
                    return False
            except json.JSONDecodeError:
                self.log_test("/history/activity", False, "Invalid JSON response")
                return False
        else:
            self.log_test("/history/activity", False, f"Status code: {response.status_code}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print(f"🚀 Starting comprehensive backend integration tests...\n")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Startup Check", self.test_startup_check), 
            ("Upload PDF", self.test_upload_pdf),
            ("Upload CSV", self.test_upload_csv),
            ("Chat Plain", self.test_chat_plain),
            ("Chat Contextual", self.test_chat_contextual),
            ("Reminders", self.test_reminders_all),
            ("History", self.test_history_activity),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                # Small delay between tests
                time.sleep(0.5)
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected error: {e}")
        
        # Print summary
        print(f"\n" + "=" * 60)
        print(f"🧪 TEST SUMMARY")
        print(f"=" * 60)
        
        for test_name, success, details in self.test_results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}")
            if not success and details:
                print(f"   └─ {details}")
        
        print(f"\n📊 RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print(f"🎉 ALL TESTS PASSED")
            return True
        else:
            failed_count = total_tests - passed_tests
            print(f"⚠️  {failed_count} test(s) failed")
            return False

def check_backend_running(base_url: str) -> bool:
    """Check if backend is running"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test execution"""
    base_url = "http://localhost:8000"
    
    # Check if backend is running
    print(f"🔍 Checking if backend is running at {base_url}...")
    if not check_backend_running(base_url):
        print(f"❌ Backend not accessible at {base_url}")
        print(f"💡 Make sure to start the backend first:")
        print(f"   cd backend")
        print(f"   python main.py")
        sys.exit(1)
    
    print(f"✅ Backend is running!")
    
    # Run tests
    tester = BackendIntegrationTest(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 