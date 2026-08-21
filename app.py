from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="src", static_url_path="/src")


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "app": "Nexus Tecnologia"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
