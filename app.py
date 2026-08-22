import hmac
import json
import os
import shutil
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, static_folder="src", static_url_path="/src")
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
app.secret_key = SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "1") != "0",
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)


def choose_database_path():
    """Choose a persistent database location on Render, with safe local fallback."""
    configured = os.environ.get("DATABASE_PATH", "").strip()
    candidates = [Path(configured)] if configured else []
    if not configured:
        candidates.extend([Path("/var/data/nexus.db"), BASE_DIR / "data" / "nexus.db", Path("/tmp/nexus.db")])
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            test_file = candidate.parent / ".nexus_write_test"
            test_file.touch(exist_ok=True)
            test_file.unlink(missing_ok=True)
            return candidate
        except (PermissionError, OSError):
            continue
    return Path("/tmp/nexus.db")


DB_PATH = choose_database_path()
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
RENDER_API_KEY = os.environ.get("RENDER_API_KEY", "").strip()


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("CREATE TABLE IF NOT EXISTS systems (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, url TEXT NOT NULL, description TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    for column, definition in (("enabled", "INTEGER NOT NULL DEFAULT 1"), ("render_service_id", "TEXT DEFAULT ''")):
        try:
            conn.execute(f"ALTER TABLE systems ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError:
            pass
    if ADMIN_USERNAME and ADMIN_PASSWORD and not conn.execute("SELECT id FROM users WHERE username=?", (ADMIN_USERNAME,)).fetchone():
        conn.execute("INSERT INTO users(username,password_hash,name) VALUES(?,?,?)", (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD)))
    conn.commit()
    conn.close()


init_db()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped


def json_error(message, status=400):
    return jsonify(success=False, message=message), status


def render_request(path, method="GET"):
    if not RENDER_API_KEY:
        raise RuntimeError("RENDER_API_KEY não está configurada no serviço Nexus Tecnologia.")
    req = urllib.request.Request("https://api.render.com/v1" + path, method=method, headers={"Authorization": f"Bearer {RENDER_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body) if body else {}


def service_from_payload(item):
    return item.get("service", item) if isinstance(item, dict) else {}


def list_render_services():
    _, data = render_request("/services?limit=100")
    items = data if isinstance(data, list) else data.get("services", [])
    return [service_from_payload(item) for item in items]


def get_render_service(service_id):
    _, data = render_request("/services/" + urllib.parse.quote(service_id, safe=""))
    return service_from_payload(data)


def render_action(service_id, action):
    if not RENDER_API_KEY:
        return False, "RENDER_API_KEY não está configurada no serviço Nexus Tecnologia."
    if not service_id:
        return False, "Nenhum serviço Render está vinculado a este sistema."
    req = urllib.request.Request(f"https://api.render.com/v1/services/{urllib.parse.quote(service_id, safe='')}/{action}", method="POST", headers={"Authorization": f"Bearer {RENDER_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return True, response.status
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return False, f"Render retornou HTTP {exc.code}. {detail[:500]}"
    except Exception as exc:
        return False, f"Falha ao comunicar com o Render: {exc}"


def find_matching_service(system_name, system_url):
    services = list_render_services()
    name_key = "".join(ch for ch in (system_name or "").lower() if ch.isalnum())
    host = urllib.parse.urlparse(system_url or "").netloc.lower().replace("www.", "")
    host_key = "".join(ch for ch in host.split(".")[0] if ch.isalnum()) if host else ""
    for service in services:
        service_name = "".join(ch for ch in (service.get("name", "")).lower() if ch.isalnum())
        service_host = urllib.parse.urlparse(service.get("url") or "").netloc.lower()
        service_host = "".join(ch for ch in service_host.split(".")[0] if ch.isalnum()) if service_host else ""
        if service_name and (service_name == name_key or service_name in name_key or name_key in service_name):
            return service
        if host_key and service_host and (host_key == service_host or host_key in service_host or service_host in host_key):
            return service
    return None


def sync_system_service(system_id, name, url):
    try:
        service = find_matching_service(name, url)
        service_id = service.get("id", "") if service else ""
    except Exception:
        service_id = ""
    if service_id:
        conn = get_db()
        conn.execute("UPDATE systems SET render_service_id=? WHERE id=?", (service_id, system_id))
        conn.commit()
        conn.close()
    return service_id


@app.get("/")
def home():
    return redirect(url_for("dashboard")) if session.get("authenticated") else send_from_directory(BASE_DIR, "index.html")


@app.get("/criar-conta")
def criar_conta_page():
    return send_from_directory(BASE_DIR, "criar-conta.html")


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user["password_hash"], password):
        session.clear()
        session.permanent = True
        session.update(authenticated=True, username=user["username"], name=user["name"])
        return redirect(url_for("dashboard"))
    return json_error("Usuário ou senha incorretos.", 401)


@app.post("/usuarios/criar")
def criar_usuario():
    name = request.form.get("name", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not name or not username or len(password) < 6:
        return json_error("Preencha nome, usuário e uma senha de pelo menos 6 caracteres.")
    if len(username) > 80 or len(name) > 120:
        return json_error("Nome ou usuário muito longo.")
    conn = get_db()
    try:
        conn.execute("INSERT INTO users(username,password_hash,name) VALUES(?,?,?)", (username, generate_password_hash(password), name))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return json_error("Esse usuário já existe.", 409)
    except sqlite3.Error as exc:
        conn.rollback()
        conn.close()
        return json_error(f"Erro ao salvar a conta no banco de dados: {exc}", 500)
    conn.close()
    return jsonify(success=True, message="Conta criada com sucesso.")


@app.get("/dashboard")
@login_required
def dashboard():
    return send_from_directory(BASE_DIR, "dashboard.html")


@app.get("/usuarios")
@login_required
def usuarios():
    return send_from_directory(BASE_DIR, "usuarios.html")


@app.get("/sistemas")
@login_required
def sistemas():
    return send_from_directory(BASE_DIR, "sistemas.html")


@app.get("/api/usuarios")
@login_required
def listar_usuarios():
    conn = get_db()
    rows = conn.execute("SELECT id,name,username,created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return jsonify(users=[dict(row) for row in rows])


@app.post("/usuarios/excluir/<int:user_id>")
@login_required
def excluir_usuario(user_id):
    conn = get_db()
    user = conn.execute("SELECT username FROM users WHERE id=?", (user_id,)).fetchone()
    if user and hmac.compare_digest(user["username"], session.get("username", "")):
        conn.close()
        return json_error("Você não pode excluir o usuário conectado.")
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.post("/sistemas/criar")
@login_required
def criar_sistema():
    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()
    description = request.form.get("description", "").strip()
    service_id = request.form.get("render_service_id", "").strip()
    if not name or not url:
        return json_error("Informe o nome e a URL do sistema.")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if RENDER_API_KEY and not service_id:
        service = find_matching_service(name, url)
        service_id = service.get("id", "") if service else ""
    conn = get_db()
    conn.execute("INSERT INTO systems(name,url,description,enabled,render_service_id) VALUES(?,?,?,1,?)", (name, url, description, service_id))
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.post("/sistemas/<int:system_id>/editar")
@login_required
def editar_sistema(system_id):
    name = request.form.get("name", "").strip()
    url = request.form.get("url", "").strip()
    description = request.form.get("description", "").strip()
    service_id = request.form.get("render_service_id", "").strip()
    if not name or not url:
        return json_error("Informe o nome e a URL do sistema.")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    conn = get_db()
    if not conn.execute("SELECT id FROM systems WHERE id=?", (system_id,)).fetchone():
        conn.close()
        return json_error("Sistema não encontrado.", 404)
    conn.execute("UPDATE systems SET name=?,url=?,description=?,render_service_id=? WHERE id=?", (name, url, description, service_id, system_id))
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.get("/api/sistemas")
@login_required
def listar_sistemas():
    conn = get_db()
    rows = conn.execute("SELECT id,name,url,description,enabled,render_service_id,created_at FROM systems ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(systems=[dict(row) for row in rows])


@app.get("/api/render-services")
@login_required
def api_render_services():
    if not RENDER_API_KEY:
        return jsonify(configured=False, services=[], message="Adicione RENDER_API_KEY nas Environment Variables do Render."), 503
    try:
        services = list_render_services()
        return jsonify(configured=True, services=[{"id": s.get("id"), "name": s.get("name"), "type": s.get("type"), "url": s.get("url"), "suspended": bool(s.get("suspended"))} for s in services if s.get("id") and s.get("name")])
    except urllib.error.HTTPError as exc:
        return jsonify(configured=True, services=[], message=f"Render retornou HTTP {exc.code}. Verifique a RENDER_API_KEY."), 502
    except Exception as exc:
        return jsonify(configured=False, services=[], message=str(exc)), 503


@app.post("/sistemas/<int:system_id>/toggle")
@login_required
def toggle_sistema(system_id):
    conn = get_db()
    row = conn.execute("SELECT id,name,url,render_service_id FROM systems WHERE id=?", (system_id,)).fetchone()
    conn.close()
    if not row:
        return json_error("Sistema não encontrado.", 404)
    if not RENDER_API_KEY:
        return json_error("A RENDER_API_KEY não está configurada no serviço Nexus Tecnologia.", 503)
    service_id = row["render_service_id"] or sync_system_service(system_id, row["name"], row["url"])
    if not service_id:
        return json_error("Não encontrei automaticamente o serviço no Render. Edite o sistema e selecione o serviço correto.")
    try:
        service = get_render_service(service_id)
        currently_suspended = bool(service.get("suspended"))
    except Exception as exc:
        return json_error(f"Não consegui consultar o estado do Render: {exc}", 502)
    action = "resume" if currently_suspended else "suspend"
    desired_enabled = action == "resume"
    ok, detail = render_action(service_id, action)
    if not ok:
        return json_error(str(detail), 502)
    confirmed = False
    final_suspended = currently_suspended
    for _ in range(5):
        time.sleep(1)
        try:
            current = get_render_service(service_id)
            final_suspended = bool(current.get("suspended"))
            if final_suspended == (not desired_enabled):
                confirmed = True
                break
        except Exception:
            continue
    if not confirmed:
        return json_error("O Render recebeu o comando, mas ainda não confirmou a mudança de estado. Aguarde alguns segundos e atualize.", 409)
    conn = get_db()
    conn.execute("UPDATE systems SET enabled=?,render_service_id=? WHERE id=?", (1 if desired_enabled else 0, service_id, system_id))
    conn.commit()
    conn.close()
    return jsonify(success=True, enabled=desired_enabled, suspended=final_suspended, render_controlled=True)


@app.post("/sistemas/excluir/<int:system_id>")
@login_required
def excluir_sistema(system_id):
    conn = get_db()
    conn.execute("DELETE FROM systems WHERE id=?", (system_id,))
    conn.commit()
    conn.close()
    return jsonify(success=True)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/health")
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1").fetchone()
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        return jsonify(status="ok", app="Nexus Tecnologia", database=str(DB_PATH), users=user_count, persistent=str(DB_PATH).startswith("/var/data"), render_configured=bool(RENDER_API_KEY))
    except Exception as exc:
        return jsonify(status="error", app="Nexus Tecnologia", error=str(exc)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
