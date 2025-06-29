"""
Audio Downloader Module

This module provides functionality to download audio files from various sources
using yt-dlp and other methods.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import subprocess
import tempfile

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    yt_dlp = None
    logging.warning("yt-dlp not available. Some download functionality will be limited.")

try:
    import imageio_ffmpeg
    FFMPEG_PACKAGE_AVAILABLE = True
    # Get the path to the bundled FFmpeg executable
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PACKAGE_AVAILABLE = False
    FFMPEG_PATH = 'ffmpeg'  # Fall back to system FFmpeg

# Create a general purpose download error class
class DownloadError(Exception):
    """General download error for the audio downloader"""
    pass

from ..api.base_service import Track


@dataclass
class DownloadResult:
    """Represents the result of a download operation"""
    success: bool
    track: Track
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    duration: float = 0.0
    file_size: int = 0


class AudioDownloader:
    """Downloads audio files from various sources"""
    
    def __init__(self, download_path: str = "./downloads", audio_quality: str = "192"):
        """
        Initialize the audio downloader
        
        Args:
            download_path: Directory to save downloaded files
            audio_quality: Audio quality for downloads (128, 192, 256, 320)
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.audio_quality = audio_quality
        
        # Set up logging
        self.logger = logging.getLogger(__name__)        # Check if FFmpeg is available
        self.ffmpeg_available = self._check_ffmpeg_availability()        # Configure yt-dlp options
        self._configure_ydl_options()
    
    def _check_ffmpeg_availability(self) -> bool:
        """
        Check if FFmpeg is available on the system
        
        Returns:
            True if FFmpeg is available, False otherwise
        """
        # First try the bundled FFmpeg from imageio-ffmpeg
        if FFMPEG_PACKAGE_AVAILABLE:
            try:
                result = subprocess.run(
                    [FFMPEG_PATH, '-version'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    self.logger.info(f"✅ Bundled FFmpeg is available: {FFMPEG_PATH}")
                    return True
            except Exception as e:
                self.logger.warning(f"Bundled FFmpeg check failed: {e}")
        
        # Fall back to system FFmpeg
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info("✅ System FFmpeg is available")
                return True
            else:
                self.logger.warning("FFmpeg check failed - not available")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            self.logger.warning(f"FFmpeg not found: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Error checking FFmpeg availability: {e}")
            return False

    def _configure_ydl_options(self) -> None:
        """
        Configure yt-dlp options based on FFmpeg availability
        """
        if self.ffmpeg_available:
            # Full options with FFmpeg post-processing
            self.ydl_opts = {
                'format': f'bestaudio[abr<={self.audio_quality}]/best[abr<={self.audio_quality}]',
                'outtmpl': str(self.download_path / '%(uploader)s - %(title)s.%(ext)s'),
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': self.audio_quality,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': self.audio_quality,
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }
                ],
                'embed_metadata': True,
                'add_metadata': True,
                'writeinfojson': False,
                'writesubtitles': False,
                'ignoreerrors': True,
                'no_warnings': False,
                'quiet': False
            }
        else:
            # Fallback options without FFmpeg post-processing
            self.logger.warning("FFmpeg not available. Using fallback download options without audio conversion.")
            self.ydl_opts = {
                'format': f'bestaudio[ext=m4a]/best[ext=mp4]/bestaudio/best',
                'outtmpl': str(self.download_path / '%(uploader)s - %(title)s.%(ext)s'),
                'writeinfojson': False,
                'writesubtitles': False,
                'ignoreerrors': True,
                'no_warnings': False,
                'quiet': False
            }

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to be safe for filesystem
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)        # Replace multiple spaces with single space
        filename = re.sub(r'\s+', ' ', filename)
        # Trim whitespace
        filename = filename.strip()
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def search_and_download_track(self, track: Track, search_engines: Optional[List[str]] = None,
                                  playlist_folder: Optional[Path] = None) -> DownloadResult:
        """
        Search for and download a track from various sources
        
        Args:
            track: Track object to download
            search_engines: List of search engines to use (youtube, soundcloud, etc.)
            playlist_folder: Optional specific folder for playlist-organized downloads
            
        Returns:
            DownloadResult object
        """
        if not YT_DLP_AVAILABLE:
            return DownloadResult(
                success=False,
                track=track,
                error_message="yt-dlp is not available. Please install it to enable downloads."
            )
        
        # Determine download path - use playlist folder if provided, otherwise default
        download_path = playlist_folder if playlist_folder is not None else self.download_path
        download_path.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists - if so, skip download (ONE FILE PER SONG)
        expected_filename = self.sanitize_filename(f"{track.artist} - {track.title}.mp3")
        expected_path = download_path / expected_filename
        
        if expected_path.exists():
            self.logger.info(f"File already exists, skipping download: {expected_filename}")
            return DownloadResult(
                success=True,
                track=track,
                file_path=str(expected_path),
                duration=0.0,  # Could read from file if needed
                file_size=expected_path.stat().st_size
            )
        
        if search_engines is None:
            search_engines = ['youtube', 'soundcloud']
        
        # Create search query
        query = f"{track.artist} {track.title}"
        if track.album:
            query += f" {track.album}"
        
        # Try each search engine
        for engine in search_engines:
            try:
                result = self._download_from_engine(track, query, engine, download_path)
                if result.success:
                    return result
            except Exception as e:
                self.logger.warning(f"Failed to download from {engine}: {e}")
                continue
        
        return DownloadResult(
            success=False,
            track=track,
            error_message="Could not find track on any supported platform"
        )

    def download_playlist(self, playlist_info, playlist_folder: Path, 
                         search_engines: Optional[List[str]] = None) -> List[DownloadResult]:
        """
        Download all tracks from a playlist to a specific folder
        
        Args:
            playlist_info: PlaylistInfo object containing tracks
            playlist_folder: Folder path for the playlist downloads
            search_engines: List of search engines to use
            
        Returns:
            List of DownloadResult objects
        """
        from ..utils.config import save_playlist_manifest
        
        # Ensure playlist folder exists
        playlist_folder.mkdir(parents=True, exist_ok=True)
        
        results = []
        downloaded_tracks = []
        
        self.logger.info(f"Starting download of {len(playlist_info.tracks)} tracks to {playlist_folder}")
        
        for i, track in enumerate(playlist_info.tracks):
            self.logger.info(f"Downloading {i+1}/{len(playlist_info.tracks)}: {track.artist} - {track.title}")
            
            result = self.search_and_download_track(
                track, 
                search_engines=search_engines, 
                playlist_folder=playlist_folder
            )
            results.append(result)
            
            if result.success:
                downloaded_tracks.append(track)
        
        # Save playlist manifest with download results
        save_playlist_manifest(playlist_folder, playlist_info, downloaded_tracks)
        
        successful = len(downloaded_tracks)
        total = len(playlist_info.tracks)
        self.logger.info(f"Playlist download complete: {successful}/{total} tracks downloaded to {playlist_folder}")
        
        return results
    def _download_from_engine(self, track: Track, query: str, engine: str, download_path: Path = None) -> DownloadResult:
        """
        Download from a specific search engine
        
        Args:
            track: Track object
            query: Search query
            engine: Search engine name
            download_path: Specific download path (defaults to self.download_path)
            
        Returns:
            DownloadResult object
        """
        if not YT_DLP_AVAILABLE or yt_dlp is None:
            return DownloadResult(
                success=False,
                track=track,
                error_message="yt-dlp is not available"
            )
        
        if download_path is None:
            download_path = self.download_path
            
        search_url = self._get_search_url(query, engine)
        
        # Create a temporary directory for this download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_opts = self.ydl_opts.copy()
            sanitized_name = self.sanitize_filename(f"{track.artist} - {track.title}")
            temp_opts['outtmpl'] = os.path.join(temp_dir, f"{sanitized_name}.%(ext)s")
            
            try:
                with yt_dlp.YoutubeDL(temp_opts) as ydl:
                    # Search and get the first result
                    search_results = ydl.extract_info(
                        search_url,
                        download=False,
                        process=False
                    )
                    
                    if not search_results or 'entries' not in search_results:
                        raise DownloadError("No search results found")
                    
                    # Get the first entry
                    first_entry = None
                    for entry in search_results['entries']:
                        if entry:
                            first_entry = entry
                            break
                    
                    if not first_entry:
                        raise DownloadError("No valid entries found")
                    
                    # Download the first result
                    video_url = first_entry['url'] if 'url' in first_entry else first_entry['webpage_url']
                    
                    # Download the audio
                    info = ydl.extract_info(video_url, download=True)
                      # Find the downloaded file
                    downloaded_files = list(Path(temp_dir).glob("*"))
                    if not downloaded_files:
                        raise DownloadError("No files were downloaded")
                    
                    downloaded_file = downloaded_files[0]
                    
                    # Determine final filename based on FFmpeg availability
                    if self.ffmpeg_available:
                        final_filename = self.sanitize_filename(f"{track.artist} - {track.title}.mp3")
                    else:
                        # Keep original extension if FFmpeg is not available
                        original_ext = downloaded_file.suffix
                        final_filename = self.sanitize_filename(f"{track.artist} - {track.title}{original_ext}")
                    
                    # Move file to final destination
                    final_path = download_path / final_filename
                    
                    # Ensure destination directory exists
                    final_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    downloaded_file.replace(final_path)
                    
                    # Get file info
                    file_size = final_path.stat().st_size
                    duration = info.get('duration', 0.0) if info else 0.0
                    
                    self.logger.info(f"Successfully downloaded: {final_filename}")
                    
                    return DownloadResult(
                        success=True,
                        track=track,
                        file_path=str(final_path),
                        duration=duration,
                        file_size=file_size
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to download from {engine}: {e}")
                return DownloadResult(
                    success=False,
                    track=track,
                    error_message=f"Download failed: {e}"
                )
                    
            except Exception as e:
                self.logger.error(f"Download failed: {e}")
                return DownloadResult(
                    success=False,
                    track=track,
                    error_message=str(e)
                )
    
    def _get_search_url(self, query: str, engine: str) -> str:
        """
        Get search URL for the specified engine
        
        Args:
            query: Search query
            engine: Search engine name
            
        Returns:
            Search URL
        """
        encoded_query = query.replace(' ', '+')
        
        if engine == 'youtube':
            return f"ytsearch1:{query}"
        elif engine == 'soundcloud':
            return f"scsearch1:{query}"
        else:
            # Default to YouTube
            return f"ytsearch1:{query}"
    
    def download_tracks_batch(self, tracks: List[Track], 
                             max_concurrent: int = 3) -> List[DownloadResult]:
        """
        Download multiple tracks
        
        Args:
            tracks: List of tracks to download
            max_concurrent: Maximum concurrent downloads
            
        Returns:
            List of DownloadResult objects
        """
        results = []
        
        for i, track in enumerate(tracks):
            self.logger.info(f"Downloading {i+1}/{len(tracks)}: {track}")
            result = self.search_and_download_track(track)
            results.append(result)
            
            if result.success:
                self.logger.info(f"Successfully downloaded: {result.file_path}")
            else:
                self.logger.error(f"Failed to download {track}: {result.error_message}")
        
        return results
    
    def get_download_statistics(self, results: List[DownloadResult]) -> Dict[str, Any]:
        """
        Get statistics about download results
        
        Args:
            results: List of download results
            
        Returns:
            Dictionary with statistics
        """
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        total_size = sum(r.file_size for r in successful)
        total_duration = sum(r.duration for r in successful)
        
        return {
            'total_tracks': len(results),
            'successful_downloads': len(successful),
            'failed_downloads': len(failed),
            'success_rate': len(successful) / len(results) * 100 if results else 0,
            'total_file_size': total_size,
            'total_duration': total_duration,
            'average_file_size': total_size / len(successful) if successful else 0,
            'average_duration': total_duration / len(successful) if successful else 0
        }
    def convert_to_mono(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """
        Convert an audio file to mono
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output file (optional, will overwrite input if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ffmpeg_available:
            self.logger.warning("FFmpeg not available, skipping mono conversion")
            return False
            
        try:
            import subprocess
            
            input_path = Path(input_file)
            if not input_path.exists():
                self.logger.error(f"Input file does not exist: {input_file}")
                return False
            
            if output_file is None:
                output_file = input_file
              # Use FFmpeg to convert to mono
            ffmpeg_cmd = FFMPEG_PATH if FFMPEG_PACKAGE_AVAILABLE else 'ffmpeg'
            cmd = [
                ffmpeg_cmd, '-i', str(input_path), 
                '-ac', '1',  # 1 audio channel (mono)
                '-y',  # Overwrite output file
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Successfully converted {input_file} to mono")
                return True
            else:
                self.logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error converting to mono: {e}")
            return False
    
    def enhance_metadata(self, file_path: str, track: Track) -> bool:
        """
        Enhance metadata for an audio file
        
        Args:
            file_path: Path to the audio file
            track: Track object with metadata
            
        Returns:
            True if successful, False otherwise        """
        try:
            # Try to use mutagen for metadata (simplified approach)
            try:
                from mutagen.mp3 import MP3
                
                audio = MP3(file_path)
                
                # Set basic metadata using the simple interface
                if hasattr(audio, 'tags') and audio.tags is not None:
                    if track.title:
                        audio.tags['TIT2'] = track.title
                    if track.artist:
                        audio.tags['TPE1'] = track.artist
                    if track.album:
                        audio.tags['TALB'] = track.album
                    
                    audio.save()
                    self.logger.info(f"Enhanced metadata for {file_path}")
                    return True
                else:
                    # No tags, fallback to FFmpeg
                    return self._enhance_metadata_ffmpeg(file_path, track)
                
            except ImportError:
                # Fallback to FFmpeg for metadata
                self.logger.warning("mutagen not available, using FFmpeg for metadata")
                return self._enhance_metadata_ffmpeg(file_path, track)
                
        except Exception as e:
            self.logger.error(f"Error enhancing metadata: {e}")
            return False
    
    def _enhance_metadata_ffmpeg(self, file_path: str, track: Track) -> bool:
        """
        Enhance metadata using FFmpeg
        
        Args:
            file_path: Path to the audio file
            track: Track object with metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import subprocess
            import tempfile
            
            input_path = Path(file_path)
              # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            ffmpeg_cmd = FFMPEG_PATH if FFMPEG_PACKAGE_AVAILABLE else 'ffmpeg'
            cmd = [ffmpeg_cmd, '-i', str(input_path)]
            
            # Add metadata
            if track.title:
                cmd.extend(['-metadata', f'title={track.title}'])
            if track.artist:
                cmd.extend(['-metadata', f'artist={track.artist}'])
            if track.album:
                cmd.extend(['-metadata', f'album={track.album}'])
            
            cmd.extend(['-codec', 'copy', '-y', temp_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Replace original file with enhanced version
                Path(temp_path).replace(input_path)
                self.logger.info(f"Enhanced metadata for {file_path} using FFmpeg")
                return True
            else:
                # Clean up temp file
                try:
                    Path(temp_path).unlink()
                except:
                    pass
                self.logger.error(f"FFmpeg metadata error: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error enhancing metadata with FFmpeg: {e}")
            return False
    
    def batch_convert_to_mono(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Convert multiple audio files to mono
        
        Args:
            file_paths: List of file paths to convert
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        for file_path in file_paths:
            self.logger.info(f"Converting to mono: {file_path}")
            success = self.convert_to_mono(file_path)
            results[file_path] = success
            
        return results
    
    def batch_enhance_metadata(self, file_paths: List[str], tracks: List[Track]) -> Dict[str, bool]:
        """
        Enhance metadata for multiple audio files
        
        Args:
            file_paths: List of file paths
            tracks: List of corresponding Track objects
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        for file_path, track in zip(file_paths, tracks):
            self.logger.info(f"Enhancing metadata: {file_path}")
            success = self.enhance_metadata(file_path, track)
            results[file_path] = success
            
        return results
