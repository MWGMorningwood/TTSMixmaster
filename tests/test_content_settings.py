#!/usr/bin/env python3
"""
Test ContentSettings creation to verify the cache_control fix
"""

def test_content_settings():
    """Test that ContentSettings can be created without errors"""
    try:
        from azure.storage.blob import ContentSettings
        
        # Test creating ContentSettings object
        content_settings = ContentSettings(
            content_type="audio/mpeg",
            content_disposition='inline; filename="test.mp3"'
        )
        
        print("✅ ContentSettings object created successfully")
        print(f"Content type: {content_settings.content_type}")
        print(f"Content disposition: {content_settings.content_disposition}")
        print(f"Has cache_control attribute: {hasattr(content_settings, 'cache_control')}")
        
        return True
        
    except ImportError:
        print("❌ Azure SDK not available")
        return False
    except Exception as e:
        print(f"❌ Error creating ContentSettings: {e}")
        return False

if __name__ == "__main__":
    print("ContentSettings Test")
    print("=" * 20)
    test_content_settings()
