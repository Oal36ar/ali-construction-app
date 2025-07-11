#!/usr/bin/env python3
"""
End-to-End Integration Validation Script
Tests all frontend-backend integrations

Usage: python validate_integration.py
"""

import requests
import json
import time
import sys
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class IntegrationValidator:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if success else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
        self.test_results.append((test_name, success, details, response_data))
        
        if success:
            print(f"{status} {test_name}")
            if details:
                print(f"    └─ {Colors.CYAN}{details}{Colors.ENDC}")
        else:
            print(f"{status} {test_name}")
            if details:
                print(f"    └─ {Colors.YELLOW}{details}{Colors.ENDC}")

    def test_backend_health(self):
        """Test backend health endpoint"""
        print(f"\n{Colors.BLUE}🔍 Testing Backend Health...{Colors.ENDC}")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                services = data.get('services', {})
                self.log_test(
                    "Backend Health Check", 
                    True, 
                    f"Status: {status}, Services: {list(services.keys())}",
                    data
                )
                return True
            else:
                self.log_test("Backend Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False

    def test_backend_startup(self):
        """Test backend startup check"""
        try:
            response = requests.get(f"{self.backend_url}/startup-check", timeout=10)
            if response.status_code == 200:
                data = response.json()
                all_routes_ready = data.get('all_routes_ready', False)
                routes_loaded = data.get('routes_loaded', [])
                self.log_test(
                    "Backend Startup Check", 
                    all_routes_ready, 
                    f"Routes loaded: {routes_loaded}",
                    data
                )
                return all_routes_ready
            else:
                self.log_test("Backend Startup Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Startup Check", False, str(e))
            return False

    def test_chat_endpoint(self):
        """Test chat endpoint"""
        print(f"\n{Colors.BLUE}💬 Testing Chat Endpoint...{Colors.ENDC}")
        
        try:
            # Test simple chat
            data = {'message': 'Hello, this is a test message'}
            response = requests.post(f"{self.backend_url}/chat", data=data, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                chat_response = response_data.get('response', '')
                model = response_data.get('model', 'unknown')
                success_flag = response_data.get('success', False)
                
                self.log_test(
                    "Chat Endpoint (Plain)", 
                    True and len(chat_response) > 0, 
                    f"Response length: {len(chat_response)}, Model: {model}",
                    response_data
                )
                return True
            else:
                self.log_test("Chat Endpoint (Plain)", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Endpoint (Plain)", False, str(e))
            return False

    def test_upload_endpoint(self):
        """Test file upload endpoint"""
        print(f"\n{Colors.BLUE}📁 Testing Upload Endpoint...{Colors.ENDC}")
        
        try:
            # Create a test file
            test_content = """CONSTRUCTION PROJECT REPORT
Project: Test Building
Date: 2024-01-15
Status: In Progress
Budget: $50,000
Tasks:
- Foundation: Complete
- Framing: In Progress
- Electrical: Pending
"""
            
            files = {'file': ('test_construction.txt', test_content, 'text/plain')}
            response = requests.post(f"{self.backend_url}/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                filename = data.get('filename', '')
                file_type = data.get('file_type', '')
                extracted_data = data.get('extracted_data', {})
                
                self.log_test(
                    "File Upload", 
                    True, 
                    f"File: {filename}, Type: {file_type}, Size: {extracted_data.get('size', 0)} bytes",
                    data
                )
                return True
            else:
                self.log_test("File Upload", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("File Upload", False, str(e))
            return False

    def test_reminders_endpoint(self):
        """Test reminders endpoint"""
        print(f"\n{Colors.BLUE}📅 Testing Reminders Endpoint...{Colors.ENDC}")
        
        try:
            response = requests.get(f"{self.backend_url}/reminders/all", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                reminder_count = len(data) if isinstance(data, list) else 0
                
                self.log_test(
                    "Reminders Endpoint", 
                    True, 
                    f"Found {reminder_count} reminders",
                    {"reminder_count": reminder_count, "reminders": data[:3] if reminder_count > 3 else data}
                )
                return True
            else:
                self.log_test("Reminders Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Reminders Endpoint", False, str(e))
            return False

    def test_history_endpoint(self):
        """Test history endpoint"""
        print(f"\n{Colors.BLUE}📊 Testing History Endpoint...{Colors.ENDC}")
        
        try:
            response = requests.get(f"{self.backend_url}/history/activity", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get('summary', {})
                total_chats = summary.get('total_chats', 0)
                total_uploads = summary.get('total_uploads', 0)
                
                self.log_test(
                    "History Endpoint", 
                    True, 
                    f"Chats: {total_chats}, Uploads: {total_uploads}",
                    summary
                )
                return True
            else:
                self.log_test("History Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("History Endpoint", False, str(e))
            return False

    def test_frontend_accessibility(self):
        """Test frontend accessibility"""
        print(f"\n{Colors.BLUE}🌐 Testing Frontend...{Colors.ENDC}")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                # Check if it's a proper HTML page
                content = response.text
                is_html = '<html' in content.lower() and '</html>' in content.lower()
                has_react = 'react' in content.lower() or 'vite' in content.lower()
                
                self.log_test(
                    "Frontend Accessibility", 
                    is_html, 
                    f"HTML page: {is_html}, React/Vite detected: {has_react}",
                    {"content_length": len(content), "is_html": is_html}
                )
                return is_html
            else:
                self.log_test("Frontend Accessibility", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", False, str(e))
            return False

    def test_frontend_proxy(self):
        """Test frontend proxy to backend"""
        print(f"\n{Colors.BLUE}🔗 Testing Frontend-Backend Proxy...{Colors.ENDC}")
        
        try:
            # Test proxy by calling backend through frontend
            response = requests.get(f"{self.frontend_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                self.log_test(
                    "Frontend Proxy", 
                    True, 
                    f"Proxy working, backend status: {status}",
                    data
                )
                return True
            else:
                self.log_test("Frontend Proxy", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Proxy", False, str(e))
            return False

    def test_contextual_chat(self):
        """Test chat with context (after file upload)"""
        print(f"\n{Colors.BLUE}🗨️  Testing Contextual Chat...{Colors.ENDC}")
        
        try:
            # First upload a file for context
            test_content = """CONSTRUCTION SCHEDULE
Phase 1: Site Preparation (Week 1-2)
Phase 2: Foundation (Week 3-4) 
Phase 3: Framing (Week 5-7)
Phase 4: Electrical & Plumbing (Week 8-9)
Phase 5: Finishing (Week 10-12)
Total Budget: $75,000
Project Manager: John Smith
"""
            
            files = {'file': ('schedule.txt', test_content, 'text/plain')}
            upload_response = requests.post(f"{self.backend_url}/upload", files=files, timeout=30)
            
            if upload_response.status_code == 200:
                # Now test contextual chat
                time.sleep(1)  # Brief pause
                
                data = {'message': 'Summarize the construction project schedule and budget'}
                chat_response = requests.post(f"{self.backend_url}/chat", data=data, timeout=30)
                
                if chat_response.status_code == 200:
                    response_data = chat_response.json()
                    chat_text = response_data.get('response', '')
                    
                    # Check if response includes context from uploaded file
                    has_context = any(word in chat_text.lower() for word in ['construction', 'schedule', 'budget', 'phase', 'week'])
                    
                    self.log_test(
                        "Contextual Chat", 
                        has_context, 
                        f"Response includes file context: {has_context}",
                        {"response_length": len(chat_text), "has_context": has_context}
                    )
                    return has_context
                else:
                    self.log_test("Contextual Chat", False, f"Chat HTTP {chat_response.status_code}")
                    return False
            else:
                self.log_test("Contextual Chat", False, f"Upload HTTP {upload_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Contextual Chat", False, str(e))
            return False

    def run_validation(self):
        """Run all validation tests"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}   🧪 END-TO-END INTEGRATION VALIDATION   {Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        # Run all tests
        tests = [
            ("Backend Services", [
                self.test_backend_health,
                self.test_backend_startup,
                self.test_chat_endpoint,
                self.test_upload_endpoint,
                self.test_reminders_endpoint,
                self.test_history_endpoint
            ]),
            ("Frontend & Integration", [
                self.test_frontend_accessibility,
                self.test_frontend_proxy,
                self.test_contextual_chat
            ])
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for category, test_functions in tests:
            print(f"\n{Colors.CYAN}{'='*30} {category} {'='*30}{Colors.ENDC}")
            
            for test_func in test_functions:
                try:
                    result = test_func()
                    total_tests += 1
                    if result:
                        passed_tests += 1
                    time.sleep(0.5)  # Small delay between tests
                except Exception as e:
                    print(f"{Colors.RED}❌ Test error: {str(e)}{Colors.ENDC}")
                    total_tests += 1

        # Print summary
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}   📊 VALIDATION SUMMARY   {Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        for test_name, success, details, _ in self.test_results:
            status = f"{Colors.GREEN}✅{Colors.ENDC}" if success else f"{Colors.RED}❌{Colors.ENDC}"
            print(f"{status} {test_name}")
            if not success and details:
                print(f"   └─ {Colors.YELLOW}{details}{Colors.ENDC}")

        print(f"\n{Colors.CYAN}Results: {passed_tests}/{total_tests} tests passed{Colors.ENDC}")
        
        if passed_tests == total_tests:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED - INTEGRATION SUCCESSFUL!{Colors.ENDC}")
            print(f"{Colors.GREEN}✨ Your full-stack application is working perfectly!{Colors.ENDC}")
            return True
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  MOSTLY WORKING - Some non-critical issues{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Check the failed tests above for details{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ INTEGRATION ISSUES DETECTED{Colors.ENDC}")
            print(f"{Colors.RED}🔧 Please check the failed tests and fix the issues{Colors.ENDC}")
            return False

def main():
    """Main validation function"""
    print(f"{Colors.CYAN}🔍 Checking if services are running...{Colors.ENDC}")
    
    validator = IntegrationValidator()
    
    # Quick check if services are up
    try:
        backend_check = requests.get(f"{validator.backend_url}/health", timeout=5)
        frontend_check = requests.get(f"{validator.frontend_url}", timeout=5)
        
        if backend_check.status_code != 200:
            print(f"{Colors.RED}❌ Backend not accessible at {validator.backend_url}{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Start backend with: cd backend && python main.py{Colors.ENDC}")
            sys.exit(1)
            
        if frontend_check.status_code != 200:
            print(f"{Colors.RED}❌ Frontend not accessible at {validator.frontend_url}{Colors.ENDC}")
            print(f"{Colors.YELLOW}💡 Start frontend with: cd frontend && npm run dev{Colors.ENDC}")
            sys.exit(1)
            
        print(f"{Colors.GREEN}✅ Both services are running!{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error checking services: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}💡 Make sure both backend and frontend are running{Colors.ENDC}")
        sys.exit(1)
    
    # Run full validation
    success = validator.run_validation()
    
    if success:
        print(f"\n{Colors.GREEN}🚀 Ready for development/testing!{Colors.ENDC}")
        print(f"{Colors.CYAN}Frontend: {validator.frontend_url}{Colors.ENDC}")
        print(f"{Colors.CYAN}Backend:  {validator.backend_url}{Colors.ENDC}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 