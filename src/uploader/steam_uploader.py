"""
Backward Compatibility Module

This module provides backward compatibility for the old steam_uploader imports.
All functionality has been moved to azure_uploader.py
"""

# Import everything from the new Azure uploader
from .azure_uploader import (
    AzureBlobUploader,
    UploadResult,
    CloudUploader
)

# Backward compatibility aliases
SteamWorkshopUploader = AzureBlobUploader
SteamUploader = AzureBlobUploader

# Export all the classes
__all__ = [
    'AzureBlobUploader',
    'UploadResult', 
    'CloudUploader',
    'SteamWorkshopUploader',
    'SteamUploader'
]