import os
import subprocess
import webbrowser
from urllib.parse import urlparse

ALLOWED_URL_SCHEMES = {"http", "https"}

def open_target(target: str):
    value = target.strip()
    if not value:
        raise ValueError("O destino está vazio.")

    parsed = urlparse(value)
    if parsed.scheme:
        if parsed.scheme not in ALLOWED_URL_SCHEMES:
            raise ValueError("Tipo de endereço não permitido.")
        webbrowser.open(value)
        return f"Abrindo {value}."

    if os.name != "nt":
        raise RuntimeError("Abertura local v0.2 está disponível no Windows.")

    subprocess.Popen(["cmd", "/c", "start", "", value], shell=False)
    return f"Abrindo {value}."
