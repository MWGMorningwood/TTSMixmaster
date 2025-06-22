"""
Spotify API Integration Module

This module provides functionality to interact with the Spotify Web API
to retrieve playlists and track information.
"""

import os
import base64
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

from .base_service import BaseMusicService, Track, PlaylistInfo, ServiceType, PlaylistType


class SpotifyService(BaseMusicService):
    """Spotify API client for retrieving playlists and tracks"""
    
    def __init__(self, client_id: str, client_secret: str, user_id: str = ""):
        """
        Initialize the Spotify API client
        
        Args:
            client_id: Spotify Client ID
            client_secret: Spotify Client Secret
            user_id: Default user ID for user operations
        """
        super().__init__(ServiceType.SPOTIFY)
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = user_id
        self.access_token = None
        self.base_url = "https://api.spotify.com/v1"
          # Authenticate using Client Credentials flow
        if client_id and client_secret:
            print(f"Attempting to authenticate Spotify with client ID: {client_id[:10]}...")
            if self._authenticate():
                print("Spotify authentication successful")
            else:
                print("Spotify authentication failed")
        else:
            print("Spotify credentials not provided - service will not be available")
    
    def _authenticate(self) -> bool:
        """
        Authenticate using the Client Credentials flow
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Encode client credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            # Request access token
            headers = {
                "Authorization": f"Basic {credentials_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "client_credentials"
            }
            
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                return True
            else:
                print(f"Spotify authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Spotify authentication error: {e}")
            return False
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make authenticated request to Spotify API
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            
        Returns:
            JSON response data or None if failed
        """
        if not self.access_token:
            if not self._authenticate():
                return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expired, try to re-authenticate
                if self._authenticate():
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    response = requests.get(url, headers=headers, params=params)
                    if response.status_code == 200:
                        return response.json()
            
            print(f"Spotify API request failed: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"Spotify API request error: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test the Spotify API connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Try to get featured playlists as a test
            response = self._make_request("browse/featured-playlists", {"limit": 1})
            return response is not None
        except Exception:
            return False
    
    def get_user_playlists(self, **kwargs) -> List[PlaylistInfo]:
        """
        Get user's playlists/collections
        
        Returns:
            List of available playlists
        """
        playlists = []
        
        # If user ID is provided, try to get user playlists
        if self.user_id:
            try:
                user_playlists = self._get_user_playlists()
                playlists.extend(user_playlists)
            except Exception as e:
                print(f"Failed to get user playlists: {e}")
        
        return playlists
    
    def _get_user_playlists(self) -> List[PlaylistInfo]:
        """Get playlists for a specific user"""
        playlists = []
        
        try:
            response = self._make_request(f"users/{self.user_id}/playlists", {"limit": 50})
            
            if response and "items" in response:
                for item in response["items"]:
                    playlist_info = PlaylistInfo(
                        name=item["name"],
                        tracks=[],  # Will be populated later if needed
                        description=item.get("description", ""),
                        service_type=ServiceType.SPOTIFY,
                        playlist_type=PlaylistType.SPOTIFY_PLAYLIST,
                        total_tracks=item["tracks"]["total"],
                        service_id=item["id"],
                        owner=item["owner"]["display_name"]
                    )
                    playlists.append(playlist_info)
        
        except Exception as e:
            print(f"Error getting user playlists: {e}")
        
        return playlists
    def get_playlist_tracks(self, playlist_id: str, **kwargs) -> PlaylistInfo:
        """
        Get tracks from a specific playlist
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            PlaylistInfo with tracks
        """
        tracks = []
        playlist_name = "Spotify Playlist"
        playlist_description = ""
        
        try:
            # First get playlist info
            playlist_response = self._make_request(f"playlists/{playlist_id}")
            if playlist_response:
                playlist_name = playlist_response.get("name", "Spotify Playlist")
                playlist_description = playlist_response.get("description", "")
            
            # Get playlist tracks
            response = self._make_request(f"playlists/{playlist_id}/tracks", {"limit": 100})
            
            if response and "items" in response:
                for item in response["items"]:
                    track_data = item.get("track")
                    if track_data and track_data.get("type") == "track":
                        # Build artist string
                        artists = [artist["name"] for artist in track_data.get("artists", [])]
                        artist_str = ", ".join(artists)
                        track = Track(
                            artist=artist_str,
                            title=track_data.get("name", "Unknown"),
                            album=track_data.get("album", {}).get("name", "Unknown"),
                            url=track_data.get("external_urls", {}).get("spotify", ""),
                            duration=track_data.get("duration_ms", 0) // 1000,  # Convert to seconds
                            service_id=track_data.get("id", ""),
                            service_type=ServiceType.SPOTIFY
                        )
                        tracks.append(track)
            
            # Handle pagination if needed
            while response and response.get("next"):
                next_url = response["next"]
                # Extract just the endpoint from the full URL
                endpoint = next_url.replace(self.base_url + "/", "")
                response = self._make_request(endpoint)
                
                if response and "items" in response:
                    for item in response["items"]:
                        track_data = item.get("track")
                        if track_data and track_data.get("type") == "track":
                            # Build artist string
                            artists = [artist["name"] for artist in track_data.get("artists", [])]
                            artist_str = ", ".join(artists)
                            track = Track(
                                artist=artist_str,
                                title=track_data.get("name", "Unknown"),
                                album=track_data.get("album", {}).get("name", "Unknown"),
                                url=track_data.get("external_urls", {}).get("spotify", ""),
                                duration=track_data.get("duration_ms", 0) // 1000,
                                service_id=track_data.get("id", ""),
                                service_type=ServiceType.SPOTIFY                            )
                            tracks.append(track)
        
        except Exception as e:
            print(f"Error getting playlist tracks: {e}")
        
        # Return PlaylistInfo with tracks
        return PlaylistInfo(
            name=playlist_name,
            tracks=tracks,
            description=playlist_description,
            service_type=ServiceType.SPOTIFY,
            playlist_type=PlaylistType.SPOTIFY_PLAYLIST,
            service_id=playlist_id
        )
    
    def search_playlists(self, query: str, limit: int = 20) -> List[PlaylistInfo]:
        """
        Search for playlists on Spotify
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of found playlists
        """
        playlists = []
        
        try:
            params = {
                "q": query,
                "type": "playlist",
                "limit": min(limit, 50)  # Spotify API limit
            }
            
            response = self._make_request("search", params)
            
            if response and "playlists" in response:
                for item in response["playlists"]["items"]:
                    playlist_info = PlaylistInfo(
                        name=item["name"],
                        tracks=[],  # Will be populated later if needed
                        description=item.get("description", ""),
                        service_type=ServiceType.SPOTIFY,
                        playlist_type=PlaylistType.SPOTIFY_PLAYLIST,
                        total_tracks=item["tracks"]["total"],
                        service_id=item["id"],
                        owner=item["owner"]["display_name"]
                    )
                    playlists.append(playlist_info)
        
        except Exception as e:
            print(f"Error searching playlists: {e}")
        
        return playlists
