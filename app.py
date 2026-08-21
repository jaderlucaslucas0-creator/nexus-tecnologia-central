import hmac
import os
import sqlite3

from flask import Flask, jsonify, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="src", static_url_path="/src")

app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
DB_PATH = os.environ.get("DATABASE_PATH", "/var/data/nexus.db")


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()
    db.close()


init_db()


def credentials_configured():
    return bool(ADMIN_USERNAME and ADMIN_PASSWORD)


def authenticate_user(username, password):
    if credentials_configured():
        if hmac.compare_digest(username, ADMIN_USERNAME) and hmac.compare_digest(password, ADMIN_PASSWORD):
            return True

    db = get_db()
    user = db.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return bool(user and check_password_hash(user["password_hash"], password))


@app.get("/")
def home():
    if session.get("authenticated"):
        return redirect(url_for("dashboard"))
    return send_from_directory(".", "index.html")


@app.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if authenticate_user(username, password):
        session.clear()
        session["authenticated"] = True
        session["username"] = username
        return redirect(url_for("dashboard"))

    return {"success": False, "message": "Usuário ou senha incorretos."}, 401


@app.get("/dashboard")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("home"))
    return send_from_directory(".", "dashboard.html")


@app.get("/api/usuarios")
def listar_usuarios():
    if not session.get("authenticated"):
        return {"success": False, "message": "Não autorizado."}, 401

    db = get_db()
    users = db.execute("SELECT id, username, created_at FROM users ORDER BY username").fetchall()
    db.close()
    return jsonify({"success": True, "users": [dict(user) for user in users]})


@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if not session.get("authenticated"):
        return redirect(url_for("home"))

    if request.method == "GET":
        return send_from_directory(".", "usuarios.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if len(username) < 3:
        return {"success": False, "message": "O usuário precisa ter pelo menos 3 caracteres."}, 400
    if len(password) < 6:
        return {"success": False, "message": "A senha precisa ter pelo menos 6 caracteres."}, 400
    if password != confirm_password:
        return {"success": False, "message": "As senhas não conferem."}, 400
    if credentials_configured() and hmac.compare_digest(username, ADMIN_USERNAME):
        return {"success": False, "message": "Esse usuário já está reservado para o administrador."}, 409

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return {"success": False, "message": "Esse usuário já existe."}, 409
    finally:
        db.close()

    return {"success": True, "message": "Usuário criado com sucesso!"}


@app.post("/usuarios/<int:user_id>/excluir")
def excluir_usuario(user_id):
    if not session.get("authenticated"):
        return {"success": False, "message": "Não autorizado."}, 401

    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return {"success": False, "message": "Usuário não encontrado."}, 404

    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    db.close()
    return redirect(url_for("dashboard"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Nexus Tecnologia"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
