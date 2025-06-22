"""
Main GUI Application Window

This module provides the main GUI interface for TTSMixmaster using CustomTkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import List, Optional, Dict, Any
import threading
import os
from pathlib import Path

from ..api.lastfm_client import LastFMAPI, Playlist, Track
from ..downloader.audio_downloader import AudioDownloader, DownloadResult
from ..uploader.azure_uploader import AzureBlobUploader, UploadResult
from ..tts_formatter.tts_formatter import TTSFormatter, TTSMusicPlayer
from ..utils.config import ConfigManager, AppConfig, setup_logging


class TTSMixmasterApp:
    """Main application class for TTSMixmaster GUI"""
    
    def __init__(self):
        """Initialize the application"""
        # Set up configuration
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        
        # Set up logging
        setup_logging()
        
        # Initialize API clients
        self.lastfm_api = None
        self.downloader = None
        self.uploader = None
        self.formatter = None
        
        # Initialize GUI
        self._setup_gui()
        
        # Data storage
        self.current_playlists: List[Playlist] = []
        self.download_results: List[DownloadResult] = []
        self.upload_results: List[UploadResult] = []
        
        # Load configuration
        self._load_config_to_gui()
        
    def _setup_gui(self):
        """Set up the main GUI interface"""
        # Set appearance mode and color theme
        ctk.set_appearance_mode(self.config.theme)
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("TTSMixmaster - Tabletop Simulator Music Manager")
        
        # Parse window size
        try:
            width, height = map(int, self.config.window_size.split('x'))
            self.root.geometry(f"{width}x{height}")
        except:
            self.root.geometry("1200x800")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_config_tab()
        self._create_playlist_tab()
        self._create_download_tab()
        self._create_upload_tab()
        self._create_format_tab()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_config_tab(self):
        """Create configuration tab"""
        tab = self.tabview.add("Configuration")
        
        # API Configuration Frame
        api_frame = ctk.CTkFrame(tab)
        api_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(api_frame, text="API Configuration", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Last.fm API settings
        lastfm_frame = ctk.CTkFrame(api_frame)
        lastfm_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lastfm_frame, text="Last.fm Settings").pack(anchor="w", padx=5, pady=2)
        
        self.lastfm_api_key_entry = ctk.CTkEntry(lastfm_frame, placeholder_text="Last.fm API Key")
        self.lastfm_api_key_entry.pack(fill="x", padx=5, pady=2)
        
        self.lastfm_api_secret_entry = ctk.CTkEntry(lastfm_frame, placeholder_text="Last.fm API Secret")
        self.lastfm_api_secret_entry.pack(fill="x", padx=5, pady=2)
        
        self.lastfm_username_entry = ctk.CTkEntry(lastfm_frame, placeholder_text="Last.fm Username")
        self.lastfm_username_entry.pack(fill="x", padx=5, pady=2)
          # Azure Storage settings
        azure_frame = ctk.CTkFrame(api_frame)
        azure_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(azure_frame, text="Azure Storage Settings").pack(anchor="w", padx=5, pady=2)
        
        self.azure_connection_entry = ctk.CTkEntry(azure_frame, placeholder_text="Azure Storage Connection String", show="*")
        self.azure_connection_entry.pack(fill="x", padx=5, pady=2)
        
        self.azure_container_entry = ctk.CTkEntry(azure_frame, placeholder_text="Container Name (default: tts-audio)")
        self.azure_container_entry.pack(fill="x", padx=5, pady=2)
        
        # Path Configuration Frame
        path_frame = ctk.CTkFrame(tab)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(path_frame, text="Path Configuration", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Download path
        download_frame = ctk.CTkFrame(path_frame)
        download_frame.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(download_frame, text="Download Path:").pack(anchor="w", padx=5)
        path_inner_frame = ctk.CTkFrame(download_frame)
        path_inner_frame.pack(fill="x", padx=5, pady=2)
        
        self.download_path_entry = ctk.CTkEntry(path_inner_frame)
        self.download_path_entry.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkButton(path_inner_frame, text="Browse", width=80,
                     command=lambda: self._browse_folder(self.download_path_entry)).pack(side="right", padx=2)
        
        # Upload path
        upload_frame = ctk.CTkFrame(path_frame)
        upload_frame.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(upload_frame, text="Upload Path:").pack(anchor="w", padx=5)
        path_inner_frame2 = ctk.CTkFrame(upload_frame)
        path_inner_frame2.pack(fill="x", padx=5, pady=2)
        
        self.upload_path_entry = ctk.CTkEntry(path_inner_frame2)
        self.upload_path_entry.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkButton(path_inner_frame2, text="Browse", width=80,
                     command=lambda: self._browse_folder(self.upload_path_entry)).pack(side="right", padx=2)
        
        # TTS output path
        tts_frame = ctk.CTkFrame(path_frame)
        tts_frame.pack(fill="x", padx=10, pady=2)
        
        ctk.CTkLabel(tts_frame, text="TTS Output Path:").pack(anchor="w", padx=5)
        path_inner_frame3 = ctk.CTkFrame(tts_frame)
        path_inner_frame3.pack(fill="x", padx=5, pady=2)
        
        self.tts_path_entry = ctk.CTkEntry(path_inner_frame3)
        self.tts_path_entry.pack(side="left", fill="x", expand=True, padx=2)
        
        ctk.CTkButton(path_inner_frame3, text="Browse", width=80,
                     command=lambda: self._browse_folder(self.tts_path_entry)).pack(side="right", padx=2)
        
        # Audio Settings Frame
        audio_frame = ctk.CTkFrame(tab)
        audio_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(audio_frame, text="Audio Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        quality_frame = ctk.CTkFrame(audio_frame)
        quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(quality_frame, text="Audio Quality:").pack(side="left", padx=5)
        self.audio_quality_var = ctk.StringVar(value="192")
        self.audio_quality_combo = ctk.CTkComboBox(quality_frame, values=["128", "192", "256", "320"],
                                                  variable=self.audio_quality_var)
        self.audio_quality_combo.pack(side="left", padx=5)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Save Configuration", command=self._save_config).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Test Last.fm Connection", command=self._test_lastfm_connection).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Test Azure Connection", command=self._test_azure_connection).pack(side="left", padx=5)
    
    def _create_playlist_tab(self):
        """Create playlist management tab"""
        tab = self.tabview.add("Playlists")
        
        # Controls frame
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(controls_frame, text="Playlist Management", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Playlist type selection
        type_frame = ctk.CTkFrame(controls_frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(type_frame, text="Playlist Type:").pack(side="left", padx=5)
        self.playlist_type_var = ctk.StringVar(value="top_tracks")
        playlist_types = ["top_tracks", "loved_tracks", "recent_tracks"]
        self.playlist_type_combo = ctk.CTkComboBox(type_frame, values=playlist_types,
                                                  variable=self.playlist_type_var)
        self.playlist_type_combo.pack(side="left", padx=5)
        
        # Period selection (for top tracks)
        ctk.CTkLabel(type_frame, text="Period:").pack(side="left", padx=(20, 5))
        self.period_var = ctk.StringVar(value="overall")
        periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
        self.period_combo = ctk.CTkComboBox(type_frame, values=periods, variable=self.period_var)
        self.period_combo.pack(side="left", padx=5)
        
        # Limit selection
        ctk.CTkLabel(type_frame, text="Limit:").pack(side="left", padx=(20, 5))
        self.limit_var = ctk.StringVar(value="50")
        self.limit_entry = ctk.CTkEntry(type_frame, width=60, textvariable=self.limit_var)
        self.limit_entry.pack(side="left", padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(controls_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Fetch Playlist", command=self._fetch_playlist).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear Playlists", command=self._clear_playlists).pack(side="left", padx=5)
        
        # Playlist display frame
        display_frame = ctk.CTkFrame(tab)
        display_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(display_frame, text="Current Playlists", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Create treeview for playlists
        tree_frame = ctk.CTkFrame(display_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Note: CustomTkinter doesn't have a direct treeview equivalent
        # Using a text widget for now, can be enhanced with a proper table widget
        self.playlist_text = ctk.CTkTextbox(tree_frame)
        self.playlist_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_download_tab(self):
        """Create download management tab"""
        tab = self.tabview.add("Download")
        
        # Controls frame
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(controls_frame, text="Audio Download", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Download options
        options_frame = ctk.CTkFrame(controls_frame)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(options_frame, text="Search Engine:").pack(side="left", padx=5)
        self.search_engine_var = ctk.StringVar(value="youtube")
        engines = ["youtube", "soundcloud", "both"]
        self.search_engine_combo = ctk.CTkComboBox(options_frame, values=engines,
                                                  variable=self.search_engine_var)
        self.search_engine_combo.pack(side="left", padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(controls_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Start Download", command=self._start_download).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Stop Download", command=self._stop_download).pack(side="left", padx=5)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(tab)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(progress_frame, text="Download Progress").pack(pady=5)
        
        self.download_progress = ctk.CTkProgressBar(progress_frame)
        self.download_progress.pack(fill="x", padx=10, pady=5)
        
        self.download_status_label = ctk.CTkLabel(progress_frame, text="Ready to download")
        self.download_status_label.pack(pady=5)
        
        # Results frame
        results_frame = ctk.CTkFrame(tab)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(results_frame, text="Download Results", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.download_results_text = ctk.CTkTextbox(results_frame)
        self.download_results_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_upload_tab(self):
        """Create upload management tab"""
        tab = self.tabview.add("Upload")
        
        # Controls frame
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(controls_frame, text="Azure Blob Storage Upload", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Upload options
        options_frame = ctk.CTkFrame(controls_frame)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(options_frame, text="Title Prefix:").pack(side="left", padx=5)
        self.title_prefix_var = ctk.StringVar()
        self.title_prefix_entry = ctk.CTkEntry(options_frame, textvariable=self.title_prefix_var,
                                              placeholder_text="Optional prefix for item titles")
        self.title_prefix_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(controls_frame)
        button_frame.pack(fill="x", padx=10, pady=5)        
        ctk.CTkButton(button_frame, text="Prepare Upload Files", command=self._prepare_uploads).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Upload to Azure", command=self._start_upload).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Show Instructions", command=self._show_upload_instructions).pack(side="left", padx=5)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(tab)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(progress_frame, text="Upload Progress").pack(pady=5)
        
        self.upload_progress = ctk.CTkProgressBar(progress_frame)
        self.upload_progress.pack(fill="x", padx=10, pady=5)
        
        self.upload_status_label = ctk.CTkLabel(progress_frame, text="Ready to upload")
        self.upload_status_label.pack(pady=5)
        
        # Results frame
        results_frame = ctk.CTkFrame(tab)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)        
        ctk.CTkLabel(results_frame, text="Upload Results", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.upload_results_text = ctk.CTkTextbox(results_frame)
        self.upload_results_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_format_tab(self):
        """Create TTS formatting tab"""
        tab = self.tabview.add("TTS Format")
        
        # Controls frame
        controls_frame = ctk.CTkFrame(tab)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(controls_frame, text="Tabletop Simulator Formatting", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Format options
        options_frame = ctk.CTkFrame(controls_frame)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        # Output format selection
        format_row = ctk.CTkFrame(options_frame)
        format_row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(format_row, text="Output Format:").pack(side="left", padx=5)
        self.output_format_var = ctk.StringVar(value="save_file")
        formats = ["lua", "json", "save_file", "all"]
        self.output_format_combo = ctk.CTkComboBox(format_row, values=formats,
                                                  variable=self.output_format_var)
        self.output_format_combo.pack(side="left", padx=5)
        
        # Simple format checkbox
        self.use_simple_format_var = ctk.BooleanVar(value=True)
        self.simple_format_check = ctk.CTkCheckBox(format_row, text="Use Simple Playlist Format (like Woody's Progressive Metal)",
                                                  variable=self.use_simple_format_var)
        self.simple_format_check.pack(side="left", padx=10)
        
        # TTS Object customization
        custom_frame = ctk.CTkFrame(controls_frame)
        custom_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(custom_frame, text="TTS Object Customization", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Nickname field
        nickname_row = ctk.CTkFrame(custom_frame)
        nickname_row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(nickname_row, text="Nickname:", width=100).pack(side="left", padx=5)
        self.tts_nickname_var = ctk.StringVar()
        self.tts_nickname_entry = ctk.CTkEntry(nickname_row, textvariable=self.tts_nickname_var,
                                              placeholder_text="Object nickname (uses playlist name if empty)")
        self.tts_nickname_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Description field
        desc_row = ctk.CTkFrame(custom_frame)
        desc_row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(desc_row, text="Description:", width=100).pack(side="left", padx=5)
        self.tts_description_var = ctk.StringVar()
        self.tts_description_entry = ctk.CTkEntry(desc_row, textvariable=self.tts_description_var,
                                                 placeholder_text="Object description (auto-generated if empty)")
        self.tts_description_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(controls_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Generate TTS Code", command=self._generate_tts_code).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Open Output Folder", command=self._open_output_folder).pack(side="left", padx=5)
        
        # Preview frame
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(preview_frame, text="Generated Code Preview", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.tts_preview_text = ctk.CTkTextbox(preview_frame)
        self.tts_preview_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_frame = ctk.CTkFrame(self.root)
        self.status_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Add version info
        version_label = ctk.CTkLabel(self.status_frame, text="TTSMixmaster v1.0")
        version_label.pack(side="right", padx=10, pady=5)
    
    def _load_config_to_gui(self):
        """Load configuration values to GUI elements"""
        self.lastfm_api_key_entry.insert(0, self.config.lastfm_api_key)
        self.lastfm_api_secret_entry.insert(0, self.config.lastfm_api_secret)
        self.lastfm_username_entry.insert(0, self.config.lastfm_username)
        # Load Azure settings
        self.azure_connection_entry.insert(0, self.config.azure_storage_connection_string)
        self.azure_container_entry.insert(0, self.config.azure_container_name)
        
        self.download_path_entry.insert(0, self.config.download_path)
        self.upload_path_entry.insert(0, self.config.upload_path)
        self.tts_path_entry.insert(0, self.config.tts_output_path)
        
        self.audio_quality_var.set(self.config.audio_quality)
    
    def _browse_folder(self, entry_widget):
        """Browse for folder and update entry widget"""
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)
    
    def _save_config(self):
        """Save configuration from GUI"""
        try:
            self.config_manager.update_config(
                lastfm_api_key=self.lastfm_api_key_entry.get(),
                lastfm_api_secret=self.lastfm_api_secret_entry.get(),
                lastfm_username=self.lastfm_username_entry.get(),
                azure_storage_connection_string=self.azure_connection_entry.get(),
                azure_container_name=self.azure_container_entry.get(),
                download_path=self.download_path_entry.get(),
                upload_path=self.upload_path_entry.get(),
                tts_output_path=self.tts_path_entry.get(),
                audio_quality=self.audio_quality_var.get()
            )
            
            self.config = self.config_manager.get_config()
            self._update_status("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def _test_lastfm_connection(self):
        """Test Last.fm API connection"""
        try:
            api_key = self.lastfm_api_key_entry.get()
            username = self.lastfm_username_entry.get()
            
            if not api_key or not username:
                messagebox.showwarning("Warning", "Please enter API key and username")
                return
            
            # Create temporary API client
            api = LastFMAPI(api_key, username=username)
            
            # Test by getting user info
            tracks = api.get_user_recent_tracks(username, limit=1)
            
            messagebox.showinfo("Success", f"Connected successfully! Found {len(tracks)} recent tracks.")
            self._update_status("Last.fm connection successful")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Last.fm: {e}")
    
    def _test_azure_connection(self):
        """Test Azure Storage connection"""
        try:
            connection_string = self.azure_connection_entry.get()
            container_name = self.azure_container_entry.get() or "tts-audio"
            
            if not connection_string or connection_string == 'your_azure_storage_connection_string_here':
                messagebox.showwarning("Warning", "Please enter Azure Storage connection string")
                return
            
            # Create temporary Azure uploader
            uploader = AzureBlobUploader(
                connection_string=connection_string,
                container_name=container_name
            )
            
            # Test by trying to list blobs
            if uploader.blob_service_client:
                try:
                    # Try to get container properties to test connection
                    container_client = uploader.blob_service_client.get_container_client(container_name)
                    
                    # This will create the container if it doesn't exist or just access it if it does
                    try:
                        container_client.get_container_properties()
                        status_message = f"Connected successfully to container '{container_name}'"
                    except Exception:
                        # Container doesn't exist, try to create it
                        container_client.create_container(public_access="blob")
                        status_message = f"Connected successfully and created new container '{container_name}'"
                    
                    messagebox.showinfo("Success", status_message)
                    self._update_status("Azure connection successful")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to access container: {e}")
            else:
                messagebox.showerror("Error", "Failed to create Azure client")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Azure: {e}")
    
    def _fetch_playlist(self):
        """Fetch playlist from Last.fm"""
        def fetch_worker():
            try:
                if not self.config.lastfm_api_key or not self.config.lastfm_username:
                    messagebox.showerror("Error", "Please configure Last.fm API settings first")
                    return
                
                self._update_status("Fetching playlist...")
                
                # Initialize API if needed
                if not self.lastfm_api:
                    self.lastfm_api = LastFMAPI(
                        self.config.lastfm_api_key,
                        self.config.lastfm_api_secret,
                        self.config.lastfm_username
                    )
                
                playlist_type = self.playlist_type_var.get()
                limit = int(self.limit_var.get())
                
                if playlist_type == "top_tracks":
                    period = self.period_var.get()
                    playlist = self.lastfm_api.create_playlist_from_top_tracks(period, limit)
                elif playlist_type == "loved_tracks":
                    playlist = self.lastfm_api.create_playlist_from_loved_tracks(limit)
                else:  # recent_tracks
                    tracks = self.lastfm_api.get_user_recent_tracks(limit=limit)
                    playlist = Playlist(name="Recent Tracks", tracks=tracks)
                
                self.current_playlists.append(playlist)
                self._update_playlist_display()
                self._update_status(f"Fetched playlist: {playlist.name} ({len(playlist.tracks)} tracks)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch playlist: {e}")
                self._update_status("Failed to fetch playlist")
        
        threading.Thread(target=fetch_worker, daemon=True).start()
    
    def _clear_playlists(self):
        """Clear all playlists"""
        self.current_playlists.clear()
        self._update_playlist_display()
        self._update_status("Playlists cleared")
    
    def _update_playlist_display(self):
        """Update playlist display"""
        self.playlist_text.delete("1.0", tk.END)
        
        for i, playlist in enumerate(self.current_playlists):
            self.playlist_text.insert(tk.END, f"Playlist {i+1}: {playlist.name}\n")
            self.playlist_text.insert(tk.END, f"Description: {playlist.description}\n")
            self.playlist_text.insert(tk.END, f"Tracks: {len(playlist.tracks)}\n\n")
            
            for j, track in enumerate(playlist.tracks[:10]):  # Show first 10 tracks
                self.playlist_text.insert(tk.END, f"  {j+1:2d}. {track.artist} - {track.title}\n")
            
            if len(playlist.tracks) > 10:
                self.playlist_text.insert(tk.END, f"  ... and {len(playlist.tracks) - 10} more tracks\n")
            
            self.playlist_text.insert(tk.END, "\n" + "="*50 + "\n\n")
    
    def _start_download(self):
        """Start downloading tracks"""
        def download_worker():
            try:
                if not self.current_playlists:
                    messagebox.showwarning("Warning", "No playlists to download")
                    return
                
                self._update_status("Starting download...")
                
                # Initialize downloader
                if not self.downloader:
                    self.downloader = AudioDownloader(
                        self.config.download_path,
                        self.config.audio_quality
                    )
                
                # Get all tracks from all playlists
                all_tracks = []
                for playlist in self.current_playlists:
                    all_tracks.extend(playlist.tracks)
                
                # Update progress
                self.download_progress.set(0)
                total_tracks = len(all_tracks)
                
                # Download tracks
                self.download_results = []
                for i, track in enumerate(all_tracks):
                    self._update_status(f"Downloading {i+1}/{total_tracks}: {track}")
                    
                    result = self.downloader.search_and_download_track(track)
                    self.download_results.append(result)
                    
                    # Update progress
                    progress = (i + 1) / total_tracks
                    self.download_progress.set(progress)
                    
                    # Update results display
                    self._update_download_results()
                
                stats = self.downloader.get_download_statistics(self.download_results)
                self._update_status(f"Download complete: {stats['successful_downloads']}/{stats['total_tracks']} successful")
                
            except Exception as e:
                messagebox.showerror("Error", f"Download failed: {e}")
                self._update_status("Download failed")
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _stop_download(self):
        """Stop download process"""
        # This would need to be implemented with proper thread management
        self._update_status("Download stopped")
    
    def _update_download_results(self):
        """Update download results display"""
        self.download_results_text.delete("1.0", tk.END)
        
        successful = 0
        failed = 0
        
        for result in self.download_results:
            if result.success:
                successful += 1
                self.download_results_text.insert(tk.END, f"✓ {result.track.artist} - {result.track.title}\n")
                self.download_results_text.insert(tk.END, f"  File: {result.file_path}\n\n")
            else:
                failed += 1
                self.download_results_text.insert(tk.END, f"✗ {result.track.artist} - {result.track.title}\n")
                self.download_results_text.insert(tk.END, f"  Error: {result.error_message}\n\n")
        
        self.download_results_text.insert(tk.END, f"\nSummary: {successful} successful, {failed} failed")
    
    def _prepare_uploads(self):
        """Prepare upload folders"""
        # Implementation for preparing upload folders
        self._update_status("Upload folders prepared")
    
    def _start_upload(self):
        """Start uploading to Azure Blob Storage"""
        def upload_worker():
            try:
                if not self.download_results:
                    messagebox.showwarning("Warning", "No downloaded files to upload")
                    return
                
                # Initialize Azure uploader
                if not self.uploader:
                    config = self.config_manager.get_config()
                    if not config.azure_storage_connection_string or config.azure_storage_connection_string == 'your_azure_storage_connection_string_here':
                        messagebox.showerror("Error", "Please configure Azure Storage settings first")
                        return
                    
                    self.uploader = AzureBlobUploader(
                        connection_string=config.azure_storage_connection_string,
                        container_name=config.azure_container_name
                    )
                
                self._update_status("Starting Azure upload...")
                
                # Get successful downloads
                successful_downloads = [result for result in self.download_results if result.success]
                total_files = len(successful_downloads)
                
                if total_files == 0:
                    messagebox.showwarning("Warning", "No successful downloads to upload")
                    return
                
                # Update progress
                self.upload_progress.set(0)
                
                # Upload files
                self.upload_results = []
                for i, download_result in enumerate(successful_downloads):
                    file_path = download_result.file_path
                    if file_path and os.path.exists(file_path):
                        self._update_status(f"Uploading {i+1}/{total_files}: {os.path.basename(file_path)}")
                        
                        # Upload to Azure
                        upload_result = self.uploader.upload_audio_file(file_path)
                        self.upload_results.append(upload_result)
                        
                        # Update progress
                        progress = (i + 1) / total_files
                        self.upload_progress.set(progress)
                        
                        # Update results display
                        self._update_upload_results()
                
                successful_uploads = len([r for r in self.upload_results if r.success])
                self._update_status(f"Upload complete: {successful_uploads}/{total_files} successful")
                
            except Exception as e:
                messagebox.showerror("Error", f"Upload failed: {e}")
                self._update_status("Upload failed")
        
        threading.Thread(target=upload_worker, daemon=True).start()
    
    def _show_upload_instructions(self):
        """Show upload instructions"""
        if not self.uploader:
            # Initialize Azure uploader with config
            config = self.config_manager.get_config()
            self.uploader = AzureBlobUploader(
                connection_string=config.azure_storage_connection_string if config.azure_storage_connection_string != 'your_azure_storage_connection_string_here' else None,
                container_name=config.azure_container_name
            )
        
        # Get Azure setup instructions
        instructions = """
