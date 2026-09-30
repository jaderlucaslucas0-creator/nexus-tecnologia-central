# Nexus Tecnologia — JARVIS AI

JARVIS AI v0.1 é a primeira base desktop modular do assistente pessoal da Nexus Tecnologia.

## Desktop v0.1

- Interface desktop PySide6.
- JARVIS Core com contexto e roteamento básico.
- Memória persistente SQLite.
- Camada de segurança para ações locais.
- Ferramentas de sistema e abertura de URLs.
- Arquitetura inicial de plugins.
- Fallback local quando nenhum provedor remoto de IA está configurado.
- Testes do núcleo e build automático para Windows.

## Estrutura

core/ — núcleo, contexto e segurança.
ai/ — abstração de provedores de IA.
memory/ — SQLite e memória persistente.
tools/ — ferramentas locais.
plugins/ — sistema de plugins.
interface/ — interface e tema futurista.
security/ — camada de permissões.
tests/ — testes automatizados.

## Executar

```powershell
python -m pip install -r desktop-requirements.txt
python desktop_app.py
```

Comandos iniciais: `/system`, `/clear`, `abra https://exemplo.com`, `memorize ...`.

## Evolução

v0.1: núcleo, interface, memória, segurança e ferramentas básicas.
v0.2: IA remota, pesquisa e comandos adicionais.
v0.3: voz, wake word e automações.
v0.4: visão e plugins avançados.
v0.5: dashboard e logs avançados.
v1.0: pacote completo para uso diário.

A aplicação web existente da Nexus Tecnologia permanece preservada; `desktop_app.py` é o ponto de entrada do aplicativo desktop.