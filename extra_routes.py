import sqlite3
from flask import jsonify, redirect, request, send_from_directory, session, url_for

from app import BASE_DIR, app, get_db, json_error, login_required


def init_extra_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'normal',
        status TEXT NOT NULL DEFAULT 'aberto',
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()


init_extra_db()


@app.get("/configuracoes")
@login_required
def configuracoes():
    return send_from_directory(BASE_DIR, "configuracoes.html")


@app.get("/relatorios")
@login_required
def relatorios():
    return send_from_directory(BASE_DIR, "relatorios.html")


@app.get("/atendimento")
@login_required
def atendimento():
    return send_from_directory(BASE_DIR, "atendimento.html")


@app.get("/api/relatorios")
@login_required
def api_relatorios():
    conn = get_db()
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    systems = conn.execute("SELECT COUNT(*) FROM systems").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM systems WHERE enabled=1").fetchone()[0]
    inactive = systems - active
    tickets = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    open_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status IN ('aberto','em_atendimento')").fetchone()[0]
    closed_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='resolvido'").fetchone()[0]
    conn.close()
    return jsonify(users=users, systems=systems, active_systems=active,
                   inactive_systems=inactive, tickets=tickets,
                   open_tickets=open_tickets, closed_tickets=closed_tickets)


@app.get("/api/atendimento")
@login_required
def api_atendimento():
    conn = get_db()
    rows = conn.execute("SELECT id,subject,description,priority,status,username,created_at,updated_at FROM tickets ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify(tickets=[dict(r) for r in rows])


@app.post("/api/atendimento")
@login_required
def criar_atendimento():
    subject = request.form.get("subject", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "normal").strip().lower()
    if not subject or not description:
        return json_error("Informe o assunto e a descrição do atendimento.")
    if priority not in {"baixa", "normal", "alta", "urgente"}:
        priority = "normal"
    if len(subject) > 160 or len(description) > 2000:
        return json_error("O atendimento ultrapassa o limite permitido.")
    conn = get_db()
    conn.execute("INSERT INTO tickets(subject,description,priority,status,username) VALUES(?,?,?,?,?)",
                 (subject, description, priority, "aberto", session.get("username", "usuário")))
    conn.commit()
    conn.close()
    return jsonify(success=True, message="Atendimento aberto com sucesso.")


@app.post("/api/atendimento/<int:ticket_id>/status")
@login_required
def atualizar_atendimento(ticket_id):
    status = request.form.get("status", "").strip().lower()
    allowed = {"aberto", "em_atendimento", "resolvido", "cancelado"}
    if status not in allowed:
        return json_error("Status inválido.")
    conn = get_db()
    cur = conn.execute("UPDATE tickets SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return json_error("Atendimento não encontrado.", 404)
    return jsonify(success=True)


@app.post("/api/atendimento/<int:ticket_id>/excluir")
@login_required
def excluir_atendimento(ticket_id):
    conn = get_db()
    cur = conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return json_error("Atendimento não encontrado.", 404)
    return jsonify(success=True)
