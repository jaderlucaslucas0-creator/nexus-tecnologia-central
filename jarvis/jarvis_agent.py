#!/usr/bin/env python3
import html
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(ROOT, "jarvis", "tasks.json")
OUT_DIR = os.path.join(ROOT, "jarvis", "results")


def load_tasks():
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("tasks", [])


def _duckduckgo(query, limit=8):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-Research/2.0"})
    with urllib.request.urlopen(url=req, timeout=25, context=ssl.create_default_context()) as response:
        source = response.read().decode("utf-8", "ignore")

    blocks = re.findall(
        r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        source, re.I | re.S
    )
    results = []
    for href, title in blocks[:limit]:
        title = html.unescape(re.sub(r"<[^>]+>", "", title))
        title = re.sub(r"\s+", " ", title).strip()
        results.append((title, href))
    return results


def search_web(query, limit=8):
    """Usa várias formulações da pergunta e remove resultados duplicados."""
    queries = [
        query,
        f"{query} notícias",
        f"{query} análise",
        f"{query} documentação",
        f"{query} dados evidências",
        f"{query} pesquisa estudo",
    ]
    seen = set()
    collected = []

    for search_query in queries:
        try:
            for title, url in _duckduckgo(search_query, limit):
                key = url.split("#")[0].lower()
                if key not in seen:
                    seen.add(key)
                    collected.append((title, url, search_query))
        except Exception:
            continue
        if len(collected) >= limit * 2:
            break

    return collected[:limit * 2]


def fetch_page_text(url, max_chars=6000):
    """Tenta extrair texto público da página para comparação."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-Research/2.0"})
        with urllib.request.urlopen(req, timeout=15, context=ssl.create_default_context()) as response:
            raw = response.read(max_chars * 5).decode("utf-8", "ignore")

        raw = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
        raw = re.sub(r"<style[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
        raw = re.sub(r"<[^>]+>", " ", raw)
        return re.sub(r"\s+", " ", html.unescape(raw)).strip()[:max_chars]
    except Exception as exc:
        return f"[Fonte não acessível: {exc}]"


def build_research_report(query):
    sources = search_web(query)
    report = [
        "# JARVIS — INVESTIGAÇÃO APROFUNDADA",
        "",
        f"**Pergunta:** {query}",
        f"**Executado:** {datetime.now(timezone.utc).isoformat()}",
        f"**Fontes únicas encontradas:** {len(sources)}",
        "",
        "## 1. Fontes encontradas",
        ""
    ]

    for index, (title, url, search_query) in enumerate(sources, 1):
        text = fetch_page_text(url)
        report.extend([
            f"### Fonte {index}: {title}",
            f"- URL: {url}",
            f"- Consulta: {search_query}",
            f"- Evidência disponível: {text[:1800]}",
            ""
        ])
        time.sleep(0.2)

    report.extend([
        "## 2. Verificação cruzada",
        "",
        "O JARVIS coletou a mesma questão usando diferentes formulações para aumentar a cobertura.",
        "Resultados repetidos foram removidos por URL.",
        "Afirmações presentes em fontes independentes devem ser comparadas antes de serem tratadas como confirmadas.",
        "",
        "## 3. Conflitos e incertezas",
        "",
        "Diferenças entre fontes podem ocorrer por data, contexto, metodologia ou atualização dos dados.",
        "O JARVIS deve registrar essas diferenças em vez de escolher uma resposta sem evidência suficiente.",
        "",
        "## 4. Limitações",
        "",
        "Páginas bloqueadas, conteúdo dinâmico, paywalls e informações ausentes podem impedir a verificação completa.",
        "Uma busca automatizada não garante que todos os documentos existentes na internet tenham sido encontrados.",
        "",
        "## 5. Regra de conclusão",
        "",
        "O JARVIS não deve inventar informações. Quando as evidências forem insuficientes ou conflitantes, deve declarar a incerteza e realizar nova pesquisa quando possível."
    ])
    return "\n".join(report)


def due(task, now):
    if not task.get("enabled", True):
        return False

    run_at = task.get("run_at")
    if not run_at:
        return True

    try:
        target = datetime.fromisoformat(run_at.replace("Z", "+00:00"))
        repeat = int(task.get("repeat_minutes") or 0)

        if repeat <= 0:
            return now >= target and not task.get("_done", False)

        return now >= target
    except Exception:
        return False


def run_task(task):
    now = datetime.now(timezone.utc)
    title = task.get("title", task.get("id", "Tarefa"))
    kind = task.get("type", "research")

    if kind == "research":
        query = task.get("query", title)
        try:
            output = build_research_report(query)
        except Exception as exc:
            output = f"# JARVIS — {title}\n\nErro na pesquisa: {exc}\n"
    else:
        output = (
            f"# JARVIS — {title}\n\n"
            f"Executado em: {now.isoformat()}\n\n"
            f"Atividade: {task.get('description', title)}\n"
        )

    os.makedirs(OUT_DIR, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(task.get("id", "task")))
    path = os.path.join(OUT_DIR, f"{safe}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(output + "\n")

    print(output)


def main():
    now = datetime.now(timezone.utc)
    for task in load_tasks():
        if due(task, now):
            run_task(task)


if __name__ == "__main__":
    main()
