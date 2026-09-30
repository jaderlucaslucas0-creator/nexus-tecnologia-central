@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r desktop-requirements.txt

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q JARVIS-Nexus.spec 2>nul

python -m PyInstaller --noconfirm --clean --windowed --name JARVIS-Nexus ^
  --collect-all PySide6 ^
  --collect-all webview ^
  --hidden-import=webview.platforms.qt ^
  --add-data "index.html;." ^
  --add-data "dashboard.html;." ^
  --add-data "jarvis.html;." ^
  --add-data "criar-conta.html;." ^
  --add-data "usuarios.html;." ^
  --add-data "sistemas.html;." ^
  --add-data "src;src" ^
  --add-data "jarvis;jarvis" ^
  desktop_app.py

if errorlevel 1 exit /b 1

echo.
echo JARVIS criado em dist\JARVIS-Nexus\JARVIS-Nexus.exe
