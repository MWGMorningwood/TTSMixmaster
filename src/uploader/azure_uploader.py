"""
Azure Blob Storage Uploader Module

This module provides functionality to upload audio files to Azure Blob Storage
for use with Tabletop Simulator. Files uploaded here get public URLs that
TTS can access directly.
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from datetime import datetime

try:
    from azure.storage.blob import BlobServiceClient, ContainerClient, PublicAccess
    from azure.storage.blob import ContentSettings
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    ContentSettings = None
    logging.warning("Azure SDK not available. Please install azure-storage-blob to enable uploads.")

from ..api.lastfm_client import Track


@dataclass
class UploadResult:
    """Represents the result of an upload operation"""
    success: bool
    file_path: str
    public_url: Optional[str] = None
    blob_name: Optional[str] = None
    file_size: int = 0
    upload_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class AzureBlobUploader:
    """Uploads audio files to Azure Blob Storage for TTS integration"""
    
    def __init__(self, connection_string: Optional[str] = None, account_name: Optional[str] = None, 
                 account_key: Optional[str] = None, container_name: str = "tts-audio"):
        """
        Initialize the Azure Blob uploader
        
        Args:
            connection_string: Azure Storage connection string
            account_name: Azure Storage account name (if not using connection string)
            account_key: Azure Storage account key (if not using connection string)
            container_name: Name of the container to upload to
        """
        self.container_name = container_name
        self.logger = logging.getLogger(__name__)
        self.blob_service_client = None
        self.account_name = account_name or "unknown"
        
        if not AZURE_AVAILABLE:
            self.logger.error("Azure SDK not available. Install azure-storage-blob to use this uploader.")
            return
            
        try:
            if connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)  # type: ignore
                # Extract account name from connection string if possible
                if "AccountName=" in connection_string:
                    self.account_name = connection_string.split("AccountName=")[1].split(";")[0]
            elif account_name and account_key:
                account_url = f"https://{account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)  # type: ignore
                self.account_name = account_name
            else:
                # Try to get from environment variables
                env_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
                if env_connection_string:
                    self.blob_service_client = BlobServiceClient.from_connection_string(env_connection_string)  # type: ignore
                    if "AccountName=" in env_connection_string:
                        self.account_name = env_connection_string.split("AccountName=")[1].split(";")[0]
                else:
                    self.logger.error("No Azure Storage credentials provided")
                    return
            
            # Ensure container exists
            self._ensure_container_exists()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure Blob client: {e}")
            self.blob_service_client = None
    
    def _ensure_container_exists(self):
        """Ensure the container exists and is configured for public access"""
        if not self.blob_service_client:
            return
            
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)  # type: ignore
            
            # Try to get container properties to see if it exists
            try:
                container_client.get_container_properties()  # type: ignore
                self.logger.info(f"Container '{self.container_name}' already exists")
            except Exception:
                # Container doesn't exist, create it with public blob access
                self.logger.info(f"Creating container '{self.container_name}' with public blob access")
                if AZURE_AVAILABLE:
                    container_client.create_container(public_access=PublicAccess.Blob)  # type: ignore
                
        except Exception as e:
            self.logger.error(f"Failed to ensure container exists: {e}")
            raise
    
    def upload_audio_file(self, file_path: str, track: Optional[Track] = None, 
                         custom_blob_name: Optional[str] = None) -> UploadResult:
        """
        Upload an audio file to Azure Blob Storage
        
        Args:
            file_path: Path to the audio file to upload
            track: Track object for metadata (optional)
            custom_blob_name: Custom blob name (optional, will generate if not provided)
            
        Returns:
            UploadResult object
        """
        if not self.blob_service_client:
            return UploadResult(
                success=False,
                file_path=file_path,
                error_message="Azure Blob client not initialized"
            )        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return UploadResult(
                success=False,
                file_path=file_path,
                error_message="File does not exist"
            )
        
        try:
            # Generate blob name (no hash-based uniqueness - ONE FILE PER SONG)
            blob_name = custom_blob_name or self._generate_blob_name(file_path_obj, track)
            
            # Check if blob already exists - if so, skip upload
            blob_client = self.blob_service_client.get_blob_client(  # type: ignore
                container=self.container_name, 
                blob=blob_name
            )
            
            try:
                # Check if blob exists
                blob_properties = blob_client.get_blob_properties()  # type: ignore
                if blob_properties:
                    # Blob exists, generate public URL and return success
                    public_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
                    self.logger.info(f"Blob already exists, skipping upload: {blob_name}")
                    
                    return UploadResult(
                        success=True,
                        file_path=str(file_path_obj),
                        public_url=public_url,
                        blob_name=blob_name,
                        file_size=file_path_obj.stat().st_size,
                        upload_time=datetime.utcnow(),
                        metadata=self._prepare_metadata(file_path_obj, track)
                    )
            except Exception:
                # Blob doesn't exist, continue with upload
                pass
            
            # Prepare metadata
            metadata = self._prepare_metadata(file_path_obj, track)
            
            # Get file info
            file_size = file_path_obj.stat().st_size
            content_type = mimetypes.guess_type(str(file_path_obj))[0] or 'audio/mpeg'
            
            self.logger.info(f"Uploading {file_path_obj.name} to Azure Blob Storage...")
            
            with open(file_path_obj, 'rb') as data:
                # Create ContentSettings object if Azure is available
                content_settings = None
                if AZURE_AVAILABLE and ContentSettings is not None:
                    try:
                        content_settings = ContentSettings(
                            content_type=content_type,
                            content_disposition=f'inline; filename="{file_path_obj.name}"'
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not create ContentSettings: {e}")
                        content_settings = None
                
                blob_client.upload_blob(  # type: ignore
                    data, 
                    overwrite=True,
                    content_settings=content_settings,
                    metadata=metadata
                )
            
            # Generate public URL
            public_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
            
            self.logger.info(f"Successfully uploaded to: {public_url}")
            
            return UploadResult(
                success=True,
                file_path=file_path,
                public_url=public_url,
                blob_name=blob_name,
                file_size=file_size,
                upload_time=datetime.utcnow(),
                metadata=metadata
            )
            
        except Exception as e:
            if AZURE_AVAILABLE:
                try:
                    from azure.core.exceptions import AzureError
                    if isinstance(e, AzureError):
                        error_msg = f"Azure upload failed: {str(e)}"
                    else:
                        error_msg = f"Upload failed: {str(e)}"
                except ImportError:
                    error_msg = f"Upload failed: {str(e)}"
            else:
                error_msg = f"Upload failed: {str(e)}"
                
            self.logger.error(error_msg)
            return UploadResult(
                success=False,
                file_path=file_path,                error_message=error_msg
            )
    
    def _generate_blob_name(self, file_path: Path, track: Optional[Track] = None) -> str:
        """
        Generate a consistent blob name for the file (no hash for uniqueness)
        
        Args:
            file_path: Path to the file
            track: Track object for metadata
            
        Returns:
            Generated blob name
        """
        if track:
            # Use track info for meaningful names
            safe_artist = self._sanitize_filename(track.artist)
            safe_title = self._sanitize_filename(track.title)
            base_name = f"{safe_artist} - {safe_title}"
        else:
            # Use original filename
            base_name = file_path.stem
        
        extension = file_path.suffix.lower()
        
        # Create blob name with folder structure for organization (no hash)
        blob_name = f"audio/{base_name}{extension}"
        
        return blob_name
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for use in blob names"""
        import re
        # Remove invalid characters and limit length
        filename = re.sub(r'[<>:"/\\|?*\[\]]', '', filename)
        filename = re.sub(r'\s+', '_', filename.strip())
        return filename[:50]  # Limit length
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file for uniqueness"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _prepare_metadata(self, file_path: Path, track: Optional[Track] = None) -> Dict[str, str]:
        """Prepare metadata for the blob"""
        metadata = {
            'source': 'TTSMixmaster',
            'upload_time': datetime.utcnow().isoformat(),
            'original_filename': file_path.name,
            'file_size': str(file_path.stat().st_size)
        }
        
        if track:
            metadata.update({
                'artist': track.artist or '',
                'title': track.title or '',
                'album': track.album or '',
                'duration': str(track.duration) if track.duration else '0'
            })
        
        # Azure metadata keys must be valid
        return {k: v for k, v in metadata.items() if v and k.replace('_', '').isalnum()}
    
    def upload_playlist_files(self, file_paths: List[str], tracks: Optional[List[Track]] = None) -> List[UploadResult]:
        """
        Upload multiple files for a playlist
        
        Args:
            file_paths: List of file paths to upload
            tracks: List of corresponding Track objects (optional)
            
        Returns:
            List of UploadResult objects
        """
        results = []
        tracks_list = tracks or [None] * len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            track = tracks_list[i] if i < len(tracks_list) else None
            result = self.upload_audio_file(file_path, track)
            results.append(result)
            
            if result.success:
                self.logger.info(f"Uploaded {i+1}/{len(file_paths)}: {Path(file_path).name}")
            else:
                self.logger.error(f"Failed to upload {i+1}/{len(file_paths)}: {result.error_message}")
        
        return results
    
    def list_uploaded_files(self, prefix: str = "audio/") -> List[Dict[str, Any]]:
        """
        List files in the container
        
        Args:
            prefix: Blob name prefix to filter by
            
        Returns:
            List of blob information dictionaries
        """
        if not self.blob_service_client:
            return []
        
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)  # type: ignore
            blobs = []
            
            for blob in container_client.list_blobs(name_starts_with=prefix):  # type: ignore
                blob_info = {
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified,
                    'url': f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}",
                    'metadata': blob.metadata or {}
                }
                blobs.append(blob_info)
            
            return blobs
            
        except Exception as e:
            self.logger.error(f"Failed to list blobs: {e}")
            return []
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Azure Blob Storage
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(  # type: ignore
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()  # type: ignore
            self.logger.info(f"Deleted blob: {blob_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete blob {blob_name}: {e}")
            return False
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Get statistics about uploaded files"""
        files = self.list_uploaded_files()
        
        if not files:
            return {
                'total_files': 0,
                'total_size': 0,
                'last_upload': None
            }
        
        total_size = sum(f['size'] for f in files)
        last_upload = max(f['last_modified'] for f in files) if files else None
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'last_upload': last_upload,
            'container_name': self.container_name
        }


# Backward compatibility aliases
SteamUploader = AzureBlobUploader
CloudUploader = AzureBlobUploader
