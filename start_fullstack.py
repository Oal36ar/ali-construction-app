#!/usr/bin/env python3
"""
Full-Stack Startup Script for Construction AI App
Starts both backend (FastAPI) and frontend (Vite) services

Usage: python start_fullstack.py
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path
import signal
import threading
import webbrowser

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class FullStackLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_port = 8000
        self.frontend_port = 5173
        
    def print_banner(self):
        """Print startup banner"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}   🏗️  CONSTRUCTION AI - FULL STACK LAUNCHER   {Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.CYAN}Backend:{Colors.ENDC} FastAPI + LangChain + OpenRouter")
        print(f"{Colors.CYAN}Frontend:{Colors.ENDC} React + Vite + TailwindCSS")
        print(f"{Colors.CYAN}Features:{Colors.ENDC} File Upload, Chat, Reminders, History")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

    def check_requirements(self):
        """Check if required tools are available"""
        print(f"{Colors.YELLOW}🔍 Checking requirements...{Colors.ENDC}")
        
        # Check Python
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print(f"{Colors.RED}❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}{Colors.ENDC}")
            return False
        print(f"{Colors.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}{Colors.ENDC}")
        
        # Check if backend directory exists
        if not os.path.exists('backend'):
            print(f"{Colors.RED}❌ Backend directory not found{Colors.ENDC}")
            return False
        print(f"{Colors.GREEN}✅ Backend directory found{Colors.ENDC}")
        
        # Check if frontend directory exists
        if not os.path.exists('frontend'):
            print(f"{Colors.RED}❌ Frontend directory not found{Colors.ENDC}")
            return False
        print(f"{Colors.GREEN}✅ Frontend directory found{Colors.ENDC}")
        
        # Check if package.json exists
        if not os.path.exists('frontend/package.json'):
            print(f"{Colors.RED}❌ Frontend package.json not found{Colors.ENDC}")
            return False
        print(f"{Colors.GREEN}✅ Frontend package.json found{Colors.ENDC}")
        
        # Check Node.js/npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ npm {result.stdout.strip()}{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ npm not found or not working{Colors.ENDC}")
                return False
        except FileNotFoundError:
            print(f"{Colors.RED}❌ npm not found - please install Node.js{Colors.ENDC}")
            return False
        
        print(f"{Colors.GREEN}✅ All requirements met{Colors.ENDC}\n")
        return True

    def check_port_available(self, port):
        """Check if a port is available"""
        try:
            response = requests.get(f'http://localhost:{port}', timeout=2)
            return False  # Port is occupied
        except (requests.ConnectionError, requests.Timeout):
            return True  # Port is available

    def wait_for_backend(self, timeout=60):
        """Wait for backend to be ready"""
        print(f"{Colors.YELLOW}⏳ Waiting for backend to start...{Colors.ENDC}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f'http://localhost:{self.backend_port}/health', timeout=2)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✅ Backend is ready!{Colors.ENDC}")
                    return True
            except (requests.ConnectionError, requests.Timeout):
                time.sleep(2)
                print(".", end="", flush=True)
        
        print(f"\n{Colors.RED}❌ Backend failed to start within {timeout} seconds{Colors.ENDC}")
        return False

    def wait_for_frontend(self, timeout=30):
        """Wait for frontend to be ready"""
        print(f"{Colors.YELLOW}⏳ Waiting for frontend to start...{Colors.ENDC}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f'http://localhost:{self.frontend_port}', timeout=2)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✅ Frontend is ready!{Colors.ENDC}")
                    return True
            except (requests.ConnectionError, requests.Timeout):
                time.sleep(1)
                print(".", end="", flush=True)
        
        print(f"\n{Colors.RED}❌ Frontend failed to start within {timeout} seconds{Colors.ENDC}")
        return False

    def start_backend(self):
        """Start the FastAPI backend"""
        print(f"{Colors.BLUE}🚀 Starting backend (FastAPI + LangChain)...{Colors.ENDC}")
        
        try:
            # Change to backend directory and start
            self.backend_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                cwd='backend',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"{Colors.GREEN}✅ Backend process started (PID: {self.backend_process.pid}){Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start backend: {e}{Colors.ENDC}")
            return False

    def start_frontend(self):
        """Start the Vite frontend"""
        print(f"{Colors.BLUE}🚀 Starting frontend (React + Vite)...{Colors.ENDC}")
        
        try:
            # Install dependencies first
            print(f"{Colors.YELLOW}📦 Installing frontend dependencies...{Colors.ENDC}")
            install_result = subprocess.run(
                ['npm', 'install'],
                cwd='frontend',
                capture_output=True,
                text=True
            )
            
            if install_result.returncode != 0:
                print(f"{Colors.YELLOW}⚠️ npm install had issues, continuing anyway...{Colors.ENDC}")
            
            # Start frontend
            self.frontend_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd='frontend',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"{Colors.GREEN}✅ Frontend process started (PID: {self.frontend_process.pid}){Colors.ENDC}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start frontend: {e}{Colors.ENDC}")
            return False

    def test_integration(self):
        """Test the integration between frontend and backend"""
        print(f"\n{Colors.YELLOW}🧪 Testing integration...{Colors.ENDC}")
        
        tests = [
            ("Backend Health", f"http://localhost:{self.backend_port}/health"),
            ("Backend Startup", f"http://localhost:{self.backend_port}/startup-check"),
            ("Frontend", f"http://localhost:{self.frontend_port}"),
        ]
        
        all_passed = True
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✅ {test_name}: OK{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}❌ {test_name}: HTTP {response.status_code}{Colors.ENDC}")
                    all_passed = False
            except Exception as e:
                print(f"{Colors.RED}❌ {test_name}: {str(e)}{Colors.ENDC}")
                all_passed = False
        
        if all_passed:
            print(f"\n{Colors.GREEN}🎉 All integration tests passed!{Colors.ENDC}")
        else:
            print(f"\n{Colors.YELLOW}⚠️ Some tests failed, but services may still work{Colors.ENDC}")
        
        return all_passed

    def print_status(self):
        """Print current status and URLs"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}   🎯 APPLICATION READY   {Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.CYAN}Frontend:{Colors.ENDC} {Colors.BOLD}http://localhost:{self.frontend_port}{Colors.ENDC}")
        print(f"{Colors.CYAN}Backend:{Colors.ENDC}  {Colors.BOLD}http://localhost:{self.backend_port}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.GREEN}✨ Features Available:{Colors.ENDC}")
        print(f"   • 📁 File Upload (PDF, CSV, DOCX, XLSX)")
        print(f"   • 💬 AI Chat with File Context") 
        print(f"   • 📅 Reminders Management")
        print(f"   • 📊 Activity History")
        print(f"   • 🔗 Real-time Backend Integration")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop both services{Colors.ENDC}\n")

    def cleanup(self, signal_num=None, frame=None):
        """Clean up processes"""
        print(f"\n{Colors.YELLOW}🛑 Shutting down services...{Colors.ENDC}")
        
        if self.backend_process:
            print(f"{Colors.BLUE}🔌 Stopping backend...{Colors.ENDC}")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print(f"{Colors.BLUE}🔌 Stopping frontend...{Colors.ENDC}")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print(f"{Colors.GREEN}✅ All services stopped{Colors.ENDC}")
        sys.exit(0)

    def run(self):
        """Main run method"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        self.print_banner()
        
        # Check requirements
        if not self.check_requirements():
            sys.exit(1)
        
        # Start backend
        if not self.start_backend():
            sys.exit(1)
        
        # Wait for backend to be ready
        if not self.wait_for_backend():
            self.cleanup()
            sys.exit(1)
        
        # Start frontend  
        if not self.start_frontend():
            self.cleanup()
            sys.exit(1)
        
        # Wait for frontend to be ready
        if not self.wait_for_frontend():
            self.cleanup()
            sys.exit(1)
        
        # Test integration
        self.test_integration()
        
        # Print status
        self.print_status()
        
        # Open browser
        try:
            webbrowser.open(f'http://localhost:{self.frontend_port}')
        except:
            pass
        
        # Keep running until interrupted
        try:
            while True:
                if self.backend_process and self.backend_process.poll() is not None:
                    print(f"{Colors.RED}❌ Backend process died{Colors.ENDC}")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print(f"{Colors.RED}❌ Frontend process died{Colors.ENDC}")
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.cleanup()

if __name__ == "__main__":
    launcher = FullStackLauncher()
    launcher.run() 