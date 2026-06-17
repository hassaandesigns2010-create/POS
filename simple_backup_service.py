#!/usr/bin/env python3
"""
PostgreSQL Database Backup - Background Process
Runs every hour and creates backup on E: drive
Runs silently in background without any UI
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import threading
import zipfile

# Configuration
DB_NAME = "pos_network"
DB_USER = "admin"
DB_PASSWORD = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"
BACKUP_DIR = "E:\\Database_Backups"
LOG_FILE = "E:\\Database_Backups\\backup.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
    ]
)
logger = logging.getLogger(__name__)

def ensure_backup_directory():
    """Ensure backup directory exists"""
    if not os.path.exists(BACKUP_DIR):
        try:
            os.makedirs(BACKUP_DIR)
            logger.info(f"Created backup directory: {BACKUP_DIR}")
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            return False
    return True

def create_backup():
    """Create PostgreSQL database backup"""
    try:
        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"pos_backup_{timestamp}.sql")
        
        # Create pg_dump command
        cmd = [
            "pg_dump",
            f"-h{DB_HOST}",
            f"-p{DB_PORT}",
            f"-U{DB_USER}",
            f"-d{DB_NAME}",
            "--no-password",
            "--verbose",
            "--clean",
            "--if-exists",
            "--create",
            f"--file={backup_file}"
        ]
        
        # Set password environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = DB_PASSWORD
        
        logger.info(f"Starting backup: {backup_file}")
        
        # Run backup command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            # Compress the backup file
            compressed_file = backup_file + ".zip"
            with zipfile.ZipFile(compressed_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_file, os.path.basename(backup_file))
            
            # Remove uncompressed file
            os.remove(backup_file)
            
            # Get file size
            size_mb = os.path.getsize(compressed_file) / (1024 * 1024)
            
            logger.info(f"Backup completed: {compressed_file} ({size_mb:.2f} MB)")
            
            # Clean old backups (keep last 24)
            cleanup_old_backups()
            
            return True
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Backup timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return False

def cleanup_old_backups():
    """Keep only last 24 backups (1 day worth)"""
    try:
        backup_files = []
        for file in os.listdir(BACKUP_DIR):
            if file.startswith("pos_backup_") and file.endswith(".zip"):
                file_path = os.path.join(BACKUP_DIR, file)
                backup_files.append((file_path, os.path.getctime(file_path)))
        
        # Sort by creation time (oldest first)
        backup_files.sort(key=lambda x: x[1])
        
        # Keep only last 24 files
        if len(backup_files) > 24:
            for file_path, _ in backup_files[:-24]:
                os.remove(file_path)
                logger.info(f"Removed old backup: {os.path.basename(file_path)}")
                
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def backup_loop():
    """Main backup loop - runs every hour"""
    logger.info("Backup service started")
    
    # Run immediately on start
    create_backup()
    
    # Then run every hour
    while True:
        time.sleep(3600)  # Sleep for 1 hour
        create_backup()

def main():
    """Main entry point"""
    # Hide console window (run in background)
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Ensure backup directory exists
    if not ensure_backup_directory():
        logger.error("Cannot create backup directory. Exiting.")
        return
    
    # Start backup loop in main thread
    backup_loop()

if __name__ == '__main__':
    main()
