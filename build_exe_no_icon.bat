@echo off
cd "c:/Users/pc/Downloads/pos_app/pos_app"
pyinstaller --onefile --windowed --name "POSSystem" --exclude PyQt6 --exclude PyQt6.QtCore --exclude PyQt6.QtWidgets --exclude PyQt6.QtGui main.py
pause
