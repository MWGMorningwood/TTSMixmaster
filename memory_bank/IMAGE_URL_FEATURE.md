# Image URL Customization Feature

## Overview
The TTSMixmaster application now supports custom image URLs for TTS (Tabletop Simulator) objects, allowing users to specify their own images instead of using the default Steam Workshop images.

## Changes Made

### Backend Changes (TTSFormatter)

#### File: `src/tts_formatter/tts_formatter.py`

1. **Updated `generate_save_file` method signature:**
   - Added `image_url: str = ""` parameter
   - Added `image_secondary_url: str = ""` parameter
   - Updated docstring to document new parameters

2. **Added logic to use custom or default URLs:**
   ```python
   # Use custom image URLs or defaults
   default_image_url = "https://steamusercontent-a.akamaihd.net/ugc/9672878331288570/AE7A2999E8CD0EFF71210D7961A41E1F87F9DE78/"
   default_secondary_url = "https://steamusercontent-a.akamaihd.net/ugc/1778335968028979741/9DA6ABA2450EBDA4E967816C4FA92289A638DB53/"
   
   final_image_url = image_url.strip() if image_url.strip() else default_image_url
   final_secondary_url = image_secondary_url.strip() if image_secondary_url.strip() else default_secondary_url
   ```

3. **Updated CustomImage section to use parameters:**
   ```python
   "CustomImage": {
       "ImageURL": final_image_url,
       "ImageSecondaryURL": final_secondary_url,
       # ... other properties
   }
   ```

4. **Updated `save_formatted_files` method:**
   - Added same image URL parameters
   - Passes parameters through to `generate_save_file`

### Frontend Changes (GUI)

#### File: `src/gui/main_window.py`

1. **Added image URL input fields in TTS customization section:**
   - Primary Image URL field with placeholder text
   - Secondary Image URL field with placeholder text
   - Both fields use proper CustomTkinter styling

2. **Updated `_generate_tts_code` method:**
   - Extracts image URL values from GUI fields
   - Passes values to all relevant formatter method calls
   - Supports both individual format generation and "all" format generation

## Usage Instructions

### For Users

1. **Access the TTS Format Tab** in the TTSMixmaster application
2. **Navigate to TTS Object Customization section**
3. **Enter Image URLs:**
   - **Image URL**: Primary image for the TTS object (appears on top/front)
   - **Secondary URL**: Secondary image for the TTS object (appears on bottom/back)
4. **Leave fields empty** to use default Steam Workshop images
5. **Generate TTS Code** as usual - custom images will be included automatically

### For Developers

The new parameters are available in both key methods:

```python
# Direct save file generation
save_data = formatter.generate_save_file(
    music_player=music_player,
    nickname="My Playlist",
    description="Custom description",
    image_url="https://example.com/my-image.jpg",
    image_secondary_url="https://example.com/my-secondary.jpg"
)

# Complete file generation
saved_files = formatter.save_formatted_files(
    music_player=music_player,
    nickname="My Playlist", 
    description="Custom description",
    image_url="https://example.com/my-image.jpg",
    image_secondary_url="https://example.com/my-secondary.jpg"
)
```

## Default Behavior

- **Empty/blank URLs**: Uses default Steam Workshop images
- **Whitespace-only URLs**: Treated as empty, uses defaults
- **Valid URLs**: Uses exactly as provided (no validation performed)

## Default Steam Workshop Images

- **Primary**: `https://steamusercontent-a.akamaihd.net/ugc/9672878331288570/AE7A2999E8CD0EFF71210D7961A41E1F87F9DE78/`
- **Secondary**: `https://steamusercontent-a.akamaihd.net/ugc/1778335968028979741/9DA6ABA2450EBDA4E967816C4FA92289A638DB53/`

## Testing

A comprehensive test script `test_image_url_feature.py` has been created to verify:
- Custom URLs are properly applied
- Default URLs are used when custom URLs are empty
- The complete workflow from GUI to saved files works correctly

Run the test with:
```bash
python test_image_url_feature.py
```

## Backward Compatibility

This feature is fully backward compatible:
- Existing code will continue to work without modification
- Default parameters ensure no breaking changes
- GUI maintains existing workflow while adding new optional fields
