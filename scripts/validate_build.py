#!/usr/bin/env python3
"""
Validation script for TTSMixmaster PyInstaller build
Tests the spec file and validates the build output
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    try:
        import pyinstaller
        print(f"✅ PyInstaller found: {pyinstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    spec_file = Path("TTSMixmaster.spec")
    if not spec_file.exists():
        print("❌ TTSMixmaster.spec not found")
        return False
    print("✅ PyInstaller spec file found")
    
    main_file = Path("main.py")
    if not main_file.exists():
        print("❌ main.py not found")
        return False
    print("✅ Main script found")
    
    return True

def validate_dependencies():
    """Check if critical dependencies can be imported"""
    print("\n🔍 Validating critical imports...")
    
    critical_imports = [
        ("requests", "HTTP client"),
        ("dotenv", "Environment configuration"),
        ("pathlib", "Path handling"),
    ]
    
    failed_imports = []
    for module, description in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError:
            print(f"❌ {module} ({description}) - MISSING")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Missing dependencies: {', '.join(failed_imports)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def run_pyinstaller_build():
    """Run PyInstaller with the spec file"""
    print("\n🔨 Running PyInstaller build...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "TTSMixmaster.spec",
            "--clean",
            "--noconfirm"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ PyInstaller build completed successfully")
            return True
        else:
            print("❌ PyInstaller build failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PyInstaller build timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ PyInstaller build error: {e}")
        return False

def validate_build_output():
    """Validate the PyInstaller build output"""
    print("\n🔍 Validating build output...")
    
    dist_dir = Path("dist/TTSMixmaster")
    if not dist_dir.exists():
        print("❌ dist/TTSMixmaster directory not found")
        return False
    print("✅ Build directory found")
    
    exe_file = dist_dir / "TTSMixmaster.exe"
    if not exe_file.exists():
        print("❌ TTSMixmaster.exe not found")
        return False
    
    exe_size = exe_file.stat().st_size
    print(f"✅ Executable found ({exe_size:,} bytes)")
    
    internal_dir = dist_dir / "_internal"
    if not internal_dir.exists():
        print("❌ _internal directory not found - THIS IS THE MAIN ISSUE!")
        return False
    print("✅ _internal directory found")
    
    # Check critical files in _internal
    critical_files = ["base_library.zip"]
    internal_files = list(internal_dir.glob("*"))
    
    print(f"✅ _internal directory contains {len(internal_files)} files/directories")
    
    base_library = internal_dir / "base_library.zip"
    if base_library.exists():
        base_size = base_library.stat().st_size
        print(f"✅ base_library.zip found ({base_size:,} bytes)")
    else:
        print("❌ base_library.zip not found")
        return False
    
    # Check for Python DLL files
    dll_files = list(internal_dir.glob("python*.dll"))
    if dll_files:
        print(f"✅ Found {len(dll_files)} Python DLL files")
    else:
        print("⚠️  No Python DLL files found")
    
    # Calculate total build size
    total_size = sum(f.stat().st_size for f in dist_dir.rglob("*") if f.is_file())
    total_size_mb = total_size / (1024 * 1024)
    print(f"✅ Total build size: {total_size_mb:.1f} MB")
    
    if total_size_mb < 30:
        print("⚠️  Build size seems small, may be missing dependencies")
        return False
    
    return True

def main():
    """Main validation function"""
    print("🚀 TTSMixmaster Build Validation")
    print("=" * 50)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed")
        return 1
    
    if not validate_dependencies():
        print("\n❌ Dependencies validation failed")
        return 1
    
    if not run_pyinstaller_build():
        print("\n❌ PyInstaller build failed")
        return 1
    
    if not validate_build_output():
        print("\n❌ Build output validation failed")
        return 1
    
    print("\n🎉 All validations passed!")
    print("✅ The MSI installer issue should be fixed")
    print("\nNext steps:")
    print("1. Test the executable: dist/TTSMixmaster/TTSMixmaster.exe")
    print("2. Build MSI with WiX if available")
    print("3. Test MSI installation and launch")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())