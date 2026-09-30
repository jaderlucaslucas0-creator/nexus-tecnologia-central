# Nexus Tecnologia — JARVIS AI

JARVIS AI v0.2 adiciona pesquisa, memória contextual e ferramentas locais à base desktop modular.

## Arquitetura

- `core/`: núcleo, contexto e segurança.
- `ai/`: roteamento e abstração do provedor de IA.
- `memory/`: SQLite e memória de curto/longo prazo.
- `tools/`: sistema, arquivos, aplicativos e pesquisa.
- `plugins/`: base para plugins.
- `interface/`: interface desktop.
- `security/`: permissões e segurança.
- `tests/`: testes automatizados.

## Executar

```powershell
python -m pip install -r desktop-requirements.txt
python desktop_app.py
```

## Comandos v0.2

- `/system` — informações básicas do computador.
- `/clear` — limpa o contexto.
- `pesquise Python 3.14` — pesquisa na web.
- `procure arquivo relatório` — procura arquivos pelo nome.
- `abra https://exemplo.com` — abre uma URL permitida.
- `memorize ...` — salva memória local.

A pesquisa e serviços externos podem ficar indisponíveis; o núcleo mantém fallback local.

## Próximas versões

v0.3: voz, wake word e automações.
v0.4: visão e plugins avançados.
v0.5: dashboard e logs avançados.
v1.0: pacote completo para uso diário.
