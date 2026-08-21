import hmac, os, sqlite3
from functools import wraps
from pathlib import Path
from flask import Flask, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
app=Flask(__name__,static_folder="src",static_url_path="/src"); app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-key")
DB_PATH=Path(os.environ.get("DATABASE_PATH","nexus.db")); ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME",""); ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD","")
def get_db():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
 c=get_db(); c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"); c.execute("CREATE TABLE IF NOT EXISTS systems (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, url TEXT NOT NULL, description TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
 if ADMIN_USERNAME and ADMIN_PASSWORD and not c.execute("SELECT id FROM users WHERE username=?",(ADMIN_USERNAME,)).fetchone(): c.execute("INSERT INTO users(username,password_hash,name) VALUES(?,?,?)",(ADMIN_USERNAME,generate_password_hash(ADMIN_PASSWORD),"Administrador"))
 c.commit(); c.close()
init_db()
def login_required(view):
 @wraps(view)
 def wrapped(*a,**k): return view(*a,**k) if session.get("authenticated") else redirect(url_for("home"))
 return wrapped
@app.get("/")
def home(): return redirect(url_for("dashboard")) if session.get("authenticated") else send_from_directory(".","index.html")
@app.get("/criar-conta")
def criar_conta_page(): return send_from_directory(".","criar-conta.html")
@app.post("/login")
def login():
 u=request.form.get("username","").strip(); p=request.form.get("password",""); c=get_db(); user=c.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone(); c.close()
 if user and check_password_hash(user["password_hash"],p): session.clear(); session.update(authenticated=True,username=user["username"],name=user["name"]); return redirect(url_for("dashboard"))
 return {"success":False,"message":"Usuário ou senha incorretos."},401
@app.post("/usuarios/criar")
def criar_usuario():
 n=request.form.get("name","").strip(); u=request.form.get("username","").strip(); p=request.form.get("password","")
 if not n or not u or len(p)<6:return {"success":False,"message":"Preencha nome, usuário e uma senha de pelo menos 6 caracteres."},400
 c=get_db()
 try:c.execute("INSERT INTO users(username,password_hash,name) VALUES(?,?,?)",(u,generate_password_hash(p),n));c.commit()
 except sqlite3.IntegrityError:c.close();return {"success":False,"message":"Esse usuário já existe."},409
 c.close();return {"success":True,"message":"Conta criada com sucesso."}
@app.get("/dashboard")
@login_required
def dashboard():return send_from_directory(".","dashboard.html")
@app.get("/usuarios")
@login_required
def usuarios():return send_from_directory(".","usuarios.html")
@app.get("/api/usuarios")
@login_required
def listar_usuarios():
 c=get_db(); rows=c.execute("SELECT id,name,username,created_at FROM users ORDER BY id").fetchall();c.close();return {"users":[dict(x) for x in rows]}
@app.post("/usuarios/excluir/<int:user_id>")
@login_required
def excluir_usuario(user_id):
 c=get_db();u=c.execute("SELECT username FROM users WHERE id=?",(user_id,)).fetchone()
 if u and hmac.compare_digest(u["username"],session.get("username","")):c.close();return {"success":False,"message":"Você não pode excluir o usuário conectado."},400
 c.execute("DELETE FROM users WHERE id=?",(user_id,));c.commit();c.close();return redirect(url_for("usuarios"))
@app.post("/sistemas/criar")
@login_required
def criar_sistema():
 n=request.form.get("name","").strip(); url=request.form.get("url","").strip(); d=request.form.get("description","").strip()
 if not n or not url:return {"success":False,"message":"Informe o nome e a URL do sistema."},400
 if not url.startswith(("http://","https://")):url="https://"+url
 c=get_db();c.execute("INSERT INTO systems(name,url,description) VALUES(?,?,?)",(n,url,d));c.commit();c.close();return redirect(url_for("dashboard"))
@app.get("/api/sistemas")
@login_required
def listar_sistemas():
 c=get_db();rows=c.execute("SELECT id,name,url,description,created_at FROM systems ORDER BY id DESC").fetchall();c.close();return {"systems":[dict(x) for x in rows]}
@app.post("/sistemas/excluir/<int:system_id>")
@login_required
def excluir_sistema(system_id):
 c=get_db();c.execute("DELETE FROM systems WHERE id=?",(system_id,));c.commit();c.close();return redirect(url_for("dashboard"))
@app.post("/logout")
def logout():session.clear();return redirect(url_for("home"))
@app.get("/health")
def health():return {"status":"ok","app":"Nexus Tecnologia"}
if __name__=="__main__":app.run(host="0.0.0.0",port=5000)
