use serde::{Deserialize, Serialize};
use std::process::Command;

#[derive(Serialize)]
struct SystemInfo { os:String, arch:String, hostname:String }

#[derive(Deserialize)]
struct ChatChoice { message: ChatMessage }
#[derive(Deserialize)]
struct ChatMessage { content:String }
#[derive(Deserialize)]
struct ChatResponse { choices:Vec<ChatChoice> }

#[tauri::command]
fn jarvis_status()->String{"SYSTEM ONLINE | CORE ACTIVE".to_string()}

#[tauri::command]
fn system_info()->SystemInfo{SystemInfo{os:std::env::consts::OS.into(),arch:std::env::consts::ARCH.into(),hostname:std::env::var("COMPUTERNAME").or_else(|_|std::env::var("HOSTNAME")).unwrap_or_else(|_|"UNKNOWN".into())}}

fn safe_url(url:&str)->bool{url.starts_with("https://")||url.starts_with("http://")}

#[tauri::command]
fn open_url(url:String)->Result<(),String>{
 if !safe_url(&url){return Err("Somente URLs HTTP/HTTPS são permitidas.".into());}
 #[cfg(target_os="windows")] { Command::new("cmd").args(["/C","start","",&url]).spawn().map_err(|e|e.to_string())?; Ok(()) }
 #[cfg(not(target_os="windows"))] { Err("Comando disponível nesta versão para Windows.".into()) }
}

#[tauri::command]
fn launch_app(app:String)->Result<(),String>{
 let allowed=["notepad","calc","mspaint","explorer"];
 let name=app.to_lowercase();
 if !allowed.contains(&name.as_str()){return Err("Aplicativo não permitido pela lista de segurança.".into());}
 #[cfg(target_os="windows")] { Command::new(name).spawn().map_err(|e|e.to_string())?; Ok(()) }
 #[cfg(not(target_os="windows"))] { Err("Comando disponível nesta versão para Windows.".into()) }
}

#[tauri::command]
async fn ai_chat(endpoint:String,api_key:String,model:String,system:String,messages:Vec<serde_json::Value>)->Result<String,String>{
 if endpoint.trim().is_empty(){return Err("Configure o endpoint da IA.".into());}
 let mut all=vec![serde_json::json!({"role":"system","content":system})]; all.extend(messages);
 let body=serde_json::json!({"model":model,"messages":all});
 let client=reqwest::Client::new();
 let mut req=client.post(endpoint).json(&body);
 if !api_key.trim().is_empty(){req=req.bearer_auth(api_key);}
 let response=req.send().await.map_err(|e|e.to_string())?;
 if !response.status().is_success(){return Err(format!("IA HTTP {}",response.status()));}
 let data:ChatResponse=response.json().await.map_err(|e|e.to_string())?;
 data.choices.first().map(|c|c.message.content.clone()).ok_or_else(||"A IA não retornou conteúdo.".into())
}

#[tauri::command]
async fn web_search(query:String)->Result<Vec<serde_json::Value>,String>{
 let url=format!("https://html.duckduckgo.com/html/?q={}",urlencoding::encode(&query));
 let text=reqwest::get(url).await.map_err(|e|e.to_string())?.text().await.map_err(|e|e.to_string())?;
 let mut results=Vec::new();
 for chunk in text.split("result__a").skip(1).take(5){
  let title=chunk.split('>').nth(1).and_then(|s|s.split("</a").next()).unwrap_or("").replace("&quot;",""");
  if !title.trim().is_empty(){results.push(serde_json::json!({"title":title.trim()}));}
 }
 Ok(results)
}

#[cfg_attr(mobile,tauri::mobile_entry_point)]
pub fn run(){
 tauri::Builder::default().plugin(tauri_plugin_shell::init())
 .invoke_handler(tauri::generate_handler![jarvis_status,system_info,open_url,launch_app,ai_chat,web_search])
 .run(tauri::generate_context!()).expect("error while running JARVIS AI");
}
