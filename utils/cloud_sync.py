"""Cloud synchronization module for POS system
Handles auto-updates, log uploads, and backup uploads to cloud storage
"""

import os
import sys
import json
import requests
import zipfile
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CloudSync:
    """Handles cloud synchronization for POS system"""
    
    def __init__(self, config_file: str = "cloud_config.json"):
        # Use absolute path for config file
        if not os.path.isabs(config_file):
            # Get the parent directory of utils (which is pos_app/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            config_file = os.path.join(parent_dir, config_file)
        
        self.config_file = config_file
        self.config = self._load_config()
        self.device_id = self._get_or_create_device_id()
        self.last_update_check = None
        self.last_log_upload = None
        self.last_backup_upload = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "github_repo": "your-username/pos-system",
            "github_token": "",
            "update_check_interval_hours": 24,
            "log_upload_interval_hours": 24,
            "backup_upload_interval_hours": 24,
            "cloud_enabled": False,
            "log_upload_enabled": False,
            "backup_upload_enabled": False
        }
        
        logger.info(f"Loading config from: {self.config_file}")
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                logger.info(f"Config loaded successfully. cloud_enabled={config.get('cloud_enabled')}, log_upload_enabled={config.get('log_upload_enabled')}, backup_upload_enabled={config.get('backup_upload_enabled')}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        else:
            logger.warning(f"Config file not found: {self.config_file}. Using defaults.")
        
        return default_config
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _get_or_create_device_id(self) -> str:
        """Get or create a unique device ID"""
        # Use absolute path for device ID file in parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        device_id_file = os.path.join(parent_dir, "device_id.txt")
        
        if os.path.exists(device_id_file):
            with open(device_id_file, 'r') as f:
                return f.read().strip()
        else:
            # Generate unique ID based on machine characteristics
            import platform
            machine_id = f"{platform.node()}-{platform.machine()}-{os.getlogin()}"
            device_id = hashlib.md5(machine_id.encode()).hexdigest()[:16]
            with open(device_id_file, 'w') as f:
                f.write(device_id)
            logger.info(f"Created device ID: {device_id}")
            return device_id
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """Check if a new version is available on GitHub Releases"""
        if not self.config.get("cloud_enabled"):
            logger.info("Cloud sync is disabled in config")
            return None
        
        try:
            repo = self.config.get("github_repo")
            if not repo or repo == "your-username/pos-system":
                logger.warning("GitHub repo not configured")
                return None
            
            logger.info(f"Checking for updates from repo: {repo}")
            
            # Get latest release from GitHub
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            headers = {}
            token = self.config.get("github_token")
            if token:
                headers["Authorization"] = f"token {token}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                logger.info(f"No releases found in repository {repo}. Create a release to enable auto-updates.")
                return None
            
            response.raise_for_status()
            
            release = response.json()
            latest_version = release.get("tag_name", "")
            
            # Get current version (use exe modification time as version)
            current_exe_path = sys.executable
            current_version = datetime.fromtimestamp(os.path.getmtime(current_exe_path)).strftime("%Y%m%d")
            
            if latest_version != current_version:
                logger.info(f"New version available: {latest_version} (current: {current_version})")
                
                # Find exe asset
                exe_url = None
                for asset in release.get("assets", []):
                    if asset.get("name", "").endswith(".exe"):
                        exe_url = asset.get("browser_download_url")
                        break
                
                if exe_url:
                    return {
                        "version": latest_version,
                        "download_url": exe_url,
                        "release_notes": release.get("body", ""),
                        "current_version": current_version
                    }
            
            logger.info(f"Already up to date: {current_version}")
            return None
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None
    
    def download_update(self, update_info: Dict[str, Any], download_path: str = "POSSystem_new.exe") -> bool:
        """Download the new exe from GitHub"""
        try:
            logger.info(f"Downloading update from {update_info['download_url']}")
            response = requests.get(update_info['download_url'], stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            logger.info(f"Downloaded: {percent:.1f}%")
            
            logger.info(f"Update downloaded to {download_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            if os.path.exists(download_path):
                os.remove(download_path)
            return False
    
    def apply_update(self, new_exe_path: str) -> bool:
        """Apply the update by replacing the current exe"""
        try:
            current_exe = sys.executable
            backup_path = current_exe + ".old"
            
            # Move current exe to backup
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(current_exe, backup_path)
            
            # Move new exe to current location
            os.rename(new_exe_path, current_exe)
            
            logger.info(f"Update applied successfully. Restart required.")
            return True
            
        except Exception as e:
            logger.error(f"Error applying update: {e}")
            # Try to restore backup
            if os.path.exists(backup_path):
                try:
                    os.rename(backup_path, current_exe)
                except:
                    pass
            return False
    
    def upload_logs(self, logs_dir: str = "logs") -> bool:
        """Upload logs to GitHub repository as individual txt files"""
        if not self.config.get("log_upload_enabled"):
            return False
        
        try:
            # Use absolute path for logs directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            logs_dir = os.path.join(parent_dir, logs_dir)
            
            if not os.path.exists(logs_dir):
                logger.info("No logs directory found")
                return False
            
            success_count = 0
            total_count = 0
            
            # Upload each log file individually
            for file_name in os.listdir(logs_dir):
                if file_name.endswith('.log') or file_name.endswith('.txt'):
                    total_count += 1
                    local_file_path = os.path.join(logs_dir, file_name)
                    github_path = f"cloud_logs/{self.device_id}/{file_name}"
                    
                    if self._upload_to_github(local_file_path, github_path):
                        success_count += 1
                        logger.info(f"Uploaded log: {file_name}")
                    else:
                        logger.error(f"Failed to upload log: {file_name}")
            
            logger.info(f"Log upload complete: {success_count}/{total_count} files uploaded")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error uploading logs: {e}")
            return False
    
    def upload_backup(self, backup_path: str = "backups") -> bool:
        """Upload database backup to GitHub repository as SQL file"""
        if not self.config.get("backup_upload_enabled"):
            return False
        
        try:
            # Use absolute path for backup directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(script_dir)
            backup_path = os.path.join(parent_dir, backup_path)
            
            if not os.path.exists(backup_path):
                logger.info("No backup directory found")
                return False
            
            # Find latest backup file
            backup_files = [f for f in os.listdir(backup_path) if f.endswith('.sql')]
            if not backup_files:
                logger.info("No backup files found")
                return False
            
            latest_backup = max(backup_files, key=lambda f: os.path.getmtime(os.path.join(backup_path, f)))
            backup_file_path = os.path.join(backup_path, latest_backup)
            
            # Upload directly as SQL file
            github_path = f"cloud_backups/{self.device_id}/{latest_backup}"
            success = self._upload_to_github(backup_file_path, github_path)
            
            if success:
                logger.info(f"Successfully uploaded backup: {latest_backup}")
            else:
                logger.error(f"Failed to upload backup: {latest_backup}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error uploading backup: {e}")
            return False
    
    def _upload_to_github(self, local_file_path: str, github_path: str) -> bool:
        """Upload a file to GitHub repository using API"""
        try:
            repo = self.config.get("github_repo")
            token = self.config.get("github_token") or ""
            
            if not repo or repo == "your-username/pos-system":
                logger.warning("GitHub repo not configured")
                return False
            
            # Read file content
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            # Encode to base64
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # Check if file exists
            url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Get current file SHA if it exists
            sha = None
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    sha = response.json().get('sha')
            except:
                pass
            
            # Prepare API payload
            data = {
                "message": f"Upload {github_path} from device {self.device_id}",
                "content": encoded_content
            }
            if sha:
                data["sha"] = sha
            
            # Upload file
            response = requests.put(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Successfully uploaded {local_file_path} to GitHub as {github_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to GitHub: {e}")
            return False
    
    def test_uploads(self) -> Dict[str, bool]:
        """Test log and backup uploads manually - returns dict with success status"""
        results = {
            "log_upload": False,
            "backup_upload": False
        }
        
        logger.info("=== Testing Cloud Sync Uploads ===")
        
        # Test log upload
        logger.info("Testing log upload...")
        results["log_upload"] = self.upload_logs("logs")
        
        # Test backup upload
        logger.info("Testing backup upload...")
        results["backup_upload"] = self.upload_backup("backups")
        
        logger.info(f"=== Upload Test Results: {results} ===")
        return results
    
    def run_periodic_checks(self):
        """Run periodic checks for updates, log uploads, and backup uploads"""
        now = datetime.now()
        
        # Check for updates
        if self.last_update_check is None or (now - self.last_update_check).hours >= self.config.get("update_check_interval_hours", 24):
            logger.info("Checking for updates...")
            update_info = self.check_for_updates()
            if update_info:
                logger.info(f"Update available: {update_info['version']}")
                # TODO: Show dialog to user asking if they want to update
            self.last_update_check = now
        
        # Upload logs
        if self.config.get("log_upload_enabled") and (self.last_log_upload is None or (now - self.last_log_upload).hours >= self.config.get("log_upload_interval_hours", 24)):
            logger.info("Uploading logs...")
            self.upload_logs()
            self.last_log_upload = now
        
        # Upload backup
        if self.config.get("backup_upload_enabled") and (self.last_backup_upload is None or (now - self.last_backup_upload).hours >= self.config.get("backup_upload_interval_hours", 24)):
            logger.info("Uploading backup...")
            self.upload_backup()
            self.last_backup_upload = now


def start_background_sync(config_file: str = None):
    """Start background thread for cloud synchronization"""
    if config_file is None:
        # Use absolute path for config file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        config_file = os.path.join(parent_dir, "cloud_config.json")
    
    def sync_worker():
        sync = CloudSync(config_file)
        while True:
            try:
                sync.run_periodic_checks()
                # Sleep for 1 hour
                import time
                time.sleep(3600)
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                import time
                time.sleep(3600)
    
    thread = threading.Thread(target=sync_worker, daemon=True)
    thread.start()
    logger.info("Cloud sync background thread started")
    return thread
