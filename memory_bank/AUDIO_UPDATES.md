# TTSMixmaster - Audio Processing & TTS Format Updates

## Recent Updates

### ✅ Fixed Issues
1. **TTS Save File Image URLs** - Now uses the correct Steam URLs for consistent appearance
2. **Mono Audio Output** - All downloaded audio files are automatically converted to mono for TTS compatibility
3. **Enhanced Metadata** - Audio files now have proper artist, title, and album metadata

### 🎵 Audio Processing Improvements

#### Automatic Mono Conversion
All newly downloaded audio files are automatically processed to:
- Convert from stereo to mono (single channel)
- Maintain audio quality while reducing file size
- Ensure compatibility with Tabletop Simulator's audio system

#### Enhanced Metadata
Downloaded files now include:
- **Title** - Song title
- **Artist** - Artist name  
- **Album** - Album name (when available)
- **Duration** - Track duration
- Proper ID3 tags for better organization

### 🖼️ TTS Save File Updates

#### Correct Image URLs
TTS save files now use the proper Steam Workshop image URLs:
- **Primary Image**: `https://steamusercontent-a.akamaihd.net/ugc/9672878331288570/AE7A2999E8CD0EFF71210D7961A41E1F87F9DE78/`
- **Secondary Image**: `https://steamusercontent-a.akamaihd.net/ugc/1778335968028979741/9DA6ABA2450EBDA4E967816C4FA92289A638DB53/`

This ensures all music players have a consistent appearance in Tabletop Simulator.

## 🛠️ New Utilities

### Convert Existing Audio Files
Use the included utility script to process your existing audio files:

```bash
# Convert all MP3 files in downloads folder to mono and enhance metadata
python convert_audio_files.py ./downloads

# Only convert to mono
python convert_audio_files.py ./downloads --mono-only

# Only enhance metadata
python convert_audio_files.py ./downloads --metadata-only

# Process specific file types
python convert_audio_files.py ./downloads --pattern "*.wav"
```

### Testing the Updates
Run the test script to verify everything is working:

```bash
python test_audio_improvements.py
```

## 📋 Usage Examples

### Basic Workflow (Updated)
1. **Fetch Playlists** from Last.fm as usual
2. **Download Audio** - Now automatically mono with metadata
3. **Generate TTS Files** - Now with correct image URLs
4. **Upload to TTS** - Optimized files for better performance

### Processing Existing Files
If you have existing audio files that need to be converted:

```python
from src.downloader.audio_downloader import AudioDownloader

downloader = AudioDownloader()

# Convert a single file to mono
downloader.convert_to_mono("path/to/audio.mp3")

# Enhance metadata for a file
from src.api.lastfm_client import Track
track = Track(title="Song Title", artist="Artist Name", album="Album Name")
downloader.enhance_metadata("path/to/audio.mp3", track)
```

## 🔧 Technical Details

### Audio Processing Pipeline
1. **Download** - yt-dlp extracts audio at specified quality
2. **Convert** - FFmpeg converts to mono using `-ac 1` flag
3. **Metadata** - Enhanced using either mutagen or FFmpeg
4. **Validate** - File integrity and format verification

### TTS Save Format
The save files now follow the exact format from "Woody's Progressive Metal":
- Correct image URLs for visual consistency
- Simple playlist Lua format for better performance
- Customizable nickname and description fields
- Proper object placement and properties

## 🎯 Performance Benefits

### File Size Reduction
- Mono files are approximately 50% smaller than stereo
- Faster uploads to Steam Workshop
- Better performance in Tabletop Simulator

### Compatibility
- Consistent audio format across all tracks
- Proper metadata for better organization
- Optimized for TTS audio system

## 🐛 Troubleshooting

### FFmpeg Required
The mono conversion requires FFmpeg to be installed:
- **Windows**: Download from https://ffmpeg.org/download.html
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian)

### Metadata Issues
If metadata enhancement fails:
1. Check if mutagen is installed: `pip install mutagen`
2. Ensure FFmpeg is available in system PATH
3. Verify file permissions are correct

### File Processing Errors
Common issues:
- **File in use** - Close media players before processing
- **Permissions** - Ensure write access to audio files
- **Disk space** - Processing requires temporary space

## 📚 API Changes

### AudioDownloader Updates
New methods available:
- `convert_to_mono(file_path)` - Convert audio file to mono
- `enhance_metadata(file_path, track)` - Add metadata to audio file
- `batch_convert_to_mono(file_paths)` - Process multiple files
- `batch_enhance_metadata(file_paths, tracks)` - Bulk metadata enhancement

### TTSFormatter Updates
Updated methods:
- `generate_save_file()` - Now uses correct image URLs
- All save files automatically include proper Steam image references

---

*These updates ensure your TTSMixmaster generates the highest quality, most compatible audio files for Tabletop Simulator while maintaining the exact format shown in the reference "Woody's Progressive Metal" playlist.*
