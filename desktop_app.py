"""JARVIS Desktop - Nexus Tecnologia.

Aplicativo Windows nativo usando PySide6 + QtWebEngine.
Não usa pywebview/pythonnet/WinForms, evitando o erro Python.Runtime.dll.
"""
import os
import sys
import threading
import time
import urllib.request

os.environ.setdefault("COOKIE_SECURE", "0")

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView


def start_local_server():
    from app import app
    app.run(host="127.0.0.1", port=int(os.environ.get("NEXUS_DESKTOP_PORT", "8765")),
            debug=False, use_reloader=False, threaded=True)


def wait_for_server(url):
    for _ in range(100):
        try:
            with urllib.request.urlopen(url + "health", timeout=0.5):
                return
        except Exception:
            time.sleep(0.1)


def main():
    remote_url = os.environ.get("NEXUS_APP_URL", "").strip()
    if remote_url:
        url = remote_url.rstrip("/") + "/"
    else:
        threading.Thread(target=start_local_server, daemon=True).start()
        url = "http://127.0.0.1:8765/"
        wait_for_server("http://127.0.0.1:8765/")

    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS | Nexus Tecnologia")
    app.setOrganizationName("Nexus Tecnologia")

    window = QMainWindow()
    window.setWindowTitle("JARVIS | Nexus Tecnologia")
    window.resize(1440, 900)
    window.setMinimumSize(1050, 700)

    browser = QWebEngineView()
    browser.setUrl(QUrl(url))
    window.setCentralWidget(browser)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
