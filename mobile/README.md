# Nexus Gestão — Aplicativo Android

Esta pasta inicia o aplicativo mobile do Nexus Gestão.

## Objetivo

Aplicativo para gestão de clínicas e profissionais, conectado a uma API Python e banco PostgreSQL.

## Módulos previstos

- Login e cadastro
- Acesso por código no WhatsApp
- Dashboard
- Pacientes
- Profissionais
- Agenda
- Prontuários
- Sessões
- Documentos
- Financeiro
- Notificações
- Relatórios
- Configurações

## Arquitetura

O aplicativo mobile não deve guardar dados clínicos como fonte principal. Ele consumirá uma API HTTPS autenticada. Os dados serão armazenados no PostgreSQL no servidor.

## Próxima etapa técnica

Criar o projeto Flutter com Android, configurar a URL da API, autenticação por token e navegação entre os módulos.

> Nunca coloque tokens do WhatsApp, senhas, chaves da API ou credenciais do banco neste diretório.
