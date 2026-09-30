# JARVIS

Agente de tarefas automáticas do projeto Nexus.

Ele executa tarefas, pesquisa a web quando o tipo é research e salva os resultados em jarvis/results.

Para cadastrar uma pesquisa, edite jarvis/tasks.json.

Exemplo:
{
  "tasks": [
    {
      "id": "noticias-ia",
      "enabled": true,
      "type": "research",
      "title": "Notícias de IA",
      "query": "principais novidades de inteligência artificial hoje",
      "run_at": null,
      "repeat_minutes": 1440
    }
  ]
}

repeat_minutes: 60 = a cada hora; 1440 = diariamente.

O GitHub Actions pode sofrer atrasos de alguns minutos no horário agendado.
