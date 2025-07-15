#!/usr/bin/env python3
"""
TailwindCSS Configuration Validation Script
Checks if all TailwindCSS files are properly configured

Usage: python fix_tailwind_validation.py
"""

import os
import json

def validate_tailwind_setup():
    """Validate TailwindCSS configuration"""
    
    print("🎨 Validating TailwindCSS Setup...")
    print("=" * 50)
    
    issues = []
    
    # Check if frontend directory exists
    if not os.path.exists('frontend'):
        issues.append("❌ frontend/ directory not found")
        return False
    
    # Check PostCSS config in frontend
    if os.path.exists('frontend/postcss.config.js'):
        print("✅ frontend/postcss.config.js exists")
        
        try:
            with open('frontend/postcss.config.js', 'r') as f:
                content = f.read()
                if 'tailwindcss' in content and 'autoprefixer' in content:
                    print("✅ PostCSS config includes TailwindCSS and Autoprefixer")
                else:
                    issues.append("❌ PostCSS config missing TailwindCSS or Autoprefixer")
        except:
            issues.append("❌ Could not read PostCSS config")
    else:
        issues.append("❌ frontend/postcss.config.js missing")
    
    # Check TailwindCSS config
    if os.path.exists('frontend/tailwind.config.js'):
        print("✅ frontend/tailwind.config.js exists")
    else:
        issues.append("❌ frontend/tailwind.config.js missing")
    
    # Check CSS file with TailwindCSS directives
    if os.path.exists('frontend/src/index.css'):
        print("✅ frontend/src/index.css exists")
        
        try:
            with open('frontend/src/index.css', 'r') as f:
                content = f.read()
                required_directives = ['@tailwind base', '@tailwind components', '@tailwind utilities']
                
                for directive in required_directives:
                    if directive in content:
                        print(f"✅ Found: {directive}")
                    else:
                        issues.append(f"❌ Missing: {directive}")
        except:
            issues.append("❌ Could not read index.css")
    else:
        issues.append("❌ frontend/src/index.css missing")
    
    # Check package.json for TailwindCSS dependency
    if os.path.exists('frontend/package.json'):
        print("✅ frontend/package.json exists")
        
        try:
            with open('frontend/package.json', 'r') as f:
                package_data = json.load(f)
                dev_deps = package_data.get('devDependencies', {})
                
                if 'tailwindcss' in dev_deps:
                    print(f"✅ TailwindCSS dependency: {dev_deps['tailwindcss']}")
                else:
                    issues.append("❌ TailwindCSS not in devDependencies")
                    
                if 'autoprefixer' in dev_deps:
                    print(f"✅ Autoprefixer dependency: {dev_deps['autoprefixer']}")
                else:
                    issues.append("❌ Autoprefixer not in devDependencies")
                    
                if 'postcss' in dev_deps:
                    print(f"✅ PostCSS dependency: {dev_deps['postcss']}")
                else:
                    issues.append("❌ PostCSS not in devDependencies")
        except:
            issues.append("❌ Could not read package.json")
    else:
        issues.append("❌ frontend/package.json missing")
    
    # Check for conflicting root PostCSS config
    if os.path.exists('postcss.config.js'):
        issues.append("⚠️  Root postcss.config.js found (may cause conflicts)")
    else:
        print("✅ No conflicting root PostCSS config")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print("❌ Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        print("\n🔧 Fix Required: Please address the issues above")
        return False
    else:
        print("🎉 TailwindCSS is properly configured!")
        print("\n📋 Next Steps:")
        print("1. cd frontend")
        print("2. npm install")
        print("3. npm run dev")
        print("\nTailwindCSS should now load without errors! 🎨")
        return True

if __name__ == "__main__":
    import sys
    success = validate_tailwind_setup()
    sys.exit(0 if success else 1) 