import hmac
import os

from flask import Flask, redirect, request, send_from_directory, session, url_for

app = Flask(__name__, static_folder="src", static_url_path="/src")

# Configure these values in Render Environment Variables.
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")


def credentials_configured():
    return bool(ADMIN_USERNAME and ADMIN_PASSWORD)


@app.get("/")
def home():
    if session.get("authenticated"):
        return redirect(url_for("dashboard"))
    return send_from_directory(".", "index.html")


@app.post("/login")
def login():
    if not credentials_configured():
        return {"success": False, "message": "O usuário do sistema ainda não foi configurado no Render."}, 503

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    valid_username = hmac.compare_digest(username, ADMIN_USERNAME)
    valid_password = hmac.compare_digest(password, ADMIN_PASSWORD)

    if valid_username and valid_password:
        session.clear()
        session["authenticated"] = True
        session["username"] = ADMIN_USERNAME
        return redirect(url_for("dashboard"))

    return {"success": False, "message": "Usuário ou senha incorretos."}, 401


@app.get("/dashboard")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("home"))
    return send_from_directory(".", "dashboard.html")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Nexus Tecnologia"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
