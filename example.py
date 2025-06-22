#!/usr/bin/env python3
"""
TTSMixmaster Example Script

This script demonstrates how to use TTSMixmaster programmatically
without the GUI interface.
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from api.lastfm_client import LastFMAPI, Track, Playlist
from tts_formatter.tts_formatter import TTSFormatter
from utils.config import ConfigManager, setup_logging


def example_usage():
    """Example of using TTSMixmaster programmatically"""
    
    # Set up logging
    setup_logging("INFO")
    
    print("TTSMixmaster Example Usage")
    print("=" * 50)
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # Check if configured
    if not config_manager.is_configured():
        print("❌ TTSMixmaster is not configured!")
        print("Please edit the .env file with your Last.fm API credentials.")
        print("You can copy .env.template to .env and fill in the values.")
        return False
    
    print("✅ Configuration loaded successfully")
    
    # Example 1: Create a simple playlist manually
    print("\n1. Creating a sample playlist...")
    
    sample_tracks = [
        Track(title="Bohemian Rhapsody", artist="Queen", album="A Night at the Opera"),
        Track(title="Stairway to Heaven", artist="Led Zeppelin", album="Led Zeppelin IV"),
        Track(title="Hotel California", artist="Eagles", album="Hotel California"),
        Track(title="Sweet Child O' Mine", artist="Guns N' Roses", album="Appetite for Destruction"),
        Track(title="Smells Like Teen Spirit", artist="Nirvana", album="Nevermind")
    ]
    
    sample_playlist = Playlist(
        name="Classic Rock Favorites",
        tracks=sample_tracks,
        description="A collection of classic rock hits"
    )
    
    print(f"Created playlist: {sample_playlist.name}")
    print(f"Tracks: {len(sample_playlist.tracks)}")
    
    # Example 2: Generate TTS code
    print("\n2. Generating Tabletop Simulator code...")
    
    formatter = TTSFormatter(config.tts_output_path)
    music_player = formatter.create_music_player(sample_playlist)
    
    # Generate Lua script
    lua_code = formatter.generate_lua_script(music_player)
    
    # Save all formatted files
    saved_files = formatter.save_formatted_files(music_player, "example_playlist")
    
    print("Generated files:")
    for file_type, file_path in saved_files.items():
        print(f"  {file_type}: {file_path}")
    
    # Example 3: Show Last.fm API usage (if configured)
    if config.lastfm_api_key:
        print("\n3. Testing Last.fm API connection...")
        
        try:
            api = LastFMAPI(config.lastfm_api_key, config.lastfm_api_secret, config.lastfm_username)
            
            # Try to get recent tracks (just 5 for testing)
            recent_tracks = api.get_user_recent_tracks(limit=5)
            
            if recent_tracks:
                print(f"✅ Successfully connected to Last.fm!")
                print(f"Found {len(recent_tracks)} recent tracks:")
                for i, track in enumerate(recent_tracks, 1):
                    print(f"  {i}. {track}")
            else:
                print("⚠️ Connected but no recent tracks found")
                
        except Exception as e:
            print(f"❌ Last.fm connection failed: {e}")
    else:
        print("\n3. Last.fm API key not configured, skipping API test")
      # Example 4: Show downloader setup (without actually downloading)
    print("\n4. Audio downloader information...")
    
    print(f"✅ Downloader would be configured with:")
    print(f"  Download path: {config.download_path}")
    print(f"  Audio quality: {config.audio_quality}")
    print(f"  Note: Downloader requires yt-dlp and uses YouTube/SoundCloud for audio sources")
    
    # Example 5: Preview generated Lua code
    print("\n5. Generated Lua Code Preview:")
    print("-" * 50)
    
    # Show first 20 lines of the generated code
    lua_lines = lua_code.split('\n')
    for i, line in enumerate(lua_lines[:20], 1):
        print(f"{i:2d}: {line}")
    
    if len(lua_lines) > 20:
        print(f"... and {len(lua_lines) - 20} more lines")
    
    print("\n" + "=" * 50)
    print("✅ Example completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env with your Last.fm API credentials to test API features")
    print("2. Run 'python main.py' to use the GUI interface")
    print("3. Check the generated files in the tts_formatted/ directory")
    
    return True


if __name__ == "__main__":
    try:
        success = example_usage()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nExample interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
