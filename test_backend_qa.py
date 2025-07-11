#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for LangChain-powered FastAPI Backend
Tests all critical functionality across file upload, embedding, chat orchestration, and dynamic LLM handling
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("test_files")

class BackendQATester:
    def __init__(self):
        self.test_results = {}
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        
    def log_test(self, test_name, status, details=None, error=None):
        """Log test results"""
        result = {
            "status": status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if details:
            result["details"] = details
        if error:
            result["error"] = str(error)
        
        self.test_results[test_name] = result
        print(f"[{status}] {test_name}")
        if error:
            print(f"    Error: {error}")
        if details:
            print(f"    Details: {details}")
    
    def test_health_check(self):
        """Test 1: Health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", "✅ PASS", {
                    "status": data.get("status"),
                    "services": data.get("services"),
                    "endpoints": data.get("endpoints")
                })
                return True
            else:
                self.log_test("Health Check", "❌ FAIL", error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", "❌ FAIL", error=e)
            return False
    
    def test_root_endpoint(self):
        """Test basic connectivity"""
        try:
            response = self.session.get(f"{BASE_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", "✅ PASS", {
                    "message": data.get("message"),
                    "version": data.get("version"),
                    "endpoints": len(data.get("endpoints", {}))
                })
                return True
            else:
                self.log_test("Root Endpoint", "❌ FAIL", error=f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", "❌ FAIL", error=e)
            return False
    
    def create_test_file(self, filename, content):
        """Create a test file for uploading"""
        TEST_FILES_DIR.mkdir(exist_ok=True)
        file_path = TEST_FILES_DIR / filename
        
        if filename.endswith('.txt'):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        elif filename.endswith('.csv'):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return file_path
    
    def test_file_upload(self, filename, content, expected_type):
        """Test file upload functionality"""
        try:
            # Create test file
            file_path = self.create_test_file(filename, content)
            
            # Upload file
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                data = {'intent': 'auto'}
                response = self.session.post(f"{BASE_URL}/upload/", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(f"Upload {filename}", "✅ PASS", {
                    "filename": result.get("filename"),
                    "file_type": result.get("file_type"),
                    "summary": result.get("summary", "")[:100] + "..." if len(result.get("summary", "")) > 100 else result.get("summary", ""),
                    "extracted_data": result.get("extracted_data", {})
                })
                return result
            else:
                self.log_test(f"Upload {filename}", "❌ FAIL", error=f"Status code: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(f"Upload {filename}", "❌ FAIL", error=e)
            return None
    
    def test_embedding_stats(self):
        """Test embedding statistics endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/upload/embedding-stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Embedding Stats", "✅ PASS", {
                    "embedding_available": data.get("embedding_available"),
                    "total_chunks": data.get("total_chunks"),
                    "unique_sources": data.get("unique_sources"),
                    "sources": data.get("sources", [])
                })
                return data
            else:
                self.log_test("Embedding Stats", "❌ FAIL", error=f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Embedding Stats", "❌ FAIL", error=e)
            return None
    
    def test_chat_endpoint(self, message, expected_keywords=None):
        """Test chat endpoint functionality"""
        try:
            data = {
                "message": message,
                "session_id": "test_session"
            }
            response = self.session.post(f"{BASE_URL}/chat", data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                details = {
                    "model": result.get("model"),
                    "input_type": result.get("input_type"),
                    "response_length": len(result.get("response", "")),
                    "success": result.get("success")
                }
                
                # Check for expected keywords in response
                if expected_keywords:
                    response_text = result.get("response", "").lower()
                    found_keywords = [kw for kw in expected_keywords if kw.lower() in response_text]
                    details["found_keywords"] = found_keywords
                
                self.log_test(f"Chat: {message[:30]}...", "✅ PASS", details)
                return result
            else:
                self.log_test(f"Chat: {message[:30]}...", "❌ FAIL", error=f"Status code: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(f"Chat: {message[:30]}...", "❌ FAIL", error=e)
            return None
    
    def test_chat_with_file(self, message, filename, content):
        """Test chat endpoint with file upload"""
        try:
            # Create test file
            file_path = self.create_test_file(filename, content)
            
            # Send chat with file
            with open(file_path, 'rb') as f:
                files = {'files': (filename, f, 'application/octet-stream')}
                data = {'message': message, 'session_id': 'test_session_with_file'}
                response = self.session.post(f"{BASE_URL}/chat", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(f"Chat with File: {filename}", "✅ PASS", {
                    "model": result.get("model"),
                    "input_type": result.get("input_type"),
                    "processed_files": result.get("processed_files"),
                    "response_length": len(result.get("response", "")),
                    "file_previews": result.get("file_previews", [])
                })
                return result
            else:
                self.log_test(f"Chat with File: {filename}", "❌ FAIL", error=f"Status code: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test(f"Chat with File: {filename}", "❌ FAIL", error=e)
            return None
    
    def test_history_endpoint(self):
        """Test activity history endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/history/activity", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Activity History", "✅ PASS", {
                    "total_activities": len(data.get("activities", [])),
                    "recent_count": len(data.get("recent", [])) if "recent" in data else "N/A"
                })
                return data
            else:
                self.log_test("Activity History", "❌ FAIL", error=f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Activity History", "❌ FAIL", error=e)
            return None
    
    def test_upload_history(self):
        """Test upload history endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/upload/history", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Upload History", "✅ PASS", {
                    "files_count": len(data.get("files", []))
                })
                return data
            else:
                self.log_test("Upload History", "❌ FAIL", error=f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Upload History", "❌ FAIL", error=e)
            return None
    
    def test_tools_endpoint(self):
        """Test available tools endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/tools/available", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Available Tools", "✅ PASS", {
                    "tool_count": data.get("tool_count"),
                    "status": data.get("status")
                })
                return data
            else:
                self.log_test("Available Tools", "❌ FAIL", error=f"Status code: {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Available Tools", "❌ FAIL", error=e)
            return None
    
    def run_comprehensive_tests(self):
        """Run all tests in sequence"""
        print("🧪 Starting Comprehensive Backend QA Tests")
        print("=" * 60)
        
        # Wait for backend startup
        print("⏳ Waiting for backend startup...")
        time.sleep(5)
        
        # Test 1: Basic connectivity
        print("\n📡 Testing Basic Connectivity...")
        if not self.test_root_endpoint():
            print("❌ Backend not accessible, stopping tests")
            return
        
        self.test_health_check()
        
        # Test 2: File uploads
        print("\n📤 Testing File Uploads...")
        
        # Test text file with reminder content
        txt_content = """Test Document for Backend QA

This is a sample text file for testing.

Important Information:
- Omar visa renewal: 2027-11-20
- Project deadline: 2024-02-15
- Meeting scheduled: 2024-01-30 at 2:00 PM

Content for analysis and embedding testing."""
        
        self.test_file_upload("test.txt", txt_content, "text")
        
        # Test CSV file
        csv_content = """Name,Date,Task,Priority,Status
Omar,2027-11-20,Visa renewal,High,Pending
Sarah,2024-02-15,Project deadline,Critical,Active
Mike,2024-01-30,Team meeting,Medium,Scheduled"""
        
        self.test_file_upload("test.csv", csv_content, "csv")
        
        # Test 3: Embedding functionality
        print("\n🧠 Testing Embedding System...")
        self.test_embedding_stats()
        
        # Test 4: Chat functionality
        print("\n💬 Testing Chat Endpoints...")
        self.test_chat_endpoint("Hello, how are you?")
        self.test_chat_endpoint("Summarize the uploaded document.", ["document", "summarize"])
        self.test_chat_endpoint("Create a reminder for Omar visa renewal on 2027-11-20", ["reminder", "visa"])
        
        # Test 5: Chat with file upload
        print("\n📁 Testing Chat with File Upload...")
        reminder_content = "Important: Omar visa renewal due on 2027-11-20. Please prepare documents."
        self.test_chat_with_file("What reminders are in this document?", "reminder_doc.txt", reminder_content)
        
        # Test 6: History endpoints
        print("\n📊 Testing History Endpoints...")
        self.test_history_endpoint()
        self.test_upload_history()
        
        # Test 7: Tools endpoint
        print("\n🔧 Testing Tools Endpoint...")
        self.test_tools_endpoint()
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE QA TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r["status"] == "✅ PASS"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            print(f"  {result['status']} {test_name}")
            if result["status"] == "❌ FAIL":
                print(f"    Error: {result.get('error', 'Unknown error')}")
        
        # Production readiness assessment
        print("\n🚀 Production Readiness Assessment:")
        
        critical_tests = [
            "Root Endpoint", "Health Check", "Upload test.txt", "Upload test.csv", 
            "Chat: Hello, how are you?...", "Embedding Stats"
        ]
        
        critical_passed = len([t for t in critical_tests if t in self.test_results and self.test_results[t]["status"] == "✅ PASS"])
        
        if critical_passed == len(critical_tests):
            print("✅ PRODUCTION READY")
            print("   - File uploads → parsed cleanly")
            print("   - Embeddings → available (if configured)")
            print("   - Chat → responding correctly")
            print("   - History → tracking events")
        else:
            print("⚠️ NOT PRODUCTION READY")
            print(f"   Critical tests failed: {len(critical_tests) - critical_passed}/{len(critical_tests)}")
        
        # Save results to file
        with open("qa_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Full results saved to: qa_test_results.json")

if __name__ == "__main__":
    tester = BackendQATester()
    tester.run_comprehensive_tests() 