import os
from functools import wraps
from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "render-dev-change-this-secret")

ACCESS_USER = os.environ.get("ACCESS_USER", "admin")
ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD", "1234")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.get("/")
def login():
    if session.get("authenticated"):
        return redirect(url_for("dashboard"))
    return app.send_static_file("index.html")


@app.post("/login")
def do_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if username == ACCESS_USER and password == ACCESS_PASSWORD:
        session["authenticated"] = True
        session["username"] = username
        return redirect(url_for("dashboard"))

    return redirect(url_for("login") + "?error=1")


@app.get("/dashboard")
@login_required
def dashboard():
    return app.send_static_file("dashboard.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/health")
def health():
    return {"status": "ok", "system": "Render", "company": "Nexus Tecnologia"}


@app.get("/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
