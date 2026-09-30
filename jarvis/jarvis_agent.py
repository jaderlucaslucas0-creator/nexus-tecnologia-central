#!/usr/bin/env python3
import json, os, re, ssl, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(ROOT, "jarvis", "tasks.json")
OUT_DIR = os.path.join(ROOT, "jarvis", "results")

def load_tasks():
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("tasks", [])

def search_web(query, limit=5):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": "JARVIS/1.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=25, context=ctx) as response:
        html = response.read().decode("utf-8", "ignore")
    blocks = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S)
    results = []
    for href, title in blocks[:limit]:
        title = re.sub(r"<[^>]+>", "", title)
        title = re.sub(r"\s+", " ", title).strip()
        results.append((title, href))
    return results

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
    lines = [f"# JARVIS — {title}", "", f"Executado em: {now.isoformat()}", ""]
    if kind == "research":
        query = task.get("query", title)
        lines += [f"Pesquisa: {query}", ""]
        try:
            results = search_web(query)
            if not results:
                lines.append("Nenhum resultado encontrado.")
            for i, (name, url) in enumerate(results, 1):
                lines.append(f"{i}. [{name}]({url})")
        except Exception as exc:
            lines.append(f"Erro na pesquisa: {exc}")
    else:
        lines += [f"Atividade: {task.get('description', title)}", "", "Tarefa registrada pelo JARVIS."]
    os.makedirs(OUT_DIR, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(task.get("id", "task")))
    path = os.path.join(OUT_DIR, f"{safe}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))

def main():
    now = datetime.now(timezone.utc)
    for task in load_tasks():
        if due(task, now):
            run_task(task)

if __name__ == "__main__":
    main()
