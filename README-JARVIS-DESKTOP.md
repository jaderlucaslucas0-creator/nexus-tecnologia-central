# JARVIS Desktop — Nexus Tecnologia

O JARVIS pode rodar como aplicativo Windows, sem depender do navegador.

## Rodar no computador

1. Instale Python 3.12.
2. Abra o terminal na pasta do projeto.
3. Execute:
   `pip install -r desktop-requirements.txt`
4. Execute:
   `python desktop_app.py`

O aplicativo inicia o Flask localmente e abre uma janela nativa com o JARVIS.

## Gerar EXE

No Windows, execute `build-desktop.bat`.

O executável será criado em:

`dist\\JARVIS-Nexus\\JARVIS-Nexus.exe`

O build usa **PySide6/Qt** como backend gráfico do pywebview. O backend WinForms não é usado, evitando o erro de carregamento do `Python.Runtime.dll` que pode ocorrer no PyInstaller.

## Diagnóstico do erro anterior

O erro:

`Failed to resolve Python.Runtime.Loader.Initialize`

vinha do caminho:

`pywebview -> WinForms -> pythonnet -> Python.Runtime.dll`

A versão desktop agora força:

`pywebview -> Qt/PySide6`

## Segurança

Não coloque chaves de API diretamente no código. Use variáveis de ambiente.
