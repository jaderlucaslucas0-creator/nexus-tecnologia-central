@echo off
setlocal
python -m pip install -r desktop-requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name JARVIS-Nexus --add-data "index.html;." --add-data "dashboard.html;." --add-data "jarvis.html;." --add-data "criar-conta.html;." --add-data "usuarios.html;." --add-data "sistemas.html;." --add-data "src;src" --add-data "jarvis;jarvis" desktop_app.py
if errorlevel 1 exit /b 1
echo JARVIS criado em dist\JARVIS-Nexus\JARVIS-Nexus.exe
