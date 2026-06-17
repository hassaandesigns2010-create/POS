@echo off
cd "c:/Users/pc/Downloads/pos_app/pos_app"
pyinstaller --onefile --windowed --name "POSSystem" --icon "assets/icon.ico" main.py
pause
