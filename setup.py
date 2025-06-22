"""
Setup script for installing TTSMixmaster dependencies
"""

import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """Install requirements from requirements.txt"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("Error: requirements.txt not found!")
        return False
    
    try:
        print("Installing Python dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(__file__).parent / ".env"
    template_file = Path(__file__).parent / ".env.template"
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if not template_file.exists():
        print("Warning: .env.template not found!")
        return False
    
    try:
        # Copy template to .env
        with open(template_file, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print("✓ Created .env file from template")
        print("  Please edit .env file with your API credentials")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = [
        "downloads",
        "uploads", 
        "tts_formatted",
        "backups"
    ]
    
    base_path = Path(__file__).parent
    
    for directory in directories:
        dir_path = base_path / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        except Exception as e:
            print(f"✗ Failed to create directory {directory}: {e}")
            return False
    
    return True


def check_optional_dependencies():
    """Check for optional dependencies and provide installation instructions"""
    print("\nChecking optional dependencies...")
    
    # Check for SteamCMD
    try:
        subprocess.run(["steamcmd", "+help", "+quit"], 
                      capture_output=True, timeout=5)
        print("✓ SteamCMD is available")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("⚠ SteamCMD not found (optional for Steam Workshop uploads)")
        print("  Download from: https://developer.valvesoftware.com/wiki/SteamCMD")
    
    # Check for ffmpeg (needed by yt-dlp for some audio formats)
    try:
        subprocess.run(["ffmpeg", "-version"], 
                      capture_output=True, timeout=5)
        print("✓ FFmpeg is available")
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("⚠ FFmpeg not found (recommended for audio processing)")
        print("  Download from: https://ffmpeg.org/download.html")


def main():
    """Main setup function"""
    print("TTSMixmaster Setup")
    print("=" * 50)
    
    success = True
    
    # Install Python dependencies
    if not install_requirements():
        success = False
    
    # Create .env file
    if not create_env_file():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Check optional dependencies
    check_optional_dependencies()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API credentials")
        print("2. Run: python main.py")
    else:
        print("✗ Setup completed with errors")
        print("Please check the error messages above")
    
    return success


if __name__ == "__main__":
    main()
