import os
import tempfile

_tmp_dir = tempfile.TemporaryDirectory()
os.environ["DATABASE_PATH"] = os.path.join(_tmp_dir.name, "test.db")
os.environ["COOKIE_SECURE"] = "0"
os.environ.pop("ADMIN_USERNAME", None)
os.environ.pop("ADMIN_PASSWORD", None)

from app import app  # noqa: E402


def test_core_flow():
    app.config.update(TESTING=True)
    client = app.test_client()

    response = client.post("/usuarios/criar", data={"name": "Administrador", "username": "admin", "password": "senha123"})
    assert response.status_code == 200

    duplicate = client.post("/usuarios/criar", data={"name": "Outro", "username": "admin", "password": "senha123"})
    assert duplicate.status_code == 409

    response = client.post("/login", data={"username": "admin", "password": "senha123"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    assert client.get("/health").get_json()["status"] == "ok"
    users = client.get("/api/usuarios").get_json()["users"]
    assert len(users) == 1
    user_id = users[0]["id"]

    response = client.post(f"/usuarios/editar/{user_id}", data={"name": "Administrador Atualizado", "username": "admin2", "password": "nova123"})
    assert response.status_code == 200

    client.post("/logout")
    response = client.post("/login", data={"username": "admin2", "password": "nova123"}, follow_redirects=False)
    assert response.status_code == 302

    response = client.post("/sistemas/criar", data={"name": "Seven Store", "url": "https://seven-store.onrender.com/", "description": "Sistema de teste", "render_service_id": ""})
    assert response.status_code == 200

    systems = client.get("/api/sistemas").get_json()["systems"]
    assert len(systems) == 1
    assert systems[0]["enabled"] == 1
    system_id = systems[0]["id"]

    response = client.post(f"/sistemas/{system_id}/editar", data={"name": "Seven Store", "url": "https://seven-store.onrender.com/", "description": "Atualizado", "render_service_id": ""})
    assert response.status_code == 200

    response = client.post(f"/sistemas/excluir/{system_id}")
    assert response.status_code == 200
    assert client.get("/api/sistemas").get_json()["systems"] == []


if __name__ == "__main__":
    test_core_flow()
    _tmp_dir.cleanup()
    print("Nexus Tecnologia: fluxo principal OK")
