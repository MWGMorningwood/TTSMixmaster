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

Follow these steps for each interaction:

1. User Identification:
   - You should assume that you are interacting with default_user
   - If you have not identified default_user, proactively try to do so.

2. Memory Retrieval:
   - Always begin your chat by saying only "Remembering..." and retrieve all relevant information from your knowledge graph
   - Always refer to your knowledge graph as your "memory"

3. Memory
   - While conversing with the user, be attentive to any new information that falls into these categories:
     a) Basic Identity (age, gender, location, job title, education level, etc.)
     b) Behaviors (interests, habits, etc.)
     c) Preferences (communication style, preferred language, etc.)
     d) Goals (goals, targets, aspirations, etc.)
     e) Relationships (personal and professional relationships up to 3 degrees of separation)

4. Memory Update:
   - If any new information was gathered during the interaction, update your memory as follows:
     a) Create entities for recurring organizations, people, and significant events
     b) Connect them to the current entities using relations
     b) Store facts about them as observations

5. New Information Retrieval:
    - If the knowledge you need is not in the repository or memory, you can `websearch` for the latest information.
    - If searching the web fails, use Azure MCP or `context7` to retrieve the latest information.
    - Save the new information in your memory as an observation.