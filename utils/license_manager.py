6711187122211
import hashlib
import os
import platform
import uuid
from pathlib import Path
try:
    from PySide6.QtWidgets import QInputDialog, QMessageBox, QLineEdit
except ImportError:
    from PyQt6.QtWidgets import QInputDialog, QMessageBox, QLineEdit

class LicenseManager:
    def __init__(self, app_name="POS_System"):
        self.app_name = app_name
        self.license_key = "yallahmaA1!23"  # Hardcoded license key
        self.license_file = self._get_license_file_path()
        self.current_pc_id = self._get_pc_id()

    def _get_license_file_path(self):
        """Get path to the license file in user's app data directory"""
        if platform.system() == "Windows":
            app_data = os.getenv('APPDATA')
            license_dir = os.path.join(app_data, self.app_name)
        else:  # Linux/Mac
            home = os.path.expanduser('~')
            license_dir = os.path.join(home, f".{self.app_name.lower()}")
        
        os.makedirs(license_dir, exist_ok=True)
        return os.path.join(license_dir, "license.dat")

    def _get_pc_id(self):
        """Generate a stable unique ID for the current PC"""
        try:
            # Use more stable identifiers that don't change between restarts
            import subprocess
            import re
            
            # Get motherboard serial number (most stable)
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['wmic', 'baseboard', 'get', 'serialnumber'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        serial = result.stdout.strip()
                        # Extract actual serial number
                        lines = serial.split('\n')
                        for line in lines:
                            if 'SerialNumber' in line and not line.strip().endswith('SerialNumber'):
                                motherboard_serial = line.split('=')[-1].strip()
                                if motherboard_serial and motherboard_serial != 'To be filled by O.E.M.':
                                    print(f"[License] Using motherboard serial: {motherboard_serial}")
                                    return hashlib.sha256(motherboard_serial.encode()).hexdigest()
            except Exception as e:
                print(f"[License] Failed to get motherboard serial: {e}")
            
            # Fallback to disk serial number
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        serial = result.stdout.strip()
                        lines = serial.split('\n')
                        for line in lines:
                            if 'SerialNumber' in line and not line.strip().endswith('SerialNumber'):
                                disk_serial = line.split('=')[-1].strip()
                                if disk_serial:
                                    print(f"[License] Using disk serial: {disk_serial}")
                                    return hashlib.sha256(disk_serial.encode()).hexdigest()
            except Exception as e:
                print(f"[License] Failed to get disk serial: {e}")
            
            # Final fallback - use machine name (more stable than UUID)
            machine = platform.node()
            if machine and machine != '':
                print(f"[License] Using machine name: {machine}")
                return hashlib.sha256(machine.encode()).hexdigest()
                
        except Exception as e:
            print(f"[License] Error generating PC ID: {e}")
        
        # Ultimate fallback - generate a persistent random ID and save it
        persistent_id_file = os.path.join(os.path.dirname(self.license_file), ".pc_id")
        if os.path.exists(persistent_id_file):
            try:
                with open(persistent_id_file, 'r') as f:
                    saved_id = f.read().strip()
                    if saved_id:
                        print(f"[License] Using persistent PC ID: {saved_id}")
                        return saved_id
            except Exception:
                pass
        
        # Generate new persistent ID
        persistent_id = str(uuid.uuid4())
        try:
            with open(persistent_id_file, 'w') as f:
                f.write(persistent_id)
            print(f"[License] Generated new persistent PC ID: {persistent_id}")
            return persistent_id
        except Exception:
            return str(uuid.uuid4())

    def is_license_valid(self):
        """Check if the license is valid for this PC"""
        if not os.path.exists(self.license_file):
            return False
            
        try:
            with open(self.license_file, 'r') as f:
                saved_key, saved_pc_id = f.read().split('|')
                
            # Verify both the key and PC ID match
            return (saved_key == self.license_key and 
                    saved_pc_id == self.current_pc_id)
        except Exception:
            return False

    def activate_license(self, key):
        """Activate the license with the provided key"""
        if key == self.license_key:
            try:
                with open(self.license_file, 'w') as f:
                    f.write(f"{key}|{self.current_pc_id}")
                return True
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to save license: {str(e)}")
                return False
        return False

    def show_license_dialog(self, parent=None):
        """Show license activation dialog"""
        if self.is_license_valid():
            return True
            
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("License Activation")
        msg.setText("Please enter your license key to activate the software.")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        # Create and configure input dialog
        input_widget = QInputDialog(parent)
        input_widget.setWindowTitle("License Key")
        input_widget.setLabelText("Enter License Key:")
        input_widget.setTextEchoMode(QLineEdit.Password)
        
        while True:
            ok = input_widget.exec()
            if not ok:
                return False
                
            key = input_widget.textValue().strip()
            if self.activate_license(key):
                QMessageBox.information(parent, "Success", "License activated successfully!")
                return True
            else:
                retry = QMessageBox.critical(
                    parent,
                    "Invalid Key",
                    "The license key is invalid. Would you like to try again?",
                    QMessageBox.Retry | QMessageBox.Cancel
                )
                if retry != QMessageBox.Retry:
                    return False
