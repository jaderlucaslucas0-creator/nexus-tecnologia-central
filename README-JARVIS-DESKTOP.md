# JARVIS Desktop — Nexus Tecnologia

O JARVIS pode rodar como aplicativo Windows, sem depender do navegador.

## Rodar no computador
1. Instale Python 3.12.
2. Abra o terminal na pasta do projeto.
3. Execute: pip install -r desktop-requirements.txt
4. Execute: python desktop_app.py

O aplicativo inicia o Flask localmente e abre uma janela nativa com o JARVIS.

## Gerar EXE
No Windows, execute build-desktop.bat. O executável será criado em dist\\JARVIS-Nexus\\JARVIS-Nexus.exe.

O GitHub Actions também gera automaticamente um ZIP do aplicativo Windows quando o workflow for executado.

## Segurança
Não coloque chaves de API diretamente no código. Use variáveis de ambiente.
