# TTSMixmaster

A comprehensive tool for exporting your favorite playlists to Tabletop Simulator playlist chips meant for usage with the [Music Box](https://steamcommunity.com/sharedfiles/filedetails/?id=3114355269). This application allows you to fetch playlists from Last.fm, download MP3 files, upload them to Azure Blob Storage and generate formatted Lua code for use in Tabletop Simulator.

[Application Screenshot](./Screenshot 2025-06-22 141024.png)

## Features

### 🎵 Last.fm Integration
- Fetch user's top tracks, loved tracks, and recent tracks
- Support for different time periods (overall, 7 days, 1 month, etc.)
- Configurable track limits
- Real-time playlist fetching with progress tracking

### ⬇️ Audio Downloading
- Download audio files from YouTube and SoundCloud using yt-dlp
- Configurable audio quality (128, 192, 256, 320 kbps)
- Batch downloading with real-time progress tracking
- Automatic file naming and organization
- Support for multiple search engines

### ☁️ Cloud Upload Support
- **Azure Blob Storage**: Upload to Azure with automatic URL generation

### 🎮 Tabletop Simulator Integration
- Generate Lua scripts for TTS music players
- Create JSON data structures
- Generate complete TTS save files with **custom image support**
- Support for playlist management and playback controls
- **New**: Custom image URL fields for TTS objects
- Simple playlist format and full music player format

### 🖥️ Modern GUI Interface
- Built with CustomTkinter for modern appearance
- Dark/light theme support
- Real-time progress tracking for all operations
- Tabbed interface for organized workflow
- Configuration management with validation
- **New**: Image URL customization fields in TTS formatting

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup
1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Note: This automatically includes FFmpeg via the `imageio-ffmpeg` package.

4. Copy `.env.template` to `.env` and fill in your API credentials:
   ```bash
   cp .env.template .env
   ```
5. Edit `.env` with your API keys:
   - Last.fm API key and secret (get from https://www.last.fm/api/account/create)
   - Your Last.fm username
   - (Optional) Azure Storage connection string for cloud uploads

## Usage

### Running the Application
```bash
python main.py
```

### Configuration
1. Open the "Configuration" tab
2. Enter your Last.fm API credentials and username
3. (Optional) Enter Azure Storage connection string and container name for cloud uploads
4. Set your preferred download and output paths
5. Configure audio quality settings
6. Click "Save Configuration"
7. Test your Last.fm connection with "Test Connection"

### Fetching Playlists
1. Go to the "Playlists" tab
2. Select playlist type (top tracks, loved tracks, or recent tracks)
3. Choose time period (for top tracks) and track limit
4. Click "Fetch Playlist"
5. Monitor progress and view results in the results panel

### Downloading Audio
1. Switch to the "Download" tab
2. Select your preferred search engine (YouTube, SoundCloud)
3. Configure audio quality if desired
4. Click "Start Download" to begin downloading all tracks
5. Monitor real-time progress in the progress bar and results panel

### Uploading to Cloud Storage
1. Go to the "Upload" tab
2. Choose upload method:
   - **Azure Blob Storage**: For cloud storage with direct URL access
3. (Optional) Set a title prefix for your upload items
4. Click "Prepare Upload Folders" to organize files
5. Use "Upload to Azure" or "Upload to Workshop" based on your choice
6. Monitor upload progress and view results

### Generating TTS Code
1. Navigate to the "TTS Format" tab
2. **Customize TTS Object** (New Feature):
   - Enter custom nickname for your TTS object
   - Add custom description
   - **Set custom image URLs** for primary and secondary images
   - Leave image fields empty to use default Steam Workshop images
3. Select output format (Lua script, JSON data, save file, or all formats)
4. Choose between simple playlist format or full music player format
5. Click "Generate TTS Code"
6. Preview the generated code in the preview panel
7. Files are automatically saved to your TTS output directory

## File Structure

```
TTSMixmaster/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.template          # Environment variables template
├── config.json            # Application configuration
├── src/
│   ├── api/               # Last.fm API integration
│   │   ├── __init__.py
│   │   └── lastfm_client.py
│   ├── downloader/        # Audio downloading with yt-dlp
│   │   ├── __init__.py
│   │   └── audio_downloader.py
│   ├── uploader/          # Cloud upload
│   │   ├── __init__.py
│   │   ├── azure_blob_uploader.py
│   │   ├── azure_uploader.py
│   │   └── steam_uploader.py
│   ├── tts_formatter/     # TTS code generation
│   │   ├── __init__.py
│   │   └── tts_formatter.py
│   ├── gui/               # CustomTkinter GUI interface
│   │   ├── __init__.py
│   │   └── main_window.py
│   └── utils/             # Utilities and configuration
│       ├── __init__.py
│       └── config.py
├── downloads/             # Downloaded audio files
├── uploads/               # Prepared upload folders
├── tts_formatted/         # Generated TTS files
├── tests/                 # Test files
├── memory_bank/           # Documentation and feature notes
└── backups/               # Configuration backups
```

## Configuration Options

### Environment Variables
- `LASTFM_API_KEY` - Your Last.fm API key
- `LASTFM_API_SECRET` - Your Last.fm API secret
- `LASTFM_USERNAME` - Your Last.fm username
- `AZURE_STORAGE_CONNECTION_STRING` - Azure Storage connection string (optional)
- `AZURE_CONTAINER_NAME` - Azure Storage container name (optional, defaults to "tts-audio")
- `DOWNLOAD_PATH` - Path for downloaded files
- `UPLOAD_PATH` - Path for upload preparation
- `TTS_OUTPUT_PATH` - Path for TTS formatted files
- `AUDIO_QUALITY` - Audio quality (128, 192, 256, 320)
- `THEME` - UI theme (dark, light)

### GUI Configuration
The application also provides a comprehensive configuration interface:
- **API Settings**: Last.fm credentials and connection testing
- **Azure Settings**: Cloud storage configuration for uploads
- **Path Settings**: Customizable paths for downloads, uploads, and TTS output
- **Audio Settings**: Quality selection and search engine preferences
- **Theme Settings**: Dark/light mode selection

## API Requirements

### Last.fm API
1. Create an account at https://www.last.fm/api/account/create
2. Get your API key and secret
3. Add them to your `.env` file

### Azure Storage (Optional)
- Azure Storage account for cloud uploads
- Connection string for authentication
- Container for storing audio files

## New Features

### 🖼️ Custom Image URLs for TTS Objects
One of the major new features is the ability to customize the images used in Tabletop Simulator objects:

- **Primary Image URL**: Set a custom image for the front/top of your TTS object
- **Secondary Image URL**: Set a custom image for the back/bottom of your TTS object
- **Default Fallback**: If left empty, uses default Steam Workshop images
- **Easy Integration**: Simply enter URLs in the TTS Format tab

This feature allows for:
- Personalized music player objects in TTS
- Album artwork or artist images
- Custom branding for your playlists
- Complete visual customization

### 🔄 Enhanced Upload Options
- **Azure Blob Storage**: Direct cloud storage with public URL generation
- **Real-time Progress**: Live progress tracking for all uploads
- **Better Error Handling**: Improved error messages and retry mechanisms

## Troubleshooting

### Common Issues
1. **FFmpeg Error (`'FFmpegPostProcessorPP'`)**: 
   - Make sure you've installed all dependencies: `pip install -r requirements.txt`
   - The `imageio-ffmpeg` package should handle FFmpeg automatically
   
2. **Import errors**: Ensure all dependencies are installed and you're using the correct virtual environment

3. **API connection failed**: Check your Last.fm API credentials in your `.env` file

4. **Download failures**: 
   - Verify internet connection and try different search engines
   - Some videos may be region-restricted or unavailable
   - Check that yt-dlp is up to date

5. **Upload issues**: 
   - For Azure: Verify your connection string and container name
   - For Steam: Ensure SteamCMD is installed and Steam credentials are correct

6. **TTS generation errors**: 
   - Ensure you have valid playlist data before generating TTS code
   - Check that output paths are writable
   - Verify custom image URLs are valid (if used)

### Dependencies Not Installing
If you encounter issues with dependencies:
```bash
# For audio processing
pip install pydub

# For YouTube downloading
pip install yt-dlp

# For GUI
pip install customtkinter

# For environment variables
pip install python-dotenv

# For Azure storage (optional)
pip install azure-storage-blob
```

### Image URL Guidelines
When using custom image URLs for TTS objects:
- Use direct links to image files (JPG, PNG, GIF)
- Ensure URLs are publicly accessible
- Recommended image size: 512x512 or higher
- Test URLs in a browser before using them

## Contributing

This project welcomes contributions! Areas for improvement:
- Additional audio sources and search engines
- Enhanced TTS features and customization options
- Better error handling and user feedback
- Performance optimizations
- UI/UX improvements
- Additional cloud storage providers
- Integration with other music services

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Testing
Run the test suite to ensure your changes don't break existing functionality:
```bash
python -m pytest tests/
```

## Recent Updates

### v1.2.0 - Custom Image Support
- Added custom image URL fields for TTS objects
- Enhanced TTS formatter with image customization
- Improved GUI with new configuration options
- Better error handling and validation

### v1.1.0 - Azure Integration
- Added Azure Blob Storage upload support
- Enhanced upload progress tracking
- Improved configuration management
- Better file organization

## License

This project is provided as-is for educational and personal use. Please respect the terms of service of all integrated APIs and services.

## Disclaimer

- This tool is for personal use with your own Last.fm data
- Respect copyright and licensing when downloading audio
- Steam Workshop uploads must comply with Steam's terms of service
- Azure uploads must comply with Azure's terms of service
- When using custom images, ensure you have the right to use them
- The developers are not responsible for any misuse of this software
