# PostgreSQL Database Backup Service

## Overview
This service automatically backs up your PostgreSQL database every hour to the E: drive without showing any screens.

## Files Created:
1. **simple_backup_service.py** - Main backup script
2. **start_backup_service.bat** - Start backup service manually
3. **add_to_startup.bat** - Add to Windows startup
4. **install_backup_service.bat** - Install as Windows Service (optional)

## Quick Start (Recommended)

### Option 1: Run Now + Add to Startup
1. Right-click on `add_to_startup.bat` and "Run as administrator"
2. The service will now start automatically when Windows boots

### Option 2: Run Manually
1. Double-click `start_backup_service.bat`
2. Service runs in background until you restart computer

## How It Works:
- Runs every hour (60 minutes)
- Creates compressed backup files in `E:\Database_Backups`
- Keeps only last 24 backups (1 day worth)
- Logs all activity to `E:\Database_Backups\backup.log`
- Runs silently in background (no windows shown)

## Backup Files:
- Location: `E:\Database_Backups\`
- Format: `pos_backup_YYYYMMDD_HHMMSS.sql.zip`
- Example: `pos_backup_20260305_171500.sql.zip`

## To Stop the Service:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Find and end `python.exe` processes
3. Or restart your computer

## To Check Logs:
- Open: `E:\Database_Backups\backup.log`
- Shows all backup attempts and results

## Database Configuration:
- Database: pos_network
- Host: localhost:5432
- User: admin
- Password: admin

## Requirements:
- PostgreSQL client tools (pg_dump) must be installed
- Python 3.x
- E: drive must exist

## Optional: Windows Service Installation
For a more robust installation as a proper Windows service:
1. Right-click `install_backup_service.bat` and "Run as administrator"
2. This installs it as a Windows service that starts automatically

## Troubleshooting:
1. If backups fail, check `E:\Database_Backups\backup.log`
2. Ensure PostgreSQL is running
3. Ensure E: drive exists and has space
4. Ensure pg_dump is in system PATH
