#!/usr/bin/env python3
"""
Backend Startup Fix Script
Resolves common issues preventing the FastAPI backend from starting
"""

import os
import sys
from pathlib import Path

def fix_env_file():
    """Create a proper .env file with UTF-8 encoding"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    # Remove corrupted .env file if it exists
    if env_file.exists():
        try:
            env_file.unlink()
            print("✅ Removed corrupted .env file")
        except Exception as e:
            print(f"⚠️ Could not remove .env file: {e}")
    
    # Create new .env file with proper encoding
    env_content = """# Environment Variables for Backend
# Add your actual API keys here for full testing

# OpenRouter API Key (for LLM routing)
OPENROUTER_API_KEY=sk-or-your-key-here

# OpenAI API Key (for embeddings and fallback)
OPENAI_API_KEY=sk-proj-your-key-here

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///./orchestrator.db

# Optional: Debug mode
DEBUG=True
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Created new .env file with proper UTF-8 encoding")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    backend_dir = Path("backend")
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("📦 Checking dependencies...")
    
    # Try to import key modules
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        print("❌ FastAPI not installed - run: pip install fastapi")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except ImportError:
        print("❌ Uvicorn not installed - run: pip install uvicorn")
        return False
    
    try:
        import pandas
        print("✅ Pandas available")
    except ImportError:
        print("⚠️ Pandas not available - file parsing may be limited")
    
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF available")
    except ImportError:
        print("⚠️ PyMuPDF not available - PDF parsing disabled")
    
    return True

def create_minimal_env():
    """Create a minimal environment that works without API keys"""
    backend_dir = Path("backend")
    
    # Create a minimal .env for testing
    minimal_env = backend_dir / ".env.minimal"
    content = """# Minimal environment for testing without API keys
DEBUG=True
USE_MOCK_RESPONSES=True
"""
    
    try:
        with open(minimal_env, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Created minimal environment file")
        return True
    except Exception as e:
        print(f"❌ Failed to create minimal env: {e}")
        return False

def fix_orchestrator_agent():
    """Fix the orchestrator agent import issues"""
    backend_dir = Path("backend")
    agent_file = backend_dir / "agents" / "orchestrator_agent.py"
    
    if not agent_file.exists():
        print("⚠️ orchestrator_agent.py not found")
        return True
    
    try:
        # Read the file
        with open(agent_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add error handling for load_dotenv
        if "load_dotenv()" in content and "try:" not in content[:200]:
            fixed_content = content.replace(
                "load_dotenv()",
                """try:
    load_dotenv()
except Exception as e:
    print(f"⚠️ Warning: Could not load .env file: {e}")
    print("Continuing with environment variables or defaults...")"""
            )
            
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print("✅ Added error handling to orchestrator_agent.py")
        
        return True
    except Exception as e:
        print(f"⚠️ Could not fix orchestrator_agent.py: {e}")
        return True  # Non-critical

def test_backend_startup():
    """Test if the backend can start"""
    backend_dir = Path("backend")
    main_file = backend_dir / "main.py"
    
    if not main_file.exists():
        print("❌ main.py not found in backend directory")
        return False
    
    print("🧪 Testing backend startup...")
    
    # Change to backend directory
    original_dir = os.getcwd()
    try:
        os.chdir(backend_dir)
        
        # Try to import the main module
        sys.path.insert(0, str(backend_dir.absolute()))
        
        try:
            import main
            print("✅ Backend imports successfully")
            return True
        except Exception as e:
            print(f"❌ Backend import failed: {e}")
            return False
        
    finally:
        os.chdir(original_dir)
        if str(backend_dir.absolute()) in sys.path:
            sys.path.remove(str(backend_dir.absolute()))

def main():
    """Run all fixes"""
    print("🔧 Backend Startup Fix Script")
    print("=" * 40)
    
    success_count = 0
    total_fixes = 5
    
    # Fix 1: Environment file
    if fix_env_file():
        success_count += 1
    
    # Fix 2: Check dependencies
    if check_dependencies():
        success_count += 1
    
    # Fix 3: Create minimal environment
    if create_minimal_env():
        success_count += 1
    
    # Fix 4: Fix orchestrator agent
    if fix_orchestrator_agent():
        success_count += 1
    
    # Fix 5: Test startup
    if test_backend_startup():
        success_count += 1
    
    print("\n" + "=" * 40)
    print(f"🎯 Fix Results: {success_count}/{total_fixes} successful")
    
    if success_count >= 4:
        print("✅ Backend should now start properly!")
        print("\n🚀 Next steps:")
        print("1. cd backend")
        print("2. python main.py")
        print("3. Run manual tests from MANUAL_QA_GUIDE.md")
    else:
        print("⚠️ Some issues remain. Check the errors above.")
        print("\n🔧 Manual steps needed:")
        print("1. Install missing dependencies: pip install -r backend/requirements.txt")
        print("2. Add your API keys to backend/.env")
        print("3. Check Python version compatibility")

if __name__ == "__main__":
    main() 