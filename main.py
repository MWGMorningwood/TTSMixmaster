"""
TTSMixmaster - Main Application Entry Point

A comprehensive tool for managing Last.fm playlists and integrating them with Tabletop Simulator.
This application provides functionality to:
- Query Last.fm API for playlists
- Download MP3 files
- Upload to Steam Workshop
- Generate Tabletop Simulator formatted code
- Manage playlists through a GUI interface
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.gui.main_window import TTSMixmasterApp


def main():
    """Main entry point for the TTSMixmaster application."""
    try:
        app = TTSMixmasterApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
