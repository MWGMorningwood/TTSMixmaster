"""
Test script for the updated TTSMixmaster TTS formatter
Demonstrates the new Woody's Progressive Metal format support
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.api.lastfm_client import Track, Playlist
from src.tts_formatter.tts_formatter import TTSFormatter


def create_sample_playlist() -> Playlist:
    """Create a sample playlist for testing"""
    sample_tracks = [
        Track(title="Ayla, Pt. 2", artist="Ayla", album=""),
        Track(title="Vois sur ton chemin (Techno Mix)", artist="BENNETT", album=""),
        Track(title="1998 (Kay Cee 1999 Radio Mix)", artist="Binary Finary", album=""),
        Track(title="Around the World (Radio Edit)", artist="Daft Punk", album=""),
        Track(title="Sandstorm (Radio Edit)", artist="Darude", album=""),
        Track(title="The Grey", artist="TesseracT", album=""),
        Track(title="Stranger Heads Prevail", artist="Thank You Scientist", album=""),
        Track(title="Vicarious", artist="Tool", album=""),
        Track(title="Schism", artist="Tool", album=""),
        Track(title="Blue", artist="A Perfect Circle", album=""),
    ]
    
    return Playlist(
        name="Test Progressive Metal",
        tracks=sample_tracks,
        description="A test playlist mixing electronic and progressive metal"
    )


def main():
    """Main function to test TTS formatting"""
    print("🎵 TTSMixmaster TTS Formatter Test")
    print("=" * 50)
    
    # Create sample playlist
    playlist = create_sample_playlist()
    print(f"Created playlist: {playlist.name}")
    print(f"Number of tracks: {len(playlist.tracks)}")
    
    # Initialize formatter
    formatter = TTSFormatter("./test_output")
    
    # Create music player
    music_player = formatter.create_music_player(playlist)
    print(f"\\nCreated music player: {music_player.name}")
    
    # Test the new simple playlist format
    print("\\n📄 Generating simple playlist Lua (Woody's format)...")
    simple_lua = formatter.generate_simple_playlist_lua(music_player)
    
    # Save a snippet to show the format
    with open("test_simple_playlist.lua", 'w', encoding='utf-8') as f:
        f.write(simple_lua)
    print("✅ Simple playlist saved to test_simple_playlist.lua")
    
    # Test the new save file format with custom nickname and description
    print("\\n📁 Generating TTS save file with custom fields...")
    custom_nickname = "My Awesome Playlist"
    custom_description = "A custom description for the music player"
    
    save_files = formatter.save_formatted_files(
        music_player, 
        base_filename="test_progressive_metal",
        nickname=custom_nickname,
        description=custom_description,
        use_simple_format=True
    )
    
    print("✅ Files generated:")
    for file_type, file_path in save_files.items():
        print(f"   {file_type}: {file_path}")
    
    # Show a preview of the simple playlist format
    print("\\n🎶 Preview of simple playlist format:")
    print("=" * 30)
    lines = simple_lua.split('\\n')
    for i, line in enumerate(lines[:20]):  # Show first 20 lines
        print(line)
    if len(lines) > 20:
        print("... (truncated)")
    
    print("\\n🎮 Usage Instructions:")
    print("1. Load the generated .json file in Tabletop Simulator")
    print("2. The object will have the custom nickname and description")
    print("3. The simple playlist format matches Woody's Progressive Metal style")
    print("4. You can customize the nickname and description fields")
    
    print("\\n✨ Test completed successfully!")


if __name__ == "__main__":
    main()
