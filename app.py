import hmac, os, sqlite3, urllib.request, urllib.error, urllib.parse, json
from functools import wraps
from pathlib import Path
from flask import Flask, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app=Flask(__name__,static_folder="src",static_url_path="/src")
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-key")
app.permanent_session_lifetime=60*60*24*30
DB_PATH=Path(os.environ.get("DATABASE_PATH","/var/data/nexus.db")); DB_PATH.parent.mkdir(parents=True,exist_ok=True)
ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME",""); ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD",""); RENDER_API_KEY=os.environ.get("RENDER_API_KEY","")

def get_db(): c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
 c=get_db(); c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"); c.execute("CREATE TABLE IF NOT EXISTS systems (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, url TEXT NOT NULL, description TEXT DEFAULT '', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
 for col,typ in [("enabled","INTEGER NOT NULL DEFAULT 1"),("render_service_id","TEXT DEFAULT ''")]:
  try:c.execute(f"ALTER TABLE systems ADD COLUMN {col} {typ}")
  except sqlite3.OperationalError:pass
 if ADMIN_USERNAME and ADMIN_PASSWORD and not c.execute("SELECT id FROM users WHERE username=?",(ADMIN_USERNAME,)).fetchone(): c.execute("INSERT INTO users(username,password_hash,name) VALUES(?,?,?)",(ADMIN_USERNAME,generate_password_hash(ADMIN_PASSWORD),"Administrador"))
 c.commit();c.close()
init_db()

def login_required(view):
 @wraps(view)
 def wrapped(*a,**k): return view(*a,**k) if session.get("authenticated") else redirect(url_for("home"))
 return wrapped

def render_request(path,method="GET"):
 if not RENDER_API_KEY: raise RuntimeError("RENDER_API_KEY não está configurada no serviço Nexus.")
 req=urllib.request.Request("https://api.render.com/v1"+path,method=method,headers={"Authorization":f"Bearer {RENDER_API_KEY}","Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=20) as r:
  body=r.read().decode("utf-8"); return r.status,json.loads(body) if body else {}

def service_from_payload(item):
 return item.get("service",item) if isinstance(item,dict) else {}

def list_render_services():
 _,data=render_request("/services?limit=100")
 items=data if isinstance(data,list) else data.get("services",[])
 return [service_from_payload(x) for x in items]

def get_render_service(service_id):
 _,data=render_request("/services/"+urllib.parse.quote(service_id,safe=""))
 return service_from_payload(data)

def render_action(service_id,action):
 if not RENDER_API_KEY:return False,"O RENDER_API_KEY não está configurado no serviço Nexus."
 if not service_id:return False,"Selecione o serviço do Render deste sistema antes de ligar/desligar."
 req=urllib.request.Request(f"https://api.render.com/v1/services/{urllib.parse.quote(service_id,safe='')}/{action}",method="POST",headers={"Authorization":f"Bearer {RENDER_API_KEY}","Accept":"application/json"})
 try:
  with urllib.request.urlopen(req,timeout=20) as r:return True,r.status
 except urllib.error.HTTPError as e:
  detail=e.read().decode("utf-8",errors="replace")
  return False,f"Render retornou HTTP {e.code}. {detail[:250]}"
 except Exception as e:return False,f"Falha ao comunicar com o Render: {e}"

@app.get("/")
def home(): return redirect(url_for("dashboard")) if session.get("authenticated") else send_from_directory(".","index.html")
@app.get("/criar-conta")
def criar_conta_page(): return send_from_directory(".","criar-conta.html")
@app.post("/login")
def login():
 u=request.form.get("username","").strip();p=request.form.get("password","");c=get_db();user=c.execute("SELECT * FROM users WHERE username=?",(u,)).fetchone();c.close()
 if user and check_password_hash(user["password_hash"],p):session.clear();session.permanent=True;session.update(authenticated=True,username=user["username"],name=user["name"]);return redirect(url_for("dashboard"))
 return {"success":False,"message":"Usuário ou senha incorretos."},401
@app.post("/usuarios/criar")
def criar_usuario():
 n=request.form.get("name","").strip();u=request.form.get("username","").strip();p=request.form.get("password","")
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
@app.get("/sistemas")
@login_required
def sistemas():return send_from_directory(".","sistemas.html")
@app.get("/api/usuarios")
@login_required
def listar_usuarios():
 c=get_db();rows=c.execute("SELECT id,name,username,created_at FROM users ORDER BY id").fetchall();c.close();return {"users":[dict(x) for x in rows]}
@app.post("/usuarios/excluir/<int:user_id>")
@login_required
def excluir_usuario(user_id):
 c=get_db();u=c.execute("SELECT username FROM users WHERE id=?",(user_id,)).fetchone()
 if u and hmac.compare_digest(u["username"],session.get("username","")):c.close();return {"success":False,"message":"Você não pode excluir o usuário conectado."},400
 c.execute("DELETE FROM users WHERE id=?",(user_id,));c.commit();c.close();return redirect(url_for("usuarios"))
@app.post("/sistemas/criar")
@login_required
def criar_sistema():
 n=request.form.get("name","").strip();url=request.form.get("url","").strip();d=request.form.get("description","").strip();sid=request.form.get("render_service_id","").strip()
 if not n or not url:return {"success":False,"message":"Informe o nome e a URL do sistema."},400
 if not url.startswith(("http://","https://")):url="https://"+url
 c=get_db();c.execute("INSERT INTO systems(name,url,description,enabled,render_service_id) VALUES(?,?,?,1,?)",(n,url,d,sid));c.commit();c.close();return redirect(url_for("sistemas"))
@app.post("/sistemas/<int:system_id>/editar")
@login_required
def editar_sistema(system_id):
 n=request.form.get("name","").strip();url=request.form.get("url","").strip();d=request.form.get("description","").strip();sid=request.form.get("render_service_id","").strip()
 if not n or not url:return {"success":False,"message":"Informe o nome e a URL do sistema."},400
 if not url.startswith(("http://","https://")):url="https://"+url
 c=get_db();c.execute("UPDATE systems SET name=?,url=?,description=?,render_service_id=? WHERE id=?",(n,url,d,sid,system_id));c.commit();c.close();return {"success":True}
@app.get("/api/sistemas")
@login_required
def listar_sistemas():
 c=get_db();rows=c.execute("SELECT id,name,url,description,enabled,render_service_id,created_at FROM systems ORDER BY id DESC").fetchall();c.close();return {"systems":[dict(x) for x in rows]}
@app.get("/api/render-services")
@login_required
def api_render_services():
 try:
  services=list_render_services()
  return {"configured":True,"services":[{"id":s.get("id"),"name":s.get("name"),"type":s.get("type"),"url":s.get("url"),"suspended":s.get("suspended")} for s in services if s.get("id") and s.get("name")]}
 except urllib.error.HTTPError as e:return {"configured":True,"message":f"Render retornou HTTP {e.code}."},502
 except Exception as e:return {"configured":False,"message":str(e)},503
@app.get("/api/render-services/<service_id>")
@login_required
def api_render_service(service_id):
 try:
  s=get_render_service(service_id);return {"id":s.get("id"),"name":s.get("name"),"suspended":s.get("suspended"),"url":s.get("url")}
 except Exception as e:return {"message":str(e)},502
@app.post("/sistemas/<int:system_id>/toggle")
@login_required
def toggle_sistema(system_id):
 c=get_db();row=c.execute("SELECT id,name,enabled,render_service_id FROM systems WHERE id=?",(system_id,)).fetchone()
 if not row:c.close();return {"success":False,"message":"Sistema não encontrado."},404
 if not RENDER_API_KEY:c.close();return {"success":False,"message":"RENDER_API_KEY não está disponível no serviço Nexus. Configure a variável no Environment do serviço, não apenas como um nome de ambiente."},503
 service_id=row["render_service_id"]
 if not service_id:
  c.close();return {"success":False,"message":"Este sistema ainda não está vinculado a um serviço do Render. Clique em Editar e selecione o serviço correto."},400
 new_value=0 if row["enabled"] else 1
 ok,msg=render_action(service_id,"resume" if new_value else "suspend")
 if not ok:c.close();return {"success":False,"message":msg},502
 c.execute("UPDATE systems SET enabled=? WHERE id=?",(new_value,system_id));c.commit();c.close();return {"success":True,"enabled":bool(new_value),"render_controlled":True}
@app.post("/sistemas/excluir/<int:system_id>")
@login_required
def excluir_sistema(system_id):
 c=get_db();c.execute("DELETE FROM systems WHERE id=?",(system_id,));c.commit();c.close();return {"success":True}
@app.post("/logout")
def logout():session.clear();return redirect(url_for("home"))
@app.get("/health")
def health():return {"status":"ok","app":"Nexus Tecnologia"}
if __name__=="__main__":app.run(host="0.0.0.0",port=5000)
