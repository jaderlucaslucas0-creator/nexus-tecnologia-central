"""Nexus Gestão - aplicativo desktop para Windows.

Executa o sistema web em uma janela própria usando pywebview.
Para usar localmente: pip install -r desktop-requirements.txt
Depois: python desktop_app.py
"""
import os
import threading
import webview

APP_URL = os.environ.get("NEXUS_APP_URL", "http://127.0.0.1:5000")


def main():
    webview.create_window(
        "Nexus Gestão",
        APP_URL,
        width=1280,
        height=800,
        min_size=(980, 620),
        resizable=True,
        text_select=True,
    )
    webview.start()


if __name__ == "__main__":
    main()
