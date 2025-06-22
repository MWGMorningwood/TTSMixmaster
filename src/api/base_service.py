"""
Base Service Interface

This module provides the base interface for all music service APIs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ServiceType(Enum):
    """Enum for different service types"""
    LASTFM = "lastfm"
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"


class PlaylistType(Enum):
    """Enum for different playlist/collection types"""
    # LastFM specific (not real playlists, but collections)
    LASTFM_TOP_TRACKS = "lastfm_top_tracks"
    LASTFM_LOVED_TRACKS = "lastfm_loved_tracks"
    LASTFM_RECENT_TRACKS = "lastfm_recent_tracks"
    
    # YouTube specific
    YOUTUBE_PLAYLIST = "youtube_playlist"
    YOUTUBE_LIKED_VIDEOS = "youtube_liked_videos"
    YOUTUBE_WATCH_LATER = "youtube_watch_later"
    
    # Spotify specific
    SPOTIFY_PLAYLIST = "spotify_playlist"
    SPOTIFY_LIKED_SONGS = "spotify_liked_songs"
    SPOTIFY_RECENTLY_PLAYED = "spotify_recently_played"
    SPOTIFY_TOP_TRACKS = "spotify_top_tracks"


@dataclass
class Track:
    """Represents a music track from any service"""
    title: str
    artist: str
    album: str = ""
    duration: int = 0  # in seconds
    url: str = ""
    service_id: str = ""  # Service-specific ID
    service_type: ServiceType = ServiceType.LASTFM
    playcount: int = 0
    thumbnail_url: str = ""
    
    def __str__(self):
        return f"{self.artist} - {self.title}"


@dataclass
class PlaylistInfo:
    """Represents a playlist or collection of tracks"""
    name: str
    tracks: List[Track]
    description: str = ""
    total_tracks: int = 0
    service_type: ServiceType = ServiceType.LASTFM
    playlist_type: PlaylistType = PlaylistType.LASTFM_TOP_TRACKS
    service_id: str = ""  # Service-specific playlist ID
    thumbnail_url: str = ""
    owner: str = ""
    
    def __post_init__(self):
        if self.total_tracks == 0:
            self.total_tracks = len(self.tracks)


class BaseMusicService(ABC):
    """Base class for all music service APIs"""
    
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the service connection is working"""
        pass
    
    @abstractmethod
    def get_user_playlists(self, **kwargs) -> List[PlaylistInfo]:
        """Get user's playlists/collections"""
        pass
    
    @abstractmethod
    def get_playlist_tracks(self, playlist_id: str, **kwargs) -> PlaylistInfo:
        """Get tracks from a specific playlist"""
        pass
    
    @abstractmethod
    def search_playlists(self, query: str, limit: int = 20) -> List[PlaylistInfo]:
        """Search for public playlists"""
        pass
    
    def get_supported_playlist_types(self) -> List[PlaylistType]:
        """Get list of supported playlist types for this service"""
        return []
