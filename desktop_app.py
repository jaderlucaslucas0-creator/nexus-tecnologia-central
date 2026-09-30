"""JARVIS Desktop - Nexus Tecnologia.

Windows desktop wrapper using pywebview + Qt/PySide6.
Qt is used explicitly to avoid the WinForms/pythonnet backend that can
fail inside PyInstaller with Python.Runtime.dll.
"""
import os
import threading
import time
import urllib.request

# O servidor local usa HTTP; cookies Secure impediriam a sessão de login no desktop.
os.environ.setdefault("COOKIE_SECURE", "0")

import webview


def start_local_server():
    from app import app

    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("NEXUS_DESKTOP_PORT", "8765")),
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def main():
    remote_url = os.environ.get("NEXUS_APP_URL", "").strip()

    if remote_url:
        url = remote_url.rstrip("/") + "/"
    else:
        threading.Thread(target=start_local_server, daemon=True).start()
        url = "http://127.0.0.1:8765/"

        for _ in range(80):
            try:
                with urllib.request.urlopen(url + "health", timeout=0.5):
                    break
            except Exception:
                time.sleep(0.1)

    webview.create_window(
        "JARVIS | Nexus Tecnologia",
        url,
        width=1440,
        height=900,
        min_size=(1050, 700),
        resizable=True,
        text_select=True,
    )

    # Força o backend Qt/PySide6 no Windows.
    # Isso evita o caminho WinForms -> pythonnet -> Python.Runtime.dll.
    webview.start(gui="qt", debug=False)


if __name__ == "__main__":
    main()
