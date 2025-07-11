#!/usr/bin/env python3
"""
Production Startup Script for LangChain + FastAPI Backend
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the backend in production mode"""
    print("🚀 Starting LangChain + FastAPI Backend")
    print("=" * 50)
    
    # Set production environment
    os.environ["ENVIRONMENT"] = "production"
    
    # Ensure we're in the right directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    try:
        # Import and start the app
        from main import app
        
        print("✅ Backend loaded successfully")
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API docs available at http://localhost:8000/docs")
        print("🔄 Health check: http://localhost:8000/health")
        print("=" * 50)
        
        # Start with production settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False  # Disabled for production
        )
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        print("Check your .env file and dependencies")
        sys.exit(1)

if __name__ == "__main__":
    main()
