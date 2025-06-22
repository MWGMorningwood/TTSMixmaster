"""
Azure Blob Upload Test

Test script to verify Azure Blob Storage integration works properly.
This will test uploading an existing audio file to Azure Blob Storage.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.uploader.azure_uploader import AzureBlobUploader, UploadResult
from src.api.lastfm_client import Track
from src.utils.config import ConfigManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_azure_upload():
    """Test uploading a file to Azure Blob Storage"""
    print("Azure Blob Storage Upload Test")
    print("=" * 50)
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"Azure connection string configured: {'Yes' if config.azure_storage_connection_string and config.azure_storage_connection_string != 'your_azure_storage_connection_string_here' else 'No'}")
    print(f"Container name: {config.azure_container_name}")
    
    # Initialize uploader
    uploader = AzureBlobUploader(
        connection_string=config.azure_storage_connection_string if config.azure_storage_connection_string != 'your_azure_storage_connection_string_here' else None,
        container_name=config.azure_container_name
    )
    
    if not uploader.blob_service_client:
        print("❌ Azure Blob client not initialized. Please configure AZURE_STORAGE_CONNECTION_STRING in .env")
        return False
    
    # Find an audio file to upload
    downloads_dir = Path("./downloads")
    if not downloads_dir.exists():
        print("❌ Downloads directory doesn't exist")
        return False
    
    audio_files = list(downloads_dir.glob("*.mp3"))
    if not audio_files:
        print("❌ No MP3 files found in downloads directory")
        return False
    
    test_file = audio_files[0]
    print(f"Testing with file: {test_file.name}")
    
    # Create a test track object
    track = Track(
        artist="Test Artist",
        title="Test Song",
        album="Test Album",
        duration=180,
        url="https://example.com"
    )
    
    # Upload the file
    print("Uploading file to Azure Blob Storage...")
    result = uploader.upload_audio_file(str(test_file), track)
    
    if result.success:
        print("✅ Upload successful!")
        print(f"   Public URL: {result.public_url}")
        print(f"   Blob name: {result.blob_name}")
        print(f"   File size: {result.file_size} bytes")
        print(f"   Upload time: {result.upload_time}")
        
        # Test listing files
        print("\nListing uploaded files...")
        files = uploader.list_uploaded_files()
        print(f"Found {len(files)} files in container")
        for file_info in files[-3:]:  # Show last 3 files
            print(f"   - {file_info['name']} ({file_info['size']} bytes)")
        
        # Test getting stats
        stats = uploader.get_upload_stats()
        print(f"\nUpload statistics:")
        print(f"   Total files: {stats['total_files']}")
        print(f"   Total size: {stats['total_size_mb']} MB")
        print(f"   Container: {stats['container_name']}")
        
        return True
    else:
        print(f"❌ Upload failed: {result.error_message}")
        return False

if __name__ == "__main__":
    success = test_azure_upload()
    sys.exit(0 if success else 1)
