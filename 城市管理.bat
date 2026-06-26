@echo off
chcp 65001 >nul
cd /d "%~dp0"
python city_manager_gui.py
pause
