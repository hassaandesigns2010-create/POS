@echo off
echo Starting PostgreSQL Backup Service...
echo This window will close automatically and the service will run in background.
echo.

REM Check if backup directory exists
if not exist "E:\Database_Backups" (
    mkdir "E:\Database_Backups"
    echo Created backup directory: E:\Database_Backups
)

REM Start the backup service in background (hidden)
start /B python "C:\Users\pc\Downloads\pos_app\pos_app\simple_backup_service.py"

echo Backup service started in background.
echo Backups will be created every hour in E:\Database_Backups
echo.
echo To stop the service, use Task Manager and end python.exe processes
echo Or restart your computer to stop it.
echo.

timeout /t 3 /nobreak >nul
