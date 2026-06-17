@echo off
echo POS System Installer
echo =====================
echo.

echo Creating installation directory...
if not exist "C:\POSSystem" mkdir "C:\POSSystem"

echo Copying files...
copy "dist\POSSystem.exe" "C:\POSSystem\"
xcopy "config" "C:\POSSystem\config\" /E /I /Y
xcopy "assets" "C:\POSSystem\assets\" /E /I /Y
xcopy "static" "C:\POSSystem\static\" /E /I /Y

echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\POSSystem.lnk'); $Shortcut.TargetPath = 'C:\POSSystem\POSSystem.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run POS System from your desktop or from C:\POSSystem\POSSystem.exe
echo.
pause
