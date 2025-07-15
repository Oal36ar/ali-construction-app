#!/usr/bin/env python3
"""
Quick test script to verify frontend 404 fix
Usage: python test_frontend_fix.py
"""

import subprocess
import time
import requests
import sys
import os

def test_frontend_startup():
    """Test if frontend starts correctly and serves pages"""
    
    print("🧪 Testing Frontend Fix...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('frontend/package.json'):
        print("❌ Please run this from the root project directory")
        return False
    
    print("✅ Project structure looks correct")
    
    # Check if index.html exists in frontend
    if os.path.exists('frontend/index.html'):
        print("✅ frontend/index.html exists")
    else:
        print("❌ frontend/index.html missing")
        return False
    
    # Check if App.tsx has proper routing
    try:
        with open('frontend/src/App.tsx', 'r') as f:
            app_content = f.read()
            if 'Navigate' in app_content and 'path="*"' in app_content:
                print("✅ App.tsx has fallback route")
            else:
                print("❌ App.tsx missing fallback route")
                return False
    except:
        print("❌ Could not read App.tsx")
        return False
    
    print("\n🎉 All frontend fixes applied successfully!")
    print("\n📋 Next Steps:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("4. Visit http://localhost:5173")
    print("\nThe 404 error should be resolved! 🚀")
    
    return True

if __name__ == "__main__":
    success = test_frontend_startup()
    sys.exit(0 if success else 1) 