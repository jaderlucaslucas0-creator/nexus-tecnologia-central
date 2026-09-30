"""JARVIS Desktop - Nexus Tecnologia."""
import os
import threading
import time
import urllib.request
import webview

def start_local_server():
    from app import app
    app.run(host="127.0.0.1", port=int(os.environ.get("NEXUS_DESKTOP_PORT", "8765")), debug=False, use_reloader=False, threaded=True)

def main():
    remote_url = os.environ.get("NEXUS_APP_URL", "").strip()
    if remote_url:
        url = remote_url.rstrip("/") + "/jarvis"
    else:
        threading.Thread(target=start_local_server, daemon=True).start()
        url = "http://127.0.0.1:8765/"
        for _ in range(50):
            time.sleep(0.1)
            try:
                with urllib.request.urlopen(url + "health", timeout=0.5):
                    break
            except Exception:
                continue
    webview.create_window("JARVIS | Nexus Tecnologia", url, width=1440, height=900, min_size=(1050, 700), resizable=True, text_select=True)
    webview.start()

if __name__ == "__main__":
    main()
