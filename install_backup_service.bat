@echo off
echo Installing PostgreSQL Backup Service...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run this script as Administrator
    pause
    exit /b 1
)

REM Install required Python packages
echo Installing required packages...
pip install pywin32 schedule

REM Create backup directory
if not exist "E:\Database_Backups" (
    mkdir "E:\Database_Backups"
    echo Created backup directory: E:\Database_Backups
)

REM Install the Windows service
echo Installing Windows service...
python "C:\Users\pc\Downloads\pos_app\pos_app\backup_service.py" install

REM Start the service
echo Starting the service...
net start PostgreSQLBackupService

REM Configure service to start automatically
echo Configuring service to start automatically...
sc config PostgreSQLBackupService start= auto

echo.
echo Installation complete!
echo The service will now run every hour and create backups in E:\Database_Backups
echo.
echo To check status: sc query PostgreSQLBackupService
echo To stop service: net stop PostgreSQLBackupService
echo To uninstall: python "C:\Users\pc\Downloads\pos_app\pos_app\backup_service.py" remove
echo.
pause
