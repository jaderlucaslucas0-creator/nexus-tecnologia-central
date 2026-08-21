import hmac
import os
import sqlite3

from flask import Flask, jsonify, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, static_folder="src", static_url_path="/src")

# Configure these values in Render Environment Variables.
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
DB_PATH = os.environ.get("DATABASE_PATH", "nexus.db")


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
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
        valid_username = hmac.compare_digest(username, ADMIN_USERNAME)
        valid_password = hmac.compare_digest(password, ADMIN_PASSWORD)
        if valid_username and valid_password:
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
        return jsonify(success=False, message="O usuário precisa ter pelo menos 3 caracteres."), 400
    if len(password) < 6:
        return jsonify(success=False, message="A senha precisa ter pelo menos 6 caracteres."), 400
    if password != confirm_password:
        return jsonify(success=False, message="As senhas não conferem."), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(success=False, message="Esse usuário já existe."), 409
    finally:
        db.close()

    return jsonify(success=True, message="Usuário criado com sucesso!")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Nexus Tecnologia"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
