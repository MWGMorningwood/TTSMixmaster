# TTSMixmaster

A comprehensive tool for managing Last.fm playlists and integrating them with Tabletop Simulator. This application allows you to fetch playlists from Last.fm, download MP3 files, upload them to Steam Workshop, and generate formatted Lua code for use in Tabletop Simulator.

## Features

### 🎵 Last.fm Integration
- Fetch user's top tracks, loved tracks, and recent tracks
- Support for different time periods (overall, 7 days, 1 month, etc.)
- Configurable track limits

### ⬇️ Audio Downloading
- Download audio files from YouTube and SoundCloud
- Configurable audio quality (128, 192, 256, 320 kbps)
- Batch downloading with progress tracking
- Automatic file naming and organization

### ☁️ Steam Workshop Upload
- Prepare files for Steam Workshop upload
- Automatic preview image generation
- Batch upload support
- Manual upload instructions for users without SteamCMD

### 🎮 Tabletop Simulator Integration
- Generate Lua scripts for TTS music players
- Create JSON data structures
- Generate complete TTS save files
- Support for playlist management and playback controls

### 🖥️ Modern GUI Interface
- Dark/light theme support
- Progress tracking for all operations
- Tabbed interface for different features
- Configuration management

## Installation

### Prerequisites
- Python 3.8 or higher
- (Optional) SteamCMD for direct Workshop uploads

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
4. Edit `.env` with your API keys:
   - Last.fm API key and secret (get from https://www.last.fm/api/account/create)
   - Your Last.fm username
   - (Optional) Steam username for Workshop uploads

## Usage

### Running the Application
```bash
python main.py
```

### Configuration
1. Open the "Configuration" tab
2. Enter your Last.fm API credentials and username
3. Set your preferred download and output paths
4. Configure audio quality settings
5. Click "Save Configuration"
6. Test your Last.fm connection

### Fetching Playlists
1. Go to the "Playlists" tab
2. Select playlist type (top tracks, loved tracks, or recent tracks)
3. Choose time period (for top tracks) and track limit
4. Click "Fetch Playlist"

### Downloading Audio
1. Switch to the "Download" tab
2. Select your preferred search engine
3. Click "Start Download" to begin downloading all tracks
4. Monitor progress in the progress bar and results panel

### Uploading to Steam Workshop
1. Go to the "Upload" tab
2. (Optional) Set a title prefix for your workshop items
3. Click "Prepare Upload Folders" to organize files
4. Use "Upload to Workshop" for automatic upload (requires SteamCMD)
5. Or use "Show Instructions" for manual upload steps

### Generating TTS Code
1. Navigate to the "TTS Format" tab
2. Select output format (Lua, JSON, or save file)
3. Click "Generate TTS Code"
4. Preview the generated code
5. Files are automatically saved to your TTS output directory

## File Structure

```
TTSMixmaster/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.template          # Environment variables template
├── config.json            # Application configuration
├── src/
│   ├── api/               # Last.fm API integration
│   ├── downloader/        # Audio downloading
│   ├── uploader/          # Steam Workshop upload
│   ├── tts_formatter/     # TTS code generation
│   ├── gui/               # GUI interface
│   └── utils/             # Utilities and configuration
├── downloads/             # Downloaded audio files
├── uploads/               # Prepared upload folders
├── tts_formatted/         # Generated TTS files
└── tests/                 # Test files
```

## Configuration Options

### Environment Variables
- `LASTFM_API_KEY` - Your Last.fm API key
- `LASTFM_API_SECRET` - Your Last.fm API secret
- `LASTFM_USERNAME` - Your Last.fm username
- `STEAM_USERNAME` - Your Steam username
- `DOWNLOAD_PATH` - Path for downloaded files
- `UPLOAD_PATH` - Path for upload preparation
- `TTS_OUTPUT_PATH` - Path for TTS formatted files
- `AUDIO_QUALITY` - Audio quality (128, 192, 256, 320)
- `THEME` - UI theme (dark, light)

## API Requirements

### Last.fm API
1. Create an account at https://www.last.fm/api/account/create
2. Get your API key and secret
3. Add them to your `.env` file

### Steam (Optional)
- Steam account with Tabletop Simulator ownership
- SteamCMD installed for automatic uploads

## Troubleshooting

### Common Issues
1. **FFmpeg Error (`'FFmpegPostProcessorPP'`)**: 
   - Make sure you've installed all dependencies: `pip install -r requirements.txt`
   - The `imageio-ffmpeg` package should handle FFmpeg automatically
   
2. **Import errors**: Ensure all dependencies are installed and you're using the correct virtual environment

3. **API connection failed**: Check your Last.fm API credentials in your `.env` file

4. **Download failures**: Verify internet connection and try different search engines

5. **Upload issues**: Ensure SteamCMD is installed and Steam credentials are correct

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
```

## Contributing

This project welcomes contributions! Areas for improvement:
- Additional audio sources
- Enhanced TTS features
- Better error handling
- Performance optimizations
- UI/UX improvements

## License

This project is provided as-is for educational and personal use. Please respect the terms of service of all integrated APIs and services.

## Disclaimer

- This tool is for personal use with your own Last.fm data
- Respect copyright and licensing when downloading audio
- Steam Workshop uploads must comply with Steam's terms of service
- The developers are not responsible for any misuse of this software
