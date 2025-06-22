<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# TTSMixmaster Project Instructions

This is a Python application for managing Last.fm playlists and integrating them with Tabletop Simulator.

## Project Structure
- `src/api/` - Last.fm API integration
- `src/downloader/` - Audio downloading functionality using yt-dlp
- `src/uploader/` - Steam Workshop upload functionality
- `src/tts_formatter/` - Tabletop Simulator code generation
- `src/gui/` - GUI interface using CustomTkinter
- `src/utils/` - Configuration and utility functions

## Code Style Guidelines
- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use dataclasses for data structures
- Handle exceptions gracefully with proper error messages
- Use logging for debugging and information messages
- Follow the existing module structure and naming conventions

## Dependencies
- requests for API calls
- yt-dlp for audio downloading
- customtkinter for modern GUI
- python-dotenv for environment configuration
- pydub for audio processing

## Key Features
1. Last.fm API integration for playlist fetching
2. Audio file downloading from YouTube/SoundCloud
3. Steam Workshop upload preparation
4. Tabletop Simulator Lua code generation
5. Modern GUI interface with progress tracking

## Configuration
The application uses environment variables and a config.json file for settings. All API keys and sensitive information should be stored in environment variables or the .env file.
