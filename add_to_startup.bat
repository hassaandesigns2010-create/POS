@echo off
echo Creating Windows Startup shortcut for PostgreSQL Backup Service...
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0

REM Create VBScript to make shortcut
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo Set oShortcut = WshShell.CreateShortcut("%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PostgreSQL Backup.lnk") >> "%TEMP%\CreateShortcut.vbs"
echo oShortcut.TargetPath = "%SCRIPT_DIR%simple_backup_service.py" >> "%TEMP%\CreateShortcut.vbs"
echo oShortcut.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oShortcut.WindowStyle = 7  REM Minimized >> "%TEMP%\CreateShortcut.vbs"
echo oShortcut.Save >> "%TEMP%\CreateShortcut.vbs"

REM Execute VBScript to create shortcut
cscript //nologo "%TEMP%\CreateShortcut.vbs"

REM Clean up
del "%TEMP%\CreateShortcut.vbs"

echo.
echo Startup shortcut created successfully!
echo The backup service will now start automatically when Windows boots.
echo.
echo Shortcut location: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PostgreSQL Backup.lnk
echo.
pause
