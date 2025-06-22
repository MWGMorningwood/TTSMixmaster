# Azure Blob Storage Setup Guide for TTSMixmaster

## What You Need

To use Azure Blob Storage for uploading your audio files, you'll need:

1. **Azure Storage Account** - A storage account in Microsoft Azure
2. **Connection String** - To authenticate and connect to your storage account

## Step 1: Create Azure Storage Account

1. Go to the [Azure Portal](https://portal.azure.com)
2. Create a new **Storage Account**:
   - Choose a unique name (e.g., `ttsmixmaster2024`)
   - Select a region close to you
   - Choose **Standard** performance
   - Select **Locally-redundant storage (LRS)** for cost efficiency
3. Wait for deployment to complete

## Step 2: Get Your Connection String

1. In your Storage Account, go to **Security + networking** → **Access keys**
2. Copy the **Connection string** from **key1**
3. It will look like this:
   ```
   DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=abc123...;EndpointSuffix=core.windows.net
   ```

## Step 3: Configure TTSMixmaster

1. Edit your `.env` file:
   ```bash
   # Replace with your actual connection string
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=abc123...;EndpointSuffix=core.windows.net
   
   # Optional: Change container name (default is fine)
   AZURE_CONTAINER_NAME=tts-audio
   ```

2. Save the file

## Step 4: Test the Upload

Run the test script to verify everything works:

```bash
python test_azure_upload.py
```

## How It Works

1. **Container Creation**: TTSMixmaster automatically creates a container called `tts-audio` with public blob access
2. **File Upload**: Audio files are uploaded to the `audio/` folder in your container
3. **Public URLs**: Each uploaded file gets a public URL like:
   ```
   https://youraccount.blob.core.windows.net/tts-audio/audio/Artist_-_Song_abc12345.mp3
   ```
4. **TTS Integration**: These URLs can be used directly in Tabletop Simulator

## Cost Estimation

Azure Blob Storage is very affordable:
- **Storage**: ~$0.018 per GB per month
- **Transactions**: ~$0.0004 per 10,000 operations
- **100 songs (~500 MB)**: Less than $0.01 per month

## Benefits

✅ **Reliable**: Enterprise-grade cloud storage  
✅ **Fast**: Global CDN for fast downloads  
✅ **Secure**: Private storage with public file access  
✅ **Scalable**: Unlimited storage capacity  
✅ **TTS Compatible**: Direct URL access for Tabletop Simulator  

## Next Steps

Once configured, you can:
1. Use the GUI to upload playlists
2. Generate TTS Lua code with real URLs
3. Load the music directly in Tabletop Simulator

Happy mixing! 🎵