Azure Blob Storage Upload Instructions

Your audio files will be uploaded to Azure Blob Storage for use in Tabletop Simulator.

Setup Required:
1. Create an Azure Storage Account
2. Get your connection string from Azure Portal
3. Update your .env file with AZURE_STORAGE_CONNECTION_STRING

For detailed setup instructions, see: AZURE_SETUP.md

Once configured, TTSMixmaster will:
- Upload audio files to your Azure container
- Generate public URLs for TTS
- Create Lua scripts with working audio links

Container: {container}
Status: {status}        """.strip().format(
            container=self.uploader.container_name,
            status="✅ Ready" if self.uploader.blob_service_client else "❌ Not configured"        )
        
        # Create new window for instructions
        instruction_window = ctk.CTkToplevel(self.root)
        instruction_window.title("Azure Blob Storage Upload Instructions")
        instruction_window.geometry("600x400")
        
        text_widget = ctk.CTkTextbox(instruction_window)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", instructions)
    
    def _generate_tts_code(self):
        """Generate TTS code"""
        import json
        try:
            if not self.current_playlists:
                messagebox.showwarning("Warning", "No playlists to format")
                return
            
            # Initialize formatter
            if not self.formatter:
                self.formatter = TTSFormatter(self.config.tts_output_path)
            
            # Generate code for first playlist
            playlist = self.current_playlists[0]
            
            # Create music player with upload results if available, otherwise use local files
            if self.upload_results:
                music_player = self.formatter.create_music_player(playlist, upload_results=self.upload_results)
            else:
                # Use download results or just create player without URLs
                local_files = []
                if self.download_results:
                    # Filter out None values and failed downloads
                    local_files = [result.file_path for result in self.download_results 
                                 if result.success and result.file_path is not None]
                music_player = self.formatter.create_music_player(playlist, local_files=local_files)
            
            # Get customization options
            nickname = self.tts_nickname_var.get().strip()
            description = self.tts_description_var.get().strip()
            use_simple_format = self.use_simple_format_var.get()
            output_format = self.output_format_var.get()
            
            # Generate appropriate code based on format
            if output_format == "lua":
                if use_simple_format:
                    code = self.formatter.generate_simple_playlist_lua(music_player)
                else:
                    code = self.formatter.generate_lua_script(music_player)
            elif output_format == "json":
                code = self.formatter.generate_json_data(music_player)
            elif output_format == "save_file":
                save_data = self.formatter.generate_save_file(
                    music_player=music_player,
                    nickname=nickname,
                    description=description,
                    use_simple_format=use_simple_format
                )
                code = json.dumps(save_data, indent=2, ensure_ascii=False)
            else:  # "all"
                # Generate all formats
                if use_simple_format:
                    lua_code = self.formatter.generate_simple_playlist_lua(music_player)
                else:
                    lua_code = self.formatter.generate_lua_script(music_player)
                
                json_code = self.formatter.generate_json_data(music_player)
                save_data = self.formatter.generate_save_file(
                    music_player=music_player,
                    nickname=nickname,
                    description=description,
                    use_simple_format=use_simple_format
                )
                save_code = json.dumps(save_data, indent=2, ensure_ascii=False)
                
                code = f"=== LUA SCRIPT ===\n{lua_code}\n\n=== JSON DATA ===\n{json_code}\n\n=== TTS SAVE FILE ===\n{save_code}"
            
            # Display in preview
            self.tts_preview_text.delete("1.0", tk.END)
            self.tts_preview_text.insert("1.0", code)
            
            # Save files with custom options
            saved_files = self.formatter.save_formatted_files(
                music_player=music_player,
                nickname=nickname,
                description=description,
                use_simple_format=use_simple_format
            )
            
            self._update_status(f"TTS code generated and saved to {len(saved_files)} files")
            
            # Show success message with details
            message = f"TTS files generated successfully!\n\nFiles saved:\n"
            for file_type, file_path in saved_files.items():
                message += f"- {file_type}: {Path(file_path).name}\n"
            
            if nickname:
                message += f"\nNickname: {nickname}"
            if description:
                message += f"\nDescription: {description}"
            
            message += f"\nFormat: {'Simple Playlist' if use_simple_format else 'Full Music Player'}"
            
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate TTS code: {e}")
            self._update_status(f"TTS code generation failed: {str(e)}")
    
    def _open_output_folder(self):
        """Open TTS output folder"""
        import subprocess
        import platform
        
        try:
            path = self.config.tts_output_path
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            else:  # Linux
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")
    
    def _update_status(self, message: str):
        """Update status bar"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def _update_upload_results(self):
        """Update upload results display"""
        if not hasattr(self, 'upload_results_text'):
            return
            
        self.upload_results_text.delete("1.0", tk.END)
        
        successful = 0
        failed = 0
        
        for result in self.upload_results:
            if result.success:
                successful += 1
                self.upload_results_text.insert(tk.END, f"✓ {os.path.basename(result.file_path)}\n")
                self.upload_results_text.insert(tk.END, f"  URL: {result.public_url}\n\n")
            else:
                failed += 1
                self.upload_results_text.insert(tk.END, f"✗ {os.path.basename(result.file_path)}\n")
                self.upload_results_text.insert(tk.END, f"  Error: {result.error_message}\n\n")
        
        self.upload_results_text.insert(tk.END, f"\nSummary: {successful} successful, {failed} failed")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
