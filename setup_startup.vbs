Set WshShell = CreateObject("WScript.Shell")
Set oShortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Startup") & "\PostgreSQL Backup.lnk")
oShortcut.TargetPath = "pythonw"
oShortcut.Arguments = "simple_backup_service.py"
oShortcut.WorkingDirectory = "C:\Users\pc\Downloads\pos_app\pos_app"
oShortcut.WindowStyle = 7
oShortcut.Save
MsgBox "PostgreSQL Backup Service has been added to Windows startup!", 64, "Setup Complete"
