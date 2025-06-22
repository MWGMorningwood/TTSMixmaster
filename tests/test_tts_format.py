#!/usr/bin/env python3
"""
Test script for the new TTS format matching Woody's Progressive Metal
"""

import json
from pathlib import Path
from src.api.lastfm_client import Track, Playlist
from src.tts_formatter.tts_formatter import TTSFormatter

def test_simple_format():
    """Test the simple playlist format generation"""
    
    # Create test tracks
    test_tracks = [        Track(
            title="Vicarious",
            artist="Tool",
            album="10,000 Days",
            duration=427
        ),
        Track(
            title="Schism", 
            artist="Tool",
            album="Lateralus",
            duration=547
        ),
        Track(
            title="The Grey",
            artist="TesseracT",
            album="One",
            duration=284
        )
    ]
      # Create test playlist
    test_playlist = Playlist(
        name="Test Progressive Metal",
        description="Test playlist for TTS format",
        tracks=test_tracks,
        total_tracks=len(test_tracks)
    )
    
    # Initialize formatter
    formatter = TTSFormatter("./test_output")
    
    # Create music player
    music_player = formatter.create_music_player(test_playlist)
    
    # Test simple playlist Lua generation
    simple_lua = formatter.generate_simple_playlist_lua(music_player)
    print("Simple Playlist Lua Script:")
    print("=" * 50)
    print(simple_lua[:500] + "..." if len(simple_lua) > 500 else simple_lua)
    print("=" * 50)
    
    # Test full save file generation with custom nickname/description
    save_data = formatter.generate_save_file(
        music_player=music_player,
        nickname="Progressive Metal Playlist",
        description="A collection of progressive metal tracks for TTS",
        use_simple_format=True
    )
    
    # Save test file
    output_file = Path("./test_output/test_progressive_metal.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest file saved to: {output_file}")
    print(f"Nickname: {save_data['ObjectStates'][0]['Nickname']}")
    print(f"Description: {save_data['ObjectStates'][0]['Description']}")
    print(f"Number of tracks in playlist: {len(test_tracks)}")
    
    # Verify the LuaScript contains the playlist
    lua_script = save_data['ObjectStates'][0]['LuaScript']
    if 'playlist = {' in lua_script and 'Tool' in lua_script:
        print("✓ LuaScript contains playlist data")
    else:
        print("✗ LuaScript missing playlist data")
    
    return save_data

def test_with_workshop_urls():
    """Test with mock workshop URLs"""
    
    # Create test tracks with mock workshop URLs
    test_tracks = [        Track(
            title="Knights of Cydonia",
            artist="Muse", 
            album="Black Holes and Revelations",
            duration=366
        ),
        Track(
            title="Reapers",
            artist="Muse",
            album="Drones", 
            duration=308
        )
    ]    
    test_playlist = Playlist(
        name="Muse Test Playlist",
        description="Test Muse tracks",
        tracks=test_tracks,
        total_tracks=len(test_tracks)
    )
    
    formatter = TTSFormatter("./test_output")
    music_player = formatter.create_music_player(test_playlist)
    
    # Manually add some mock workshop URLs to the audio objects
    music_player.playlist[0].url = "https://steamusercontent-a.akamaihd.net/ugc/test1/MOCK_URL_1/"
    music_player.playlist[1].url = "https://steamusercontent-a.akamaihd.net/ugc/test2/MOCK_URL_2/"
    
    # Generate save file
    save_data = formatter.generate_save_file(
        music_player=music_player,
        nickname="Muse Playlist",
        description="Progressive rock tracks by Muse",
        use_simple_format=True
    )
    
    # Save test file
    output_file = Path("./test_output/test_muse_playlist.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nMuse test file saved to: {output_file}")
    
    # Check that URLs are in the Lua script
    lua_script = save_data['ObjectStates'][0]['LuaScript']
    if 'steamusercontent-a.akamaihd.net' in lua_script:
        print("✓ Workshop URLs found in LuaScript")
    else:
        print("✗ Workshop URLs missing from LuaScript")
    
    return save_data

if __name__ == "__main__":
    print("Testing TTS Format Generation")
    print("============================")
    
    # Run tests
    test1_result = test_simple_format()
    print("\n" + "-" * 50)
    test2_result = test_with_workshop_urls()
    
    print("\n✓ All tests completed!")
    print("Check the ./test_output/ directory for generated files.")
