#!/usr/bin/env python3
"""
Test script to verify the new image URL feature works correctly
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tts_formatter.tts_formatter import TTSFormatter, TTSMusicPlayer, TTSAudioObject
from src.api.lastfm_client import Track
import json


def test_image_url_feature():
    """Test the new image URL functionality"""
    print("Testing Image URL Feature...")
    
    # Create a test music player
    test_tracks = [
        TTSAudioObject(
            name="Test Track 1",
            url="https://example.com/track1.mp3",
            volume=0.8
        ),
        TTSAudioObject(
            name="Test Track 2", 
            url="https://example.com/track2.mp3",
            volume=0.7
        )
    ]
    
    music_player = TTSMusicPlayer(
        name="Test Playlist",
        playlist=test_tracks
    )
    
    # Create formatter
    formatter = TTSFormatter(output_path="test_output")
    
    # Test with custom image URLs
    custom_image_url = "https://example.com/my-custom-image.jpg"
    custom_secondary_url = "https://example.com/my-custom-secondary.jpg"
    
    print(f"Testing with custom image URL: {custom_image_url}")
    print(f"Testing with custom secondary URL: {custom_secondary_url}")
    
    # Generate save file with custom URLs
    save_data = formatter.generate_save_file(
        music_player=music_player,
        nickname="Test Music Player",
        description="Testing custom image URLs",
        image_url=custom_image_url,
        image_secondary_url=custom_secondary_url
    )
    
    # Check if the custom URLs are in the save file
    custom_image = save_data["ObjectStates"][0]["CustomImage"]
    actual_image_url = custom_image["ImageURL"]
    actual_secondary_url = custom_image["ImageSecondaryURL"]
    
    print(f"Actual image URL in save file: {actual_image_url}")
    print(f"Actual secondary URL in save file: {actual_secondary_url}")
    
    # Verify the URLs match our input
    assert actual_image_url == custom_image_url, f"Expected {custom_image_url}, got {actual_image_url}"
    assert actual_secondary_url == custom_secondary_url, f"Expected {custom_secondary_url}, got {actual_secondary_url}"
    
    print("✓ Custom URLs correctly applied!")
    
    # Test with empty URLs (should use defaults)
    print("\nTesting with empty URLs (should use defaults)...")
    
    save_data_default = formatter.generate_save_file(
        music_player=music_player,
        nickname="Test Music Player",
        description="Testing default image URLs",
        image_url="",
        image_secondary_url=""
    )
    
    custom_image_default = save_data_default["ObjectStates"][0]["CustomImage"]
    default_image_url = custom_image_default["ImageURL"]
    default_secondary_url = custom_image_default["ImageSecondaryURL"]
    
    print(f"Default image URL: {default_image_url}")
    print(f"Default secondary URL: {default_secondary_url}")
    
    # Verify defaults are Steam Workshop URLs
    assert "steamusercontent" in default_image_url, "Default should be Steam Workshop URL"
    assert "steamusercontent" in default_secondary_url, "Default should be Steam Workshop URL"
    
    print("✓ Default URLs correctly applied!")
    
    # Test save_formatted_files with custom URLs
    print("\nTesting save_formatted_files with custom URLs...")
    
    # Create test output directory
    test_output_dir = Path("test_output")
    test_output_dir.mkdir(exist_ok=True)
    
    saved_files = formatter.save_formatted_files(
        music_player=music_player,
        base_filename="test_custom_images",
        nickname="Custom Image Test",
        description="Testing custom images in save_formatted_files",
        image_url=custom_image_url,
        image_secondary_url=custom_secondary_url
    )
    
    print(f"Files saved: {list(saved_files.keys())}")
    
    # Verify the save file contains our custom URLs
    if 'save_file' in saved_files:
        with open(saved_files['save_file'], 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        saved_custom_image = saved_data["ObjectStates"][0]["CustomImage"]
        saved_image_url = saved_custom_image["ImageURL"] 
        saved_secondary_url = saved_custom_image["ImageSecondaryURL"]
        
        assert saved_image_url == custom_image_url, f"Expected {custom_image_url}, got {saved_image_url}"
        assert saved_secondary_url == custom_secondary_url, f"Expected {custom_secondary_url}, got {saved_secondary_url}"
        
        print("✓ Custom URLs correctly saved to file!")
    
    print("\n🎉 All tests passed! Image URL feature is working correctly.")
    

if __name__ == "__main__":
    test_image_url_feature()
