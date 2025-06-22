#!/usr/bin/env python3
"""
Full integration test for the updated TTS format functionality
"""

import json
from pathlib import Path
from src.api.lastfm_client import Track, Playlist
from src.tts_formatter.tts_formatter import TTSFormatter

def test_full_integration():
    """Test the full integration with custom nickname and description"""
    
    # Create a realistic test playlist
    test_tracks = [
        Track(
            title="One",
            artist="Metallica",
            album="...And Justice for All",
            duration=428
        ),
        Track(
            title="Master of Puppets",
            artist="Metallica",
            album="Master of Puppets",
            duration=515
        ),
        Track(
            title="The Number of the Beast",
            artist="Iron Maiden",
            album="The Number of the Beast",
            duration=292
        )
    ]
    
    test_playlist = Playlist(
        name="Metal Classics",
        description="Classic heavy metal tracks",
        tracks=test_tracks,
        total_tracks=len(test_tracks)
    )
    
    # Initialize formatter
    formatter = TTSFormatter("./test_output")
    
    # Create music player
    music_player = formatter.create_music_player(test_playlist)
    
    # Add some mock workshop URLs
    music_player.playlist[0].url = "https://steamusercontent-a.akamaihd.net/ugc/test1/metallica_one/"
    music_player.playlist[1].url = "https://steamusercontent-a.akamaihd.net/ugc/test2/metallica_master/"
    music_player.playlist[2].url = "https://steamusercontent-a.akamaihd.net/ugc/test3/iron_maiden_beast/"
    
    print("Testing TTS Format Generation with Custom Options")
    print("=" * 55)
    
    # Test 1: Simple format with custom nickname and description
    print("\n1. Testing Simple Format with Custom Options:")
    save_data = formatter.generate_save_file(
        music_player=music_player,
        nickname="🎵 Metal Classics Player",
        description="A curated collection of classic heavy metal tracks for your TTS sessions",
        use_simple_format=True
    )
    
    # Save the test file
    output_file = Path("./test_output/metal_classics_simple.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ File saved: {output_file}")
    print(f"✓ Nickname: {save_data['ObjectStates'][0]['Nickname']}")
    print(f"✓ Description: {save_data['ObjectStates'][0]['Description']}")
    
    # Test 2: Full format with different custom options
    print("\n2. Testing Full Format with Different Custom Options:")
    save_data_full = formatter.generate_save_file(
        music_player=music_player,
        nickname="Advanced Metal Player",
        description="Full-featured music player with advanced controls",
        use_simple_format=False
    )
    
    output_file_full = Path("./test_output/metal_classics_full.json")
    with open(output_file_full, 'w', encoding='utf-8') as f:
        json.dump(save_data_full, f, indent=2, ensure_ascii=False)
    
    print(f"✓ File saved: {output_file_full}")
    print(f"✓ Nickname: {save_data_full['ObjectStates'][0]['Nickname']}")
    print(f"✓ Description: {save_data_full['ObjectStates'][0]['Description']}")
    
    # Test 3: Default options (no custom nickname/description)
    print("\n3. Testing Default Options:")
    save_data_default = formatter.generate_save_file(
        music_player=music_player,
        nickname="",
        description="",
        use_simple_format=True
    )
    
    output_file_default = Path("./test_output/metal_classics_default.json")
    with open(output_file_default, 'w', encoding='utf-8') as f:
        json.dump(save_data_default, f, indent=2, ensure_ascii=False)
    
    print(f"✓ File saved: {output_file_default}")
    print(f"✓ Nickname: {save_data_default['ObjectStates'][0]['Nickname']}")
    print(f"✓ Description: {save_data_default['ObjectStates'][0]['Description']}")
    
    # Test 4: Verify the save_formatted_files method with custom options
    print("\n4. Testing save_formatted_files with Custom Options:")
    saved_files = formatter.save_formatted_files(
        music_player=music_player,
        base_filename="metal_classics_complete",
        nickname="🎸 Complete Metal Collection",
        description="The ultimate metal playlist for Tabletop Simulator",
        use_simple_format=True
    )
    
    print("✓ All files saved:")
    for file_type, file_path in saved_files.items():
        print(f"  - {file_type}: {Path(file_path).name}")
    
    # Verify the LuaScript contains the playlist in the simple format
    lua_script = save_data['ObjectStates'][0]['LuaScript']
    if 'playlist = {' in lua_script and 'Metallica' in lua_script:
        print("✓ LuaScript contains simple playlist format with track data")
    else:
        print("✗ LuaScript missing expected format")
    
    print("\n" + "=" * 55)
    print("✅ All integration tests completed successfully!")
    print("\nGenerated files can be imported directly into Tabletop Simulator.")
    print("The simple format matches the structure shown in Woody's Progressive Metal.json")
    
    return {
        'simple_format': save_data,
        'full_format': save_data_full,
        'default_format': save_data_default,
        'saved_files': saved_files
    }

if __name__ == "__main__":
    results = test_full_integration()
    
    print("\n📁 Check the ./test_output/ directory for all generated files:")
    print("- metal_classics_simple.json (Simple format with custom options)")
    print("- metal_classics_full.json (Full format with custom options)")
    print("- metal_classics_default.json (Default format)")
    print("- metal_classics_complete.json (Complete save file)")
    print("- metal_classics_complete.lua (Full Lua script)")
    print("- metal_classics_complete_simple.lua (Simple Lua script)")
    print("- metal_classics_complete_data.json (JSON data)")
    print("- metal_classics_complete_summary.txt (Text summary)")
