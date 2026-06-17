"""Cloud sync configuration dialog for POS system"""

import os
import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QLineEdit, QPushButton, QCheckBox, QSpinBox,
                                QGroupBox, QMessageBox)
from PySide6.QtCore import Qt


class CloudSyncDialog(QDialog):
    """Dialog for configuring cloud synchronization settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cloud Sync Configuration")
        self.setMinimumWidth(500)
        # Use absolute path for config file
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(script_dir))
        self.config_file = os.path.join(parent_dir, "cloud_config.json")
        self.config = self._load_config()
        self._setup_ui()
    
    def _load_config(self):
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
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")
            return False
    
    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # GitHub Settings Group
        github_group = QGroupBox("GitHub Settings")
        github_layout = QVBoxLayout()
        
        # GitHub Repository
        repo_layout = QHBoxLayout()
        repo_label = QLabel("GitHub Repository:")
        repo_label.setMinimumWidth(150)
        self.repo_input = QLineEdit(self.config.get("github_repo", ""))
        self.repo_input.setPlaceholderText("username/repo-name")
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_input)
        github_layout.addLayout(repo_layout)
        
        # GitHub Token (optional)
        token_layout = QHBoxLayout()
        token_label = QLabel("GitHub Token (optional):")
        token_label.setMinimumWidth(150)
        self.token_input = QLineEdit(self.config.get("github_token", ""))
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("For private repos only")
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        github_layout.addLayout(token_layout)
        
        github_info = QLabel("Create a GitHub repository and upload your exe as a Release.")
        github_info.setStyleSheet("color: gray; font-size: 10px;")
        github_info.setWordWrap(True)
        github_layout.addWidget(github_info)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        # Features Group
        features_group = QGroupBox("Cloud Features")
        features_layout = QVBoxLayout()
        
        # Enable Cloud Sync
        self.cloud_enabled_cb = QCheckBox("Enable Cloud Sync")
        self.cloud_enabled_cb.setChecked(self.config.get("cloud_enabled", False))
        self.cloud_enabled_cb.setToolTip("Enable all cloud synchronization features")
        features_layout.addWidget(self.cloud_enabled_cb)
        
        # Auto-Update
        self.update_enabled_cb = QCheckBox("Enable Auto-Update")
        self.update_enabled_cb.setChecked(self.config.get("cloud_enabled", False))
        self.update_enabled_cb.setToolTip("Automatically check for and download updates")
        features_layout.addWidget(self.update_enabled_cb)
        
        # Update Check Interval
        update_interval_layout = QHBoxLayout()
        update_interval_label = QLabel("Update Check Interval (hours):")
        update_interval_label.setMinimumWidth(200)
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setMinimum(1)
        self.update_interval_spin.setMaximum(168)  # 1 week
        self.update_interval_spin.setValue(self.config.get("update_check_interval_hours", 24))
        update_interval_layout.addWidget(update_interval_label)
        update_interval_layout.addWidget(self.update_interval_spin)
        update_interval_layout.addStretch()
        features_layout.addLayout(update_interval_layout)
        
        # Log Upload
        self.log_upload_cb = QCheckBox("Enable Log Upload")
        self.log_upload_cb.setChecked(self.config.get("log_upload_enabled", False))
        self.log_upload_cb.setToolTip("Upload logs to cloud daily")
        features_layout.addWidget(self.log_upload_cb)
        
        # Log Upload Interval
        log_interval_layout = QHBoxLayout()
        log_interval_label = QLabel("Log Upload Interval (hours):")
        log_interval_label.setMinimumWidth(200)
        self.log_interval_spin = QSpinBox()
        self.log_interval_spin.setMinimum(1)
        self.log_interval_spin.setMaximum(168)
        self.log_interval_spin.setValue(self.config.get("log_upload_interval_hours", 24))
        log_interval_layout.addWidget(log_interval_label)
        log_interval_layout.addWidget(self.log_interval_spin)
        log_interval_layout.addStretch()
        features_layout.addLayout(log_interval_layout)
        
        # Backup Upload
        self.backup_upload_cb = QCheckBox("Enable Backup Upload")
        self.backup_upload_cb.setChecked(self.config.get("backup_upload_enabled", False))
        self.backup_upload_cb.setToolTip("Upload database backups to cloud daily")
        features_layout.addWidget(self.backup_upload_cb)
        
        # Backup Upload Interval
        backup_interval_layout = QHBoxLayout()
        backup_interval_label = QLabel("Backup Upload Interval (hours):")
        backup_interval_label.setMinimumWidth(200)
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setMinimum(1)
        self.backup_interval_spin.setMaximum(168)
        self.backup_interval_spin.setValue(self.config.get("backup_upload_interval_hours", 24))
        backup_interval_layout.addWidget(backup_interval_label)
        backup_interval_layout.addWidget(self.backup_interval_spin)
        backup_interval_layout.addStretch()
        features_layout.addLayout(backup_interval_layout)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # Device Info
        device_group = QGroupBox("Device Information")
        device_layout = QVBoxLayout()
        
        try:
            with open("device_id.txt", 'r') as f:
                device_id = f.read().strip()
            device_label = QLabel(f"Device ID: {device_id}")
            device_layout.addWidget(device_label)
        except:
            device_label = QLabel("Device ID: Not generated yet")
            device_layout.addWidget(device_label)
        
        device_info = QLabel("This unique ID identifies your device in the cloud.")
        device_info.setStyleSheet("color: gray; font-size: 10px;")
        device_layout.addWidget(device_info)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        self.test_btn = QPushButton("🧪 Test Uploads")
        self.test_btn.clicked.connect(self._test_uploads)
        button_layout.addWidget(self.test_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _check_for_updates(self):
        """Check for updates manually"""
        try:
            from pos_app.utils.cloud_sync import CloudSync
            sync = CloudSync(self.config_file)
            update_info = sync.check_for_updates()
            
            if update_info:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Update Available")
                msg.setText(f"New version available: {update_info['version']}")
                msg.setInformativeText(update_info.get('release_notes', 'No release notes available.'))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
            else:
                QMessageBox.information(self, "No Updates", "You are already up to date!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check for updates: {e}")
    
    def _save_settings(self):
        """Save the settings"""
        self.config["github_repo"] = self.repo_input.text()
        self.config["github_token"] = self.token_input.text()
        self.config["cloud_enabled"] = self.cloud_enabled_cb.isChecked()
        self.config["update_check_interval_hours"] = self.update_interval_spin.value()
        self.config["log_upload_enabled"] = self.log_upload_cb.isChecked()
        self.config["log_upload_interval_hours"] = self.log_interval_spin.value()
        self.config["backup_upload_enabled"] = self.backup_upload_cb.isChecked()
        self.config["backup_upload_interval_hours"] = self.backup_interval_spin.value()
        
        if self._save_config():
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.accept()
    
    def _test_uploads(self):
        """Test log and backup uploads"""
        try:
            from pos_app.utils.cloud_sync import CloudSync
            sync = CloudSync(self.config_file)
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Testing Uploads")
            msg.setText("Testing log and backup uploads to GitHub...")
            msg.setStandardButtons(QMessageBox.NoButton)
            msg.show()
            
            # Process events to show the message
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
            
            results = sync.test_uploads()
            
            msg.close()
            
            # Show results
            result_text = f"Log Upload: {'✅ Success' if results['log_upload'] else '❌ Failed'}\n"
            result_text += f"Backup Upload: {'✅ Success' if results['backup_upload'] else '❌ Failed'}"
            
            QMessageBox.information(self, "Test Results", result_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to test uploads: {e}")
