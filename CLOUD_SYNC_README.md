# Cloud Sync Feature for POS System

## Overview
This feature provides automatic updates, log uploads, and backup uploads to cloud storage for your POS system.

## Features
1. **Auto-Update**: Automatically checks for and downloads new exe versions from GitHub Releases
2. **Log Upload**: Compresses and uploads application logs to cloud daily
3. **Backup Upload**: Compresses and uploads database backups to cloud daily
4. **Device Tracking**: Each device has a unique ID for tracking purposes

## Setup Instructions

### 1. Create a GitHub Repository
1. Go to GitHub and create a new repository for your POS system
2. Make it public (free) or private (requires GitHub token)

### 2. Upload Your Exe as a Release
1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag version: `v20260413` (format: vYYYYMMDD)
4. Release title: e.g., "POSSystem v20260413"
5. Description: Add release notes about what's new
6. Attach your `POSSystem.exe` file
7. Click "Publish release"

### 3. Configure Cloud Sync in the Application
1. Open the POS application
2. Go to **Settings** → **☁️ Cloud Sync**
3. Click **⚙️ Configure Cloud Sync**
4. Enter your GitHub repository: `username/repo-name` (e.g., `johnsmith/pos-system`)
5. (Optional) Enter GitHub token if using a private repository
6. Enable the features you want:
   - **Enable Cloud Sync**: Master switch for all features
   - **Enable Auto-Update**: Automatically check for updates
   - **Enable Log Upload**: Upload logs daily
   - **Enable Backup Upload**: Upload backups daily
7. Set intervals (in hours) for each feature
8. Click **Save**

### 4. Device ID
Each device automatically gets a unique ID stored in `device_id.txt`. This ID is used to:
- Track which device uploaded logs/backups
- Identify devices in the cloud storage

## How It Works

### Auto-Update
- Checks GitHub Releases for new versions every 24 hours (configurable)
- Compares current exe modification date with release tag
- Downloads new exe if available
- Replaces current exe and requires restart
- Shows update notification before applying

### Log Upload
- Compresses all files in `logs/` directory to a zip file
- Names file: `logs_{device_id}_{YYYYMMDD}.zip`
- Uploads to GitHub repository in `cloud_logs/` folder using GitHub API
- Runs every 24 hours (configurable)
- Cleans up local zip file after upload

### Backup Upload
- Finds latest SQL backup file in `backups/` directory
- Compresses to zip file
- Names file: `backup_{device_id}_{YYYYMMDD}.zip`
- Uploads to GitHub repository in `cloud_backups/` folder using GitHub API
- Runs every 24 hours (configurable)
- Cleans up local zip file after upload

### GitHub Upload Details
- Files are uploaded directly to the repository using GitHub API
- Each device's files are organized in `cloud_logs/` and `cloud_backups/` folders
- Files are named with device ID and date for easy tracking
- GitHub token is used for authentication (already configured)
- Existing files are updated if uploaded again on the same day

## Configuration File
Configuration is stored in `cloud_config.json`:

```json
{
  "github_repo": "your-username/pos-system",
  "github_token": "",
  "update_check_interval_hours": 24,
  "log_upload_interval_hours": 24,
  "backup_upload_interval_hours": 24,
  "cloud_enabled": false,
  "log_upload_enabled": false,
  "backup_upload_enabled": false
}
```

## Current Implementation
- ✅ Log upload to GitHub (fully implemented)
- ✅ Backup upload to GitHub (fully implemented)
- Auto-update downloads the exe but doesn't automatically restart the application
- Only works with GitHub Releases for updates

## Future Enhancements
1. Add support for automatic restart after update
2. Add support for multiple cloud storage providers (Dropbox, Google Drive, AWS S3)
3. Add web dashboard to view all device logs and backups
4. Add remote device management capabilities
5. Add analytics and usage tracking

## Troubleshooting

### Updates not downloading
- Check GitHub repo URL is correct
- Check if repository is public (or token is provided for private repos)
- Check internet connection
- View logs for error messages

### Device ID issues
- Delete `device_id.txt` to generate a new ID
- Make sure application has write permissions

### Configuration not saving
- Check if application has write permissions to the directory
- Check `cloud_config.json` file permissions

## Security Considerations
- GitHub tokens should be stored securely
- Consider using environment variables for sensitive data
- Logs may contain sensitive information - review before enabling upload
- Backups contain customer data - ensure cloud storage is secure

## API Rate Limits
GitHub API has rate limits:
- 60 requests/hour for unauthenticated requests
- 5000 requests/hour for authenticated requests
- Consider using a GitHub token if you have many devices
