"""
Basic tests for TTSMixmaster modules
"""

import unittest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from api.lastfm_client import Track, Playlist
from utils.config import AppConfig


class TestTrack(unittest.TestCase):
    """Test Track dataclass"""
    
    def test_track_creation(self):
        """Test basic track creation"""
        track = Track(
            title="Test Song",
            artist="Test Artist",
            album="Test Album"
        )
        
        self.assertEqual(track.title, "Test Song")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(str(track), "Test Artist - Test Song")


class TestPlaylist(unittest.TestCase):
    """Test Playlist dataclass"""
    
    def test_playlist_creation(self):
        """Test basic playlist creation"""
        tracks = [
            Track("Song 1", "Artist 1"),
            Track("Song 2", "Artist 2"),
        ]
        
        playlist = Playlist(
            name="Test Playlist",
            tracks=tracks,
            description="A test playlist"
        )
        
        self.assertEqual(playlist.name, "Test Playlist")
        self.assertEqual(len(playlist.tracks), 2)
        self.assertEqual(playlist.total_tracks, 2)


class TestAppConfig(unittest.TestCase):
    """Test AppConfig dataclass"""
    
    def test_config_creation(self):
        """Test basic config creation"""
        config = AppConfig(
            lastfm_api_key="test_key",
            lastfm_username="test_user"
        )
        
        self.assertEqual(config.lastfm_api_key, "test_key")
        self.assertEqual(config.lastfm_username, "test_user")
        self.assertEqual(config.audio_quality, "192")  # default value


if __name__ == "__main__":
    unittest.main()
