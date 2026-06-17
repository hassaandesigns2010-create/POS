"""Standalone test script for GitHub upload functionality"""

import os
import requests
import base64
from datetime import datetime

# Configuration
GITHUB_REPO = "storesarhad-debug/POS"
GITHUB_TOKEN = ""
DEVICE_ID = "test_device_001"

def upload_to_github(local_file_path: str, github_path: str) -> bool:
    """Upload a file to GitHub repository using API"""
    try:
        print(f"Uploading {local_file_path} to {github_path}...")
        
        # Read file content
        with open(local_file_path, 'rb') as f:
            file_content = f.read()
        
        print(f"File size: {len(file_content)} bytes")
        
        # Encode to base64
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # Check if file exists
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{github_path}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Get current file SHA if it exists
        sha = None
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                sha = response.json().get('sha')
                print(f"File exists, SHA: {sha}")
        except Exception as e:
            print(f"Error checking file existence: {e}")
        
        # Prepare API payload
        data = {
            "message": f"Upload {github_path} from device {DEVICE_ID}",
            "content": encoded_content
        }
        if sha:
            data["sha"] = sha
        
        # Upload file
        print("Sending PUT request to GitHub API...")
        response = requests.put(url, headers=headers, json=data, timeout=60)
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        
        response.raise_for_status()
        
        print(f"✅ Successfully uploaded {local_file_path} to GitHub as {github_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to GitHub: {e}")
        return False

def test_log_upload():
    """Test uploading log file"""
    print("\n=== Testing Log Upload ===")
    
    # Create a test log file
    test_log_content = f"""Test Log from {DEVICE_ID}
Timestamp: {datetime.now()}
This is a test log file for GitHub upload verification.
Line 1: Application started
Line 2: User logged in
Line 3: Sale completed
"""
    
    test_log_file = "test_log.log"
    with open(test_log_file, 'w') as f:
        f.write(test_log_content)
    
    print(f"Created test log file: {test_log_file}")
    
    # Upload
    success = upload_to_github(test_log_file, f"cloud_logs/{DEVICE_ID}/test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Cleanup
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
    
    return success

def test_backup_upload():
    """Test uploading backup file"""
    print("\n=== Testing Backup Upload ===")
    
    # Create a test backup file
    test_backup_content = f"""-- Test Backup from {DEVICE_ID}
-- Timestamp: {datetime.now()}
-- This is a test SQL backup file

CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

INSERT INTO test_table (name) VALUES ('Test Data 1');
INSERT INTO test_table (name) VALUES ('Test Data 2');
"""
    
    test_backup_file = "test_backup.sql"
    with open(test_backup_file, 'w') as f:
        f.write(test_backup_content)
    
    print(f"Created test backup file: {test_backup_file}")
    
    # Upload
    success = upload_to_github(test_backup_file, f"cloud_backups/{DEVICE_ID}/test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
    
    # Cleanup
    if os.path.exists(test_backup_file):
        os.remove(test_backup_file)
    
    return success

if __name__ == "__main__":
    print("=" * 60)
    print("GitHub Upload Test Script")
    print("=" * 60)
    print(f"Repository: {GITHUB_REPO}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Log file
    results["log_upload"] = test_log_upload()
    
    # Test 2: SQL backup file
    results["backup_upload"] = test_backup_upload()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    print("=" * 60)
    
    if all(results.values()):
        print("\n🎉 All tests passed! GitHub upload is working.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
