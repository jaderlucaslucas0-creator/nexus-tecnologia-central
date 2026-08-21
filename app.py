import hmac
import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="src", static_url_path="/src")
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DB_PATH = Path(os.environ.get("DATABASE_PATH", "nexus.db"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    if ADMIN_USERNAME and ADMIN_PASSWORD:
        exists = conn.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,)).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)",
                (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD), "Administrador"),
            )
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


@app.get("/")
def home():
    if session.get("authenticated"):
        return redirect(url_for("dashboard"))
    return send_from_directory(".", "index.html")


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    valid = bool(user and check_password_hash(user["password_hash"], password))
    if valid:
        session.clear()
        session["authenticated"] = True
        session["username"] = user["username"]
        session["name"] = user["name"]
        return redirect(url_for("dashboard"))

    return {"success": False, "message": "Usuário ou senha incorretos."}, 401


@app.get("/dashboard")
@login_required
def dashboard():
    return send_from_directory(".", "dashboard.html")


@app.get("/usuarios")
@login_required
def usuarios():
    return send_from_directory(".", "usuarios.html")


@app.post("/usuarios/criar")
@login_required
def criar_usuario():
    name = request.form.get("name", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not name or not username or len(password) < 6:
        return {"success": False, "message": "Preencha nome, usuário e uma senha de pelo menos 6 caracteres."}, 400

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, name) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), name),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "message": "Esse usuário já existe."}, 409
    conn.close()
    return redirect(url_for("usuarios"))


@app.post("/usuarios/excluir/<int:user_id>")
@login_required
def excluir_usuario(user_id):
    conn = get_db()
    user = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if user and hmac.compare_digest(user["username"], session.get("username", "")):
        conn.close()
        return {"success": False, "message": "Você não pode excluir o usuário que está conectado."}, 400
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("usuarios"))


@app.get("/api/usuarios")
@login_required
def listar_usuarios():
    conn = get_db()
    users = conn.execute("SELECT id, name, username, created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return {"users": [dict(user) for user in users]}


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Nexus Tecnologia"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
