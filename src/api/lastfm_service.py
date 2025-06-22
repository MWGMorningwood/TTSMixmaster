"""
Updated Last.fm API Integration Module

This module provides functionality to interact with the Last.fm API
using the new base service interface.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import time

from .base_service import BaseMusicService, Track, PlaylistInfo, ServiceType, PlaylistType


class LastFMService(BaseMusicService):
    """Last.fm API client for retrieving user collections (not real playlists)"""
    
    BASE_URL = "http://ws.audioscrobbler.com/2.0/"
    
    def __init__(self, api_key: str, api_secret: str = "", username: str = ""):
        """
        Initialize the Last.fm API client
        
        Args:
            api_key: Last.fm API key
            api_secret: Last.fm API secret (optional, for write operations)
            username: Default username for API calls
        """
        super().__init__(ServiceType.LASTFM)
        self.api_key = api_key
        self.api_secret = api_secret
        self.username = username
        self.session = requests.Session()
        
    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Last.fm API
        
        Args:
            method: API method to call
            params: Parameters for the API call
            
        Returns:
            JSON response from the API
        """
        params.update({
            'method': method,
            'api_key': self.api_key,
            'format': 'json'
        })
        
        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                raise Exception(f"Last.fm API Error {data['error']}: {data.get('message', 'Unknown error')}")
                
            return data
            
        except requests.RequestException as e:
            raise Exception(f"Network error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")
    
    def test_connection(self) -> bool:
        """Test if the Last.fm connection is working"""
        try:
            if not self.username:
                return False
            
            # Try to get user info
            params = {'user': self.username}
            self._make_request('user.getinfo', params)
            return True
        except:
            return False
    
    def get_supported_playlist_types(self) -> List[PlaylistType]:
        """Get list of supported collection types for Last.fm"""
        return [
            PlaylistType.LASTFM_TOP_TRACKS,
            PlaylistType.LASTFM_LOVED_TRACKS,
            PlaylistType.LASTFM_RECENT_TRACKS
        ]
    
    def get_user_playlists(self, **kwargs) -> List[PlaylistInfo]:
        """
        Get user's collections (Last.fm doesn't have real playlists)
        
        Returns:
            List of available collections (Top Tracks, Loved Tracks, Recent Tracks)
        """
        collections = []
        
        # Add Top Tracks collection
        collections.append(PlaylistInfo(
            name="Top Tracks",
            tracks=[],  # Tracks loaded on demand
            description="Your most played tracks",
            service_type=ServiceType.LASTFM,
            playlist_type=PlaylistType.LASTFM_TOP_TRACKS,
            service_id="top_tracks",
            owner=self.username
        ))
        
        # Add Loved Tracks collection
        collections.append(PlaylistInfo(
            name="Loved Tracks",
            tracks=[],  # Tracks loaded on demand
            description="Your loved tracks on Last.fm",
            service_type=ServiceType.LASTFM,
            playlist_type=PlaylistType.LASTFM_LOVED_TRACKS,
            service_id="loved_tracks",
            owner=self.username
        ))
        
        # Add Recent Tracks collection
        collections.append(PlaylistInfo(
            name="Recent Tracks",
            tracks=[],  # Tracks loaded on demand
            description="Your recently played tracks",
            service_type=ServiceType.LASTFM,
            playlist_type=PlaylistType.LASTFM_RECENT_TRACKS,
            service_id="recent_tracks",
            owner=self.username
        ))
        
        return collections
    
    def get_playlist_tracks(self, playlist_id: str, **kwargs) -> PlaylistInfo:
        """
        Get tracks from a specific Last.fm collection
        
        Args:
            playlist_id: Collection ID (top_tracks, loved_tracks, recent_tracks)
            **kwargs: Additional parameters like period, limit
            
        Returns:
            PlaylistInfo with tracks loaded
        """
        limit = kwargs.get('limit', 50)
        period = kwargs.get('period', 'overall')
        
        if playlist_id == "top_tracks":
            tracks = self._get_user_top_tracks(period=period, limit=limit)
            return PlaylistInfo(
                name=f"Top Tracks ({period})",
                tracks=tracks,
                description=f"Your top {limit} tracks from {period}",
                service_type=ServiceType.LASTFM,
                playlist_type=PlaylistType.LASTFM_TOP_TRACKS,
                service_id=playlist_id,
                owner=self.username
            )
        
        elif playlist_id == "loved_tracks":
            tracks = self._get_user_loved_tracks(limit=limit)
            return PlaylistInfo(
                name="Loved Tracks",
                tracks=tracks,
                description=f"Your {len(tracks)} loved tracks on Last.fm",
                service_type=ServiceType.LASTFM,
                playlist_type=PlaylistType.LASTFM_LOVED_TRACKS,
                service_id=playlist_id,
                owner=self.username
            )
        
        elif playlist_id == "recent_tracks":
            tracks = self._get_user_recent_tracks(limit=limit)
            return PlaylistInfo(
                name="Recent Tracks",
                tracks=tracks,
                description=f"Your {len(tracks)} most recent tracks",
                service_type=ServiceType.LASTFM,
                playlist_type=PlaylistType.LASTFM_RECENT_TRACKS,
                service_id=playlist_id,
                owner=self.username
            )
        
        else:
            raise ValueError(f"Unknown playlist ID: {playlist_id}")
    
    def search_playlists(self, query: str, limit: int = 20) -> List[PlaylistInfo]:
        """Last.fm doesn't support playlist search (no real playlists)"""
        return []
    
    def _get_user_top_tracks(self, username: str = None, period: str = "overall", 
                           limit: int = 50, page: int = 1) -> List[Track]:
        """Get user's top tracks"""
        if not username:
            username = self.username
            
        if not username:
            raise ValueError("Username is required")
        
        params = {
            'user': username,
            'period': period,
            'limit': limit,
            'page': page
        }
        
        data = self._make_request('user.gettoptracks', params)
        
        tracks = []
        if 'toptracks' in data and 'track' in data['toptracks']:
            for track_data in data['toptracks']['track']:
                track = Track(
                    title=track_data.get('name', ''),
                    artist=track_data.get('artist', {}).get('name', '') if isinstance(track_data.get('artist'), dict) else str(track_data.get('artist', '')),
                    url=track_data.get('url', ''),
                    service_id=track_data.get('mbid', ''),
                    service_type=ServiceType.LASTFM,
                    playcount=int(track_data.get('playcount', 0))
                )
                tracks.append(track)
        
        return tracks
    
    def _get_user_loved_tracks(self, username: str = None, limit: int = 50, 
                             page: int = 1) -> List[Track]:
        """Get user's loved tracks"""
        if not username:
            username = self.username
            
        if not username:
            raise ValueError("Username is required")
        
        params = {
            'user': username,
            'limit': limit,
            'page': page
        }
        
        data = self._make_request('user.getlovedtracks', params)
        
        tracks = []
        if 'lovedtracks' in data and 'track' in data['lovedtracks']:
            for track_data in data['lovedtracks']['track']:
                track = Track(
                    title=track_data.get('name', ''),
                    artist=track_data.get('artist', {}).get('name', '') if isinstance(track_data.get('artist'), dict) else str(track_data.get('artist', '')),
                    url=track_data.get('url', ''),
                    service_id=track_data.get('mbid', ''),
                    service_type=ServiceType.LASTFM
                )
                tracks.append(track)
        
        return tracks
    
    def _get_user_recent_tracks(self, username: str = None, limit: int = 50, 
                              page: int = 1) -> List[Track]:
        """Get user's recent tracks"""
        if not username:
            username = self.username
            
        if not username:
            raise ValueError("Username is required")
        
        params = {
            'user': username,
            'limit': limit,
            'page': page
        }
        
        data = self._make_request('user.getrecenttracks', params)
        
        tracks = []
        if 'recenttracks' in data and 'track' in data['recenttracks']:
            for track_data in data['recenttracks']['track']:
                # Skip currently playing track
                if track_data.get('@attr', {}).get('nowplaying') == 'true':
                    continue
                    
                track = Track(
                    title=track_data.get('name', ''),
                    artist=track_data.get('artist', {}).get('#text', '') if isinstance(track_data.get('artist'), dict) else str(track_data.get('artist', '')),
                    album=track_data.get('album', {}).get('#text', '') if isinstance(track_data.get('album'), dict) else str(track_data.get('album', '')),
                    url=track_data.get('url', ''),
                    service_id=track_data.get('mbid', ''),
                    service_type=ServiceType.LASTFM
                )
                tracks.append(track)
        
        return tracks


# Legacy compatibility - keep the old classes for existing code
from .lastfm_client import LastFMAPI, Track as OldTrack, Playlist as OldPlaylist
