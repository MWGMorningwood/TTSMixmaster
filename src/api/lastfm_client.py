"""
Last.fm API Integration Module

This module provides functionality to interact with the Last.fm API
to retrieve user playlists, track information, and user data.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlencode
import time


@dataclass
class Track:
    """Represents a music track from Last.fm"""
    title: str
    artist: str
    album: str = ""
    duration: int = 0  # in seconds
    url: str = ""
    mbid: str = ""  # MusicBrainz ID
    playcount: int = 0
    
    def __str__(self):
        return f"{self.artist} - {self.title}"


@dataclass
class Playlist:
    """Represents a playlist or collection of tracks"""
    name: str
    tracks: List[Track]
    description: str = ""
    total_tracks: int = 0
    
    def __post_init__(self):
        if self.total_tracks == 0:
            self.total_tracks = len(self.tracks)


class LastFMAPI:
    """Last.fm API client for retrieving user data and playlists"""
    
    BASE_URL = "http://ws.audioscrobbler.com/2.0/"
    
    def __init__(self, api_key: str, api_secret: str = "", username: str = ""):
        """
        Initialize the Last.fm API client
        
        Args:
            api_key: Last.fm API key
            api_secret: Last.fm API secret (optional, for write operations)
            username: Default username for API calls
        """
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
    
    def get_user_top_tracks(self, username: str = None, period: str = "overall", 
                           limit: int = 50, page: int = 1) -> List[Track]:
        """
        Get user's top tracks
        
        Args:
            username: Last.fm username (uses default if not provided)
            period: Time period (overall, 7day, 1month, 3month, 6month, 12month)
            limit: Number of tracks to retrieve (max 1000)
            page: Page number for pagination
            
        Returns:
            List of Track objects
        """
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
                    mbid=track_data.get('mbid', ''),
                    playcount=int(track_data.get('playcount', 0))
                )
                tracks.append(track)
        
        return tracks
    
    def get_user_loved_tracks(self, username: str = None, limit: int = 50, 
                             page: int = 1) -> List[Track]:
        """
        Get user's loved tracks
        
        Args:
            username: Last.fm username (uses default if not provided)
            limit: Number of tracks to retrieve (max 1000)
            page: Page number for pagination
            
        Returns:
            List of Track objects
        """
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
                    mbid=track_data.get('mbid', '')
                )
                tracks.append(track)
        
        return tracks
    
    def get_user_recent_tracks(self, username: str = None, limit: int = 50, 
                              page: int = 1) -> List[Track]:
        """
        Get user's recent tracks
        
        Args:
            username: Last.fm username (uses default if not provided)
            limit: Number of tracks to retrieve (max 200)
            page: Page number for pagination
            
        Returns:
            List of Track objects
        """
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
                # Skip currently playing tracks
                if '@attr' in track_data and 'nowplaying' in track_data['@attr']:
                    continue
                    
                track = Track(
                    title=track_data.get('name', ''),
                    artist=track_data.get('artist', {}).get('#text', '') if isinstance(track_data.get('artist'), dict) else str(track_data.get('artist', '')),
                    album=track_data.get('album', {}).get('#text', '') if isinstance(track_data.get('album'), dict) else str(track_data.get('album', '')),
                    url=track_data.get('url', ''),
                    mbid=track_data.get('mbid', '')
                )
                tracks.append(track)
        
        return tracks
    
    def search_tracks(self, query: str, limit: int = 30, page: int = 1) -> List[Track]:
        """
        Search for tracks
        
        Args:
            query: Search query
            limit: Number of results to retrieve
            page: Page number for pagination
            
        Returns:
            List of Track objects
        """
        params = {
            'track': query,
            'limit': limit,
            'page': page
        }
        
        data = self._make_request('track.search', params)
        
        tracks = []
        if 'results' in data and 'trackmatches' in data['results'] and 'track' in data['results']['trackmatches']:
            for track_data in data['results']['trackmatches']['track']:
                track = Track(
                    title=track_data.get('name', ''),
                    artist=track_data.get('artist', ''),
                    url=track_data.get('url', ''),
                    mbid=track_data.get('mbid', '')
                )
                tracks.append(track)
        
        return tracks
    
    def get_track_info(self, artist: str, track: str, username: str = None) -> Optional[Track]:
        """
        Get detailed information about a specific track
        
        Args:
            artist: Artist name
            track: Track name
            username: Username for user-specific data (optional)
            
        Returns:
            Track object with detailed information
        """
        params = {
            'artist': artist,
            'track': track
        }
        
        if username:
            params['username'] = username
        
        try:
            data = self._make_request('track.getinfo', params)
            
            if 'track' in data:
                track_data = data['track']
                return Track(
                    title=track_data.get('name', ''),
                    artist=track_data.get('artist', {}).get('name', '') if isinstance(track_data.get('artist'), dict) else str(track_data.get('artist', '')),
                    album=track_data.get('album', {}).get('title', '') if track_data.get('album') else '',
                    duration=int(track_data.get('duration', 0)) // 1000,  # Convert from ms to seconds
                    url=track_data.get('url', ''),
                    mbid=track_data.get('mbid', ''),
                    playcount=int(track_data.get('playcount', 0))
                )
        except Exception:
            # Return None if track not found or error occurs
            pass
        
        return None
    
    def create_playlist_from_top_tracks(self, period: str = "overall", 
                                       limit: int = 50, username: str = None) -> Playlist:
        """
        Create a playlist from user's top tracks
        
        Args:
            period: Time period for top tracks
            limit: Number of tracks to include
            username: Last.fm username
            
        Returns:
            Playlist object
        """
        tracks = self.get_user_top_tracks(username, period, limit)
        
        playlist_name = f"Top Tracks ({period.title()})"
        return Playlist(
            name=playlist_name,
            tracks=tracks,
            description=f"Your top {len(tracks)} tracks from {period}"
        )
    
    def create_playlist_from_loved_tracks(self, limit: int = 50, 
                                         username: str = None) -> Playlist:
        """
        Create a playlist from user's loved tracks
        
        Args:
            limit: Number of tracks to include
            username: Last.fm username
            
        Returns:
            Playlist object
        """
        tracks = self.get_user_loved_tracks(username, limit)
        
        return Playlist(
            name="Loved Tracks",
            tracks=tracks,
            description=f"Your {len(tracks)} most loved tracks"
        )
