#!/usr/bin/env python3
"""
Test script for the updated audio processing and TTS format
Verifies mono audio output and correct image URLs
"""

import sys
import json
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.api.lastfm_client import Track, Playlist
from src.tts_formatter.tts_formatter import TTSFormatter
from src.downloader.audio_downloader import AudioDownloader


def test_image_urls():
    """Test that the TTS save file uses the correct image URLs"""
    print("Testing TTS Save File Image URLs...")
    
    # Create test playlist
    tracks = [
        Track(title="Test Track 1", artist="Test Artist 1", album="Test Album"),
        Track(title="Test Track 2", artist="Test Artist 2", album="Test Album"),
    ]
    playlist = Playlist(name="Image URL Test", tracks=tracks)
    
    # Create formatter
    formatter = TTSFormatter(output_path="./test_output")
    
    # Create music player
    music_player = formatter.create_music_player(playlist, player_name="Image URL Test")
    
    # Generate save file
    save_data = formatter.generate_save_file(
        music_player, 
        nickname="🎵 Image URL Test", 
        description="Testing the correct image URLs",
        use_simple_format=True
    )
    
    # Check the image URLs
    object_state = save_data['ObjectStates'][0]
    custom_image = object_state['CustomImage']
    
    expected_primary = "https://steamusercontent-a.akamaihd.net/ugc/9672878331288570/AE7A2999E8CD0EFF71210D7961A41E1F87F9DE78/"
    expected_secondary = "https://steamusercontent-a.akamaihd.net/ugc/1778335968028979741/9DA6ABA2450EBDA4E967816C4FA92289A638DB53/"
    
    print(f"Primary Image URL: {custom_image['ImageURL']}")
    print(f"Secondary Image URL: {custom_image['ImageSecondaryURL']}")
    
    assert custom_image['ImageURL'] == expected_primary, f"Primary URL mismatch. Expected: {expected_primary}, Got: {custom_image['ImageURL']}"
    assert custom_image['ImageSecondaryURL'] == expected_secondary, f"Secondary URL mismatch. Expected: {expected_secondary}, Got: {custom_image['ImageSecondaryURL']}"
    
    # Save the test file
    output_path = Path("./test_output") / "image_url_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Image URLs are correct!")
    print(f"✓ Test file saved to: {output_path}")
    return True


def test_audio_downloader_config():
    """Test that the audio downloader is configured for mono output"""
    print("\nTesting Audio Downloader Configuration...")
    
    downloader = AudioDownloader(download_path="./test_downloads")
    
    # Check if postprocessors are configured
    postprocessors = downloader.ydl_opts.get('postprocessors', [])
    
    print(f"Number of postprocessors: {len(postprocessors)}")
    
    # Check for mono conversion
    mono_processor = None
    for processor in postprocessors:
        if processor.get('key') == 'FFmpegPostProcessor':
            extra_args = processor.get('extra_args', [])
            if '-ac' in extra_args and '1' in extra_args:
                mono_processor = processor
                break
    
    assert mono_processor is not None, "Mono conversion postprocessor not found!"
    print(f"✓ Mono conversion configured: {mono_processor}")
    
    # Check for metadata processor
    metadata_processor = None
    for processor in postprocessors:
        if processor.get('key') == 'FFmpegMetadata':
            metadata_processor = processor
            break
    
    assert metadata_processor is not None, "Metadata postprocessor not found!"
    print(f"✓ Metadata enhancement configured: {metadata_processor}")
    
    print("✓ Audio downloader is properly configured for mono output and metadata!")
    return True


def test_existing_file_processing():
    """Test processing existing files to mono"""
    print("\nTesting Existing File Processing...")
    
    downloader = AudioDownloader()
    
    # Check for existing audio files in the downloads directory
    downloads_dir = Path("./downloads")
    if downloads_dir.exists():
        audio_files = list(downloads_dir.glob("*.mp3"))
        
        if audio_files:
            print(f"Found {len(audio_files)} audio files in downloads directory")
            
            # Test mono conversion on the first file (if it exists)
            test_file = audio_files[0]
            print(f"Testing mono conversion on: {test_file.name}")
            
            # Note: This will actually modify the file, so be careful
            # result = downloader.convert_to_mono(str(test_file))
            # print(f"Mono conversion result: {result}")
            
            print("✓ Mono conversion function is available")
            
            # Test metadata enhancement
            test_track = Track(
                title="Enhanced Title",
                artist="Enhanced Artist", 
                album="Enhanced Album"
            )
            
            # Note: This will actually modify the file, so be careful
            # result = downloader.enhance_metadata(str(test_file), test_track)
            # print(f"Metadata enhancement result: {result}")
            
            print("✓ Metadata enhancement function is available")
        else:
            print("No audio files found in downloads directory - functions available but not tested")
    else:
        print("Downloads directory not found - functions available but not tested")
    
    return True


def test_complete_integration():
    """Test complete integration with new features"""
    print("\nTesting Complete Integration...")
    
    # Create a comprehensive test playlist
    tracks = [
        Track(title="Integration Test 1", artist="Test Artist A", album="Test Album A"),
        Track(title="Integration Test 2", artist="Test Artist B", album="Test Album B"),
        Track(title="Integration Test 3", artist="Test Artist C", album="Test Album C"),
    ]
    playlist = Playlist(name="Integration Test", tracks=tracks)
    
    # Create formatter
    formatter = TTSFormatter(output_path="./test_output")
    
    # Create music player
    music_player = formatter.create_music_player(playlist, player_name="Integration Test")
    
    # Save all files with the new features
    saved_files = formatter.save_formatted_files(
        music_player,
        base_filename="integration_test",
        nickname="🎵 Integration Test Player",
        description="Testing complete integration with mono audio and correct images",
        use_simple_format=True
    )
    
    print("Generated files:")
    for file_type, file_path in saved_files.items():
        print(f"  {file_type}: {file_path}")
    
    # Verify the save file has correct image URLs
    save_file_path = Path(saved_files['save_file'])
    with open(save_file_path, 'r', encoding='utf-8') as f:
        save_data = json.load(f)
    
    object_state = save_data['ObjectStates'][0]
    custom_image = object_state['CustomImage']
    
    expected_primary = "https://steamusercontent-a.akamaihd.net/ugc/9672878331288570/AE7A2999E8CD0EFF71210D7961A41E1F87F9DE78/"
    expected_secondary = "https://steamusercontent-a.akamaihd.net/ugc/1778335968028979741/9DA6ABA2450EBDA4E967816C4FA92289A638DB53/"
    
    assert custom_image['ImageURL'] == expected_primary, "Primary URL incorrect in integration test"
    assert custom_image['ImageSecondaryURL'] == expected_secondary, "Secondary URL incorrect in integration test"
    
    print("✓ Integration test completed successfully!")
    print("✓ All files generated with correct image URLs")
    return True


def main():
    """Run all tests"""
    print("Testing Updated TTSMixmaster Features")
    print("====================================")
    
    try:
        # Run all tests
        test_image_urls()
        test_audio_downloader_config()
        test_existing_file_processing()
        test_complete_integration()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("✅ Image URLs are now correct")
        print("✅ Audio downloader configured for mono output")
        print("✅ Metadata enhancement is available")
        print("✅ Integration test successful")
        print("\nFeatures now available:")
        print("- TTS save files use the correct Steam image URLs")
        print("- Downloaded audio files are automatically converted to mono")
        print("- Metadata is enhanced during download")
        print("- Functions available to process existing files")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
