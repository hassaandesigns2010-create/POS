"""
Automatic SQL Backup Manager
Creates SQL backups every time the app runs
"""
import os
import sys
import subprocess
import shutil
from datetime import datetime
import logging
from pathlib import Path

class BackupManager:
    def __init__(self, db_config=None):
        self.db_config = db_config or self.get_default_config()
        self.backup_dir = self.setup_backup_directory()
        self.logger = logging.getLogger(__name__)
        
    def get_default_config(self):
        """Get default database configuration"""
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'pos_network',
            'user': 'admin',
            'password': 'admin'
        }
    
    def setup_backup_directory(self):
        """Create backup directory in the app's running location"""
        # Get the directory where the EXE is running
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as Python script
            app_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(os.path.dirname(app_dir))  # Go up to main app dir
        
        backup_dir = os.path.join(app_dir, 'backups')
        
        # Create backup directory if it doesn't exist
        try:
            os.makedirs(backup_dir, exist_ok=True)
            print(f"✅ Backup directory created: {backup_dir}")
        except Exception as e:
            print(f"❌ Failed to create backup directory: {e}")
            backup_dir = os.path.join(os.getcwd(), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
        return backup_dir
    
    def get_pg_dump_path(self):
        """Find pg_dump.exe in common PostgreSQL installation paths"""
        common_paths = [
            r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\13\bin\pg_dump.exe", 
            r"C:\Program Files\PostgreSQL\12\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
            r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\13\bin\pg_dump.exe",
            r"C:\Program Files (x86)\PostgreSQL\12\bin\pg_dump.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Try to find it in PATH
        try:
            result = subprocess.run(['where', 'pg_dump'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split('\n')[0].strip()
        except:
            pass
        
        return None
    
    def create_sql_backup(self):
        """Create SQL backup using pg_dump"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"pos_backup_{timestamp}.sql")
            
            # Get pg_dump path
            pg_dump_path = self.get_pg_dump_path()
            if not pg_dump_path:
                print("❌ pg_dump not found. Please install PostgreSQL client tools")
                return None
            
            print(f"🔧 Using pg_dump: {pg_dump_path}")
            
            # Build pg_dump command
            cmd = [
                pg_dump_path,
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--username={self.db_config["user"]}',
                f'--dbname={self.db_config["database"]}',
                '--verbose',
                '--clean',
                '--no-owner',
                '--no-privileges',
                '--disable-triggers',
                '--exclude-table-data=schema_migrations',
                f'--file={backup_file}'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            print(f"🔄 Creating SQL backup: {os.path.basename(backup_file)}")
            
            # Execute backup
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                # Verify backup file was created and has content
                if os.path.exists(backup_file) and os.path.getsize(backup_file) > 1000:
                    print(f"✅ SQL backup created successfully: {backup_file}")
                    self.cleanup_old_backups()
                    return backup_file
                else:
                    print(f"❌ Backup file is empty or missing: {backup_file}")
                    return None
            else:
                print(f"❌ Backup failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Backup timed out after 5 minutes")
            return None
        except FileNotFoundError:
            print("❌ pg_dump not found. Please install PostgreSQL client tools")
            return None
        except Exception as e:
            print(f"❌ Backup failed with error: {e}")
            return None
    
    def create_sqlite_backup(self, sqlite_path):
        """Create backup of SQLite database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"sqlite_backup_{timestamp}.db")
            
            if os.path.exists(sqlite_path):
                shutil.copy2(sqlite_path, backup_file)
                print(f"✅ SQLite backup created: {backup_file}")
                return backup_file
            else:
                print(f"❌ SQLite database not found: {sqlite_path}")
                return None
                
        except Exception as e:
            print(f"❌ SQLite backup failed: {e}")
            return None
    
    def cleanup_old_backups(self, keep_count=10):
        """Keep only the most recent backups"""
        try:
            # Clean SQL backups
            sql_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.sql')]
            sql_files.sort(reverse=True)
            
            for old_file in sql_files[keep_count:]:
                old_path = os.path.join(self.backup_dir, old_file)
                os.remove(old_path)
                print(f"🗑️ Removed old backup: {old_file}")
            
            # Clean SQLite backups
            db_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.db')]
            db_files.sort(reverse=True)
            
            for old_file in db_files[keep_count:]:
                old_path = os.path.join(self.backup_dir, old_file)
                os.remove(old_path)
                print(f"🗑️ Removed old SQLite backup: {old_file}")
                
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def get_backup_list(self):
        """Get list of available backups"""
        backups = []
        
        try:
            for file in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, file)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    backups.append({
                        'name': file,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'type': 'SQL' if file.endswith('.sql') else 'SQLite'
                    })
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            print(f"❌ Failed to list backups: {e}")
        
        return backups
    
    def get_psql_path(self):
        """Find psql.exe in common PostgreSQL installation paths"""
        common_paths = [
            r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\13\bin\psql.exe", 
            r"C:\Program Files\PostgreSQL\12\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
            r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
            r"C:\Program Files (x86)\PostgreSQL\14\bin\psql.exe",
            r"C:\Program Files (x86)\PostgreSQL\13\bin\psql.exe",
            r"C:\Program Files (x86)\PostgreSQL\12\bin\psql.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # Try to find it in PATH
        try:
            result = subprocess.run(['where', 'psql'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.split('\n')[0].strip()
        except:
            pass
        
        return None
    
    def restore_from_backup(self, backup_file):
        """Restore database from SQL backup"""
        try:
            if not os.path.exists(backup_file):
                print(f"❌ Backup file not found: {backup_file}")
                return False
            
            print(f"🔄 Restoring from backup: {os.path.basename(backup_file)}")
            
            # Get psql path
            psql_path = self.get_psql_path()
            if not psql_path:
                print("❌ psql not found. Please install PostgreSQL client tools")
                return False
            
            print(f"🔧 Using psql: {psql_path}")
            
            # Build psql command
            cmd = [
                psql_path,
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--username={self.db_config["user"]}',
                f'--dbname={self.db_config["database"]}',
                '--file=' + backup_file,
                '--verbose'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            # Execute restore
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"✅ Database restored successfully from: {backup_file}")
                return True
            else:
                print(f"❌ Restore failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Restore timed out after 10 minutes")
            return False
        except Exception as e:
            print(f"❌ Restore failed with error: {e}")
            return False
    
    def backup_on_startup(self):
        """Create backup when application starts"""
        print("="*60)
        print("🔄 AUTOMATIC BACKUP SYSTEM")
        print("="*60)
        
        # Create PostgreSQL backup
        pg_backup = self.create_sql_backup()
        
        # Create SQLite backup if exists
        sqlite_path = os.path.join(os.path.expanduser('~'), 'POS_Offline_Data.db')
        sqlite_backup = self.create_sqlite_backup(sqlite_path)
        
        # Show backup status
        backups = self.get_backup_list()
        print(f"\n📁 Total backups available: {len(backups)}")
        
        if backups:
            print("\n📋 Recent backups:")
            for i, backup in enumerate(backups[:5]):
                size_mb = backup['size'] / (1024 * 1024)
                print(f"  {i+1}. {backup['name']} ({backup['type']}) - {size_mb:.1f}MB - {backup['created'].strftime('%Y-%m-%d %H:%M')}")
        
        print("="*60)
        
        return pg_backup or sqlite_backup

# Global backup manager instance
backup_manager = None

def initialize_backup(db_config=None):
    """Initialize the backup manager"""
    global backup_manager
    backup_manager = BackupManager(db_config)
    return backup_manager

def create_startup_backup(db_config=None):
    """Create backup on application startup"""
    manager = initialize_backup(db_config)
    return manager.backup_on_startup() if manager else None
